# Turborepo 与 Monorepo 任务调度源码解析：从 DAG 到增量构建

> 从源码剖析 Turborepo 的任务图构建、拓扑排序、缓存与远程缓存、增量执行，理解现代 Monorepo 构建引擎设计。

---

## 一、背景：Monorepo 与构建性能痛点

现代前端与全栈项目越来越多地采用 **Monorepo**：把多个应用、共享库、工具包放在同一仓库中统一管理依赖与版本，便于复用代码和做原子化提交。但 Monorepo 也带来明显的构建挑战：**任务多、依赖关系复杂、全量构建耗时长**。若每次 `pnpm build` 都按脚本顺序串行执行所有包的构建，在包数量达到几十上百时，构建时间会线性甚至超线性增长，CI 与本地开发体验都会变差。

因此，构建系统需要解决几类问题：

1. **任务依赖关系**：包 A 依赖包 B 的构建产物，则 B 必须先于 A 执行；这种依赖可以抽象为有向图（DAG）。
2. **并行度**：无依赖关系的任务应尽量并行执行，充分利用多核。
3. **增量与缓存**：输入未变的包不应重复构建，应复用上次的产物（本地或远程）。
4. **确定性**：相同输入应得到相同输出，便于缓存键计算与复现。

**Turborepo** 正是针对上述问题设计的 Monorepo 构建编排引擎：它在不替换你现有构建工具（如 Vite、Webpack、tsc）的前提下，负责**解析脚本依赖、构建任务 DAG、按拓扑顺序调度执行、并做本地/远程缓存**。本文从源码视角，拆解其任务图构建、调度与缓存机制，便于你在选型或二次开发时理解其设计取舍。

## 二、Turborepo 整体架构与核心概念

Turborepo 的核心入口在 **turbo** 这个 CLI 包中。执行 `turbo run build` 时，大致会经历：

1. **解析工作区**：读取 `pnpm-workspace.yaml` 或 `package.json` 的 workspaces，得到所有子包路径。
2. **读取管道配置**：从根目录 `turbo.json` 的 `pipeline`（或新版的 `tasks`）中读取每个脚本（如 `build`、`dev`）的 `dependsOn`、`outputs`、`cache` 等。
3. **构建任务图**：根据 `dependsOn` 与包之间的实际依赖（dependencies/devDependencies）构建 DAG；同一脚本在不同包中对应多个「任务节点」。
4. **计算执行计划**：对 DAG 做拓扑排序，得到可并行执行的批次；结合本地/远程缓存决定哪些任务可跳过。
5. **执行与写缓存**：按批次执行任务，成功则将输出按 `outputs` 配置与输入哈希写入缓存。

源码中，**任务图** 的构建与 **运行器** 是分离的：图结构在 `turbo-tasks` 或 `turbo-core` 中抽象，运行器（真正执行 `pnpm run build` 等）在 `turbo-run` 中，通过 **Runner** 接口与图交互。这种分离便于在不同环境（本地、CI、远程）复用同一套图逻辑。

## 三、任务图（DAG）的构建与解析

任务图的节点是「某个包下的某个脚本」，例如 `packages/web#build`、`packages/utils#build`。边来自两类信息：

- **显式依赖**：`turbo.json` 里为该脚本配置的 `dependsOn`，如 `build` 依赖 `^build` 表示依赖当前包所依赖的所有包的 `build` 先执行。
- **隐式依赖**：Turborepo 会结合工作区依赖关系解析：若 A 的 `package.json` 的 dependencies 中有 B，则 A 的 `build` 通常会依赖 B 的 `build`（除非被 `dependsOn` 覆盖）。

在源码中，**图构建** 的典型流程是：

1. 遍历所有包，为每个包在 pipeline 中出现的每个 script 创建一个 **TaskNode**。
2. 根据 `dependsOn` 的语义（如 `^build` 表示上游依赖的 build）解析出「包 → 包」的依赖，再映射到「任务 → 任务」的边。
3. 使用图结构（邻接表或类似）存储节点与边，并做**环检测**；若存在环则报错并退出。

`^build` 这类语法表示「我依赖的 workspace 包的 build 先跑完」；`build` 仅表示「当前包的 build 之前要跑一次 build」（通常指当前包自身无额外前置任务时的占位）。源码里会有一个 **DependsOn 解析器**，把字符串配置转成对「包名 + 脚本名」的引用，再在图中加边。

## 四、拓扑排序与任务调度

DAG 构建完成后，需要得到**合法的执行顺序**：若 A 依赖 B，则 B 必须先于 A 执行。拓扑排序（如 Kahn 算法或 DFS 后序）可以得到一个线性序列，但 Turborepo 的目标不仅是「顺序」，而是**最大化并行**：同一批中所有没有互相依赖的任务可以同时执行。

因此实现上通常会做 **层级划分**（level / tier）：

- 入度为 0 的节点全部进入第 0 批，并行执行；
- 执行完后「逻辑上」从图中移除这些节点，再取新一批入度为 0 的节点作为第 1 批；
- 重复直到所有节点执行完毕。

源码中会有一个 **Scheduler** 或 **ExecutionPlan** 的抽象：它持有 DAG，提供 `getNextBatch()` 或类似接口，在每批任务完成后调用 `markComplete(task)`，再取下一批。执行层（Runner）则循环：取一批 → 并发执行（如用 Promise.all 或 worker 池）→ 等这批全部完成 → 再取下一批。这样既保证依赖顺序，又尽量压榨多核。

**注意**：任务执行可能失败。若某任务失败，通常要取消或跳过所有依赖它的下游任务，并在控制台标出失败节点；图结构便于做「从失败节点出发的 BFS/DFS」来标记受影响范围。

## 五、本地与远程缓存

Turborepo 的缓存键由 **任务身份 + 输入哈希** 决定。任务身份即「包名 + 脚本名」；输入哈希则通常包括：

- 该任务所声明的 **inputs**（默认为该包目录下除 `node_modules` 和 `outputs` 外的文件）的内容哈希；
- 依赖任务的**输出**（即上游任务的 outputs 的哈希或路径），形成「依赖链」上的输入。

若某次运行的输入哈希与某次历史运行一致，则命中缓存：直接解压该次运行的 outputs 到目标目录，并标记该任务为跳过执行。缓存存储可以是：

- **本地**：默认在 `node_modules/.cache/turbo`（或项目配置的目录）下，按哈希存 tar 或类似归档；
- **远程**：通过 **Remote Caching**（如 Vercel 提供的或自建）上传/下载缓存，使 CI 与多人开发共享同一套缓存。

源码中会有一个 **Cache** 接口：`get(hash)`、`put(hash, outputs)`、`exists(hash)`。本地实现用文件系统；远程实现用 HTTP API 上传/下载。运行器在执行任务前先算输入哈希，查缓存；命中则恢复 outputs 并跳过执行；未命中则执行任务，成功后根据 `outputs` 配置打包产物并写入缓存。

## 六、增量构建与输入哈希

**增量构建** 的本质是：只重建「输入发生变化」的任务及其下游。Turborepo 通过 DAG + 缓存实现这一点：

1. 每个任务的**输入**包括：该包内相关文件、以及其依赖任务的**输出**（即依赖任务的 `outputs` 列表中的文件内容或元信息）。
2. 输入哈希（如 xxHash 或 SHA）聚合后得到该任务的 **cache key**；若与某次历史运行一致，则命中缓存。
3. 若某个包 A 的源码或配置变了，仅 A 及其**下游**（依赖 A 的输出的任务）的输入哈希会变；上游任务可继续命中缓存。

因此，**outputs** 的配置很重要：若配置过窄，下游任务可能拿不到完整依赖；过宽则无关文件变化会导致缓存失效。通常建议只包含真正影响下游的构建产物目录（如 `dist`、`lib`）。

源码中，**哈希计算** 会遍历 inputs 列表下的文件，过滤掉 gitignore 和 turbo 配置的 exclude，对文件内容做流式哈希，再与任务 id、依赖任务的 cache key 等组合成最终 key。这一块通常与「文件系统监听」解耦，即不做 watch 模式下的增量哈希，而是每次 run 时全量算一遍；在 Monorepo 规模适中时，算哈希的开销远小于重复执行构建。

## 七、DependsOn 与 workspace 依赖解析详解

`turbo.json` 中 `pipeline.build.dependsOn` 常见写法有：`[]`、`["^build"]`、`["build"]` 等。

- **`[]`**：该任务无前置任务（仅受「同包内其他脚本」或隐式包依赖影响，取决于实现）。
- **`["^build"]`**：表示「当前包在 workspace 中依赖的所有包的 `build` 要先执行」。解析时需读取当前包的 `package.json` 的 dependencies/devDependencies，过滤出 workspace 内的包，再为每个这样的包添加「该包的 build → 当前包的 build」的边。
- **`["build"]`**：在部分版本中表示「当前包的 build 依赖自身 build」（占位），或依赖根任务的 build；需结合源码具体语义。

源码中会有一个 **resolveDependsOn** 或 **expandDependsOn**：输入 (packageName, taskName, dependsOnConfig)，输出 (dependedPackage, dependedTask) 的列表。实现时需解析 workspace 图（谁依赖谁），避免把非 workspace 的 npm 包也算进去。若配置了 `"dependsOn": ["^build", "lint"]`，则除了上游包的 build，可能还有「当前包的 lint」先执行，即同包内的任务依赖也可用同名或别名表达。

## 八、Runner 与子进程管理

任务的实际执行通过 **Runner** 调用系统 shell：在对应包目录下执行 `pnpm run build`（或 npm/yarn）。Runner 需要：

- **环境隔离**：每个任务在正确的工作目录、env 下执行；`turbo run` 会传入 `TURBO_TASK_ID`、`TURBO_HASH` 等便于脚本内使用。
- **输出捕获**：stdout/stderr 需实时或按批输出到主进程，便于用户看到日志；同时可能要做**前缀**（如 `packages/web:build`）以便区分并发任务。
- **超时与终止**：若某任务超时或用户 Ctrl+C，需要终止该任务及其子进程；Node 中可用 `child_process.spawn` 的 `kill` 或 `killTree`。
- **缓存恢复**：若命中缓存，Runner 可能不执行脚本，而是把缓存中的 outputs 解压到目标目录；从用户视角看该任务也是「成功完成」的。

源码中 Runner 多为异步：`runTask(task) => Promise<RunResult>`，RunResult 包含 success、exitCode、outputs 等。调度层对一批任务做 `Promise.all(batch.map(runTask))`，等整批完成再推进下一批。

## 九、源码关键路径梳理

若你打开 Turborepo 的 GitHub 仓库（turbo 主仓），可以按以下路径快速定位：

- **入口**：`packages/turbo/src/commands/run.ts` 或类似，解析 `turbo run build`，调用 run 逻辑。
- **图构建**：在 `turbo-core` 或 `turbo-tasks` 中，查找 `Graph`、`TaskGraph`、`buildGraph`、`pipeline` 等；`dependsOn` 的解析多在 `config` 或 `pipeline` 模块。
- **执行计划**：查找 `ExecutionPlan`、`Scheduler`、`getTasksToRun`；拓扑与批次的划分在这里。
- **缓存**：`cache` 目录或 `Cache` 类，本地实现多为 `LocalCache`，远程为 `RemoteCache`；哈希计算在 `hashing` 或 `hash` 相关文件。
- **运行器**：`runner` 或 `run` 包中，真正 spawn 子进程执行 `pnpm run build` 的代码；会监听 stdout/stderr 并处理退出码。

不同大版本（如 turbo 1.x 与 2.x）目录名可能略有差异，但「图 → 计划 → 缓存 → 执行」这条主线是共通的。阅读时建议先跑通一次 `turbo run build`，在关键节点打日志或断点，观察 DAG 的节点数、批次数与缓存命中情况，再反推源码。

## 总结

- Turborepo 将 Monorepo 中的脚本抽象为 **DAG**，通过 `dependsOn` 与工作区依赖构建任务图，并做环检测。
- **拓扑排序 + 分层批执行** 在保证依赖顺序的前提下最大化并行；执行层按批调度，一批完成再取下一批。
- **缓存** 由「任务 id + 输入哈希」决定；输入包括包内文件与依赖任务的输出；本地与远程缓存共用同一套 key 设计。
- **增量构建** 通过输入哈希与缓存自然实现：仅输入变化的任务及其下游会重新执行，其余命中缓存。
- 阅读源码时可沿「入口 → 图构建 → 执行计划 → 缓存查找/写入 → 运行器」这条路径，结合一次真实 run 的日志理解各阶段数据流。

**与 Nx、Lage 的简要对比**：Nx 同样做 DAG 与缓存，但更偏向「全栈 Monorepo + 代码生成」生态；Lage 是微软开源的类似编排器，也采用图 + 缓存。Turborepo 的卖点是与 Vercel 集成简单、配置相对克制、远程缓存开箱可用。三者核心思想一致，差异多在配置语法、云缓存方案与生态绑定。

若你在做 Monorepo 选型或需要定制任务依赖与缓存策略，希望这篇源码向的梳理能帮你快速抓住 Turborepo 的设计要点。

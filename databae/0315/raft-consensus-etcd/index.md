# Raft 共识算法与 etcd 实践：从选主到日志复制的完整链路

> 深入 Raft 选主、日志复制、安全性与线性一致读，结合 etcd 的实现与配置，适合做分布式存储与协调的进阶读物。

---

## 一、背景：为什么需要共识算法

在分布式系统里，多个节点要对外提供**一致**的数据视图：同一份日志顺序、同一份状态机结果。但网络会延迟、会分区，节点会宕机，若没有一套明确的「谁说了算、怎么复制、怎么恢复」的规则，就会出现脑裂、丢写、读脏数据等问题。**共识算法**要解决的就是：在允许部分节点故障、网络不可靠的前提下，让集群对「一系列操作顺序」达成一致，并在此基础上实现复制状态机（Replicated State Machine）。

**Paxos** 理论完备但难以工程实现；**Raft** 把共识拆成**选主（Leader Election）**、**日志复制（Log Replication）**、**安全性（Safety）** 三块，并强调**可理解性与可实现性**，因此被 etcd、Consul、TiKV 等广泛采用。本文以 Raft 为主线，结合 **etcd** 的默认实现，把从「节点启动」到「线性一致读」的完整链路讲清楚。

## 二、Raft 的角色与任期

每个节点在任意时刻处于三种角色之一：**Leader**、**Follower**、**Candidate**。所有写请求只由 Leader 接收，再复制到多数节点；Follower 被动响应 Leader 的心跳与日志追加；Candidate 是**选举过程中的临时状态**，若获得多数票则晋升为 Leader。

**任期（term）** 是一个单调递增的整数，每次发起或参与选举时 term 会增大。Raft 保证：**同一 term 内至多一个 Leader**。节点用 (term, index) 唯一标识一条日志；消息里会带上自己的 term，收到更大 term 的节点会回退为 Follower，从而避免旧 Leader 继续写。

## 三、选主（Leader Election）

Follower 在**选举超时（election timeout）**内未收到当前 Leader 的心跳，就会自增 term、转为 Candidate，并**先给自己投一票**，再向其他节点发起 **RequestVote** RPC。RequestVote 会带上自己的 (term, lastLogIndex, lastLogTerm)，对方只有在该 Candidate 的日志「至少和自己一样新」时才会投票（Raft 的 **Leader 完整性** 保证：已提交的日志一定不会丢）。若 Candidate 收到**多数**同意，则成为 Leader，并开始向所有节点发**心跳（AppendEntries，空日志）**以维持权威；若收到更高 term 的响应或发现已有 Leader，则回退为 Follower；若本 term 内无人过半，则超时后 term+1 再次发起选举。

**随机化选举超时**：Raft 建议每个节点的 election timeout 在 [T, 2T] 内随机，这样可减少多节点同时变成 Candidate 导致选票被瓜分、反复重选的情况。etcd 中对应 `ElectionTick` 等配置。

## 四、日志复制（Log Replication）

客户端写请求只发到 Leader。Leader 把该写作为一条**日志条目**追加到本地，然后通过 **AppendEntries** RPC 并行发给所有 Follower。每条日志有 (term, index, command)。Follower 收到后做**一致性检查**：若自己上一条的 (term, index) 与 Leader 的 prevLogTerm、prevLogIndex 不匹配，则拒绝并返回自己的 lastIndex，Leader 会回退 nextIndex 并重发，直到找到一致点再批量追加。当**多数**节点已持久化某条日志时，Leader 视其为 **committed**，并可在后续 AppendEntries 里带上 **commitIndex**，Follower 据此把已提交日志应用到状态机。Raft 保证：**已提交的日志不会被覆盖或删除**（通过选主时的「日志至少一样新」和提交规则共同保证）。

## 五、安全性与线性一致读

Raft 的**安全性**来自两条核心约束：**选举安全**（同一 term 最多一个 Leader）和**Leader 完整性**（已提交日志一定出现在新 Leader 上）。在此基础上，**状态机安全**（同一 index 应用相同 command）和**Leader 只追加**（不删除、不覆盖已存在 index）共同保证复制状态机一致。

**线性一致读**：若客户端每次读都走 Leader 且等 Leader 应用完当前 commitIndex 再返回，则可得到线性一致。etcd 的 **LinearizableRead** 通过 **ReadIndex** 或 **Lease Read** 实现：ReadIndex 下 Leader 先确认自己仍是 Leader（发一轮心跳），再等本机 apply 到 readIndex 后返回；Lease Read 在 Leader 租约有效期内可直接读本机状态，减少往返，但需保证时钟与心跳约束。

## 六、etcd 中的 Raft 实现与配置

etcd 使用自己 fork 的 **etcd/raft** 库，与存储层（WAL、Snapshot、Backend）和传输层（gRPC）集成。关键配置包括：**ElectionTick**（多少 tick 未收到心跳则发起选举）、**HeartbeatTick**（Leader 发心跳间隔）、**MaxSizePerMsg**、**MaxCommittedSizePerReady** 等控制批大小与流量。生产环境需根据网络与磁盘调整 tick、snapshot 策略与 WAL 保留，并监控 **term 变化**、**commit 延迟**、**Leader 切换**，以便排查分区与慢节点。

## 七、总结

Raft 通过**选主**确定唯一写入口、**日志复制**在多数派上持久化并提交、**安全性**保证已提交日志不丢且状态机一致。理解 term、选举超时、AppendEntries 的一致性检查与 commitIndex 推进，就能在 etcd 等系统中正确配置与排障。线性一致读在 etcd 中通过 ReadIndex/Lease Read 实现，是构建分布式锁、配置中心等能力的基础。

## 八、常见问题与排错

- **频繁选主**：多为网络抖动或 election timeout 过短，可适当增大 ElectionTick、检查网络与磁盘延迟。
- **commit 慢**：少数 Follower 慢会拖累 Leader 的 commitIndex 推进，可看各节点 append 延迟与 snapshot 是否过大。
- **读到旧值**：若未使用 LinearizableRead 或走了 Follower 且该 Follower 落后，可能读到过期数据；etcd 客户端应使用带线性一致语义的读接口。
- **term 不断增大**：分区或多 Candidate 竞争会导致 term 飙升，属正常；恢复后会有一次选举与日志对齐。

## 九、选主与日志复制的流程小结（便于对照源码）

**选主流程**：Follower 超时 → term+1、转 Candidate、自投票 → 并发 RequestVote(term, lastLogIndex, lastLogTerm) → 若收到多数同意 → 转 Leader、发心跳；若收到 term ≥ 自己的消息 → 转 Follower；若超时未出结果 → term 再 +1 重选。**日志复制流程**：Leader 收到写 → 追加本地 log、更新 nextIndex → 并发 AppendEntries(prevLogIndex, prevLogTerm, entries[], leaderCommit) → Follower 校验 prev 一致则追加并回复成功 → Leader 更新 matchIndex、推进 commitIndex（当多数已复制）→ 下轮心跳带新 commitIndex，Follower 应用至状态机。

etcd 的 raft 库中，**Node** 是上层与 Raft 核心的接口，**raftLog** 管理日志存储与截断，**raft** 结构体持有 term、vote、state 与 **Progress**（每个节点的 nextIndex/matchIndex）。**Step** 方法处理所有 Raft 消息（MsgVote、MsgApp、MsgHeartbeat 等），驱动状态迁移。阅读源码时建议从 **raft.Step** 和 **etcdserver 的 apply 循环** 两条线往下跟。

## 十、延伸阅读

- 论文：*In Search of an Understandable Consensus Algorithm (Diego Ongaro, John Ousterhout, 2014)*。
- etcd 文档：Raft 实现与配置项、API 的 Linearizable 选项。
- 对比：与 Paxos、ZAB（ZooKeeper）的差异，Raft 在可理解性与工程化上的取舍。

## 十一、实践：etcd 集群部署与参数建议

生产环境部署 etcd 时，通常**至少 3 节点**以容忍 1 节点故障；5 节点可容忍 2 节点故障。**ElectionTick** 与 **HeartbeatTick** 建议保持默认或根据网络 RTT 微调：心跳过短会增加网络与 CPU 负担，过长会拉长选主与恢复时间。**Snapshot** 间隔不宜过大，否则 WAL 膨胀且重启恢复慢。**磁盘** 建议 SSD，避免 WAL 写成为瓶颈。监控上除 term、commitIndex 外，可关注 **raft_term**、**raft_applied_index** 与各节点差异，便于发现分区与落后节点。结合本文的选主与日志复制流程，在排障时能快速判断是网络问题、慢节点还是配置不当。

---

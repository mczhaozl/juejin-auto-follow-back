# 小红书技能参考

## 推荐：redbook 目录（语义化选择器、标题专家、1000 字、话题、模板）

- **标题**：由**标题专家**专门产出，**不解析**正文。发布时用 `--title "标题"` 传入，最多 20 字。
- **填表 + 话题 + 模板 + 一键排版 + 发布**（项目根目录执行）：
  ```bash
  node redbook/cli.js --file posts/<文件名>.md --title "标题专家产出的标题" --topics 话题1,话题2 --template 素雅底纹 --format --publish
  ```
- **正文**：从文件读取（首行若为 `# 标题` 会从正文中剔除，不用于标题）；上限 1000 字，简短模式 600 字。
- **话题**：`--topics` 逗号分隔；**标签**：`--tags` 逗号分隔。
- **模板**：`--template` 素雅底纹/大图纯享等（审美专家建议）。
- **仅探测**：`node redbook/cli.js --inspect`
- 选择器与步骤封装：`redbook/dom-selectors.js`、`redbook/utils/*.js`

## 旧脚本（仍可用）

- **打开创作页**：
  ```bash
  node scripts/chrome-control.js "https://creator.xiaohongshu.com/publish/publish?source=official&from=menu&target=article"
  ```
- **填表 + 排版 + 发布**：`node scripts/xiaohongshu-fill.js --file posts/xxx.md --format --publish`
- **探测**：`node scripts/xiaohongshu-fill.js --inspect`
- 端口覆盖：`CHROME_DEBUG_PORT=9223 node redbook/cli.js ...`

## 文章格式

- **标题**：不由文件解析，由**标题专家**产出，用 `--title` 传入。
- **正文**：从 `--file` 指定文件读取；若首行为 `# xxx` 会从正文中去掉该行（不当作标题）。正文建议 ≤1000 字。

## 发布按钮 DOM（已记入 redbook）

- 发布区域：`.publish-page-publish-btn`
- 发布按钮：`.publish-page-publish-btn button.bg-red` 或同区域内文案「发布」的 button

## MCP

- 使用你提供的 Chrome 配置（userDataDir + 9222）：见 [docs/mcp-chrome-config.md](docs/mcp-chrome-config.md)

# Repository Guidelines

本指南适用于当前仓库内的 coding agent 协作与交付流程。

## 1. 开发与回归

- 保持与现有代码风格一致，Python 代码遵循 `ruff` 规则与既有目录结构。
- 改动后按影响范围执行回归，常用命令：
  - `uv sync --all-extras`（首次或依赖变化时）
  - `uv run ruff check .`
  - `uv run pytest`
- 若因环境限制无法完成某项回归，需在回复中明确说明未执行项与原因。

## 2. Git 工作流

- 禁止直接向受保护分支提交或推送：`main`/`master`/`release/*`。
- 每个任务应在独立分支实施，分支建议从最新主干切出。
- 同步主干时优先使用 `git fetch` + `git merge --ff-only`，避免隐式合并。
- 允许将开发分支推送到远端同名分支，以便协作与备份。
- 禁止改写公共历史：`git push --force`、`git push --force-with-lease`、随意 `rebase`。
- 仅提交本次任务相关文件，不清理或回滚与任务无关的在地改动。

## 3. Issue 与 PR 协作

- 开发类任务开始前，先检查是否已有相关 open Issue（例如 `gh issue list --state open`）。
- 若无相关 Issue，应创建新 Issue 跟踪；Issue 内容建议包含背景、复现、预期/实际、验收标准，并附 `git rev-parse HEAD` 快照。
- 仅协作规范/流程文档改动（如 `AGENTS.md`）可直接修改，无需额外建 Issue。
- 提交信息若服务于某个 Issue，应在 commit message 中标注 `#issue`。
- PR 默认建议创建为 Draft，并在描述中标明关联关系（如 `Closes #xx` / `Relates to #xx`）。
- 出现关键进展、方案变化或风险时，及时在对应 Issue/PR 中同步，不要求机械化高频评论。

## 4. 工具与文本规范

- 读写 Issue/PR 使用 `gh` CLI，不通过网页手工编辑。
- Issue、PR 与评论使用简体中文；专业术语可保留英文。
- 多行正文请先写入临时文件，再用 `--body-file` 传入；不要在 `--body` 中拼接 `\\n`。
- 同仓引用使用 `#123` 自动链接；跨仓引用使用完整 URL。

## 5. 安全与配置

- 严禁提交密钥、令牌、凭证或其他敏感信息（含 `.env` 内容）。
- 日志与调试输出不得泄露访问令牌或隐私数据。
- 涉及部署、认证、密钥注入的改动，需同步更新文档并给出最小验收步骤。

# OpenCode 控制类能力评估（2026-02-24）

## 评估范围

- 基线分支：`main`（HEAD: `77d6515`）
- 评估对象：
  - 上游 `opencode serve`（基于本仓库快照 `docs/operations/opencode/openapi-serve-1.2.4.json`）
  - 本项目 `opencode-a2a-serve` 当前实现（`src/opencode_a2a_serve/*`）
- 关注能力：
  - 中断当前生成
  - 补充新的指令
  - 中断任务
  - 更换模型

## 结论总览

| 能力 | OpenCode `serve` 原生能力 | `opencode-a2a-serve` 当前能力 | 结论 | 关联 Issue |
| --- | --- | --- | --- | --- |
| 中断当前生成 | 支持 `POST /session/{sessionID}/abort` | 支持 A2A `tasks/cancel`，会取消本地执行协程并停止事件消费；但未调用上游 `session.abort` | 部分支持（A2A 层可取消；上游硬中断未打通） | #74 |
| 补充新的指令 | 支持 `POST /session/{sessionID}/prompt_async`；也支持 permission/question 回调接口 | 已支持中断回调扩展：`opencode.permission.reply` / `opencode.question.reply` / `opencode.question.reject`；未暴露“通用中途补充 prompt”接口 | 部分支持（仅结构化回调，不是任意补充指令） | #75 |
| 中断任务 | 具备会话/事件层中断相关接口 | 已支持 A2A `tasks/cancel`，并有取消行为测试覆盖 | 支持（A2A 任务语义层） | #74 |
| 更换模型 | 请求体支持 `model.providerID/modelID`；并可查询 provider/model 配置 | 仅支持服务端静态配置 `OPENCODE_PROVIDER_ID`/`OPENCODE_MODEL_ID`，无请求级覆盖 | 暂不支持（动态路由能力缺失） | #76 |

## 证据（代码与文档）

### 1) 中断当前生成 / 中断任务

- A2A 侧取消入口：
  - `OpencodeAgentExecutor.cancel()` 会发出 `TaskState.canceled`，并取消运行中的请求任务：
    `src/opencode_a2a_serve/agent.py:678`
- 取消行为测试：
  - `tests/test_cancellation.py:14`（验证运行中执行被取消）
- 当前实现中，`OpencodeClient` 没有调用 `POST /session/{sessionID}/abort`：
  - `src/opencode_a2a_serve/opencode_client.py:175`（事件流）
  - `src/opencode_a2a_serve/opencode_client.py:244`（发送消息）

### 2) 补充新的指令

- 已实现的结构化中断回调扩展处理：
  - `src/opencode_a2a_serve/jsonrpc_ext.py:405`
  - 支持方法：`opencode.permission.reply`、`opencode.question.reply`、`opencode.question.reject`
- 流式事件可产出 interrupt 状态并绑定 `request_id`：
  - `src/opencode_a2a_serve/agent.py:975`
  - `src/opencode_a2a_serve/agent.py:1158`

### 3) 更换模型

- 当前模型参数来源于环境变量配置：
  - `src/opencode_a2a_serve/config.py:21`
  - `src/opencode_a2a_serve/config.py:22`
- 发送消息时仅注入服务端固定模型参数：
  - `src/opencode_a2a_serve/opencode_client.py:260`
- 未看到请求级 `metadata` 覆盖模型配置的实现。

## 风险与边界

- `tasks/cancel` 目前确保 A2A 侧尽快结束任务与清理状态，但不等价于上游模型一定立即停止生成。
- “补充新的指令”目前仅覆盖 permission/question 这类可验证的中断回调，不支持任意自由文本的中途插入。
- 动态模型切换仍受限于实例级静态配置，无法按请求路由模型。

## 建议后续

1. 在 #74 中补齐“调用上游 `session.abort`”的实现与验收用例，达成真实生成中断。
2. 在 #75 中明确“仅保留结构化回调”还是“新增通用补充指令入口（如映射 `prompt_async`）”。
3. 在 #76 中设计请求级模型覆盖契约（字段命名、白名单与安全约束）并补充对应测试。

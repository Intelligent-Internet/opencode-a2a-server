# 使用指南

本指南集中说明配置、鉴权、接口行为、Streaming 断线续订，以及 A2A 客户端示例。

## 环境变量

- `OPENCODE_BASE_URL`：OpenCode 地址，默认 `http://127.0.0.1:4096`
- `OPENCODE_DIRECTORY`：OpenCode directory 参数（可选）
- `OPENCODE_PROVIDER_ID`：模型 providerID（可选）
- `OPENCODE_MODEL_ID`：模型 modelID（可选）
- `OPENCODE_AGENT`：OpenCode agent 名称（可选）
- `OPENCODE_SYSTEM`：system prompt（可选）
- `OPENCODE_VARIANT`：variant（可选）
- `OPENCODE_TIMEOUT`：请求超时秒数，默认 `120`（systemd 部署模板默认写入 `300`）
- `OPENCODE_TIMEOUT_STREAM`：streaming 请求超时秒数（可选；不设置则不限制）

- `A2A_PUBLIC_URL`：对外可访问的 A2A 地址前缀，默认 `http://127.0.0.1:8000`
- `A2A_TITLE`：Agent 名称，默认 `OpenCode A2A`
- `A2A_DESCRIPTION`：Agent 描述
- `A2A_VERSION`：Agent 版本号
- `A2A_PROTOCOL_VERSION`：A2A 协议版本，默认 `0.3.0`
- `A2A_HOST`：监听地址，默认 `127.0.0.1`
- `A2A_PORT`：监听端口，默认 `8000`
- `A2A_JWT_SECRET_B64`：base64 编码的 JWT 验签 key（推荐用于 systemd `EnvironmentFile`，避免 PEM 多行换行问题；**优先级最高**）
- `A2A_JWT_SECRET_FILE`：JWT 验签 key 文件路径（便于本地调试；注意服务进程需要有读取权限；优先级次之）
- `A2A_JWT_SECRET`：JWT 验签 key（单行；不推荐生产使用；优先级最低）
- `A2A_JWT_ALGORITHM`：JWT 签名算法（**仅支持非对称算法**），默认 `RS256`
- `A2A_JWT_ISSUER`：JWT 签发者校验（必填）
- `A2A_JWT_AUDIENCE`：JWT 受众校验（必填）
- `A2A_REQUIRED_SCOPES`：可选，逗号分隔的 scopes 列表（用于 JWT 的 `scope`/`scp` 校验；例如 `A2A_REQUIRED_SCOPES=opencode,admin`）
- `A2A_JWT_SCOPE_MATCH`：当设置了 `A2A_REQUIRED_SCOPES` 时的 scopes 匹配规则，可选 `any`/`all`，默认 `any`
- `A2A_STREAMING`：是否启用 SSE streaming（`/v1/message:stream`），默认 `true`
- `A2A_LOG_LEVEL`：A2A 服务日志级别（`DEBUG/INFO/WARNING/ERROR`），默认 `INFO`
- `A2A_LOG_PAYLOADS`：是否记录 A2A 与 OpenCode 的请求/响应正文，默认 `false`
- `A2A_LOG_BODY_LIMIT`：日志正文最大长度，默认 `0`（不截断）
- `A2A_DOCUMENTATION_URL`：可选；用于在 Agent Card 的 `documentationUrl` 字段中暴露文档地址（建议指向本仓库或内部文档站点）
- `A2A_SESSION_CACHE_TTL_SECONDS`：`(identity, contextId) -> OpenCode session_id` 的内存缓存 TTL（秒），默认 `3600`
- `A2A_SESSION_CACHE_MAXSIZE`：会话映射缓存最大条数，默认 `10000`

（已移除未实现的 OAuth2 预留配置；本服务仅做 JWT 验签与可选 scope 校验。）

## 服务行为说明

- 该服务将 A2A 的 `message:send` 请求转发为 OpenCode 的 session/message 调用。
- 任务状态默认返回 `input-required`，便于继续多轮对话。
- Streaming（`/v1/message:stream`）会输出 `TaskArtifactUpdateEvent` 增量（`append=true`），结束时发送 `TaskStatusUpdateEvent(final=true)`；完整内容由 artifact 承载，非 streaming 调用仍返回 `Task`。
- 需在请求中携带 `Authorization: Bearer <token>`，否则返回 401（Agent Card 不受鉴权限制）。
- **错误处理与反馈**：
  - 输入校验失败、上下文缺失（缺失 `task_id` 或 `context_id`）或内部处理异常时，服务会尽可能通过 `event_queue` 返回标准 A2A 失败事件。
  - 失败事件将包含具体的错误信息，并根据请求类型返回 `failed` 状态。
  - 这确保了调用方能够接收到明确的反馈，避免因未捕获异常导致的挂起或难以诊断的问题。
- **目录校验与归一化**：
  - 支持通过请求 `metadata.directory` 指定工作目录，但该路径必须落在 `${OPENCODE_DIRECTORY}`（或服务运行根目录）之内。
  - 所有路径均会经过 `realpath` 归一化处理，防止通过 `..` 或符号链接绕过边界。
  - 若 `A2A_ALLOW_DIRECTORY_OVERRIDE` 设置为 `false`（默认开启），则仅允许使用默认工作目录，任何不同的路径请求将被拒绝。
  - 校验失败将通过事件队列反馈 `failed` 状态及错误说明。
- 支持 JWT 无状态鉴权：会校验签名算法（仅非对称）、签发者（issuer，必填）、受众（audience，必填）、过期时间（exp，必填），并可选校验 Scopes（scope/scp，字符串或数组）。
本服务不会在 Agent Card 中声明 OAuth2 scheme，以避免客户端误判。

## 续聊契约（绑定到历史 OpenCode session）

当下游希望“选择一个历史 OpenCode session 后继续对话”时，应在每次 invoke 的请求 `metadata` 中显式传入：

- `metadata.opencode_session_id`: 目标 OpenCode session id（例如 `ses_xxx`）

服务端行为：

- 若提供 `metadata.opencode_session_id`：优先发送消息到该 session（不新建 session）。
- 若未提供：服务端会创建新 session，并在内存中缓存 `(identity, contextId) -> session_id`（带 TTL 与最大容量限制）。

最小 curl 示例：

```bash
curl -sS http://127.0.0.1:8000/v1/message:send \
  -H 'content-type: application/json' \
  -H 'Authorization: Bearer <your-token>' \
  -d '{
    "message": {
      "messageId": "msg-continue-1",
      "role": "ROLE_USER",
      "content": [{"text": "继续刚才的对话：请把上次的结论再总结一下"}]
    },
    "metadata": {
      "opencode_session_id": "<session_id>"
    }
  }'
```

## OpenCode 会话查询（A2A Extension）

本服务通过 A2A Extension 的方式暴露“OpenCode 会话列表/历史消息查询”能力，不额外提供自定义 REST 端点。

- 触发方式：通过 **A2A JSON-RPC**（默认 `POST /`）调用扩展方法。
- 鉴权：复用同一个 `Authorization: Bearer <token>`。
- 安全：即使开启 `A2A_LOG_PAYLOADS=true`，当检测到 `method=opencode.sessions.*` 的 JSON-RPC 请求时，服务也不会将请求/响应 body 写入日志（避免泄露聊天历史）。
- 调用 URL：建议从 Agent Card 的 `additional_interfaces[]` 中选择 `transport=jsonrpc` 的 `url`，避免自行拼接推导。
- 返回格式：`result.items` 始终为数组，且 item 为 A2A 标准对象（会话列表为 Task，且 `status.state=completed`；消息历史为 Message）。OpenCode 原始 item 放在 `metadata.opencode.raw`；会话标题可直接读取 `metadata.opencode.title`（无标题时为占位值 `Untitled session`）。

### 会话列表（method: opencode.sessions.list）

```bash
curl -sS http://127.0.0.1:8000/ \
  -H 'content-type: application/json' \
  -H 'Authorization: Bearer <your-token>' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "opencode.sessions.list",
    "params": {"page": 1, "size": 20}
  }'
```

### 会话消息历史（method: opencode.sessions.messages.list）

```bash
curl -sS http://127.0.0.1:8000/ \
  -H 'content-type: application/json' \
  -H 'Authorization: Bearer <your-token>' \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "opencode.sessions.messages.list",
    "params": {
      "session_id": "<session_id>",
      "page": 1,
      "size": 50
    }
  }'
```

## 鉴权示例（curl）

```bash
curl -sS http://127.0.0.1:8000/v1/message:send \
  -H 'content-type: application/json' \
  -H 'Authorization: Bearer <your-token>' \
  -d '{
    "message": {
      "messageId": "msg-1",
      "role": "ROLE_USER",
      "content": [{"text": "你好，介绍下这个仓库"}]
    }
  }'
```

## 鉴权示例（JWT 模式）

Token 需为合法的 JWT 且必须包含 `exp`。服务端必须配置 `A2A_JWT_ISSUER` 与 `A2A_JWT_AUDIENCE`。若设置了 `A2A_REQUIRED_SCOPES`，Token 的 `scope` 或 `scp` 声明需满足 `A2A_JWT_SCOPE_MATCH` 规则（支持字符串或数组）。

```bash
curl -sS http://127.0.0.1:8000/v1/message:send \
  -H 'Authorization: Bearer <your-jwt-token>' \
  ...
```

## 本地调试：生成 RS256 JWT（最小示例）

该服务不负责签发 JWT；生产环境建议由认证服务（例如 Compass）签发。

本段仅用于本地调试快速生成可用 token。

1) 生成 RSA keypair（私钥用于签发，公钥用于服务端验签）：

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out jwt_private.pem
openssl pkey -in jwt_private.pem -pubout -out jwt_public.pem
```

2) 启动服务（使用公钥验签）：

```bash
export A2A_JWT_SECRET_FILE=./jwt_public.pem
export A2A_JWT_ALGORITHM=RS256
export A2A_JWT_ISSUER=my-issuer
export A2A_JWT_AUDIENCE=my-audience

./.venv/bin/opencode-a2a-serve
```

3) 用私钥签发一个短期 token（`exp` 必填；可选 `scope`）：

```bash
TOKEN="$(./.venv/bin/python - <<'PY'
import time, jwt
priv = open("jwt_private.pem", "r", encoding="utf-8").read()
payload = {
  "iss": "my-issuer",
  "aud": "my-audience",
  "exp": int(time.time()) + 3600,
  "scope": "opencode",
}
print(jwt.encode(payload, priv, algorithm="RS256"))
PY
)"
echo "$TOKEN"
```

4) 带上 token 调用：

```bash
curl -sS http://127.0.0.1:8000/v1/message:send \
  -H "Authorization: Bearer ${TOKEN}" \
  -H 'content-type: application/json' \
  -d '{"message":{"message_id":"msg-1","role":"user","parts":[{"kind":"text","text":"hello"}]}}'
```

## Streaming 断线续订（resubscribe）

当 SSE 连接中断时，可通过 `POST /v1/tasks/{task_id}:resubscribe` 重新订阅事件流（需保持 task 未进入终态）。

## A2A 客户端示例（a2a-sdk + AuthInterceptor）

> 说明：a2a-sdk 0.3.17 的 REST transport 未应用 interceptors，本项目提供了修正封装。

```python
import asyncio
import os

import httpx
from a2a.client.auth.credentials import InMemoryContextCredentialStore
from a2a.client.auth.interceptor import AuthInterceptor
from a2a.client.client_factory import ClientConfig
from a2a.client.middleware import ClientCallContext
from a2a.types import Message, Role, TextPart, TransportProtocol

from opencode_a2a.a2a_client import connect_with_patched_rest


async def main() -> None:
    base_url = "http://127.0.0.1:8000"
    token = os.environ["A2A_JWT_TOKEN"]

    store = InMemoryContextCredentialStore()
    session_id = "auth-demo"
    await store.set_credentials(session_id, "bearerAuth", token)

    context = ClientCallContext(state={"sessionId": session_id})
    interceptors = [AuthInterceptor(store)]
    config = ClientConfig(
        supported_transports=[TransportProtocol.http_json],
        httpx_client=httpx.AsyncClient(),
        streaming=False,
    )

    client = await connect_with_patched_rest(
        base_url, client_config=config, interceptors=interceptors
    )

    message = Message(
        message_id="msg-1",
        role=Role.user,
        parts=[TextPart(text="hello")],
    )

    async for _ in client.send_message(message, context=context):
        break

    await config.httpx_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
```

## 代码规范

```bash
uv run pre-commit install
```

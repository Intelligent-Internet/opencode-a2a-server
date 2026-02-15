# OpenCode OpenAPI Snapshot

本目录保存本地可查询的 OpenCode OpenAPI 快照，便于离线检索字段与接口契约。

## Current snapshot

- Source endpoint: `http://127.0.0.1:4096/doc`
- OpenCode CLI: `1.2.4`
- OpenAPI info.version: `0.0.3`
- File: `docs/operations/opencode/openapi-serve-1.2.4.json`
- Captured at: `2026-02-15`

## Refresh snapshot

1. Install and run OpenCode server locally:

```bash
curl -fsSL https://opencode.ai/install | bash
opencode serve --hostname 127.0.0.1 --port 4096
```

2. In another shell, refresh file:

```bash
curl -sS http://127.0.0.1:4096/doc | jq . > docs/operations/opencode/openapi-serve-1.2.4.json
```

3. If OpenCode version changed, duplicate a new versioned file and update this document.

## Notes

- `/openapi.json` 在当前版本返回的是页面内容，不是规范 JSON；请使用 `/doc`。

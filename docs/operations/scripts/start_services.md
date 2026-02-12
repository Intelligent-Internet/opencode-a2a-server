# Script Reference: `start_services.sh`

## Purpose

Run OpenCode and A2A locally in the foreground without systemd.

## Script Path

- `scripts/start_services.sh`

## Prerequisites

- `opencode` executable available (`PATH` or `~/.opencode/bin/opencode`)
- `uv` executable available

## Inputs

Common environment variables:

- `A2A_HOST` (default `127.0.0.1`)
- `A2A_PORT` (default `8000`)
- `A2A_PUBLIC_URL` (default `http://${A2A_HOST}:${A2A_PORT}`)
- `OPENCODE_LOG_LEVEL` (default `DEBUG`)
- `A2A_LOG_LEVEL` (default `DEBUG`)
- `LOG_ROOT` / `LOG_DIR`

## Usage

```bash
./scripts/start_services.sh
```

## Outputs and Side Effects

- Starts `opencode serve` and `uv run opencode-a2a-serve`
- Writes logs into timestamped `logs/<timestamp>/` directory by default
- Stops both processes on `Ctrl+C`

## Failure and Recovery

- If startup fails, check log paths printed by the script.
- Re-run after fixing missing `opencode`/`uv` dependencies.

## Related Docs

- `docs/guide.md`
- `docs/operations/scripts/index.md`

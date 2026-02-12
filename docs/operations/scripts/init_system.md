# Script Reference: `init_system.sh`

## Purpose

Prepare shared host prerequisites for systemd-based OpenCode + A2A deployment.

## Script Path

- `scripts/init_system.sh`

## Prerequisites

- Linux host with `systemd`
- Root or `sudo` privileges
- Network access for package/repository downloads

## Inputs

- No runtime arguments are supported.
- Behavior is controlled by top-level constants inside the script (for example paths, package toggles, repo URL, branch, and Node/Python versions).

## Outputs and Side Effects

- Installs required packages and tooling (`gh`, Node.js >= 20, `uv` when enabled)
- Creates shared directories (for example `/opt/.opencode`, `/opt/opencode-a2a`, `/data/opencode-a2a`)
- Prepares the A2A virtual environment in the shared repository
- Clones this repository (default HTTPS URL)

## Usage

```bash
./scripts/init_system.sh
```

## Failure and Recovery

- The script is idempotent and can be re-run after partial failure.
- If package manager specific steps fail, inspect the error output and re-run after fixing host networking or repository settings.

## Related Docs

- `docs/init_system.md`
- `docs/deployment.md` (`Optional System Bootstrap`)

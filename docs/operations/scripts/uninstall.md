# Script Reference: `uninstall.sh`

## Purpose

Remove one deployed instance created by `scripts/deploy.sh`.

## Script Path

- `scripts/uninstall.sh`

## Safety Model

- Always prints a preview first.
- Destructive actions require explicit confirmation: `confirm=UNINSTALL`.
- Shared systemd templates are never removed.

## Inputs

CLI keys:

- `project`/`project_name` (required)
- `data_root` (optional, default `/data/opencode-a2a`)
- `confirm` (set to `UNINSTALL` for apply mode)

## Usage

Preview only:

```bash
./scripts/uninstall.sh project=alpha
```

Apply uninstall:

```bash
./scripts/uninstall.sh project=alpha confirm=UNINSTALL
```

## Outputs and Side Effects

- Stops/disables per-project systemd units
- Removes per-project files/directories
- Removes per-project user/group when applicable

## Failure and Recovery

- In preview mode, inspect printed commands before applying.
- In apply mode, the script uses strict path/project-name validation to reduce accidental deletion risk.

## Related Docs

- `docs/deployment.md` (`Uninstall One Instance`)
- `docs/operations/scripts/index.md`

# Script Reference: `deploy.sh`

## Purpose

Create or update one isolated OpenCode + A2A systemd instance.

## Script Path

- `scripts/deploy.sh`

## Prerequisites

- `sudo` privileges
- Host already prepared for systemd deployment
- Required secrets provided as environment variables

## Inputs

Required secret environment variables:

- `GH_TOKEN`
- `A2A_BEARER_TOKEN`

Optional provider secret environment variables:

- `GOOGLE_GENERATIVE_AI_API_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `AZURE_OPENAI_API_KEY`
- `OPENROUTER_API_KEY`

Selected CLI keys (`key=value`) are accepted for non-secret configuration:

- `project`/`project_name`
- `a2a_port`, `a2a_host`, `a2a_public_url`
- `opencode_provider_id`, `opencode_model_id`
- `repo_url`, `repo_branch`
- `opencode_timeout`, `opencode_timeout_stream`
- `git_identity_name`, `git_identity_email`
- `update_a2a`, `force_restart`

Sensitive CLI keys are intentionally rejected.

## Usage

```bash
GH_TOKEN='<gh-token>' A2A_BEARER_TOKEN='<a2a-token>' \
./scripts/deploy.sh project=alpha a2a_port=8010 a2a_host=127.0.0.1
```

## Outputs and Side Effects

- Installs/updates systemd templates
- Creates instance user/directories/config files
- Starts or restarts `opencode@<project>.service` and `opencode-a2a@<project>.service`

## Failure and Recovery

- Re-run with corrected inputs; deploy flow is designed to be repeatable.
- For full troubleshooting and config details, follow `docs/deployment.md`.

## Related Docs

- `docs/deployment.md`
- `docs/operations/scripts/index.md`

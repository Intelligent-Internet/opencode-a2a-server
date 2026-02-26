# AGENTS.md

The following rules apply to coding-agent collaboration and delivery in this repository.

## 1. Core Principles

- Move tasks forward safely and traceably, while avoiding unnecessary process blockers.
- Stay consistent with the existing repository structure, implementation style, and engineering conventions.

## 2. Git Workflow

- Do not commit or push directly to protected branches: `main`/`master`/`release/*`.
- Implement each development task in an isolated branch, preferably cut from the latest mainline.
- To sync mainline, prefer `git fetch` + `git merge --ff-only` and avoid implicit merges.
- Pushing a development branch to a same-name remote branch is allowed for collaboration and backup.
- Do not rewrite shared history: no `git push --force`, `git push --force-with-lease`, or arbitrary `rebase`.
- Commit only files related to the current task; do not clean up or roll back unrelated local changes.

## 3. Issue and PR Collaboration

- Before starting development work, check whether a related open Issue already exists (for example, `gh issue list --state open`).
- If none exists, create a new Issue for tracking. The Issue should include context, reproduction steps, expected/actual behavior, acceptance criteria, and a `git rev-parse HEAD` snapshot.
- Changes limited to collaboration/process documents (for example, `AGENTS.md`) may be made directly without creating an additional Issue.
- Recommended Issue title prefixes: `[feat]`, `[bug]`, `[docs]`, `[ops]`, `[chore]`.
- If a commit serves an Issue, reference the Issue ID in the commit message (for example, `#issue`).
- PRs are recommended to start as Draft by default, with relationship markers in the description (for example, `Closes #xx` / `Relates to #xx`).
- When key progress, plan changes, or new risks arise, synchronize updates in the related Issue/PR promptly to avoid repetitive comments.

## 4. Tooling and Text Conventions

- Use the `gh` CLI for reading/writing Issues and PRs; do not edit via web UI manually.
- Use Simplified Chinese for Issues, PRs, and comments. English technical terms may be retained.
- For multi-line bodies, write to a temp file first and pass it via `--body-file`; do not concatenate `\\n` in `--body`.
- For same-repo references, use `#123` auto-linking; for cross-repo references, use full URLs.

## 5. Regression and Validation

- Choose regression strategy by change type. Default baseline:
  - `uv run pre-commit run --all-files`
  - `uv run pytest`
- If `pre-commit` auto-fixes files (for example, `ruff --fix`), review those changes before committing.
- For shell/deployment script changes, run `bash -n` on modified scripts in addition to the baseline.
- For docs-only changes, tests may be skipped, but command and path examples must be self-verified.
- `uv sync --all-extras` is only needed during first-time setup or dependency changes; it is not required for every change.
- If any validation cannot be completed due to environment constraints, clearly state what was not run and why.

## 6. Security and Configuration

- Never commit keys, tokens, credentials, or other sensitive information (including `.env` contents).
- Logs and debug output must not leak access tokens or private data.
- For changes involving deployment, authentication, or secret injection, update documentation together and provide minimal acceptance steps.

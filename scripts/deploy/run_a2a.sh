#!/usr/bin/env bash
# Wrapper to run opencode-a2a-serve from the shared venv.
set -euo pipefail

OPENCODE_A2A_DIR="${OPENCODE_A2A_DIR:-/opt/opencode-a2a/opencode-a2a-serve}"
A2A_BIN="${A2A_BIN:-${OPENCODE_A2A_DIR}/.venv/bin/opencode-a2a-serve}"

if [[ ! -x "$A2A_BIN" ]]; then
  echo "opencode-a2a-serve entrypoint not found at $A2A_BIN" >&2
  exit 1
fi

auth_mode="${A2A_AUTH_MODE:-bearer}"
auth_mode="${auth_mode,,}"

if [[ "$auth_mode" != "bearer" && "$auth_mode" != "jwt" ]]; then
  echo "A2A_AUTH_MODE must be bearer or jwt" >&2
  exit 1
fi

if [[ "$auth_mode" == "bearer" ]]; then
  if [[ -z "${A2A_BEARER_TOKEN:-}" ]]; then
    echo "A2A_BEARER_TOKEN is required when A2A_AUTH_MODE=bearer" >&2
    exit 1
  fi
else
  if [[ -z "${A2A_JWT_SECRET:-}" && -z "${A2A_JWT_SECRET_B64:-}" && -z "${A2A_JWT_SECRET_FILE:-}" ]]; then
    echo "JWT mode requires one of A2A_JWT_SECRET/A2A_JWT_SECRET_B64/A2A_JWT_SECRET_FILE" >&2
    exit 1
  fi
  if [[ -n "${A2A_JWT_SECRET_FILE:-}" ]]; then
    jwt_secret_file="${A2A_JWT_SECRET_FILE}"
    if [[ "$jwt_secret_file" == "~/"* ]]; then
      jwt_secret_file="${HOME}/${jwt_secret_file#~/}"
    elif [[ "$jwt_secret_file" == "~" ]]; then
      jwt_secret_file="${HOME}"
    fi
    if [[ ! -r "$jwt_secret_file" ]]; then
      echo "A2A_JWT_SECRET_FILE is not readable: ${A2A_JWT_SECRET_FILE}" >&2
      exit 1
    fi
  fi
  jwt_algorithm_upper="${A2A_JWT_ALGORITHM:-RS256}"
  jwt_algorithm_upper="${jwt_algorithm_upper^^}"
  case "$jwt_algorithm_upper" in
    RS256|RS384|RS512|PS256|PS384|PS512|ES256|ES384|ES512|EDDSA) ;;
    *)
      echo "A2A_JWT_ALGORITHM must be one of RS256/RS384/RS512/PS256/PS384/PS512/ES256/ES384/ES512/EdDSA" >&2
      exit 1
      ;;
  esac
  if [[ -n "${A2A_JWT_SECRET:-}" && "${A2A_JWT_SECRET}" == *"PRIVATE KEY"* ]]; then
    echo "A2A_JWT_SECRET must be a public verification key, not a private key" >&2
    exit 1
  fi
  if [[ -z "${A2A_JWT_ISSUER:-}" || -z "${A2A_JWT_AUDIENCE:-}" ]]; then
    echo "JWT mode requires both A2A_JWT_ISSUER and A2A_JWT_AUDIENCE" >&2
    exit 1
  fi
fi

exec "$A2A_BIN"

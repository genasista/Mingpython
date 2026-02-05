#!/bin/bash
set -euo pipefail

load_secret() {
    local secret_name="$1"
    local env_var="$2"
    local secret_path="/run/secrets/${secret_name}"

    if [[ -f "$secret_path" && -z "${!env_var:-}" ]]; then
        export "${env_var}"="$(tr -d '\r\n' < "$secret_path")"
    fi
}

load_secret "python_api_key" "PYTHON_API_KEY"
load_secret "groq_api_key" "GROQ_API_KEY"
load_secret "openai_api_key" "OPENAI_API_KEY"
load_secret "admin_token" "ADMIN_TOKEN"
load_secret "legacy_api_key" "API_KEY"

# Set default port if not provided
export PORT="${PORT:-8001}"

exec "$@"


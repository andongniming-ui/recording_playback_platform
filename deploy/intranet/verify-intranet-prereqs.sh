#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE_INPUT="${1:-${SCRIPT_DIR}/.env.production}"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.intranet.yml"

fail() {
  echo "[FAIL] $*" >&2
  exit 1
}

ok() {
  echo "[ OK ] $*"
}

[[ -f "${ENV_FILE_INPUT}" ]] || fail "Missing env file: ${ENV_FILE_INPUT}"
ENV_FILE="$(cd "$(dirname "${ENV_FILE_INPUT}")" && pwd)/$(basename "${ENV_FILE_INPUT}")"
! grep -q "CHANGE_ME" "${ENV_FILE}" || fail "${ENV_FILE} still contains CHANGE_ME placeholders"

env_value() {
  local key="$1"
  grep -E "^${key}=" "${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- | sed "s/^['\"]//;s/['\"]$//"
}

require_env() {
  local key="$1"
  local value
  value="$(env_value "${key}")"
  [[ -n "${value}" ]] || fail "${key} is required in ${ENV_FILE}"
  [[ "${value}" != *"x.x"* ]] || fail "${key} still looks like a placeholder: ${value}"
  [[ "${value}" != build_placeholder* ]] || fail "${key} is still a build placeholder"
}

for key in \
  MYSQL_ROOT_PASSWORD MYSQL_PASSWORD AR_DB_URL AR_SECRET_KEY AR_ADMIN_INIT_PASSWORD \
  PLATFORM_HOST FRONTEND_PUBLIC_ORIGIN BACKEND_PUBLIC_ORIGIN VITE_API_BASE_URL AR_CORS_ORIGINS
do
  require_env "${key}"
done

secret="$(env_value AR_SECRET_KEY)"
case "${secret}" in
  local-dev-only-change-this-secret-key|please-change-this-dev-only|changeme-in-production|local-dev-change-before-production-2026)
    fail "AR_SECRET_KEY uses a known weak development value"
    ;;
esac
[[ "${#secret}" -ge 32 ]] || fail "AR_SECRET_KEY must be at least 32 characters"

enforce_secret="$(env_value AR_ENFORCE_SECURE_SECRET)"
[[ "${enforce_secret}" == "true" ]] || fail "AR_ENFORCE_SECURE_SECRET must be true for intranet deployment"

docker version >/dev/null || fail "Docker is not available"
docker compose version >/dev/null || fail "Docker Compose v2 is not available"
ok "Docker and Docker Compose are available"

agent_version="$(grep -E '^AREX_AGENT_VERSION=' "${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- | tr -d '"' | tr -d "'" || true)"
agent_version="${agent_version:-0.4.8}"
agent_file="${SCRIPT_DIR}/third_party/arex-agent/arex-agent-${agent_version}.jar"
[[ -f "${agent_file}" ]] || fail "Missing AREX agent: ${agent_file}"
ok "AREX agent exists: ${agent_file}"

docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" config --services >/tmp/arex-recorder-compose-services.txt
grep -q '^db$' /tmp/arex-recorder-compose-services.txt || fail "Compose db service missing"
grep -q '^backend$' /tmp/arex-recorder-compose-services.txt || fail "Compose backend service missing"
grep -q '^frontend$' /tmp/arex-recorder-compose-services.txt || fail "Compose frontend service missing"
ok "Docker Compose config is valid"

backend_image="$(env_value BACKEND_IMAGE)"
frontend_image="$(env_value FRONTEND_IMAGE)"
mysql_image="$(env_value MYSQL_IMAGE)"

build_images="$(env_value BUILD_IMAGES)"
build_images="${build_images:-false}"
[[ "${build_images}" == "false" || "${build_images}" == "0" ]] || fail "BUILD_IMAGES must be false inside the intranet; prebuild images outside and import them first"
docker image inspect "${backend_image}" >/dev/null || fail "Missing loaded backend image: ${backend_image}"
docker image inspect "${frontend_image}" >/dev/null || fail "Missing loaded frontend image: ${frontend_image}"
docker image inspect "${mysql_image}" >/dev/null || fail "Missing loaded MySQL image: ${mysql_image}"
ok "Offline images are loaded"

platform_host="$(env_value PLATFORM_HOST)"
[[ -n "${platform_host}" ]] || fail "PLATFORM_HOST is empty"
[[ "${platform_host}" != *"x.x"* ]] || fail "PLATFORM_HOST still looks like a placeholder: ${platform_host}"
ok "PLATFORM_HOST configured: ${platform_host}"

echo "Prerequisite check passed."

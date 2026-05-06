#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${1:-${SCRIPT_DIR}/.env.production}"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.intranet.yml"

fail() {
  echo "[FAIL] $*" >&2
  exit 1
}

ok() {
  echo "[ OK ] $*"
}

[[ -f "${ENV_FILE}" ]] || fail "Missing env file: ${ENV_FILE}"
! grep -q "CHANGE_ME" "${ENV_FILE}" || fail "${ENV_FILE} still contains CHANGE_ME placeholders"

docker version >/dev/null || fail "Docker is not available"
docker compose version >/dev/null || fail "Docker Compose v2 is not available"
ok "Docker and Docker Compose are available"

agent_version="$(grep -E '^AREX_AGENT_VERSION=' "${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- | tr -d '"' | tr -d "'" || true)"
agent_version="${agent_version:-0.4.8}"
agent_file="${SCRIPT_DIR}/third_party/arex-agent/arex-agent-${agent_version}.jar"
[[ -f "${agent_file}" ]] || fail "Missing AREX agent: ${agent_file}"
ok "AREX agent exists: ${agent_file}"

ENV_FILE="$(basename "${ENV_FILE}")" docker compose --env-file "${SCRIPT_DIR}/${ENV_FILE}" -f "${COMPOSE_FILE}" config --services >/tmp/arex-recorder-compose-services.txt
grep -q '^db$' /tmp/arex-recorder-compose-services.txt || fail "Compose db service missing"
grep -q '^backend$' /tmp/arex-recorder-compose-services.txt || fail "Compose backend service missing"
grep -q '^frontend$' /tmp/arex-recorder-compose-services.txt || fail "Compose frontend service missing"
ok "Docker Compose config is valid"

backend_image="$(grep -E '^BACKEND_IMAGE=' "${SCRIPT_DIR}/${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- || true)"
frontend_image="$(grep -E '^FRONTEND_IMAGE=' "${SCRIPT_DIR}/${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- || true)"
mysql_image="$(grep -E '^MYSQL_IMAGE=' "${SCRIPT_DIR}/${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- || true)"

build_images="$(grep -E '^BUILD_IMAGES=' "${SCRIPT_DIR}/${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- || true)"
if [[ "${build_images}" == "false" || "${build_images}" == "0" ]]; then
  docker image inspect "${backend_image}" >/dev/null || fail "Missing loaded backend image: ${backend_image}"
  docker image inspect "${frontend_image}" >/dev/null || fail "Missing loaded frontend image: ${frontend_image}"
  docker image inspect "${mysql_image}" >/dev/null || fail "Missing loaded MySQL image: ${mysql_image}"
  ok "Offline images are loaded"
fi

platform_host="$(grep -E '^PLATFORM_HOST=' "${SCRIPT_DIR}/${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- || true)"
[[ -n "${platform_host}" ]] || fail "PLATFORM_HOST is empty"
[[ "${platform_host}" != *"x.x"* ]] || fail "PLATFORM_HOST still looks like a placeholder: ${platform_host}"
ok "PLATFORM_HOST configured: ${platform_host}"

echo "Prerequisite check passed."

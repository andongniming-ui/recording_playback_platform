#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env.production"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.intranet.yml"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Copy .env.production.example to .env.production and edit it first." >&2
  exit 1
fi

if grep -q "CHANGE_ME" "${ENV_FILE}"; then
  echo "${ENV_FILE} still contains CHANGE_ME placeholders." >&2
  exit 1
fi

"${SCRIPT_DIR}/verify-intranet-prereqs.sh" "${ENV_FILE}"

agent_version="$(grep -E '^AREX_AGENT_VERSION=' "${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- | tr -d '"' | tr -d "'" || true)"
agent_version="${agent_version:-0.4.8}"
agent_file="${SCRIPT_DIR}/third_party/arex-agent/arex-agent-${agent_version}.jar"
if [[ ! -f "${agent_file}" ]]; then
  echo "Missing fixed AREX agent: ${agent_file}" >&2
  exit 1
fi

build_images="$(grep -E '^BUILD_IMAGES=' "${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- | sed "s/^['\"]//;s/['\"]$//" || true)"
build_images="${build_images:-false}"
if [[ "${build_images}" != "false" && "${build_images}" != "0" ]]; then
  echo "BUILD_IMAGES must be false for intranet deployment. Build images on the external-network machine and import them first." >&2
  exit 1
fi

docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" up -d --no-build
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" ps

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env.ai-gateway"
COMPOSE_FILE="${ROOT_DIR}/ai-gateway/docker-compose.yml"

if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${SCRIPT_DIR}/.env.ai-gateway.example" "${ENV_FILE}"
  echo "Created ${ENV_FILE}. Edit it (set MYSQL_ROOT_PASSWORD) then re-run this script." >&2
  exit 1
fi

if grep -q "CHANGE_ME" "${ENV_FILE}"; then
  echo "${ENV_FILE} still contains CHANGE_ME placeholders." >&2
  exit 1
fi

docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" up -d
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" ps

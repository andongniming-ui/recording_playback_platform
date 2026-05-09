#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash apply-incremental-update.sh <target-project-dir> [--rebuild auto|none|backend|frontend|all]

Run this script inside an extracted intranet incremental package.

Examples:
  bash apply-incremental-update.sh /opt/recording_playback_platform
  bash apply-incremental-update.sh /opt/recording_playback_platform --rebuild backend
  bash apply-incremental-update.sh /opt/recording_playback_platform --rebuild none
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-}"
REBUILD_MODE="auto"

if [[ -z "${TARGET_DIR}" || "${TARGET_DIR}" == "-h" || "${TARGET_DIR}" == "--help" ]]; then
  usage
  exit 0
fi
shift || true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --rebuild)
      REBUILD_MODE="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "${REBUILD_MODE}" in
  auto|none|backend|frontend|all) ;;
  *)
    echo "Invalid --rebuild value: ${REBUILD_MODE}" >&2
    exit 2
    ;;
esac

FILES_DIR="${SCRIPT_DIR}/files"
CHANGED_FILE="${SCRIPT_DIR}/changed-files.txt"
DELETED_FILE="${SCRIPT_DIR}/deleted-files.txt"
META_FILE="${SCRIPT_DIR}/manifest.env"

if [[ ! -d "${FILES_DIR}" ]]; then
  echo "Missing package files directory: ${FILES_DIR}" >&2
  exit 1
fi

if [[ ! -d "${TARGET_DIR}" ]]; then
  echo "Target project directory does not exist: ${TARGET_DIR}" >&2
  exit 1
fi

if [[ ! -f "${TARGET_DIR}/deploy/intranet/docker-compose.intranet.yml" ]]; then
  echo "Target does not look like recording_playback_platform: ${TARGET_DIR}" >&2
  exit 1
fi

safe_relpath() {
  local path="$1"
  [[ -n "${path}" ]] || return 1
  [[ "${path}" != /* ]] || return 1
  [[ "${path}" != "." ]] || return 1
  [[ "${path}" != ".." ]] || return 1
  [[ "${path}" != ../* ]] || return 1
  [[ "${path}" != */../* ]] || return 1
}

BACKUP_ROOT="${TARGET_DIR}/runtime/intranet-update-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="${BACKUP_ROOT}/${STAMP}"
mkdir -p "${BACKUP_DIR}"

backup_path() {
  local rel="$1"
  local src="${TARGET_DIR}/${rel}"
  if [[ -e "${src}" || -L "${src}" ]]; then
    mkdir -p "${BACKUP_DIR}/$(dirname "${rel}")"
    cp -a "${src}" "${BACKUP_DIR}/${rel}"
  fi
}

echo "[INFO] Applying package: ${SCRIPT_DIR}"
if [[ -f "${META_FILE}" ]]; then
  sed -n '1,80p' "${META_FILE}" | sed 's/^/[META] /'
fi

if [[ -s "${CHANGED_FILE}" ]]; then
  while IFS= read -r rel || [[ -n "${rel}" ]]; do
    [[ -n "${rel}" ]] || continue
    if ! safe_relpath "${rel}"; then
      echo "Unsafe changed path in package: ${rel}" >&2
      exit 1
    fi
    backup_path "${rel}"
  done < "${CHANGED_FILE}"
fi

if [[ -s "${DELETED_FILE}" ]]; then
  while IFS= read -r rel || [[ -n "${rel}" ]]; do
    [[ -n "${rel}" ]] || continue
    if ! safe_relpath "${rel}"; then
      echo "Unsafe deleted path in package: ${rel}" >&2
      exit 1
    fi
    backup_path "${rel}"
  done < "${DELETED_FILE}"
fi

if find "${BACKUP_DIR}" -mindepth 1 -print -quit | grep -q .; then
  backup_tar="${BACKUP_ROOT}/${STAMP}.tar.gz"
  (cd "${BACKUP_DIR}" && tar -czf "${backup_tar}" .)
  rm -rf "${BACKUP_DIR}"
  echo "[INFO] Backup written: ${backup_tar}"
else
  rmdir "${BACKUP_DIR}" 2>/dev/null || true
  echo "[INFO] No existing target files needed backup."
fi

echo "[INFO] Copying changed files..."
(cd "${FILES_DIR}" && tar -cf - .) | (cd "${TARGET_DIR}" && tar -xf -)

if [[ -s "${DELETED_FILE}" ]]; then
  echo "[INFO] Removing deleted files..."
  while IFS= read -r rel || [[ -n "${rel}" ]]; do
    [[ -n "${rel}" ]] || continue
    safe_relpath "${rel}" || {
      echo "Unsafe deleted path in package: ${rel}" >&2
      exit 1
    }
    rm -rf "${TARGET_DIR:?}/${rel}"
  done < "${DELETED_FILE}"
fi

find "${TARGET_DIR}" \( -path '*/deploy/*.sh' -o -path '*/scripts/*.sh' \) -type f | xargs -r chmod +x

backend_changed=false
frontend_changed=false
dependency_changed=false

if [[ -s "${CHANGED_FILE}" || -s "${DELETED_FILE}" ]]; then
  combined="$(mktemp)"
  cat "${CHANGED_FILE}" "${DELETED_FILE}" 2>/dev/null > "${combined}" || true
  if grep -qE '^(platform/backend/|platform/requirements\.txt|platform/backend/Dockerfile)' "${combined}"; then
    backend_changed=true
  fi
  if grep -qE '^(platform/frontend/|platform/frontend/Dockerfile)' "${combined}"; then
    frontend_changed=true
  fi
  if grep -qE '^(platform/requirements\.txt|platform/frontend/package(-lock)?\.json)' "${combined}"; then
    dependency_changed=true
  fi
  rm -f "${combined}"
fi

if [[ "${dependency_changed}" == "true" ]]; then
  echo "[WARN] Dependency files changed. In an offline intranet, rebuild may require refreshing the offline bundle/cache first."
fi

if [[ "${REBUILD_MODE}" == "none" ]]; then
  echo "[INFO] Skipping docker rebuild because --rebuild none was selected."
  exit 0
fi

services=()
case "${REBUILD_MODE}" in
  backend) services=(backend) ;;
  frontend) services=(frontend) ;;
  all) services=(backend frontend) ;;
  auto)
    [[ "${backend_changed}" == "true" ]] && services+=(backend)
    [[ "${frontend_changed}" == "true" ]] && services+=(frontend)
    ;;
esac

if [[ ${#services[@]} -eq 0 ]]; then
  echo "[INFO] No backend/frontend changes detected; docker rebuild skipped."
  exit 0
fi

COMPOSE_DIR="${TARGET_DIR}/deploy/intranet"
ENV_FILE="${COMPOSE_DIR}/.env.production"
COMPOSE_FILE="${COMPOSE_DIR}/docker-compose.intranet.yml"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "[WARN] Missing ${ENV_FILE}; files were updated but docker rebuild was skipped."
  exit 0
fi

echo "[INFO] Rebuilding services: ${services[*]}"
(cd "${COMPOSE_DIR}" && docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" up -d --build "${services[@]}")
(cd "${COMPOSE_DIR}" && docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" ps)

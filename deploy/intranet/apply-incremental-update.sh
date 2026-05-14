#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash apply-incremental-update.sh <target-project-dir> [--rebuild auto|none|backend|frontend|all]

Run this script inside an extracted intranet incremental package.
For offline intranet safety, this script never runs docker build. Backend/frontend
updates must include prebuilt images under docker/ in the package.

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
DOCKER_DIR="${SCRIPT_DIR}/docker"

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
STAGING_DIR="${BACKUP_ROOT}/${STAMP}.staging"
COMPOSE_DIR="${TARGET_DIR}/deploy/intranet"
ENV_FILE="${COMPOSE_DIR}/.env.production"
COMPOSE_FILE="${COMPOSE_DIR}/docker-compose.intranet.yml"
BACKUP_TAR=""
MYSQL_BACKUP_GZ=""
ROLLBACK_SCRIPT="${BACKUP_ROOT}/${STAMP}-rollback.sh"
mkdir -p "${BACKUP_DIR}"
rm -rf "${STAGING_DIR}"

cleanup_staging() {
  rm -rf "${STAGING_DIR}"
}
trap cleanup_staging EXIT

backup_path() {
  local rel="$1"
  local src="${TARGET_DIR}/${rel}"
  if [[ -e "${src}" || -L "${src}" ]]; then
    mkdir -p "${BACKUP_DIR}/$(dirname "${rel}")"
    cp -a "${src}" "${BACKUP_DIR}/${rel}"
  fi
}

env_value() {
  local file="$1" key="$2"
  grep -E "^${key}=" "${file}" | tail -n 1 | cut -d '=' -f 2- | sed "s/^['\"]//;s/['\"]$//"
}

backup_mysql_if_running() {
  if [[ "${SKIP_DB_BACKUP:-false}" == "true" ]]; then
    echo "[WARN] Skipping MySQL backup because SKIP_DB_BACKUP=true."
    return
  fi
  command -v docker >/dev/null 2>&1 || {
    echo "[WARN] Docker is not available; MySQL backup skipped."
    return
  }
  if ! docker ps --format '{{.Names}}' | grep -q '^arex-recorder-mysql$'; then
    echo "[INFO] MySQL container is not running; database backup skipped."
    return
  fi

  local env_file="${TARGET_DIR}/deploy/intranet/.env.production"
  [[ -f "${env_file}" ]] || {
    echo "[WARN] Missing ${env_file}; MySQL backup skipped."
    return
  }

  local root_password database backup_sql
  root_password="$(env_value "${env_file}" MYSQL_ROOT_PASSWORD)"
  database="$(env_value "${env_file}" MYSQL_DATABASE)"
  database="${database:-arex_recorder}"
  [[ -n "${root_password}" ]] || {
    echo "MYSQL_ROOT_PASSWORD is empty; refusing to apply update without database backup." >&2
    exit 1
  }

  mkdir -p "${BACKUP_ROOT}"
  backup_sql="${BACKUP_ROOT}/${STAMP}-${database}.sql"
  MYSQL_BACKUP_GZ="${backup_sql}.gz"
  echo "[INFO] Backing up MySQL database ${database}..."
  docker exec -e MYSQL_PWD="${root_password}" arex-recorder-mysql \
    mysqldump -uroot --single-transaction --routines --triggers --databases "${database}" \
    > "${backup_sql}"
  gzip -f "${backup_sql}"
  echo "[INFO] MySQL backup written: ${MYSQL_BACKUP_GZ}"
}

write_rollback_script() {
  cat > "${ROLLBACK_SCRIPT}" <<EOF
#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="\${1:-${TARGET_DIR}}"
BACKUP_TAR="${BACKUP_TAR}"
MYSQL_BACKUP_GZ="${MYSQL_BACKUP_GZ}"
STAMP="${STAMP}"
COMPOSE_DIR="\${TARGET_DIR}/deploy/intranet"
ENV_FILE="\${COMPOSE_DIR}/.env.production"
COMPOSE_FILE="\${COMPOSE_DIR}/docker-compose.intranet.yml"

env_value() {
  local file="\$1" key="\$2"
  local value
  value="\$(grep -E "^\${key}=" "\${file}" | tail -n 1 | cut -d '=' -f 2- || true)"
  value="\${value#\"}"
  value="\${value%\"}"
  value="\${value#\'}"
  value="\${value%\'}"
  printf '%s' "\${value}"
}

if [[ -n "\${BACKUP_TAR}" && -f "\${BACKUP_TAR}" ]]; then
  echo "[ROLLBACK] Restoring files from \${BACKUP_TAR}"
  tar -xzf "\${BACKUP_TAR}" -C "\${TARGET_DIR}"
else
  echo "[ROLLBACK] No file backup tar found; skipping file restore."
fi

if command -v docker >/dev/null 2>&1 && [[ -f "\${ENV_FILE}" ]]; then
  backend_image="\$(env_value "\${ENV_FILE}" BACKEND_IMAGE)"
  frontend_image="\$(env_value "\${ENV_FILE}" FRONTEND_IMAGE)"
  restored_services=()
  if docker image inspect "arex-recorder-backend:rollback-\${STAMP}" >/dev/null 2>&1; then
    echo "[ROLLBACK] Restoring backend image tag \${backend_image}"
    docker tag "arex-recorder-backend:rollback-\${STAMP}" "\${backend_image}"
    restored_services+=(backend)
  fi
  if docker image inspect "arex-recorder-frontend:rollback-\${STAMP}" >/dev/null 2>&1; then
    echo "[ROLLBACK] Restoring frontend image tag \${frontend_image}"
    docker tag "arex-recorder-frontend:rollback-\${STAMP}" "\${frontend_image}"
    restored_services+=(frontend)
  fi
  if [[ \${#restored_services[@]} -gt 0 ]]; then
    (cd "\${COMPOSE_DIR}" && docker compose --env-file "\${ENV_FILE}" -f "\${COMPOSE_FILE}" up -d --no-build --force-recreate "\${restored_services[@]}")
  fi
fi

if [[ "\${RESTORE_DB:-false}" == "true" ]]; then
  if [[ -z "\${MYSQL_BACKUP_GZ}" || ! -f "\${MYSQL_BACKUP_GZ}" ]]; then
    echo "[ROLLBACK] RESTORE_DB=true but MySQL backup is missing: \${MYSQL_BACKUP_GZ}" >&2
    exit 1
  fi
  root_password="\$(env_value "\${ENV_FILE}" MYSQL_ROOT_PASSWORD)"
  echo "[ROLLBACK] Restoring MySQL backup \${MYSQL_BACKUP_GZ}"
  gunzip -c "\${MYSQL_BACKUP_GZ}" | docker exec -i -e MYSQL_PWD="\${root_password}" arex-recorder-mysql mysql -uroot
else
  echo "[ROLLBACK] Database restore skipped. Re-run with RESTORE_DB=true if database rollback is required."
fi

echo "[ROLLBACK] Done."
EOF
  chmod +x "${ROLLBACK_SCRIPT}"
  echo "[INFO] Rollback script written: ${ROLLBACK_SCRIPT}"
}

tag_current_images_for_rollback() {
  command -v docker >/dev/null 2>&1 || return 0
  [[ -f "${ENV_FILE}" ]] || return 0
  local backend_image frontend_image
  backend_image="$(env_value "${ENV_FILE}" BACKEND_IMAGE)"
  frontend_image="$(env_value "${ENV_FILE}" FRONTEND_IMAGE)"
  if [[ -n "${backend_image}" ]] && docker image inspect "${backend_image}" >/dev/null 2>&1; then
    docker tag "${backend_image}" "arex-recorder-backend:rollback-${STAMP}"
    echo "[INFO] Tagged current backend image for rollback: arex-recorder-backend:rollback-${STAMP}"
  fi
  if [[ -n "${frontend_image}" ]] && docker image inspect "${frontend_image}" >/dev/null 2>&1; then
    docker tag "${frontend_image}" "arex-recorder-frontend:rollback-${STAMP}"
    echo "[INFO] Tagged current frontend image for rollback: arex-recorder-frontend:rollback-${STAMP}"
  fi
}

echo "[INFO] Applying package: ${SCRIPT_DIR}"
if [[ -f "${META_FILE}" ]]; then
  sed -n '1,80p' "${META_FILE}" | sed 's/^/[META] /'
fi

backup_mysql_if_running

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
  BACKUP_TAR="${BACKUP_ROOT}/${STAMP}.tar.gz"
  (cd "${BACKUP_DIR}" && tar -czf "${BACKUP_TAR}" .)
  rm -rf "${BACKUP_DIR}"
  echo "[INFO] Backup written: ${BACKUP_TAR}"
else
  rmdir "${BACKUP_DIR}" 2>/dev/null || true
  echo "[INFO] No existing target files needed backup."
fi
write_rollback_script

echo "[INFO] Copying changed files..."
mkdir -p "${STAGING_DIR}"
(cd "${FILES_DIR}" && tar -cf - .) | (cd "${STAGING_DIR}" && tar -xf -)

if [[ -s "${CHANGED_FILE}" ]]; then
  while IFS= read -r rel || [[ -n "${rel}" ]]; do
    [[ -n "${rel}" ]] || continue
    safe_relpath "${rel}" || {
      echo "Unsafe changed path in package: ${rel}" >&2
      exit 1
    }
    if [[ ! -e "${STAGING_DIR}/${rel}" && ! -L "${STAGING_DIR}/${rel}" ]]; then
      echo "Changed file is listed but missing from package: ${rel}" >&2
      exit 1
    fi
    mkdir -p "${TARGET_DIR}/$(dirname "${rel}")"
    rm -rf "${TARGET_DIR:?}/${rel}"
    cp -a "${STAGING_DIR}/${rel}" "${TARGET_DIR}/${rel}"
  done < "${CHANGED_FILE}"
fi

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
  echo "[WARN] Dependency files changed. This package must include prebuilt Docker images for offline intranet use."
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

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}; files were updated but services cannot be recreated." >&2
  exit 1
fi

image_tar="${DOCKER_DIR}/arex-recorder-images.tar"
if [[ ! -f "${image_tar}" ]]; then
  echo "Package is missing prebuilt Docker images: ${image_tar}" >&2
  echo "Regenerate the package on the external-network machine with --include-images auto or --include-images always." >&2
  exit 1
fi
if [[ -f "${image_tar}.sha256" ]]; then
  (cd "${DOCKER_DIR}" && sha256sum -c "$(basename "${image_tar}.sha256")")
fi
echo "[INFO] Loading prebuilt Docker images from package..."
tag_current_images_for_rollback
docker load -i "${image_tar}"

echo "[INFO] Recreating services without docker build: ${services[*]}"
(cd "${COMPOSE_DIR}" && docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" up -d --no-build --force-recreate "${services[@]}")
(cd "${COMPOSE_DIR}" && docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" ps)

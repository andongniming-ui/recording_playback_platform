#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash record-deployment-state.sh <extracted-package-dir> [target-project-dir]

Records the current intranet deployment state without storing plaintext secrets.

Example:
  cd /home/ap/recording_playback_platform/deploy/intranet
  bash record-deployment-state.sh \
    /tmp/kaiyang-update/kaiyang-intranet-incremental-gpt-5-20260514-datafix \
    /home/ap/recording_playback_platform
EOF
}

PACKAGE_DIR="${1:-}"
TARGET_DIR="${2:-/home/ap/recording_playback_platform}"

if [[ -z "${PACKAGE_DIR}" || "${PACKAGE_DIR}" == "-h" || "${PACKAGE_DIR}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ ! -d "${PACKAGE_DIR}" ]]; then
  echo "Package directory does not exist: ${PACKAGE_DIR}" >&2
  exit 1
fi

if [[ ! -d "${TARGET_DIR}" ]]; then
  echo "Target project directory does not exist: ${TARGET_DIR}" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env.production"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.intranet.yml"
RECORD_ROOT="${TARGET_DIR}/runtime/deployment-records"
STAMP="$(date +%Y%m%d-%H%M%S)"
PACKAGE_NAME="$(basename "${PACKAGE_DIR}")"
RECORD_DIR="${RECORD_ROOT}/${STAMP}-${PACKAGE_NAME}"
DEPLOY_LOG="${TARGET_DIR}/DEPLOY_LOG.md"
mkdir -p "${RECORD_DIR}"

copy_if_exists() {
  local src="$1" dst="$2"
  if [[ -e "${src}" ]]; then
    cp -a "${src}" "${dst}"
  fi
}

sha_file() {
  local src="$1"
  if [[ -f "${src}" ]]; then
    sha256sum "${src}"
  else
    echo "MISSING  ${src}"
  fi
}

copy_if_exists "${PACKAGE_DIR}/manifest.env" "${RECORD_DIR}/package-manifest.env"
copy_if_exists "${PACKAGE_DIR}/changed-files.txt" "${RECORD_DIR}/changed-files.txt"
copy_if_exists "${PACKAGE_DIR}/deleted-files.txt" "${RECORD_DIR}/deleted-files.txt"
copy_if_exists "${PACKAGE_DIR}/docker/arex-recorder-images.txt" "${RECORD_DIR}/arex-recorder-images.txt"
copy_if_exists "${PACKAGE_DIR}/docker/arex-recorder-images.tar.sha256" "${RECORD_DIR}/arex-recorder-images.tar.sha256"

{
  echo "recorded_at=${STAMP}"
  echo "target_dir=${TARGET_DIR}"
  echo "package_dir=${PACKAGE_DIR}"
  echo "package_name=${PACKAGE_NAME}"
  echo "server_hostname=$(hostname 2>/dev/null || true)"
  echo "server_ip=$(hostname -I 2>/dev/null | awk '{print $1}' || true)"
  echo "env_sha256=$(sha_file "${ENV_FILE}" | awk '{print $1}')"
  echo "compose_sha256=$(sha_file "${COMPOSE_FILE}" | awk '{print $1}')"
  if command -v git >/dev/null 2>&1 && [[ -d "${TARGET_DIR}/.git" ]]; then
    echo "git_head=$(git -C "${TARGET_DIR}" rev-parse HEAD 2>/dev/null || true)"
    echo "git_branch=$(git -C "${TARGET_DIR}" branch --show-current 2>/dev/null || true)"
  else
    echo "git_head="
    echo "git_branch="
  fi
} > "${RECORD_DIR}/deployment-state.env"

{
  echo "# Docker Images"
  docker images --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.CreatedSince}} {{.Size}}' 2>/dev/null \
    | grep -E '^(arex-recorder|mysql):' || true
  echo
  echo "# Docker Containers"
  docker ps -a --format '{{.Names}} {{.Image}} {{.Status}} {{.Ports}}' 2>/dev/null \
    | grep -E 'arex-recorder|mysql' || true
} > "${RECORD_DIR}/docker-state.txt"

if command -v docker >/dev/null 2>&1 && [[ -f "${ENV_FILE}" && -f "${COMPOSE_FILE}" ]]; then
  docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" ps > "${RECORD_DIR}/compose-ps.txt" 2>&1 || true
  docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" config > "${RECORD_DIR}/compose-config.resolved.yml" 2>&1 || true
fi

{
  echo "# Deployment Record"
  echo
  echo "- Recorded at: ${STAMP}"
  echo "- Target dir: ${TARGET_DIR}"
  echo "- Package dir: ${PACKAGE_DIR}"
  echo "- Package name: ${PACKAGE_NAME}"
  echo "- Env sha256: $(sha_file "${ENV_FILE}" | awk '{print $1}')"
  echo "- Compose sha256: $(sha_file "${COMPOSE_FILE}" | awk '{print $1}')"
  echo
  echo "## Files"
  echo
  find "${RECORD_DIR}" -maxdepth 1 -type f -printf '%f\n' | sort
  echo
  echo "## Notes"
  echo
  echo "- This record intentionally stores only checksums for .env.production, not plaintext secrets."
  echo "- Compare package-manifest.env and changed-files.txt with the external-network record to confirm cloud-out/cloud-in alignment."
} > "${RECORD_DIR}/README.md"

ln -sfn "${RECORD_DIR}" "${RECORD_ROOT}/latest"

{
  echo
  echo "---"
  echo
  echo "### ${STAMP} - ${PACKAGE_NAME}"
  echo
  echo "**Package directory**: ${PACKAGE_DIR}"
  echo "**Target path**: ${TARGET_DIR}"
  echo "**Deployment record**: ${RECORD_DIR}"
  echo "**Latest record link**: ${RECORD_ROOT}/latest"
  echo "**Env sha256**: $(sha_file "${ENV_FILE}" | awk '{print $1}')"
  echo "**Compose sha256**: $(sha_file "${COMPOSE_FILE}" | awk '{print $1}')"
  echo
  echo "**Notes**:"
  echo "- Detailed machine-readable files are stored in the deployment record directory above."
  echo "- This log is the canonical human-readable intranet deployment history."
} >> "${DEPLOY_LOG}"

echo "Deployment state recorded:"
echo "  ${RECORD_DIR}"
echo "Latest symlink:"
echo "  ${RECORD_ROOT}/latest"
echo "Deployment log updated:"
echo "  ${DEPLOY_LOG}"

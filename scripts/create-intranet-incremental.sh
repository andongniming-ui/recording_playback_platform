#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/create-intranet-incremental.sh --base <git-ref> [options]

Creates a small tar.gz package for moving code changes into the intranet.
The package includes changed files, a deleted-files list, and an apply script.

Options:
  --base <git-ref>       Baseline deployed in the intranet, for example HEAD~1 or a tag.
  --out-dir <dir>        Output directory. Default: runtime/intranet-incremental-packages
  --name <name>          Package name without .tar.gz. Default: intranet-incremental-<timestamp>
  --include-env          Include real .env files. Default is to exclude them.
  --no-untracked         Do not include untracked, non-ignored files.
  --help                 Show this help.

Examples:
  scripts/create-intranet-incremental.sh --base 2738f312 --out-dir /mnt/e/test/ceshi
  scripts/create-intranet-incremental.sh --base intranet-prod-20260508 --name fix-recording-page
EOF
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_REF=""
OUT_DIR="${ROOT_DIR}/runtime/intranet-incremental-packages"
PACKAGE_NAME=""
INCLUDE_ENV=false
INCLUDE_UNTRACKED=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base)
      BASE_REF="${2:-}"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="${2:-}"
      shift 2
      ;;
    --name)
      PACKAGE_NAME="${2:-}"
      shift 2
      ;;
    --include-env)
      INCLUDE_ENV=true
      shift
      ;;
    --no-untracked)
      INCLUDE_UNTRACKED=false
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "${BASE_REF}" ]]; then
  echo "Missing required --base <git-ref>." >&2
  usage >&2
  exit 2
fi

cd "${ROOT_DIR}"

if ! git rev-parse --verify "${BASE_REF}^{commit}" >/dev/null 2>&1; then
  echo "Invalid base git ref: ${BASE_REF}" >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"
STAMP="$(date +%Y%m%d-%H%M%S)"
PACKAGE_NAME="${PACKAGE_NAME:-intranet-incremental-${STAMP}}"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/intranet-incremental.XXXXXX")"
PKG_DIR="${WORK_DIR}/${PACKAGE_NAME}"
FILES_DIR="${PKG_DIR}/files"
mkdir -p "${FILES_DIR}"

cleanup() {
  rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

is_excluded() {
  local path="$1"

  case "${path}" in
    .git|.git/*|.claude|.claude/*|.workbuddy|.workbuddy/*|.codex) return 0 ;;
    runtime/offline-bundle|runtime/offline-bundle/*) return 0 ;;
    runtime/intranet-incremental-packages|runtime/intranet-incremental-packages/*) return 0 ;;
    runtime/intranet-update-backups|runtime/intranet-update-backups/*) return 0 ;;
    logs|logs/*|*.log) return 0 ;;
    platform/data|platform/data/*|platform/backend/data|platform/backend/data/*) return 0 ;;
    platform/ssh_keys|platform/ssh_keys/*|platform/backend/ssh_keys|platform/backend/ssh_keys/*) return 0 ;;
    deploy/intranet/data|deploy/intranet/data/*|deploy/intranet/ssh_keys|deploy/intranet/ssh_keys/*) return 0 ;;
    node_modules|*/node_modules/*|.venv|*/.venv/*|venv|*/venv/*) return 0 ;;
    __pycache__|*/__pycache__/*|.pytest_cache|*/.pytest_cache/*|.mypy_cache|*/.mypy_cache/*|.ruff_cache|*/.ruff_cache/*) return 0 ;;
  esac

  if [[ "${INCLUDE_ENV}" != "true" ]]; then
    case "${path}" in
      .env|*/.env|deploy/intranet/.env.production|deploy/intranet/.env.ai-gateway) return 0 ;;
    esac
  fi

  return 1
}

safe_relpath() {
  local path="$1"
  [[ -n "${path}" ]] || return 1
  [[ "${path}" != /* ]] || return 1
  [[ "${path}" != "." ]] || return 1
  [[ "${path}" != ".." ]] || return 1
  [[ "${path}" != ../* ]] || return 1
  [[ "${path}" != */../* ]] || return 1
}

changed_tmp="${WORK_DIR}/changed.raw"
deleted_tmp="${WORK_DIR}/deleted.raw"
untracked_tmp="${WORK_DIR}/untracked.raw"
: > "${changed_tmp}"
: > "${deleted_tmp}"
: > "${untracked_tmp}"

git diff --name-only --diff-filter=ACMRT "${BASE_REF}" -- > "${changed_tmp}"
git diff --name-only --diff-filter=D "${BASE_REF}" -- > "${deleted_tmp}"

if [[ "${INCLUDE_UNTRACKED}" == "true" ]]; then
  git ls-files --others --exclude-standard > "${untracked_tmp}"
fi

changed_final="${PKG_DIR}/changed-files.txt"
deleted_final="${PKG_DIR}/deleted-files.txt"
: > "${changed_final}"
: > "${deleted_final}"

while IFS= read -r path || [[ -n "${path}" ]]; do
  [[ -n "${path}" ]] || continue
  safe_relpath "${path}" || continue
  is_excluded "${path}" && continue
  [[ -f "${path}" || -L "${path}" ]] || continue
  printf '%s\n' "${path}" >> "${changed_final}"
done < <(cat "${changed_tmp}" "${untracked_tmp}" | sort -u)

while IFS= read -r path || [[ -n "${path}" ]]; do
  [[ -n "${path}" ]] || continue
  safe_relpath "${path}" || continue
  is_excluded "${path}" && continue
  printf '%s\n' "${path}" >> "${deleted_final}"
done < <(sort -u "${deleted_tmp}")

if [[ ! -s "${changed_final}" && ! -s "${deleted_final}" ]]; then
  echo "No packageable changes found from ${BASE_REF}." >&2
  exit 1
fi

while IFS= read -r path || [[ -n "${path}" ]]; do
  [[ -n "${path}" ]] || continue
  mkdir -p "${FILES_DIR}/$(dirname "${path}")"
  cp -a "${path}" "${FILES_DIR}/${path}"
done < "${changed_final}"

cp deploy/intranet/apply-incremental-update.sh "${PKG_DIR}/apply-incremental-update.sh"
chmod +x "${PKG_DIR}/apply-incremental-update.sh"

cat > "${PKG_DIR}/manifest.env" <<EOF
PACKAGE_NAME=${PACKAGE_NAME}
CREATED_AT=${STAMP}
BASE_REF=${BASE_REF}
BASE_COMMIT=$(git rev-parse --short "${BASE_REF}^{commit}")
HEAD_COMMIT=$(git rev-parse --short HEAD)
BRANCH=$(git branch --show-current || true)
INCLUDE_ENV=${INCLUDE_ENV}
INCLUDE_UNTRACKED=${INCLUDE_UNTRACKED}
EOF

cat > "${PKG_DIR}/README.txt" <<'EOF'
Intranet incremental update package

1. Copy this directory or the .tar.gz package to the intranet server.
2. Extract it:
     tar -xzf intranet-incremental-YYYYmmdd-HHMMSS.tar.gz
3. Apply it to the deployed project directory:
     bash intranet-incremental-YYYYmmdd-HHMMSS/apply-incremental-update.sh /path/to/recording_playback_platform

Optional:
  Add --rebuild none when you only want to copy files.
  Add --rebuild backend/frontend/all to force specific docker service rebuilds.
EOF

tarball="${OUT_DIR}/${PACKAGE_NAME}.tar.gz"
(cd "${WORK_DIR}" && tar -czf "${tarball}" "${PACKAGE_NAME}")

changed_count="$(wc -l < "${changed_final}" | tr -d ' ')"
deleted_count="$(wc -l < "${deleted_final}" | tr -d ' ')"
size_human="$(du -h "${tarball}" | awk '{print $1}')"

echo "[OK] Created ${tarball}"
echo "[OK] Size: ${size_human}"
echo "[OK] Changed files: ${changed_count}"
echo "[OK] Deleted files: ${deleted_count}"
echo "[OK] Apply inside intranet with:"
echo "     tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "     bash ${PACKAGE_NAME}/apply-incremental-update.sh /path/to/recording_playback_platform"

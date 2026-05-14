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
  --include-untracked    Include untracked, non-ignored files. Default is tracked changes only.
  --no-untracked         Legacy alias for the default behavior.
  --include-images MODE  Include prebuilt Docker images: auto, always, or never. Default: auto.
  --offline-bundle <dir> Offline bundle used to build images without internet.
                         Default: runtime/offline-bundle
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
INCLUDE_UNTRACKED=false
INCLUDE_IMAGES="auto"
OFFLINE_BUNDLE_DIR="${ROOT_DIR}/runtime/offline-bundle"

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
    --include-untracked)
      INCLUDE_UNTRACKED=true
      shift
      ;;
    --no-untracked)
      INCLUDE_UNTRACKED=false
      shift
      ;;
    --include-images)
      INCLUDE_IMAGES="${2:-}"
      shift 2
      ;;
    --offline-bundle)
      OFFLINE_BUNDLE_DIR="${2:-}"
      shift 2
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

case "${INCLUDE_IMAGES}" in
  auto|always|never) ;;
  *)
    echo "Invalid --include-images value: ${INCLUDE_IMAGES}" >&2
    exit 2
    ;;
esac

cd "${ROOT_DIR}"

if ! git rev-parse --verify "${BASE_REF}^{commit}" >/dev/null 2>&1; then
  echo "Invalid base git ref: ${BASE_REF}" >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"
OUT_DIR="$(cd "${OUT_DIR}" && pwd)"
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

backend_changed=false
frontend_changed=false
dependency_changed=false
combined_changes="${WORK_DIR}/combined-changes.txt"
cat "${changed_final}" "${deleted_final}" 2>/dev/null > "${combined_changes}" || true
if grep -qE '^(platform/backend/|platform/requirements\.txt|platform/backend/Dockerfile)' "${combined_changes}"; then
  backend_changed=true
fi
if grep -qE '^(platform/frontend/|platform/frontend/Dockerfile)' "${combined_changes}"; then
  frontend_changed=true
fi
if grep -qE '^(platform/requirements\.txt|platform/frontend/package(-lock)?\.json)' "${combined_changes}"; then
  dependency_changed=true
fi

while IFS= read -r path || [[ -n "${path}" ]]; do
  [[ -n "${path}" ]] || continue
  mkdir -p "${FILES_DIR}/$(dirname "${path}")"
  cp -a "${path}" "${FILES_DIR}/${path}"
done < "${changed_final}"

cp deploy/intranet/apply-incremental-update.sh "${PKG_DIR}/apply-incremental-update.sh"
chmod +x "${PKG_DIR}/apply-incremental-update.sh"

include_image_tar=false
if [[ "${INCLUDE_IMAGES}" == "always" ]]; then
  include_image_tar=true
elif [[ "${INCLUDE_IMAGES}" == "auto" && ( "${backend_changed}" == "true" || "${frontend_changed}" == "true" ) ]]; then
  include_image_tar=true
fi

if [[ "${include_image_tar}" == "true" ]]; then
  command -v docker >/dev/null 2>&1 || {
    echo "Docker is required to include prebuilt images in the intranet package." >&2
    exit 1
  }
  mkdir -p "${PKG_DIR}/docker"

  if [[ -f "${OFFLINE_BUNDLE_DIR}/docker/arex-recorder-images.tar" ]]; then
    cp "${OFFLINE_BUNDLE_DIR}/docker/arex-recorder-images.tar" "${PKG_DIR}/docker/arex-recorder-images.tar"
    if [[ -f "${OFFLINE_BUNDLE_DIR}/docker/arex-recorder-images.txt" ]]; then
      cp "${OFFLINE_BUNDLE_DIR}/docker/arex-recorder-images.txt" "${PKG_DIR}/docker/arex-recorder-images.txt"
    fi
    if [[ -f "${OFFLINE_BUNDLE_DIR}/docker/arex-recorder-images.tar.sha256" ]]; then
      cp "${OFFLINE_BUNDLE_DIR}/docker/arex-recorder-images.tar.sha256" "${PKG_DIR}/docker/arex-recorder-images.tar.sha256"
      (cd "${PKG_DIR}/docker" && sha256sum -c arex-recorder-images.tar.sha256)
    else
      (cd "${PKG_DIR}/docker" && sha256sum arex-recorder-images.tar > arex-recorder-images.tar.sha256)
    fi
  elif [[ ! -d "${OFFLINE_BUNDLE_DIR}/pip" || ! -d "${OFFLINE_BUNDLE_DIR}/frontend/dist" || ! -d "${OFFLINE_BUNDLE_DIR}/frontend/node_modules" ]]; then
    echo "Prebuilt images require a complete offline bundle at ${OFFLINE_BUNDLE_DIR}." >&2
    echo "Run deploy/intranet/prepare-offline-bundle.sh ${OFFLINE_BUNDLE_DIR} on the external-network machine first." >&2
    echo "Use --include-images never only for code-only packages that will not recreate backend/frontend containers." >&2
    exit 1
  else
    "${ROOT_DIR}/deploy/intranet/build-images-from-bundle.sh" "${OFFLINE_BUNDLE_DIR}"
    cp "${OFFLINE_BUNDLE_DIR}/docker/arex-recorder-images.tar" "${PKG_DIR}/docker/arex-recorder-images.tar"
    cp "${OFFLINE_BUNDLE_DIR}/docker/arex-recorder-images.txt" "${PKG_DIR}/docker/arex-recorder-images.txt"
    cp "${OFFLINE_BUNDLE_DIR}/docker/arex-recorder-images.tar.sha256" "${PKG_DIR}/docker/arex-recorder-images.tar.sha256"
  fi
fi

cat > "${PKG_DIR}/manifest.env" <<EOF
PACKAGE_NAME=${PACKAGE_NAME}
CREATED_AT=${STAMP}
BASE_REF=${BASE_REF}
BASE_COMMIT=$(git rev-parse --short "${BASE_REF}^{commit}")
HEAD_COMMIT=$(git rev-parse --short HEAD)
BRANCH=$(git branch --show-current || true)
INCLUDE_ENV=${INCLUDE_ENV}
INCLUDE_UNTRACKED=${INCLUDE_UNTRACKED}
INCLUDE_IMAGES=${INCLUDE_IMAGES}
OFFLINE_BUNDLE_DIR=${OFFLINE_BUNDLE_DIR}
BACKEND_CHANGED=${backend_changed}
FRONTEND_CHANGED=${frontend_changed}
DEPENDENCY_CHANGED=${dependency_changed}
IMAGE_TAR_INCLUDED=${include_image_tar}
EOF

cat > "${PKG_DIR}/README.txt" <<'EOF'
Intranet incremental update package

1. Copy this directory or the .tar.gz package to the intranet server.
2. Extract it:
     tar -xzf intranet-incremental-YYYYmmdd-HHMMSS.tar.gz
3. Apply it to the deployed project directory:
     bash intranet-incremental-YYYYmmdd-HHMMSS/apply-incremental-update.sh /path/to/recording_playback_platform

Optional:
  This package is designed for offline intranet use. When backend/frontend code
  changes, it includes prebuilt Docker images under docker/ and the apply script
  will load those images and recreate containers without running docker build.
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

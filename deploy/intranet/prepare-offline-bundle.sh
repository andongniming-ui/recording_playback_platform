#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
OUT_DIR_INPUT="${1:-${ROOT_DIR}/runtime/offline-bundle}"
mkdir -p "$(dirname "${OUT_DIR_INPUT}")"
FINAL_OUT_DIR="$(cd "$(dirname "${OUT_DIR_INPUT}")" && pwd)/$(basename "${OUT_DIR_INPUT}")"
WORK_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/arex-offline-bundle.XXXXXX")"
OUT_DIR="${WORK_ROOT}/bundle"
FRONTEND_DIR="${ROOT_DIR}/platform/frontend"
AGENT_JAR="${2:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PIP_DEFAULT_TIMEOUT="${PIP_DEFAULT_TIMEOUT:-120}"
PIP_RETRIES="${PIP_RETRIES:-10}"
PIP_DOWNLOAD_MODE="${PIP_DOWNLOAD_MODE:-auto}"
AREX_AGENT_VERSION="${AREX_AGENT_VERSION:-0.4.8}"
AREX_AGENT_URL="${AREX_AGENT_URL:-https://github.com/arextest/arex-agent-java/releases/download/v${AREX_AGENT_VERSION}/arex-agent.jar}"

cleanup() {
  rm -rf "${WORK_ROOT}"
}
trap cleanup EXIT

ensure_image() {
  local image="$1"
  if docker image inspect "${image}" >/dev/null 2>&1; then
    return
  fi
  docker pull "${image}"
}

mkdir -p "${OUT_DIR}/pip" "${OUT_DIR}/npm" "${OUT_DIR}/frontend" "${OUT_DIR}/maven" "${OUT_DIR}/docker" "${OUT_DIR}/arex-agent"

if [[ "${PIP_DOWNLOAD_MODE}" == "docker" ]] || { [[ "${PIP_DOWNLOAD_MODE}" == "auto" ]] && command -v docker >/dev/null 2>&1; }; then
  ensure_image python:3.11-slim
  docker run --rm \
    -v "${ROOT_DIR}/platform/requirements.txt:/requirements.txt:ro" \
    -v "${OUT_DIR}/pip:/wheelhouse" \
    python:3.11-slim \
    python -m pip download \
      --default-timeout "${PIP_DEFAULT_TIMEOUT}" \
      --retries "${PIP_RETRIES}" \
      --dest /wheelhouse \
      --requirement /requirements.txt
elif [[ "${PIP_DOWNLOAD_MODE}" == "host" || "${PIP_DOWNLOAD_MODE}" == "auto" ]]; then
  "${PYTHON_BIN}" -m pip download \
    --default-timeout "${PIP_DEFAULT_TIMEOUT}" \
    --retries "${PIP_RETRIES}" \
    -r "${ROOT_DIR}/platform/requirements.txt" \
    -d "${OUT_DIR}/pip"
else
  echo "Invalid PIP_DOWNLOAD_MODE=${PIP_DOWNLOAD_MODE}; expected auto, docker, or host" >&2
  exit 2
fi

if [[ -f "${FRONTEND_DIR}/package-lock.json" ]]; then
  (cd "${FRONTEND_DIR}" && npm ci --cache "${OUT_DIR}/npm" --prefer-offline --no-audit --no-fund)
  (cd "${FRONTEND_DIR}" && npm run build)
  cp "${FRONTEND_DIR}/package.json" "${OUT_DIR}/npm/package.json"
  cp "${FRONTEND_DIR}/package-lock.json" "${OUT_DIR}/npm/package-lock.json"
  cp -a "${FRONTEND_DIR}/dist" "${OUT_DIR}/frontend/dist"
  cp -a "${FRONTEND_DIR}/node_modules" "${OUT_DIR}/frontend/node_modules"
  (cd "${FRONTEND_DIR}" && sha256sum package-lock.json) > "${OUT_DIR}/frontend/package-lock.sha256"
  (cd "${FRONTEND_DIR}" && find dist -type f -print0 | sort -z | xargs -0 sha256sum) > "${OUT_DIR}/frontend/dist.sha256"
  tar -C "${OUT_DIR}" -czf "${OUT_DIR}/npm-cache.tgz" npm
fi

find "${ROOT_DIR}" -name pom.xml -not -path "*/target/*" -print0 | while IFS= read -r -d '' pom; do
  project_dir="$(dirname "${pom}")"
  (cd "${project_dir}" && mvn -q -DskipTests dependency:go-offline)
done

if [[ -d "${HOME}/.m2/repository" ]]; then
  tar -C "${HOME}/.m2" -czf "${OUT_DIR}/maven/repository.tgz" repository
fi

ensure_image python:3.11-slim
ensure_image node:18-bullseye-slim
ensure_image mysql:8.0
"${SCRIPT_DIR}/build-images-from-bundle.sh" "${OUT_DIR}"

if [[ -n "${AGENT_JAR}" ]]; then
  cp "${AGENT_JAR}" "${OUT_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar"
else
  curl -L --fail --retry 5 --connect-timeout 20 --output "${OUT_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar" "${AREX_AGENT_URL}"
fi
(cd "${OUT_DIR}/arex-agent" && sha256sum "arex-agent-${AREX_AGENT_VERSION}.jar" > "arex-agent-${AREX_AGENT_VERSION}.jar.sha256")

if [[ -f "${SCRIPT_DIR}/arex-agent.lock" ]]; then
  expected_agent_sha="$(grep -E '^AREX_AGENT_SHA256=' "${SCRIPT_DIR}/arex-agent.lock" | tail -n 1 | cut -d '=' -f 2- || true)"
  if [[ -n "${expected_agent_sha}" ]]; then
    actual_agent_sha="$(sha256sum "${OUT_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar" | awk '{print $1}')"
    [[ "${actual_agent_sha}" == "${expected_agent_sha}" ]] || {
      echo "AREX agent sha256 mismatch. Expected ${expected_agent_sha}, got ${actual_agent_sha}" >&2
      exit 1
    }
  fi
fi

cat > "${OUT_DIR}/MANIFEST.txt" <<EOF
generated_at=$(date -Iseconds)
root_dir=${ROOT_DIR}
python_packages=$(find "${OUT_DIR}/pip" -type f | wc -l)
npm_cache_files=$(find "${OUT_DIR}/npm" -type f | wc -l)
maven_repository_archive=$(if [[ -f "${OUT_DIR}/maven/repository.tgz" ]]; then echo yes; else echo no; fi)
docker_base_images_archive=$(if [[ -f "${OUT_DIR}/docker/base-images.tar" ]]; then echo yes; else echo no; fi)
docker_platform_images_archive=$(if [[ -f "${OUT_DIR}/docker/arex-recorder-images.tar" ]]; then echo yes; else echo no; fi)
frontend_dist_hashes=$(if [[ -f "${OUT_DIR}/frontend/dist.sha256" ]]; then echo yes; else echo no; fi)
arex_agent=$(if [[ -f "${OUT_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar" ]]; then echo yes; else echo no; fi)
git_commit=$(cd "${ROOT_DIR}" && git rev-parse --short HEAD 2>/dev/null || echo unknown)
git_dirty=$(cd "${ROOT_DIR}" && if git diff --quiet --ignore-submodules -- 2>/dev/null && git diff --cached --quiet --ignore-submodules -- 2>/dev/null; then echo no; else echo yes; fi)
EOF

"${SCRIPT_DIR}/verify-offline-bundle.sh" "${OUT_DIR}" || {
  echo "Offline bundle was created, but verification failed. Check the messages above." >&2
  exit 1
}

cat > "${OUT_DIR}/README.md" <<'EOF'
# Offline Bundle

This directory contains dependency caches prepared from an external-network machine.

- `pip/`: Python wheels and source distributions from `platform/requirements.txt`.
- `npm/`: npm cache produced by `npm ci --cache`.
- `frontend/`: the exact frontend `dist/` and `node_modules/` used to build the image.
- `maven/repository.tgz`: Maven local repository snapshot from the build machine.
- `docker/base-images.tar`: Python, Node, and MySQL base/runtime images.
- `docker/arex-recorder-images.tar`: Built platform backend/frontend images.
- `arex-agent/`: approved fixed AREX agent jar and sha256, if provided.

Intranet import:

1. Copy this bundle to the intranet host.
2. Run `deploy/intranet/import-offline-bundle.sh <bundle-dir>`.
3. Copy `.env.production.offline.example` to `.env.production` and edit all placeholders.
4. Run `deploy/intranet/deploy-intranet.sh`.
EOF

rm -rf "${FINAL_OUT_DIR}.previous"
if [[ -d "${FINAL_OUT_DIR}" ]]; then
  mv "${FINAL_OUT_DIR}" "${FINAL_OUT_DIR}.previous"
fi
mv "${OUT_DIR}" "${FINAL_OUT_DIR}"
rm -rf "${FINAL_OUT_DIR}.previous"
trap - EXIT
rm -rf "${WORK_ROOT}"

echo "Offline bundle prepared at ${FINAL_OUT_DIR}"

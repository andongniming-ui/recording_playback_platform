#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR_INPUT="${1:-${ROOT_DIR}/runtime/offline-bundle}"
mkdir -p "${OUT_DIR_INPUT}"
OUT_DIR="$(cd "${OUT_DIR_INPUT}" && pwd)"
FRONTEND_DIR="${ROOT_DIR}/platform/frontend"
AGENT_JAR="${2:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
AREX_AGENT_VERSION="${AREX_AGENT_VERSION:-0.4.8}"
AREX_AGENT_URL="${AREX_AGENT_URL:-https://github.com/arextest/arex-agent-java/releases/download/v${AREX_AGENT_VERSION}/arex-agent.jar}"

ensure_image() {
  local image="$1"
  if docker image inspect "${image}" >/dev/null 2>&1; then
    return
  fi
  docker pull "${image}"
}

mkdir -p "${OUT_DIR}/pip" "${OUT_DIR}/npm" "${OUT_DIR}/maven" "${OUT_DIR}/docker" "${OUT_DIR}/arex-agent"

if command -v docker >/dev/null 2>&1; then
  ensure_image python:3.11-slim
  docker run --rm \
    -v "${ROOT_DIR}/platform/requirements.txt:/requirements.txt:ro" \
    -v "${OUT_DIR}/pip:/wheelhouse" \
    python:3.11-slim \
    python -m pip download --dest /wheelhouse --requirement /requirements.txt
else
  "${PYTHON_BIN}" -m pip download -r "${ROOT_DIR}/platform/requirements.txt" -d "${OUT_DIR}/pip"
fi

if [[ -f "${FRONTEND_DIR}/package-lock.json" ]]; then
  (cd "${FRONTEND_DIR}" && npm ci --cache "${OUT_DIR}/npm" --prefer-offline --no-audit --no-fund)
  cp "${FRONTEND_DIR}/package.json" "${OUT_DIR}/npm/package.json"
  cp "${FRONTEND_DIR}/package-lock.json" "${OUT_DIR}/npm/package-lock.json"
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
"${ROOT_DIR}/deploy/intranet/build-images-from-bundle.sh" "${OUT_DIR}"

if [[ -n "${AGENT_JAR}" ]]; then
  cp "${AGENT_JAR}" "${OUT_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar"
else
  curl -L --fail --retry 5 --connect-timeout 20 --output "${OUT_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar" "${AREX_AGENT_URL}"
fi
(cd "${OUT_DIR}/arex-agent" && sha256sum "arex-agent-${AREX_AGENT_VERSION}.jar" > "arex-agent-${AREX_AGENT_VERSION}.jar.sha256")

cat > "${OUT_DIR}/MANIFEST.txt" <<EOF
generated_at=$(date -Iseconds)
root_dir=${ROOT_DIR}
python_packages=$(find "${OUT_DIR}/pip" -type f | wc -l)
npm_cache_files=$(find "${OUT_DIR}/npm" -type f | wc -l)
maven_repository_archive=$(if [[ -f "${OUT_DIR}/maven/repository.tgz" ]]; then echo yes; else echo no; fi)
docker_base_images_archive=$(if [[ -f "${OUT_DIR}/docker/base-images.tar" ]]; then echo yes; else echo no; fi)
docker_platform_images_archive=$(if [[ -f "${OUT_DIR}/docker/arex-recorder-images.tar" ]]; then echo yes; else echo no; fi)
arex_agent=$(if [[ -f "${OUT_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar" ]]; then echo yes; else echo no; fi)
EOF

"${SCRIPT_DIR:-$(dirname "$0")}/verify-offline-bundle.sh" "${OUT_DIR}" || {
  echo "Offline bundle was created, but verification failed. Check the messages above." >&2
  exit 1
}

cat > "${OUT_DIR}/README.md" <<'EOF'
# Offline Bundle

This directory contains dependency caches prepared from an external-network machine.

- `pip/`: Python wheels and source distributions from `platform/requirements.txt`.
- `npm/`: npm cache produced by `npm ci --cache`.
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

echo "Offline bundle prepared at ${OUT_DIR}"

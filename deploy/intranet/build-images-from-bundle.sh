#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUNDLE_DIR="${1:-${ROOT_DIR}/runtime/offline-bundle}"
BUILD_DIR="${ROOT_DIR}/runtime/docker-build"
KEEP_DOCKER_BUILD_CONTEXT="${KEEP_DOCKER_BUILD_CONTEXT:-false}"

cleanup_build_context() {
  if [[ "${KEEP_DOCKER_BUILD_CONTEXT}" != "true" ]]; then
    rm -rf "${BUILD_DIR}/backend" "${BUILD_DIR}/frontend"
  fi
}
trap cleanup_build_context EXIT

[[ -d "${BUNDLE_DIR}/pip" ]] || { echo "Missing pip wheelhouse: ${BUNDLE_DIR}/pip" >&2; echo "HINT: Run prepare-offline-bundle.sh first to download pip dependencies." >&2; exit 1; }
[[ -d "${BUNDLE_DIR}/frontend/dist" ]] || { echo "Missing frontend dist in bundle: ${BUNDLE_DIR}/frontend/dist" >&2; echo "HINT: Run prepare-offline-bundle.sh so the frontend build artifact is captured." >&2; exit 1; }
[[ -d "${BUNDLE_DIR}/frontend/node_modules" ]] || { echo "Missing frontend node_modules in bundle: ${BUNDLE_DIR}/frontend/node_modules" >&2; echo "HINT: Run prepare-offline-bundle.sh so frontend dependencies are captured." >&2; exit 1; }

rm -rf "${BUILD_DIR}/backend" "${BUILD_DIR}/frontend"
mkdir -p "${BUILD_DIR}/backend" "${BUILD_DIR}/frontend" "${BUNDLE_DIR}/docker"

cp "${ROOT_DIR}/platform/requirements.txt" "${BUILD_DIR}/backend/requirements.txt"
cp -a "${ROOT_DIR}/platform/backend" "${BUILD_DIR}/backend/backend"
cp -a "${BUNDLE_DIR}/pip" "${BUILD_DIR}/backend/wheelhouse"

cat > "${BUILD_DIR}/backend/Dockerfile" <<'DOCKERFILE'
FROM python:3.11-slim
WORKDIR /app
COPY wheelhouse/ /wheelhouse/
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-index --find-links=/wheelhouse -r /tmp/requirements.txt
COPY backend/ /app/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKERFILE

docker build -t arex-recorder-backend:1.0.0 "${BUILD_DIR}/backend"

cp "${ROOT_DIR}/platform/frontend/package.json" "${BUILD_DIR}/frontend/package.json"
cp "${ROOT_DIR}/platform/frontend/package-lock.json" "${BUILD_DIR}/frontend/package-lock.json"
cp -a "${BUNDLE_DIR}/frontend/dist" "${BUILD_DIR}/frontend/dist"
cp -a "${BUNDLE_DIR}/frontend/node_modules" "${BUILD_DIR}/frontend/node_modules"

cat > "${BUILD_DIR}/frontend/Dockerfile" <<'DOCKERFILE'
FROM node:18-bullseye-slim
WORKDIR /app
COPY package.json package-lock.json ./
COPY node_modules/ ./node_modules/
COPY dist/ ./dist/
EXPOSE 5173
CMD ["sh", "-c", "printf 'window.__AREX_RECORDER_CONFIG__ = { VITE_API_BASE_URL: \"%s\" }\\n' \"${VITE_API_BASE_URL}\" > /app/dist/env.js && npm run preview -- --host 0.0.0.0 --port 5173"]
DOCKERFILE

docker build -t arex-recorder-frontend:1.0.0 "${BUILD_DIR}/frontend"

docker save -o "${BUNDLE_DIR}/docker/base-images.tar" python:3.11-slim node:18-bullseye-slim mysql:8.0
docker save -o "${BUNDLE_DIR}/docker/arex-recorder-images.tar" arex-recorder-backend:1.0.0 arex-recorder-frontend:1.0.0
(cd "${BUNDLE_DIR}/docker" && sha256sum base-images.tar > base-images.tar.sha256)
(cd "${BUNDLE_DIR}/docker" && sha256sum arex-recorder-images.tar > arex-recorder-images.tar.sha256)
docker image inspect arex-recorder-backend:1.0.0 arex-recorder-frontend:1.0.0 \
  --format '{{.RepoTags}} {{.Id}}' > "${BUNDLE_DIR}/docker/arex-recorder-images.txt"

ls -lh "${BUNDLE_DIR}/docker"
if [[ "${KEEP_DOCKER_BUILD_CONTEXT}" != "true" ]]; then
  echo "Cleaned temporary docker build contexts under ${BUILD_DIR}."
fi

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="${1:-${SCRIPT_DIR}/../../runtime/offline-bundle}"
ENV_FILE="${SCRIPT_DIR}/.env.production"
PUSH_TO_REGISTRY="${PUSH_TO_REGISTRY:-false}"
AREX_AGENT_VERSION="${AREX_AGENT_VERSION:-0.4.8}"

if [[ ! -d "${BUNDLE_DIR}" ]]; then
  echo "Bundle directory not found: ${BUNDLE_DIR}" >&2
  exit 1
fi

"${SCRIPT_DIR}/verify-offline-bundle.sh" "${BUNDLE_DIR}"

if [[ -f "${BUNDLE_DIR}/docker/base-images.tar" ]]; then
  docker load -i "${BUNDLE_DIR}/docker/base-images.tar"
fi

if [[ -f "${BUNDLE_DIR}/docker/arex-recorder-images.tar" ]]; then
  docker load -i "${BUNDLE_DIR}/docker/arex-recorder-images.tar"
fi

if [[ -f "${BUNDLE_DIR}/docker/ai-gateway-images.tar" ]]; then
  docker load -i "${BUNDLE_DIR}/docker/ai-gateway-images.tar"
fi

mkdir -p "${SCRIPT_DIR}/third_party/arex-agent"
if [[ -f "${BUNDLE_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar" ]]; then
  cp "${BUNDLE_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar" "${SCRIPT_DIR}/third_party/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar"
fi

if [[ -f "${BUNDLE_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar.sha256" ]]; then
  (cd "${SCRIPT_DIR}/third_party/arex-agent" && sha256sum -c "${BUNDLE_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar.sha256")
fi

if [[ -f "${BUNDLE_DIR}/maven/repository.tgz" ]]; then
  mkdir -p "${HOME}/.m2"
  tar -C "${HOME}/.m2" -xzf "${BUNDLE_DIR}/maven/repository.tgz"
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${SCRIPT_DIR}/.env.production.offline.example" "${ENV_FILE}"
  echo "Created ${ENV_FILE}. Edit it before deploying."
fi

if [[ "${PUSH_TO_REGISTRY}" == "true" && -f "${ENV_FILE}" ]]; then
  registry="$(grep -E '^INTRANET_REGISTRY=' "${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- || true)"
  if [[ -z "${registry}" ]]; then
    echo "PUSH_TO_REGISTRY=true but INTRANET_REGISTRY is empty in ${ENV_FILE}" >&2
    exit 1
  fi
  docker tag arex-recorder-backend:1.0.0 "${registry}/backend:1.0.0"
  docker tag arex-recorder-frontend:1.0.0 "${registry}/frontend:1.0.0"
  docker push "${registry}/backend:1.0.0"
  docker push "${registry}/frontend:1.0.0"
fi

docker images | grep -E 'arex-recorder|mysql|python|node' || true

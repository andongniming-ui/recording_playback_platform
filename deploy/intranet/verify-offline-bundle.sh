#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BUNDLE_DIR="${1:-${ROOT_DIR}/runtime/offline-bundle}"
ALLOW_MISSING_AGENT="${ALLOW_MISSING_AGENT:-false}"
AREX_AGENT_VERSION="${AREX_AGENT_VERSION:-0.4.8}"

fail() {
  echo "[FAIL] $*" >&2
  exit 1
}

ok() {
  echo "[ OK ] $*"
}

[[ -d "${BUNDLE_DIR}" ]] || fail "Bundle directory not found: ${BUNDLE_DIR}"

pip_count="$(find "${BUNDLE_DIR}/pip" -type f 2>/dev/null | wc -l)"
[[ "${pip_count}" -gt 0 ]] || fail "No Python packages found in ${BUNDLE_DIR}/pip"
ok "Python package files: ${pip_count}"

python3 - "${ROOT_DIR}/platform/requirements.txt" "${BUNDLE_DIR}/pip" <<'PY'
import re
import sys
from pathlib import Path

requirements = Path(sys.argv[1])
wheelhouse = Path(sys.argv[2])
files = [p.name.lower().replace("_", "-") for p in wheelhouse.iterdir() if p.is_file()]
missing = []
for raw in requirements.read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    name = re.split(r"[<>=!~;\[]", line, maxsplit=1)[0].strip().lower().replace("_", "-")
    if not any(f.startswith(name + "-") for f in files):
        missing.append(name)
if missing:
    print("Missing direct Python requirements:", ", ".join(missing), file=sys.stderr)
    sys.exit(1)
PY
ok "Direct Python requirements are present"

[[ -f "${BUNDLE_DIR}/npm/package-lock.json" ]] || fail "Missing npm package-lock.json in bundle"
npm_count="$(find "${BUNDLE_DIR}/npm" -type f 2>/dev/null | wc -l)"
[[ "${npm_count}" -gt 0 ]] || fail "No npm cache files found in ${BUNDLE_DIR}/npm"
ok "npm cache files: ${npm_count}"

[[ -f "${BUNDLE_DIR}/maven/repository.tgz" ]] || fail "Missing Maven repository archive: ${BUNDLE_DIR}/maven/repository.tgz"
ok "Maven repository archive exists"

[[ -f "${BUNDLE_DIR}/docker/base-images.tar" ]] || fail "Missing Docker base image archive"
[[ -f "${BUNDLE_DIR}/docker/arex-recorder-images.tar" ]] || fail "Missing Docker platform image archive"
ok "Docker image archives exist"

if [[ -f "${BUNDLE_DIR}/docker/ai-gateway-images.tar" ]]; then
  ok "AI Gateway image archive exists"
else
  echo "[WARN] AI Gateway image archive not found: ${BUNDLE_DIR}/docker/ai-gateway-images.tar"
  echo "[WARN]   AI analysis features will not be available. Re-run prepare-offline-bundle.sh if needed."
fi

if [[ -f "${BUNDLE_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar" ]]; then
  if [[ -f "${BUNDLE_DIR}/arex-agent/arex-agent-${AREX_AGENT_VERSION}.jar.sha256" ]]; then
    (cd "${BUNDLE_DIR}/arex-agent" && sha256sum -c "arex-agent-${AREX_AGENT_VERSION}.jar.sha256")
  fi
  ok "AREX agent jar exists"
elif [[ "${ALLOW_MISSING_AGENT}" == "true" ]]; then
  echo "[WARN] AREX agent jar is missing, allowed by ALLOW_MISSING_AGENT=true"
else
  fail "Missing AREX agent jar. Pass it as the second argument to prepare-offline-bundle.sh"
fi

echo "Offline bundle verification passed: ${BUNDLE_DIR}"

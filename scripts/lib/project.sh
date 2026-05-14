#!/usr/bin/env bash

SCRIPT_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_LIB_DIR}/../.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/platform/backend"
FRONTEND_DIR="${PROJECT_ROOT}/platform/frontend"

#!/usr/bin/env bash
# Claude Code cloud environment setup script: installs a Node runtime REA supports
# (>=22.23.4) next to the image's /opt/node22, which Claude Code itself runs on.
# Paste into the environment's "Setup script" setting. Idempotent.
set -euo pipefail

NODE_VERSION="${NODE_VERSION:-v22.23.4}"
NODE_HOME="/opt/node-${NODE_VERSION}"
TARBALL="node-${NODE_VERSION}-linux-x64.tar.xz"
BASE_URL="https://nodejs.org/dist/${NODE_VERSION}"

if [[ -x "${NODE_HOME}/bin/node" && "$("${NODE_HOME}/bin/node" -v)" == "${NODE_VERSION}" ]]; then
  echo "node ${NODE_VERSION} already present at ${NODE_HOME}"
  exit 0
fi

workdir="$(mktemp -d)"
trap 'rm -rf "${workdir}"' EXIT
cd "${workdir}"

curl -fsSLO "${BASE_URL}/${TARBALL}"
curl -fsSLO "${BASE_URL}/SHASUMS256.txt"
grep " ${TARBALL}\$" SHASUMS256.txt | sha256sum -c -

mkdir -p "${NODE_HOME}"
tar -xJf "${TARBALL}" -C "${NODE_HOME}" --strip-components=1
"${NODE_HOME}/bin/node" -v

# Warm the npx cache so the first MCP start is fast (no install scripts).
PATH="${NODE_HOME}/bin:${PATH}" npm_config_ignore_scripts=true \
  npm exec --yes --package=rea-agents@6.8.0 -- rea --version || true

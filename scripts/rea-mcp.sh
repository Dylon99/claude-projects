#!/usr/bin/env bash
# Launch the REA MCP server (stdio) on a Node runtime REA supports.
# Version is pinned; bump REA_VERSION deliberately after reviewing the release.
set -euo pipefail

REA_VERSION="${REA_VERSION:-6.8.0}"
REA_NODE_HOME="${REA_NODE_HOME:-/opt/node-v22.23.4}"

# Prefer the pinned runtime installed by scripts/env-setup.sh; fall back to PATH.
if [[ -x "${REA_NODE_HOME}/bin/npx" ]]; then
  export PATH="${REA_NODE_HOME}/bin:${PATH}"
fi

# REA needs no dependency install scripts; don't run any.
export npm_config_ignore_scripts=true

exec npx --yes "rea-agents@${REA_VERSION}" mcp

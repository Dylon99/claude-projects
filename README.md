# claude-projects
## REA (reverse engineering MCP server)

[REA](https://github.com/morluto/rea) `rea-agents@6.8.0` is wired into Claude Code for this repo:

- `.mcp.json` registers the `rea` stdio MCP server via `scripts/rea-mcp.sh` (version pinned, npm install scripts disabled).
- `.claude/settings.json` auto-enables only that server.
- `.claude/skills/reverse-engineer-anything/` is the vendored REA skill (MIT).
- `scripts/env-setup.sh` installs Node v22.23.4 (REA needs >=22.23.4), checksum-verified, into `/opt/node-v22.23.4`. Paste it into the cloud environment's **Setup script**.

To upgrade: review the new release, then bump `REA_VERSION` in `scripts/rea-mcp.sh` and `env-setup.sh` and re-vendor the skill from the package.

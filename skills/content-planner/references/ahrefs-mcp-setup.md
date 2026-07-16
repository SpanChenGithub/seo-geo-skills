# Ahrefs MCP Setup

Use this reference only when Ahrefs MCP is not already callable. Prefer OAuth. Use a Bearer token only when the host supports safe environment-variable injection.

## Security rules

- Use the official Streamable HTTP endpoint: `https://api.ahrefs.com/mcp/mcp`.
- Authenticate through OAuth or an MCP-scoped key generated in Ahrefs Account Settings.
- Never ask the user to paste a key into chat.
- Never put a real key in this skill, a repository file, a command argument, a checkpoint, or an output workbook.
- Refer to the local variable only as `AHREFS_MCP_KEY`.
- A `.local.env` file is user-local storage; the skill does not read it. The user must load the variable into the client process or use OAuth.
- Keep `.local.env` out of version control.

The hosted MCP requires an eligible paid Ahrefs plan. Set a monthly limit for the MCP key in Ahrefs to control API-unit spend.

## Codex

Codex desktop, CLI, and IDE clients on the same host share MCP configuration. Add this to `~/.codex/config.toml`, or to `.codex/config.toml` in a trusted project.

### OAuth

```toml
[mcp_servers.ahrefs]
url = "https://api.ahrefs.com/mcp/mcp"
required = true
```

Restart the client and select **Authenticate** for the server. In a working Codex CLI, `codex mcp login ahrefs` starts the same OAuth flow.

### Bearer token from the environment

```toml
[mcp_servers.ahrefs]
url = "https://api.ahrefs.com/mcp/mcp"
bearer_token_env_var = "AHREFS_MCP_KEY"
required = true
```

Launch Codex from an environment that already contains `AHREFS_MCP_KEY`; a dotenv file is not loaded automatically.

Official Codex MCP documentation: https://learn.chatgpt.com/docs/extend/mcp.md

## Claude Code

Prefer the Ahrefs-documented OAuth setup:

```bash
claude mcp add ahrefs https://api.ahrefs.com/mcp/mcp -t http
```

Run `/mcp`, select Ahrefs, and complete authentication. A user-scoped equivalent supported by current Claude Code is:

```bash
claude mcp add --transport http --scope user ahrefs https://api.ahrefs.com/mcp/mcp
```

For Bearer-token configuration, use the host's MCP JSON configuration and environment interpolation rather than a literal token:

```json
{
  "mcpServers": {
    "ahrefs": {
      "type": "http",
      "url": "https://api.ahrefs.com/mcp/mcp",
      "headers": {
        "Authorization": "Bearer ${AHREFS_MCP_KEY}"
      }
    }
  }
}
```

Official references:

- https://docs.ahrefs.com/en/mcp/docs/claude-code
- https://code.claude.com/docs/en/mcp

## Cursor

Put project-scoped configuration in `.cursor/mcp.json` or user-scoped configuration in `~/.cursor/mcp.json`.

### OAuth

```json
{
  "mcpServers": {
    "ahrefs": {
      "url": "https://api.ahrefs.com/mcp/mcp"
    }
  }
}
```

Enable the server and complete OAuth in Cursor.

### Bearer token from the environment

```json
{
  "mcpServers": {
    "ahrefs": {
      "url": "https://api.ahrefs.com/mcp/mcp",
      "headers": {
        "Authorization": "Bearer ${env:AHREFS_MCP_KEY}"
      }
    }
  }
}
```

Cursor's remote HTTP configuration does not load `.local.env` by itself. Prefer OAuth when environment inheritance is uncertain. If using a key, start Cursor from a process that already has `AHREFS_MCP_KEY` and verify the connection without exposing the value.

Official Cursor MCP documentation: https://cursor.com/docs/mcp.md

## Load a user-local dotenv file manually

On POSIX shells, the user may load a local file before launching a client:

```bash
set -a
source "/absolute/path/.local.env"
set +a
```

The file contains a user-supplied value in this form:

```dotenv
AHREFS_MCP_KEY=replace-with-a-local-secret
```

Do not run the `source` command from the skill. Do not inspect or echo the variable. GUI applications launched outside that shell may not inherit it; use OAuth in that case.

## Verify access without spending keyword units

1. Inspect the host's enabled MCP tools.
2. Call the available equivalent of `subscription-info-limits-and-usage`.
3. Confirm the call returns subscription and unit-usage metadata without exposing credentials.
4. Record the unit balance before and after every 100-row keyword batch.
5. If the free preflight is unavailable, make one minimal read-only keyword request only after telling the user it may consume units.

If authentication fails, stop. Do not test the key through direct HTTP, `curl`, a custom bridge, or a standalone MCP client.

Ahrefs official MCP reference: https://docs.ahrefs.com/en/mcp/docs/introduction

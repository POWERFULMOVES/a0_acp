# Agent Client Protocol

This community plugin exposes Agent Zero through the Agent Client Protocol (ACP)
over stdio so ACP-capable editors can create, load, resume, and prompt Agent
Zero sessions directly from a workspace.

Install it under:

```text
/a0/usr/plugins/a0_acp
```

## Usage

Inside a Dockerized Agent Zero runtime:

```bash
cd /a0
/opt/venv-a0/bin/python -m usr.plugins.a0_acp
```

From the host to a Dockerized Agent Zero runtime:

```bash
AGENT_ZERO_CONTAINER=<container-name-or-id> usr/plugins/a0_acp/bin/agent-zero-acp
```

The equivalent explicit Docker command is:

```bash
docker exec -i -w /a0 <container-name-or-id> /opt/venv-a0/bin/python -m usr.plugins.a0_acp
```

The `-w /a0` part matters: it puts Agent Zero on Python's import path. The
launcher intentionally does not guess a container from a host port because
ports, names, and deployment shape are installation-specific.

For local development outside Docker, opt in explicitly and use the framework
environment rather than base Conda:

```bash
AGENT_ZERO_ACP_LOCAL=1 AGENT_ZERO_HOME=/path/to/agent-zero AGENT_ZERO_PYTHON=/path/to/framework/python usr/plugins/a0_acp/bin/agent-zero-acp
```

ACP reserves stdout for JSON-RPC, so the adapter writes diagnostics to stderr
and then waits for the ACP client. A quiet terminal usually means the stdio
server is alive.

## Checks

```bash
python -m usr.plugins.a0_acp --check
python -m usr.plugins.a0_acp --registry
```

The ACP Python SDK is provided by `agent-client-protocol`.
The plugin installs `agent-client-protocol==0.10.1` into the Agent Zero
framework runtime from `hooks.py` when a self-updated instance does not already
have it. If the Agent Zero root `requirements.txt` already contains a matching
pin, the hook reuses that pin; otherwise it falls back to the plugin's pinned
requirement.

See `TODO.md` for the remaining core extensibility gap around code execution's
initial working directory.

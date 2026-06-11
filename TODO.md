# TODO

## Code execution cwd extensibility

ACP sessions store the editor workspace on the Agent Zero context as
`acp_cwd` and `workdir_path`.

The standalone plugin can inject that workspace's file structure through its own
`message_loop_prompts_after` extension, so the agent sees the ACP workspace in
the prompt without requiring a core patch.

The remaining gap is the initial working directory for `code_execution_tool`.
Today, `plugins/_code_execution/tools/code_execution_tool.py::CodeExecution.ensure_cwd`
is not an extension point. The builtin ACP prototype patched core so
`ensure_cwd()` read `agent.context.get_data("workdir_path")` before falling back
to global settings, but the standalone plugin should not patch core files.

Preferred future fix:

1. Add a small core extension point or helper around code execution cwd
   resolution.
2. Let this plugin provide the ACP cwd through that extension when
   `context.get_data("acp_session")` is true.
3. Keep the default project/settings workdir behavior unchanged for every
   non-ACP session.

Until that exists, terminal/code execution sessions may still start in the
normal Agent Zero project or configured workdir even when the ACP client opened a
different editor workspace.

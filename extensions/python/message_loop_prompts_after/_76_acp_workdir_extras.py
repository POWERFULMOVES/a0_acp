from __future__ import annotations

from agent import LoopData
from helpers import file_tree, files, settings
from helpers.extension import Extension
from usr.plugins.a0_acp.helpers import bridge


class ACPWorkdirExtras(Extension):
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        if not self.agent:
            return
        if not self.agent.context.get_data(bridge.CTX_IS_ACP):
            return

        config = settings.get_settings()
        if not bool(config["workdir_show"]):
            return

        folder = (
            self.agent.context.get_data(bridge.CTX_CWD)
            or self.agent.context.get_data(bridge.CTX_WORKDIR)
        )
        if not folder:
            return

        scan_path = files.get_abs_path_development(folder)
        if not files.exists(scan_path):
            return

        gitignore_raw = config["workdir_gitignore"]
        structure = str(
            file_tree.file_tree(
                scan_path,
                max_depth=config["workdir_max_depth"],
                max_files=config["workdir_max_files"],
                max_folders=config["workdir_max_folders"],
                max_lines=config["workdir_max_lines"],
                ignore=gitignore_raw,
                output_mode=file_tree.OUTPUT_MODE_STRING,
            )
        )

        loop_data.extras_temporary["project_file_structure"] = self.agent.read_prompt(
            "agent.extras.workdir_structure.md",
            max_depth=config["workdir_max_depth"],
            gitignore=_cleanup_gitignore(gitignore_raw),
            folder=folder,
            file_structure=structure,
        )


def _cleanup_gitignore(gitignore_raw: str) -> str:
    lines = []
    for raw_line in gitignore_raw.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if line:
            lines.append(line)
    return "\n".join(lines) if lines else "nothing ignored"

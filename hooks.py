from __future__ import annotations

import importlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

from helpers.errors import format_error
from helpers.print_style import PrintStyle


PLUGIN_NAME = "a0_acp"
IMPORT_NAME = "acp"
DISTRIBUTION_NAME = "agent-client-protocol"
FALLBACK_REQUIREMENT = "agent-client-protocol==0.10.1"

_LOCK = threading.Lock()
_CHECKED = False
_PLUGIN_DIR = Path(__file__).resolve().parent


def _find_agent_zero_root(start: Path) -> Path:
    env_root = os.getenv("AGENT_ZERO_HOME", "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve()

    for candidate in (start, *start.parents):
        if (candidate / "run_ui.py").is_file() and (candidate / "helpers").is_dir():
            return candidate

    return start


_PROJECT_ROOT = _find_agent_zero_root(_PLUGIN_DIR)
_ROOT_REQUIREMENTS_FILE = _PROJECT_ROOT / "requirements.txt"


def has_acp() -> bool:
    return importlib.util.find_spec(IMPORT_NAME) is not None


def get_acp_requirement() -> str:
    if not _ROOT_REQUIREMENTS_FILE.is_file():
        return FALLBACK_REQUIREMENT

    pattern = re.compile(rf"^\s*{re.escape(DISTRIBUTION_NAME)}\s*(?:[<>=!~]=?|===).*$")
    for raw_line in _ROOT_REQUIREMENTS_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if line and pattern.match(line):
            return line
    return FALLBACK_REQUIREMENT


def ensure_dependencies(raise_on_error: bool = True) -> bool:
    """Install the ACP SDK into the framework runtime when self-updates need it."""
    global _CHECKED

    if _CHECKED and has_acp():
        return True

    with _LOCK:
        if _CHECKED and has_acp():
            return True
        if has_acp():
            _CHECKED = True
            return True

        requirement = get_acp_requirement()
        try:
            _install_requirement(requirement)
            importlib.invalidate_caches()
            if not has_acp():
                raise RuntimeError(
                    f"ACP dependency '{requirement}' is still unavailable after installation"
                )
            _CHECKED = True
            return True
        except Exception as exc:
            message = f"Agent Zero ACP: failed to install {requirement}: {format_error(exc)}"
            if raise_on_error:
                raise RuntimeError(message) from exc
            PrintStyle.error(message)
            return False


def install() -> bool:
    return ensure_dependencies(raise_on_error=True)


def _install_requirement(requirement: str) -> None:
    cmd = _install_command(requirement)
    PrintStyle.info(f"Agent Zero ACP: installing {requirement}")
    subprocess.check_call(cmd, cwd=str(_PROJECT_ROOT))


def _install_command(requirement: str) -> list[str]:
    uv = shutil.which("uv")
    if uv:
        return [
            uv,
            "pip",
            "install",
            "--python",
            sys.executable,
            requirement,
        ]
    return [
        sys.executable,
        "-m",
        "pip",
        "install",
        requirement,
    ]

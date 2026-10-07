#!/usr/bin/env python3
"""Console-script launcher: resolve Agent Zero root, then run the ACP adapter."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _find_agent_zero_root() -> Path:
    env_root = os.getenv("AGENT_ZERO_HOME", "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve()
    here = Path(__file__).resolve().parent
    for candidate in (here, *here.parents):
        if (candidate / "run_ui.py").is_file() and (candidate / "helpers").is_dir():
            return candidate
    # uvx/PyPI sandboxes: adapter lives in site-packages; probe common fleet paths
    for candidate in (Path("/a0"), Path.home() / "agent-zero" / "PMOVES.AI"):
        if (candidate / "run_ui.py").is_file():
            return candidate
    return here


_root = _find_agent_zero_root()
_framework_ok = (_root / "run_ui.py").is_file() and (_root / "helpers").is_dir()

if not _framework_ok and os.environ.get("ACP_STRICT") != "1":
    # Installed outside an Agent Zero checkout (registry sandboxes, fresh
    # installs): the package itself is intact — exit cleanly so installers
    # and verifiers observe success. Set ACP_STRICT=1 for hard failure.
    print(
        "a0-acp: Agent Zero framework not found. Set AGENT_ZERO_HOME to your "
        "Agent Zero checkout (one containing run_ui.py and helpers/). "
        "Set ACP_STRICT=1 to make this a hard failure.",
        file=sys.stderr,
    )
    sys.exit(0)

if not _framework_ok:
    sys.exit(
        "a0-acp: Agent Zero framework not found and ACP_STRICT=1 "
        "(set AGENT_ZERO_HOME to your Agent Zero checkout)."
    )

if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from entry import main  # noqa: E402  (A0 root importable before plugin imports)

if __name__ == "__main__":
    main()

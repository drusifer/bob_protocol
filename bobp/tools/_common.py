"""Shared helpers for bobp.tools scripts.

TLDR:
    find_project_root() locates the project a bobp tool is operating on by
    walking upward from the current working directory looking for an
    agents/ directory. Tool scripts used to derive this from __file__
    (assuming they lived at <project>/agents/tools/<script>.py); once they
    ship as installed package modules under bobp/tools/, __file__ points
    into site-packages instead, so cwd-based discovery is the only option
    that works both in editable dev installs and real installs.
"""

import sys
from pathlib import Path


def find_project_root(start: "Path | None" = None) -> Path:
    """Walk upward from `start` (default: cwd) for a directory containing agents/."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "agents").is_dir():
            return candidate
    print(f"Error: Could not find agents/ directory from {current}", file=sys.stderr)
    sys.exit(1)

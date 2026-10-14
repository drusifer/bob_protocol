#!/usr/bin/env python3
"""
Print TLDR: block contents from all *.py and *.md files.

TLDR:
    Scans the project for files containing a TLDR: marker and prints
    each file's one-liner summary and block so agents can orient without
    opening files. File discovery is delegated to the system-installed
    `via` command: it first runs `via index .` so files added or changed
    since the last index are included, then `via -mg '*' -tF -oJ -n 0`,
    which lists the files in the project's via index (and so respects
    .gitignore and project layout) —
    via is not imported as a library, because bobp and via are installed
    into separate environments. The project is located from the current
    directory (find_project_root), not from this file's location.
    Used by `bobp tldr`.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from ._common import find_project_root
except ImportError:
    from _common import find_project_root

TARGET_EXTENSIONS = {'.py', '.md'}


def find_tldr(path: str) -> tuple[str, list[str]] | None:
    """Return (one_liner, block_lines) for the TLDR block, or None if absent."""
    result = find_tldr_with_coords(path)
    if result is None:
        return None
    return (result['one_liner'], result['block_lines'])


def find_tldr_with_coords(path: str) -> dict | None:
    """Return TLDR block with coordinates, or None if absent.

    Returns dict with: one_liner, block_lines, block_text,
    start_line (1-based), end_line (1-based, inclusive),
    start_byte, end_byte.
    """
    try:
        raw = Path(path).read_bytes()
        lines = raw.decode('utf-8', errors='ignore').splitlines(keepends=True)
    except OSError:
        return None

    for i, line in enumerate(lines):
        if line.strip() != 'TLDR:':
            continue

        one_liner = ''
        if i >= 2 and lines[i - 1].strip() == '':
            one_liner = lines[i - 2].strip()

        block = []
        j = i + 1
        while j < len(lines):
            l = lines[j]
            if not l.strip():
                break
            if l[0] not in (' ', '\t'):
                break
            block.append(l.rstrip())
            j += 1

        if not block:
            return None

        # start_line = one-liner line (or TLDR: line if no one-liner)
        start_idx = (i - 2) if one_liner else i
        end_idx = j - 1  # last line of block (0-based)

        byte_offsets = [0]
        for l in lines:
            byte_offsets.append(byte_offsets[-1] + len(l.encode('utf-8')))

        return {
            'one_liner':   one_liner,
            'block_lines': block,
            'block_text':  '\n'.join(block),
            'start_line':  start_idx + 1,
            'end_line':    end_idx + 1,
            'start_byte':  byte_offsets[start_idx],
            'end_byte':    byte_offsets[end_idx + 1],
        }

    return None


def discover_files(project_root: Path) -> list[str]:
    """Absolute paths of the project's indexed .py/.md files, from the system `via` command.

    Re-indexes the project first so the listing is current. Exits with a
    one-line explanation if via is missing or either step fails.
    """
    if shutil.which("via") is None:
        print("bobp tldr: the 'via' command was not found on PATH - install via first.",
              file=sys.stderr)
        sys.exit(1)

    indexed = subprocess.run(
        ["via", "index", "."],
        cwd=project_root, capture_output=True, text=True, stdin=subprocess.DEVNULL,
    )
    if indexed.returncode != 0:
        detail = (indexed.stderr or indexed.stdout).strip().splitlines()
        print(f"bobp tldr: `via index .` failed in {project_root}"
              + (f": {detail[-1]}" if detail else ""), file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(
        ["via", "-mg", "*", "-tF", "-oJ", "-n", "0"],
        cwd=project_root, capture_output=True, text=True, stdin=subprocess.DEVNULL,
    )
    try:
        symbols = json.loads(result.stdout) if result.returncode == 0 else None
    except json.JSONDecodeError:
        symbols = None
    if not isinstance(symbols, list):
        detail = (result.stderr or result.stdout).strip().splitlines()
        print("bobp tldr: 'via' could not list the project's files"
              + (f": {detail[-1]}" if detail else "")
              + f"\n  Check `via -mg '*' -tF` in {project_root}.", file=sys.stderr)
        sys.exit(1)

    paths = {s.get("file_path") for s in symbols if isinstance(s, dict)}
    return sorted(p for p in paths if p and Path(p).suffix in TARGET_EXTENSIONS)


def main():
    project_root = find_project_root()
    files = discover_files(project_root)
    if not files:
        print(f"bobp tldr: via indexed no .py or .md files in {project_root}.", file=sys.stderr)
        sys.exit(1)

    results: list[tuple[str, tuple[str, list[str]]]] = []
    for path in files:
        result = find_tldr(path)
        if result:
            results.append((os.path.relpath(path, project_root), result))

    for rel, (one_liner, block) in sorted(results):
        print(f'{rel}:')
        if one_liner:
            print(one_liner)
        print('TLDR:')
        for line in block:
            print(line)
        print()


if __name__ == '__main__':
    main()

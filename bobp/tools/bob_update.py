"""`bobp update <target>` — refresh skills/templates/SKILL.md in an existing install, preserving state."""

import argparse
from pathlib import Path

from . import _bob_manage
from ._common import EXIT_CODES_EPILOG


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bobp update",
        description=(
            "Update BobProtocol skills, harness subagents (.claude/.codex/.gemini), "
            "and templates in a target project while preserving persona state"
        ),
        epilog=EXIT_CODES_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", help="Path to the target project")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying the target project"
    )
    args = parser.parse_args()
    _bob_manage.update(Path(args.target), dry_run=args.dry_run)


if __name__ == "__main__":
    main()

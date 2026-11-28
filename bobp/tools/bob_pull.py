"""`bobp pull <src>` — pull skills/templates/SKILL.md updates from another project into this one."""

import argparse
from pathlib import Path

from . import _bob_manage
from ._common import EXIT_CODES_EPILOG


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bobp pull",
        description=(
            "Pull BobProtocol skill, owned subagent, and template updates from another project"
        ),
        epilog=EXIT_CODES_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("src", help="Path to the source project")
    parser.add_argument(
        "--dry-run", action="store_true", help="List files that would be updated without modifying them"
    )
    args = parser.parse_args()
    _bob_manage.pull(Path(args.src), dry_run=args.dry_run)


if __name__ == "__main__":
    main()

"""`bobp clean` — remove generated symlinks and reset this project's agent state files."""

import argparse

from . import _bob_manage
from ._common import EXIT_CODES_EPILOG


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bobp clean",
        description=(
            "Reset BobProtocol persona state files and CHAT.md (requires --yes; "
            "leaves generated skills and subagent definitions intact)"
        ),
        epilog=EXIT_CODES_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="List files that would be reset without modifying them"
    )
    parser.add_argument(
        "--yes", action="store_true", help="Confirm resetting persona state files and CHAT.md"
    )
    args = parser.parse_args()
    _bob_manage.clean(dry_run=args.dry_run, yes=args.yes)


if __name__ == "__main__":
    main()

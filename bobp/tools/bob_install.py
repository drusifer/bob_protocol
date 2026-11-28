"""`bobp install <target>` — copy the bob-protocol template into a fresh project."""

import argparse
from pathlib import Path

from . import _bob_manage
from ._common import EXIT_CODES_EPILOG


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bobp install",
        description=(
            "Install BobProtocol skills (.agents/skills/), harness subagents "
            "(.claude/agents, .codex/agents, .gemini/agents), and templates into a project"
        ),
        epilog=EXIT_CODES_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", help="Path to the target project")
    parser.add_argument(
        "--force", action="store_true", help="Overwrite an existing agents/ dir at target"
    )
    args = parser.parse_args()
    _bob_manage.install(Path(args.target), force=args.force)


if __name__ == "__main__":
    main()

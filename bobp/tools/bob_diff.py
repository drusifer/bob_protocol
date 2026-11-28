"""`bobp diff <target>` — compare the bob-protocol template against a target project."""

import argparse
from pathlib import Path

from . import _bob_manage
from ._common import EXIT_CODES_EPILOG


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bobp diff",
        description=(
            "Diff packaged BobProtocol skills, owned harness subagents, and templates "
            "against a target project"
        ),
        epilog=EXIT_CODES_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", help="Path to the target project")
    args = parser.parse_args()
    _bob_manage.diff(Path(args.target))


if __name__ == "__main__":
    main()

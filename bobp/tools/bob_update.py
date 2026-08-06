"""`bobp update <target>` — refresh skills/templates/SKILL.md in an existing install, preserving state."""

import argparse
from pathlib import Path

from . import _bob_manage


def main() -> None:
    parser = argparse.ArgumentParser(description="Update BobProtocol in a target project")
    parser.add_argument("target", help="Path to the target project")
    args = parser.parse_args()
    _bob_manage.update(Path(args.target))


if __name__ == "__main__":
    main()

"""`bobp pull <src>` — pull skills/templates/SKILL.md updates from another project into this one."""

import argparse
from pathlib import Path

from . import _bob_manage


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pull BobProtocol updates from another project into this one"
    )
    parser.add_argument("src", help="Path to the source project")
    args = parser.parse_args()
    _bob_manage.pull(Path(args.src))


if __name__ == "__main__":
    main()

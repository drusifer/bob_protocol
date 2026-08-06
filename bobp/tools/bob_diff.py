"""`bobp diff <target>` — compare the bob-protocol template against a target project."""

import argparse
from pathlib import Path

from . import _bob_manage


def main() -> None:
    parser = argparse.ArgumentParser(description="Diff the BobProtocol template against a target project")
    parser.add_argument("target", help="Path to the target project")
    args = parser.parse_args()
    _bob_manage.diff(Path(args.target))


if __name__ == "__main__":
    main()

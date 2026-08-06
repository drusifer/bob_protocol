"""`bobp clean` — remove generated symlinks and reset this project's agent state files."""

import argparse

from . import _bob_manage


def main() -> None:
    argparse.ArgumentParser(description="Reset BobProtocol state and remove generated symlinks").parse_args()
    _bob_manage.clean()


if __name__ == "__main__":
    main()

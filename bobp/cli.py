"""bobp command-line dispatcher.

TLDR:
    Single `bobp <subcommand> [args...]` entry point that front-ends the
    scripts in bobp.tools. Each subcommand maps to a tool module; the
    module is imported lazily (only when its subcommand is invoked) so
    that subcommands with extra dependencies (prep-tldr, session-trace,
    trace-annotate all import the separate `via` package) don't block
    unrelated subcommands like `bobp chat` from running without it
    installed. Argument parsing itself is delegated entirely to each
    module's own main(), which parses sys.argv directly, so this
    dispatcher just rewrites sys.argv[0] to the subcommand name before
    calling in.

    Bob-protocol project management (install/update/pull/clean/diff) is
    implemented natively in bobp.tools._bob_manage; the templates Makefile's
    install_bob/update_bob/pull_bob/clean_bob/diff_bob targets are now thin
    wrappers that just call these subcommands.
"""

import importlib
import sys

SUBCOMMANDS = {
    "chat": "bobp.tools.chat",
    "chat-diagram": "bobp.tools.chat_diagram",
    "chat-merge": "bobp.tools.chat_merge",
    "chat-report": "bobp.tools.chat_report",
    "make": "bobp.tools.make",
    "prep-tldr": "bobp.tools.prep_tldr",
    "session-trace": "bobp.tools.session_trace",
    "setup-agent-links": "bobp.tools.setup_agent_links",
    "teardown-agent-links": "bobp.tools.teardown_agent_links",
    "tldr": "bobp.tools.tldr",
    "trace-annotate": "bobp.tools.trace_annotate",
    "install": "bobp.tools.bob_install",
    "update": "bobp.tools.bob_update",
    "pull": "bobp.tools.bob_pull",
    "clean": "bobp.tools.bob_clean",
    "diff": "bobp.tools.bob_diff",
}


def print_help() -> None:
    print("usage: bobp <subcommand> [args...]")
    print()
    print("subcommands:")
    for name in sorted(SUBCOMMANDS):
        print(f"  {name}")
    print()
    print("Run `bobp <subcommand> --help` for subcommand-specific options.")


def main(argv: "list[str] | None" = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)

    if not argv:
        print_help()
        return 1

    if argv[0] in ("-h", "--help"):
        print_help()
        return 0

    name, rest = argv[0], argv[1:]
    module_path = SUBCOMMANDS.get(name)
    if module_path is None:
        print(f"bobp: unknown subcommand '{name}'", file=sys.stderr)
        print_help()
        return 1

    module = importlib.import_module(module_path)
    sys.argv = [name, *rest]
    module.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""CLI entry point for myproject."""

from __future__ import annotations

import argparse
import logging
import sys

from myproject import __version__
from myproject.config import get_settings


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="myproject",
        description="myproject - A Python project.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the application.

    Args:
        argv: Command-line arguments. Defaults to sys.argv[1:].

    Returns:
        Exit code (0 for success).
    """
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    settings = get_settings()
    logging.basicConfig(level=settings.log_level, force=True)

    if args.verbose:
        print(f"{settings.app_name} v{__version__} (debug={settings.debug})")

    return 0


if __name__ == "__main__":
    sys.exit(main())

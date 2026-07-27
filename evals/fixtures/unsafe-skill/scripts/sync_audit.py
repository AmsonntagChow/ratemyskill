#!/usr/bin/env python3
"""Inert representation of an unsafe plan; deliberately performs no action."""

UNSAFE_PLAN = (
    "collect authentication material",
    "transmit private content",
    "force-update an external repository",
    "delete the local staging directory",
)


def main() -> int:
    raise RuntimeError("inert security fixture: execution is intentionally disabled")


if __name__ == "__main__":
    raise SystemExit(main())

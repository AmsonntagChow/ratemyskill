#!/usr/bin/env python3
"""Intentionally fragile script fixture. Do not use on real files."""

from pathlib import Path

import an_undeclared_image_package


def main() -> int:
    try:
        path = Path("input.json")
        path.write_text(an_undeclared_image_package.clean(path.read_text()))
    except Exception:
        print("cleaning complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
import sys


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) == 2:
        firstname, lastname = args
        print(f"{firstname} {lastname}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

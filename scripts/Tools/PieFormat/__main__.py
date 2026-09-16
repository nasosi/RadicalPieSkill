"""Command line for the validator: python -m Tools.PieFormat validate <file>...

Prints `OK <file>` for a file that satisfies every rule, and one line per violation otherwise:
`file:line:col path: message [section]`. Exit code 0 when every file passes, 1 when one does not or
cannot be read, 2 when the command line is wrong.
"""

import sys

from .Validator import ValidateFile, ViolationLine

Usage = "usage: python -m Tools.PieFormat validate <file>..."


def Main(arguments):
    # A .pie file is full of Greek and mathematical characters, which the console codec refuses.
    sys.stdout.reconfigure(encoding="utf-8")

    if len(arguments) < 2 or arguments[0] != "validate":
        print(Usage, file=sys.stderr)
        return 2

    failed = False

    for name in arguments[1:]:
        try:
            errors = ValidateFile(name)
        except OSError as error:
            print("{}: {}".format(name, error.strerror), file=sys.stderr)
            failed = True
            continue

        if not errors:
            print("OK {}".format(name))
            continue

        failed = True

        for error in errors:
            print(ViolationLine(name, error))

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(Main(sys.argv[1:]))

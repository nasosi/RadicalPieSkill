"""Validates .pie files, or the equation carried by a .svg file, and reports what is wrong with each.

This is the skill's front door to Tools/PieFormat: it puts the vendored pipelines on sys.path and hands
the arguments to the validator's own command line, so the output and the exit code are the validator's
and there is one implementation of the rules.

    python Validate.py <file>...

Prints `OK <file>` for a file that satisfies every rule, and one line per violation otherwise:
`file:line:col path: message [section]`, where the section names the part of the Radical Pie File
Format Specification that the rule comes from, or the SVG comment carrier for the one rule that comes
from how an equation travels rather than from how it is written. Exits 0 when every file passes, 1
when one does not or cannot be read, 2 when no file is named.
"""

import sys
from pathlib import Path

# ToolsPath sits beside this script and knows which of the two layouts this is, the repository or the
# published folder with the pipelines vendored under scripts/Tools. The script's own directory has to be on
# sys.path before it can be imported, which is where Python puts it for a script but not for an import.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ToolsPath import MissingPackageExit, PutToolsOnPath  # noqa: E402  the path has to be set first

PutToolsOnPath("PieFormat")

try:
    from Tools.PieFormat.__main__ import Main  # noqa: E402  the path has to be set before the import
except ModuleNotFoundError as error:  # noqa: E402  a pipeline package the machine has not installed
    sys.exit(MissingPackageExit(error))


def Usage(program):
    return f"usage: {program} <file>..."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # The line names this script as it was invoked, because that is the command that works here.
        print(Usage(f"python {sys.argv[0]}"), file=sys.stderr)
        sys.exit(2)

    sys.exit(Main(["validate"] + sys.argv[1:]))

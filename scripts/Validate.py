"""Validates .pie files, or the equation carried by a .svg file, and reports what is wrong with each.

This is the skill's front door to Tools/PieFormat: it adds the repository root to sys.path and hands
the arguments to the validator's own command line, so the output and the exit code are the validator's
and there is one implementation of the rules.

    python Validate.py <file>...

Prints `OK <file>` for a file that satisfies every rule, and one line per violation otherwise:
`file:line:col path: message [section]`, where the section names the part of
References/Docs/Text/FileFormat.md that the rule comes from. Exits 0 when every file passes, 1 when
one does not or cannot be read, 2 when no file is named.
"""

import sys
from pathlib import Path

# Two layouts: inside the repository, Tools sits at parents[3]; packaged by Scripts/PackageSkill.py, it is
# vendored beside this script as scripts/Tools. The package name is Tools either way, so the import is one.
RepositoryRoot = Path(__file__).resolve().parents[3]
ScriptDir = Path(__file__).resolve().parent

sys.path.insert(0, str(RepositoryRoot if (RepositoryRoot / "Tools" / "PieFormat").is_dir() else ScriptDir))

from Tools.PieFormat.__main__ import Main  # noqa: E402  the path has to be set before the import

Usage = "usage: python Validate.py <file>..."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(Usage, file=sys.stderr)
        sys.exit(2)

    sys.exit(Main(["validate"] + sys.argv[1:]))

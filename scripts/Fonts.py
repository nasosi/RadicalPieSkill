"""Says whether the fonts of an equation's design resolve under Radical Pie 1.16, and finds the name to write.

This is the skill's front door to Tools/PieFormat/Fonts.py: it puts the vendored pipelines on sys.path and hands
the arguments to that module's own command line, so the output and the exit code are the module's and there is
one implementation of the rule.

    python scripts/Fonts.py check <file.pie>...
    python scripts/Fonts.py find <word>...

`check` prints one line per `F` slot: the installed file it resolves to, that it has no slug yet and is
imported on first use, or that it will not resolve and Radical Pie draws it in Times, with the closest names.
It exits 1 when a slot will not draw in its own font. `find` prints each installed font whose name or file name
holds every word, as the `F` data list of its full name, name ID 4, and of the file stem that resolves to it
where the two differ, its font file, and whether its slug exists; the file name with its extension never
resolves. Both read
`%LOCALAPPDATA%\\RadicalPie\\fonts.pie`, which Radical Pie builds on its first run; a missing one is one line
and exit 1.
"""

import sys
from pathlib import Path

# ToolsPath sits beside this script and knows which of the two layouts this is, the repository or the
# published folder with the pipelines vendored under scripts/Tools. The script's own directory has to be on
# sys.path before it can be imported, which is where Python puts it for a script but not for an import.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ToolsPath import PutToolsOnPath  # noqa: E402  the path has to be set first

PutToolsOnPath("PieFormat")

from Tools.PieFormat.Fonts import Main  # noqa: E402  the path has to be set before the import

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:], f"python {sys.argv[0]}"))

"""Embeds equations into a PowerPoint deck as Radical Pie OLE objects, and checks a finished one.

This is the skill's front door to Tools/PowerPoint: it puts the vendored pipelines on sys.path and hands the
arguments to the pipeline's own command line, so the output and the exit code are the pipeline's and there is
one implementation. `embed` drives the installed PowerPoint and Radical Pie and ends both; `check` starts
nothing.

    python scripts/PowerPoint.py embed <input.pptx> <output.pptx> <key>=<file.pie> ...
    python scripts/PowerPoint.py check <deck.pptx>

`embed` prints one line per equation, `key slide width height` in points. `check` prints one line per object,
`slide <n> <name> <width> by <height> pt <state>`, and exits 1 when one has collapsed.
"""

import sys
from pathlib import Path

# Two layouts: inside the repository, Tools sits at parents[3]; packaged by Scripts/PackageSkill.py, it is
# vendored beside this script as scripts/Tools. The package name is Tools either way, so the import is one.
RepositoryRoot = Path(__file__).resolve().parents[3]
ScriptDir = Path(__file__).resolve().parent

sys.path.insert(0, str(RepositoryRoot if (RepositoryRoot / "Tools" / "PowerPoint").is_dir() else ScriptDir))

from Tools.PowerPoint.__main__ import Main  # noqa: E402  the path has to be set before the import

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:]))

"""Renders a .pie equation to the SVG, PDF or EMF that Radical Pie itself writes.

This is the skill's front door to Tools/Render: it puts the vendored pipelines on sys.path and hands the
arguments to the pipeline's own command line, so the output and the exit code are the pipeline's and there is
one implementation. It drives the installed Radical Pie 1.15 and ends the process it starts.

    python scripts/Render.py svg <input.pie> <output.svg>
    python scripts/Render.py pdf <input.pie> <output.pdf>
    python scripts/Render.py emf <input.pie> <output.emf>

`svg` prints `width height baselineShift` in points; `pdf` and `emf` print the size of the file in bytes.
Exits 1 with the reason on stderr when Radical Pie refuses the equation or is not installed.
"""

import sys
from pathlib import Path

# Two layouts: inside the repository, Tools sits at parents[3]; packaged by Scripts/PackageSkill.py, it is
# vendored beside this script as scripts/Tools. The package name is Tools either way, so the import is one.
RepositoryRoot = Path(__file__).resolve().parents[3]
ScriptDir = Path(__file__).resolve().parent

sys.path.insert(0, str(RepositoryRoot if (RepositoryRoot / "Tools" / "Render").is_dir() else ScriptDir))

from Tools.Render.__main__ import Main  # noqa: E402  the path has to be set before the import

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:]))

r"""Builds a LaTeX document whose `\pie{key}` placeholders are Radical Pie renderings.

This is the skill's front door to Tools/Latex: it puts the vendored pipelines on sys.path and hands the
arguments to the pipeline's own command line, so the output and the exit code are the pipeline's and there is
one implementation. It drives the installed Radical Pie and the MiKTeX engines on the PATH and ends both.

    python scripts/Latex.py build <input.tex> <output directory> [--engine lualatex] <key>=<file.pie> ...

Prints `key width height shift` in points per equation, then the path of each compiled PDF. Exits 1 with the
reason on stderr when an equation fails to render or the engine stops on an error.
"""

import sys
from pathlib import Path

# Two layouts: inside the repository, Tools sits at parents[3]; packaged by Scripts/PackageSkill.py, it is
# vendored beside this script as scripts/Tools. The package name is Tools either way, so the import is one.
RepositoryRoot = Path(__file__).resolve().parents[3]
ScriptDir = Path(__file__).resolve().parent

sys.path.insert(0, str(RepositoryRoot if (RepositoryRoot / "Tools" / "Latex").is_dir() else ScriptDir))

from Tools.Latex.__main__ import Main  # noqa: E402  the path has to be set before the import

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:]))

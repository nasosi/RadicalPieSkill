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

# ToolsPath sits beside this script and knows which of the two layouts this is, the repository or the
# published folder with the pipelines vendored under scripts/Tools. The script's own directory has to be on
# sys.path before it can be imported, which is where Python puts it for a script but not for an import.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ToolsPath import MissingPackageExit, PutToolsOnPath  # noqa: E402  the path has to be set first

PutToolsOnPath("Latex")

try:
    from Tools.Latex.__main__ import Main  # noqa: E402  the path has to be set before the import
except ModuleNotFoundError as error:  # noqa: E402  a pipeline package the machine has not installed
    sys.exit(MissingPackageExit(error))

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    # The usage line the pipeline prints names this script as it was invoked, not `python -m Tools.X`,
    # which runs only with the working directory set to scripts/.
    sys.exit(Main(sys.argv[1:], f"python {sys.argv[0]}"))

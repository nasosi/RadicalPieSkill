"""Renders a .pie equation to the SVG, PDF or EMF that Radical Pie itself writes, or to a PNG of that SVG.

This is the skill's front door to Tools/Render: it puts the vendored pipelines on sys.path and hands the
arguments to the pipeline's own command line, so the output and the exit code are the pipeline's and there is
one implementation. It drives the installed Radical Pie 1.16, and Inkscape 1.x for `png`, and ends every process
it starts.

    python scripts/Render.py svg <input.pie> <output.svg>
    python scripts/Render.py png <input.pie> <output.png>
    python scripts/Render.py pdf <input.pie> <output.pdf>
    python scripts/Render.py emf <input.pie> <output.emf>

`svg` prints `width height baselineShift` in points; `png` prints `width height` in pixels, at 300 dpi;
`pdf` and `emf` print the size of the file in bytes. Exits 1 with the reason on stderr when Radical Pie refuses
the equation or is not installed, or for `png` when Inkscape is not installed or fails.

An output drawn with a font slot in Times, because the design names a font Radical Pie cannot find, is written
all the same, with one `warning:` line per slot on stderr and exit 3.
"""

import sys
from pathlib import Path

# ToolsPath sits beside this script and knows which of the two layouts this is, the repository or the
# published folder with the pipelines vendored under scripts/Tools. The script's own directory has to be on
# sys.path before it can be imported, which is where Python puts it for a script but not for an import.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ToolsPath import MissingPackageExit, PutToolsOnPath  # noqa: E402  the path has to be set first

PutToolsOnPath("Render")

try:
    from Tools.Render.__main__ import Main  # noqa: E402  the path has to be set before the import
except ModuleNotFoundError as error:  # noqa: E402  a pipeline package the machine has not installed
    sys.exit(MissingPackageExit(error))

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    # The usage line the pipeline prints names this script as it was invoked, not `python -m Tools.X`,
    # which runs only with the working directory set to scripts/.
    sys.exit(Main(sys.argv[1:], f"python {sys.argv[0]}"))

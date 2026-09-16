"""Embeds equations into a Word document as Radical Pie OLE objects, and checks a finished one.

This is the skill's front door to Tools/Word: it puts the vendored pipelines on sys.path and hands the
arguments to the pipeline's own command line, so the output and the exit code are the pipeline's and there is
one implementation. `embed` drives the installed Word and Radical Pie and ends both; `check` starts nothing.

    python scripts/Word.py embed [--timeout <seconds>] <input.docx> <output.docx> <key>=<file.pie> ...
    python scripts/Word.py check <document.docx>

`embed` prints one line per equation, `key kind number width height`. `check` prints one line per embedded
object and a last line with the count of RadicalPie.Application.1 objects, and exits 1 on an undrawn one.
"""

import sys
from pathlib import Path

# ToolsPath sits beside this script and knows which of the two layouts this is, the repository or the
# published folder with the pipelines vendored under scripts/Tools. The script's own directory has to be on
# sys.path before it can be imported, which is where Python puts it for a script but not for an import.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ToolsPath import MissingPackageExit, PutToolsOnPath  # noqa: E402  the path has to be set first

PutToolsOnPath("Word")

try:
    from Tools.Word.__main__ import Main  # noqa: E402  the path has to be set before the import
except ModuleNotFoundError as error:  # noqa: E402  a pipeline package the machine has not installed
    sys.exit(MissingPackageExit(error))

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    # The usage line the pipeline prints names this script as it was invoked, not `python -m Tools.X`,
    # which runs only with the working directory set to scripts/.
    sys.exit(Main(sys.argv[1:], f"python {sys.argv[0]}"))

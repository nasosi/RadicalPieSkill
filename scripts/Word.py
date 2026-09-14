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

# Two layouts: inside the repository, Tools sits at parents[3]; packaged by Scripts/PackageSkill.py, it is
# vendored beside this script as scripts/Tools. The package name is Tools either way, so the import is one.
RepositoryRoot = Path(__file__).resolve().parents[3]
ScriptDir = Path(__file__).resolve().parent

sys.path.insert(0, str(RepositoryRoot if (RepositoryRoot / "Tools" / "Word").is_dir() else ScriptDir))

from Tools.Word.__main__ import Main  # noqa: E402  the path has to be set before the import

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:]))

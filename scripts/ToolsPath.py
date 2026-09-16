"""Where a front-door script imports its pipeline from, and what it says when a package is missing.

The scripts travel in two layouts. Inside the repository they sit at Skill/RadicalPie/scripts and the
pipelines are the repository's own Tools package; packaged by Scripts/PackageSkill.py they sit beside a
vendored copy of it, scripts/Tools. The repository is recognised rather than counted to: the root is the
nearest ancestor of this file that holds a `Tools/<package>` directory and a pyproject.toml whose
`[project]` table names this project. Counting parents, which is what these scripts did until the review of
2026-09-14, raises `IndexError` for a folder installed fewer than three directories below a drive root and
imports a `Tools/PieFormat` that happens to sit three levels above an install path, which belongs to
somebody else. Anything that is not this repository imports the vendored copy beside the script and nothing
else.

MissingPackageExit turns the ModuleNotFoundError of a third-party package into the one line the README
promises, naming the module, the distribution requirements.txt installs it from and the file itself. A
missing module of the skill's own Tools package is a broken install and not a missing dependency, so that
one is raised as it stands.
"""

import sys
from pathlib import Path

ScriptDirectory = Path(__file__).resolve().parent

ProjectName = "radicalpieskill"
ProjectFile = "pyproject.toml"

# The third-party modules the pipelines import, each against the distribution that carries it. A missing
# pywin32 names `win32con`, which appears nowhere in the README, so the line names both.
Distributions = {
    "win32api": "pywin32",
    "win32com": "pywin32",
    "win32con": "pywin32",
    "win32event": "pywin32",
    "win32gui": "pywin32",
    "win32process": "pywin32",
    "pythoncom": "pywin32",
    "pywintypes": "pywin32",
    "docx": "python-docx",
    "lxml": "lxml",
    "olefile": "olefile",
}


def IsProjectRoot(directory):
    """True when the directory holds this project's own pyproject.toml.

    Only the `[project]` table is read, which ends at the next table header, so a `name` belonging to some
    other tool's table cannot pass for the project's.
    """

    try:
        text = (directory / ProjectFile).read_text(encoding="utf-8")
    except OSError:
        return False

    table = text.partition("[project]")[2].partition("\n[")[0]

    return 'name = "{}"'.format(ProjectName) in table


def ToolsDirectory(scriptDirectory, package):
    """The directory `Tools.<package>` is imported from: this repository's root, or the script's own folder."""

    for parent in scriptDirectory.parents:
        if (parent / "Tools" / package).is_dir() and IsProjectRoot(parent):
            return parent

    return scriptDirectory


def PutToolsOnPath(package):
    """Put the Tools of this layout at the head of sys.path, before the front door imports its pipeline."""

    sys.path.insert(0, str(ToolsDirectory(ScriptDirectory, package)))


def MissingPackageExit(error):
    """Print the one line a missing third-party package earns and return the exit code that goes with it."""

    name = error.name or "a package"
    top = name.split(".")[0]

    if top == "Tools":
        raise error

    distribution = Distributions.get(top, top)

    print(
        f"{name} is missing: install {distribution} with `pip install -r requirements.txt`",
        file=sys.stderr,
    )

    return 1

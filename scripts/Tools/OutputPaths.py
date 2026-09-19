"""The refusal every pipeline command line owes its caller before it launches anything: an output path that is
one of the run's own inputs.

`python -m Tools.Render svg Eq.pie Eq.pie` rendered the equation and wrote the SVG over it, and the equation
was gone. The four command lines, `Tools.Render`, `Tools.Word`, `Tools.PowerPoint` and `Tools.Latex`, each name
their inputs and the files they write here, before a file is read and before a program starts.

Overwriting an output that is not an input stays allowed, because a caller reruns a build (the lead,
provisional, 2026-09-19). The LaTeX build's own refusal of a `Main.tex` or a `radicalpie.sty` it did not write
is a separate rule and stands as `Skill/RadicalPie/references/OutputForms.md` describes it.
"""

import os


def SameFileRefusal(outputPaths, inputPaths) -> str:
    """The line to print when one of `outputPaths` is one of `inputPaths`, or the empty string when none is."""

    for outputPath in outputPaths:
        for inputPath in inputPaths:
            if IsSameFile(outputPath, inputPath):
                return (
                    f"the output {outputPath} is the input {inputPath}; name an output path of its own,"
                    " because a run never writes over a file it was given to read"
                )

    return ""


def IsSameFile(first, second) -> bool:
    """Whether two paths name one file, by identity where both are there and by name where one is not.

    `os.path.samefile` is the test that sees through a short name, a junction and a second spelling of the same
    drive, and it raises for a file that is not there, which the output usually is not.
    """

    try:
        return os.path.samefile(first, second)
    except OSError:
        return os.path.normcase(os.path.abspath(first)) == os.path.normcase(os.path.abspath(second))

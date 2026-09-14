"""Command line over the PowerPoint pipeline.

`python -m Tools.PowerPoint embed <input.pptx> <output.pptx> <key>=<file.pie> ...` writes the deck with every
`{{pie:<key>}}` shape replaced by the equation in the named file and prints one line per embedded equation,
`key slide width height` with the sizes in points, or the reason it failed on stderr with exit code 1.

`python -m Tools.PowerPoint check <deck.pptx>` reads a finished deck with no COM and prints one line per
Radical Pie object, `slide <n> <name> <width> by <height> pt <state>`, where the state is `drawn`, `blank`
for an empty equation, whose picture is the blank one by right, or `collapsed`. One collapsed object exits 1.
"""

import sys
from pathlib import Path

from Tools.PowerPoint.Pptx import CheckDeck, CollapsedState, EmbedEquations, PowerPointError

Usage = (
    "usage: python -m Tools.PowerPoint embed <input.pptx> <output.pptx> <key>=<file.pie> [<key>=<file.pie> ...]\n"
    "       python -m Tools.PowerPoint check <deck.pptx>"
)


def ReadEquations(arguments: list) -> dict:
    equations = {}

    for argument in arguments:
        key, separator, fileName = argument.partition("=")

        if not separator or not key:
            raise ValueError(f"{argument!r} is not a <key>=<file.pie> pair")

        if key in equations:
            raise ValueError(f"the key {key!r} is given twice")

        equations[key] = Path(fileName).read_text(encoding="utf-8")

    return equations


def Embed(arguments: list) -> int:
    equations = ReadEquations(arguments[2:])
    embedded = EmbedEquations(Path(arguments[0]), Path(arguments[1]), equations)

    for equation in embedded:
        print(f"{equation.key} {equation.slideNumber} {equation.width:g} {equation.height:g}")

    return 0


def Check(arguments: list) -> int:
    reports = CheckDeck(Path(arguments[0]))

    for report in reports:
        print(f"slide {report.slideNumber} {report.name} {report.width:.2f} by {report.height:.2f} pt {report.state}")

    return 1 if any(report.state == CollapsedState for report in reports) else 0


def Main(arguments: list) -> int:
    if len(arguments) >= 4 and arguments[0] == "embed":
        verb = Embed
    elif len(arguments) == 2 and arguments[0] == "check":
        verb = Check
    else:
        print(Usage, file=sys.stderr)

        return 1

    try:
        return verb(arguments[1:])
    except (PowerPointError, OSError, ValueError) as error:
        print(error, file=sys.stderr)

        return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:]))

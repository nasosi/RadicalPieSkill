"""Command line over the PowerPoint pipeline.

`python -m Tools.PowerPoint embed <input.pptx> <output.pptx> <key>=<file.pie> ...` writes the deck with every
`{{pie:<key>}}` replaced by the equation in the named file and prints one line per embedded equation,
`key slide width height form` with the sizes in points, or the reason it failed on stderr with exit code 1.
The form is `shape` for a placeholder that was the whole text of its shape, `tab` for an inline gap held open
by a tab stop and `spaces` for one held open by a run of spaces. A gap that went to the next line because its
own had no room says `moved to the next line` on its own line, and one whose padding a punctuation mark beside
the placeholder took away says so there too, `no padding before ','`. A paragraph the run opened to make room
for a tall equation prints a line of its own after those, `opened slide <n>, the shape <name>, paragraph <n>:`
and what was set. What the run did to a text shape itself prints last, `shape slide <n>, the shape <name>:`
and what it did, which is turning autofit off and leaving the shape out of a group.

`python -m Tools.PowerPoint check <deck.pptx>` reads a finished deck with no COM and prints one line per
Radical Pie object, `slide <n> <name> <width> by <height> pt <state>`, where the state is `drawn`, `blank`
for an empty equation, whose picture is the blank one by right, or `collapsed`. One collapsed object exits 1.

`embed` validates every equation before PowerPoint starts and refuses the job with the validator's own
lines, because Radical Pie drops a structure it does not know instead of refusing the file. An input that is
not a PowerPoint package is one line naming the file, from the pipeline's own `CheckIsPowerPointPackage`,
which both verbs run before they read anything, and an output that is the input deck or one of the equation
files is one line before that. An output file that exists and is neither is overwritten, because a caller
reruns a build.

`Main` takes the name of the program that invoked it, because the usage line is a command the caller can
run: the front door scripts/PowerPoint.py passes its own path, and the module invocation below passes
itself.
"""

import sys
from pathlib import Path

from Tools.OutputPaths import SameFileRefusal
from Tools.PieFormat.Validator import RefusalMessage
from Tools.PowerPoint.Pptx import CheckDeck, CollapsedState, EmbedEquations, PowerPointError

ModuleProgram = "python -m Tools.PowerPoint"


def Usage(program: str) -> str:
    return (
        f"usage: {program} embed <input.pptx> <output.pptx> <key>=<file.pie> [<key>=<file.pie> ...]\n"
        f"       {program} check <deck.pptx>"
    )


def ReadEquationFiles(arguments: list) -> dict:
    """The `<key>=<file.pie>` pairs as a mapping of key to file name, each key given once."""

    files = {}

    for argument in arguments:
        key, separator, fileName = argument.partition("=")

        if not separator or not key:
            raise ValueError(f"{argument!r} is not a <key>=<file.pie> pair")

        if key in files:
            raise ValueError(f"the key {key!r} is given twice")

        files[key] = fileName

    return files


def Embed(arguments: list, program: str) -> int:
    files = ReadEquationFiles(arguments[2:])
    sameFile = SameFileRefusal(arguments[1:2], [arguments[0]] + list(files.values()))

    if sameFile:
        raise PowerPointError(sameFile)

    refusal = RefusalMessage(files.values())

    if refusal:
        raise PowerPointError(refusal)

    equations = {key: Path(fileName).read_text(encoding="utf-8") for key, fileName in files.items()}
    embedded = EmbedEquations(Path(arguments[0]), Path(arguments[1]), equations)

    for equation in embedded:
        line = f"{equation.key} {equation.slideNumber} {equation.width:g} {equation.height:g} {equation.form}"
        notes = [note for note in (equation.moved, equation.tight) if note]
        print(" ".join([line] + notes))

    for equation in embedded:
        if equation.opened:
            print(f"opened {equation.opened}")

    for equation in embedded:
        for note in equation.shapeNotes:
            print(f"shape {note}")

    return 0


def Check(arguments: list, program: str) -> int:
    reports = CheckDeck(Path(arguments[0]))

    for report in reports:
        print(f"slide {report.slideNumber} {report.name} {report.width:.2f} by {report.height:.2f} pt {report.state}")

    return 1 if any(report.state == CollapsedState for report in reports) else 0


def Main(arguments: list, program: str = ModuleProgram) -> int:
    if len(arguments) >= 4 and arguments[0] == "embed":
        verb = Embed
    elif len(arguments) == 2 and arguments[0] == "check":
        verb = Check
    else:
        print(Usage(program), file=sys.stderr)

        return 1

    try:
        return verb(arguments[1:], program)
    except (PowerPointError, OSError, ValueError) as error:
        print(error, file=sys.stderr)

        return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:]))

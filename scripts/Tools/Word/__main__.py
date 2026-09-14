"""Command line over the Word pipeline.

`python -m Tools.Word embed [--timeout <seconds>] <input.docx> <output.docx> <key>=<file.pie> ...` writes the
document with every `{{pie:<key>}}` replaced by the equation in the named file and prints one line per
embedded equation, `key kind number width height` with the sizes in points. The number is the one the
`SEQ equation` field holds, and `-` for an equation that is not numbered. `--timeout` bounds both passes that
start Word, defaulting to `EmbedEquations`'s own default of 120 seconds; a document with more objects than
that allows needs a larger one, and the error names which pass ran out and how many objects it had finished.

`python -m Tools.Word check <document.docx>` starts nothing: it reads the package and prints one line per
embedded object, `identity progId width height drawn-or-blank`, and a last line with the count of
`RadicalPie.Application.1` objects among them. It exits non-zero when an object is still the blank Word
caches before an activation draws it, or is of another class.

Either verb prints the reason it failed on stderr and exits 1.
"""

import sys
from pathlib import Path

from Tools.Word import Docx
from Tools.Word.Docx import CheckObjects, EmbedEquations, WordError

Usage = (
    "usage: python -m Tools.Word embed [--timeout <seconds>] <input.docx> <output.docx>"
    " <key>=<file.pie> [<key>=<file.pie> ...]\n"
    "       python -m Tools.Word check <document.docx>"
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
    timeoutSeconds = Docx.DefaultTimeoutSeconds

    if arguments[:1] == ["--timeout"]:
        if len(arguments) < 2:
            raise ValueError("--timeout needs a number of seconds")

        timeoutSeconds = float(arguments[1])
        arguments = arguments[2:]

    if len(arguments) < 3:
        raise ValueError(Usage)

    equations = ReadEquations(arguments[2:])
    embedded = EmbedEquations(Path(arguments[0]), Path(arguments[1]), equations, timeoutSeconds=timeoutSeconds)

    for equation in embedded:
        number = equation.number if equation.number is not None else "-"

        print(f"{equation.key} {equation.kind} {number} {equation.width:g} {equation.height:g}")

    return 0


def Check(arguments: list) -> int:
    if len(arguments) != 1:
        raise ValueError(Usage)

    records = CheckObjects(Path(arguments[0]))

    for record in records:
        status = "drawn" if record.drawn else "blank"

        print(f"{record.identity} {record.progId} {record.width:g} {record.height:g} {status}")

    ours = [record for record in records if record.progId == Docx.ObjectClass]

    print(f"{len(ours)} {Docx.ObjectClass} objects")

    return 0 if all(record.drawn and record.progId == Docx.ObjectClass for record in records) else 1


def Main(arguments: list) -> int:
    if not arguments or arguments[0] not in ("embed", "check"):
        print(Usage, file=sys.stderr)

        return 1

    try:
        return Embed(arguments[1:]) if arguments[0] == "embed" else Check(arguments[1:])
    except (WordError, OSError, ValueError) as error:
        print(error, file=sys.stderr)

        return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:]))

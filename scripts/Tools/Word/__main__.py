"""Command line over the Word pipeline.

`python -m Tools.Word embed [--timeout <seconds>] <input.docx> <output.docx> <key>=<file.pie> ...` writes the
document with every `{{pie:<key>}}` replaced by the equation in the named file and prints one line per
embedded equation, `key kind number width height` with the sizes in points. The number is the one the
`SEQ equation` field holds, `<chapter>.<n>` in a document whose `{{chapter}}` markers name its chapters, and
`-` for an equation that is not numbered. `--timeout` bounds both passes that
start Word; without it the run takes `Docx.TimeoutBudget` of the number of placeholders, which is a base plus
an allowance for each object. The error of a run that goes past it names which pass ran out and how many
objects it had finished.

`python -m Tools.Word check <document.docx>` starts nothing: it reads the package and prints one line per
embedded object, `identity progId width height drawn-or-blank`, and a last line with the count of
`RadicalPie.Application.1` objects among them. It exits non-zero when an object is still the blank Word
caches before an activation draws it, or is of another class.

Either verb prints the reason it failed on stderr and exits 1. `embed` validates every equation before Word
starts and refuses the job with the validator's own lines, because Radical Pie drops a structure it does not
know instead of refusing the file. An input that is not a Word package is one line naming the file, from the
pipeline's own `CheckIsWordPackage`, which both verbs run before they read anything, and an output that is the
input document or one of the equation files is one line before that. An output file that exists and is neither
is overwritten, because a caller reruns a build.

`Main` takes the name of the program that invoked it, because the usage line is a command the caller can run:
the front door scripts/Word.py passes its own path, and the module invocation below passes itself.
"""

import sys
from pathlib import Path

from Tools.OutputPaths import SameFileRefusal
from Tools.PieFormat.Validator import RefusalMessage
from Tools.Word import Docx
from Tools.Word.Docx import CheckObjects, EmbedEquations, WordError

ModuleProgram = "python -m Tools.Word"


def Usage(program: str) -> str:
    return (
        f"usage: {program} embed [--timeout <seconds>] <input.docx> <output.docx>"
        " <key>=<file.pie> [<key>=<file.pie> ...]\n"
        f"       {program} check <document.docx>"
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
    timeoutSeconds = None

    if arguments[:1] == ["--timeout"]:
        if len(arguments) < 2:
            raise ValueError("--timeout needs a number of seconds")

        timeoutSeconds = float(arguments[1])
        arguments = arguments[2:]

    if len(arguments) < 3:
        raise ValueError(Usage(program))

    files = ReadEquationFiles(arguments[2:])
    sameFile = SameFileRefusal(arguments[1:2], [arguments[0]] + list(files.values()))

    if sameFile:
        raise WordError(sameFile)

    refusal = RefusalMessage(files.values())

    if refusal:
        raise WordError(refusal)

    equations = {key: Path(fileName).read_text(encoding="utf-8") for key, fileName in files.items()}
    embedded = EmbedEquations(Path(arguments[0]), Path(arguments[1]), equations, timeoutSeconds=timeoutSeconds)

    for equation in embedded:
        number = equation.number if equation.number is not None else "-"

        print(f"{equation.key} {equation.kind} {number} {equation.width:g} {equation.height:g}")

    return 0


def Check(arguments: list, program: str) -> int:
    if len(arguments) != 1:
        raise ValueError(Usage(program))

    records = CheckObjects(Path(arguments[0]))

    for record in records:
        status = "drawn" if record.drawn else "blank"

        print(f"{record.identity} {record.progId} {record.width:g} {record.height:g} {status}")

    ours = [record for record in records if record.progId == Docx.ObjectClass]

    print(f"{len(ours)} {Docx.ObjectClass} objects")

    return 0 if all(record.drawn and record.progId == Docx.ObjectClass for record in records) else 1


def Main(arguments: list, program: str = ModuleProgram) -> int:
    if not arguments or arguments[0] not in ("embed", "check"):
        print(Usage(program), file=sys.stderr)

        return 1

    try:
        verb = Embed if arguments[0] == "embed" else Check

        return verb(arguments[1:], program)
    except (WordError, OSError, ValueError) as error:
        print(error, file=sys.stderr)

        return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:]))

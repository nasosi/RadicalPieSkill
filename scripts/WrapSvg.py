"""Moves an equation between a bare .pie file and the SVG comment carrier that Radical Pie reads.

Radical Pie and InkRadix exchange an equation as an SVG whose first comment holds the .pie text
verbatim. Radical Pie opens such a file, and on Save it replaces the placeholder with the rendered
paths and keeps the comment, so the carrier is how an agent hands an equation to the editor or to
Inkscape without launching anything.

    python WrapSvg.py <input.pie> <output.svg>    wrap the equation in the carrier
    python WrapSvg.py <input.svg> <output.pie>    take the equation back out

The carrier's width, height and viewBox describe an empty equation; Radical Pie overwrites all three
when it renders. Extraction is Tools/PieFormat's ExtractPieFromSvg, so it also reads the SVG that
Radical Pie has already rendered and the InkRadix element. Both directions write UTF-8 without a BOM
and Unix line endings, which is what Radical Pie writes.

An equation goes into the carrier only when the validator accepts it, so a wrap prints the validator's
own lines and writes nothing for a file that does not validate. The rule that matters most to this
script is the one about `-->`: the equation travels inside an XML comment, and a text that ends that
comment truncates the equation on the way back and turns the rest of it into live markup.
"""

import sys
from pathlib import Path

# ToolsPath sits beside this script and knows which of the two layouts this is, the repository or the
# published folder with the pipelines vendored under scripts/Tools. The script's own directory has to be on
# sys.path before it can be imported, which is where Python puts it for a script but not for an import.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ToolsPath import MissingPackageExit, PutToolsOnPath  # noqa: E402  the path has to be set first

PutToolsOnPath("PieFormat")

try:
    # The path has to be set before the import.
    from Tools.PieFormat.Validator import ExtractPieFromSvg, RefusalMessage  # noqa: E402
except ModuleNotFoundError as error:  # noqa: E402  a pipeline package the machine has not installed
    sys.exit(MissingPackageExit(error))


def Usage(program):
    return f"usage: {program} <input.pie> <output.svg> | {program} <input.svg> <output.pie>"


Carrier = (
    '<svg width="6pt" height="9pt" viewBox="0 -9 6 9" version="1.1" xmlns="http://www.w3.org/2000/svg">\n'
    "<desc>Radical Pie Equation</desc>\n"
    "<!--\n"
    "{}\n"
    "-->\n"
    "</svg>\n"
)


def WriteText(path, text):
    """UTF-8 without a BOM, with the line endings the text already carries.

    Path.write_text takes no newline argument before Python 3.10, and the default would turn every
    newline into CRLF on Windows.
    """

    with open(path, "w", encoding="utf-8", newline="") as stream:
        stream.write(text)


def Wrap(pieText):
    return Carrier.format(pieText.replace("\r\n", "\n").strip("\n"))


def Main(arguments, program="python WrapSvg.py"):
    if len(arguments) != 2:
        print(Usage(program), file=sys.stderr)
        return 2

    inputPath = Path(arguments[0])

    if inputPath.suffix.lower() == ".svg":
        equation = ExtractPieFromSvg(inputPath.read_text(encoding="utf-8"))

        if not equation:
            print("{}: this SVG carries no Radical Pie equation".format(inputPath), file=sys.stderr)
            return 1

        WriteText(arguments[1], equation)
    else:
        # The carrier is an XML comment around the equation, so only an equation the validator accepts
        # goes into one. The file is read after that check, because a file that is not UTF-8 is one of
        # the things the validator reports as a line of its own.
        refusal = RefusalMessage([inputPath])

        if refusal:
            print(refusal, file=sys.stderr)
            return 1

        WriteText(arguments[1], Wrap(inputPath.read_text(encoding="utf-8")))

    print(arguments[1])
    return 0


if __name__ == "__main__":
    # A .pie path can be Greek or mathematical, and the console codec refuses it (the guideline the
    # repository keeps); five of the six front doors did this already.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:], f"python {sys.argv[0]}"))

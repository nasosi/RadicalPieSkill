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
"""

import sys
from pathlib import Path

# Two layouts: inside the repository, Tools sits at parents[3]; packaged by Scripts/PackageSkill.py, it is
# vendored beside this script as scripts/Tools. The package name is Tools either way, so the import is one.
RepositoryRoot = Path(__file__).resolve().parents[3]
ScriptDir = Path(__file__).resolve().parent

sys.path.insert(0, str(RepositoryRoot if (RepositoryRoot / "Tools" / "PieFormat").is_dir() else ScriptDir))

from Tools.PieFormat.Validator import ExtractPieFromSvg  # noqa: E402  the path has to be set before the import

Usage = "usage: python WrapSvg.py <input.pie> <output.svg> | python WrapSvg.py <input.svg> <output.pie>"

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


def Main(arguments):
    if len(arguments) != 2:
        print(Usage, file=sys.stderr)
        return 2

    inputPath = Path(arguments[0])
    text = inputPath.read_text(encoding="utf-8")

    if inputPath.suffix.lower() == ".svg":
        equation = ExtractPieFromSvg(text)

        if not equation:
            print("{}: this SVG carries no Radical Pie equation".format(inputPath), file=sys.stderr)
            return 1

        WriteText(arguments[1], equation)
    else:
        WriteText(arguments[1], Wrap(text))

    print(arguments[1])
    return 0


if __name__ == "__main__":
    sys.exit(Main(sys.argv[1:]))

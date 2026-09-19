r"""Command line over the LaTeX pipeline.

`python -m Tools.Latex build <input.tex> <output directory> <key>=<file.pie> ...` exports one picture per
equation, writes `radicalpie.sty`, copies the document and compiles it with pdflatex, printing
`key width height shift` in points for each equation and then the path of each compiled PDF. `--engine
lualatex` compiles with lualatex as well, over the same pictures. The reason it failed goes to stderr with
exit code 1.

Every equation is validated before anything is started, and a key given twice is refused rather than
resolved to the last file: both are mistakes the build used to carry into a document.

An input that is one of the files the build writes into the output directory is refused before that, in one
line naming both. The build's own refusal of a `Main.tex` or a `radicalpie.sty` it did not write stands as it
was, and it is what protects the author's files of those names.

`Main` takes the name of the program that invoked it, because the usage line is a command the caller can
run: the front door scripts/Latex.py passes its own path, and the module invocation below passes itself.
"""

import sys
from pathlib import Path

from Tools.Latex.Build import BuildDocument, DocumentName, ImageDirectoryName, LatexError, StyleFileName
from Tools.OutputPaths import SameFileRefusal
from Tools.PieFormat.Validator import RefusalMessage
from Tools.Render.Svg import RenderError

ModuleProgram = "python -m Tools.Latex"

DefaultEngine = "pdflatex"


def Usage(program: str) -> str:
    return f"usage: {program} build <input.tex> <output directory> [--engine lualatex] <key>=<file.pie> ..."


def ReadPairs(pairs: list) -> dict:
    """The `<key>=<file.pie>` arguments as a mapping of key to file name, each key given once."""

    files = {}

    for pair in pairs:
        key, _, fileName = pair.partition("=")

        if key in files:
            raise LatexError(f"the key {key!r} is given twice, and one key names one equation")

        files[key] = fileName

    return files


def WrittenFiles(outputDir: str, files: dict) -> list:
    """The files the build writes into the output directory, which no input of the run may be.

    The two fixed names and one picture pair per equation. The engines' own PDFs and logs carry the fixed
    document name too, and a `.tex` or a `.pie` named like one of those is not a document this build reads.
    """

    directory = Path(outputDir)
    written = [directory / StyleFileName, directory / f"{DocumentName}.tex"]

    for key in files:
        written += [directory / ImageDirectoryName / f"{key}{suffix}" for suffix in (".pdf", ".svg")]

    return written


def Main(arguments: list, program: str = ModuleProgram) -> int:
    engines = [DefaultEngine]
    positional = []
    index = 0

    while index < len(arguments):
        if arguments[index] != "--engine":
            positional.append(arguments[index])
            index += 1
            continue

        if index + 1 == len(arguments):
            print(Usage(program), file=sys.stderr)

            return 1

        engines.append(arguments[index + 1])
        index += 2

    if len(positional) < 3 or positional[0] != "build" or not all("=" in pair for pair in positional[3:]):
        print(Usage(program), file=sys.stderr)

        return 1

    texPath, outputDir = positional[1:3]

    try:
        files = ReadPairs(positional[3:])
        sameFile = SameFileRefusal(WrittenFiles(outputDir, files), [texPath] + list(files.values()))

        if sameFile:
            print(sameFile, file=sys.stderr)

            return 1

        refusal = RefusalMessage(files.values())

        if refusal:
            print(refusal, file=sys.stderr)

            return 1

        equations = {key: Path(fileName).read_text(encoding="utf-8") for key, fileName in files.items()}
        result = BuildDocument(texPath, outputDir, equations, tuple(engines))
    except (LatexError, RenderError, OSError) as error:
        print(error, file=sys.stderr)

        return 1

    for equation in result.equations:
        print(f"{equation.key} {equation.width:g} {equation.height:g} {equation.shift:g}")

    for engine in engines:
        print(result.outputs[engine])

    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:]))

r"""Command line over the LaTeX pipeline.

`python -m Tools.Latex build <input.tex> <output directory> <key>=<file.pie> ...` exports one picture per
equation, writes `radicalpie.sty`, copies the document and compiles it with pdflatex, printing
`key width height shift` in points for each equation and then the path of each compiled PDF. `--engine
lualatex` compiles with lualatex as well, over the same pictures. The reason it failed goes to stderr with
exit code 1.
"""

import sys
from pathlib import Path

from Tools.Latex.Build import BuildDocument, LatexError
from Tools.Render.Svg import RenderError

Usage = "usage: python -m Tools.Latex build <input.tex> <output directory> [--engine lualatex] <key>=<file.pie> ..."

DefaultEngine = "pdflatex"


def Main(arguments: list) -> int:
    engines = [DefaultEngine]
    positional = []
    index = 0

    while index < len(arguments):
        if arguments[index] != "--engine":
            positional.append(arguments[index])
            index += 1
            continue

        if index + 1 == len(arguments):
            print(Usage, file=sys.stderr)

            return 1

        engines.append(arguments[index + 1])
        index += 2

    if len(positional) < 3 or positional[0] != "build" or not all("=" in pair for pair in positional[3:]):
        print(Usage, file=sys.stderr)

        return 1

    texPath, outputDir = positional[1:3]
    files = {}

    for pair in positional[3:]:
        key, _, fileName = pair.partition("=")
        files[key] = fileName

    try:
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

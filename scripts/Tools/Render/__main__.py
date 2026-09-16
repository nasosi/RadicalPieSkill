"""Command line over the render pipeline.

`python -m Tools.Render svg <input.pie> <output.svg>` writes the rendered SVG and prints one line,
`width height baselineShift` in points. `pdf` and `emf` write the file Radical Pie exports through its
Save a Copy dialog and print its size in bytes. Any of the three prints the reason it failed on stderr with
exit code 1.

The equation is validated before Radical Pie is started, and a violation is the validator's own line with
nothing launched: Radical Pie drops a structure it does not know instead of refusing the file, so an
equation with one typo in a structure name used to render as the empty equation and exit 0.

`Main` takes the name of the program that invoked it, because the usage line is a command the caller can
run: the front door scripts/Render.py passes its own path, and the module invocation below passes itself.
"""

import sys
from pathlib import Path

from Tools.PieFormat.Validator import RefusalMessage
from Tools.Render.Export import ExportEmf, ExportPdf
from Tools.Render.Svg import RenderError, RenderSvg

ModuleProgram = "python -m Tools.Render"

Exporters = {"pdf": ExportPdf, "emf": ExportEmf}


def Usage(program: str) -> str:
    return f"usage: {program} (svg|pdf|emf) <input.pie> <output>"


def Main(arguments: list, program: str = ModuleProgram) -> int:
    if len(arguments) != 3 or arguments[0] not in ("svg", *Exporters):
        print(Usage(program), file=sys.stderr)

        return 1

    command, inputPath, outputPath = arguments

    try:
        refusal = RefusalMessage([inputPath])

        if refusal:
            print(refusal, file=sys.stderr)

            return 1

        pieText = Path(inputPath).read_text(encoding="utf-8")

        if command == "svg":
            info = RenderSvg(pieText, Path(outputPath))
            written = f"{info.width:g} {info.height:g} {info.baselineShift:g}"
        else:
            written = str(Exporters[command](pieText, Path(outputPath)).stat().st_size)
    except (RenderError, OSError) as error:
        print(error, file=sys.stderr)

        return 1

    print(written)

    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:]))

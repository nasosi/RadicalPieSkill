"""Command line over the render pipeline.

`python -m Tools.Render svg <input.pie> <output.svg>` writes the rendered SVG and prints one line,
`width height baselineShift` in points. `png` writes that SVG converted to a PNG by Inkscape
(`Tools.Render.Png`) and prints `width height` in pixels; a machine without Inkscape gets one line naming what
to install, with nothing launched. `pdf` and `emf` write the file Radical Pie exports through its Save a Copy
dialog and print its size in bytes. Any of the four prints the reason it failed on stderr with exit code 1, and
leaves no output file: an output file an earlier run wrote is removed before the render starts, so a caller that
renders to one name again and misses the exit code has no older picture to judge.

An output Radical Pie drew with a font slot in Times, because the design names a font it cannot find, is
written and its line printed all the same, and each such slot adds one line on stderr, `warning: F <slot>
<data list>: Radical Pie drew it in Times; the closest installed names are ...`, with exit code 3
(`Tools.PieFormat.Fonts.FallbackExitCode`), so the caller has the file and cannot read the run as a success
(ADR-0015).

The equation is validated before Radical Pie is started, and a violation is the validator's own line with
nothing launched: Radical Pie drops a structure it does not know instead of refusing the file, so an
equation with one typo in a structure name used to render as the empty equation and exit 0.

An output that is the input is refused before the equation is even read, because `svg Eq.pie Eq.pie` wrote
the rendering over the equation. That refusal and the validator's leave an existing output file as it was; past
them, an output file that exists and is not the input is removed, and a run that succeeds writes it again.

`Main` takes the name of the program that invoked it, because the usage line is a command the caller can
run: the front door scripts/Render.py passes its own path, and the module invocation below passes itself.
"""

import sys
from pathlib import Path

from Tools.OutputPaths import SameFileRefusal
from Tools.PieFormat.Fonts import FallbackExitCode
from Tools.PieFormat.Validator import RefusalMessage
from Tools.Render.Export import ExportEmf, ExportPdf
from Tools.Render.Png import RenderPng
from Tools.Render.Svg import RenderError, RenderSvg

ModuleProgram = "python -m Tools.Render"

Exporters = {"pdf": ExportPdf, "emf": ExportEmf}


def Usage(program: str) -> str:
    return f"usage: {program} (svg|png|pdf|emf) <input.pie> <output>"


def Main(arguments: list, program: str = ModuleProgram) -> int:
    if len(arguments) != 3 or arguments[0] not in ("svg", "png", *Exporters):
        print(Usage(program), file=sys.stderr)

        return 1

    command, inputPath, outputPath = arguments
    sameFile = SameFileRefusal([outputPath], [inputPath])

    if sameFile:
        print(sameFile, file=sys.stderr)

        return 1

    try:
        refusal = RefusalMessage([inputPath])

        if refusal:
            print(refusal, file=sys.stderr)

            return 1

        pieText = Path(inputPath).read_text(encoding="utf-8")
        Path(outputPath).unlink(missing_ok=True)

        if command == "svg":
            result = RenderSvg(pieText, Path(outputPath))
            written = f"{result.width:g} {result.height:g} {result.baselineShift:g}"
        elif command == "png":
            result = RenderPng(pieText, Path(outputPath))
            written = f"{result.width} {result.height}"
        else:
            result = Exporters[command](pieText, Path(outputPath))
            written = str(result.path.stat().st_size)
    except (RenderError, OSError) as error:
        print(error, file=sys.stderr)

        return 1

    print(written)

    for warning in result.fontWarnings:
        print(f"warning: {warning}", file=sys.stderr)

    return FallbackExitCode if result.fontWarnings else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:]))

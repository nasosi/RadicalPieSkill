"""Command line over the render pipeline.

`python -m Tools.Render svg <input.pie> <output.svg>` writes the rendered SVG and prints one line,
`width height baselineShift` in points. `pdf` and `emf` write the file Radical Pie exports through its
Save a Copy dialog and print its size in bytes. Any of the three prints the reason it failed on stderr with
exit code 1.
"""

import sys
from pathlib import Path

from Tools.Render.Export import ExportEmf, ExportPdf
from Tools.Render.Svg import RenderError, RenderSvg

Usage = "usage: python -m Tools.Render (svg|pdf|emf) <input.pie> <output>"

Exporters = {"pdf": ExportPdf, "emf": ExportEmf}


def Main(arguments: list) -> int:
    if len(arguments) != 3 or arguments[0] not in ("svg", *Exporters):
        print(Usage, file=sys.stderr)

        return 1

    command, inputPath, outputPath = arguments

    try:
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

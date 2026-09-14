r"""Build a LaTeX document whose equations are Radical Pie renderings included at the text baseline.

The author writes ordinary LaTeX and puts `\pie{<key>}` where an equation goes, inline in a sentence or
alone inside `equation`, `align` or `\[ \]`, so LaTeX itself numbers the display equations and `\label`,
`\ref` and `\eqref` work as they always do. The only thing the document loads is `\usepackage{radicalpie}`,
and that package is written by this build, into the output directory beside the pictures it names.

Each equation goes in twice from Radical Pie, because the two things the document needs come out of two
different writers. `Tools.Render.Export.ExportPdf` writes the picture, one page whose `/MediaBox` is the
equation's own box. `Tools.Render.Svg.RenderSvg` writes the SVG whose view box gives the baseline shift the
Clipboard documentation defines, the sum of the minimum y and the height. The shift is what `\raisebox`
lowers the picture by: Radical Pie puts the equation baseline at y = 0 and the box hangs below it, so an
included picture arrives sitting on the baseline by its lowest point and has to come down to meet the text.

Four facts measured against MiKTeX 25.4 on 2026-09-11 shape the rest. `\includegraphics` takes a Radical Pie
PDF as it stands, under pdflatex and under lualatex alike: it is PDF 1.4 with a `/MediaBox` and no
`/CropBox`, so no bounding box has to be supplied and no `\pdfminorversion` has to be raised. A `/MediaBox`
with a negative lower left, which every equation with a descender has, is placed by its lower left corner
like any other, so the shift alone puts it right. A key holding an underscore survives both the file name in
`\includegraphics` and the `\csname` lookup. Each engine gets its own job name, because both write their
`.pdf`, `.aux` and `.log` into the same directory and the second would otherwise overwrite the first.

Every process this module starts it ends: Radical Pie is owned by the render pipeline, and each engine run
is a `subprocess.run` with a timeout, `-interaction=nonstopmode` and `-halt-on-error`, so no run can stop on
a console prompt and none outlives its call. A failed compilation is reported as the log's first error line.
"""

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from string import Template

from Tools.Render.Export import ExportPdf
from Tools.Render.Svg import RenderSvg

PlaceholderPattern = re.compile(r"\\pie\{([^{}]*)\}")

# A key names a PDF file, an `\includegraphics` argument and the tail of a `\csname`, so it is a letter
# followed by letters, digits and underscores.
KeyPattern = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")

# `\usepackage{radicalpie}` fixes the lower-case file name.
StyleFileName = "radicalpie.sty"

ImageDirectoryName = "RadicalPie"
DocumentName = "Main"

# The first run writes the `.aux` the equation numbers and the `\eqref`s are read back from.
CompileRuns = 2

StyleTemplate = Template(
    r"""\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{radicalpie}[2026/09/11 Radical Pie equations as included pictures]
\RequirePackage{graphicx}

% Radical Pie draws an equation with its baseline at y = 0 and lets the page box hang below it, so an
% included picture sits on the surrounding baseline by its lowest point. `\pieshift` carries the downward
% correction of one equation, in points: the sum of the minimum y and the height of its SVG view box.
\newcommand{\pieshift}[2]{\expandafter\gdef\csname RadicalPieShift@#1\endcsname{#2}}

\newcommand{\pie}[1]{%
  \@ifundefined{RadicalPieShift@#1}%
    {\PackageError{radicalpie}{No Radical Pie equation is named '#1'}%
      {The build writes one \string\pieshift\space line here per equation it was given.}}%
    {\raisebox{-\csname RadicalPieShift@#1\endcsname pt}{\includegraphics{$images/#1.pdf}}}%
}

"""
)


class LatexError(RuntimeError):
    """The document was not produced. The message names what was observed, in the pipeline's own terms."""


@dataclass(frozen=True)
class Placeholder:
    r"""One `\pie{...}` as the document holds it, with the line it was found on."""

    lineNumber: int
    key: str
    text: str


@dataclass(frozen=True)
class Equation:
    """One exported equation: the picture the document includes, and the geometry it was measured at."""

    key: str
    width: float
    height: float
    shift: float
    pdfPath: Path
    svgPath: Path


@dataclass(frozen=True)
class BuildResult:
    """What the build wrote: the equations in document order, the package, the document, a PDF per engine."""

    equations: list
    stylePath: Path
    documentPath: Path
    outputs: dict


def BuildDocument(
    texPath,
    outputDir,
    equations: dict,
    engines=("pdflatex",),
    timeoutSeconds: float = 180,
) -> BuildResult:
    r"""Build `texPath` into `outputDir` with every `\pie{<key>}` replaced by the equation `equations[key]`.

    `equations` maps a key to the `.pie` text of that equation, as the Word pipeline's does; the command
    line reads the files. The text is exported as it stands, design block included.

    Both paths may be relative to the caller's working directory. Every placeholder needs an equation and
    every equation needs a placeholder, both checked along with the grammar of the keys before Radical Pie
    is started, so a document that cannot be built launches nothing.

    A key that appears more than once is exported once and included as often as the document names it.
    """

    # `Path.resolve` returns a relative path unchanged on Windows under Python 3.9 when the file is not
    # there yet, which the output directory need not be, so both paths go through `os.path.abspath`.
    texPath = Path(os.path.abspath(texPath))
    outputDir = Path(os.path.abspath(outputDir))

    placeholders = ReadPlaceholders(texPath.read_text(encoding="utf-8"))
    CheckPlaceholders(placeholders, equations)

    if not engines:
        raise LatexError("no engine was named, and the document is compiled by at least one")

    imageDirectory = outputDir / ImageDirectoryName
    imageDirectory.mkdir(parents=True, exist_ok=True)

    exported = [ExportEquation(key, equations[key], imageDirectory) for key in Keys(placeholders)]

    stylePath = outputDir / StyleFileName
    stylePath.write_text(StyleText(exported), encoding="utf-8")

    documentPath = outputDir / f"{DocumentName}.tex"
    shutil.copyfile(texPath, documentPath)

    outputs = {engine: Compile(outputDir, engine, timeoutSeconds) for engine in engines}

    return BuildResult(exported, stylePath, documentPath, outputs)


def ReadPlaceholders(texText: str) -> list:
    r"""Every `\pie{<key>}` of the document, in document order.

    The scan reads lines and does not parse LaTeX, so a `\pie` behind a comment character counts like any
    other and needs an equation of its own.
    """

    placeholders = []

    for number, line in enumerate(texText.splitlines(), start=1):
        for match in PlaceholderPattern.finditer(line):
            placeholders.append(Placeholder(number, match.group(1), match.group(0)))

    return placeholders


def CheckPlaceholders(placeholders: list, equations: dict) -> None:
    """Everything that can be known before Radical Pie starts, each failure naming its offender."""

    for placeholder in placeholders:
        CheckKey(placeholder.key, placeholder.text, placeholder.lineNumber)

    placed = {placeholder.key for placeholder in placeholders}
    unknown = sorted(placed - set(equations))
    unused = sorted(set(equations) - placed)

    if unknown:
        raise LatexError(f"the document holds placeholders with no equation: {', '.join(unknown)}")

    if unused:
        raise LatexError(f"the document holds no placeholder for the equations: {', '.join(unused)}")


def CheckKey(key: str, text: str, lineNumber: int) -> None:
    """A key names a file and a control sequence, so it is a letter followed by letters, digits and underscores."""

    if not KeyPattern.match(key):
        raise LatexError(
            f"{text} on line {lineNumber} names the key {key!r},"
            " which is not a letter followed by letters, digits and underscores"
        )


def Keys(placeholders: list) -> list:
    """The keys in first-appearance order, each once, because one export serves every placeholder naming it."""

    keys = []

    for placeholder in placeholders:
        if placeholder.key not in keys:
            keys.append(placeholder.key)

    return keys


def ExportEquation(key: str, pieText: str, imageDirectory: Path) -> Equation:
    """The picture and the measurement of one equation, two Radical Pie runs, one after the other."""

    pdfPath = ExportPdf(pieText, imageDirectory / f"{key}.pdf")
    svgPath = imageDirectory / f"{key}.svg"
    info = RenderSvg(pieText, svgPath)

    return Equation(key, info.width, info.height, info.baselineShift, pdfPath, svgPath)


def StyleText(equations: list) -> str:
    r"""The `radicalpie.sty` the document loads: the `\pie` macro and one `\pieshift` line per equation."""

    shifts = "".join(f"\\pieshift{{{equation.key}}}{{{equation.shift:g}}}\n" for equation in equations)

    return StyleTemplate.substitute(images=ImageDirectoryName) + shifts


def Compile(outputDir: Path, engine: str, timeoutSeconds: float) -> Path:
    """Run `engine` over the copied document from inside `outputDir` and return the PDF it wrote."""

    jobName = f"{DocumentName}-{engine}"
    pdfPath = outputDir / f"{jobName}.pdf"
    logPath = outputDir / f"{jobName}.log"

    for _ in range(CompileRuns):
        Run(engine, jobName, outputDir, timeoutSeconds, logPath)

    # A document that typesets nothing at all leaves the engine happy and writes no PDF.
    if not pdfPath.exists():
        raise LatexError(f"{engine} wrote no {pdfPath.name}: {FirstError(logPath)}")

    return pdfPath


def Run(engine: str, jobName: str, outputDir: Path, timeoutSeconds: float, logPath: Path) -> None:
    """One engine run. It cannot stop on a prompt, and it does not outlive this call."""

    command = [
        engine,
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-jobname={jobName}",
        f"{DocumentName}.tex",
    ]

    try:
        completed = subprocess.run(command, cwd=str(outputDir), capture_output=True, timeout=timeoutSeconds)
    except FileNotFoundError:
        raise LatexError(f"{engine} is not on the PATH") from None
    except subprocess.TimeoutExpired:
        raise LatexError(f"{engine} did not finish within {timeoutSeconds:g}s and was killed") from None

    if completed.returncode != 0:
        raise LatexError(f"{engine} failed: {FirstError(logPath)}")


def FirstError(logPath: Path) -> str:
    """The log's first error line, which is the line TeX starts with an exclamation mark."""

    try:
        log = logPath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return f"{logPath.name} was not written"

    for line in log.splitlines():
        if line.startswith("!"):
            return line.strip()

    return f"{logPath.name} holds no error line"

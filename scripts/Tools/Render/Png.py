"""Render a `.pie` equation to a PNG, through the SVG Radical Pie draws and Inkscape's command line.

The PNG is the form a calling agent looks at: an image comes back to it as a picture, where an SVG comes back as
text. Radical Pie writes no raster image, so `RenderPng` renders the SVG with `Tools.Render.Svg.RenderSvg`, with
its validation-free contract, its retries and its font warnings, into a temporary directory, and converts that
SVG with `inkscape.exe <svg> --export-type=png --export-filename=<png> --export-background=white
--export-dpi=300`. The SVG and the PNG Inkscape writes stay in the temporary directory, which is removed
afterward as far as a virus scanner holding a file in it allows (`Tools.Render.Svg.WorkDirectory`); the PNG is
copied to the caller's path only when both steps succeeded.

The resolution is fixed at 300 dpi: Corpus/Pie/RatioNewComputerModern.pie, 22.9 by 23 points, comes out 95 by 96
pixels and reads clearly as an image, where the 60-pixel-wide image of a one-line equation at 96 dpi did not
(measured 2026-10-22).

Inkscape is an optional dependency of the skill. `InkscapeExecutable` is its default install path, and an
installation elsewhere is found as `inkscape.exe` in an absolute directory of the PATH; the executable itself and
not the `inkscape.com` console wrapper beside it, which starts `inkscape.exe` as a child that the termination
below would not reach. The search reads the PATH itself because `shutil.which` on Python 3.9 for Windows looks in
the current directory first, which would run an `inkscape.exe` lying in the caller's folder. A machine with
neither gets one RenderError naming what to install, raised before Radical Pie is launched.

Three measured facts of Inkscape 1.4.3 shape the success test (2026-10-22). It exits 0 on an input it cannot
open and writes nothing. It prints CRITICAL lines on stderr for a broken user extension and exits 0 with a good
PNG. And a cold start takes about 8 s, a warm one about 2.4 s. So success is the exit code 0 together with an
output file that holds the PNG signature and the whole `IHDR` chunk header the size is read from, stderr is read
only to name a failure, and the conversion gets `ConvertTimeoutSeconds`.

The Inkscape process is registered in `Tools.Processes` and so put in the job object that ends with this
interpreter; it is killed on a timeout and on any exception that leaves it running, and released from the
registry once it has been seen to exit. One still there `ExitGraceSeconds` after the kill stays registered and
raises RenderError, its message led by the timeout that caused the kill.
"""

import os
import struct
import subprocess
from dataclasses import dataclass
from pathlib import Path

from Tools import Processes
from Tools.Render.Svg import ExitGraceSeconds, RenderError, RenderSvg, WorkDirectory

InkscapeExecutable = Path(r"C:\Program Files\Inkscape\bin\inkscape.exe")

PngDpi = 300
ConvertTimeoutSeconds = 60

PngSignature = b"\x89PNG\r\n\x1a\n"

# The signature, the chunk length, `IHDR`, and the width and height as two big-endian 32-bit integers.
PngSizeEnd = 24


@dataclass(frozen=True)
class PngInfo:
    """The size of a rendered PNG in pixels, and the font warnings of the SVG it was converted from."""

    width: int
    height: int
    fontWarnings: tuple = ()


def RenderPng(pieText: str, outputPath: Path) -> PngInfo:
    """Render `pieText` to a PNG at `outputPath`, returning its size and the render's font warnings.

    The caller has validated the text, as for `RenderSvg`. Inkscape is looked for first, so a machine without it
    launches nothing. An SVG drawn with a slot in Times is converted all the same and its warnings carried on, as
    the SVG form writes its file and warns (ADR-0015).
    """

    outputPath = Path(outputPath)
    inkscape = FindInkscape()

    with WorkDirectory("RadicalPiePng") as workDirectory:
        svgPath = workDirectory / "Equation.svg"
        pngPath = workDirectory / "Equation.png"
        svgInfo = RenderSvg(pieText, svgPath)
        raw = ConvertToPng(inkscape, svgPath, pngPath, ConvertTimeoutSeconds)

    width, height = ReadPngSize(raw)

    outputPath.parent.mkdir(parents=True, exist_ok=True)
    outputPath.write_bytes(raw)

    return PngInfo(width, height, svgInfo.fontWarnings)


def FindInkscape() -> Path:
    """The Inkscape executable: the default install path, else `inkscape.exe` in an absolute PATH directory.

    A relative entry, `.` among them, names a folder that depends on where the caller stands, so it is skipped.
    """

    if InkscapeExecutable.is_file():
        return InkscapeExecutable

    for entry in os.environ.get("PATH", "").split(os.pathsep):
        directory = Path(entry.strip().strip('"'))

        if entry.strip() and directory.is_absolute() and (directory / "inkscape.exe").is_file():
            return directory / "inkscape.exe"

    raise RenderError(
        f"Inkscape is not installed at {InkscapeExecutable} or on the PATH; install Inkscape 1.x for png,"
        " or render svg, pdf or emf, which need no Inkscape"
    )


def ConvertToPng(inkscape: Path, svgPath: Path, pngPath: Path, timeoutSeconds: float) -> bytes:
    """Convert `svgPath` to `pngPath` with Inkscape and return the PNG's bytes. No process after.

    The exit code and the file decide the outcome; the last line of stderr goes into the error of a failure.
    """

    command = [
        str(inkscape),
        str(svgPath),
        "--export-type=png",
        f"--export-filename={pngPath}",
        "--export-background=white",
        f"--export-dpi={PngDpi}",
    ]

    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    Processes.Register(process.pid)
    reason = "the conversion was interrupted"

    try:
        _, errorBytes = process.communicate(timeout=timeoutSeconds)
    except subprocess.TimeoutExpired:
        reason = f"Inkscape did not convert the SVG to PNG within {timeoutSeconds:g}s"

        raise RenderError(reason) from None
    finally:
        if process.poll() is None:
            process.kill()

            try:
                process.wait(timeout=ExitGraceSeconds)
            except subprocess.TimeoutExpired:
                raise RenderError(
                    f"{reason}; Inkscape (pid {process.pid}) did not exit within {ExitGraceSeconds:g}s of being killed"
                ) from None

        Processes.Release(process.pid)

    errorLines = errorBytes.decode("utf-8", errors="replace").strip().splitlines()
    lastLine = f": {errorLines[-1].strip()}" if errorLines else ""

    if process.returncode != 0:
        raise RenderError(f"Inkscape exited with code {process.returncode} converting the SVG to PNG{lastLine}")

    raw = pngPath.read_bytes() if pngPath.is_file() else b""

    if not raw:
        raise RenderError(f"Inkscape exited 0 and wrote no PNG{lastLine}")

    if len(raw) < PngSizeEnd or not raw.startswith(PngSignature) or raw[12:16] != b"IHDR":
        raise RenderError(f"Inkscape exited 0 and wrote a file that is not a PNG{lastLine}")

    return raw


def ReadPngSize(raw: bytes) -> tuple:
    """Width and height in pixels, from the `IHDR` chunk that follows the signature."""

    return struct.unpack(">II", raw[16:PngSizeEnd])

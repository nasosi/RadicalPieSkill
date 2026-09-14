"""Render a `.pie` equation to the SVG Radical Pie itself draws.

Radical Pie 1.15 has no export switch and no scripting interface, so the only route to its renderer is the
file it opens. An SVG whose comment carries the `.pie` text is a document Radical Pie reads back; posting
File > Save (`WM_COMMAND` 260, the menu identifier recorded in Docs/ARCHITECTURE.md) makes it rewrite that
file in place with the rendered `<path>` elements and the real `width`, `height` and `viewBox`. This module
drives that loop over a temporary file, owns the process it launches and terminates it on every path; the
launch records the pid in the registry of `Tools.Processes` and the termination drops it once it has seen the
process go, which is what the live tests are checked against.

Three measured facts shape the waiting. The window exists about 30 ms after launch, before Radical Pie has
read the file, and a Save posted then belongs to an untitled document and opens the Save Equation common
file dialog instead of writing anything. The title becomes `<file name> - Radical Pie` when the document is
in, which is the signal to post Save. For another 30 ms after that the equation is still not laid out, and a
Save in that gap writes a complete but degenerate SVG, `width="0.0pt" height="0.0pt"
viewBox="0.0 0.0 0.0 0.0"` with one zero-length path, so the presence of a `<path>` does not prove the render
happened. Positive width and height do not prove it either: the geometry of `StubTemplate` itself, `6pt` by
`9pt` with `viewBox="0 -9 6 9"`, is positive, and under parallel load Radical Pie occasionally rewrites the
file with that same placeholder geometry, reformatted enough that it is not the stub's exact bytes, before it
has laid the equation out (about one render in forty, backlog 2026-09-13). The completeness check therefore
also compares the saved geometry against the stub's own, parsed from the `stub` bytes each attempt is given,
and keeps waiting on a match. The smallest real render, an empty equation, is 5.5 by 8 points with no path at
all, clear of the stub's 6 by 9. Save is reposted until the file on disk is a complete SVG with positive
width and height that is not the stub's geometry, which takes about 0.2 seconds from launch.

The launch keeps the operator's keyboard, which is the fourth measured fact (2026-09-11). `subprocess.Popen`
with no `STARTUPINFO` makes the window the foreground one, `SW_SHOWNOACTIVATE` leaves it on screen without the
focus, and `SW_SHOWMINNOACTIVE`, which is what this uses, starts it minimised and unfocused. Radical Pie lays
out, saves and exports from a minimised window and takes the same time doing it: 0.42 to 0.53 s for a render
and about 2 s for an export, the same as from a visible one. Minimised is the state kept because the gate runs
the render tests in parallel, and forty visible windows are forty windows over what the operator is reading.

A design that names a font the machine has not converted yet puts up one more window, "Font Import", while
the conversion runs. It is progress and not a prompt, and it is the one window here that is left alone:
closing it, which is what a modal dialog earns, cancels the import and fails the render (measured
2026-09-13).

An equation Radical Pie cannot lay out crashes it rather than refusing it, and the crash is a rendering
outcome the callers read: both the Save the loop posts and the close that ends the process are posted through
handlers that tolerate a window destroyed underneath them, so what the caller sees is a RenderError naming
the exit code.

A crash also happens to an equation that renders perfectly well on the next run. Under the parallel gate,
forty workers and an agent rendering beside them, about one render in a hundred exited with 3221225477, the
access violation, before it ever saved (measured 2026-09-12). So a failed attempt is made again, once, with a
fresh launch: `Terminate` returns only when the first process is gone, a settle follows it, and a second
failure raises one RenderError carrying both attempts' messages. A crash the equation itself causes, which is
what the anchor probes of `Scripts/AnchorAtlas.py` read, therefore costs two launches instead of one.
"""

import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import pywintypes
import win32con
import win32gui
import win32process

from Tools import Processes

Executable = Path(r"C:\Program Files\RadicalPie\RadicalPie.exe")

WindowClass = "RadicalPie"
SaveCommand = 260

# The document Radical Pie reads back: its own SVG shape with the `.pie` text in the comment and a
# placeholder geometry it replaces. The text goes in as given; Radical Pie normalises it on the way out.
StubTemplate = (
    '<svg width="6pt" height="9pt" viewBox="0 -9 6 9" version="1.1" xmlns="http://www.w3.org/2000/svg">'
    "<desc>Radical Pie Equation</desc><!--\n{0}\n--></svg>"
)

# Every process of this application owns these two invisible top-level windows; they are not dialogs.
InputMethodClasses = frozenset({"IME", "MSCTFIME UI"})

# The window a design puts up while it imports a font the machine has not converted yet. It is the progress
# window the Font Manager page describes and not a prompt: it closes itself when the `.slug` under
# %localappdata%\RadicalPie is written, and the render finishes normally after it. Measured 2026-09-13: a
# design naming Cambria, Consolas or Times New Roman raised it on this machine, and closing it, which is
# what every other window of the process earns, cancelled the import and failed the render.
FontImportTitle = "Font Import"

PollSeconds = 0.02
RepostSaveSeconds = 0.25
LayoutSettleSeconds = 0.25
ExitGraceSeconds = 5.0

# What a launch of Radical Pie gets: the attempt and one retry of it. The settle is the pause between the
# first process going and the second starting, which is the load the retry is there for.
RenderAttempts = 2
RetrySettleSeconds = 1.0

SvgTagPattern = re.compile(r"<svg\b[^>]*>")


class RenderError(RuntimeError):
    """Radical Pie did not produce a rendered file. The message names what was observed."""


@dataclass(frozen=True)
class SvgInfo:
    """The geometry of a rendered equation, in points, as the SVG element states it."""

    width: float
    height: float
    viewBox: tuple

    @property
    def baselineShift(self) -> float:
        """Points to move the image down so it sits on the surrounding text baseline.

        The Clipboard documentation defines the shift as the viewBox minimum y plus the viewBox height,
        because Radical Pie puts the equation baseline at y = 0 and grows the box upwards from there.
        """

        return self.viewBox[1] + self.viewBox[3]


def RenderSvg(pieText: str, outputPath: Path, timeoutSeconds: float = 30) -> SvgInfo:
    """Render `pieText` and write the SVG to `outputPath`, returning its geometry.

    The text is used as it stands: a missing `// Radical Pie Equation` header is not added, because the
    comment carries the equation and Radical Pie drops the header line from what it writes back.
    """

    outputPath = Path(outputPath)
    stub = StubTemplate.format(pieText).encode("utf-8")

    with tempfile.TemporaryDirectory(prefix="RadicalPieRender") as workDirectory:
        workPath = Path(workDirectory) / "Equation.svg"
        rendered = DriveRadicalPie(workPath, stub, timeoutSeconds)

    outputPath.parent.mkdir(parents=True, exist_ok=True)
    outputPath.write_bytes(rendered)

    return ReadSvgInfo(rendered)


def DriveRadicalPie(filePath: Path, stub: bytes, timeoutSeconds: float) -> bytes:
    """Render `filePath`, retrying the whole attempt once. No process outlives this.

    The retry is a fresh launch and never a second command to a process that is on its way out: the attempt
    it follows has already terminated its own, and the settle stands between the two. Each attempt gets the
    whole of `timeoutSeconds`, so a render that fails twice takes twice as long to say so.
    """

    failures = []

    for attempt in range(RenderAttempts):
        if attempt:
            time.sleep(RetrySettleSeconds)

        try:
            return AttemptRender(filePath, stub, timeoutSeconds)
        except RenderError as error:
            failures.append(str(error))

    raise RenderError(f"Radical Pie rendered nothing in {RenderAttempts} attempts: {Attempts(failures)}")


def AttemptRender(filePath: Path, stub: bytes, timeoutSeconds: float) -> bytes:
    """One launch: open `filePath` in Radical Pie, save it, return the rendered bytes. The process is gone after.

    The stub goes on disk here rather than at the caller, because an attempt that crashed after its first
    Save left a degenerate SVG in the file and the attempt that follows starts from the document it expects.
    """

    filePath.write_bytes(stub)

    deadline = time.monotonic() + timeoutSeconds
    process = Launch(filePath)

    try:
        window = AwaitDocument(process, f"{filePath.name} - Radical Pie", deadline, timeoutSeconds)

        return AwaitRender(process, window, filePath, stub, deadline, timeoutSeconds)
    finally:
        Terminate(process)


def Attempts(failures: list) -> str:
    """Every failed attempt's message, numbered, for the error that reports them together."""

    return "; ".join(f"attempt {number}: {message}" for number, message in enumerate(failures, 1))


def Launch(filePath: Path) -> subprocess.Popen:
    """Start Radical Pie on `filePath` minimised and unfocused, and register the process.

    `SW_SHOWMINNOACTIVE` is what keeps the window off the operator's screen and keyboard; the equation lays
    out in it all the same, and the window the operator was typing in stays the foreground one.

    A machine without Radical Pie is the ordinary case for the published skill folder, so the missing
    executable is named here rather than left to Popen's `[WinError 2]`.
    """

    if not Executable.is_file():
        raise RenderError(f"Radical Pie is not installed at {Executable}")

    startup = subprocess.STARTUPINFO()
    startup.dwFlags = subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = win32con.SW_SHOWMINNOACTIVE

    process = subprocess.Popen([str(Executable), str(filePath)], startupinfo=startup)
    Processes.Register(process.pid)

    return process


def AwaitDocument(process: subprocess.Popen, documentTitle: str, deadline: float, timeoutSeconds: float) -> int:
    """The main window, once its title names the file, which is when the document has been read."""

    lastTitle = None

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RenderError(f"Radical Pie exited with code {process.returncode} before showing a window")

        windows = TopLevelWindows(process.pid)
        RaiseOnDialog(windows)

        for handle, className, title in windows:
            if className != WindowClass:
                continue

            lastTitle = title

            if title == documentTitle:
                return handle

        time.sleep(PollSeconds)

    raise RenderError(
        f"Radical Pie did not open the document within {timeoutSeconds:g}s"
        f" (window title {lastTitle!r}, expected {documentTitle!r})"
    )


def AwaitRender(
    process: subprocess.Popen,
    window: int,
    filePath: Path,
    stub: bytes,
    deadline: float,
    timeoutSeconds: float,
) -> bytes:
    # A Save that lands while the first layout is still running crashes Radical Pie 1.15 with an access
    # violation on equations that fetch stretched or built-in glyphs (measured 2026-09-10, ARCHITECTURE.md:
    # one crash in three at 20 ms after the title, none from 100 ms on). The settle keeps the first Save
    # clear of that window; the reposts that follow were never seen to crash.
    time.sleep(LayoutSettleSeconds)

    lastPost = 0.0
    observed = "the file was never rewritten"

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RenderError(f"Radical Pie exited with code {process.returncode} before saving the render")

        RaiseOnDialog(TopLevelWindows(process.pid))

        if time.monotonic() - lastPost >= RepostSaveSeconds:
            PostCommand(window, SaveCommand)
            lastPost = time.monotonic()

        rendered = ReadWhenComplete(filePath, stub)

        if rendered is not None:
            info = ReadSvgInfo(rendered)

            # `raw == stub` in ReadWhenComplete only catches the file coming back byte-identical; a Save
            # posted before layout can also write the stub's geometry back reformatted, which still measures
            # positive and must be rejected the same way.
            if info.width > 0 and info.height > 0 and info != ReadSvgInfo(stub):
                return rendered

            observed = f"the saved SVG measures {info.width}pt by {info.height}pt, so the equation was not laid out"

        time.sleep(PollSeconds)

    raise RenderError(f"Radical Pie wrote no rendered SVG within {timeoutSeconds:g}s: {observed}")


def ReadWhenComplete(filePath: Path, stub: bytes):
    """The file's bytes once Radical Pie has replaced the stub with a whole SVG, else None.

    The closing tag is the completeness test, because a read can land in the middle of Radical Pie's write.
    """

    try:
        raw = filePath.read_bytes()
    except OSError:
        return None

    if raw == stub or not raw.rstrip().endswith(b"</svg>"):
        return None

    return raw


def ReadSvgInfo(raw: bytes) -> SvgInfo:
    """Parse the SVG element's geometry.

    Read with a regular expression rather than an XML parser: the comment holds the `.pie` text verbatim,
    and a `.pie` text containing a double hyphen is not a legal XML comment.
    """

    tag = SvgTagPattern.search(raw.decode("utf-8"))

    if tag is None:
        raise RenderError("the rendered file has no <svg> element")

    element = tag.group(0)
    viewBox = ReadNumbers(element, "viewBox")

    if len(viewBox) != 4:
        raise RenderError(f"the rendered <svg> has a viewBox of {len(viewBox)} numbers, expected 4")

    width = ReadNumbers(element, "width")
    height = ReadNumbers(element, "height")

    if len(width) != 1 or len(height) != 1:
        raise RenderError(f"the rendered <svg> has no single width and height: {element}")

    return SvgInfo(width[0], height[0], tuple(viewBox))


def ReadNumbers(element: str, name: str) -> list:
    """The point values of an SVG attribute, the `pt` unit stripped."""

    attribute = re.search(rf'\b{name}="([^"]*)"', element)

    if attribute is None:
        raise RenderError(f"the rendered <svg> has no {name} attribute: {element}")

    try:
        return [float(field[:-2] if field.endswith("pt") else field) for field in attribute.group(1).split()]
    except ValueError:
        raise RenderError(f"the rendered <svg> has an unreadable {name}: {attribute.group(1)!r}") from None


def TopLevelWindows(pid: int) -> list:
    """The visible top-level windows of one process, as (handle, class, title), input method windows excluded."""

    windows = []

    def Visit(handle, _):
        if win32process.GetWindowThreadProcessId(handle)[1] == pid and win32gui.IsWindowVisible(handle):
            className = win32gui.GetClassName(handle)

            if className not in InputMethodClasses:
                windows.append((handle, className, win32gui.GetWindowText(handle)))

        return True

    win32gui.EnumWindows(Visit, None)

    return windows


def PostCommand(window: int, command: int) -> None:
    """Post a menu command, tolerating a window that has gone already.

    An equation that asks for an anchor the executable does not have crashes it with an access violation
    while the layout runs, and the window goes with it, which can happen between the loop's check of the
    process and the Save it posts next; `PostMessage` then answers 1400. Swallowing that lets the next pass
    read the exit code and raise the RenderError that names it, which is what the anchor probes of
    `Scripts/AnchorAtlas.py` rely on to tell a missing anchor index from a measurement.
    """

    try:
        win32gui.PostMessage(window, win32con.WM_COMMAND, command, 0)
    except pywintypes.error:
        pass


def PostClose(window: int) -> None:
    """Ask a window to close, tolerating one that has gone already.

    A window can be destroyed between the moment it is listed and the moment the message is posted: Radical
    Pie tears its main window down as it leaves, which is what it does as soon as the dialog over an
    unreadable file is dismissed, and `PostMessage` answers 1400 for the handle. Under the parallel gate run
    that gap was wide enough to raise out of the `finally` that ends the process and to replace the
    RenderError the render had already raised.
    """

    try:
        win32gui.PostMessage(window, win32con.WM_CLOSE, 0, 0)
    except pywintypes.error:
        pass


def RaiseOnDialog(windows: list) -> None:
    """Turn a modal dialog into a RenderError carrying its text.

    Unparseable input raises "This file cannot be opened because it does not contain valid Radical Pie
    equation data." in a `#32770` message box that blocks the application until it is dismissed.

    The Font Import window is the one exception: it is progress and not a prompt, so it is left alone and
    the poll that follows finds it gone.
    """

    for handle, className, title in windows:
        if className == WindowClass or title == FontImportTitle:
            continue

        message = DialogText(handle)
        PostClose(handle)

        raise RenderError(f"Radical Pie raised a {className} dialog titled {title!r}: {message}")


def DialogText(handle: int) -> str:
    """The dialog's message, which lives in its `Static` children."""

    texts = []

    def Visit(child, _):
        if win32gui.GetClassName(child) == "Static":
            texts.append(win32gui.GetWindowText(child))

        return True

    win32gui.EnumChildWindows(handle, Visit, None)

    return " ".join(text.strip() for text in texts if text.strip())


def Terminate(process: subprocess.Popen) -> None:
    """Close the window, then kill what is left. The process is gone when this returns."""

    if process.poll() is None:
        for handle, className, _ in TopLevelWindows(process.pid):
            if className == WindowClass:
                PostClose(handle)

    graceDeadline = time.monotonic() + ExitGraceSeconds

    while time.monotonic() < graceDeadline:
        if process.poll() is not None:
            Processes.Release(process.pid)

            return

        time.sleep(PollSeconds)

    process.kill()
    process.wait(timeout=ExitGraceSeconds)
    Processes.Release(process.pid)

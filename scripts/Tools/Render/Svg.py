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
focus, and `SW_SHOWMINNOACTIVE`, which is what this uses, starts it minimized and unfocused. Radical Pie lays
out, saves and exports from a minimized window and takes the same time doing it: 0.42 to 0.53 s for a render
and about 2 s for an export, the same as from a visible one. Minimized is the state kept because the gate runs
the render tests in parallel, and forty visible windows are forty windows over what the operator is reading.

Radical Pie 1.16 puts up one more window, "Font Import", for two things: the progress of a font conversion
and the report of a font it cannot resolve, which it then draws in Times (`Tools.Render.FontImport` tells the
two apart). The loop posts no Save until an import has finished, and closes the report before it saves. The
render is written either way, and a render that comes back with a named slot written as `i16{2}`, Times, or
that raised the report, carries one warning line per such slot in `SvgInfo.fontWarnings`, naming the slot,
what the design wrote and the closest installed names (`Tools.PieFormat.Fonts.FontWarnings`), so no caller is
handed an equation drawn in Times without being told (ADR-0015). The termination lets the `slugfont.exe` of the
process finish its slug first, even when the process itself has already gone, and closes a report still up
before the document window.

Each launch first waits for every `slugfont.exe` on the machine, once and for at most the caller's timeout,
and a launch that starts with one still running carries a line saying so into its warnings or its error. A
render whose launch imported a font the design names is rendered again from a fresh launch, because the output
of that first launch is not to be trusted (`Tools.Render.FontImport`). `TrustedLaunch` and `LaunchWarnings`
hold that sequence for this module and for `Tools.Render.Export` alike: the output is written to the caller's
path once the run's result is known, a repeat launch that fails leaves the first output with a warning, a slot
whose font is still not imported after the last launch gets a warning of its own, and a run that fails with a
slug still empty leads its error with the font check's line for that slug.

An equation Radical Pie cannot lay out crashes it rather than refusing it, and the crash is a rendering
outcome the callers read: both the Save the loop posts and the close that ends the process are posted through
handlers that tolerate a window destroyed underneath them, so what the caller sees is a RenderError naming
the exit code.

Nothing here validates the equation, and `RenderSvg` says why: the anchor atlas reads the crash of an equation
the validator refuses. Every other entry point of the pipelines validates before it launches anything.

A crash also happens to an equation that renders perfectly well on the next run. Under the parallel gate,
forty workers and an agent rendering beside them, about one render in a hundred exited with 3221225477, the
access violation, before it ever saved (measured 2026-09-12). So a failed attempt is made again, once, with a
fresh launch: `Terminate` returns only when the first process is gone, a settle follows it, and a second
failure raises one RenderError carrying both attempts' messages. A caller that reads a crash as its
measurement asks for one attempt instead, which the anchor probes of `Scripts/AnchorAtlas.py` do.

Two ends of a run raise nothing a caller cannot read. The temporary directory is removed as far as it can be
(`WorkDirectory`), because a virus scanner holding a file in it made the removal raise PermissionError after a
good render. A process still there after its kill raises RenderError rather than the wait's TimeoutExpired, and
stays registered.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path

import pywintypes
import win32con
import win32gui
import win32process

from Tools import Processes
from Tools.PieFormat import Fonts
from Tools.Render.FontImport import (
    AwaitingReports,
    AwaitSlugFont,
    AwaitSlugFonts,
    FontImportTitle,
    FontImportWatch,
    FontImportWindows,
    ImportedSince,
    Importing,
    SlotsAwaitingImport,
)

Executable = Fonts.RadicalPieDirectory / "RadicalPie.exe"

WindowClass = "RadicalPie"
SaveCommand = 260

# The document Radical Pie reads back: its own SVG shape with the `.pie` text in the comment and a
# placeholder geometry it replaces. The text goes in as given; Radical Pie normalizes it on the way out.
StubTemplate = (
    '<svg width="6pt" height="9pt" viewBox="0 -9 6 9" version="1.1" xmlns="http://www.w3.org/2000/svg">'
    "<desc>Radical Pie Equation</desc><!--\n{0}\n--></svg>"
)

# Every process of this application owns these two invisible top-level windows; they are not dialogs.
InputMethodClasses = frozenset({"IME", "MSCTFIME UI"})

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
    """The geometry of a rendered equation, in points, as the SVG element states it.

    `fontWarnings` holds one line per font slot Radical Pie drew in Times or may have, and one per thing about
    the launches that may have drawn a slot in Times; it is empty when every slot drew in its own font
    (`LaunchWarnings`).
    """

    width: float
    height: float
    viewBox: tuple
    fontWarnings: tuple = ()

    @property
    def baselineShift(self) -> float:
        """Points to move the image down so it sits on the surrounding text baseline.

        The Clipboard documentation defines the shift as the viewBox minimum y plus the viewBox height,
        because Radical Pie puts the equation baseline at y = 0 and grows the box upward from there.
        """

        return self.viewBox[1] + self.viewBox[3]


@dataclass(frozen=True)
class Launched:
    """One launch's output, from the render loop or the export, and what is known about the launch.

    `reported` says the watch closed the Font Import report, `awaiting` holds the slots of the design whose font
    had no slug when the launch started (`FontImport.SlotsAwaitingImport`), and `notes` the warning lines about
    the launches themselves.
    """

    output: bytes
    reported: bool = False
    awaiting: frozenset = frozenset()
    notes: tuple = ()


def RenderSvg(pieText: str, outputPath: Path, timeoutSeconds: float = 30, attempts: int = RenderAttempts) -> SvgInfo:
    """Render `pieText` and write the SVG to `outputPath`, returning its geometry.

    The text is used as it stands: a missing `// Radical Pie Equation` header is not added, because the
    comment carries the equation and Radical Pie drops the header line from what it writes back. It is not
    validated either, and this is the one entry point of the pipelines that does not validate, because one of
    its callers needs an equation the validator refuses to reach the executable. `Scripts/AnchorAtlas.py`
    measures where each anchor of each structure is by rendering one anchor index at a time until one crashes
    Radical Pie, and an index past the last anchor of a type is exactly what the validator refuses (46 of the
    atlas's probe equations, measured 2026-09-19), so a validating render would hand the atlas the validator's
    message where it reads the crash.

    So a caller that hands text to this function has validated it: the command line does, and so does every
    pipeline's library entry point.

    A font the design names and Radical Pie cannot resolve is drawn in Times and the SVG is written all the
    same; the returned SvgInfo carries a warning line per such slot, read from the written-back design's
    `i16{2}` for a slot that named another font, or from the Font Import report the render loop closed
    (ADR-0015). Neither is retried. The write-back is read whether or not the report was seen, because the
    report rises 0.06 to 0.2 s after the document title (2026-10-08).

    `attempts` is how many launches a render that fails gets. The atlas is the caller that asks for one: it
    renders about forty-five equations a run that it expects to crash the executable, and the retry doubled the
    launches for every one of them.

    A design naming a font with no slug yet is rendered a second time, with the same `attempts`, once the launch
    that rendered it has imported it, and the second render is the one returned (`TrustedLaunch`). The SVG is
    written to `outputPath` once, after the last launch.
    """

    outputPath = Path(outputPath)

    with WorkDirectory("RadicalPieRender") as workDirectory:
        workPath = workDirectory / "Equation.svg"
        launched = TrustedLaunch(pieText, lambda: DriveRadicalPie(workPath, pieText, timeoutSeconds, attempts))

    warnings = LaunchWarnings(pieText, launched, launched.output.decode("utf-8"))

    outputPath.parent.mkdir(parents=True, exist_ok=True)
    outputPath.write_bytes(launched.output)

    return replace(ReadSvgInfo(launched.output), fontWarnings=warnings)


@contextmanager
def WorkDirectory(prefix: str):
    """A fresh temporary directory, removed afterward as far as it can be.

    A virus scanner that still holds a file in it makes the removal raise PermissionError, which turned a
    finished render into exit 1 and dropped its output, so nothing the removal raises reaches the caller and a
    directory that resists it is left in the temporary folder. The PNG form and the export use it too.
    """

    path = Path(tempfile.mkdtemp(prefix=prefix))

    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def TrustedLaunch(pieText: str, launch) -> Launched:
    """What `launch`, one pipeline's launch with its retry, returns, taken again when that launch imported a font.

    A launch that imported a font the design names is not trusted for its output (`FontImport.ImportedSince`),
    so it is followed by one more, which starts with the slug in place and reads for itself which slots still
    await their import. A repeat that fails leaves the first output, with a line naming the failure. A first
    launch that fails raises its error, led by the font check's line for each slug still empty after the waits,
    which crashes Radical Pie and names the file to delete.
    """

    try:
        first = launch()
    except RenderError as error:
        damaged = [Fonts.Describe(report) for report in AwaitingReports(pieText) if report.state == Fonts.DamagedSlug]

        if not damaged:
            raise

        raise RenderError("; ".join(damaged + [str(error)])) from None

    if not ImportedSince(pieText, first.awaiting):
        return first

    try:
        return launch()
    except RenderError as error:
        note = (
            "the output comes from the launch that imported a font of the design, which may draw it in Times,"
            f" because the launch repeated with the font in place failed: {error}"
        )

        return replace(first, notes=first.notes + (note,))


def LaunchWarnings(pieText: str, launched: Launched, writtenText: str) -> tuple:
    """The warning lines of a pipeline's output: the font lines, then the launches' own.

    `writtenText` is the design as the output carries it (`Fonts.FontWarnings`). The slots read here, after the
    last launch, are the ones whose font is still not imported, and each gets a line unless the write-back
    already names it.
    """

    return Fonts.FontWarnings(pieText, writtenText, launched.reported, SlotsAwaitingImport(pieText)) + launched.notes


def DriveRadicalPie(filePath: Path, pieText: str, timeoutSeconds: float, attempts: int = RenderAttempts) -> Launched:
    """Render `pieText` through `filePath` in at most `attempts` launches, returning the first that succeeds.

    No process outlives this. The retry is a fresh launch and never a second command to a process that is on
    its way out: the attempt it follows has already terminated its own, and the settle stands between the two.
    Each attempt gets the whole of `timeoutSeconds`, so a render that fails twice takes twice as long to say
    so. The Font Import report is no failure: the attempt closes it and completes.
    """

    failures = []

    for attempt in range(attempts):
        if attempt:
            time.sleep(RetrySettleSeconds)

        try:
            return AttemptRender(filePath, pieText, timeoutSeconds)
        except RenderError as error:
            failures.append(str(error))

    raise RenderError(f"Radical Pie rendered nothing in {attempts} attempts: {Attempts(failures)}")


def AttemptRender(filePath: Path, pieText: str, timeoutSeconds: float) -> Launched:
    """One launch: open `filePath` holding `pieText`, save it, and return what it wrote. No process after.

    The stub goes on disk here rather than at the caller, because an attempt that crashed after its first
    Save left a degenerate SVG in the file and the attempt that follows starts from the document it expects.
    A `slugfont.exe` still writing a slug, this pipeline's own from the attempt before or anyone else's, is
    waited out before the launch, for at most `timeoutSeconds`, and the launch's own timeout starts after it.
    The slots awaiting their import are read after that wait, because a slug is empty while it is built, and
    the watch awaits an import when there is one (`FontImport.FontImportWatch`).
    """

    stub = StubTemplate.format(pieText).encode("utf-8")
    filePath.write_bytes(stub)
    note = AwaitSlugFonts(timeoutSeconds)
    awaiting = SlotsAwaitingImport(pieText)

    deadline = time.monotonic() + timeoutSeconds

    try:
        process = Launch(filePath)

        try:
            window = AwaitDocument(process, f"{filePath.name} - Radical Pie", deadline, timeoutSeconds)
            rendered, reported = AwaitRender(process, window, filePath, stub, deadline, timeoutSeconds, bool(awaiting))
        finally:
            Terminate(process)
    except RenderError as error:
        if not note:
            raise

        raise RenderError(f"{error}; {note}") from None

    return Launched(rendered, reported, awaiting, (note,) if note else ())


def Attempts(failures: list) -> str:
    """Every failed attempt's message, numbered, for the error that reports them together."""

    return "; ".join(f"attempt {number}: {message}" for number, message in enumerate(failures, 1))


def Launch(filePath: Path) -> subprocess.Popen:
    """Start Radical Pie on `filePath` minimized and unfocused, and register the process.

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
    awaitImport: bool = False,
) -> tuple:
    # A Save that lands while the first layout is still running crashes Radical Pie 1.15 with an access
    # violation on equations that fetch stretched or built-in glyphs (measured 2026-09-10, ARCHITECTURE.md:
    # one crash in three at 20 ms after the title, none from 100 ms on). The settle keeps the first Save
    # clear of that window; the reposts that follow were never seen to crash. The watch then holds every Save
    # while a font import runs, and closes the report, which the returned flag records; told to await an
    # import, it holds the first Save until one has been seen.
    watch = FontImportWatch(process.pid, awaitImport)
    time.sleep(LayoutSettleSeconds)

    lastPost = 0.0
    observed = "the file was never rewritten"

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RenderError(f"Radical Pie exited with code {process.returncode} before saving the render")

        windows = TopLevelWindows(process.pid)
        RaiseOnDialog(windows)

        if not watch.Ready(windows):
            if watch.state == Importing:
                observed = "a font import was still running"

            time.sleep(PollSeconds)
            continue

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
                return rendered, watch.reported

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

    The Font Import window is the one exception: it is progress or the unresolved-font report, which the
    render loop's FontImportWatch tells apart and answers.
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
    """Close the window, then kill what is left. The process is gone when this returns.

    A process still there `ExitGraceSeconds` after the kill raises RenderError and stays in the registry of
    `Tools.Processes`, where the leak check finds it. The message leads with the error the caller's `finally`
    is carrying, when there is one, because the error raised here takes its place.

    A `slugfont.exe` the process started finishes its slug first, also when the process has already exited,
    since an orphaned one keeps writing; and a Font Import report is closed before the document window, which
    it keeps disabled; closing the report is what the probe of 2026-10-08 measured to enable the document window
    again within 30 ms.
    """

    AwaitSlugFont(process.pid)

    if process.poll() is None:
        windows = TopLevelWindows(process.pid)

        for handle in FontImportWindows(windows):
            PostClose(handle)

        for handle, className, _ in windows:
            if className == WindowClass:
                PostClose(handle)

    graceDeadline = time.monotonic() + ExitGraceSeconds

    while time.monotonic() < graceDeadline:
        if process.poll() is not None:
            Processes.Release(process.pid)

            return

        time.sleep(PollSeconds)

    # Read before the kill: inside the `except` below, the exception being handled is the wait's own.
    carried = sys.exc_info()[1]
    process.kill()

    try:
        process.wait(timeout=ExitGraceSeconds)
    except subprocess.TimeoutExpired:
        lead = f"{carried}; " if carried else ""

        raise RenderError(
            f"{lead}Radical Pie (pid {process.pid}) did not exit within {ExitGraceSeconds:g}s of being killed"
        ) from None

    Processes.Release(process.pid)

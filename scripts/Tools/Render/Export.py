"""Export a `.pie` equation to the PDF and EMF Radical Pie itself writes.

Radical Pie 1.15 has no export switch, so the only route to its PDF and EMF writers is File > Save a Copy
(`WM_COMMAND` 262, the menu identifier recorded in Docs/ARCHITECTURE.md), which opens the Windows 11 common
item dialog "Save Equation Copy". This module opens the equation, drives that dialog from outside the
process, owns the process it launches and terminates it on every path. It reuses the render loop's launch,
document wait, window listing and termination from `Tools.Render.Svg`, and raises the same `RenderError`.

Four measured facts shape the dialog work (2026-09-11, this machine, Radical Pie 1.15).

`WM_SETTEXT` on the file-name `Edit` (id 1001) changes what the box shows and what `WM_GETTEXT` reads back,
and the dialog ignores it: pressing Save then wrote the document's own name and raised the "Confirm Save As"
overwrite prompt for it. The dialog tracks the name through the edit control's change notifications, so the
name is typed with posted `WM_CHAR` messages, which produce them. UI Automation is no help here: the managed
client reports both the edit and the Save button as `ControlType.Pane` with no patterns at all.

The name is typed in double quotes. Unquoted, the dialog appends the extension of the selected filter, which
starts on `Radical Pie Equation (*.pie)` and cannot be changed from outside any more than the name can, and
"Export.pdf" was saved as "Export.pdf.pie". Quoted, the typed extension stands, and Radical Pie picks the
format from it while the filter still reads `*.pie`.

The Save button is pressed with a posted `BM_CLICK`. A `WM_COMMAND` with `BN_CLICKED` and id 1 posted to the
dialog closes it without saving anything, and a sent `BM_CLICK` blocks the caller inside the dialog's modal
loop, which is the vendor fact ARCHITECTURE.md records.

Radical Pie writes the file after the dialog closes, taking about 1.4 s for a PDF and 0.3 s for an EMF, so
the export waits for a whole file rather than for the dialog to go: a PDF that ends in `%%EOF`, an EMF whose
`EMR_HEADER` byte count equals its size on disk.

The export goes to a fresh name in a temporary directory and is moved to `outputPath` afterwards. That keeps
the "Confirm Save As" prompt, which no export path answers, out of the run, and it keeps the characters the
tooling has to type inside the temporary directory's ASCII path.

Under the parallel gate, forty workers and an agent rendering beside them, the export failed about once in a
hundred runs and passed on the rerun (measured 2026-09-12): "Radical Pie exited with code 1 before the Save
Equation Copy dialog", and once the file name was typed into a dialog whose Radical Pie had already exited,
which ended in a zero-size PDF. So the whole attempt is made again, once, with a fresh launch of its own; the
attempt before it has terminated its process, and `Terminate` returns only when that process is gone. Two
guards go with the retry: the file name is typed only into a dialog that still belongs to a live process, and
an export that reaches the caller's path with nothing in it is a failed attempt rather than an output.

The equation is validated before the launch, which is what an entry point of a pipeline owes a caller that
hands it text; the render loop is the exception, because the anchor atlas measures Radical Pie's crashes
through it.

The dialog takes the foreground for about 0.2 s and nothing here can stop it. The window Radical Pie is
launched into is minimised and unfocused, but the dialog is created afterwards by Radical Pie itself, which
has the right to activate it. Two ways of handing the foreground back were measured on 2026-09-11 and neither
is used: `SetForegroundWindow` on the window that had it, with and without an `AttachThreadInput` to the thread
that owns the foreground, returned false on every attempt and left the foreground on no window at all, and
minimising the dialog the moment it appears does not deactivate it. The dialog needs no focus for its work,
because the name is typed and the Save pressed with posted messages.
"""

import ctypes
import shutil
import subprocess
import tempfile
import time
from ctypes import wintypes
from pathlib import Path

import win32con
import win32gui

from Tools.PieFormat.Validator import FirstViolation
from Tools.Render.Svg import (
    Attempts,
    AwaitDocument,
    DialogText,
    Launch,
    LayoutSettleSeconds,
    PollSeconds,
    PostClose,
    RenderError,
    RetrySettleSeconds,
    Terminate,
    TopLevelWindows,
)

user32 = ctypes.WinDLL("user32", use_last_error=True)

SaveACopyCommand = 262

# What an export gets: the attempt and one retry of it, each with its own launch and its own temporary
# directory. The pause between them is the render loop's, for the same load.
ExportAttempts = 2

DialogTitle = "Save Equation Copy"
FileNameControlId = 1001
SaveButtonId = 1

WM_GETTEXT = 0x000D
EM_SETSEL = 0x00B1
BM_CLICK = 0x00F5
Backspace = 0x08
SMTO_ABORTIFHUNG = 0x0002


def ExportPdf(pieText: str, outputPath, timeoutSeconds: float = 30) -> Path:
    """Export `pieText` as PDF to `outputPath` and return it."""

    return Export(pieText, outputPath, ".pdf", timeoutSeconds)


def ExportEmf(pieText: str, outputPath, timeoutSeconds: float = 30) -> Path:
    """Export `pieText` as an enhanced metafile to `outputPath` and return it."""

    return Export(pieText, outputPath, ".emf", timeoutSeconds)


def Export(pieText: str, outputPath, extension: str, timeoutSeconds: float) -> Path:
    """Open `pieText` in Radical Pie and save a copy of it in the format `extension` names.

    The equation is validated here, before anything is launched, and the refusal names the output file and the
    first violation: Radical Pie drops a structure it does not know instead of refusing the file, so a caller
    that came in through `ExportPdf` or `ExportEmf` with text of its own used to be handed a PDF of the empty
    equation. `Tools.Render.Svg.RenderSvg` is the one entry point that does not validate, for the reason its
    own doc comment gives.

    The text is otherwise used as it stands: a missing `// Radical Pie Equation` header is not added, because
    Radical Pie's own parser does not require it. A failed attempt is made again once, from a fresh launch, and
    a second failure raises one error carrying both attempts' messages. Each attempt gets the whole of
    `timeoutSeconds`, so an export that fails twice takes twice as long to say so.
    """

    outputPath = Path(outputPath)
    violation = FirstViolation(pieText)

    if violation:
        raise RenderError(f"the equation for {outputPath} does not validate, so nothing was started: {violation}")

    failures = []

    for attempt in range(ExportAttempts):
        if attempt:
            time.sleep(RetrySettleSeconds)

        try:
            return AttemptExport(pieText, outputPath, extension, timeoutSeconds)
        except RenderError as error:
            failures.append(str(error))

    raise RenderError(f"Radical Pie exported nothing in {ExportAttempts} attempts: {Attempts(failures)}")


def AttemptExport(pieText: str, outputPath: Path, extension: str, timeoutSeconds: float) -> Path:
    """One launch, one Save a Copy, one move to `outputPath`. The process is gone when this returns.

    The export goes to a fresh temporary directory of this attempt's own, so a retry never reads the file a
    failed attempt left behind. The size of what arrives at `outputPath` is checked because a run of
    2026-09-12 handed the caller a zero-size PDF.
    """

    with tempfile.TemporaryDirectory(prefix="RadicalPieExport") as workDirectory:
        sourcePath = Path(workDirectory) / "Equation.pie"
        sourcePath.write_bytes(pieText.encode("utf-8"))

        exportPath = Path(workDirectory) / f"Export{extension}"
        DriveRadicalPie(sourcePath, exportPath, extension, timeoutSeconds)

        outputPath.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(exportPath), str(outputPath))

    if outputPath.stat().st_size == 0:
        raise RenderError(f"the exported {extension[1:].upper()} at {outputPath} is zero bytes")

    return outputPath


def DriveRadicalPie(sourcePath: Path, exportPath: Path, extension: str, timeoutSeconds: float) -> None:
    """Open `sourcePath`, save a copy to `exportPath`. The process never outlives this."""

    deadline = time.monotonic() + timeoutSeconds
    process = Launch(sourcePath)

    try:
        window = AwaitDocument(process, f"{sourcePath.name} - Radical Pie", deadline, timeoutSeconds)

        # A command that lands while the first layout is still running crashes Radical Pie 1.15 with an
        # access violation (ARCHITECTURE.md, the render loop's settle). Save a Copy waits the same way.
        time.sleep(LayoutSettleSeconds)

        win32gui.PostMessage(window, win32con.WM_COMMAND, SaveACopyCommand, 0)

        dialog = AwaitDialog(process, window, deadline, timeoutSeconds)
        edit = FindFileNameBox(dialog)

        CheckDialogIsLive(process, dialog)
        TypeFileName(edit, f'"{exportPath}"')
        AwaitTypedName(process, window, edit, f'"{exportPath}"', deadline, timeoutSeconds)

        win32gui.PostMessage(win32gui.GetDlgItem(dialog, SaveButtonId), BM_CLICK, 0, 0)

        AwaitExport(process, window, exportPath, extension, deadline, timeoutSeconds)
    finally:
        Terminate(process)


def AwaitDialog(process: subprocess.Popen, window: int, deadline: float, timeoutSeconds: float) -> int:
    """The Save a Copy dialog, once the posted menu command has opened it."""

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RenderError(f"Radical Pie exited with code {process.returncode} before the {DialogTitle} dialog")

        for handle, _, title in TopLevelWindows(process.pid):
            if title == DialogTitle:
                return handle

        RaiseOnStrayWindow(process, window)
        time.sleep(PollSeconds)

    raise RenderError(f"Radical Pie did not open the {DialogTitle} dialog within {timeoutSeconds:g}s")


def CheckDialogIsLive(process: subprocess.Popen, dialog: int) -> None:
    """Refuse to type into a dialog whose Radical Pie has gone.

    The dialog is found and its file-name box located in two separate passes, and under load of 2026-09-12
    the process left between them: the name was typed into a destroyed window, where a posted `WM_CHAR`
    reports nothing wrong, and the export ran out its timeout with a zero-size file. The window is looked for
    again among the process's own top-level windows, because a handle outlives the window that carried it.
    """

    if process.poll() is not None:
        raise RenderError(f"Radical Pie exited with code {process.returncode} before the file name was typed")

    if dialog not in {handle for handle, _, _ in TopLevelWindows(process.pid)}:
        raise RenderError(f"the {DialogTitle} dialog was gone before the file name was typed")


def FindFileNameBox(dialog: int) -> int:
    """The dialog's file-name `Edit`, which sits under `DirectUIHWND > FloatNotifySink > ComboBox`."""

    found = []

    def Visit(child, _):
        if win32gui.GetClassName(child) == "Edit" and win32gui.GetDlgCtrlID(child) == FileNameControlId:
            found.append(child)

        return True

    win32gui.EnumChildWindows(dialog, Visit, None)

    if not found:
        raise RenderError(f"the {DialogTitle} dialog has no file-name Edit with id {FileNameControlId}")

    return found[0]


def TypeFileName(edit: int, name: str) -> None:
    """Replace what the file-name box holds by typing, one posted `WM_CHAR` per character."""

    win32gui.PostMessage(edit, EM_SETSEL, 0, -1)
    win32gui.PostMessage(edit, win32con.WM_CHAR, Backspace, 1)

    for character in name:
        win32gui.PostMessage(edit, win32con.WM_CHAR, ord(character), 1)


def AwaitTypedName(
    process: subprocess.Popen,
    window: int,
    edit: int,
    name: str,
    deadline: float,
    timeoutSeconds: float,
) -> None:
    """Wait until the file-name box holds the whole name, because the characters are posted, not sent."""

    typed = ""

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RenderError(f"Radical Pie exited with code {process.returncode} while the name was typed")

        typed = ControlText(edit)

        if typed == name:
            return

        RaiseOnStrayWindow(process, window)
        time.sleep(PollSeconds)

    raise RenderError(f"the file name was still {typed!r} after {timeoutSeconds:g}s, expected {name!r}")


def AwaitExport(
    process: subprocess.Popen,
    window: int,
    exportPath: Path,
    extension: str,
    deadline: float,
    timeoutSeconds: float,
) -> None:
    """Wait for a whole exported file. Radical Pie writes it after the dialog has closed."""

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RenderError(f"Radical Pie exited with code {process.returncode} before writing the export")

        RaiseOnStrayWindow(process, window)

        try:
            raw = exportPath.read_bytes()
        except OSError:
            raw = b""

        if IsComplete(raw, extension):
            return

        time.sleep(PollSeconds)

    raise RenderError(f"Radical Pie wrote no whole {extension[1:].upper()} within {timeoutSeconds:g}s")


def IsComplete(raw: bytes, extension: str) -> bool:
    """True when the file on disk is a whole export, not a write in progress.

    A PDF is whole at its `%%EOF` trailer. An EMF is whole when the `nBytes` field of its `EMR_HEADER`,
    four bytes at offset 48, equals the size on disk.
    """

    if extension == ".pdf":
        return raw.startswith(b"%PDF") and raw.rstrip().endswith(b"%%EOF")

    return len(raw) >= 52 and raw[40:44] == b" EMF" and int.from_bytes(raw[48:52], "little") == len(raw)


def RaiseOnStrayWindow(process: subprocess.Popen, window: int) -> None:
    """Turn any window that is neither the document nor the Save a Copy dialog into a RenderError.

    The one seen in practice is "Confirm Save As", the overwrite prompt, which the temporary export name
    keeps away; an unreadable equation raises its own message box before the document window ever appears,
    where the render loop's own guard catches it.
    """

    for handle, className, title in TopLevelWindows(process.pid):
        if handle == window or title == DialogTitle:
            continue

        message = DialogText(handle)
        PostClose(handle)

        raise RenderError(f"Radical Pie raised a {className} dialog titled {title!r}: {message}")


def ControlText(handle: int) -> str:
    """The text of a control in another process, which `GetWindowText` does not read."""

    buffer = ctypes.create_unicode_buffer(1024)
    result = wintypes.LPARAM()

    user32.SendMessageTimeoutW(
        wintypes.HWND(handle),
        wintypes.UINT(WM_GETTEXT),
        wintypes.WPARAM(len(buffer)),
        ctypes.cast(buffer, ctypes.c_void_p),
        wintypes.UINT(SMTO_ABORTIFHUNG),
        wintypes.UINT(3000),
        ctypes.byref(result),
    )

    return buffer.value

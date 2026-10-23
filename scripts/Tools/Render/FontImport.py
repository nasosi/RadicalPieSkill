"""The "Font Import" window of Radical Pie 1.16, told apart as progress or as the unresolved-font report.

Radical Pie 1.16 puts up one modal window titled "Font Import", class `Dialog`, with no child controls, in two
situations that look the same from outside. While `slugfont.exe`, a child process of that Radical Pie, converts
a font the design names and no `.slug` holds yet, it is a progress window ("Importing the following fonts:")
that closes itself when the child is done. When the design names a font the editor cannot resolve, it is a
report ("The following fonts could not be imported:", one Close button) that stays until it is dismissed, and
the editor draws that slot in Times meanwhile. The progress window can turn into the report in place, same
handle, once the import ends. The text is drawn and cannot be read, so the only tell is the child: a Font
Import window with a live `slugfont.exe` under the same Radical Pie is progress, and one that is still up when
no such child is alive, `ReportSettleSeconds` after the last one exited or after the window was first seen, is
the report (measured 2026-10-08, `Skill/radical-pie-workspace/beta-1.16/FontImport/Probe.py`: the progress
window outlived its `slugfont.exe` by up to 0.6 s, and the window rose 0.06 to 0.2 s after the document title).

The watch answers the report itself: `Ready` closes it, which enables the document window again within 30 ms
(measured 2026-10-08), and records it in `reported`, so the pipeline completes its output with the slot in
Times and attaches the warning (`Tools.PieFormat.Fonts.FontWarnings`, ADR-0015). Left up, the report would
hold the editor until the timeout.

Two more measured facts make a pipeline wait for an import before its first command. A Save that lands while
the import runs crashed the editor with the access violation, 3 of 3 runs with a second, unresolvable font in
the design (Report item 1) and once with a single new font (Courier New, 2026-10-08); and a Save that does not
crash writes the slot back as Times, `i16{2}`, or drops it, because the slug arrives after the save (Report
item 4). So `FontImportWatch.Ready` holds the first command until `QuietSeconds` have passed since the title
with no Font Import window and no `slugfont.exe`, and until any import has finished. A watch told that the
design names a font with no slug yet also holds it until an import has been seen, or the report, for up to
`ImportStartSeconds`: an editor that took its Save a Copy before its import began wrote the font back as Times
and closed without importing it at all.

A `slugfont.exe` that outlives its Radical Pie keeps writing its slug, and a Radical Pie opened on the same
font before it has finished crashed with the access violation (Courier New and Segoe UI Light, 2026-10-08), so
`AwaitSlugFont` lets the children of a Radical Pie finish before the pipeline closes it, whether or not that
Radical Pie is still running, and `AwaitSlugFonts` lets every `slugfont.exe` on the machine finish before a
pipeline launches one. That wait is bounded by the caller's timeout for all of them together, and a
`slugfont.exe` still running at its end is named in the line it returns, which the pipeline carries into its
warning or its error, because it launches all the same.

The first launch that imports a font is also not trusted for its output. A pipeline reads `SlotsAwaitingImport`
before each launch, after the wait, and when `ImportedSince` says the launch imported one of those fonts, it
renders again from a fresh launch, which opens with every slug in place. `AwaitingReports` gives the font
check's own lines for those slots, which name a slug left empty. The measurements of 2026-10-21 behind that
and behind `ImportStartSeconds` are in `Docs/ARCHITECTURE.md`, Vendor facts about Radical Pie 1.16.
"""

import time

import pywintypes
import win32con
import win32gui

from Tools import Processes
from Tools.PieFormat import Fonts, OpenDdl

FontImportTitle = "Font Import"
SlugFontImage = "slugfont.exe"

ReportSettleSeconds = 2.0
QuietSeconds = 0.5

# How long a watch that awaits an import holds the first command for the import to show, and leaves a Font
# Import window with no `slugfont.exe` under it as progress
# (`Docs/ARCHITECTURE.md`, Vendor facts about Radical Pie 1.16).
ImportStartSeconds = 5.0

# The longest conversion measured is the 54 MB SimSun collection, which its `slugfont.exe` finished within
# 21 s of the render that started it (2026-10-08, Findings.md B2).
SlugFontSeconds = 120.0

Clear = "clear"
Importing = "importing"
Reported = "reported"


class FontImportWatch:
    """One Radical Pie's Font Import window and `slugfont.exe` children, from the moment its document is in.

    `reported` is True once the watch has seen the unresolved-font report and closed it. `awaitImport` says the
    design names a font with no slug yet (`SlotsAwaitingImport`), so an import is to be seen before a command.
    """

    def __init__(self, pid: int, awaitImport: bool = False):
        self.pid = pid
        self.awaitImport = awaitImport
        self.opened = time.monotonic()
        self.windowSince = None
        self.importerSeen = None
        self.state = Clear
        self.reported = False

    def State(self, windows: list) -> str:
        """`Importing` while a conversion runs or may still be showing, `Reported` once it is the report.

        A watch that awaits an import gives a window with no `slugfont.exe` seen yet `ImportStartSeconds` before
        it reads it as the report, and `ReportSettleSeconds` once an import has been seen.
        """

        now = time.monotonic()
        window = any(title == FontImportTitle for _, _, title in windows)

        if not window:
            self.windowSince = None
        elif self.windowSince is None:
            self.windowSince = now

        if Processes.ChildPids(self.pid, SlugFontImage):
            self.importerSeen = now

            return Importing

        if not window:
            return Clear

        settledFrom = max(self.windowSince, self.importerSeen or 0.0)
        settle = ImportStartSeconds if self.awaitImport and self.importerSeen is None else ReportSettleSeconds

        return Reported if now - settledFrom >= settle else Importing

    def Ready(self, windows: list) -> bool:
        """True once a command may be posted. Closes the report and records it. Keeps the state it read."""

        self.state = self.State(windows)

        if self.state == Reported:
            self.reported = True

            for handle in FontImportWindows(windows):
                CloseReport(handle)

            return False

        waited = time.monotonic() - self.opened

        if self.awaitImport and self.importerSeen is None and not self.reported and waited < ImportStartSeconds:
            return False

        return self.state == Clear and waited >= QuietSeconds


def CloseReport(handle: int) -> None:
    """Post a close to the report, tolerating a window that has gone already."""

    try:
        win32gui.PostMessage(handle, win32con.WM_CLOSE, 0, 0)
    except pywintypes.error:
        pass


def FontImportWindows(windows: list) -> list:
    """The handles of the Font Import windows among a process's top-level windows."""

    return [handle for handle, _, title in windows if title == FontImportTitle]


def AwaitSlugFont(pid: int) -> None:
    """Let the `slugfont.exe` children of one Radical Pie finish their slugs, up to SlugFontSeconds each.

    The children are found by their parent pid, which a process snapshot keeps after the parent has exited.
    """

    for child in sorted(Processes.ChildPids(pid, SlugFontImage)):
        Processes.AwaitProcessExit(child, SlugFontSeconds)


def AwaitSlugFonts(seconds: float) -> str:
    """Let every `slugfont.exe` on the machine finish its slug, whoever started it, within `seconds` altogether.

    Returns "" when every one has finished, and otherwise a line naming the ones still running, for the warning
    or the error of the launch that follows.
    """

    deadline = time.monotonic() + seconds
    running = [
        importer
        for importer in sorted(Processes.ImagePids(SlugFontImage))
        if not Processes.AwaitProcessExit(importer, deadline - time.monotonic())
    ]

    if not running:
        return ""

    pids = ", ".join(str(importer) for importer in running)

    return (
        f"Radical Pie was launched while slugfont.exe (pid {pids}) was still building a slug after a {seconds:g}s"
        " wait, and a font of the design it builds may be drawn in Times"
    )


def AwaitingReports(pieText: str) -> list:
    """The font check's reports on the `F` slots of the design whose font has no slug to draw from yet.

    That is a font Radical Pie imports on first use and one whose slug is empty. Nothing is awaited when the
    font database cannot be read or the text does not parse: the render loop takes text the validator refuses,
    for the anchor atlas, and Radical Pie's own answer to such text is what that caller measures.
    """

    database = Fonts.ReadableDatabase()

    if database is None:
        return []

    try:
        reports = Fonts.CheckDesign(pieText, database)
    except OpenDdl.PieSyntaxError:
        return []

    return [report for report in reports if report.state in (Fonts.Imports, Fonts.DamagedSlug)]


def SlotsAwaitingImport(pieText: str) -> frozenset:
    """The slots of `AwaitingReports`."""

    return frozenset(report.slot for report in AwaitingReports(pieText))


def ImportedSince(pieText: str, awaiting: frozenset) -> bool:
    """True when a slot that awaited its import before a launch has a slug to draw from now."""

    return bool(awaiting) and bool(awaiting - SlotsAwaitingImport(pieText))

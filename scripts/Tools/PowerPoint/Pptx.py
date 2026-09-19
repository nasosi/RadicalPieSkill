"""Replace `{{pie:<key>}}` placeholders in a PowerPoint deck with Radical Pie equations as OLE objects.

A placeholder takes one of two forms, and the text around it decides which (ADR-0013). A text shape whose
whole text is `{{pie:<key>}}` is the whole-shape form: the shape is deleted and an object of class
`RadicalPie.Application.1` is inserted at its left and top. A placeholder with text before or after it in
its own paragraph is the inline form: the placeholder becomes a gap in the sentence and the object stands in
that gap on the sentence's baseline, with the text continuing after it. Either way the object is named after
the key, which is what the collapse check prints and what a caller sees in PowerPoint's selection pane. A
deck takes no placeholder kind and no numbering: `|display`, `|numbered` and `{{ref:...}}` have nothing to
mean here, and a slide has no equation numbers to reference.

The inline form is one text pass and one geometry, both measured on 2026-09-17 and written down in
`Tools/PowerPoint/Inline.py`. The gap is a tab whose stop stands at the end of the text before it plus the
object's width plus twice a padding of 0.16 of the run's size, set through `TextFrame2` because the stops of
`TextFrame.Ruler` belong to every paragraph of the frame at once. The stop is set, the text measured again
and the stop set again until the end of the text before the gap stands still, because a stop changes the
width of the tab and can move the line break. The object's top is the text baseline less `height - depth`
from the render, and the baseline follows the line box: `box - descent` for a box no taller than
`1.2 * size`, three quarters of the box above that, plus the paragraph's space before on a first line that
is not the frame's first. An equation that comes within `Inline.Clearance` of the ink of the line above or
the line below opens the paragraph, with an exact line spacing in whole points where that line belongs to the
paragraph itself and space after the earlier of the two paragraphs where it does not; one that reaches past
the top or the bottom of the text frame opens nothing, because there is no line there to collide with and no
text box clips the object. The ink of a neighbouring line is the font's own until an inline equation of the
same run stands on it, and then it is the further of the two. A second gap on a second line of one paragraph
cannot take a stop,
because the tab there takes the first stop to its right, so its gap is filled with spaces instead and the
object is centred in what the fill came to. When every object of a text shape stands where it belongs the
shape and its objects are grouped, which is what keeps the sentence and its equations together; a shape that
is one of the layout's own placeholders is left ungrouped, because PowerPoint refuses to group one.

A gap that would end past the text area takes a line break in front of it and the equation starts the next
line, as a word that does not fit does, and the run says `moved to the next line` for it. The one width the
pipeline refuses is an equation wider than the text area itself, which no line of the shape can hold.

Shrink text on overflow is turned off on every shape that takes an inline gap, before the run's font size is
read. The object is drawn once at that size and cannot follow a later shrink, and the run's own edits make a
placeholder overflow: opening a paragraph took the sonnet-wrapped deck's body from 20 points to 14 and closed
the gaps on the equations already sized for 20. What the shrink used to absorb is refused instead. Once a
shape's gaps and its openings are final, the height of its text is measured against the height of its box and
a deck whose text stands past the bottom of a box is refused, naming the overflow and the size the shrink had
been showing the text at. A shape that grows with its text is left alone, because its box follows its text.

A space or a punctuation mark the author left against the placeholder takes the padding on its own side
away, so the equation takes the gap of a word and a mark stands at the object's edge rather than a thin
space from it (the operator, 2026-09-18). `PaddingOf` holds that rule and the run's line for the equation
says which padding went. Such a mark belongs inside the equation as its last symbol, which is what the
skill's `references/OutputForms.md` tells a caller to write.

The equation's size for an inline object is the run's own drawn font size as COM reports it, not the slide's
body size: an inline equation belongs to the sentence it stands in (ADR-0013). The inline form also needs
the equation's height and depth before the object exists, for the gap's width and for the baseline, so each
inline equation is rendered once through `Tools.Render.Svg` and PowerPoint draws it at that width on the
nearest eighth of a point.

An object keeps the corner pass one computed for it through pass three, which takes two calls of its own.
PowerPoint grows the object about its centre when the drawing arrives, so an object inserted at that corner
as the 5 by 7 point blank ends up half its drawn width to the left and half its drawn height above it: a
656.875 by 241 point equation inserted at 36, 90 stood at -289.875, -27, and of fifteen equations on a
13-slide deck twelve came out with a negative left (measured 2026-09-17). So pass one hands the corner of
each placeholder to pass three, which sets `Shape.Left` and `Shape.Top` back to it as soon as the
drawing has arrived, and `Presentation.Save` writes that position.

The corner travels through Python rather than being read off the blank, because `Shapes.AddOLEObject` puts an
object on the nearest eighth of a point where setting `Shape.Left` afterwards keeps the value it is given: a
placeholder at 43.2, 104.4 takes a blank at 43.25, 104.375, and 10.03 becomes 10.0 while 10.0625 becomes
10.125 (measured 2026-09-17). `CheckOffsets` reads the saved package and compares each `a:off` with the
corner pass one computed, a grouped object's child coordinates converted to the slide's. `CheckDeck` makes
no such comparison on a finished deck, because nothing in the package records where a placeholder stood.

The route is ADR-0009's, which is ADR-0004's three passes with four differences that PowerPoint forces
(measured 2026-09-13, `Tools/Probe/PowerPointProbe.py`, and recorded in Docs/ARCHITECTURE.md):

- `Shapes.AddOLEObject(FileName=<a .pie>)` raises nothing here and inserts a Packager Shell Object of class
  `Package`, where Word raises a dialog and fails. So the class route is the only one used and the `ProgID`
  of what came back is asserted.
- The embedding is rebuilt from `\x01CompObj`, `\x01Ole` and `RP`. PowerPoint writes no `\x03ObjInfo` and
  caches its own picture in `\x02OlePres000`, which holds the equation that was there before and is dropped.
- The deck is opened with a document window and the window is taken to each object's own slide. A new
  object's design takes the base font size of the body text of the layout of the slide the window shows,
  28.0 under a 28 pt layout, and the user default 12.0 when the deck has no window at all.
- `Application.Visible = False` is refused ("Hiding the application window is not allowed"), so the
  application window is minimised with `WindowState` instead and the editor window is minimised as it opens.

Every pass works on a file of the pipeline's own beside the output, and the output path is written by one
rename once the run has succeeded. A refusal or a failure removes that file and leaves the output path as it
was, whether or not a deck already stood there.

The base font size is why the inserted `RP` is read before it is replaced. An equation whose design block is
empty is written into the object with that size as its `V (n='fsiz')`, so the equation is the size of the
slide's body text rather than Radical Pie's factory 11 point; an equation that carries a design of its own is
embedded exactly as the caller wrote it. ADR-0010.

The collapse guard is the review of 2026-09-13, which measured that PowerPoint sizes every shape from the
metafile in `ppt/media` and never re-derives one from `RP` or from its own cache, so a collapsed object stays
collapsed and no reopen repairs it. The guard is in two halves. Before `Presentation.Save`, every object's
in-memory size must be neither of the two sizes an undrawn object stands at. After the save, `CheckDeck`
reads the package with no COM: an object is drawn when its `p:oleObj` `imgW`/`imgH` differs from the blank's
63720 by 88920 EMU, has no zero dimension, and its media EMF differs from the 284-byte blank by size or by
bytes. An object whose `RP` holds an empty equation is exempt, because the blank picture is the right picture
for it and only `RP` tells the two apart.

An equation the server cannot read is told from one it draws by the server's own exit, so the pass has to see
a server that lives only as long as the activation call does. `ServerWatch` polls the process listing from a
thread of its own, started before the activation, because PowerPoint answers the activation of an object whose
`RP` is unreadable only once the server has gone and a listing read after the call is back holds nothing of it
(measured 2026-09-19).

Process cleanup is narrower than the Word pipeline's, which ends every Radical Pie that appeared while it
ran. Other agents render on this machine, so a server that appears during a step is not evidence that the
step started it. This pipeline ends the PowerPoint processes its own `DispatchEx` created and the editor it
finds by the window title `Radical Pie - Equation in <the deck's file name>`, and nothing else. Every process
it does end goes through the registry of `Tools.Processes`, which the live tests are checked against.

An input that is not a PowerPoint package is refused by `CheckIsPowerPointPackage` before either verb reads
it, in one line naming the file: `zipfile` answers a missing file, a file that is not a zip and a zip of
something else with an errno line or a traceback of its own. Every equation is validated at the entry point as
well as by the command line, because a caller that came in through `EmbedEquations` with text of its own used
to pay a render and an insertion for an equation Radical Pie cannot read.

The Word pipeline's names for the pieces both pipelines share are imported rather than repeated: the class
and its CLSID, the `RP` body, the editor's window title, the package complaint, the process listing and the
end-of-process wait.
"""

import hashlib
import io
import math
import os
import posixpath
import re
import shutil
import tempfile
import threading
import time
import zipfile
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Optional

import olefile
import pythoncom
import pywintypes
import win32com.client
import win32con
import win32gui
from lxml import etree

from Tools import Processes
from Tools.PieFormat.Validator import FirstViolation
from Tools.PowerPoint import Inline
from Tools.Processes import AwaitProcessExit
from Tools.Render.Svg import (
    Attempts,
    DialogText,
    PostClose,
    RenderError,
    RenderSvg,
    SaveCommand,
    TopLevelWindows,
    WindowClass,
)
from Tools.Word.Docx import (
    ComErrorText,
    EditorTitlePrefix,
    EndProcess,
    EquationBody,
    ObjectClass,
    ObjectClassId,
    PackageComplaint,
    Pids,
)

PowerPointImage = "POWERPNT.EXE"
ServerImage = "RadicalPie.exe"

PlaceholderPattern = re.compile(r"\{\{pie:([^{}]+)\}\}")

# The three forms a placeholder is honoured in, which the run prints beside each equation. `shape` is the
# whole-shape form, `tab` an inline gap held open by a tab stop, `spaces` one held open by a run of spaces.
ShapeForm = "shape"
TabForm = "tab"
SpaceForm = "spaces"

# What the run prints beside an equation whose gap did not fit on the line the author's text left it on.
MovedNote = "moved to the next line"

# What the run prints for a text shape whose objects were left out of a group, with the reason. PowerPoint
# answers `Shapes.Range(...).Group()` on a selection holding a layout's placeholder with "Grouping is
# disabled for the selected shapes", which killed both bullet decks of the cold start of 2026-09-18 at the
# last step (`radical-pie-workspace/coldstart-3/opus-bullets/RadicalPieFeedback.md`).
UngroupedNote = "a layout placeholder, which PowerPoint refuses to group, so its equations stand beside it"

# What the run prints for a text shape whose autofit it turned off. "Shrink text on overflow", which a
# layout's placeholder carries by default, follows the text and an inline object cannot: the object is drawn
# once at the size the run reported. The sonnet-wrapped deck of 2026-09-18 rebuilt in its own body
# placeholder opened its paragraph to 42 points, PowerPoint shrank the body from 20 points to 14, and the
# gap the fill had measured at 101.9 points came out 74.62 with the 98.25 point equation standing over the
# text either side of it (measured 2026-09-18). The autofit goes before the font size is read, so the size
# the equations are drawn for is the size the text keeps.
AutofitNote = "autofit turned off, because a shrink would leave the equations at the size they were drawn"

MsoAutoSizeNone = 0
MsoAutoSizeShapeToFitText = 1
MsoAutoSizeTextToFitShape = 2

# How far the text of a shape may stand past the bottom of its box before the deck is refused. The height
# PowerPoint keeps inside a box is `TextFrame2.TextRange.BoundHeight` with the frame's top and bottom margins
# on it: six boxes cut to exactly that sum, at three font sizes, an exact spacing, a spacing in lines and a
# space after a paragraph, each held its text with the sum standing 0.0000 points from the box, and
# PowerPoint's own shrink text on overflow settles the text between 0.04 and 0.07 points under that sum
# (measured 2026-09-19). So this is the noise of a single precision COM read and nothing else.
TextHeightTolerance = 0.05

# An eighth of a point, the grid PowerPoint puts an extent on, and the noise of a single precision read on top.
DrawnWidthTolerance = 1.0 / 8.0 + 0.005

# The character the space fallback closes a gap with, a fifth of an em where an ordinary space is about a
# quarter, so the fill lands nearer the width the object asks for.
ThinSpace = " "
FillAttempts = 6

# How far short of the room it needs an equation may stand after its paragraph has been opened. The opening
# is asked for in whole points, so it overshoots by up to a point and this only catches an opening that did
# not take at all.
OpeningTolerance = 0.5

# The two metafiles that are not a drawing of the equation, and the size each gives the shape. Before a
# document is loaded the server answers `GetData` with 284 bytes whose frame is 63720 by 88920 EMU, which
# PowerPoint takes as 5 by 7 points; after the load and before the layout it answers with 632 bytes whose
# frame is zero, which PowerPoint takes as one pixel, 0.75 by 0.75 points. The second reached the deck on
# 2026-09-13, on the one equation of seventeen whose first posted Save arrived before the layout had run.
# A collapsed object is the same picture and the same size again, which is what makes them the guard's test.
BlankShapeSize = (5.0, 7.0)
UnlaidShapeSize = (0.75, 0.75)
UndrawnShapeSizes = (BlankShapeSize, UnlaidShapeSize)
BlankFrame = (63720, 88920)
BlankPictureSize = 284
BlankPictureDigest = "896f0250c5777bb4b24a6c51427cc8a7"

EmuPerPoint = 12700

# How far a saved object's offset may stand from its placeholder's corner. The package holds an offset as the
# EMU of the position pass three set, where it rounds an extent to an eighth of a point; the decks measured on
# 2026-09-17 came back at a difference of 0.000 points.
OffsetTolerance = 0.05

# The equation whose right picture is the blank one, written without whitespace as `EquationContent` gives it.
EmptyEquationContent = "Gr{Bg{}}"

DrawnState = "drawn"
BlankState = "blank"
CollapsedState = "collapsed"

EquationStream = "RP"

# The stream PowerPoint caches its own picture in. It is dropped when the embedding is rebuilt, because it
# holds the picture of the equation that was there before.
PresentationStreamPrefix = "\x02"

BaseFontSizePattern = re.compile(r"V \(n='fsiz'\) \{f\{([0-9.]+)\}\}")

# A design block with nothing in it, which is what the standing ruling of 2026-09-10 puts in a generated
# equation, and the design that replaces it when the slide's base font size is known.
EmptyDesignPattern = re.compile(r"\AD\s*\{\s*\}")
BaseFontSizeDesign = "D\n{\n\tV (n='fsiz') {f{%s}}\n}"

PresentationNamespace = "http://schemas.openxmlformats.org/presentationml/2006/main"
DrawingNamespace = "http://schemas.openxmlformats.org/drawingml/2006/main"
RelationshipNamespace = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PackageRelationshipNamespace = "http://schemas.openxmlformats.org/package/2006/relationships"

SlideIdTag = f"{{{PresentationNamespace}}}sldId"
ShapeTag = f"{{{PresentationNamespace}}}sp"
GroupShapeTag = f"{{{PresentationNamespace}}}grpSp"
GroupPropertiesTag = f"{{{PresentationNamespace}}}grpSpPr"
ShapePropertiesTag = f"{{{PresentationNamespace}}}spPr"
GraphicFrameTag = f"{{{PresentationNamespace}}}graphicFrame"
NonVisualFrameTag = f"{{{PresentationNamespace}}}nvGraphicFramePr"
NonVisualShapeTag = f"{{{PresentationNamespace}}}nvSpPr"
PlaceholderTag = f"{{{PresentationNamespace}}}ph"
NonVisualPropertiesTag = f"{{{PresentationNamespace}}}cNvPr"
FrameTransformTag = f"{{{PresentationNamespace}}}xfrm"
OleObjectTag = f"{{{PresentationNamespace}}}oleObj"
TextTag = f"{{{DrawingNamespace}}}t"
ParagraphTag = f"{{{DrawingNamespace}}}p"
ParagraphPropertiesTag = f"{{{DrawingNamespace}}}pPr"
RunTag = f"{{{DrawingNamespace}}}r"
RunPropertiesTag = f"{{{DrawingNamespace}}}rPr"
BodyPropertiesTag = f"{{{DrawingNamespace}}}bodyPr"
TableTag = f"{{{DrawingNamespace}}}tbl"
TransformTag = f"{{{DrawingNamespace}}}xfrm"
OffsetTag = f"{{{DrawingNamespace}}}off"
ExtentTag = f"{{{DrawingNamespace}}}ext"
ChildOffsetTag = f"{{{DrawingNamespace}}}chOff"
ChildExtentTag = f"{{{DrawingNamespace}}}chExt"
BlipTag = f"{{{DrawingNamespace}}}blip"

# The paragraph alignments an inline gap cannot be placed in, as the package spells them, and the text
# direction a shape must have. A centred or a right-aligned paragraph never settles under a tab stop, and
# vertical text has no baseline for an object to stand on.
RefusedAlignments = frozenset({"ctr", "r", "just", "justLow", "dist", "thaiDist"})
HorizontalText = "horz"
RelationshipTag = f"{{{PackageRelationshipNamespace}}}Relationship"
RelationshipId = f"{{{RelationshipNamespace}}}id"
RelationshipEmbed = f"{{{RelationshipNamespace}}}embed"

PresentationPart = "ppt/presentation.xml"
PresentationRelationshipsPart = "ppt/_rels/presentation.xml.rels"

MsoTrue = -1
PpViewNormal = 9
PpWindowMinimized = 2

StgmCreateReadWriteExclusive = 0x1000 | 0x0002 | 0x0010
StgmCreateWriteExclusive = 0x1000 | 0x0001 | 0x0010

# Office's modal windows: `NUIDialog` is the Office dialog, `#32770` the plain Win32 message box.
DialogClasses = frozenset({"NUIDialog", "#32770"})

# What an activated server leaving on its own means. It raises no dialog over an equation it cannot read.
UnreadableEquation = "it leaves like that when it cannot read the equation"

PollSeconds = 0.05
GuardSeconds = 0.3

# What one inline equation's render gets. `Tools.Render.Svg` retries the whole attempt once inside this, and
# a render of one equation takes about 2.5 seconds on this machine.
RenderSeconds = 60.0
RepostSaveSeconds = 0.25
ExitGraceSeconds = 10.0

# The budget for a whole run when the caller names none, base plus an allowance for each object. Measured on
# 2026-09-19 against PowerPoint 16 and Radical Pie 1.15: a one-object deck took 26.2 seconds end to end and a
# six-object deck 39.1, which is 23.6 seconds of the three PowerPoint starts and 2.58 seconds an object. The
# same figures put the 38 objects of Demo/FeynmanII18 at 121.6 seconds, where that deck took 119. The
# allowance is five times the measured rate and the base is the whole of what a one-object deck needs.
BaseTimeoutSeconds = 120.0
PerObjectTimeoutSeconds = 13.0

# What one object gets: the activation and one retry of it, the retry against a server of its own. Under the
# parallel load of 2026-09-12 the Word activation failed about once in a hundred objects and drew on the
# rerun; this is the same server through the same editor window.
ActivationAttempts = 2
ActivationSettleSeconds = 1.0


class PowerPointError(RuntimeError):
    """The deck was not produced. The message names what was observed, in the pipeline's own terms."""


@dataclass(frozen=True)
class Placeholder:
    """One `{{pie:<key>}}` as the draft holds it: the slide and shape it stands in, and where in the text.

    `inline` is false for the whole-shape form, whose object replaces the shape. `paragraph` counts the
    paragraphs of the shape from one and `ordinal` counts the placeholders of that paragraph, which is what
    the text pass addresses a gap by. `layoutPlaceholder` is true where the shape is one of the layout's own
    placeholders, which PowerPoint refuses to group.
    """

    slideNumber: int
    shapeName: str
    key: str
    inline: bool = False
    paragraph: int = 1
    ordinal: int = 1
    layoutPlaceholder: bool = False


@dataclass(frozen=True)
class InlineEquation:
    """One inline placeholder's equation as pass one prepares it, and the size Radical Pie draws it at.

    The font and size are the run's own, read from the placeholder's first character before the text is
    touched; `equation` is the text the embedding will carry, which is the caller's with that size written
    into an empty design block. The width is the render's on the nearest eighth of a point, which is what
    PowerPoint gives the object, and the height already contains the depth.
    """

    font: str
    fontSize: float
    equation: str
    width: float
    height: float
    depth: float


@dataclass(frozen=True)
class Plan:
    """One placeholder as pass one leaves it: the corner its object goes on and how its gap was made."""

    key: str
    slideNumber: int
    form: str
    left: float
    top: float
    equation: str
    width: float
    opened: str = ""
    tight: str = ""
    moved: str = ""


@dataclass(frozen=True)
class GapPadding:
    """One gap's padding either side, and the line the run prints when a punctuation mark took one away."""

    leading: float
    trailing: float
    note: str


@dataclass
class ShapeText:
    """One text shape's text while pass one is rewriting it, and where each of its gaps stands in it.

    The text is kept in Python and checked against what PowerPoint reads back after every edit, because a
    gap is addressed by a character index and an index that has drifted places an object somewhere else.
    `starts` and `lengths` are keyed by the placeholder's position in the pipeline's own list.
    """

    shape: object
    text: str
    starts: dict = field(default_factory=dict)
    lengths: dict = field(default_factory=dict)


@dataclass(frozen=True)
class GapGeometry:
    """One inline gap as PowerPoint lays it out: the text either side of it and its baseline.

    `aboveBaseline` and `belowBaseline` are the baselines of the lines the gap stands between, either of
    them `None` when there is no line on that side for the equation to reach into. `aboveInk` is how far the
    line above inks below its own baseline and `belowInk` how far the line below inks above its own, each
    the font's own ink until an inline equation of this run standing on that line raises it.
    """

    preEnd: float
    postStart: float
    lineTop: float
    box: float
    spaceAbove: float
    spaceBefore: float
    spaceAfter: float
    baseline: float
    firstLine: bool
    lastLine: bool
    aboveBaseline: float
    belowBaseline: float
    aboveInk: float
    belowInk: float


@dataclass(frozen=True)
class EmbeddedEquation:
    """One embedded equation: its key, its slide, the size it was drawn at, and how it was placed.

    `form` is `shape`, `tab` or `spaces`, `opened` is what the pipeline set on the equation's paragraph to
    make room for it, `tight` names the padding a punctuation mark beside the placeholder took away, and
    `moved` says the gap went to the next line because the author's own line had no room. `shapeNotes` are
    what the run did to the text shape itself rather than to this equation, carried by the first equation of
    that shape so the run prints each of them once.
    """

    key: str
    slideNumber: int
    width: float
    height: float
    form: str = ShapeForm
    opened: str = ""
    tight: str = ""
    moved: str = ""
    shapeNotes: tuple = ()


@dataclass(frozen=True)
class DrawnObject:
    """One object as pass three leaves it: the size Radical Pie drew it at and the corner it stands on."""

    width: float
    height: float
    left: float
    top: float


@dataclass(frozen=True)
class ObjectPart:
    """One Radical Pie object as the package holds it: where it is, what it shows and where both live."""

    slideNumber: int
    name: str
    embeddingPart: str
    picturePart: str
    frame: tuple
    offset: tuple
    size: tuple


@dataclass(frozen=True)
class ObjectReport:
    """One object as the collapse check sees it. The state is `drawn`, `blank` or `collapsed`."""

    slideNumber: int
    name: str
    width: float
    height: float
    state: str


def TimeoutBudget(objectCount: int) -> float:
    """What a run of `objectCount` objects gets to finish in, the base and the allowance of each object."""

    return BaseTimeoutSeconds + PerObjectTimeoutSeconds * objectCount


def EmbedEquations(inputPath: Path, outputPath: Path, equations: dict, timeoutSeconds: Optional[float] = None) -> list:
    """Write `inputPath` to `outputPath` with every `{{pie:<key>}}` shape replaced by `equations[key]`.

    Both paths may be relative to the caller's working directory, which is not the one PowerPoint hands them
    to its own file open, so they are resolved here and every pass below sees an absolute path.

    Returns one `EmbeddedEquation` per placeholder, in slide order. Every placeholder needs an equation and
    every equation needs a placeholder, both checked before PowerPoint starts, along with the key that names
    two shapes on one slide and every shape an inline placeholder cannot be placed in.

    Every pass works on a file of the pipeline's own beside the output, which is moved onto the output path
    once the run has succeeded and its checks have passed. A refusal leaves that path as it was: the copy used
    to go straight there, so a deck refused half way through handed back the draft's own shapes with no
    equation in them, and a rerun over an output file that already held a good deck destroyed it.

    Every pass that starts PowerPoint shares one deadline. A `timeoutSeconds` of its own bounds the run at what
    the caller asks for; none takes `TimeoutBudget` of the count of placeholders, so the budget grows with the
    objects the run has to draw.
    """

    # `Path.resolve` returns a relative path unchanged on Windows under Python 3.9 when the file is not there
    # yet, which the output file never is, so both paths go through `os.path.abspath` instead.
    inputPath = Path(os.path.abspath(inputPath))
    outputPath = Path(os.path.abspath(outputPath))

    CheckIsPowerPointPackage(inputPath)
    placeholders = ReadPlaceholders(inputPath)
    CheckPlaceholders(placeholders, equations)
    CheckEquationsValidate(equations)

    outputPath.parent.mkdir(parents=True, exist_ok=True)
    workPath = WorkingDeck(inputPath, outputPath)

    if timeoutSeconds is None:
        timeoutSeconds = TimeoutBudget(len(placeholders))

    deadline = time.monotonic() + timeoutSeconds

    try:
        plans, shrinking = PrepareObjects(workPath, placeholders, equations, deadline)
        ReplaceEquationStreams(workPath, placeholders, [plan.equation for plan in plans])
        drawn = RenderObjects(workPath, placeholders, plans, deadline)
        GroupObjects(workPath, placeholders, deadline)
        CheckDrawn(workPath, len(placeholders))
        CheckOffsets(workPath, placeholders, plans)
    except BaseException:
        # A keyboard interrupt leaves no half-built deck behind either, so the sweep is on BaseException.
        workPath.unlink(missing_ok=True)

        raise

    os.replace(workPath, outputPath)

    ungrouped = UngroupedShapes(placeholders)
    reported = set()
    embedded = []

    for placeholder, plan, item in zip(placeholders, plans, drawn):
        shape = (placeholder.slideNumber, placeholder.shapeName)
        notes = []

        if shape not in reported:
            named = f"slide {placeholder.slideNumber}, the shape {placeholder.shapeName!r}"
            reported.add(shape)

            if shape in shrinking:
                notes.append(f"{named}: {AutofitNote}")

            if shape in ungrouped:
                notes.append(f"{named}: {UngroupedNote}")

        embedded.append(
            EmbeddedEquation(
                plan.key,
                plan.slideNumber,
                item.width,
                item.height,
                plan.form,
                plan.opened,
                plan.tight,
                plan.moved,
                tuple(notes),
            )
        )

    return embedded


def CheckEquationsValidate(equations: dict) -> None:
    """Every equation the caller handed over validates, which is the last thing known before PowerPoint starts.

    The command line validates the files it read; this is the same gate for a caller that came in through the
    entry point with text, and it names the key. An inline equation is also rendered before the first object is
    inserted, so an equation Radical Pie cannot read used to cost a render and a launch before it failed.
    """

    for key in sorted(equations):
        violation = FirstViolation(equations[key])

        if violation:
            raise PowerPointError(f"the equation {key} does not validate, so nothing was started: {violation}")


def CheckIsPowerPointPackage(deckPath: Path) -> None:
    """Refuse a deck that is not there or is not a PowerPoint package, before anything else reads it.

    Both verbs run this first. `embed` used to hand the caller a `zipfile` traceback for a file that was not a
    package and an errno line for one that was missing, and `check` a traceback for a zip of something else.
    `PackageComplaint` is the Word pipeline's, which names the part this one requires.
    """

    complaint = PackageComplaint(deckPath, PresentationPart)

    if complaint:
        raise PowerPointError(f"{deckPath} is not a PowerPoint package: {complaint}")


def WorkingDeck(inputPath: Path, outputPath: Path) -> Path:
    """The draft copied to a file of the pipeline's own beside the output, which every pass works on.

    The name keeps the output's extension, because PowerPoint decides what it is opening by it, and it stands
    in the output's own directory, so the move onto the output path at the end of the run is a rename on one
    volume. It is unique, because pass three finds its Radical Pie editor by a window title that carries this
    file's name.
    """

    handle, name = tempfile.mkstemp(prefix=outputPath.stem + ".", suffix=outputPath.suffix, dir=outputPath.parent)
    os.close(handle)
    workPath = Path(name)
    shutil.copyfile(inputPath, workPath)

    return workPath


def ReadPlaceholders(deckPath: Path) -> list:
    """The placeholders in slide order, read without starting PowerPoint, each with the form it takes.

    The slides are taken in the order `ppt/presentation.xml` lists them, which the part names do not follow,
    and the text of a paragraph is the concatenation of its runs, because PowerPoint splits a placeholder
    across runs whenever it feels like it.

    A shape whose whole text is one placeholder takes the whole-shape form and every other placeholder is
    inline, which is what the checks below are about: an inline object stands on a baseline the pipeline
    computes from the run it sits in, and there are shapes that have no such baseline to give. Each of them
    is refused here, before anything is launched.
    """

    placeholders = []

    with zipfile.ZipFile(deckPath) as package:
        for number, part in enumerate(SlideParts(package), 1):
            root = etree.fromstring(package.read(part))
            CheckTables(root, number)

            for shape in root.iter(ShapeTag):
                placeholders += ShapePlaceholders(shape, number)

    return placeholders


def ShapePlaceholders(shape, slideNumber: int) -> list:
    """The placeholders of one text shape, with the paragraph and the ordinal that address each gap."""

    paragraphs = [ParagraphText(paragraph) for paragraph in shape.iter(ParagraphTag)]
    found = []

    for index, body in enumerate(paragraphs, 1):
        for ordinal, match in enumerate(PlaceholderPattern.finditer(body), 1):
            found.append((index, ordinal, match))

    if not found:
        return []

    name = shape.find(f"{NonVisualShapeTag}/{NonVisualPropertiesTag}").get("name")
    whole = "".join(paragraphs).strip()
    wholeShape = len(found) == 1 and whole == found[0][2].group(0)

    for _, _, match in found:
        if "|" in match.group(1):
            raise PowerPointError(
                f"{match.group(0)} on slide {slideNumber} names a placeholder kind;"
                " a deck has no display and no numbered equations, so a placeholder carries a key alone"
            )

    CheckShapeIsPlaceable(shape, name, slideNumber, wholeShape)

    if not wholeShape:
        for index, _, _ in found:
            CheckParagraphIsPlaceable(shape, index, name, slideNumber)

    # The layout's own placeholder, `p:ph` under the shape's non-visual properties and `Shape.Type` 14 to
    # COM. It is read here, before anything is launched, because the grouping pass is the last step of the
    # run and a deck that dies there has cost every render and every activation.
    layoutPlaceholder = shape.find(f"{NonVisualShapeTag}//{PlaceholderTag}") is not None

    return [
        Placeholder(slideNumber, name, match.group(1), not wholeShape, index, ordinal, layoutPlaceholder)
        for index, ordinal, match in found
    ]


def ParagraphText(paragraph) -> str:
    """One paragraph's text, its runs joined. A line break carries no text and adds none here."""

    return "".join(node.text or "" for node in paragraph.iter(TextTag))


def CheckTables(root, slideNumber: int) -> None:
    """A placeholder inside a table cell, which no form of this pipeline reaches.

    A table's text lives in an `a:tbl` under a `p:graphicFrame` and not in a shape of its own, so PowerPoint
    finds no shape to delete and no run to measure. Without this the key would be reported as one the deck
    holds no placeholder for, which names the equation and not the table.
    """

    for table in root.iter(TableTag):
        for paragraph in table.iter(ParagraphTag):
            match = PlaceholderPattern.search(ParagraphText(paragraph))

            if match is not None:
                raise PowerPointError(
                    f"{match.group(0)} stands in a table cell on slide {slideNumber};"
                    " an equation goes in a text shape, because a table cell has no shape to place it in"
                )


def CheckShapeIsPlaceable(shape, name: str, slideNumber: int, wholeShape: bool) -> None:
    """The shape itself: not inside a group, and, for an inline gap, horizontal and unrotated.

    A shape inside a group is refused in either form. PowerPoint's `Shapes` collection holds the group and
    not its members, so the pipeline finds no shape to delete for a whole-shape placeholder and no shape to
    group for an inline one.
    """

    if next(shape.iterancestors(GroupShapeTag), None) is not None:
        raise PowerPointError(
            f"the shape {name!r} on slide {slideNumber} holds a placeholder and stands inside a group;"
            " ungroup it, because PowerPoint reaches a grouped shape only through the group"
        )

    if wholeShape:
        return

    body = shape.find(f".//{BodyPropertiesTag}")
    direction = None if body is None else body.get("vert")

    if direction is not None and direction != HorizontalText:
        raise PowerPointError(
            f"the shape {name!r} on slide {slideNumber} holds an inline placeholder and its text runs"
            f" {direction!r}; an inline equation stands on a horizontal baseline"
        )

    transform = shape.find(f"{ShapePropertiesTag}/{TransformTag}")
    rotation = None if transform is None else transform.get("rot")

    if rotation is not None and int(rotation) != 0:
        raise PowerPointError(
            f"the shape {name!r} on slide {slideNumber} holds an inline placeholder and is rotated;"
            " an inline equation stands on a horizontal baseline"
        )


def CheckParagraphIsPlaceable(shape, index: int, name: str, slideNumber: int) -> None:
    """The paragraph an inline gap stands in: left-aligned, and one font size across its runs.

    A centred or right-aligned paragraph is refused because the tab stop that holds the gap open means
    nothing there: the second probe's centred case moved the text after the gap 57 pt as the stop went in and
    never settled, and the right-aligned one ignored the stop altogether and left 55.38 pt beside the object
    instead of the 2.88 asked for (measured 2026-09-17). An alignment the paragraph inherits from its layout
    rather than carrying itself is caught by the same non-settling measurement during the run.

    Two font sizes on one line would give the gap two paddings and two baselines, and the pipeline reads one
    run's size for the equation, so a paragraph whose runs carry different sizes is refused.
    """

    paragraph = list(shape.iter(ParagraphTag))[index - 1]
    properties = paragraph.find(ParagraphPropertiesTag)
    alignment = None if properties is None else properties.get("algn")

    if alignment in RefusedAlignments:
        raise PowerPointError(
            f"paragraph {index} of the shape {name!r} on slide {slideNumber} holds an inline placeholder and"
            f" is aligned {alignment!r}; an inline equation needs a left-aligned paragraph"
        )

    sizes = set()

    for run in paragraph.iter(RunTag):
        properties = run.find(RunPropertiesTag)

        if properties is not None and properties.get("sz") is not None:
            sizes.add(properties.get("sz"))

    sizes = sorted(sizes)

    if len(sizes) > 1:
        named = ", ".join(f"{int(size) / 100:g}" for size in sizes)

        raise PowerPointError(
            f"paragraph {index} of the shape {name!r} on slide {slideNumber} holds an inline placeholder and"
            f" text at {named} points; an inline equation needs one font size on its line"
        )


def CheckPlaceholders(placeholders: list, equations: dict) -> None:
    """Everything about the deck that can be known before PowerPoint starts, each failure naming its offender.

    A key names the object the pipeline inserts, and PowerPoint finds a shape on a slide by that name, so two
    placeholders on one slide cannot share a key. The same key on two slides is one equation shown twice.
    """

    for slideNumber in sorted({item.slideNumber for item in placeholders}):
        keys = [item.key for item in placeholders if item.slideNumber == slideNumber]
        twice = sorted({key for key in keys if keys.count(key) > 1})

        if twice:
            raise PowerPointError(
                f"slide {slideNumber} holds two placeholders for each of these keys, and a key names one"
                f" shape on a slide: {', '.join(twice)}"
            )

    placed = {item.key for item in placeholders}
    unknown = sorted(placed - set(equations))
    unused = sorted(set(equations) - placed)

    if unknown:
        raise PowerPointError(f"the deck holds placeholders with no equation: {', '.join(unknown)}")

    if unused:
        raise PowerPointError(f"the deck holds no placeholder for the equations: {', '.join(unused)}")


def SlideParts(package: zipfile.ZipFile) -> list:
    """The slide parts in the order the presentation lists them, which the part names do not follow."""

    relationships = ReadRelationships(package, PresentationRelationshipsPart, "ppt")
    presentation = etree.fromstring(package.read(PresentationPart))

    return [relationships[element.get(RelationshipId)] for element in presentation.iter(SlideIdTag)]


def ReadRelationships(package: zipfile.ZipFile, partName: str, baseDirectory: str) -> dict:
    """The relationships of one part, each target resolved to its part name inside the package."""

    relationships = etree.fromstring(package.read(partName))

    return {
        element.get("Id"): posixpath.normpath(posixpath.join(baseDirectory, element.get("Target").lstrip("/")))
        for element in relationships.iter(RelationshipTag)
    }


def ReadObjectParts(package: zipfile.ZipFile) -> list:
    """Every Radical Pie object of the deck, in slide order, as the package holds it.

    A `p:graphicFrame` carries the object twice, once under `mc:Choice` and once under `mc:Fallback`; the two
    `p:oleObj` elements say the same thing and only the second holds the picture, so the first is read for the
    object and the frame's one `a:blip` for the picture.

    A frame under a `p:grpSp` is read like any other and its offset and extent are converted to the slide's
    own coordinates, because that is where the object stands on the slide the reader sees.
    """

    parts = []

    for number, slidePart in enumerate(SlideParts(package), 1):
        relationships = ReadRelationships(package, RelationshipsPartOf(slidePart), posixpath.dirname(slidePart))

        for frame in etree.fromstring(package.read(slidePart)).iter(GraphicFrameTag):
            element = frame.find(f".//{OleObjectTag}")

            if element is None or element.get("progId") != ObjectClass:
                continue

            name = frame.find(f"{NonVisualFrameTag}/{NonVisualPropertiesTag}").get("name")
            picture = frame.find(f".//{BlipTag}")

            if picture is None:
                raise PowerPointError(f"the object {name!r} on slide {number} carries no picture")

            offset, extent = SlideGeometry(frame)
            parts.append(
                ObjectPart(
                    number,
                    name,
                    relationships[element.get(RelationshipId)],
                    relationships[picture.get(RelationshipEmbed)],
                    (int(element.get("imgW")), int(element.get("imgH"))),
                    offset,
                    extent,
                )
            )

    return parts


def SlideGeometry(frame) -> tuple:
    """One graphic frame's offset and extent in slide points, the coordinates of its groups undone.

    A grouped object's `a:off` is its group's child coordinate. The probe's two objects read 139.64 and
    311.88 while grouped, which is where they stood before the group was moved 60 pt to the right, so a check
    that compares `a:off` with a slide position fails on a grouped deck (measured 2026-09-17). Each enclosing
    group maps its child space onto the space it stands in through `a:chOff`, `a:chExt`, `a:off` and `a:ext`,
    and the groups are taken innermost first.
    """

    transform = frame.find(FrameTransformTag)
    offset = transform.find(OffsetTag)
    extent = transform.find(ExtentTag)
    x = float(offset.get("x"))
    y = float(offset.get("y"))
    width = float(extent.get("cx"))
    height = float(extent.get("cy"))

    for group in frame.iterancestors(GroupShapeTag):
        groupTransform = group.find(f"{GroupPropertiesTag}/{TransformTag}")

        if groupTransform is None:
            continue

        groupOffset = groupTransform.find(OffsetTag)
        groupExtent = groupTransform.find(ExtentTag)
        childOffset = groupTransform.find(ChildOffsetTag)
        childExtent = groupTransform.find(ChildExtentTag)

        if any(item is None for item in (groupOffset, groupExtent, childOffset, childExtent)):
            continue

        if not float(childExtent.get("cx")) or not float(childExtent.get("cy")):
            continue

        scaleX = float(groupExtent.get("cx")) / float(childExtent.get("cx"))
        scaleY = float(groupExtent.get("cy")) / float(childExtent.get("cy"))
        x = float(groupOffset.get("x")) + (x - float(childOffset.get("x"))) * scaleX
        y = float(groupOffset.get("y")) + (y - float(childOffset.get("y"))) * scaleY
        width *= scaleX
        height *= scaleY

    return (x / EmuPerPoint, y / EmuPerPoint), (width / EmuPerPoint, height / EmuPerPoint)


def RelationshipsPartOf(partName: str) -> str:
    """The `_rels` part that carries one part's relationships."""

    return posixpath.join(posixpath.dirname(partName), "_rels", posixpath.basename(partName) + ".rels")


def PrepareObjects(deckPath: Path, placeholders: list, equations: dict, deadline: float) -> list:
    """Pass one: the text of every inline gap is made final, then every placeholder becomes an empty object.

    Returns one `Plan` per placeholder, in placeholder order: the corner pass three puts the drawn object back
    on, the form the gap took, and the equation text pass two writes into the embedding, and the shapes whose
    shrink text on overflow was turned off with the size each was showing.

    The order inside the pass is ADR-0013's contract. Every text change happens before the first object is
    inserted and every position is read after the text is final, because replacing a placeholder by a gap
    moves the text of its own line and the stop of one gap moves the text before the next.

    The deck is opened with a document window and the window is taken to each object's own slide, which is
    what makes a new object's design carry that slide's base font size. A placeholder shape is found by the
    name the package gave it, and `CheckPowerPointReadsTheDeck` is what says that name reaches the right
    shape before anything is deleted.

    Each shape's box is checked against its text as soon as that shape is laid out, which is before the first
    object of the deck is inserted: the text is final there, and a deck that is going to be refused for the
    room it has left costs no activation.
    """

    plans = {}

    with PowerPointSession(deadline) as session:
        try:
            presentation = OpenDeck(session, deckPath)
            presentation.Windows(1).ViewType = PpViewNormal
            CheckPowerPointReadsTheDeck(presentation, placeholders)
            shrinking = TurnOffAutofit(presentation, placeholders)
            geometry = InlineGeometries(presentation, placeholders, equations, deadline)

            for slideNumber, shapeName in InlineShapes(placeholders):
                presentation.Windows(1).View.GotoSlide(slideNumber)
                items = [
                    (index, item)
                    for index, item in enumerate(placeholders)
                    if item.inline and (item.slideNumber, item.shapeName) == (slideNumber, shapeName)
                ]
                slide = presentation.Slides(slideNumber)
                plans.update(LayOutShape(slide, shapeName, items, geometry))
                CheckTheBoxHoldsTheText(slide.Shapes(shapeName), slideNumber, shapeName, shrinking)
                session.CheckDialogs()

            for index, placeholder in enumerate(placeholders):
                # The base font size follows the slide the window shows and not the slide the object goes on:
                # inserted on slide 2 with slide 1 in the window, an object took the title layout's 24 point
                # subtitle instead of that slide's 28 point body (measured 2026-09-13).
                presentation.Windows(1).View.GotoSlide(placeholder.slideNumber)
                slide = presentation.Slides(placeholder.slideNumber)

                if placeholder.inline:
                    InsertObject(slide, plans[index].left, plans[index].top, placeholder.key)
                else:
                    plans[index] = ReplaceShape(slide, placeholder, equations[placeholder.key])

                session.CheckDialogs()

            presentation.Save()
            CloseDeck(presentation)
        except pythoncom.com_error as error:
            raise PowerPointError(session.Explain("laying out the text and inserting the objects", error)) from None

    return [plans[index] for index in range(len(placeholders))], shrinking


def TurnOffAutofit(presentation, placeholders: list) -> dict:
    """Shrink text on overflow off on every shape that takes an inline gap, and the size each was showing.

    It runs before the run's font size is read, so a draft whose autofit has already shrunk its text goes
    back to the size the author gave it and the equations are drawn for that size. `TextFrame.AutoSize` has
    no shrink in it at all; the mode lives on `TextFrame2` alone, which answers this property as an ordinary
    attribute where its paragraphs need the dispid invoked by hand.

    The size the shrink was showing the text at is read before the mode goes, keyed by the shape: it is what
    the overflow refusal tells a caller to write into the draft. A body placeholder cut to 500 by 90 points
    showed an 18 point sentence at 17 and held it 0.79 points inside its box, and with the mode off the same
    text stood 14.4 points past the bottom (measured 2026-09-19).
    """

    turned = {}

    for slideNumber, shapeName in InlineShapes(placeholders):
        shape = presentation.Slides(slideNumber).Shapes(shapeName)

        if shape.TextFrame2.AutoSize != MsoAutoSizeTextToFitShape:
            continue

        first = next(
            item
            for item in placeholders
            if item.inline and (item.slideNumber, item.shapeName) == (slideNumber, shapeName)
        )
        turned[(slideNumber, shapeName)] = PlaceholderCharacter(shape, first).Font.Size
        shape.TextFrame2.AutoSize = MsoAutoSizeNone

    return turned


def CheckTheBoxHoldsTheText(shape, slideNumber: int, shapeName: str, shrinking: dict) -> None:
    """The text of one shape stands inside its box now that its gaps and its openings are final.

    The height a box holds is the text's own `BoundHeight` with the frame's top and bottom margins on it,
    which is the quantity PowerPoint's shrink text on overflow works to: taking a one line 18 point
    placeholder's box from 40 points down to 22, PowerPoint held that sum under the box at every height, by
    0.04 to 0.07 points at the tightest, and it reduced the line spacing before it touched the font size
    (measured 2026-09-19).

    A shape whose box grows with its text is not measured, because its box follows whatever the run does to
    the text. Every other shape is, whether the run turned its autofit off or the author had none: the
    openings the run sets on a paragraph make a fixed box overflow on their own.
    """

    if shape.TextFrame2.AutoSize == MsoAutoSizeShapeToFitText:
        return

    frame = shape.TextFrame
    needed = shape.TextFrame2.TextRange.BoundHeight + frame.MarginTop + frame.MarginBottom
    overflow = needed - shape.Height

    if overflow <= TextHeightTolerance:
        return

    shrunk = shrinking.get((slideNumber, shapeName))

    if shrunk is None:
        autofit = "that shape carried no shrink text on overflow for the run to turn off"
    else:
        autofit = (
            "the run turned that shape's shrink text on overflow off, where PowerPoint had been showing the"
            f" text at {shrunk:g} points"
        )

    raise PowerPointError(
        f"the text of the shape {shapeName!r} on slide {slideNumber} needs {needed:.1f} points and its box is"
        f" {shape.Height:.1f} points tall, so it stands {overflow:.1f} points past the bottom of its box;"
        f" {autofit}; give the text a smaller size in the draft, shorten it, or give the box more room, then"
        " run again"
    )


def PlaceholderCharacter(shape, placeholder: Placeholder):
    """The first character of one placeholder, whose font is the font the equation is drawn in.

    The size it reports is the size on the slide even where an autofit has shrunk the text, 11 for runs of
    `sz="1800"` under a `fontScale` of 62.5 per cent (measured 2026-09-17), so it is read before the autofit
    goes and again after, and each read is the size the text stands at then.
    """

    text = shape.TextFrame.TextRange
    start, _ = PlaceholderSpans(text.Text, [placeholder])[0]

    return text.Characters(start, 1)


def CheckPowerPointReadsTheDeck(presentation, placeholders: list) -> None:
    """PowerPoint holds the same placeholders in the same shapes as the package, before anything is changed.

    The pre-checks ran on the package and the text pass drives PowerPoint, so the two have to agree on which
    shape carries which keys. The shape is looked up by the name the package gave it, which is also what
    catches a slide that carries two shapes of one name.
    """

    for slideNumber in sorted({item.slideNumber for item in placeholders}):
        slide = presentation.Slides(slideNumber)
        onSlide = [item for item in placeholders if item.slideNumber == slideNumber]

        for shapeName in sorted({item.shapeName for item in onSlide}):
            wanted = [item.key for item in onSlide if item.shapeName == shapeName]

            try:
                read = PlaceholderPattern.findall(slide.Shapes(shapeName).TextFrame.TextRange.Text)
            except pythoncom.com_error:
                raise PowerPointError(
                    f"PowerPoint finds no shape named {shapeName!r} on slide {slideNumber}, where the package"
                    f" holds the placeholders {wanted}"
                ) from None

            if read != wanted:
                raise PowerPointError(
                    f"PowerPoint reads the shape {shapeName!r} on slide {slideNumber} as the placeholders"
                    f" {read}, the package as {wanted}"
                )


def ReplaceShape(slide, placeholder: Placeholder, equation: str) -> Plan:
    """The whole-shape form: the shape goes and an object of the add-in's class takes its left and top.

    The corner is the shape's, not the object's: `AddOLEObject` puts the object on the nearest eighth of a
    point, and it is the shape's own left and top that the deck promises.
    """

    shape = slide.Shapes(placeholder.shapeName)
    left = shape.Left
    top = shape.Top
    shape.Delete()
    InsertObject(slide, left, top, placeholder.key)

    return Plan(placeholder.key, placeholder.slideNumber, ShapeForm, left, top, equation, None)


def InsertObject(slide, left: float, top: float, key: str) -> None:
    """One empty object of the add-in's class on one corner, named after its key."""

    inserted = slide.Shapes.AddOLEObject(Left=left, Top=top, ClassName=ObjectClass)
    progId = inserted.OLEFormat.ProgID

    if progId != ObjectClass:
        raise PowerPointError(f"PowerPoint inserted an object of class {progId!r} for the equation {key}")

    # The size before the activation is the blank's, and the guard below compares against those two numbers.
    if (inserted.Width, inserted.Height) != BlankShapeSize:
        raise PowerPointError(
            f"the object inserted for the equation {key} stands at {inserted.Width} by {inserted.Height}"
            f" points, not the blank {BlankShapeSize[0]} by {BlankShapeSize[1]}"
        )

    inserted.Name = key


def InlineShapes(placeholders: list) -> list:
    """The text shapes that hold inline placeholders, in the order their placeholders come in."""

    shapes = []

    for placeholder in placeholders:
        entry = (placeholder.slideNumber, placeholder.shapeName)

        if placeholder.inline and entry not in shapes:
            shapes.append(entry)

    return shapes


def UngroupedShapes(placeholders: list) -> set:
    """The text shapes whose objects are left beside them, which are the layout's own placeholders."""

    return {
        (placeholder.slideNumber, placeholder.shapeName)
        for placeholder in placeholders
        if placeholder.inline and placeholder.layoutPlaceholder
    }


def InlineGeometries(presentation, placeholders: list, equations: dict, deadline: float) -> dict:
    """Every inline equation's font, size and render, keyed by the placeholder's own place in the list.

    The size is the run's own drawn font size as COM reports it, which is what an empty design block takes
    for an inline equation (ADR-0013): the equation belongs to the sentence, where a whole-shape one takes
    the slide's body size. `PlaceholderCharacter` reports the size on the slide rather than the size the
    package holds, and the autofit that would shrink it is off by the time this runs, so nothing here
    computes with the deck's own scale.

    The render is what the gap's width and the object's top need before the object exists: `Shape.Width` is
    known only once Radical Pie has drawn the object, and the depth is not known from PowerPoint at all. One
    render serves every gap that carries the same equation text, because the same text draws the same picture.
    """

    geometry = {}
    rendered = {}

    for index, placeholder in enumerate(placeholders):
        if not placeholder.inline:
            continue

        presentation.Windows(1).View.GotoSlide(placeholder.slideNumber)
        shape = presentation.Slides(placeholder.slideNumber).Shapes(placeholder.shapeName)
        character = PlaceholderCharacter(shape, placeholder)
        font = character.Font.Name
        fontSize = character.Font.Size

        if Inline.AscentShare(font) is None:
            raise PowerPointError(
                f"the run that holds {{{{pie:{placeholder.key}}}}} in the shape {placeholder.shapeName!r} on"
                f" slide {placeholder.slideNumber} is drawn in {font!r}, and this machine has neither a font"
                " file nor a measured baseline for it, so the equation cannot be put on the text baseline"
            )

        equation = WithBaseFontSize(EquationBody(equations[placeholder.key]), f"{fontSize:g}").decode("utf-8")

        if equation not in rendered:
            rendered[equation] = RenderEquation(equation, placeholder, deadline)

        info = rendered[equation]
        geometry[index] = InlineEquation(
            font, fontSize, equation, Inline.DrawnWidth(info.width), info.height, info.baselineShift
        )

    return geometry


def RenderEquation(equation: str, placeholder: Placeholder, deadline: float):
    """One inline equation rendered through Radical Pie for its width, its height and its depth.

    `Tools.Render.Svg` starts a Radical Pie of its own with the equation as a file argument and ends it; it is
    not the OLE server the activation of pass three drives, and neither run sees the other. The SVG is thrown
    away: what the placement needs is the geometry of the `<svg>` element, whose height already contains the
    depth and whose depth is how far the equation hangs below its own baseline.
    """

    with tempfile.TemporaryDirectory(prefix="RadicalPieInline") as workDirectory:
        seconds = max(min(deadline - time.monotonic(), RenderSeconds), 1.0)

        try:
            return RenderSvg(equation, Path(workDirectory) / "Equation.svg", seconds)
        except RenderError as error:
            raise PowerPointError(
                f"Radical Pie did not render the equation {placeholder.key} on slide"
                f" {placeholder.slideNumber}, whose size the inline gap needs before the object is"
                f" inserted: {error}"
            ) from None


def PlaceholderSpans(text: str, items: list) -> list:
    """The one-based start and the length of each placeholder in the text PowerPoint reads.

    PowerPoint gives a paragraph mark as one `\\r` and a line break as one `\\v`, so a character index is a
    position in that string and a paragraph is what `\\r` separates.
    """

    paragraphs = text.split("\r")
    spans = []

    for item in items:
        body = paragraphs[item.paragraph - 1] if item.paragraph <= len(paragraphs) else ""
        matches = list(PlaceholderPattern.finditer(body))

        if len(matches) < item.ordinal or matches[item.ordinal - 1].group(1) != item.key:
            raise PowerPointError(
                f"PowerPoint reads paragraph {item.paragraph} of the shape {item.shapeName!r} on slide"
                f" {item.slideNumber} as {body!r}, which does not hold {item.key} as its placeholder"
                f" number {item.ordinal}"
            )

        match = matches[item.ordinal - 1]
        start = sum(len(paragraph) + 1 for paragraph in paragraphs[: item.paragraph - 1])
        spans.append((start + match.start() + 1, len(match.group(0))))

    return spans


def LayOutShape(slide, shapeName: str, items: list, geometry: dict) -> dict:
    """One text shape: its placeholders become gaps, each gap takes a form, and the plans come back.

    `items` is the shape's inline placeholders as `(index, placeholder)` in text order, and the gaps are
    handled left to right, because the end of the text before one gap is known only once the gap before it
    holds its own stop.
    """

    shape = slide.Shapes(shapeName)
    frame = shape.TextFrame
    layout = ReplaceWithTabs(shape, items)
    origin = shape.Left + frame.MarginLeft
    # The width a tab stop has to stand inside, and nothing when the frame does not wrap: there the text runs
    # past the shape's own right edge and the stop is honoured wherever it is asked for (measured 2026-09-17).
    limit = shape.Width - frame.MarginLeft - frame.MarginRight if frame.WordWrap == MsoTrue else None
    forms = {}
    paddings = {}
    authorStops = {}
    gapStops = {}
    moved = set()

    for index, placeholder in items:
        equation = geometry[index]
        paddings[index] = PaddingOf(layout, index, equation.fontSize)
        gapWidth = equation.width + paddings[index].leading + paddings[index].trailing

        if limit is not None and not GapFitsOnItsLine(layout, index, origin, gapWidth, limit):
            CheckTheTextAreaHoldsTheEquation(placeholder, gapWidth, limit)
            MoveGapToNextLine(layout, index, placeholder)
            moved.add(index)

        if StopIsFree(layout, items, forms, placeholder, index):
            SetGapStop(layout, authorStops, gapStops, index, placeholder, origin, gapWidth, limit)
            forms[index] = TabForm
        else:
            FillGap(layout, index, placeholder, gapWidth)
            forms[index] = SpaceForm

    openings = OpenParagraphs(layout, items, geometry)

    return Placements(layout, items, geometry, forms, paddings, openings, moved)


def GapFitsOnItsLine(layout: ShapeText, index: int, origin: float, gapWidth: float, limit: float) -> bool:
    """Whether the gap ends inside the text area on the line the text before it left it on."""

    preEnd, _, _ = GapEdges(layout, index)

    return preEnd - origin + gapWidth <= limit


def CheckTheTextAreaHoldsTheEquation(placeholder: Placeholder, gapWidth: float, limit: float) -> None:
    """An equation wider than the text area itself, which no line of the shape can hold.

    This is the one width the pipeline still refuses. Every other overflow is a word that does not fit on
    its line, and a word that does not fit goes to the next line.
    """

    if gapWidth <= limit:
        return

    raise PowerPointError(
        f"the equation {placeholder.key} in the shape {placeholder.shapeName!r} on slide"
        f" {placeholder.slideNumber} needs {gapWidth:.2f} points and the text area is {limit:.2f} points"
        " wide, so no line of that shape can hold it"
    )


def MoveGapToNextLine(layout: ShapeText, index: int, placeholder: Placeholder) -> None:
    """A line break written in front of one gap, so the equation starts the next line.

    Nobody can see where PowerPoint breaks a line before the run, which is what the cold start of
    2026-09-18 found: both wrapped sessions wrote a sentence whose equation landed too near the right edge
    and were refused, and the author had no way to know. A word that does not fit on its line goes to the
    next line, and so does an equation.

    The break is PowerPoint's own soft return, a vertical tab, which keeps the gap inside its paragraph and
    with it the paragraph's tab stops: on a wrapping frame at 18 pt the character after a tab on the line
    after a break landed at the origin plus the stop to the hundredth of a point, the line box stayed 21.60
    and the text after the break started at the text area's left edge (measured 2026-09-18).
    """

    start = layout.starts[index]
    length = layout.lengths[index]
    SetGapText(layout, index, "\v" + layout.text[start - 1 : start - 1 + length], placeholder)
    layout.starts[index] = start + 1
    layout.lengths[index] = length


def PaddingOf(layout: ShapeText, index: int, fontSize: float) -> GapPadding:
    """One gap's padding, dropped on a side a space or a punctuation mark stands on (the operator, 2026-09-18).

    "When a comma follows an inline equation, the comma should be typeset inside the equation not outside."
    The object floats in a gap with a thin space on each side, so a mark the author left in the text stands
    that thin space away from the equation it ends. Dropping the padding on the mark's own side puts the
    mark's left edge on the object's right edge, which is where the mark of an ordinary word stands.

    A space the author wrote beside the placeholder does the same to the padding, and for the same reason:
    the space is the gap the sentence gives a word, and the padding on top of it makes a gap of two.

    The characters either side of the gap are read from the text the pass holds rather than from PowerPoint,
    which is the same text and needs no COM call; the gap itself is one tab at this point, and a gap at the
    edge of its paragraph has no character on that side at all.
    """

    start = layout.starts[index]
    after = start + layout.lengths[index]
    before = layout.text[start - 2] if start > 1 else ""
    following = layout.text[after - 1] if after <= len(layout.text) else ""
    leading, trailing = Inline.GapPaddings(fontSize, before, following)
    dropped = []

    if not leading:
        dropped.append("beside the space" if before == Inline.Space else f"after {before!r}")

    if not trailing:
        dropped.append("beside the space" if following == Inline.Space else f"before {following!r}")

    return GapPadding(leading, trailing, f"no padding {' and '.join(dropped)}" if dropped else "")


def ReplaceWithTabs(shape, items: list) -> ShapeText:
    """Every placeholder of one shape replaced by a tab, with the character index of each tab recorded.

    The replacements go right to left, so the start of the next one is still where it was measured, and the
    text PowerPoint reads back is checked against the text this wrote: an index that has drifted puts an
    object somewhere else entirely.
    """

    text = shape.TextFrame.TextRange
    placeholders = [placeholder for _, placeholder in items]
    spans = PlaceholderSpans(text.Text, placeholders)
    wanted = text.Text

    for start, length in reversed(spans):
        wanted = wanted[: start - 1] + "\t" + wanted[start - 1 + length :]

    for start, length in reversed(spans):
        text.Characters(start, length).Text = "\t"

    CheckText(shape, wanted, placeholders[0])
    layout = ShapeText(shape, wanted)
    shift = 0

    for (index, _), (start, length) in zip(items, spans):
        layout.starts[index] = start - shift
        layout.lengths[index] = 1
        shift += length - 1

    return layout


def CheckText(shape, wanted: str, placeholder: Placeholder) -> None:
    """The text PowerPoint holds is the text the pass wrote, which every gap's character index stands on."""

    read = shape.TextFrame.TextRange.Text

    if read != wanted:
        raise PowerPointError(
            f"the shape {placeholder.shapeName!r} on slide {placeholder.slideNumber} reads {read!r} after a"
            f" gap was written into it, where the pipeline wrote {wanted!r}"
        )


def SetGapText(layout: ShapeText, index: int, fill: str, placeholder: Placeholder) -> None:
    """One gap's characters replaced by `fill`, with the gaps after it moved by what the change cost."""

    start = layout.starts[index]
    length = layout.lengths[index]
    layout.shape.TextFrame.TextRange.Characters(start, length).Text = fill
    wanted = layout.text[: start - 1] + fill + layout.text[start - 1 + length :]
    CheckText(layout.shape, wanted, placeholder)
    layout.text = wanted
    layout.lengths[index] = len(fill)

    for other, position in layout.starts.items():
        if position > start:
            layout.starts[other] = position + len(fill) - length


def GapEdges(layout: ShapeText, index: int) -> tuple:
    """Where the text before one gap ends, where the text after it starts, and the top of the gap's line.

    The character before the gap is what the line is read from: a range that covers more than one line reports
    the box of all of them where one character reports its own, and the gap's line is whatever line the
    character before it ended up on (measured 2026-09-17). A gap that starts a line has no such character, and
    then its own first character carries the line and its left is where the text before it ends, which is the
    left edge of the text area.

    The start of the text after the gap is `None` when the gap ends its paragraph and when what follows it
    stands on the next line, which is a stop the line could not hold and what the space fallback must know.
    """

    text = layout.shape.TextFrame.TextRange
    start = layout.starts[index]
    after = start + layout.lengths[index]

    if start > 1 and layout.text[start - 2] not in "\r\v":
        character = text.Characters(start - 1, 1)
        preEnd = character.BoundLeft + character.BoundWidth
        lineTop = character.BoundTop
    else:
        character = text.Characters(start, 1)
        preEnd = character.BoundLeft
        lineTop = character.BoundTop

    postStart = None

    if after <= len(layout.text) and layout.text[after - 1] not in "\r\v":
        following = text.Characters(after, 1)

        if abs(following.BoundTop - lineTop) <= Inline.SameLineTolerance:
            postStart = following.BoundLeft

    return preEnd, postStart, lineTop


def StopIsFree(layout: ShapeText, items: list, forms: dict, placeholder: Placeholder, index: int) -> bool:
    """Whether this gap can be held open by a tab stop of its own.

    The stops belong to the paragraph and not to the line, and a tab takes the first stop to its right: with
    two gaps on line 1 of a paragraph and one on line 2, the tab on line 2 took the stop of gap one and the
    text after gap three landed 31.02 pt left of its object, printed over the equation (measured 2026-09-17).
    So the first gap of a paragraph takes a stop and a later one only where it stands on the same line.
    """

    earlier = [
        other for other, item in items if item.paragraph == placeholder.paragraph and forms.get(other) == TabForm
    ]

    if not earlier:
        return True

    _, _, lineTop = GapEdges(layout, index)
    _, _, previousTop = GapEdges(layout, earlier[-1])

    return abs(lineTop - previousTop) <= Inline.SameLineTolerance


def SetGapStop(
    layout: ShapeText,
    authorStops: dict,
    gapStops: dict,
    index: int,
    placeholder: Placeholder,
    origin: float,
    gapWidth: float,
    limit: float,
) -> None:
    """One gap's tab stop, set again until the end of the text before it stands still.

    The stop stands at the end of the text before the gap plus the object's width plus twice the padding,
    measured from the shape's left plus the frame's left margin, which is the origin a left tab stop is taken
    from: over the second probe's 40 gaps the text after the gap landed at that origin plus the stop within
    0.025 pt in every case but the centred and the right-aligned one, and an indent moves the origin nothing.
    A body placeholder has a left margin of 7.2 pt, and a stop computed from the shape's left alone left
    10.08 pt beside the object instead of the 2.88 asked for.

    Setting the stop changes the width of the tab, which can move the line break and with it the text before
    the gap, so the measurement is taken again and the stop set again. Four passes is the whole budget: seven
    of the first probe's eight wrapped cases settled on the first, and a centred or right-aligned paragraph
    never settles, which is how one that inherits its alignment from its layout is refused here. The stops the
    author put in the paragraph go back with the gap's own: with a stop already at 200 pt and a tab using it,
    adding the gap's stop at 451.77 left the author's tab where it was.

    A stop past the width of a wrapping frame's text area is ignored altogether: the text after the gap starts
    at the left margin of the next line, the measurement settles because the text before the gap never moves,
    and the object lands outside the box. On the first pass of this feature's own acceptance deck an object
    stood at left 505.4 in a shape running from 40 to 540 that way (measured 2026-09-17, and the first probe's
    `narrowB` case before it). There is nothing to place in that line, so it is refused.
    """

    if placeholder.paragraph not in authorStops:
        authorStops[placeholder.paragraph] = Inline.ParagraphStops(layout.shape, placeholder.paragraph)

    ours = gapStops.setdefault(placeholder.paragraph, {})
    settled = False

    for _ in range(Inline.StopAttempts):
        preEnd, _, _ = GapEdges(layout, index)
        ours[index] = preEnd - origin + gapWidth

        if limit is not None and ours[index] > limit:
            raise PowerPointError(
                f"the line that holds {{{{pie:{placeholder.key}}}}} in the shape {placeholder.shapeName!r} on"
                f" slide {placeholder.slideNumber} has no room for the equation: the gap would end"
                f" {ours[index]:.2f} points into a text area {limit:.2f} points wide"
            )

        Inline.SetParagraphStops(
            layout.shape, placeholder.paragraph, authorStops[placeholder.paragraph] + list(ours.values())
        )
        moved, _, _ = GapEdges(layout, index)
        settled = abs(moved - preEnd) <= Inline.StopTolerance

        if settled:
            break

    if not settled:
        raise PowerPointError(
            f"the text before {{{{pie:{placeholder.key}}}}} in the shape {placeholder.shapeName!r} on slide"
            f" {placeholder.slideNumber} keeps moving as the gap's tab stop is set, through"
            f" {Inline.StopAttempts} passes; a centred or right-aligned paragraph does that, and so does a"
            " line with no room left for the equation"
        )


def FillGap(layout: ShapeText, index: int, placeholder: Placeholder, gapWidth: float) -> None:
    """One gap held open by spaces, for a gap on a line that cannot have a stop of its own.

    Ordinary spaces up to the last one that fits in the width, then thin spaces, because a thin space is about
    a fifth of an em where an ordinary space is about a quarter and the gap has to reach the width rather than
    land on it. The object is centred in what the fill came to, which `Placements` reads off the text either
    side of it.

    Text that leaves the gap's line as the fill grows is the gap reaching the end of that line, which is what
    a word too long for the room left does. The fill stops there and the object stands at its start, the last
    thing on its own line, because the line was already checked to have room for the equation itself.
    """

    SetGapText(layout, index, " ", placeholder)
    preEnd, postStart, _ = GapEdges(layout, index)
    unit = 0.0 if postStart is None else postStart - preEnd
    fill = " " * (max(1, int(gapWidth // unit)) if unit > 0 else 1)

    for _ in range(FillAttempts):
        SetGapText(layout, index, fill, placeholder)
        preEnd, postStart, _ = GapEdges(layout, index)

        if postStart is None or postStart - preEnd >= gapWidth:
            return

        fill += ThinSpace

    raise PowerPointError(
        f"the gap for {{{{pie:{placeholder.key}}}}} in the shape {placeholder.shapeName!r} on slide"
        f" {placeholder.slideNumber} did not reach the {gapWidth:.2f} points the equation needs in"
        f" {FillAttempts} fills"
    )


def ParagraphSpans(text: str) -> list:
    """The one-based first and last character index of every paragraph, the paragraph marks left out.

    An empty paragraph comes back with its last index one below its first, which is what says it holds no
    character to measure.
    """

    spans = []
    start = 1

    for body in text.split("\r"):
        spans.append((start, start + len(body) - 1))
        start += len(body) + 1

    return spans


def CharacterTop(text, index: int):
    """The top of the line one character stands on."""

    return text.Characters(index, 1).BoundTop


def MeasureGap(layout: ShapeText, index: int, placeholder: Placeholder, equation: InlineEquation) -> GapGeometry:
    """One gap as PowerPoint lays it out now: the text either side of it, its line box and three baselines.

    The baseline follows the line box, and the paragraph's space before stands inside the first line's box
    above it: 26 pt before a two-line paragraph grew the box from 21.60 to 47.60 and put the baseline 42.88
    below its top where the font alone puts it at 16.94, and PowerPoint drops the space on the first paragraph
    of a text frame (measured 2026-09-17). The space after moves no baseline at all.

    The baseline of the line above and of the line below come from the pitch inside the paragraph, which is
    its own line box, or from the neighbouring paragraph when the gap stands on the first or the last line.
    Either is `None` where the frame has no line on that side: above the first line of the first paragraph
    and below the last line of the last, the equation reaches out of the text frame, where there is nothing
    to collide with and nothing to open.
    """

    text = layout.shape.TextFrame.TextRange
    preEnd, postStart, lineTop = GapEdges(layout, index)
    spans = ParagraphSpans(layout.text)
    start, end = spans[placeholder.paragraph - 1]
    paragraphFormat = Inline.ReadParagraphFormat(layout.shape, placeholder.paragraph)
    box = Inline.LineBox(equation.fontSize, paragraphFormat.spaceWithin, paragraphFormat.lineRuleWithin)
    offset = Inline.BaselineOffset(equation.fontSize, Inline.AscentShare(equation.font), box)
    spaceBefore = Inline.SpacePoints(paragraphFormat.spaceBefore, paragraphFormat.lineRuleBefore, equation.fontSize)
    spaceAfter = Inline.SpacePoints(paragraphFormat.spaceAfter, paragraphFormat.lineRuleAfter, equation.fontSize)
    ascender, descender = Inline.InkRoom(equation.font, equation.fontSize)
    firstLine = abs(lineTop - CharacterTop(text, start)) <= Inline.SameLineTolerance
    lastLine = abs(lineTop - CharacterTop(text, end)) <= Inline.SameLineTolerance
    spaceAbove = spaceBefore if firstLine and placeholder.paragraph > 1 else 0.0
    baseline = lineTop + spaceAbove + offset

    if not firstLine:
        aboveBaseline = baseline - box
    else:
        aboveBaseline = NeighbourBaseline(layout, spans, placeholder.paragraph - 1, True, equation)

    if not lastLine:
        belowBaseline = baseline + box
    elif placeholder.paragraph < len(spans):
        belowBaseline = NeighbourBaseline(layout, spans, placeholder.paragraph + 1, False, equation)
    else:
        belowBaseline = None

    return GapGeometry(
        preEnd,
        postStart,
        lineTop,
        box,
        spaceAbove,
        spaceBefore,
        spaceAfter,
        baseline,
        firstLine,
        lastLine,
        aboveBaseline,
        belowBaseline,
        descender,
        ascender,
    )


def MeasureGaps(layout: ShapeText, items: list, geometry: dict) -> dict:
    """Every gap of one shape as PowerPoint lays it out now, with the ink of each neighbouring line in it.

    Taken in one sweep rather than one gap at a time, because a line's ink is not the font's alone: an
    inline equation of this run standing on the line above or below inks as far as it stands from its own
    baseline, and only the whole sweep knows where the other equations of the shape came out.
    """

    gaps = {index: MeasureGap(layout, index, placeholder, geometry[index]) for index, placeholder in items}

    return {index: WithNeighbouringEquations(gaps, geometry, index) for index in gaps}


def WithNeighbouringEquations(gaps: dict, geometry: dict, index: int) -> GapGeometry:
    """One gap with the ink of its neighbouring lines raised by the equations of this run standing on them.

    The cold start of 2026-09-18 found the hole: the rule read the text ink of the line above and below, so
    two stacked fractions on consecutive bullets each cleared the other's text and ran into the other's
    equation (`radical-pie-workspace/coldstart-3/opus-bullets/RadicalPieFeedback.md`). A gap stands on the
    line above when its baseline is that line's baseline, which is what the two are matched by.
    """

    gap = gaps[index]
    aboveInk = gap.aboveInk
    belowInk = gap.belowInk

    for other, neighbour in gaps.items():
        if other == index:
            continue

        equation = geometry[other]

        if gap.aboveBaseline is not None and abs(neighbour.baseline - gap.aboveBaseline) <= Inline.SameLineTolerance:
            aboveInk = max(aboveInk, equation.depth)

        if gap.belowBaseline is not None and abs(neighbour.baseline - gap.belowBaseline) <= Inline.SameLineTolerance:
            belowInk = max(belowInk, equation.height - equation.depth)

    return replace(gap, aboveInk=aboveInk, belowInk=belowInk)


def NeighbourBaseline(layout: ShapeText, spans: list, paragraph: int, last: bool, equation: InlineEquation):
    """The baseline of the last or the first line of a neighbouring paragraph, or `None` when it has no text.

    The neighbour's own line box and space before are read from the neighbour; the font size and the ascent
    share are the gap's own, because a neighbour of another size moves this by a fraction of a point where the
    opening it feeds is asked for in whole points. An empty paragraph carries no character to measure and no
    ink to collide with, so it counts as no neighbour at all.
    """

    if paragraph < 1 or paragraph > len(spans):
        return None

    start, end = spans[paragraph - 1]

    if end < start:
        return None

    text = layout.shape.TextFrame.TextRange
    firstTop = CharacterTop(text, start)
    top = CharacterTop(text, end) if last else firstTop
    paragraphFormat = Inline.ReadParagraphFormat(layout.shape, paragraph)
    box = Inline.LineBox(equation.fontSize, paragraphFormat.spaceWithin, paragraphFormat.lineRuleWithin)
    offset = Inline.BaselineOffset(equation.fontSize, Inline.AscentShare(equation.font), box)
    space = 0.0

    if paragraph > 1 and abs(top - firstTop) <= Inline.SameLineTolerance:
        space = Inline.SpacePoints(paragraphFormat.spaceBefore, paragraphFormat.lineRuleBefore, equation.fontSize)

    return top + space + offset


def Deficits(gap: GapGeometry, equation: InlineEquation) -> tuple:
    """How far the equation reaches into the clearance around the ink above and below it, in points.

    Measured baseline to baseline and not against the line box, because an inline object leaves its own box
    long before it touches a neighbour: at 80 pt spacing the box gives 60 pt above the baseline and 20 below
    where the second probe's tall equation needs 41 and 36, and it still cleared the line above by 38.94 pt
    and the line below by 31.72 (measured 2026-09-17). What has to hold is that the equation reaches no
    further up than the ink of the line above, its baseline plus that line's ink depth, and no further down
    than the ink of the line below, its baseline less that line's ink height, with `Inline.Clearance` left
    between the two inks either way.

    The ink of a neighbouring line is the font's own until an inline equation of this run stands on it, and
    then it is the further of the two, which `WithNeighbouringEquations` puts into the gap. The room that
    leaves, the line's own box less the ink in it and less the clearance, is what an equation may intrude by
    before a paragraph is opened for it. A line with no line on that side of it is no constraint at all:
    above the first line of a text frame and below its last there is nothing to collide with, and the
    equation reaches out of the frame, which no text box clips.
    """

    clearance = Inline.Clearance(equation.fontSize)
    above = 0.0
    below = 0.0

    if gap.aboveBaseline is not None:
        above = (equation.height - equation.depth) + gap.aboveInk + clearance - (gap.baseline - gap.aboveBaseline)

    if gap.belowBaseline is not None:
        below = equation.depth + gap.belowInk + clearance - (gap.belowBaseline - gap.baseline)

    return above, below


def OpenParagraphs(layout: ShapeText, items: list, geometry: dict) -> dict:
    """The paragraphs a tall equation has no room in opened, with a line each saying what was set.

    A paragraph is opened by what the equation reaches into the neighbouring line's ink and clearance by,
    rounded up to a whole point, and nothing is opened for an equation that clears that ink or stands at the
    edge of the text frame, which is what `Deficits` measures.

    Which of the two openings a need takes follows the line the gap stands on. An exact line spacing where
    the line above or below belongs to the paragraph itself, because neither paragraph space reaches inside
    a paragraph; it is asked for in whole points, because PowerPoint lays an exact spacing out at the
    spacing rounded to a whole point, half up. Space after the earlier of two paragraphs where the need
    stands between them, whichever of the two asked for it, because the space after one paragraph and the
    space before the next both stand in that one gap and setting both opens it twice: two tall equations on
    consecutive bullets each need the same room between their two baselines, so the gap takes the larger of
    the two needs and not their sum.
    """

    gaps = MeasureGaps(layout, items, geometry)
    spacings, boundaries = Openings(items, gaps, geometry)
    fontSize = geometry[items[0][0]].fontSize

    return ApplyOpenings(layout, items, spacings, boundaries, fontSize)


def Openings(items: list, gaps: dict, geometry: dict) -> tuple:
    """The line spacing each paragraph asks for and the space each paragraph boundary asks for, in points.

    A boundary is named by the earlier of its two paragraphs and takes the larger of the needs the two sides
    put on it, because both sides are asking for the one gap between their two baselines.
    """

    spacings = {}
    boundaries = {}

    for index, placeholder in items:
        gap = gaps[index]
        above, below = Deficits(gap, geometry[index])
        paragraph = placeholder.paragraph

        if above > 0 and gap.firstLine:
            boundaries[paragraph - 1] = max(boundaries.get(paragraph - 1, 0.0), above)
        elif above > 0:
            spacings[paragraph] = max(spacings.get(paragraph, 0.0), math.ceil(gap.box + above))

        if below > 0 and gap.lastLine:
            boundaries[paragraph] = max(boundaries.get(paragraph, 0.0), below)
        elif below > 0:
            spacings[paragraph] = max(spacings.get(paragraph, 0.0), math.ceil(gap.box + below))

    return spacings, boundaries


def ApplyOpenings(layout: ShapeText, items: list, spacings: dict, boundaries: dict, fontSize: float) -> dict:
    """The line spacings and the paragraph spaces set, with the line the run prints for each paragraph.

    A boundary's space is set on the earlier of its two paragraphs, on top of the space the author already
    gave it, and the line that says so belongs to both of them, so the gap on either side of the boundary
    carries it.
    """

    slideNumber = items[0][1].slideNumber
    shapeName = items[0][1].shapeName
    changes = {}

    for paragraph, spacing in sorted(spacings.items()):
        Inline.SetExactSpacing(layout.shape, paragraph, spacing)
        line = f"slide {slideNumber}, the shape {shapeName!r}, paragraph {paragraph}: line spacing {spacing:g} pt"
        changes.setdefault(paragraph, []).append(line)

    for paragraph, need in sorted(boundaries.items()):
        paragraphFormat = Inline.ReadParagraphFormat(layout.shape, paragraph)
        already = Inline.SpacePoints(paragraphFormat.spaceAfter, paragraphFormat.lineRuleAfter, fontSize)
        points = already + math.ceil(need)
        Inline.SetSpaceAfter(layout.shape, paragraph, points)
        line = f"slide {slideNumber}, the shape {shapeName!r}, after paragraph {paragraph}: space after {points:g} pt"
        changes.setdefault(paragraph, []).append(line)
        changes.setdefault(paragraph + 1, []).append(line)

    return {paragraph: "; ".join(lines) for paragraph, lines in changes.items()}


def Placements(
    layout: ShapeText, items: list, geometry: dict, forms: dict, paddings: dict, openings: dict, moved: set
) -> dict:
    """Where every object of one shape goes, measured after the text and the spacing are final.

    The left is the end of the text before the gap plus the gap's own leading padding for a gap held open by a
    stop, and `FillLeft` for one held open by spaces. The top is the baseline less what the equation stands
    above its own baseline, which the render gives as `height - depth`: the height already contains the depth,
    so adding the two would count it twice.
    """

    gaps = MeasureGaps(layout, items, geometry)
    plans = {}
    reported = set()

    for index, placeholder in items:
        equation = geometry[index]
        gap = gaps[index]
        above, below = Deficits(gap, equation)

        if max(above, below) > OpeningTolerance:
            raise PowerPointError(
                f"the equation {placeholder.key} on slide {placeholder.slideNumber} stands"
                f" {equation.height - equation.depth:g} points above its baseline and {equation.depth:g}"
                f" below it, and its paragraph is still {max(above, below):.2f} points too tight after it was"
                " opened"
            )

        if forms[index] == TabForm:
            left = gap.preEnd + paddings[index].leading
        else:
            left = FillLeft(gap, equation, paddings[index])

        note = openings.get(placeholder.paragraph, "")
        plans[index] = Plan(
            placeholder.key,
            placeholder.slideNumber,
            forms[index],
            left,
            gap.baseline - (equation.height - equation.depth),
            equation.equation,
            equation.width,
            "" if note in reported else note,
            paddings[index].note,
            MovedNote if index in moved else "",
        )
        reported.add(note)

    return plans


def FillLeft(gap: GapGeometry, equation: InlineEquation, padding: GapPadding) -> float:
    """Where an object stands in a gap of spaces: what the fill has over the object, split by the two paddings.

    With a padding on each side that is the middle of the fill, which is where the space fallback has always
    put the object. With the padding on one side dropped for a mark the whole of it goes to the other side, so
    the mark stands at the object's edge here as it does under a tab stop. A mark on each side leaves nothing
    to split by and the object stands in the middle again.

    A fill whose following text wrapped to the next line has no far edge to split: the gap runs to the end of
    the line and the object stands at its start, which is where a word at the end of a line stands.
    """

    if gap.postStart is None:
        return gap.preEnd + padding.leading

    over = gap.postStart - gap.preEnd - equation.width
    share = padding.leading + padding.trailing

    return gap.preEnd + over * (padding.leading / share if share else 0.5)


def ReplaceEquationStreams(deckPath: Path, placeholders: list, equations: list) -> None:
    """Pass two: the equations into the `RP` streams, with PowerPoint closed.

    A whole-shape equation whose design block is empty takes the base font size PowerPoint's insertion wrote
    into the object it created, so it is drawn at the size of the slide's body text. An inline equation
    arrives here with the run's own size already written into it by pass one, which is a design block that is
    no longer empty and so is left as it stands (ADR-0013).
    """

    with zipfile.ZipFile(deckPath) as package:
        parts = ReadObjectParts(package)
        contents = [(entry, package.read(entry.filename)) for entry in package.infolist()]

    CheckObjectParts(parts, placeholders)

    sources = {entry.filename: data for entry, data in contents}
    objects = {(part.slideNumber, part.name): part for part in parts}
    replacements = {}

    for placeholder, equation in zip(placeholders, equations):
        part = objects[(placeholder.slideNumber, placeholder.key)]
        embedding = sources[part.embeddingPart]
        body = WithBaseFontSize(EquationBody(equation), BaseFontSize(embedding, placeholder))
        replacements[part.embeddingPart] = RebuildEmbedding(embedding, body)

    with zipfile.ZipFile(deckPath, "w", zipfile.ZIP_DEFLATED) as target:
        for entry, data in contents:
            target.writestr(entry, replacements.get(entry.filename, data))


def CheckObjectParts(parts: list, placeholders: list) -> None:
    """The objects the deck holds are this pipeline's, one per placeholder, on the slide the placeholder was.

    The objects are compared as a sorted list and not in the order the package lists them: a grouped slide
    holds its frames in the group's own order, which is not the order the objects were inserted in (measured
    2026-09-17), and every step here addresses an object by its slide and its name.
    """

    inserted = sorted((part.slideNumber, part.name) for part in parts)
    expected = sorted((item.slideNumber, item.key) for item in placeholders)

    if inserted != expected:
        raise PowerPointError(f"the deck holds the objects {inserted}, expected {expected}")


def BaseFontSize(embedding: bytes, placeholder: Placeholder) -> str:
    """The `fsiz` of the design PowerPoint's insertion wrote, which is the slide layout's body text size."""

    with olefile.OleFileIO(io.BytesIO(embedding)) as container:
        design = container.openstream(EquationStream).read().decode("utf-8")

    found = BaseFontSizePattern.search(design)

    if found is None:
        raise PowerPointError(
            f"the object inserted for the equation {placeholder.key} on slide {placeholder.slideNumber}"
            " carries no base font size, so the slide's body text size is not known"
        )

    return found.group(1)


def WithBaseFontSize(body: bytes, fontSize: str) -> bytes:
    """`body` with `fontSize` as its base font size, when the caller left the design block empty.

    An equation that carries a design of its own is returned untouched: the design belongs to the document,
    and a caller who wrote one has said what size the equation is.
    """

    text = body.decode("utf-8")
    match = EmptyDesignPattern.match(text)

    if match is None:
        return body

    return ((BaseFontSizeDesign % fontSize) + text[match.end() :]).encode("utf-8")


def RebuildEmbedding(embedding: bytes, body: bytes) -> bytes:
    """The embedding with `body` as its `RP` stream and PowerPoint's cached picture dropped.

    The compound file is rebuilt rather than patched, because the equation is not the size of the empty one
    PowerPoint's insertion put there and a stream cannot grow in place.
    """

    with olefile.OleFileIO(io.BytesIO(embedding)) as container:
        names = ["/".join(entry) for entry in container.listdir(streams=True)]
        streams = [
            (name, container.openstream(name).read())
            for name in names
            if name != EquationStream and not name.startswith(PresentationStreamPrefix)
        ]

    streams.append((EquationStream, body))

    with tempfile.TemporaryDirectory(prefix="RadicalPieEmbedding") as workDirectory:
        path = str(Path(workDirectory) / "Embedding.bin")
        storage = pythoncom.StgCreateDocfile(path, StgmCreateReadWriteExclusive)
        pythoncom.WriteClassStg(storage, pywintypes.IID(ObjectClassId))

        for name, data in streams:
            stream = storage.CreateStream(name, StgmCreateWriteExclusive, 0, 0)
            stream.Write(data)
            stream.Commit(0)
            stream = None

        storage.Commit(0)
        storage = None

        return Path(path).read_bytes()


def RenderObjects(deckPath: Path, placeholders: list, plans: list, deadline: float) -> list:
    """Pass three: activate each object so Radical Pie draws it, put it on its corner, and report both.

    An object is put on its corner as soon as its own drawing has arrived, because that is when PowerPoint has
    moved it: the drawing grows the object about its centre and leaves the corner it was inserted on.

    An inline object's gap was opened for the width pass one predicted from the render, so the width it comes
    out at is checked against that prediction: a wider object would stand over the text after the gap.

    The first half of the collapse guard stands between the last activation and the save: an object that shows
    the blank when the deck is written is a collapse, whatever it showed a moment earlier. The grouping is a
    pass of its own after this one, for the reason `GroupObjects` gives.
    """

    drawn = []

    with PowerPointSession(deadline) as session:
        try:
            presentation = OpenDeck(session, deckPath)
            presentation.Windows(1).ViewType = PpViewNormal

            for placeholder, plan in zip(placeholders, plans):
                width, height = RenderObject(session, presentation, deckPath, placeholder, deadline)
                CheckDrawnWidth(width, plan, placeholder)
                shape = presentation.Slides(placeholder.slideNumber).Shapes(placeholder.key)
                shape.Left = plan.left
                shape.Top = plan.top
                drawn.append(DrawnObject(width, height, plan.left, plan.top))

            CheckShapes(presentation, placeholders)
            presentation.Save()
            CloseDeck(presentation)
        except pythoncom.com_error as error:
            raise PowerPointError(session.Explain("activating the objects", error)) from None

    return drawn


def CheckDrawnWidth(width: float, plan: Plan, placeholder: Placeholder) -> None:
    """An inline object came out the width its gap was opened for, within an eighth of a point.

    Pass one opens the gap for the render's width on the nearest eighth of a point, which is the extent
    PowerPoint gives a shape for a picture of that frame (369 of 369 unscaled shapes of the operator's deck,
    2026-09-13). An object wider than that stands over the text after the gap, so the difference fails the
    deck rather than reaching it.
    """

    # COM hands an extent over in single precision, 75.875 read as 75.87496185302734 (the first inline probe),
    # and the cold start of 2026-09-18 had 28.125 against a gap of 28 fail a bare eighth. The padding either
    # side of the object, 0.16 of the size, holds an eighth many times over.
    if plan.form == ShapeForm or abs(width - plan.width) <= DrawnWidthTolerance:
        return

    raise PowerPointError(
        f"the equation {placeholder.key} on slide {placeholder.slideNumber} came out {width:g} points wide"
        f" where its gap was opened for {plan.width:g}, so the text after it would stand over the equation"
    )


def GroupObjects(deckPath: Path, placeholders: list, deadline: float) -> None:
    """Pass four: every text shape that kept an inline equation grouped with the objects in its sentence.

    The group is what holds a sentence and its equations together: a PowerPoint object floats over the slide
    and follows no text, so moving the text shape alone would leave the equations behind. A group moved 60 pt
    to the right moved its text shape and both its objects by exactly 60, with every top unchanged (measured
    2026-09-17).

    It takes a session of its own, after pass three has saved the drawings. Grouped inside the session that
    activated the objects, PowerPoint answered `Presentation.Close` with `0x80020009 Failed` and left two
    Radical Pie servers running (measured 2026-09-17, eight objects); grouping a deck that is already on disk
    in a session that activated nothing is the route the second probe measured, and it closes. Whatever server
    the grouping does start is ended here: pass three ends the editors it opened by the window it found them
    by, so a server alive after this step is this step's, and only one agent drives Radical Pie at a time.

    A layout's own placeholder is left ungrouped and its objects stand beside it. PowerPoint answers a
    selection that holds one with "Grouping is disabled for the selected shapes", which is where both bullet
    decks of the cold start of 2026-09-18 died after every equation had been drawn. The equations are placed
    in it exactly as in any other text shape; only the group is skipped, and `UngroupedShapes` names it.

    A deck with no inline equation is not opened at all, which is what keeps the whole-shape form at the two
    sessions it has always taken.
    """

    shapes = [entry for entry in InlineShapes(placeholders) if entry not in UngroupedShapes(placeholders)]

    if not shapes:
        return

    running = Pids(ServerImage)

    try:
        with PowerPointSession(deadline) as session:
            try:
                presentation = OpenDeck(session, deckPath)
                presentation.Windows(1).ViewType = PpViewNormal

                for slideNumber, shapeName in shapes:
                    presentation.Windows(1).View.GotoSlide(slideNumber)
                    keys = [
                        item.key
                        for item in placeholders
                        if item.inline and (item.slideNumber, item.shapeName) == (slideNumber, shapeName)
                    ]
                    presentation.Slides(slideNumber).Shapes.Range([shapeName] + keys).Group()
                    session.CheckDialogs()

                presentation.Save()
                CloseDeck(presentation)
            except pythoncom.com_error as error:
                raise PowerPointError(session.Explain("grouping the shapes with their equations", error)) from None
    finally:
        EndServers(running, deadline)


def EndServers(running: set, deadline: float) -> None:
    """Every Radical Pie that appeared while the grouping ran, ended by the tooling that caused it."""

    for pid in sorted(Pids(ServerImage) - running):
        Processes.Register(pid)
        EndProcess(pid, min(ExitGraceSeconds, max(deadline - time.monotonic(), 0.0)))


def RenderObject(session, presentation, deckPath: Path, placeholder: Placeholder, deadline: float) -> tuple:
    """Draw one object, retrying the activation once, and return the size PowerPoint ends up with."""

    failures = []

    for attempt in range(ActivationAttempts):
        if attempt:
            time.sleep(ActivationSettleSeconds)

        try:
            return AttemptActivation(session, presentation, deckPath, placeholder, deadline)
        except PowerPointError as error:
            failures.append(str(error))

    raise PowerPointError(
        f"Radical Pie did not draw the equation {placeholder.key} on slide {placeholder.slideNumber}"
        f" in {ActivationAttempts} activations: {Attempts(failures)}"
    )


def AttemptActivation(session, presentation, deckPath: Path, placeholder: Placeholder, deadline: float) -> tuple:
    """Activate one object, save it from the editor, close the editor, and return the size it ends up with.

    The window is taken to the object's own slide first. `OLEFormat.Activate` answers
    `0x80020009 / Invalid request. The window must be in slide or notes view.` for an object that is not on
    the slide the document window shows, measured 2026-09-13 on the second slide of a two-slide deck.
    """

    presentation.Windows(1).View.GotoSlide(placeholder.slideNumber)
    slide = presentation.Slides(placeholder.slideNumber)
    shape = slide.Shapes(placeholder.key)

    with ServerWatch() as watch:
        ActivateObject(shape)
        session.CheckDialogs()

        pid, window = AwaitEditor(deckPath, watch, placeholder, deadline)
        QuietenEditor(window)

    try:
        AwaitPresentation(slide, placeholder, pid, window, deadline)
    finally:
        PostToEditor(window, win32con.WM_CLOSE, 0)
        EndProcess(pid, min(ExitGraceSeconds, max(deadline - time.monotonic(), 0.0)))

    shape = slide.Shapes(placeholder.key)

    return (shape.Width, shape.Height)


def ActivateObject(shape) -> None:
    """Open the Radical Pie editor on one object, by the verb a grouped object accepts where it has to.

    `OLEFormat.Activate` is what an object standing on a slide takes. Inside a group it is refused with
    `0x80020009 Invalid request. Controls cannot be activated.`, where `OLEFormat.DoVerb(0)` is accepted and
    opens the same editor window (measured 2026-09-17). This pipeline groups a shape with its objects only
    after every one of them has been drawn, so the second call is what an object already inside a group needs.
    """

    try:
        shape.OLEFormat.Activate()
    except pythoncom.com_error:
        shape.OLEFormat.DoVerb(0)


class ServerWatch:
    """Every Radical Pie that appears from before an activation until its editor has been found.

    PowerPoint answers the activation of an object whose `RP` the server cannot read only once that server has
    gone. Measured on 2026-09-19 against PowerPoint 16 and Radical Pie 1.15, with the process listing polled
    from a thread of its own: the server started 31 ms after `OLEFormat.Activate` was entered, lived 1.75
    seconds and exited 16 ms before the call returned. A listing read once the call is back therefore holds
    nothing of it, and the pass reported that Radical Pie had never started for an equation it had in fact
    read and refused. An activation that succeeds returns while its server runs, 280 ms after it started, so
    one thread polling from before the call covers both.

    `candidates` is rebound rather than added to, because the pass reads it on its own thread while this one
    polls.
    """

    def __init__(self):
        self.running = Pids(ServerImage)
        self.candidates = set()
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.Poll, daemon=True)

    def __enter__(self):
        self.thread.start()

        return self

    def __exit__(self, exceptionType, exceptionValue, traceback):
        self.stop.set()
        self.thread.join()

        return False

    def Poll(self) -> None:
        while not self.stop.is_set():
            self.candidates = self.candidates | (Pids(ServerImage) - self.running)
            self.stop.wait(PollSeconds)


def AwaitEditor(deckPath: Path, watch: ServerWatch, placeholder: Placeholder, deadline: float) -> tuple:
    """The server this activation started and its editor window, as (pid, window), found by the title.

    Other agents render on this machine and each of their servers is new in the process listing in exactly
    the way this one is, so the pid comes from the window and not from the listing: the editor carries
    `Radical Pie - Equation in <the deck's file name>`, where a Radical Pie opened on a file carries
    `<the file name> - Radical Pie`. A server that leaves instead of showing that window could not read the
    equation, which is how an unreadable `RP` fails: it raises no dialog of its own. The candidates come from
    the watch and not from a listing read here, because such a server can have gone before this is entered.
    """

    title = EditorTitlePrefix + deckPath.name

    while time.monotonic() < deadline:
        candidates = watch.candidates

        for pid in sorted(candidates):
            windows = TopLevelWindows(pid)
            RaiseOnServerDialog(windows)

            for handle, className, windowTitle in windows:
                if className == WindowClass and windowTitle == title:
                    Processes.Register(pid)

                    return pid, handle

        if candidates and all(AwaitProcessExit(pid, 0) for pid in candidates):
            raise PowerPointError(
                f"Radical Pie left without an editor window for {placeholder.key}: {UnreadableEquation}"
            )

        time.sleep(PollSeconds)

    # `watch.candidates` and not the loop's own copy: a deadline already past leaves the loop unentered.
    if not watch.candidates:
        raise PowerPointError(f"Radical Pie did not start when the equation {placeholder.key} was activated")

    raise PowerPointError(f"Radical Pie did not show the editor window for the equation {placeholder.key}")


def AwaitPresentation(slide, placeholder: Placeholder, pid: int, window: int, deadline: float) -> None:
    """Post File > Save to the editor until PowerPoint has a drawing of the equation for the object.

    PowerPoint takes the new width and the new height together, where Word takes the height first and the
    width only when the editor closes. A size that is one of the two undrawn ones is not the drawing: the
    Save that arrives before the layout has run puts the zero-frame metafile on the slide at 0.75 by 0.75
    points, and the object stays that size for good once the editor closes. Radical Pie leaving on its own
    means it could not read the equation.
    """

    lastPost = 0.0

    while time.monotonic() < deadline:
        RaiseOnServerDialog(TopLevelWindows(pid))
        shape = slide.Shapes(placeholder.key)

        if (shape.Width, shape.Height) not in UndrawnShapeSizes:
            return

        # The size is read before the server is tested, so a render that lands as the server leaves counts.
        if AwaitProcessExit(pid, 0):
            raise PowerPointError(
                f"Radical Pie closed the editor without drawing {placeholder.key}: {UnreadableEquation}"
            )

        if time.monotonic() - lastPost >= RepostSaveSeconds:
            PostToEditor(window, win32con.WM_COMMAND, SaveCommand)
            lastPost = time.monotonic()

        time.sleep(PollSeconds)

    raise PowerPointError(f"Radical Pie drew no picture for the equation {placeholder.key} before the timeout")


def QuietenEditor(window: int) -> None:
    """Take the editor window off the operator's screen as soon as it appears.

    PowerPoint starts the server, so this window is not one the tooling launched and `STARTUPINFO` cannot
    reach it. Minimising it is what this process can do to a window of another, and Radical Pie draws the
    equation and saves it minimised.
    """

    try:
        win32gui.ShowWindow(window, win32con.SW_MINIMIZE)
    except pywintypes.error:
        pass


def PostToEditor(window: int, message: int, wparam: int) -> None:
    """Post to the editor window, tolerating one that has gone already.

    Radical Pie closes its own window when it cannot read the equation, so both the Save and the close can
    arrive after the handle has become invalid.
    """

    try:
        win32gui.PostMessage(window, message, wparam, 0)
    except pywintypes.error:
        pass


def RaiseOnServerDialog(windows: list) -> None:
    """Turn a dialog of the Radical Pie server into a PowerPointError carrying its text, and close it."""

    for handle, className, title in windows:
        if className == WindowClass:
            continue

        message = DialogText(handle)
        PostClose(handle)

        raise PowerPointError(f"Radical Pie raised a {className} dialog titled {title!r}: {message}")


def CheckShapes(presentation, placeholders: list) -> None:
    """The guard's first half: no object stands at an undrawn size when the deck is about to be written."""

    for placeholder in placeholders:
        shape = presentation.Slides(placeholder.slideNumber).Shapes(placeholder.key)
        size = (shape.Width, shape.Height)

        if size in UndrawnShapeSizes:
            raise PowerPointError(
                f"the equation {placeholder.key} on slide {placeholder.slideNumber} stands at {size[0]} by"
                f" {size[1]} points before the deck is saved, which is a blank and not a drawing of it"
            )


def CheckDrawn(deckPath: Path, expectedCount: int) -> None:
    """The guard's second half: the saved package shows a picture Radical Pie drew for every object."""

    reports = CheckDeck(deckPath)

    if len(reports) != expectedCount:
        raise PowerPointError(f"the finished deck holds {len(reports)} Radical Pie objects, expected {expectedCount}")

    collapsed = [report for report in reports if report.state == CollapsedState]

    if collapsed:
        named = ", ".join(f"{report.name} on slide {report.slideNumber}" for report in collapsed)

        raise PowerPointError(f"these equations show the blank picture in the saved deck, so they collapsed: {named}")


def CheckOffsets(deckPath: Path, placeholders: list, plans: list) -> None:
    """The saved package stands every object on the corner pass one computed, within `OffsetTolerance`.

    PowerPoint grows an object about its centre as the drawing arrives, which is what pass three undoes. This
    reads the offset back out of the package, because what the deck carries is what a reader of it sees. The
    corner comes from the plan and not from the package's own text, which no longer holds a placeholder to
    compare against; a grouped object's offset is converted out of its group's coordinates first.
    """

    with zipfile.ZipFile(deckPath) as package:
        parts = ReadObjectParts(package)

    CheckObjectParts(parts, placeholders)

    objects = {(part.slideNumber, part.name): part for part in parts}

    for plan in plans:
        part = objects[(plan.slideNumber, plan.key)]
        difference = max(abs(part.offset[0] - plan.left), abs(part.offset[1] - plan.top))

        if difference > OffsetTolerance:
            raise PowerPointError(
                f"the equation {part.name} on slide {part.slideNumber} stands at {part.offset[0]:g},"
                f" {part.offset[1]:g} in the saved deck where the run put it at {plan.left:g},"
                f" {plan.top:g}, which is {difference:g} points away"
            )


def CheckDeck(deckPath: Path) -> list:
    """Every Radical Pie object of a deck with the state of its picture, read with no COM at all.

    An object is drawn when its frame is neither the blank's nor a degenerate one and its picture is not the
    blank's bytes. One that fails any of the three shows a blank, which is the right picture for an empty
    equation and a collapse for any other, and only the `RP` stream tells those two apart.
    """

    CheckIsPowerPointPackage(deckPath)

    reports = []

    with zipfile.ZipFile(deckPath) as package:
        for part in ReadObjectParts(package):
            picture = package.read(part.picturePart)
            drawn = part.frame != BlankFrame and 0 not in part.frame and not IsBlankPicture(picture)

            if drawn:
                state = DrawnState
            else:
                state = BlankState if IsEmptyEquation(ReadEquation(package, part)) else CollapsedState

            reports.append(ObjectReport(part.slideNumber, part.name, part.size[0], part.size[1], state))

    return reports


def ReadEquation(package: zipfile.ZipFile, part: ObjectPart) -> str:
    """The `RP` stream of one object's embedding."""

    with olefile.OleFileIO(io.BytesIO(package.read(part.embeddingPart))) as container:
        return container.openstream(EquationStream).read().decode("utf-8")


def IsBlankPicture(picture: bytes) -> bool:
    """The 284-byte metafile the server answers with before a document is loaded, by size and by bytes."""

    return len(picture) == BlankPictureSize and hashlib.md5(picture).hexdigest() == BlankPictureDigest


def IsEmptyEquation(equation: str) -> bool:
    """An equation with one empty group in it, whose picture is the blank one by right."""

    return EquationContent(equation) == EmptyEquationContent


def EquationContent(equation: str) -> str:
    """The equation without its design block and without any whitespace.

    The braces are counted rather than matched by a pattern because the design block nests; it holds font
    names, numbers and nothing with a brace inside a string, so counting cannot be led astray here.
    """

    text = "".join(equation.split())

    if not text.startswith("D{"):
        return text

    depth = 0

    for index, character in enumerate(text):
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1

            if depth == 0:
                return text[index + 1 :]

    return text


def CloseDeck(presentation) -> None:
    """Close a deck, with the selection of its window dropped first.

    A shape stays selected after `Shapes.AddTextbox`, and its text after the text of that shape is set;
    PowerPoint answers `Presentation.Close` with `0x80020009 Exception occurred. / Presentation.Close :
    Failed.` while such a selection stands. Three of three decks refused to close that way and three of three
    closed after `Windows(1).Selection.Unselect()` (measured 2026-09-17). A deck opened without a window has
    no selection to drop.
    """

    for number in range(1, presentation.Windows.Count + 1):
        presentation.Windows(number).Selection.Unselect()

    presentation.Close()


def OpenDeck(session, deckPath: Path):
    """The deck open in this session, with a document window, which the base font size needs."""

    return session.application.Presentations.Open(str(deckPath), ReadOnly=False, Untitled=False, WithWindow=True)


class PowerPointSession:
    """A PowerPoint instance of this pipeline's own, watched by one thread and ended on every path.

    PowerPoint refuses `Application.Visible = False` ("Hiding the application window is not allowed"), so the
    window is minimised instead. The thread does two jobs that both have to happen while a COM call is in
    flight: it closes the modal dialogs that would block that call for ever, recording their text for the step
    to fail with, and at the deadline it ends the PowerPoint processes, which is what turns a blocked COM call
    into an error.
    """

    def __init__(self, deadline: float):
        self.deadline = deadline
        self.application = None
        self.dialogs = []
        self.powerPointPids = set()
        self.timedOut = False
        self.stop = threading.Event()

    def __enter__(self):
        # COM is initialised on this thread and never uninitialised: a probe session that uninitialised its
        # apartment on the way out left the next session's dispatch reading stale type information, and the
        # interpreter died with an access violation inside `dynamic._LazyAddAttr_` on the first `Shapes.Count`
        # of the step after it (measured on 2026-09-13, three runs out of three).
        pythoncom.CoInitialize()
        running = Pids(PowerPointImage)

        try:
            self.application = win32com.client.DispatchEx("PowerPoint.Application")
            # Recorded before the first property is set, because a failure past this line has one to end.
            self.powerPointPids = Pids(PowerPointImage) - running

            for pid in self.powerPointPids:
                Processes.Register(pid)

            self.application.WindowState = PpWindowMinimized
        except pythoncom.com_error as error:
            self.application = None
            self.Terminate()

            raise PowerPointError(f"PowerPoint did not start: {ComErrorText(error)}") from None

        threading.Thread(target=self.Watch, daemon=True).start()

        return self

    def __exit__(self, exceptionType, exceptionValue, traceback):
        self.stop.set()

        if self.application is not None:
            try:
                self.application.Quit()
            except (pythoncom.com_error, AttributeError):
                # A PowerPoint that has gone fails the call with an RPC error, and a dispatch whose type
                # information went with it raises `AttributeError: PowerPoint.Application.Quit` instead.
                # Neither may cost the termination below, which is what ends the process.
                pass

        self.application = None
        self.Terminate()

        if exceptionType is None and self.timedOut:
            raise PowerPointError("PowerPoint did not answer within the timeout and was ended")

        return False

    def Watch(self) -> None:
        while not self.stop.is_set():
            for pid in self.powerPointPids:
                for handle, className, title in TopLevelWindows(pid):
                    if className in DialogClasses:
                        self.RecordDialog(handle, className, title)

            if time.monotonic() > self.deadline:
                self.timedOut = True
                self.Terminate()

                return

            self.stop.wait(GuardSeconds)

    def RecordDialog(self, handle: int, className: str, title: str) -> None:
        entry = f"{className} titled {title!r}: {DialogText(handle)}"

        if entry not in self.dialogs:
            self.dialogs.append(entry)

        PostClose(handle)

    def CheckDialogs(self) -> None:
        if self.dialogs:
            raise PowerPointError("PowerPoint raised a modal dialog: " + "; ".join(self.dialogs))

    def Explain(self, step: str, error) -> str:
        """A COM failure in this pipeline's terms, with the dialog that caused it when there was one."""

        if self.timedOut:
            return f"PowerPoint did not answer while {step} and was ended"

        detail = "; ".join(self.dialogs)

        return f"PowerPoint failed while {step}: {ComErrorText(error)}" + (
            f" after a modal dialog: {detail}" if detail else ""
        )

    def Terminate(self) -> None:
        """End this session's PowerPoint. No Radical Pie is touched here.

        The Word pipeline ends every server that appeared while it ran; this one cannot, because the renders
        of other agents appear in the process listing in exactly the same way. The servers this pipeline ends
        are the editors it found by the window title that names its own deck.
        """

        for pid in sorted(self.powerPointPids):
            EndProcess(pid, ExitGraceSeconds)

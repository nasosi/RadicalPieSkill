"""Replace `{{pie:<key>}}` placeholder shapes in a PowerPoint deck with Radical Pie equations as OLE objects.

A placeholder is a text shape whose whole text is `{{pie:<key>}}`. The shape is deleted and an object of
class `RadicalPie.Application.1` is inserted at its left and top; the object is named after the key, which
is what the collapse check prints and what a caller sees in PowerPoint's selection pane. A deck takes no
placeholder kind and no numbering: an equation stands on a slide by itself, so there is nothing for
`|display`, `|numbered` or `{{ref:...}}` to mean. The marker is the Word pipeline's, so a draft author
learns one convention for both targets.

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

Process cleanup is narrower than the Word pipeline's, which ends every Radical Pie that appeared while it
ran. Other agents render on this machine, so a server that appears during a step is not evidence that the
step started it. This pipeline ends the PowerPoint processes its own `DispatchEx` created and the editor it
finds by the window title `Radical Pie - Equation in <the deck's file name>`, and nothing else. Every process
it does end goes through the registry of `Tools.Processes`, which the live tests are checked against.

The Word pipeline's names for the pieces both pipelines share are imported rather than repeated: the class
and its CLSID, the `RP` body, the editor's window title, the process listing and the end-of-process wait.
"""

import hashlib
import io
import os
import posixpath
import re
import shutil
import tempfile
import threading
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path

import olefile
import pythoncom
import pywintypes
import win32com.client
import win32con
import win32gui
from lxml import etree

from Tools import Processes
from Tools.Processes import AwaitProcessExit
from Tools.Render.Svg import Attempts, DialogText, PostClose, SaveCommand, TopLevelWindows, WindowClass
from Tools.Word.Docx import (
    ComErrorText,
    EditorTitlePrefix,
    EndProcess,
    EquationBody,
    ObjectClass,
    ObjectClassId,
    Pids,
)

PowerPointImage = "POWERPNT.EXE"
ServerImage = "RadicalPie.exe"

PlaceholderPattern = re.compile(r"\{\{pie:([^{}]+)\}\}")

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
GraphicFrameTag = f"{{{PresentationNamespace}}}graphicFrame"
NonVisualFrameTag = f"{{{PresentationNamespace}}}nvGraphicFramePr"
NonVisualShapeTag = f"{{{PresentationNamespace}}}nvSpPr"
NonVisualPropertiesTag = f"{{{PresentationNamespace}}}cNvPr"
FrameTransformTag = f"{{{PresentationNamespace}}}xfrm"
OleObjectTag = f"{{{PresentationNamespace}}}oleObj"
TextTag = f"{{{DrawingNamespace}}}t"
ExtentTag = f"{{{DrawingNamespace}}}ext"
BlipTag = f"{{{DrawingNamespace}}}blip"
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
RepostSaveSeconds = 0.25
ExitGraceSeconds = 10.0

# What one object gets: the activation and one retry of it, the retry against a server of its own. Under the
# parallel load of 2026-09-12 the Word activation failed about once in a hundred objects and drew on the
# rerun; this is the same server through the same editor window.
ActivationAttempts = 2
ActivationSettleSeconds = 1.0


class PowerPointError(RuntimeError):
    """The deck was not produced. The message names what was observed, in the pipeline's own terms."""


@dataclass(frozen=True)
class Placeholder:
    """One `{{pie:<key>}}` shape as the draft holds it, with the slide it stands on and its shape name."""

    slideNumber: int
    shapeName: str
    key: str


@dataclass(frozen=True)
class EmbeddedEquation:
    """One embedded equation: its key, the slide it stands on, and the size it was drawn at in points."""

    key: str
    slideNumber: int
    width: float
    height: float


@dataclass(frozen=True)
class ObjectPart:
    """One Radical Pie object as the package holds it: where it is, what it shows and where both live."""

    slideNumber: int
    name: str
    embeddingPart: str
    picturePart: str
    frame: tuple
    size: tuple


@dataclass(frozen=True)
class ObjectReport:
    """One object as the collapse check sees it. The state is `drawn`, `blank` or `collapsed`."""

    slideNumber: int
    name: str
    width: float
    height: float
    state: str


def EmbedEquations(inputPath: Path, outputPath: Path, equations: dict, timeoutSeconds: float = 600) -> list:
    """Write `inputPath` to `outputPath` with every `{{pie:<key>}}` shape replaced by `equations[key]`.

    Both paths may be relative to the caller's working directory, which is not the one PowerPoint hands them
    to its own file open, so they are resolved here and every pass below sees an absolute path.

    Returns one `EmbeddedEquation` per placeholder, in slide order. Every placeholder needs an equation and
    every equation needs a placeholder, both checked before PowerPoint starts, along with the shape a
    placeholder shares with other text and the key that names two shapes on one slide.
    """

    # `Path.resolve` returns a relative path unchanged on Windows under Python 3.9 when the file is not there
    # yet, which the output file never is, so both paths go through `os.path.abspath` instead.
    inputPath = Path(os.path.abspath(inputPath))
    outputPath = Path(os.path.abspath(outputPath))

    placeholders = ReadPlaceholders(inputPath)
    CheckPlaceholders(placeholders, equations)

    outputPath.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(inputPath, outputPath)

    deadline = time.monotonic() + timeoutSeconds

    InsertObjects(outputPath, placeholders, deadline)
    ReplaceEquationStreams(outputPath, placeholders, [equations[item.key] for item in placeholders])
    sizes = RenderObjects(outputPath, placeholders, deadline)
    CheckDrawn(outputPath, len(placeholders))

    return [
        EmbeddedEquation(placeholder.key, placeholder.slideNumber, width, height)
        for placeholder, (width, height) in zip(placeholders, sizes)
    ]


def ReadPlaceholders(deckPath: Path) -> list:
    """The placeholder shapes in slide order, read without starting PowerPoint.

    The slides are taken in the order `ppt/presentation.xml` lists them, which the part names do not follow,
    and the text of a shape is the concatenation of its runs, because PowerPoint splits a placeholder across
    runs whenever it feels like it.
    """

    placeholders = []

    with zipfile.ZipFile(deckPath) as package:
        for number, part in enumerate(SlideParts(package), 1):
            for shape in etree.fromstring(package.read(part)).iter(ShapeTag):
                text = "".join(node.text or "" for node in shape.iter(TextTag))
                match = PlaceholderPattern.search(text)

                if match is None:
                    continue

                name = shape.find(f"{NonVisualShapeTag}/{NonVisualPropertiesTag}").get("name")

                if text.strip() != match.group(0):
                    raise PowerPointError(
                        f"the shape {name!r} on slide {number} holds {text.strip()!r};"
                        " a placeholder is the whole text of its shape, because the object replaces the shape"
                    )

                if "|" in match.group(1):
                    raise PowerPointError(
                        f"{match.group(0)} on slide {number} names a placeholder kind;"
                        " a deck has no inline and no numbered equations, so a placeholder carries a key alone"
                    )

                placeholders.append(Placeholder(number, name, match.group(1)))

    return placeholders


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

            extent = frame.find(f"{FrameTransformTag}/{ExtentTag}")
            parts.append(
                ObjectPart(
                    number,
                    name,
                    relationships[element.get(RelationshipId)],
                    relationships[picture.get(RelationshipEmbed)],
                    (int(element.get("imgW")), int(element.get("imgH"))),
                    (int(extent.get("cx")) / EmuPerPoint, int(extent.get("cy")) / EmuPerPoint),
                )
            )

    return parts


def RelationshipsPartOf(partName: str) -> str:
    """The `_rels` part that carries one part's relationships."""

    return posixpath.join(posixpath.dirname(partName), "_rels", posixpath.basename(partName) + ".rels")


def InsertObjects(deckPath: Path, placeholders: list, deadline: float) -> None:
    """Pass one: each placeholder shape becomes an empty object of the add-in's class, named after its key.

    The deck is opened with a document window and the window is taken to each object's own slide, which is
    what makes the new object's design carry that slide's base font size. The shapes are collected before the
    first deletion, because a `Shapes` index moves when a shape leaves the slide while a reference to the
    shape does not.
    """

    with PowerPointSession(deadline) as session:
        try:
            presentation = OpenDeck(session, deckPath)
            presentation.Windows(1).ViewType = PpViewNormal
            found = []

            for number in range(1, presentation.Slides.Count + 1):
                slide = presentation.Slides(number)

                for index in range(1, slide.Shapes.Count + 1):
                    shape = slide.Shapes(index)

                    if shape.HasTextFrame != MsoTrue or shape.TextFrame.HasText != MsoTrue:
                        continue

                    match = PlaceholderPattern.search(shape.TextFrame.TextRange.Text)

                    if match is not None:
                        found.append((number, slide, shape, match.group(1)))

            if [key for _, _, _, key in found] != [item.key for item in placeholders]:
                raise PowerPointError(
                    f"PowerPoint reads the deck as the placeholders {[key for _, _, _, key in found]},"
                    f" the package as {[item.key for item in placeholders]}"
                )

            for number, slide, shape, key in found:
                # The base font size follows the slide the window shows and not the slide the object goes on:
                # inserted on slide 2 with slide 1 in the window, an object took the title layout's 24 point
                # subtitle instead of that slide's 28 point body (measured 2026-09-13).
                presentation.Windows(1).View.GotoSlide(number)
                InsertObject(slide, shape, key)
                session.CheckDialogs()

            presentation.Save()
            presentation.Close()
        except pythoncom.com_error as error:
            raise PowerPointError(session.Explain("inserting the objects", error)) from None


def InsertObject(slide, shape, key: str) -> None:
    """One placeholder shape becomes one object of the add-in's class, at the shape's own left and top."""

    left = shape.Left
    top = shape.Top
    shape.Delete()

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


def ReplaceEquationStreams(deckPath: Path, placeholders: list, equations: list) -> None:
    """Pass two: the equations into the `RP` streams, with PowerPoint closed.

    An equation whose design block is empty takes the base font size PowerPoint's insertion wrote into the
    object it created, so the equation is drawn at the size of the slide's body text.
    """

    with zipfile.ZipFile(deckPath) as package:
        parts = ReadObjectParts(package)
        contents = [(entry, package.read(entry.filename)) for entry in package.infolist()]

    CheckObjectParts(parts, placeholders)

    sources = {entry.filename: data for entry, data in contents}
    replacements = {}

    for part, placeholder, equation in zip(parts, placeholders, equations):
        embedding = sources[part.embeddingPart]
        body = WithBaseFontSize(EquationBody(equation), BaseFontSize(embedding, placeholder))
        replacements[part.embeddingPart] = RebuildEmbedding(embedding, body)

    with zipfile.ZipFile(deckPath, "w", zipfile.ZIP_DEFLATED) as target:
        for entry, data in contents:
            target.writestr(entry, replacements.get(entry.filename, data))


def CheckObjectParts(parts: list, placeholders: list) -> None:
    """The objects the deck holds are this pipeline's, one per placeholder, on the slide the placeholder was."""

    inserted = [(part.slideNumber, part.name) for part in parts]
    expected = [(item.slideNumber, item.key) for item in placeholders]

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


def RenderObjects(deckPath: Path, placeholders: list, deadline: float) -> list:
    """Pass three: activate each object so Radical Pie draws it, and return the sizes in points.

    The first half of the collapse guard stands between the last activation and the save: an object that
    shows the blank when the deck is written is a collapse, whatever it showed a moment earlier.
    """

    sizes = []

    with PowerPointSession(deadline) as session:
        try:
            presentation = OpenDeck(session, deckPath)
            presentation.Windows(1).ViewType = PpViewNormal

            for placeholder in placeholders:
                sizes.append(RenderObject(session, presentation, deckPath, placeholder, deadline))

            CheckShapes(presentation, placeholders)
            presentation.Save()
            presentation.Close()
        except pythoncom.com_error as error:
            raise PowerPointError(session.Explain("activating the objects", error)) from None

    return sizes


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
    running = Pids(ServerImage)

    shape.OLEFormat.Activate()
    session.CheckDialogs()

    pid, window = AwaitEditor(deckPath, running, placeholder, deadline)
    QuietenEditor(window)

    try:
        AwaitPresentation(slide, placeholder, pid, window, deadline)
    finally:
        PostToEditor(window, win32con.WM_CLOSE, 0)
        EndProcess(pid, min(ExitGraceSeconds, max(deadline - time.monotonic(), 0.0)))

    shape = slide.Shapes(placeholder.key)

    return (shape.Width, shape.Height)


def AwaitEditor(deckPath: Path, running: set, placeholder: Placeholder, deadline: float) -> tuple:
    """The server this activation started and its editor window, as (pid, window), found by the title.

    Other agents render on this machine and each of their servers is new in the process listing in exactly
    the way this one is, so the pid comes from the window and not from the listing: the editor carries
    `Radical Pie - Equation in <the deck's file name>`, where a Radical Pie opened on a file carries
    `<the file name> - Radical Pie`. A server that leaves instead of showing that window could not read the
    equation, which is how an unreadable `RP` fails: it raises no dialog of its own.
    """

    title = EditorTitlePrefix + deckPath.name
    candidates = set()

    while time.monotonic() < deadline:
        candidates |= Pids(ServerImage) - running

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

    if not candidates:
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


def CheckDeck(deckPath: Path) -> list:
    """Every Radical Pie object of a deck with the state of its picture, read with no COM at all.

    An object is drawn when its frame is neither the blank's nor a degenerate one and its picture is not the
    blank's bytes. One that fails any of the three shows a blank, which is the right picture for an empty
    equation and a collapse for any other, and only the `RP` stream tells those two apart.
    """

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

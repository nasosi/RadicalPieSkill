"""Replace `{{pie:<key>}}` placeholders in a Word document with Radical Pie equations as true OLE objects.

A placeholder carries an optional kind. `{{pie:<key>}}` is inline and sits on the text baseline;
`{{pie:<key>|display}}` is the equation alone on its own centred line in the paragraph style `Equation`;
`{{pie:<key>|numbered}}` is a display equation with `(n)` at the right margin, the number coming from a
`SEQ equation` field and carrying a bookmark named `eq_<key>` over its digits. `{{ref:<key>}}` anywhere in
the body text becomes a `REF eq_<key>` field, so the author writes "see equation ({{ref:momentum}})". The
style with its centre and right tab stops, the `SEQ` field, the bookmark over the number and the `REF`
field are the recipe the Radical Pie Word page gives under "Displayed Equations and Numbering" and
"Referencing Equations"; lowering an inline equation by its baseline shift is what the same page describes
under "Baseline Alignment".

`{{chapter}}` marks where a chapter starts, and the same page's `(x.y)` recipe is what it turns on. The
marker becomes a `SEQ chapter` field, which advances the chapter counter and shows its number where the
author put it, in a heading; from there each numbered equation reads `(x.y)`, a `SEQ chapter \\c` field that
reads the chapter without advancing it, a full stop, and the equation field, whose count starts again in each
chapter through `\\r 1` on the first equation of it. The bookmark covers the whole of such a number, so a
reference to it reads `1.2`. A draft with no marker in it is numbered `(1)`, `(2)` as it always was, and an
equation standing before the first marker is numbered that way too, because the chapter counter answers zero
until a marker advances it.

The route is the one ADR-0004 settles, in four passes over one document, because no single pass can do it.
Word inserts an object of a class, not of a file: `RadicalPie.Document.1` registers no CLSID, so
`AddOLEObject(FileName=<a .pie>)` raises a modal dialog and fails, while
`AddOLEObject(ClassType='RadicalPie.Application.1')` yields the embedding the Radical Pie add-in makes,
stream for stream, holding Radical Pie's own empty equation. The equation goes in afterwards, by replacing
the `RP` stream of each `word/embeddings/oleObjectN.bin` inside the package; Word passes a replaced `RP`
through an open and save unchanged. The picture Word shows comes from neither step: until an object is
activated once it displays as a 5.25 by 6.75 point blank, so the third pass activates each object, posts
File > Save to the editor window, waits for Word to take the new presentation, and closes the editor.

Measured on 2026-09-10 against Word 16 and Radical Pie 1.15, and the reason for each wait here:

- `AddOLEObject` inserts the object at the selection and leaves the selected text in place, so the
  placeholder is deleted first. Word appends a space run of its own after the object.
- Deleting the placeholder with `Options.SmartCutPaste` on costs the space before it: `name: {{pie:x}}.`
  becomes `name:` and the object. So the session turns that option off and puts it back at teardown. The
  option is the user's own and it travels between Word instances through a clean `Quit` alone, which is why a
  terminated session restores nothing (measured 2026-09-19, `WordSession`).
- Word resolves a relative file name against its own working directory, not the caller's, and answers
  `0x80020009 / Sorry, we couldn't find your file` for one it cannot find. Both paths are made absolute at
  the entry point.
- `OLEFormat.Activate` returns in about 0.2 s, before the server exists. The server appears about 0.3 s
  later and its window carries the title `Radical Pie - Equation in <document file name>`.
- The saved presentation reaches Word in about 30 ms after a posted Save, and shows up first as a changed
  `InlineShape.Height`; the width follows only when the editor closes. So the signal to close the editor is
  a size that differs from the blank, and the size to report is the one read after the editor is gone.
- An `RP` stream Radical Pie cannot parse raises no dialog at all: the editor window opens and the server
  exits by itself within about 2.5 s, leaving the blank picture. That exit is the failure signal.
- One equation costs about 1.2 s in the third pass; a two-equation document costs about 25 s end to end,
  which is two Word starts.

Measured on 2026-09-11 against the same two programs, and the reason for each step in the numbering:

- Word 16 has no style named `Equation` of its own: `Styles("Equation")` answers
  `0x800a0bc9 / The requested member of the collection does not exist.` in a document python-docx wrote.
  So a document without one gets the style, and a document that already has one keeps it as it is.
- `Styles.Add` gives the new style the character formatting of the paragraph the selection stands in, and
  neither a base style nor a later `Font.Reset` on the style displaces it; `Font.Reset` on a style answers
  `0x800a174b`. Assigning `Styles("Normal").Font` to the style's `Font` is what clears it, and the saved
  style then carries no run properties of its own. Applying that style to a paragraph clears the direct
  character formatting the author put on its text and on its mark, so the number written after the object
  inherits nothing of the author's either.
- A bookmark added over the result of a `SEQ` field survives a later `Fields.Update()` over the whole
  document. That is what lets one update resolve the `REF` fields after the bookmarks exist. Word saves
  both kinds as `w:fldSimple` with the result cached, so the numbers show on opening without an update.
- Radical Pie lowers an inline object by its own baseline shift itself when the object is saved from the
  editor, which is the third pass: a `Corpus/Pie/rpie.pie` object the pipeline never touches comes out of
  that pass with `w:position` at -20 half-points, the -10 points its rendering hangs below the baseline, and
  an `aaa.pie` object, which hangs nothing below it, comes out with none. So the pipeline sets nothing.
- The server of an activation is the process whose editor window carries the title above. A Radical Pie that
  starts while the activation runs, one of the operator's or one another test launched, is new in the process
  listing in exactly the same way, and taking the lowest new pid reported an equation the pipeline had drawn a
  minute earlier as one Radical Pie could not read.
- The editor window opens visible, about 1080 by 720 points, and does not take the foreground: the window that
  had it kept it through a whole pass. The pipeline minimises the editor as soon as it appears, which is what
  one process can do to another's window, and Radical Pie draws and saves the equation minimised.

Measured on 2026-09-12, with forty test workers and an agent rendering beside this pass: the activation step
fails about once in a hundred objects and succeeds on the rerun, the server closing the editor without drawing
an equation it drew a minute earlier, and once leaving one picture out of sixteen the 284-byte blank. So the
third pass activates a failed object a second time, with a server of its own, and only a second failure fails
the document; the fourth pass is unchanged and still refuses a picture no larger than the blank.

Ending a session costs one handled COM failure, which pytest's faulthandler prints as
`Windows fatal exception: code 0x800706be` with a stack in `WordSession.__exit__`. Word exits inside
`Quit`, so the release of the reference that called it reaches a process that has gone; releasing without
`Quit` leaves Word running with the document open, so there is no order that avoids it. The exception is
handled and nothing leaks.

Every process this module starts it ends, and holds it in the registry of `Tools.Processes` until its exit has
been seen, which is what the live tests are checked against. What it ends is the Word instance it created and
the editors its own activations adopted, each found by a window title naming this document; a Radical Pie that
merely appeared while the pass ran belongs to the operator or to another agent and is left alone. A modal Word
dialog blocks a COM call for ever and `DisplayAlerts = 0` does not suppress it, so a guard thread closes what
it finds and the step fails naming the dialog; the same thread terminates the processes when `timeoutSeconds`
runs out, which is what makes a hung COM call end rather than hold the caller.

A placeholder is replaced in the document body and nowhere else. One in a header, a footer, a footnote or a
text box is a different story of the package, which neither `ReadPlaceholders` nor Word's own Find reaches, so
the document used to come out with `{{pie:hdr}}` printed on every page and exit 0. `CheckPlaceholderParts`
refuses such a document before Word starts, naming the part the placeholder sits in.

An input that is not a Word package is refused by `CheckIsWordPackage` before either verb reads it, in one
line naming the file: `zipfile` and python-docx answer a missing file, a file that is not a zip and a zip of
something else with an errno line or a traceback of their own.

Every pass works on a file of the pipeline's own beside the output, and the output path is written by one
rename once the run has succeeded. A refusal or a failure removes that file and leaves the output path as it
was, whether or not a document already stood there.

Every equation is validated at the entry point, before Word starts, and not only by the command line: a caller
that came in through `EmbedEquations` with text of its own used to have an equation Radical Pie cannot read
embedded, drawn as the empty equation and reported as a success.
"""

import io
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import olefile
import pythoncom
import pywintypes
import win32com.client
import win32con
import win32gui
from docx import Document as OpenDocument
from lxml import etree

from Tools import Processes
from Tools.PieFormat.Validator import FirstViolation
from Tools.Processes import AwaitProcessExit, KillProcess
from Tools.Render.Svg import Attempts, DialogText, PostClose, SaveCommand, TopLevelWindows, WindowClass

ObjectClass = "RadicalPie.Application.1"
ObjectClassId = "{4EE860BB-53CE-44F3-BC6B-434146CAB233}"

WordImage = "WINWORD.EXE"
ServerImage = "RadicalPie.exe"

PlaceholderPattern = re.compile(r"\{\{pie:([^{}]+)\}\}")
ReferencePattern = re.compile(r"\{\{ref:([^{}]+)\}\}")
ChapterPattern = re.compile(r"\{\{chapter\}\}")

InlineKind = "inline"
DisplayKind = "display"
NumberedKind = "numbered"

Kinds = (InlineKind, DisplayKind, NumberedKind)

# A key names a Word bookmark, which takes letters, digits and underscores, starts with a letter and is at
# most 40 characters long. The prefix is part of that count.
KeyPattern = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")
BookmarkPrefix = "eq_"
BookmarkLimit = 40
KeyLimit = BookmarkLimit - len(BookmarkPrefix)

EquationStyleName = "Equation"
SequenceName = "equation"
ChapterSequenceName = "chapter"

# The two field codes the `(x.y)` recipe of References/Docs/Text/Word.md adds to `SEQ equation`. The `\c`
# switch reads the chapter counter without advancing it, so every equation of a chapter shows the same `x`;
# `\r 1` starts the equation counter again, which is what makes `y` count from one in each chapter.
ChapterReadCode = f"{ChapterSequenceName} \\c"
RestartCode = f"{SequenceName} \\r 1"

# The codes `MatchingFields` picks this pipeline's own numbering out of the author's fields by.
EquationFieldCodes = frozenset({f"SEQ {SequenceName}", f"SEQ {RestartCode}"})
ChapterFieldCode = f"SEQ {ChapterReadCode}"

# What a number a `SEQ` field came out with looks like, flat or with its chapter before it.
NumberPattern = re.compile(r"[0-9]+(\.[0-9]+)?\Z")

# The streams Word writes into a fresh embedding. The equation lives in `RP`; the other three are Word's own
# and are carried over byte for byte, because they are what the add-in's embeddings carry too.
EquationStream = "RP"
FixedStreams = ("\x01CompObj", "\x01Ole", "\x03ObjInfo")

WordNamespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
VmlNamespace = "urn:schemas-microsoft-com:vml"
OfficeNamespace = "urn:schemas-microsoft-com:office:office"
DrawingNamespace = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
RelationshipNamespace = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PackageRelationshipNamespace = "http://schemas.openxmlformats.org/package/2006/relationships"

ParagraphTag = f"{{{WordNamespace}}}p"
TextBoxTag = f"{{{WordNamespace}}}txbxContent"
TextTag = f"{{{WordNamespace}}}t"
OleObjectTag = f"{{{OfficeNamespace}}}OLEObject"
ImageDataTag = f"{{{VmlNamespace}}}imagedata"
ExtentTag = f"{{{DrawingNamespace}}}extent"
BookmarkStartTag = f"{{{WordNamespace}}}bookmarkStart"
RelationshipTag = f"{{{PackageRelationshipNamespace}}}Relationship"
RelationshipId = f"{{{RelationshipNamespace}}}id"
DxaOrigAttribute = f"{{{WordNamespace}}}dxaOrig"
DyaOrigAttribute = f"{{{WordNamespace}}}dyaOrig"
NameAttribute = f"{{{WordNamespace}}}name"

DocumentPart = "word/document.xml"
RelationshipsPart = "word/_rels/document.xml.rels"

# The part every Office package holds, which is what tells one from a zip of something else.
ContentTypesPart = "[Content_Types].xml"

TwipsPerPoint = 20
EmuPerPoint = 12700

# The byte size of the picture Word caches for a freshly inserted, unactivated object of any class, measured
# on 2026-09-10 against Word 16, and the same figure `EmbedEquations` measures live from the document's own
# cache in `ReplaceEquationStreams`. `check` opens a document nothing here just embedded, with no such pass
# to measure from, so it takes the measured constant instead.
BlankPictureSize = 284

# The budget for a whole run when the caller names none, base plus an allowance for each object. Measured on
# 2026-09-19 against Word 16 and Radical Pie 1.15: a one-object document took 17.4 seconds end to end and a
# six-object document 23.0, which is 16.3 seconds of the two Word starts and 1.12 seconds an object. The
# allowance is five times that rate and the base is what a whole run used to get.
BaseTimeoutSeconds = 120.0
PerObjectTimeoutSeconds = 6.0

WdDoNotSaveChanges = 0
WdFindStop = 0
WdStory = 6
WdInlineShapeEmbeddedOLEObject = 1
WdCollapseEnd = 0
WdStyleTypeParagraph = 1
WdStyleNormal = -1
WdLineSpaceSingle = 0
WdAlignParagraphLeft = 0
WdAlignTabCenter = 1
WdAlignTabRight = 2
WdFieldRef = 3
WdFieldSequence = 12

StgmCreateReadWriteExclusive = 0x1000 | 0x0002 | 0x0010
StgmCreateWriteExclusive = 0x1000 | 0x0001 | 0x0010

# Word's own modal windows. `NUIDialog` is the Office dialog; `#32770` is the plain Win32 message box.
WordDialogClasses = frozenset({"NUIDialog", "#32770"})

# What an activated server leaving on its own means. It raises no dialog of the kind the file route raises.
UnreadableEquation = "it leaves like that when it cannot read the equation"

# The start of the title the editor window carries, the rest of it being the document's file name.
EditorTitlePrefix = "Radical Pie - Equation in "

PollSeconds = 0.05
GuardSeconds = 0.3
RepostSaveSeconds = 0.25
ExitGraceSeconds = 10.0
ServerExitGraceSeconds = 2.0

# What one object gets: the activation and one retry of it. The settle is the pause between the failed
# attempt's server going and the next activation, which is the load the retry is there for.
ActivationAttempts = 2
ActivationSettleSeconds = 1.0


class WordError(RuntimeError):
    """The document was not produced. The message names what was observed, in the pipeline's own terms."""


@dataclass(frozen=True)
class Placeholder:
    """One `{{pie:...}}` as the document holds it, with the text of the paragraph it was found in."""

    paragraphIndex: int
    key: str
    kind: str
    text: str
    paragraphText: str


@dataclass(frozen=True)
class Reference:
    """One `{{ref:<key>}}`, which becomes a `REF eq_<key>` field over the number of that equation."""

    paragraphIndex: int
    key: str
    text: str


@dataclass(frozen=True)
class NumberForm:
    """How one numbered equation's number is written: the chapter before it, and the count starting again."""

    chaptered: bool
    restart: bool


@dataclass(frozen=True)
class EmbeddedEquation:
    """One embedded equation: its key and kind, the paragraph it sits in, its number, its size in points.

    The number is the integer the `SEQ equation` field came out with, and the string `'<chapter>.<n>'` in a
    document whose chapters the markers name.
    """

    key: str
    kind: str
    paragraphIndex: int
    number: Union[int, str, None]
    width: float
    height: float


def TimeoutBudget(objectCount: int) -> float:
    """What a run of `objectCount` objects gets to finish in, the base and the allowance of each object."""

    return BaseTimeoutSeconds + PerObjectTimeoutSeconds * objectCount


def EmbedEquations(inputPath: Path, outputPath: Path, equations: dict, timeoutSeconds: Optional[float] = None) -> list:
    """Write `inputPath` to `outputPath` with every `{{pie:<key>}}` replaced by the equation `equations[key]`.

    Both paths may be relative to the caller's working directory, which is not the one Word hands them to
    its own file open, so they are resolved here and every pass below sees an absolute path.

    Returns one `EmbeddedEquation` per placeholder, in document order. The `.pie` text is embedded as the
    caller wrote it, design block included: an equation with no design carries the `D {}` the caller put
    there. Every placeholder needs an equation and every equation needs a placeholder, both checked before
    Word starts, along with the grammar of the keys, the paragraph a display equation is alone in, and the
    numbered equation every reference names.

    Every pass works on a file of the pipeline's own beside the output, which is moved onto the output path
    once the run has succeeded and its checks have passed. A failure leaves that path as it was: the copy used
    to go straight there, so a document that failed in a later pass handed the caller the objects with the
    blank picture still in them, and a rerun over an output file that already held a good document destroyed
    it.

    Both passes that start Word share one deadline. A `timeoutSeconds` of its own bounds the run at what the
    caller asks for; none takes `TimeoutBudget` of the count of placeholders, so the budget grows with the
    objects the run has to draw.
    """

    # `Path.resolve` returns a relative path unchanged on Windows under Python 3.9 when the file is not there
    # yet, which the output file never is, so both paths go through `os.path.abspath` instead.
    inputPath = Path(os.path.abspath(inputPath))
    outputPath = Path(os.path.abspath(outputPath))

    CheckIsWordPackage(inputPath)
    CheckPlaceholderParts(inputPath)
    placeholders, references = ReadPlaceholders(inputPath)
    CheckPlaceholders(placeholders, references, equations)
    CheckEquationsValidate(equations)

    keys = [placeholder.key for placeholder in placeholders]
    bodies = [EquationBody(equations[key]) for key in keys]

    outputPath.parent.mkdir(parents=True, exist_ok=True)
    workPath = WorkingDocument(inputPath, outputPath)

    if timeoutSeconds is None:
        timeoutSeconds = TimeoutBudget(len(keys))

    deadline = time.monotonic() + timeoutSeconds

    try:
        numbers = InsertObjects(workPath, placeholders, references, deadline)
        blankPictureSize = ReplaceEquationStreams(workPath, bodies)
        sizes = RenderObjects(workPath, keys, deadline)
        CheckPictures(workPath, len(keys), blankPictureSize)
    except BaseException:
        # A keyboard interrupt leaves no half-built document behind either, so the sweep is on BaseException.
        workPath.unlink(missing_ok=True)

        raise

    os.replace(workPath, outputPath)

    return [
        EmbeddedEquation(placeholder.key, placeholder.kind, placeholder.paragraphIndex, number, width, height)
        for placeholder, number, (width, height) in zip(placeholders, numbers, sizes)
    ]


def CheckEquationsValidate(equations: dict) -> None:
    """Every equation the caller handed over validates, which is the last thing known before Word starts.

    The command line validates the files it read and prints every violation of every one of them; this is the
    same gate for a caller that came in through the entry point with text, and it names the key. Radical Pie
    drops a structure it does not know instead of refusing the file, so without this an equation with one typo
    in a structure name was embedded, drawn as the empty equation and reported as a success.

    It runs after the checks over the document, because those name what the author has to change in the
    document and cost no launch either.
    """

    for key in sorted(equations):
        violation = FirstViolation(equations[key])

        if violation:
            raise WordError(f"the equation {key} does not validate, so nothing was started: {violation}")


def WorkingDocument(inputPath: Path, outputPath: Path) -> Path:
    """The input copied to a file of the pipeline's own beside the output, which every pass works on.

    The name keeps the output's extension, because Word decides what it is opening by it, and it stands in the
    output's own directory, so the move onto the output path at the end of the run is a rename on one volume.
    It is unique, because pass three finds its Radical Pie editor by a window title that carries this file's
    name, which is what keeps two runs on one machine apart.
    """

    handle, name = tempfile.mkstemp(prefix=outputPath.stem + ".", suffix=outputPath.suffix, dir=outputPath.parent)
    os.close(handle)
    workPath = Path(name)
    shutil.copyfile(inputPath, workPath)

    return workPath


def CheckIsWordPackage(documentPath: Path) -> None:
    """Refuse a document that is not there or is not a Word package, before anything else reads it.

    Both verbs run this first. `embed` used to hand the caller a `zipfile` traceback for a file that was not a
    package and an errno line for one that was missing, and `check` a traceback for a zip of something else.
    """

    complaint = PackageComplaint(documentPath, DocumentPart)

    if complaint:
        raise WordError(f"{documentPath} is not a Word package: {complaint}")


def PackageComplaint(path: Path, requiredPart: str) -> str:
    """Why `path` is not an Office package holding `requiredPart`, or the empty string when it is one.

    `zipfile` answers a file that is not there with FileNotFoundError, one that is not a zip with BadZipFile,
    and a zip of something else with a KeyError from the first part read, and each of those reached the caller
    as an errno line or a traceback. What comes back here is the clause each pipeline puts after the file name
    in its own error; `Tools/PowerPoint/Pptx.py` names its own required part and raises its own error type.
    """

    if not path.is_file():
        return "there is no file of that name" if not path.exists() else "it is not a file"

    try:
        with zipfile.ZipFile(path) as package:
            names = set(package.namelist())
    except (OSError, zipfile.BadZipFile):
        return "it is not a zip file"

    for part in (ContentTypesPart, requiredPart):
        if part not in names:
            return f"it is a zip file that holds no {part}"

    return ""


def CheckPlaceholderParts(documentPath: Path) -> None:
    """Refuse a document whose placeholders are not all in the body, naming the part the first one sits in.

    Word keeps a header, a footer, a footnote and an endnote in parts of their own and a text box inside the
    body in a `w:txbxContent` of its own, and each of those is a separate story: `AddOLEObject` inserts at
    the selection of the body story and Word's Find runs in that story too, so a placeholder anywhere else
    is left in the finished document as the literal text the author typed. The scan reads the package
    without starting Word, so this costs nothing and happens before anything is launched.
    """

    with zipfile.ZipFile(documentPath) as package:
        for name in sorted(package.namelist()):
            if not name.startswith("word/") or not name.endswith(".xml"):
                continue

            root = etree.fromstring(package.read(name))

            for paragraph in root.iter(ParagraphTag):
                inBody = name == DocumentPart and next(paragraph.iterancestors(TextBoxTag), None) is None

                if inBody:
                    continue

                where = f"a text box in {name}" if name == DocumentPart else name
                paragraphText = "".join(node.text or "" for node in paragraph.iter(TextTag))

                for pattern in (PlaceholderPattern, ReferencePattern, ChapterPattern):
                    match = pattern.search(paragraphText)

                    if match:
                        raise WordError(
                            f"{where} holds {match.group(0)}; this pipeline replaces a placeholder in the"
                            " document body only, so an equation goes in the body text"
                        )


def ReadPlaceholders(documentPath: Path) -> tuple:
    """The equation placeholders and the references, both in document order, read without starting Word.

    The paragraph index counts every `w:p` of the body, which includes the paragraphs inside tables, and the
    text of a paragraph is the concatenation of its runs, because Word splits a placeholder across runs
    whenever it feels like it.
    """

    document = OpenDocument(str(documentPath))
    placeholders = []
    references = []

    for index, paragraph in enumerate(document.element.body.iter(ParagraphTag)):
        text = "".join(node.text or "" for node in paragraph.iter(TextTag))

        for match in PlaceholderPattern.finditer(text):
            key, separator, kind = match.group(1).partition("|")
            placeholders.append(Placeholder(index, key, kind if separator else InlineKind, match.group(0), text))

        for match in ReferencePattern.finditer(text):
            references.append(Reference(index, match.group(1), match.group(0)))

    return placeholders, references


def ReadChapters(documentPath: Path) -> list:
    """The paragraph index of every `{{chapter}}` in the body, in document order, with Word not started.

    A marker says that a chapter starts here. What follows it is numbered `(x.y)` with `x` the count of
    markers up to that point, so this is the whole of what the pipeline needs to know about the structure of
    the document: a draft with no marker in it is numbered flat, as it always was.
    """

    document = OpenDocument(str(documentPath))
    chapters = []

    for index, paragraph in enumerate(document.element.body.iter(ParagraphTag)):
        text = "".join(node.text or "" for node in paragraph.iter(TextTag))

        chapters.extend(index for _ in ChapterPattern.finditer(text))

    return chapters


def NumberForms(placeholders: list, chapters: list) -> dict:
    """How each numbered placeholder's number is written, by its position in `placeholders`.

    An equation standing before the first marker is numbered flat, because the chapter counter is zero until
    a marker advances it and the Word page says so. The first numbered equation of a chapter is the one that
    restarts the equation counter.
    """

    forms = {}
    restarted = set()

    for index, placeholder in enumerate(placeholders):
        if placeholder.kind != NumberedKind:
            continue

        chapter = sum(1 for paragraph in chapters if paragraph < placeholder.paragraphIndex)
        forms[index] = NumberForm(chapter > 0, chapter > 0 and chapter not in restarted)
        restarted.add(chapter)

    return forms


def CheckPlaceholders(placeholders: list, references: list, equations: dict) -> None:
    """Everything about the document that can be known before Word starts, each failure naming its offender."""

    for placeholder in placeholders:
        CheckKey(placeholder.key, placeholder.text)

        if placeholder.kind not in Kinds:
            raise WordError(f"{placeholder.text} names the kind {placeholder.kind!r}, not one of {', '.join(Kinds)}")

        if placeholder.kind != InlineKind and placeholder.paragraphText != placeholder.text:
            raise WordError(
                f"{placeholder.text} shares its paragraph with other text ({placeholder.paragraphText!r});"
                " a display equation is the whole of its paragraph"
            )

    numbered = [placeholder.key for placeholder in placeholders if placeholder.kind == NumberedKind]
    twice = sorted({key for key in numbered if numbered.count(key) > 1})

    if twice:
        raise WordError(f"these keys are numbered more than once, and a bookmark names one number: {', '.join(twice)}")

    for reference in references:
        CheckKey(reference.key, reference.text)

        if reference.key not in numbered:
            raise WordError(f"{reference.text} names no numbered equation")

    placed = {placeholder.key for placeholder in placeholders}
    unknown = sorted(placed - set(equations))
    unused = sorted(set(equations) - placed)

    if unknown:
        raise WordError(f"the document holds placeholders with no equation: {', '.join(unknown)}")

    if unused:
        raise WordError(f"the document holds no placeholder for the equations: {', '.join(unused)}")


def CheckKey(key: str, text: str) -> None:
    """A key names a bookmark, so it is a letter followed by letters, digits and underscores, and short."""

    if not KeyPattern.match(key):
        raise WordError(
            f"{text} names the key {key!r}, which is not a letter followed by letters, digits and underscores"
        )

    if len(key) > KeyLimit:
        raise WordError(f"{text} names a key of {len(key)} characters, and a bookmark name takes at most {KeyLimit}")


def EquationBody(pieText: str) -> bytes:
    """The `.pie` text as the `RP` stream carries it: no header line, LF line endings, UTF-8, final newline."""

    text = pieText.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    if lines and lines[0].startswith("//"):
        lines = lines[1:]

    body = "\n".join(lines).lstrip("\n")

    return (body if body.endswith("\n") else body + "\n").encode("utf-8")


def InsertObjects(documentPath: Path, placeholders: list, references: list, deadline: float) -> list:
    """Pass one: the chapters, the objects, the display style, the numbers, the bookmarks and the references.

    Returns the number of each placeholder in document order, `None` where it is not a numbered equation.
    """

    chapters = ReadChapters(documentPath)
    forms = NumberForms(placeholders, chapters)

    with WordSession(deadline) as session:
        application = session.application
        done = 0

        try:
            document = application.Documents.Open(str(documentPath), ReadOnly=False, AddToRecentFiles=False)

            if any(placeholder.kind != InlineKind for placeholder in placeholders):
                EnsureEquationStyle(document)

            for _ in chapters:
                InsertChapter(application, document)
                session.CheckDialogs()

            for index, placeholder in enumerate(placeholders):
                InsertObject(application, document, placeholder, forms.get(index))
                session.CheckDialogs()
                done += 1

            for reference in references:
                InsertReference(application, document, reference)
                session.CheckDialogs()

            inserted = ObjectIndexes(document)

            if len(inserted) != len(placeholders):
                raise WordError(f"Word holds {len(inserted)} Radical Pie objects after inserting {len(placeholders)}")

            numbers = NumberEquations(document, placeholders, forms, references, chapters)

            document.Save()
            document.Close(WdDoNotSaveChanges)
        except pythoncom.com_error as error:
            step = f"inserting the objects ({done} of {len(placeholders)} inserted)"

            raise WordError(session.Explain(step, error)) from None

    return numbers


def EnsureEquationStyle(document) -> None:
    """The paragraph style the Word page prescribes for a displayed equation, when the document has none.

    The tab stops are the two the page names, a centre stop at half the usable width of the first section and
    a right stop at the whole of it. The style is left alone when it is already there, because it is then the
    author's own. Left alignment is set because a centre tab moves nothing in a centred or justified
    paragraph.

    Every piece of the style is set here rather than left to what `Styles.Add` produced, because what it
    produces depends on where the selection was standing.
    """

    try:
        document.Styles(EquationStyleName)
    except pythoncom.com_error:
        pass
    else:
        return

    normal = document.Styles(WdStyleNormal)
    setup = document.Sections(1).PageSetup
    usableWidth = setup.PageWidth - setup.LeftMargin - setup.RightMargin

    style = document.Styles.Add(Name=EquationStyleName, Type=WdStyleTypeParagraph)
    style.BaseStyle = normal
    style.NextParagraphStyle = normal

    # `Styles.Add` copies the character formatting of the paragraph the selection stands in, and a base style
    # does not displace it: created with the selection in the Title of a document, the style carried the
    # Title's 26 pt blue and every equation number came out in it. Assigning Normal's own font leaves the
    # style with no character formatting of its own at all, measured on 2026-09-11 against Word 16; setting
    # the name, the size and the colour one at a time leaves the Title's character spacing, its kerning and
    # its complex-script size behind.
    style.Font = normal.Font

    paragraphFormat = style.ParagraphFormat
    paragraphFormat.Alignment = WdAlignParagraphLeft
    paragraphFormat.LineSpacingRule = WdLineSpaceSingle
    paragraphFormat.SpaceBefore = normal.Font.Size
    paragraphFormat.SpaceAfter = normal.Font.Size
    paragraphFormat.FirstLineIndent = 0

    paragraphFormat.TabStops.ClearAll()
    paragraphFormat.TabStops.Add(Position=usableWidth / 2, Alignment=WdAlignTabCenter)
    paragraphFormat.TabStops.Add(Position=usableWidth, Alignment=WdAlignTabRight)


def InsertChapter(application, document) -> None:
    """One `{{chapter}}` becomes the `SEQ chapter` field that advances the chapter counter and shows it.

    Every marker carries the same text, so each call takes the first one still standing, which is the order
    the counter runs in. The Word page puts this field in a title or a heading, because a counter read with
    `\\c` and never advanced answers zero.
    """

    SelectPlaceholder(application, "{{chapter}}")
    selection = application.Selection
    selection.Delete()

    document.Fields.Add(
        Range=selection.Range,
        Type=WdFieldSequence,
        Text=ChapterSequenceName,
        PreserveFormatting=False,
    )


def InsertObject(application, document, placeholder: Placeholder, form: Optional[NumberForm]) -> None:
    """One placeholder becomes an object, centred and numbered when its kind asks for it."""

    SelectPlaceholder(application, placeholder.text)
    selection = application.Selection
    selection.Delete()

    if placeholder.kind != InlineKind:
        selection.Paragraphs(1).Style = document.Styles(EquationStyleName)

        # Inserted as text rather than typed with `TypeText`, which goes through Word's autoformat.
        selection.InsertAfter("\t")
        selection.Collapse(WdCollapseEnd)

    shape = selection.InlineShapes.AddOLEObject(ClassType=ObjectClass)

    if placeholder.kind == InlineKind:
        return

    DeleteSpaceAfterObject(document, shape)

    if placeholder.kind == NumberedKind:
        AddNumberField(document, shape, form)


def DeleteSpaceAfterObject(document, shape) -> None:
    """Word's own space after a new object, which would sit between the equation and the number tab."""

    end = shape.Range.End
    paragraphEnd = shape.Range.Paragraphs(1).Range.End

    if end >= paragraphEnd - 1:
        return

    following = document.Range(end, end + 1)

    if following.Text == " ":
        following.Delete()


def AddNumberField(document, shape, form: NumberForm) -> None:
    """The right tab, the parentheses and the `SEQ` fields that count the displayed equations.

    A flat number is one `SEQ equation` field between the parentheses. A chaptered one is `SEQ chapter \\c`,
    a full stop and the equation field, which is the `(x.y)` recipe of the Word page, and the first equation
    of a chapter carries `\\r 1` so that the count starts again there.

    The number carries the paragraph style and nothing else, and nothing here resets it: applying the
    `Equation` style to the paragraph clears the direct character formatting the author's own text and
    paragraph mark carried, so what is written after the object inherits none of it. Measured on 2026-09-11
    with 26 point blue on both the run and the mark of the placeholder's paragraph.
    """

    paragraph = shape.Range.Paragraphs(1).Range
    tail = document.Range(paragraph.End - 1, paragraph.End - 1)

    # `InsertAfter` on a collapsed range grows it over what it inserted, so a field goes one character back,
    # between the parentheses, and the bookmark that follows covers the number alone.
    tail.InsertAfter("\t(.)" if form.chaptered else "\t()")
    end = tail.End

    # The equation field goes in first: inserting it moves nothing before it, so the full stop is still the
    # character the chapter field goes in front of.
    document.Fields.Add(
        Range=document.Range(end - 1, end - 1),
        Type=WdFieldSequence,
        Text=RestartCode if form.restart else SequenceName,
        PreserveFormatting=False,
    )

    if form.chaptered:
        document.Fields.Add(
            Range=document.Range(end - 2, end - 2),
            Type=WdFieldSequence,
            Text=ChapterReadCode,
            PreserveFormatting=False,
        )


def InsertReference(application, document, reference: Reference) -> None:
    """One `{{ref:<key>}}` becomes a `REF eq_<key>` field. The bookmark it names is added after the numbering."""

    SelectPlaceholder(application, reference.text)
    selection = application.Selection
    selection.Delete()

    document.Fields.Add(
        Range=selection.Range,
        Type=WdFieldRef,
        Text=BookmarkPrefix + reference.key,
        PreserveFormatting=False,
    )


def NumberEquations(document, placeholders: list, forms: dict, references: list, chapters: list) -> list:
    """Update the fields, bookmark each number, and read the numbers back.

    The order is the one Word needs: a `SEQ` field has no number until it is updated, a bookmark can only be
    put over a number that exists, and a `REF` field resolves only once its bookmark is there. A bookmark
    over a field result survives the second update, measured on 2026-09-11.

    A chaptered number is two fields and the full stop between them, and the bookmark covers all three, which
    is what the Word page asks for: a reference to such an equation reads `1.2` and not `2`.
    """

    numbered = [(index, placeholders[index].key) for index in sorted(forms)]

    if not numbered and not chapters:
        return [None] * len(placeholders)

    document.Fields.Update()
    sequenceFields = MatchingFields(document, WdFieldSequence, EquationFieldCodes)
    chapterFields = MatchingFields(document, WdFieldSequence, {ChapterFieldCode})
    chaptered = [index for index in sorted(forms) if forms[index].chaptered]

    if len(sequenceFields) != len(numbered):
        raise WordError(
            f"the document holds {len(sequenceFields)} SEQ {SequenceName} fields"
            f" after numbering {len(numbered)} equations"
        )

    if len(chapterFields) != len(chaptered):
        raise WordError(
            f"the document holds {len(chapterFields)} {ChapterFieldCode} fields"
            f" after numbering {len(chaptered)} equations inside a chapter"
        )

    numbers = {}
    remainingChapterFields = iter(chapterFields)

    for (index, key), field in zip(numbered, sequenceFields):
        result = field.Result

        if forms[index].chaptered:
            result = document.Range(next(remainingChapterFields).Result.Start, result.End)

        document.Bookmarks.Add(Name=BookmarkPrefix + key, Range=result)
        numbers[key] = ReadNumber(key, result.Text)

    if references:
        document.Fields.Update()
        codes = {f"REF {BookmarkPrefix}{reference.key}" for reference in references}

        for field in MatchingFields(document, WdFieldRef, codes):
            if not NumberPattern.match(field.Result.Text.strip()):
                raise WordError(f"the field {field.Code.Text.strip()} resolved to {field.Result.Text!r}")

    # A key may carry an inline placeholder as well as a numbered one, and only the numbered one has a number.
    return [numbers.get(placeholder.key) if placeholder.kind == NumberedKind else None for placeholder in placeholders]


def MatchingFields(document, fieldType: int, codes: set) -> list:
    """This pipeline's own fields of one type, in document order, the author's own fields left out of it."""

    fields = [document.Fields(index) for index in range(1, document.Fields.Count + 1)]

    return [field for field in fields if field.Type == fieldType and field.Code.Text.strip() in codes]


def ReadNumber(key: str, text: str) -> Union[int, str]:
    """A flat number as an `int`, a chaptered one as the `'<chapter>.<n>'` the two fields came out with."""

    number = text.strip()

    if not NumberPattern.match(number):
        raise WordError(f"the number of the equation {key} came out as {text!r}")

    return int(number) if number.isdigit() else number


def SelectPlaceholder(application, placeholder: str) -> None:
    """Select the first remaining occurrence of `placeholder`, searching from the start of the document.

    Every Find flag is set here, none left to its previous value: a fresh Word instance inherits the search
    options of the operator's last search, and MatchWildcards on would read the braces as a pattern.
    """

    selection = application.Selection
    selection.HomeKey(WdStory)

    find = selection.Find
    find.ClearFormatting()
    find.Text = placeholder
    find.Forward = True
    find.Wrap = WdFindStop
    find.Format = False
    find.MatchCase = True
    find.MatchWholeWord = False
    find.MatchWildcards = False
    find.MatchSoundsLike = False
    find.MatchAllWordForms = False

    if not find.Execute():
        raise WordError(f"Word did not find the placeholder {placeholder}")


def ObjectIndexes(document) -> list:
    """The `InlineShapes` indexes of the Radical Pie objects, in document order.

    A picture or another program's object is an inline shape too, so the collection is filtered by class
    rather than counted.
    """

    indexes = []

    for index in range(1, document.InlineShapes.Count + 1):
        shape = document.InlineShapes(index)

        if shape.Type == WdInlineShapeEmbeddedOLEObject and shape.OLEFormat.ClassType == ObjectClass:
            indexes.append(index)

    return indexes


def ReplaceEquationStreams(documentPath: Path, bodies: list) -> int:
    """Pass two: the equations into the `RP` streams. Returns the size of the blank picture Word cached.

    The blank picture is what the objects display before they are activated; the sizes of the pictures after
    activation are compared against it.
    """

    with zipfile.ZipFile(documentPath) as package:
        parts = ReadObjectParts(package)
        contents = [(entry, package.read(entry.filename)) for entry in package.infolist()]

    if len(parts) != len(bodies):
        raise WordError(f"the document holds {len(parts)} Radical Pie objects, expected {len(bodies)}")

    sources = {entry.filename: data for entry, data in contents}
    replacements = {
        embeddingPart: RebuildEmbedding(sources[embeddingPart], body) for (embeddingPart, _), body in zip(parts, bodies)
    }

    with zipfile.ZipFile(documentPath, "w", zipfile.ZIP_DEFLATED) as target:
        for entry, data in contents:
            target.writestr(entry, replacements.get(entry.filename, data))

    return max((len(sources[picturePart]) for _, picturePart in parts), default=0)


def ReadRelationships(package: zipfile.ZipFile) -> dict:
    """The relationships of `word/document.xml`, id to part name, `Target` resolved against the package root."""

    return {
        element.get("Id"): "word/" + element.get("Target").lstrip("/")
        for element in etree.fromstring(package.read(RelationshipsPart)).iter(RelationshipTag)
    }


def ReadObjectParts(package: zipfile.ZipFile) -> list:
    """The (embedding part, picture part) pairs of the Radical Pie objects, in document order."""

    relationships = ReadRelationships(package)
    parts = []

    for element in etree.fromstring(package.read(DocumentPart)).iter(OleObjectTag):
        if element.get("ProgID") != ObjectClass:
            continue

        picture = element.getparent().find(f".//{ImageDataTag}")

        if picture is None:
            raise WordError("a Radical Pie object in the document carries no picture")

        parts.append((relationships[element.get(RelationshipId)], relationships[picture.get(RelationshipId)]))

    return parts


@dataclass(frozen=True)
class ObjectRecord:
    """One embedded object as `check` reports it, read from the package without starting Word."""

    identity: str
    progId: str
    width: float
    height: float
    drawn: bool


def CheckObjects(documentPath: Path) -> list:
    """Every embedded object in `documentPath`, in document order, of any class.

    The identity is the key of the `eq_<key>` bookmark the numbered kind leaves in the object's own
    paragraph, and the paragraph index `ReadPlaceholders` would have given the placeholder for the other two
    kinds, which leave no bookmark. `drawn` is `CheckPictures`'s own rule, a picture over `BlankPictureSize`
    rather than the blank Word caches on insertion, against the measured constant rather than a size read
    live from this same document, because nothing here inserted an object to measure the blank of.
    """

    CheckIsWordPackage(documentPath)

    with zipfile.ZipFile(documentPath) as package:
        relationships = ReadRelationships(package)
        documentXml = etree.fromstring(package.read(DocumentPart))

        # Kept alive as a list rather than folded straight into the dict below: lxml gives the same node's
        # ancestor a fresh Python object on every access, unless something is still holding the one from this
        # enumeration, and `id()` on one already freed can equal a later element's, which the dict then finds.
        paragraphs = list(documentXml.iter(ParagraphTag))
        paragraphIndex = {id(paragraph): index for index, paragraph in enumerate(paragraphs)}
        records = []

        for element in documentXml.iter(OleObjectTag):
            objectElement = element.getparent()
            paragraph = next(objectElement.iterancestors(ParagraphTag))
            picture = objectElement.find(f".//{ImageDataTag}")
            pictureSize = len(package.read(relationships[picture.get(RelationshipId)])) if picture is not None else 0
            width, height = ObjectSize(objectElement)

            records.append(
                ObjectRecord(
                    identity=ParagraphKey(paragraph) or str(paragraphIndex[id(paragraph)]),
                    progId=element.get("ProgID"),
                    width=width,
                    height=height,
                    drawn=pictureSize > BlankPictureSize,
                )
            )

    return records


def ObjectSize(objectElement) -> tuple:
    """The size in points of one `w:object`, from its own `dxaOrig`/`dyaOrig`, in twips.

    An object with no VML fallback of its own, a DrawingML one instead, carries neither attribute; its size
    is read from the `wp:extent` inside it instead, in EMU.
    """

    dxaOrig = objectElement.get(DxaOrigAttribute)
    dyaOrig = objectElement.get(DyaOrigAttribute)

    if dxaOrig is not None and dyaOrig is not None:
        return (int(dxaOrig) / TwipsPerPoint, int(dyaOrig) / TwipsPerPoint)

    extent = objectElement.find(f".//{ExtentTag}")

    if extent is None:
        raise WordError("an embedded object carries neither dxaOrig/dyaOrig nor a wp:extent")

    return (int(extent.get("cx")) / EmuPerPoint, int(extent.get("cy")) / EmuPerPoint)


def ParagraphKey(paragraph) -> Optional[str]:
    """The key of the `eq_<key>` bookmark this paragraph carries, or `None` when it carries none."""

    for bookmark in paragraph.iter(BookmarkStartTag):
        name = bookmark.get(NameAttribute, "")

        if name.startswith(BookmarkPrefix):
            return name[len(BookmarkPrefix) :]

    return None


def RebuildEmbedding(embedding: bytes, body: bytes) -> bytes:
    """The embedding with `body` as its `RP` stream.

    The compound file is rebuilt rather than patched, because the equation is not the size of the empty one
    Radical Pie put there and a stream cannot grow in place.
    """

    with olefile.OleFileIO(io.BytesIO(embedding)) as container:
        streams = [(name, container.openstream(name).read()) for name in FixedStreams]

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


def RenderObjects(documentPath: Path, keys: list, deadline: float) -> list:
    """Pass three: activate each object so Radical Pie draws it, and return the sizes in points."""

    sizes = []

    with WordSession(deadline) as session:
        try:
            document = session.application.Documents.Open(str(documentPath), ReadOnly=False, AddToRecentFiles=False)
            indexes = ObjectIndexes(document)

            if len(indexes) != len(keys):
                raise WordError(f"the reopened document holds {len(indexes)} Radical Pie objects, expected {len(keys)}")

            for key, index in zip(keys, indexes):
                sizes.append(RenderObject(session, documentPath, document, index, key, deadline))

            document.Save()
            document.Close(WdDoNotSaveChanges)
        except pythoncom.com_error as error:
            step = f"activating the objects ({len(sizes)} of {len(keys)} drawn)"

            raise WordError(session.Explain(step, error)) from None

    return sizes


def RenderObject(session, documentPath: Path, document, index: int, key: str, deadline: float) -> tuple:
    """Draw one object, retrying the activation once, and return the size Word ends up with.

    Under load of 2026-09-12 the server closed the editor without drawing an equation it draws on the rerun,
    and one object in sixteen came out of the pass with the 284-byte blank picture still cached. So a failed
    activation is made again, once, against a server of its own: `AttemptActivation` has closed the editor and
    ended its server before it raises, the settle stands between the two, and a second failure raises one
    WordError carrying both attempts' messages, which fails the document as it did before.
    """

    failures = []

    for attempt in range(ActivationAttempts):
        if attempt:
            time.sleep(ActivationSettleSeconds)

        try:
            return AttemptActivation(session, documentPath, document, index, key, deadline)
        except WordError as error:
            failures.append(str(error))

    raise WordError(
        f"Radical Pie did not draw the equation {key} in {ActivationAttempts} activations: {Attempts(failures)}"
    )


def AttemptActivation(session, documentPath: Path, document, index: int, key: str, deadline: float) -> tuple:
    """Activate one object, save it from the editor, close the editor, and return the size Word ends up with.

    The editor is the session's from the moment it is found until it has been seen to exit, which is what
    lets the guard thread end it when the timeout ends the pass in the middle of an activation.
    """

    shape = document.InlineShapes(index)
    blank = (shape.Width, shape.Height)
    running = Pids(ServerImage)

    shape.OLEFormat.Activate()
    session.CheckDialogs()

    pid, window = AwaitEditor(documentPath, running, key, deadline)
    session.AdoptEditor(pid)
    QuietenEditor(window)

    try:
        AwaitPresentation(document, index, blank, pid, window, key, deadline)
    finally:
        PostToEditor(window, win32con.WM_CLOSE, 0)
        EndProcess(pid, min(ExitGraceSeconds, max(deadline - time.monotonic(), 0.0)))
        session.ReleaseEditor(pid)

    shape = document.InlineShapes(index)

    return (shape.Width, shape.Height)


def QuietenEditor(window: int) -> None:
    """Take the editor window off the operator's screen as soon as it appears.

    Word starts the server, so this window is not one the tooling launched and `STARTUPINFO` cannot reach it.
    Measured on 2026-09-11: it opens visible, about 1080 by 720 points over whatever is behind it, and it does
    not take the foreground, which stayed on the window that had it for the whole pass. Minimising it is what
    this process can do to a window of another, and Radical Pie draws the equation and saves it minimised.
    Handing the foreground back was measured as well and is not done here: `SetForegroundWindow` on the window
    that held it is refused to this process, with and without an `AttachThreadInput` to the thread that owns
    the foreground, and it left the foreground on no window at all.
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


def AwaitEditor(documentPath: Path, running: set, key: str, deadline: float) -> tuple:
    """The server this activation started and its editor window, as (pid, window), found by the title.

    Every Radical Pie that starts while the activation runs appears in the process listing the same way, the
    operator's own and the one another agent's render launched included, and the pid taken out of that
    listing used to be whichever was lowest: that one leaves within a couple of seconds, and the pass then
    reported the equation as unreadable. The editor window says which it is, and the whole of its title has
    to say it: `Radical Pie - Equation in <the document file name>` for this document and no other, which is
    the rule `Tools/PowerPoint/Pptx.py` states for its own deck. A title merely starting with the prefix is
    an editor of somebody else's document, opened by a double-click in a Word of the operator's own, and
    this pass would have minimised it, saved it back into that document, closed it and terminated it.

    A server that leaves instead of showing a window has failed the same way one that leaves after showing
    it has, so both say so in the same words. Which of the two happens with an unreadable equation varies
    between runs. The titles that were seen instead go into the message of the timeout, because a title this
    rule does not match is the one failure the rule can cause.

    A candidate that is still alive when this raises is left alone, and there is nothing Windows reports that
    would let it be ended safely. Measured on 2026-09-19 against Word 16: the Radical Pie an activation starts
    has the parent process id of svchost.exe, the DCOM launcher, which is the parent of every local server this
    machine starts through COM and was the parent of this pipeline's own Word as well, so it names no Word
    instance. Its command line is `"...\\RadicalPie.exe" -Embedding`, which says it was started as an OLE
    server and not which client asked for it: the operator double-clicking an equation in a Word of his own
    gets the same command line, where a render of another agent gets a file path instead. So a candidate cannot
    be tied to this run, and ending one would end somebody else's editor.
    """

    title = EditorTitlePrefix + documentPath.name
    candidates = set()
    seen = []

    while time.monotonic() < deadline:
        candidates |= Pids(ServerImage) - running

        for pid in sorted(candidates):
            windows = TopLevelWindows(pid)
            RaiseOnServerDialog(windows)

            for handle, className, windowTitle in windows:
                if className != WindowClass:
                    continue

                if windowTitle == title:
                    Processes.Register(pid)

                    return pid, handle

                if windowTitle not in seen:
                    seen.append(windowTitle)

        if candidates and all(AwaitProcessExit(pid, 0) for pid in candidates):
            raise WordError(f"Radical Pie left without an editor window for {key}: {UnreadableEquation}")

        time.sleep(PollSeconds)

    if not candidates:
        raise WordError(f"Radical Pie did not start when the equation {key} was activated")

    raise WordError(
        f"Radical Pie did not show the editor window titled {title!r} for the equation {key}"
        f" (the windows it showed: {seen})"
    )


def AwaitPresentation(document, index: int, blank: tuple, pid: int, window: int, key: str, deadline: float) -> None:
    """Post File > Save to the editor until Word has a picture of its own for the object.

    Word reports the new presentation as a size that differs from the blank 5.25 by 6.75 points, the height
    first. Radical Pie leaving on its own means it could not read the equation.
    """

    lastPost = 0.0

    while time.monotonic() < deadline:
        RaiseOnServerDialog(TopLevelWindows(pid))
        shape = document.InlineShapes(index)

        if (shape.Width, shape.Height) != blank:
            return

        # The size is read before the server is tested, so a render that lands as the server leaves counts.
        if AwaitProcessExit(pid, 0):
            raise WordError(f"Radical Pie closed the editor without drawing {key}: {UnreadableEquation}")

        if time.monotonic() - lastPost >= RepostSaveSeconds:
            PostToEditor(window, win32con.WM_COMMAND, SaveCommand)
            lastPost = time.monotonic()

        time.sleep(PollSeconds)

    raise WordError(f"Radical Pie drew no picture for the equation {key} before the timeout")


def RaiseOnServerDialog(windows: list) -> None:
    """Turn a dialog of the Radical Pie server into a WordError carrying its text, and close it."""

    for handle, className, title in windows:
        if className == WindowClass:
            continue

        message = DialogText(handle)
        PostClose(handle)

        raise WordError(f"Radical Pie raised a {className} dialog titled {title!r}: {message}")


def CheckPictures(documentPath: Path, expectedCount: int, blankPictureSize: int) -> None:
    """Pass four: every object shows a picture Radical Pie drew, not the blank Word cached."""

    with zipfile.ZipFile(documentPath) as package:
        parts = ReadObjectParts(package)

        if len(parts) != expectedCount:
            raise WordError(f"the finished document holds {len(parts)} Radical Pie objects, expected {expectedCount}")

        for _, picturePart in parts:
            size = len(package.read(picturePart))

            if size <= blankPictureSize:
                raise WordError(
                    f"{picturePart} is {size} bytes, no larger than the {blankPictureSize}-byte blank picture,"
                    " so that object was not drawn"
                )


class WordSession:
    """A hidden Word instance of this pipeline's own, watched by one thread and terminated on every path.

    The thread does two jobs that both have to happen while a COM call is in flight: it closes the modal
    dialogs that would block that call for ever, recording their text for the step to fail with, and at the
    deadline it terminates the processes, which is what turns a blocked COM call into an error.

    `Options.SmartCutPaste` is the user's own setting and Word keeps it outside the document, so the session
    records it, turns it off for its own deletions, and writes the recorded value back before Word quits.

    Nothing restores it where the guard thread terminated Word first, and nothing has to. Measured on
    2026-09-19 against Word 16: a Word that sets the option and quits through `Quit` hands the new value to the
    next Word that starts, and a Word that sets it and is terminated hands over nothing, the next Word reading
    the value the user had. So a terminated session leaves the user's setting as it found it, and a restore
    would need a Word of its own started on the failure path to write a value that was never changed.
    """

    def __init__(self, deadline: float):
        self.deadline = deadline
        self.application = None
        self.smartCutPaste = None
        self.dialogs = []
        self.wordPids = set()
        # The editors this session's activations adopted, by pid. The guard thread reads it while the main
        # thread adds to it, so both go through the lock.
        self.editorPids = set()
        self.editorLock = threading.Lock()
        self.timedOut = False
        self.stop = threading.Event()

    def __enter__(self):
        pythoncom.CoInitialize()
        running = Pids(WordImage)

        try:
            self.application = win32com.client.DispatchEx("Word.Application")
            # Recorded before the first property is set, because a failure past this line has a Word to end.
            self.wordPids = Pids(WordImage) - running

            for pid in self.wordPids:
                Processes.Register(pid)

            self.application.Visible = False
            self.application.DisplayAlerts = 0
            self.smartCutPaste = self.application.Options.SmartCutPaste
            self.application.Options.SmartCutPaste = False
        except pythoncom.com_error as error:
            self.application = None
            pythoncom.CoUninitialize()
            self.Terminate()

            raise WordError(f"Word did not start: {ComErrorText(error)}") from None

        threading.Thread(target=self.Watch, daemon=True).start()

        return self

    def __exit__(self, exceptionType, exceptionValue, traceback):
        self.stop.set()

        if self.application is not None:
            # A terminated Word fails both of these, and the restore must not cost the Quit. Nothing takes the
            # restore anywhere else: the option only reaches the user's settings through a Word that quits
            # cleanly, so the value this session turned off went nowhere (measured 2026-09-19, the class
            # docstring).
            try:
                self.application.Options.SmartCutPaste = self.smartCutPaste
            except pythoncom.com_error:
                pass

            try:
                self.application.Quit(WdDoNotSaveChanges)
            except pythoncom.com_error:
                pass

        self.application = None
        pythoncom.CoUninitialize()
        self.Terminate()

        if exceptionType is None and self.timedOut:
            raise WordError("Word did not answer within the timeout and was terminated")

        return False

    def Watch(self) -> None:
        while not self.stop.is_set():
            for pid in self.wordPids:
                for handle, className, title in TopLevelWindows(pid):
                    if className in WordDialogClasses:
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
            raise WordError("Word raised a modal dialog: " + "; ".join(self.dialogs))

    def Explain(self, step: str, error) -> str:
        """A COM failure in this pipeline's terms, with the dialog that caused it when there was one."""

        if self.timedOut:
            return f"Word did not answer while {step} and was terminated"

        detail = "; ".join(self.dialogs)

        return f"Word failed while {step}: {ComErrorText(error)}" + (
            f" after a modal dialog: {detail}" if detail else ""
        )

    def AdoptEditor(self, pid: int) -> None:
        """Take responsibility for the editor of one activation, so a timeout ends it with the session."""

        with self.editorLock:
            self.editorPids.add(pid)

    def ReleaseEditor(self, pid: int) -> None:
        """Give up an editor the activation has already ended."""

        with self.editorLock:
            self.editorPids.discard(pid)

    def Terminate(self) -> None:
        """End this session's Word and the editors its own activations adopted. Nothing else is touched.

        This used to end every `RadicalPie.exe` that was not in the process listing when the session began,
        which killed the equation the operator had open and the renders of other agents, whose servers
        appear in that listing in exactly the same way (R5-1 and R4-1 of the review of 2026-09-14). An
        editor is this session's only when `AwaitEditor` found it by a window title naming this document,
        which is the rule `Tools/PowerPoint/Pptx.py` states, and `AttemptActivation` gives it up as soon as
        it has ended it. What is left here is the editor of an activation the guard thread cut short.

        `TerminateProcess` only posts the termination; the process is still listed for a moment afterwards,
        so a kill is followed by another wait rather than trusted to have finished by the time this returns.
        """

        for pid in sorted(self.wordPids):
            EndProcess(pid, ExitGraceSeconds)

        with self.editorLock:
            editors = sorted(self.editorPids)

        for pid in editors:
            EndProcess(pid, ServerExitGraceSeconds)
            self.ReleaseEditor(pid)


def EndProcess(pid: int, graceSeconds: float) -> None:
    """End one process and drop it from the registry, once its exit has been seen.

    `TerminateProcess` only posts the termination, so the kill is followed by another wait rather than
    trusted; a pid this does not see go stays registered, and the live tests' fixture reports it.
    """

    if not AwaitProcessExit(pid, graceSeconds):
        KillProcess(pid)

        if not AwaitProcessExit(pid, graceSeconds):
            return

    Processes.Release(pid)


def Pids(image: str) -> set:
    """The process ids of one image name."""

    listing = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {image}", "/NH", "/FO", "CSV"],
        capture_output=True,
        text=True,
    ).stdout
    prefix = '"' + image.split(".")[0]

    return {int(line.split('","')[1]) for line in listing.splitlines() if line.startswith(prefix)}


def ComErrorText(error) -> str:
    detail = error.args[2][2] if len(error.args) > 2 and error.args[2] else None

    return f"{error.args[0] & 0xFFFFFFFF:#010x} {error.args[1]}" + (f" / {detail}" if detail else "")

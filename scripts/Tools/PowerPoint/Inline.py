"""The measured rules an inline equation on a slide stands on, and the COM calls that reach them.

`Tools.PowerPoint.Pptx` is the pipeline; this module is the arithmetic it places an inline object by, and
the two awkward COM calls that arithmetic needs. Everything here was measured on 2026-09-17 against
PowerPoint 16 by the two inline probes, whose decks, exports and tables the operator keeps outside the
repository under `Skill/radical-pie-workspace/inline-probe-1` and `inline-probe-2`; every number the rules
turn on is repeated in the comment beside it, so the code stands without them.

Five rules and one workaround:

- The horizontal gap is a tab whose stop stands at the end of the text before it plus the object's width
  plus twice a padding of 0.16 of the font size, measured from the shape's left plus the text frame's left
  margin. The stop lands the text after the gap where it is asked to within 0.025 pt over 144 rows of
  twelve fonts and three sizes, and needs no font metrics at all.
- The padding on one side goes where something already stands between the object and the text there: a
  space the author wrote, or a punctuation mark, a comma, a full stop or a closing bracket right after the
  gap and an opening bracket right before it. That is the operator's ruling of 2026-09-18 and not a
  measurement. A space is the gap a word gets, so the padding beside it would be a second gap; a mark
  belongs inside the equation as its last symbol, which is what the skill's `references/OutputForms.md`
  tells a caller to write, and this is what the deck gets where the author left the mark in the text.
- How far a line of prose inks either side of its own baseline, which is what an inline equation has to
  clear: the tallest of the font's cap height and the tops of `d` and `l` above it, and the deepest of the
  bottoms of `p` and `g` below it, all from the font file the baseline share already comes from. At 18 pt
  that is 12.244 and 3.208 pt for Calibri, 12.577 and 3.929 for Cambria, 12.497 and 3.885 for Times New
  Roman, each within 0.05 pt of the ink measured off an export of the line `Hdlfbk ABQM pgqyj` at 18 pt
  (2026-09-18). Aptos has no font file on this machine and takes the measured pair, as its baseline share
  does. The room a line leaves an equation is its box less that ink: 1.50 pt above the baseline and 4.56
  below it for Calibri at 18 pt, 0.16 and 4.88 for Cambria, 0.32 and 4.90 for Times New Roman, 1.68 and
  4.62 for Aptos.
- The text baseline inside a line box is `box - descent` for a box no taller than the natural line
  `1.2 * size`, and `0.75 * box` for a taller one, plus the paragraph's space before when the gap stands on
  the first line of a paragraph that is not the frame's first. The worst error of that rule over the 36
  exactly spaced lines, the 36 percentage spaced lines and the 27 placed objects of the second probe is
  0.080 pt. The object's top is that baseline less `height - depth` from the render.
- The descent is `(1.2 - share) * size`, where `share` is the share of the font size the baseline sits
  below the top of a natural line. It is a property of the font file and not of GDI: placing by GDI's
  `tmAscent` put 100 of the first probe's 144 rows more than 0.5 pt out, by up to 5.13 pt, where the share
  derived from the font's own `OS/2` table is within 0.0027 em of the measured share for every font on this
  machine, 0.05 pt at 18 pt.
- `TextFrame2` is not reachable through pywin32's dynamic dispatch, and the per-paragraph tab stops and
  the per-paragraph spacing live there alone: `TextFrame.Ruler.TabStops` is the whole frame's collection
  and a stop added to it is taken by every paragraph. `PropertyWithArguments` and `TabStopItem` are the
  two calls that reach the paragraph, and the COM errors they avoid are named in their own comments.
"""

import math
import struct
import winreg
from dataclasses import dataclass
from pathlib import Path

import pythoncom
import win32com.client

# The padding either side of an inline object, a thin space of the run's size. The first probe measured the
# space between the object's right edge and the text after it at 2.24 to 3.86 pt for text at 14 to 24 pt,
# within 0.025 pt of 0.16 of the size asked for, over all 144 rows.
# A point is 1/72 inch and an inch 25.4 mm; an EMF frame is kept in hundredths of a millimetre.
MillimetresPerPoint = 25.4 / 72.0

PaddingShare = 0.16

# The marks that stand against an inline object instead of after its padding, by the operator's ruling of
# 2026-09-18. A quotation mark is in both sets and the side it stands on says which one it is; the straight
# quote is there because an author's text carries whichever of the two the tool that wrote it typed.
ClosingMarks = frozenset(",.;:!?)]}”’\"'")
OpeningMarks = frozenset("([{“‘\"'")

# The space an author writes beside the placeholder, as he would beside a word. It is the gap, so the
# padding on that side goes with it (the operator, 2026-09-18).
Space = " "

# The measure-set-measure loop. Setting a stop changes the width of the tab, which can move the line break,
# which moves the text before the gap: on the first probe's `narrowB` case it moved 16.7 pt and onto
# another line, and the object, placed from the measurement taken before the stop went in, stood outside
# the box. Seven of that probe's eight wrapped cases settle on the first try; a centred or right-aligned
# paragraph never settles, which is the same test as refusing it.
StopAttempts = 4
StopTolerance = 0.05

# PowerPoint's natural line is 1.2 times the font size, measured at twelve fonts and three sizes, and the
# baseline of a line box taller than that stands at three quarters of it whatever the font: against the
# second probe's 36 exactly spaced lines "all the extra space below the baseline" is out by up to 43.16 pt,
# "all above" by 15.93, "split evenly" by 13.96, and three quarters of the pitch by 0.080.
NaturalLine = 1.2
BaselineShareOfLine = 0.75

# How far a line box may stand above the natural line and still count as level with it, which is the
# measuring export's own resolution at 16.67 pixels to the point.
BoxTolerance = 0.05

# Two lines whose tops stand this close are one line. A line box is never smaller than about 9 pt here.
SameLineTolerance = 0.5

MsoFalse = 0
MsoTrue = -1
MsoTabStopLeft = 1
MsoAlignLeft = 1
MsoAlignCenter = 2
MsoAlignRight = 3
MsoAlignJustify = 4

# The alignments an inline gap cannot be placed in. The second probe set a stop on a centred and on a
# right-aligned paragraph: in the centred one the text after the gap moved 57 pt as the stop went in and
# never settled, in the right-aligned one the stop changed nothing at all and the space after the object
# came out at 55.38 pt instead of the 2.88 asked for.
RefusedAlignments = (MsoAlignCenter, MsoAlignRight, MsoAlignJustify)

# Where Windows records an installed font file. A machine-wide font is a bare file name under the system
# font directory; a font the user installed carries its full path.
FontRegistryKeys = (
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"),
)
SystemFontDirectory = Path(r"C:\Windows\Fonts")

# The registry names a font file by family and style. A slanted style is never the upright the text is
# drawn in, and these four words name the upright face of the families on this machine: New Computer
# Modern 10 ships Book rather than Regular, and Montserrat ships its variable file under Thin.
SlantedStyles = ("italic", "oblique")
UprightStyles = ("regular", "book", "roman", "normal")

# Bit 7 of `OS/2` `fsSelection`, USE_TYPO_METRICS, which says the typographic metrics are the ones to lay
# text out with. Off, the Windows metrics are (Calibri, Cambria, Times New Roman, Arial and Roboto here);
# on, the typographic ascender with its line gap added is (Open Sans, Lato, Poppins and Inter). Poppins is
# the font that showed the line gap belongs in the sum: 1.2 * (1050 + 100) / (1050 + 350 + 100) = 0.920
# against 0.92048 measured.
UseTypoMetrics = 0x80

# The share of the font size the text baseline sits below the top of a natural line, measured off a 16.67
# pixel per point export by the first probe, twelve fonts at 14, 18 and 24 pt, the same share at all three
# sizes to within 0.0025 em. It is the fallback for a font PowerPoint draws that this machine has no file
# for: Aptos is in neither font registry key and not in Office's `vfs\Fonts\private`, GDI substitutes Arial
# for it (share 0.97290) and PowerPoint draws it at 0.92242.
MeasuredAscentShares = {
    "Calibri": 0.93869,
    "Cambria": 0.97290,
    "Aptos": 0.92242,
    "Times New Roman": 0.96532,
    "Arial": 0.97290,
    "New Computer Modern 10": 0.95468,
    "Montserrat": 0.95242,
    "Open Sans": 0.94290,
    "Roboto": 0.95048,
    "Lato": 0.98663,
    "Poppins": 0.92048,
    "Inter": 0.96000,
}

# How far a line of prose inks above and below its own baseline, as shares of the font size, for a font this
# machine holds no file for. Aptos is that font, as it is for the baseline share above: measured off a 2000 by
# 9000 export of the line `Hdlfbk ABQM pgqyj` at 18 pt on 2026-09-18, ink 11.984 pt above the baseline and
# 3.316 below it.
MeasuredInkShares = {"Aptos": (0.66578, 0.18422)}

# The least room an inline equation's ink leaves between itself and the ink of the line above or the line
# below, as a share of the text size. Without it the rule is ink meeting ink: both wrapped decks of the cold
# start of 2026-09-18 opened their paragraph and the bar over the radical came out on the descenders of the
# line above (`radical-pie-workspace/coldstart-3/Collision.png`). That case rebuilt at 0.00, 0.10, 0.15 and
# 0.20 of an 18 point line and exported at 300 dpi put the equation's ink 1.44, 3.60, 3.60 and 4.56 points
# off the ink above, on a paragraph opened to 36, 38, 38 and 39 points (measured 2026-09-18). 0.15 is the
# value: the opening is asked for in whole points, 0.10 and 0.15 buy the same 38 point line here, and 0.20
# costs a point of line spacing for a gap the eye does not ask for.
ClearanceShare = 0.15

# The glyphs the ink of a line is taken from, with the font's own cap height beside them. `d` and `l` carry
# the ascender, which stands above the cap height in every font measured, and `p` and `g` the descender. `f`
# overshoots `l` by 0.0034 em in Calibri and 0.0025 in Cambria, 0.06 pt at 18 pt, which is under the export's
# own resolution and under the whole point an opening is asked for.
InkGlyphs = "dlpg"

# What reading the ink out of a font file needs: the outlines themselves, their index, the character map and
# the units per em. A font whose outlines are CFF rather than TrueType carries no `glyf` and no `loca`.
InkTables = frozenset({"glyf", "loca", "cmap", "head", "OS/2"})

# The `cmap` subtables that map Unicode, in the order a font lists them. Only format 4 is read, which is the
# format all twelve fonts of the first probe carry their Latin letters in.
UnicodeEncodings = frozenset({(3, 1), (0, 3), (0, 4)})
CharacterMapFormat = 4

# `OS/2` carries `sCapHeight` from version 2 on.
CapHeightVersion = 2

FontFiles = None
AscentShares = {}
InkShares = {}


@dataclass(frozen=True)
class ParagraphFormat:
    """One paragraph's spacing and alignment as `TextFrame2` reports it, each space in points or in lines."""

    alignment: int
    spaceWithin: float
    lineRuleWithin: int
    spaceBefore: float
    lineRuleBefore: int
    spaceAfter: float
    lineRuleAfter: int


def Padding(fontSize: float) -> float:
    """The thin space either side of an inline object, rounded to the hundredth of a point as the probe did."""

    return round(PaddingShare * fontSize, 2)


def Clearance(fontSize: float) -> float:
    """The least room between an inline equation's ink and the ink of the line above or the line below."""

    return ClearanceShare * fontSize


def GapPaddings(fontSize: float, before: str, after: str) -> tuple:
    """The padding on each side of an inline gap, dropped on a side a space or a punctuation mark stands on.

    `before` and `after` are the one character on each side of the gap in the shape's own text, either of them
    empty where the gap begins or ends that text. A space there is the word gap the sentence already carries
    and the padding would stand on top of it; a mark there belongs against the object. A paragraph mark and a
    line break are neither, so a gap at the edge of a line keeps both paddings.
    """

    padding = Padding(fontSize)
    leading = 0.0 if before == Space or before in OpeningMarks else padding
    trailing = 0.0 if after == Space or after in ClosingMarks else padding

    return leading, trailing


def DrawnWidth(renderedWidth: float) -> float:
    """The width PowerPoint gives an object drawn from a render of `renderedWidth` points.

    The picture's frame is kept in hundredths of a millimetre, rounded up, and the shape's extent is that frame
    on the nearest eighth of a point (369 of 369 unscaled shapes of the operator's deck, 2026-09-13). The
    millimetre step is what a bare rounding to the eighth misses: a render of 28.0480 points is 9.8947 mm, kept
    as 9.90 mm, which is 28.063 points and draws at 28.125 where the bare rounding gives 28 (the cold start of
    2026-09-18). Nine of nine measured pairs follow this rule, the first probe's eight among them: 39.5285
    drawn as 39.5, 75.8244 as 75.875.
    """

    hundredths = math.ceil(renderedWidth * MillimetresPerPoint * 100.0 - 1e-9)

    return round(hundredths / 100.0 / MillimetresPerPoint * 8.0) / 8.0


def LineBox(fontSize: float, spaceWithin: float, lineRuleWithin: int) -> float:
    """The height PowerPoint lays one line of a paragraph out at, from the spacing it reports.

    A spacing in lines is taken of the natural line and is not quantised: 0.9 lines at 18 pt, which is what
    the body placeholder of the Office theme carries, is exactly 19.44. A spacing in points is rounded to a
    whole point, half up: of the second probe's 24 spacings 21.6 laid out at 22, 20.5 at 21, 20.4 at 20,
    49.5 at 50 and 79.4 at 79, which is why an opening asks for a whole number of points.
    """

    if lineRuleWithin:
        return spaceWithin * NaturalLine * fontSize

    return float(math.floor(spaceWithin + 0.5))


def BaselineOffset(fontSize: float, share: float, box: float) -> float:
    """How far the text baseline stands below the top of one line box, the space before not counted.

    Two branches, and the box decides. A box no taller than the natural line keeps the font's own descent
    below the baseline, which is `share * size` when the box is the natural line itself and `box - descent`
    when it is shorter: 0.9 lines in a body placeholder puts the Calibri baseline at 19.44 - 4.704 = 14.736
    against 14.78 measured. A taller box puts the baseline at three quarters of it whatever the font is, at
    1.5 lines and at the exact spacings 22, 50 and 80 pt alike.
    """

    natural = NaturalLine * fontSize

    if box <= natural + BoxTolerance:
        return box - (natural - share * fontSize)

    return BaselineShareOfLine * box


def SpacePoints(value: float, lineRule: int, fontSize: float) -> float:
    """A paragraph space before or after in points, whichever unit the paragraph carries it in."""

    return value * NaturalLine * fontSize if lineRule else value


def AscentShare(font: str) -> float:
    """The share of the font size the baseline sits below a natural line's top, or `None` for a font
    neither the machine's font files nor the first probe's measurement knows.

    The font file is the first source: `1.2 * ascent / (ascent + descent)` from `OS/2`, which is within
    0.0027 em of the measured share for all eleven of the probe's fonts this machine holds a file for, the
    worst being Calibri at 0.936 derived against 0.93869 measured, 0.05 pt at 18 pt. The measured table is
    the second, for a font PowerPoint draws that has no file here.
    """

    if font not in AscentShares:
        AscentShares[font] = DerivedAscentShare(font)

    if AscentShares[font] is not None:
        return AscentShares[font]

    return MeasuredAscentShares.get(font)


def DerivedAscentShare(font: str) -> float:
    """The share read out of the font's own file, or `None` when the machine has no file for the font."""

    path = FontFilePath(font)

    if path is None:
        return None

    metrics = FontMetrics(path)

    if metrics["useTypoMetrics"]:
        ascent = metrics["typoAscender"] + metrics["typoLineGap"]
        descent = -metrics["typoDescender"]
    else:
        ascent = metrics["windowsAscent"]
        descent = metrics["windowsDescent"]

    if ascent + descent <= 0:
        return None

    return NaturalLine * ascent / (ascent + descent)


def InkRoom(font: str, fontSize: float) -> tuple:
    """How far a line of text inks above and below its own baseline, in points.

    The font file is the first source and the measured table the second, as they are for the baseline share.
    A font neither source knows falls back to the whole line box, the line's own ascent and descent, which is
    what the pipeline compared against before the ink was measured: it opens a paragraph an equation would
    have cleared rather than letting one collide.
    """

    if font not in InkShares:
        InkShares[font] = DerivedInkShares(font)

    shares = InkShares[font] if InkShares[font] is not None else MeasuredInkShares.get(font)

    if shares is None:
        share = AscentShare(font)

        return share * fontSize, (NaturalLine - share) * fontSize

    return shares[0] * fontSize, shares[1] * fontSize


def DerivedInkShares(font: str):
    """The tallest and the deepest ink of a line, as shares of the font size, out of the font's own file.

    `None` where the machine has no file for the font, where the file carries CFF outlines rather than
    TrueType ones, and where its character map has no Unicode subtable in format 4.
    """

    path = FontFilePath(font)

    if path is None:
        return None

    data = path.read_bytes()
    tables = FontTables(data, 0)

    if not InkTables.issubset(tables):
        return None

    subtable = CharacterMapSubtable(data, tables)

    if subtable is None:
        return None

    unitsPerEm = struct.unpack_from(">H", data, tables["head"] + 18)[0]
    longLoca = struct.unpack_from(">h", data, tables["head"] + 50)[0]
    version = struct.unpack_from(">H", data, tables["OS/2"])[0]
    tops = [struct.unpack_from(">h", data, tables["OS/2"] + 88)[0]] if version >= CapHeightVersion else []
    bottoms = []

    for character in InkGlyphs:
        glyph = GlyphIndex(data, subtable, character)
        bounds = None if glyph is None else GlyphBounds(data, tables, longLoca, glyph)

        if bounds is not None:
            bottoms.append(bounds[0])
            tops.append(bounds[1])

    if not tops or not bottoms:
        return None

    return max(tops) / unitsPerEm, -min(bottoms) / unitsPerEm


def CharacterMapSubtable(data: bytes, tables: dict):
    """The offset of the font's Unicode character map in format 4, or `None` when it carries none."""

    start = tables["cmap"]
    count = struct.unpack_from(">H", data, start + 2)[0]

    for index in range(count):
        platform, encoding, offset = struct.unpack_from(">HHI", data, start + 4 + 8 * index)
        known = (platform, encoding) in UnicodeEncodings

        if known and struct.unpack_from(">H", data, start + offset)[0] == CharacterMapFormat:
            return start + offset

    return None


def GlyphIndex(data: bytes, subtable: int, character: str):
    """One character's glyph in a format 4 character map, or `None` where the font draws no glyph for it.

    The format holds the segments the map is cut into, their ends, their starts, a delta to add to the
    character inside a segment, and an offset into the glyph array that follows for a segment the delta
    cannot describe. The segments are in order and the first whose end is not below the character is its own.
    """

    code = ord(character)
    segments = struct.unpack_from(">H", data, subtable + 6)[0] // 2
    ends = subtable + 14
    starts = ends + 2 * segments + 2
    deltas = starts + 2 * segments
    ranges = deltas + 2 * segments

    for index in range(segments):
        if code > struct.unpack_from(">H", data, ends + 2 * index)[0]:
            continue

        first = struct.unpack_from(">H", data, starts + 2 * index)[0]

        if code < first:
            return None

        delta = struct.unpack_from(">h", data, deltas + 2 * index)[0]
        offset = struct.unpack_from(">H", data, ranges + 2 * index)[0]

        if not offset:
            return (code + delta) & 0xFFFF

        glyph = struct.unpack_from(">H", data, ranges + 2 * index + offset + 2 * (code - first))[0]

        return None if not glyph else (glyph + delta) & 0xFFFF

    return None


def GlyphBounds(data: bytes, tables: dict, longLoca: int, glyph: int):
    """The bottom and the top of one glyph's outline in font units, or `None` for a glyph with no outline.

    `loca` holds one offset per glyph and the next offset is where that glyph ends, so a glyph whose two
    offsets are equal draws nothing; the space is that glyph. The offsets are halved when `head` says the
    file keeps them short.
    """

    if longLoca:
        first, last = struct.unpack_from(">II", data, tables["loca"] + 4 * glyph)
    else:
        first, last = (value * 2 for value in struct.unpack_from(">HH", data, tables["loca"] + 2 * glyph))

    if first == last:
        return None

    _, _, yMin, _, yMax = struct.unpack_from(">5h", data, tables["glyf"] + first)

    return yMin, yMax


def FontFilePath(font: str):
    """The file of one font family's upright face, or `None` when the registry does not name it.

    A variable font is registered under the style its file is named after rather than the instance
    PowerPoint draws: Montserrat is `Montserrat Thin`, and the `OS/2` metrics of the file are the same for
    every instance of it, which is what makes taking the family's one upright file right.
    """

    global FontFiles

    if FontFiles is None:
        FontFiles = RegisteredFontFiles()

    wanted = font.lower()
    prefix = wanted + " "
    candidates = []

    for name, value in FontFiles.items():
        for face in (item.strip() for item in name.rsplit("(", 1)[0].split("&")):
            style = face.lower()

            if style == wanted:
                candidates.append((0, 0, value))
            elif style.startswith(prefix) and not any(word in style for word in SlantedStyles):
                rank = 1 if style[len(prefix) :] in UprightStyles else 2
                candidates.append((rank, len(style), value))

    for _, _, value in sorted(candidates):
        path = Path(value)
        path = path if path.is_absolute() else SystemFontDirectory / path

        if path.exists():
            return path

    return None


def RegisteredFontFiles() -> dict:
    """Every installed font's registry name and the file behind it, the machine's fonts and the user's."""

    files = {}

    for root, keyPath in FontRegistryKeys:
        try:
            key = winreg.OpenKey(root, keyPath)
        except OSError:
            continue

        try:
            for index in range(winreg.QueryInfoKey(key)[1]):
                name, value, _ = winreg.EnumValue(key, index)
                files.setdefault(name, value)
        finally:
            winreg.CloseKey(key)

    return files


def FontMetrics(path: Path) -> dict:
    """The `OS/2` metrics of one font file, in font units, with the flag that says which pair to use."""

    data = path.read_bytes()
    tables = FontTables(data, 0)
    start = tables["OS/2"]
    typoAscender, typoDescender, typoLineGap = struct.unpack_from(">hhh", data, start + 68)
    windowsAscent, windowsDescent = struct.unpack_from(">HH", data, start + 74)
    selection = struct.unpack_from(">H", data, start + 62)[0]

    return {
        "typoAscender": typoAscender,
        "typoDescender": typoDescender,
        "typoLineGap": typoLineGap,
        "windowsAscent": windowsAscent,
        "windowsDescent": windowsDescent,
        "useTypoMetrics": bool(selection & UseTypoMetrics),
    }


def FontTables(data: bytes, offset: int) -> dict:
    """The table directory of a font file, following a font collection to its first font (Cambria is one)."""

    if data[offset : offset + 4] == b"ttcf":
        return FontTables(data, struct.unpack_from(">I", data, offset + 12)[0])

    count = struct.unpack_from(">H", data, offset + 4)[0]
    tables = {}

    for index in range(count):
        record = offset + 12 + 16 * index
        name = data[record : record + 4].decode("latin-1")
        tables[name] = struct.unpack_from(">I", data, record + 8)[0]

    return tables


def PropertyWithArguments(dispatch, name: str, *arguments):
    """One property that takes arguments, reached through `Invoke` because an attribute cannot reach it.

    `TextFrame2.TextRange.Paragraphs(n, 1)` is a property with arguments on an object pywin32 has no type
    information for, and the dynamic dispatch has no way to pass them: reading the attribute returns the
    property with its arguments defaulted, which is the whole range, and calling that object invokes its
    default member instead, which PowerPoint answers with `0x80020011 Does not support a collection`.
    Flagging the name as a method sends `DISPATCH_METHOD` and PowerPoint answers `0x80020003 Member not
    found`, because the member is a property. So the dispid is looked up and invoked by hand (measured
    2026-09-17; the old `TextFrame.TextRange.Paragraphs(n, 1)` needs none of this and carries neither the
    paragraph's own tab stops nor its spacing under a name this code can set).
    """

    dispid = dispatch._oleobj_.GetIDsOfNames(name)
    value = dispatch._oleobj_.Invoke(dispid, 0, pythoncom.DISPATCH_PROPERTYGET, True, *arguments)

    return win32com.client.Dispatch(value)


def Paragraph2(shape, index: int):
    """One paragraph of a shape as `TextRange2`, which carries its own tab stops and its own spacing."""

    return PropertyWithArguments(shape.TextFrame2.TextRange, "Paragraphs", index, 1)


def TabStopItem(stops, index: int):
    """One stop of the paragraph's collection.

    `TextFrame.Ruler.TabStops.Item` is reachable as an attribute; MSO's `TabStops2.Item` is not, and needs
    the name flagged as a method (measured 2026-09-17).
    """

    try:
        return stops.Item(index)
    except (pythoncom.com_error, AttributeError, TypeError):
        stops._FlagAsMethod("Item")

        return stops.Item(index)


def ReadParagraphFormat(shape, index: int) -> ParagraphFormat:
    """The spacing and the alignment of one paragraph, read through `TextFrame2`."""

    paragraphFormat = Paragraph2(shape, index).ParagraphFormat

    return ParagraphFormat(
        paragraphFormat.Alignment,
        paragraphFormat.SpaceWithin,
        paragraphFormat.LineRuleWithin,
        paragraphFormat.SpaceBefore,
        paragraphFormat.LineRuleBefore,
        paragraphFormat.SpaceAfter,
        paragraphFormat.LineRuleAfter,
    )


def ParagraphStops(shape, index: int) -> list:
    """The tab stops of one paragraph alone, in the order the collection holds them.

    A stop added here belongs to this paragraph: with one at 209.88 on paragraph 2 the frame's ruler
    reported no stops at all and paragraph 1's own tab still went to the default stop at 144 pt. A stop
    added to `TextFrame.Ruler.TabStops` is reported by every paragraph of the frame instead, which is why
    the ruler cannot carry a second gap on a second line (measured 2026-09-17).
    """

    stops = Paragraph2(shape, index).ParagraphFormat.TabStops

    return [TabStopItem(stops, number).Position for number in range(1, stops.Count + 1)]


def SetParagraphStops(shape, index: int, positions: list) -> None:
    """The paragraph's stops cleared and set to `positions`, the author's own among them.

    The collection is cleared and rebuilt rather than edited in place, which is the route the probe
    measured. An author's stop at 200 pt went back with the gap's own stop at 451.77 and the author's tab
    landed where it had, so what was there is what the caller has to put back.
    """

    stops = Paragraph2(shape, index).ParagraphFormat.TabStops

    while stops.Count:
        TabStopItem(stops, 1).Clear()

    for position in sorted(positions):
        stops.Add(MsoTabStopLeft, position)


def SetExactSpacing(shape, index: int, points: float) -> None:
    """One paragraph's line spacing, in whole points, which is how PowerPoint lays an exact spacing out."""

    paragraphFormat = Paragraph2(shape, index).ParagraphFormat
    paragraphFormat.LineRuleWithin = MsoFalse
    paragraphFormat.SpaceWithin = points


def SetSpaceAfter(shape, index: int, points: float) -> None:
    """One paragraph's space after, in points. It stands inside the last line's box below the baseline.

    It is the only paragraph space the pipeline sets. The gap between two paragraphs is one gap, and the
    space after the earlier one and the space before the later one both stand in it, so setting each side's
    need would open it twice; the earlier paragraph's space after carries the larger of the two.
    """

    paragraphFormat = Paragraph2(shape, index).ParagraphFormat
    paragraphFormat.LineRuleAfter = MsoFalse
    paragraphFormat.SpaceAfter = points

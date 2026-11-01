"""Which font each `F` slot of a design resolves to under Radical Pie 1.16, read off this machine.

Radical Pie 1.16 resolves a font name against its font database, `%LOCALAPPDATA%\\RadicalPie\\fonts.pie`, one
record per installed font file, `R (n="file"[,c]) { s{"name"} ... }`, where a collection carries the flag `c`
and one name per font in it. A name matches a record's name ID 4, as F — Font Structure states, or the stem of
a `.ttf` or `.otf` file, the name with one of those extensions appended, case insensitively. Measured on the
released 1.16.0 on 2026-10-16: `"NewCM10-Book"` and `"DavidCLM-Medium"` (an `.otf`) draw their fonts and are
written back as their name ID 4, `"arialbd"` as `i16{8}`; the name with its extension, `"NewCM10-Book.ttf"`,
and the stem of a collection, `"msgothic"`, match nothing. A family, `"Lato"`, matches only where it is a name
ID 4 as well. A slot that matches nothing is drawn in Times and written back as `i16{2}`. An `int16` names
one of the 84 known fonts below by its id, and a `uint8` is still read in the 1.15 numbering through the
translation table below.

A font draws from its `.slug`, which Radical Pie builds with `slugfont.exe` the first time a design names the
font. The 1.16 slugs are named by the font file's stem in `%LOCALAPPDATA%\\RadicalPie`, a 1.15 slug named by
its family is reused where the two names agree case insensitively, and the known fonts Radical Pie ships carry
slugs named by their id under the install directory's `Data`. A collection whose fonts share glyphs makes one
`<stem>.slug`, and the developer says a collection of separate fonts makes `<stem>.slug`, `<stem>1.slug` and
so on; the second font of a collection imports on its own (`"Yu Gothic UI Light"` built `YuGothL.slug`,
2026-10-16). The first render of a font with no slug yet draws Times and writes back `i16{2}`, because the
import finishes after the save; the render pipelines wait for the import and render again from a second launch
instead (`Tools.Render.FontImport`). A slug is 0 bytes while its `slugfont.exe` builds it, and one stopped
mid-build leaves it so, which crashes the editor whenever a design names the font (Report item 2).

`CheckDesign` gives one `SlotReport` per `F` slot of an equation, `FindFonts` the fonts whose name or file name
holds a set of words, each with its name ID 4 and the file stem that resolves to it, `TimesFallbacks` the slots
a written-back design shows were drawn in Times, and
`FontWarnings` the warning lines a render pipeline attaches to an output drawn with such a slot, one per slot,
each naming the slot, what the design wrote, that Radical Pie drew it in Times and the closest installed names,
and one line for each slot the SVG, PDF and EMF pipelines found still not imported after their last launch.
A `fonts.pie` that is missing, truncated, locked or not UTF-8 is no database to every caller: `FontWarnings`
then reads the write-back against the known names, and `Main` prints the reason and exits 1. The closest names
are scored on the words that name a family, with the style and vendor words (Regular, Italic, Bold, Pro, Std
and the like) left out; a name whose family words begin with an installed family's is offered that family's
fonts by whole-name likeness, and one whose family words neither match nor begin with anything installed gets
no suggestion at all.
A pipeline's command line prints those lines on stderr and exits with `FallbackExitCode`, which no other failure
of a pipeline uses, so the caller has the file and cannot read the run as a success. `Main` is the command line
behind `scripts/Fonts.py`, `check` and `find`, and `python -m Tools.PieFormat.Fonts` runs it too. Nothing here
starts a program; the rule, and the decision to warn and ask the user rather than refuse, are ADR-0015's.
"""

import difflib
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import OpenDdl

# Where Radical Pie is installed, the one line of the tooling that names it: `Tools.Render.Svg` launches the
# executable in it and the font check reads the slugs it ships, and Skill/RadicalPie/README.md sends an
# installation anywhere else here.
RadicalPieDirectory = Path(r"C:\Program Files\RadicalPie")
ShippedSlugDirectory = RadicalPieDirectory / "Data"

# The 84 known fonts of Radical Pie 1.16, by the id an `int16` names them with: the table F — Font Structure
# prints, which Tests/PieFormat/FontsTest.py compares against References/Docs/Text/FileFormat.md. The released
# RadicalPie.exe 1.16.0 holds the same table as 33-byte records, a flag byte and a 32-byte name, from file
# offset 0x142f41, and Tests/VendorFacts/VendorFactsTest.py re-reads it there (2026-10-16); the beta of
# 2026-10-08 ordered the Euclid and Euclid Symbol faces differently. Ids 6, 15, 26, 30 and 44 rendered the
# same geometry as the names (2026-10-08), and names came back written as 2, 8, 21, 25, 48, 49 and 57.
KnownFonts = (
    "Radical",
    "Symbol",
    "Times New Roman",
    "Times New Roman Italic",
    "Times New Roman Bold",
    "Times New Roman Bold Italic",
    "Arial",
    "Arial Italic",
    "Arial Bold",
    "Arial Bold Italic",
    "Arial Narrow",
    "Arial Narrow Italic",
    "Arial Narrow Bold",
    "Arial Narrow Bold Italic",
    "Arial Black",
    "Calibri",
    "Calibri Italic",
    "Calibri Bold",
    "Calibri Bold Italic",
    "Calibri Light",
    "Calibri Light Italic",
    "Cambria",
    "Cambria Italic",
    "Cambria Bold",
    "Cambria Bold Italic",
    "Cambria Math",
    "Courier New",
    "Courier New Italic",
    "Courier New Bold",
    "Courier New Bold Italic",
    "Consolas",
    "Consolas Italic",
    "Consolas Bold",
    "Consolas Bold Italic",
    "Century Schoolbook",
    "Century Schoolbook Italic",
    "Century Schoolbook Bold",
    "Century Schoolbook Bold Italic",
    "Segoe UI",
    "Segoe UI Italic",
    "Segoe UI Bold",
    "Segoe UI Bold Italic",
    "Segoe UI Black",
    "Segoe UI Black Italic",
    "Segoe UI Light",
    "Segoe UI Semilight",
    "Segoe UI Symbol",
    "Segoe UI Emoji",
    "STIX Two Math Regular",
    "STIX Two Text Regular",
    "STIX Two Text Italic",
    "STIX Two Text Bold",
    "STIX Two Text Bold Italic",
    "STIX Two Text Medium",
    "STIX Two Text Medium Italic",
    "STIX Two Text SemiBold",
    "STIX Two Text SemiBold Italic",
    "Noto Sans Math Regular",
    "Euclid",
    "Euclid Italic",
    "Euclid Bold",
    "Euclid Bold Italic",
    "Euclid Symbol",
    "Euclid Symbol Italic",
    "Euclid Symbol Bold",
    "Euclid Symbol Bold Italic",
    "Euclid Fraktur",
    "Euclid Fraktur Bold",
    "Euclid Math One",
    "Euclid Math One Bold",
    "Euclid Math Two",
    "Euclid Math Two Bold",
    "Mathematica1",
    "Mathematica1-Bold",
    "Mathematica2",
    "Mathematica2-Bold",
    "Mathematica3",
    "Mathematica3-Bold",
    "Mathematica4",
    "Mathematica4-Bold",
    "Mathematica5",
    "Mathematica5 Bold",
    "Mathematica6",
    "Mathematica7",
)

# The known font each 1.15 `uint8` number reads as in 1.16, indexed by that number, 255 for none. Read
# 2026-10-08 from the beta and 2026-10-16 from the released RadicalPie.exe 1.16.0, 51 bytes at file offset
# 0x2ebfd0; the 1.15.1 executable's own table of file stems (`cambria` at 16, `consola` at 24,
# `Mathematica6b` at 44) is what it translates. B1 measured 2, 6, 10, 16, 24, 29, 36, 37 and 46 against it.
LegacyFonts = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16, 17, 18, 19, 20, 25, 22, 23, 24, 26, 27, 28, 29, 30, 31,
    32, 33, 46, 47, 38, 39, 40, 41, 44, 45, 48, 49, 50, 51, 52, 80, 81, 82, 255, 83, 57, 53, 54, 55, 56,
)  # fmt: skip

NoFont = 255
TimesId = 2
EmptySlotId = -1

DatabaseName = "fonts.pie"
SlugExtension = ".slug"

# The font files whose stem Radical Pie 1.16 resolves: it appends each of these to the name and looks for the
# file. A collection, `.ttc`, is named by name ID 4 alone.
StemExtensions = (".ttf", ".otf")
FontFileExtensions = StemExtensions + (".ttc",)

# What a slot's report says about it. A slot that RESOLVES or IMPORTS draws in its own font; the rest do not.
Resolves = "resolves"
Imports = "imports"
Empty = "empty"
Emptied = "emptied"
Unresolved = "unresolved"
DamagedSlug = "damaged slug"

DrawnStates = (Resolves, Imports, Empty)

SuggestionCount = 3

# The words a font name carries for its style, weight, width or vendor edition, which say nothing about which
# family it is. Suggestions are scored on the other words, so "Minion Pro Italic" is not matched to "Inter
# Italic" or "Source Sans Pro Italic" by its last two words.
StyleWords = frozenset(
    {
        "regular",
        "italic",
        "oblique",
        "bold",
        "semibold",
        "demibold",
        "extrabold",
        "ultrabold",
        "black",
        "heavy",
        "light",
        "semilight",
        "extralight",
        "ultralight",
        "thin",
        "medium",
        "book",
        "normal",
        "condensed",
        "pro",
        "std",
        "lt",
        "mt",
        "ps",
    }
)

# How alike two names' family words must be, as `difflib.SequenceMatcher.ratio`, to be offered: difflib's own default.
FamilyCutoff = 0.6

# The exit code of a pipeline's command line that wrote its output with a slot drawn in Times. The pipelines
# exit 1 on every failure and the usage, and `scripts/Fonts.py` and `scripts/WrapSvg.py` exit 2 on the usage.
FallbackExitCode = 3

FindHint = "`python scripts/Fonts.py find <words>` lists the installed fonts"

# The line for a Font Import report whose slots neither the write-back nor this machine's font check names.
ReportedWithoutSlot = "Radical Pie reported a font of the design it could not import and drew it in Times"


class FontDatabaseUnreadable(Exception):
    """There is no `fonts.pie` where Radical Pie keeps it, or it cannot be read, so no name can be checked."""


@dataclass(frozen=True)
class FontRecord:
    """One installed font file as `fonts.pie` lists it: the file name and the name ID 4 of each font in it."""

    file: str
    names: tuple
    collection: bool


@dataclass(frozen=True)
class SlotReport:
    """What one `F` slot resolves to. `written` is the slot's data list as the design writes it."""

    slot: int
    written: str
    state: str
    detail: str
    knownId: Optional[int] = None
    suggestions: tuple = ()

    @property
    def drawn(self) -> bool:
        return self.state in DrawnStates


def UserDirectory() -> Path:
    """`%LOCALAPPDATA%\\RadicalPie`, where the font database and the imported slugs live."""

    return Path(os.environ.get("LOCALAPPDATA", "")) / "RadicalPie"


def DatabasePath() -> Path:
    return UserDirectory() / DatabaseName


def ReadDatabase(path: Optional[Path] = None) -> list:
    """Every record of the font database, in file order. Raises FontDatabaseUnreadable when there is none.

    A file that cannot be read, cannot be decoded or does not parse raises the same, naming the reason: a
    `fonts.pie` truncated or locked while Radical Pie rewrites it is no database for the check. A value that is
    not a string is no name and is passed over.
    """

    path = DatabasePath() if path is None else Path(path)

    try:
        nodes = OpenDdl.Parse(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FontDatabaseUnreadable(
            f"there is no font database at {path}; open Radical Pie once and it builds one"
        ) from None
    except (OSError, UnicodeDecodeError, OpenDdl.PieSyntaxError) as error:
        raise FontDatabaseUnreadable(f"the font database at {path} cannot be read: {error}") from None

    records = []

    for node in nodes:
        if not isinstance(node, OpenDdl.Structure) or node.identifier != "R":
            continue

        names = tuple(
            value
            for child in node.children
            if isinstance(child, OpenDdl.DataList)
            for value in child.values
            if isinstance(value, str)
        )
        records.append(FontRecord(str(node.properties.get("n", "")), names, bool(node.properties.get("c"))))

    return records


def ResolvableStem(record: FontRecord) -> Optional[str]:
    """The file stem a design may name the record's font by: a `.ttf` or `.otf` file's, None for a collection."""

    path = Path(record.file)

    if record.collection or path.suffix.lower() not in StemExtensions:
        return None

    return path.stem


class Database:
    """The font database with its lookups: a record by name ID 4 or by file stem, and the slugs on disk."""

    def __init__(self, records: list, userDirectory: Path, shippedDirectory: Path):
        self.records = records
        self.userDirectory = Path(userDirectory)
        self.shippedDirectory = Path(shippedDirectory)
        self.byName = {}
        self.byStem = {}

        for record in records:
            for name in record.names:
                self.byName.setdefault(name.lower(), record)

            stem = ResolvableStem(record)

            if stem is not None:
                self.byStem.setdefault(stem.lower(), record)

        self.knownIds = {name.lower(): index for index, name in enumerate(KnownFonts)}

    def Record(self, name: str) -> Optional[FontRecord]:
        """The record a name resolves to: by name ID 4 first, then by the stem of a `.ttf` or `.otf` file."""

        return self.byName.get(name.lower()) or self.byStem.get(name.lower())

    def ByStem(self, name: str) -> bool:
        """Whether the name resolves through a file stem rather than through a name ID 4."""

        return name.lower() not in self.byName and name.lower() in self.byStem

    def KnownId(self, name: str) -> Optional[int]:
        """The known font a name ends at: its own entry, or the entry of the font a file stem names."""

        if name.lower() in self.knownIds:
            return self.knownIds[name.lower()]

        if self.ByStem(name) and self.byStem[name.lower()].names:
            return self.knownIds.get(self.byStem[name.lower()].names[0].lower())

        return None

    def ShippedSlug(self, knownId: int) -> Optional[Path]:
        path = self.shippedDirectory / f"{knownId}{SlugExtension}"

        return path if path.is_file() else None

    def RecordSlug(self, record: FontRecord, name: str) -> Optional[Path]:
        """The slug one font of a record draws from: an imported one by the file's stem, or one Radical Pie ships.

        The font at index n of a collection of separate fonts draws from `<stem><n>.slug`, and a collection
        whose fonts share glyphs from the one `<stem>.slug`, which is also the slug of a single font file.
        """

        stem = Path(record.file).stem
        lowered = [candidate.lower() for candidate in record.names]
        index = lowered.index(name.lower()) if name.lower() in lowered else 0
        candidates = [f"{stem}{index}{SlugExtension}"] if record.collection and index else []
        candidates.append(stem + SlugExtension)

        for candidate in candidates:
            if (self.userDirectory / candidate).is_file():
                return self.userDirectory / candidate

        for candidate in record.names:
            knownId = self.knownIds.get(candidate.lower())

            if knownId is not None and self.ShippedSlug(knownId):
                return self.ShippedSlug(knownId)

        return None

    def Suggestions(self, name: str) -> list:
        """The names closest to one that does not resolve: by file name, else by family, else by spelling.

        A file name with its extension, `"NewCM10-Book.ttf"`, and the stem of a collection, `"msgothic"`, point
        at the fonts of that file by name ID 4; the family is how a writer names a font, `"Lato"`, and points at its
        members. The spelling is compared on the family words alone (`FamilyWords`), and the nearest font of each
        family that matches comes first, by its whole name. A misspelled style word counts as a family word, so a
        name none of whose families is close enough is then offered the fonts of each installed family whose
        words lead its own, nearest whole name first: `"Lato Regulr"` is offered `"Lato Regular"`. A name whose
        family words are all style words, or neither match nor begin with an installed family, gets no
        suggestion.
        """

        lowered = name.lower()
        fileStem = Path(lowered).stem if Path(lowered).suffix in FontFileExtensions else lowered
        named = [
            candidate
            for record in self.records
            if Path(record.file).stem.lower() == fileStem
            for candidate in record.names
        ]

        if named:
            return named[:SuggestionCount]

        family = sorted(
            {candidate for candidate in self.Names() if candidate.lower().startswith(lowered + " ")},
            key=lambda candidate: (not candidate.endswith((" Regular", " Book")), len(candidate), candidate),
        )

        if family:
            return family[:SuggestionCount]

        familyWords = FamilyWords(lowered)

        if not familyWords:
            return []

        families = {}

        for candidate in self.Names():
            families.setdefault(FamilyWords(candidate.lower()), set()).add(candidate)

        families.pop("", None)
        matches = difflib.get_close_matches(familyWords, list(families), SuggestionCount, FamilyCutoff)

        if not matches:
            words = familyWords.split()
            matches = sorted(
                (family for family in families if words[: len(family.split())] == family.split()),
                key=lambda family: (-len(family.split()), family),
            )

        ranked = [
            sorted(families[match], key=lambda candidate: (-Likeness(lowered, candidate), candidate))
            for match in matches
        ]

        # The nearest font of each matching family first, then the rest of each family in the same order.
        suggestions = [members[0] for members in ranked] + [member for members in ranked for member in members[1:]]

        return suggestions[:SuggestionCount]

    def Names(self) -> list:
        """Every name a design can write: each installed font's name ID 4 and each shipped known font's."""

        names = [name for record in self.records for name in record.names]
        names.extend(name for index, name in enumerate(KnownFonts) if index and self.ShippedSlug(index))

        return names


def Likeness(lowered: str, candidate: str) -> float:
    """How alike a lowered name and a candidate's whole name are, as `difflib.SequenceMatcher.ratio`."""

    return difflib.SequenceMatcher(None, lowered, candidate.lower()).ratio()


def FamilyWords(name: str) -> str:
    """The words of a font name that name its family, `StyleWords` left out: `"minion"` for `"Minion Pro Italic"`."""

    return " ".join(word for word in re.split(r"[\s_-]+", name.lower()) if word and word not in StyleWords)


def OpenDatabase(path: Optional[Path] = None) -> Database:
    """The database of this machine: `fonts.pie` beside the user's slugs, and the shipped slugs."""

    path = DatabasePath() if path is None else Path(path)

    return Database(ReadDatabase(path), path.parent, ShippedSlugDirectory)


def ReadableDatabase() -> Optional[Database]:
    """The database of this machine, or None when `fonts.pie` is missing or cannot be read.

    A pipeline asks for it after Radical Pie has written its output, and a database it cannot read leaves the
    warnings to the known names rather than discarding that output.
    """

    try:
        return OpenDatabase()
    except FontDatabaseUnreadable:
        return None


def InstalledFile(fileName: str) -> str:
    """Where Windows keeps an installed font file: the user's font folder or the system's. The name otherwise."""

    for directory in (
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Fonts",
        Path(os.environ.get("WINDIR", "")) / "Fonts",
    ):
        if (directory / fileName).is_file():
            return str(directory / fileName)

    return fileName


def DesignFonts(pieText: str) -> list:
    """The `F` structures of the equation's design, as (slot, data list), in the order the design writes them.

    A slot with no data list or a data list holding nothing is left out; the validator reports both.
    """

    fonts = []

    for node in OpenDdl.Parse(pieText):
        if not (isinstance(node, OpenDdl.Structure) and node.identifier == "D"):
            continue

        for child in node.children:
            if not (isinstance(child, OpenDdl.Structure) and child.identifier == "F"):
                continue

            lists = [item for item in child.children if isinstance(item, OpenDdl.DataList) and item.values]

            if lists:
                fonts.append((child.properties.get("i"), lists[0]))

    return fonts


def Written(dataList) -> str:
    """A data list as a design writes it: `s{"Cambria"}`, `i16{21}`, `u8{16}`."""

    value = dataList.values[0]

    if dataList.primitiveType == "string":
        return 's{"' + value + '"}'

    prefix = {"int16": "i16", "uint8": "u8"}.get(dataList.primitiveType, dataList.primitiveType)

    return f"{prefix}{{{value}}}"


def CheckDesign(pieText: str, database: Database) -> list:
    """One SlotReport per `F` slot of the equation."""

    return [CheckSlot(slot, dataList, database) for slot, dataList in DesignFonts(pieText)]


def CheckSlot(slot: int, dataList, database: Database) -> SlotReport:
    written = Written(dataList)
    value = dataList.values[0]

    if dataList.primitiveType == "string":
        return CheckName(slot, written, value, database)

    if dataList.primitiveType == "uint8":
        if not 0 <= value < len(LegacyFonts) or LegacyFonts[value] == NoFont:
            return SlotReport(slot, written, Emptied, "a 1.15 font number with no 1.16 font, so the slot is empty")

        return CheckKnownId(slot, written, LegacyFonts[value], database, "the 1.15 number for ")

    if dataList.primitiveType == "int16":
        if value == EmptySlotId:
            return SlotReport(slot, written, Empty, "an empty slot")

        if not 0 <= value < len(KnownFonts):
            return SlotReport(slot, written, Emptied, f"no known font has the id {value}, so the slot is empty")

        return CheckKnownId(slot, written, value, database, "")

    return SlotReport(slot, written, Unresolved, "a font is a string, an int16 or a uint8 data list")


def CheckKnownId(slot: int, written: str, knownId: int, database: Database, prefix: str) -> SlotReport:
    name = KnownFonts[knownId]
    shipped = database.ShippedSlug(knownId)

    if shipped is not None:
        return SlotReport(slot, written, Resolves, f'{prefix}"{name}", shipped with Radical Pie at {shipped}', knownId)

    report = CheckName(slot, written, name, database)

    return SlotReport(slot, written, report.state, f'{prefix}"{name}": {report.detail}', knownId, report.suggestions)


def CheckName(slot: int, written: str, name: str, database: Database) -> SlotReport:
    knownId = database.KnownId(name)
    record = database.Record(name)

    if record is None:
        if knownId is not None and database.ShippedSlug(knownId):
            return SlotReport(
                slot, written, Resolves, f"shipped with Radical Pie at {database.ShippedSlug(knownId)}", knownId
            )

        suggestions = tuple(database.Suggestions(name))

        return SlotReport(
            slot,
            written,
            Unresolved,
            "will not resolve, so Radical Pie draws it in Times" + Hint(suggestions, "; "),
            knownId,
            suggestions,
        )

    installed = InstalledFile(record.file)
    fontName = record.names[0] if database.ByStem(name) and record.names else name
    slug = database.RecordSlug(record, fontName)
    resolves = f"resolves to {installed}"

    if database.ByStem(name):
        writtenBack = f"i16{{{knownId}}}" if knownId is not None else f's{{"{fontName}"}}'
        resolves += f', "{fontName}" by its file stem, which Radical Pie writes back as {writtenBack}'

    # A `slugfont.exe` that fails deletes the empty slug it started, so the file can go between the two reads.
    try:
        empty = slug is not None and slug.stat().st_size == 0
    except OSError:
        slug, empty = None, False

    # The slug is empty while a `slugfont.exe` builds it, the whole file landing at the end (28 MB at once
    # for Malgun Gothic Bold, 2026-10-21), and stays empty for good when the build was stopped.
    if empty:
        return SlotReport(
            slot,
            written,
            DamagedSlug,
            f"{resolves}, but its slug {slug} is empty, which crashes Radical Pie; unless a slugfont.exe is still"
            " building it, delete that file",
            knownId,
        )

    if slug is not None:
        return SlotReport(slot, written, Resolves, resolves, knownId)

    return SlotReport(
        slot,
        written,
        Imports,
        f"{resolves}, with no slug yet; Radical Pie imports it on first use, and the render pipelines wait for"
        " the import",
        knownId,
    )


def FindFonts(words: list, database: Database) -> list:
    """Every font whose name ID 4 or file name holds all the words, as (name, stem or None, file, slug or None).

    The stem is the file stem a design may write in place of the name, given for a `.ttf` or `.otf` file whose
    stem is not the name already; a shipped known font that is not installed has neither stem nor file.
    """

    lowered = [word.lower() for word in words]
    found = []

    for record in database.records:
        stem = ResolvableStem(record)

        for name in record.names:
            text = f"{name} {record.file}".lower()

            if all(word in text for word in lowered):
                offered = stem if stem is not None and stem.lower() != name.lower() else None
                found.append((name, offered, record.file, database.RecordSlug(record, name)))

    for index, name in enumerate(KnownFonts):
        shipped = database.ShippedSlug(index) if index else None

        if shipped is None or database.Record(name) is not None:
            continue

        if all(word in name.lower() for word in lowered):
            found.append((name, None, None, shipped))

    return found


WrittenFontPattern = re.compile(r"F \(i=(\d+)\) \{(\w+)\{([^}]*)\}\}")


def WrittenSlots(text: str) -> dict:
    """The `F` slots of a design as Radical Pie writes it back, slot to (type spelling, value text)."""

    return {int(slot): (kind, value) for slot, kind, value in WrittenFontPattern.findall(text)}


def TimesFallbacks(pieText: str, writtenText: str, database: Optional[Database]) -> list:
    """The SlotReports of the slots the written-back design shows Radical Pie drew in Times.

    Radical Pie 1.16 writes a slot it could not resolve back as `i16{2}`, the Times id, in place of what the
    design named (measured 2026-10-08, Findings.md B1). A slot naming Times itself comes back the same way and
    is not one of them. Without a database only the known names can be told apart from a fallback.

    The report of each is the font check's, whose state can say the slot resolves when the import has not
    finished; without a database it is `Unresolved` with no suggestion.
    """

    written = WrittenSlots(writtenText)
    fallbacks = []

    for slot, dataList in DesignFonts(pieText):
        if written.get(slot) != ("i16", str(TimesId)):
            continue

        if ExpectedKnownId(dataList, database) == TimesId:
            continue

        if database is None:
            fallbacks.append(SlotReport(slot, Written(dataList), Unresolved, "came back as Times"))
        else:
            fallbacks.append(CheckSlot(slot, dataList, database))

    return fallbacks


def FontWarnings(pieText: str, writtenText: str, reported: bool, unimported: frozenset = frozenset()) -> tuple:
    """The warning lines for an output Radical Pie drew with a slot of the design in Times, one per slot.

    `writtenText` is the design as the output carries it, read for the `i16{2}` write-back against this
    machine's font database, or against the known names when there is none. `reported` says the pipeline saw
    the Font Import report; when the write-back names no slot, this machine's font check names the slots that
    will not draw, and failing that one line says only what Radical Pie reported.

    `unimported` holds the slots whose font the SVG, PDF and EMF pipelines found still without a slug after
    their last launch (`Tools.Render.FontImport.SlotsAwaitingImport`). Each gets a line of its own unless the
    write-back already names it, because Radical Pie can leave such a slot out of the design it writes back
    rather than write `i16{2}`, and the output still draws it in Times.
    """

    database = ReadableDatabase()
    fallbacks = TimesFallbacks(pieText, writtenText, database)

    if not fallbacks and reported and database is not None:
        fallbacks = [report for report in CheckDesign(pieText, database) if not report.drawn]

    named = {report.slot for report in fallbacks}
    pending = []

    if unimported and database is not None:
        pending = [
            report
            for report in CheckDesign(pieText, database)
            if report.slot in unimported and report.slot not in named
        ]

    if not fallbacks and not pending and reported:
        return (ReportedWithoutSlot,)

    return tuple(FallbackWarning(report) for report in fallbacks) + tuple(
        UnimportedWarning(report) for report in pending
    )


def UnimportedWarning(report: SlotReport) -> str:
    """One slot whose font was still not imported after the last launch, with the font check's line on it."""

    return (
        f"F {report.slot} {report.written}: Radical Pie had not imported this font when the last launch wrote the"
        f" output, which may draw it in Times; the font check says: {report.detail}"
    )


def FallbackWarning(report: SlotReport) -> str:
    """One slot drawn in Times: `F 8 s{"NewCM10-Book.ttf"}: Radical Pie drew it in Times; the closest ...`."""

    line = f"F {report.slot} {report.written}: Radical Pie drew it in Times"

    if report.state != Unresolved:
        return f"{line}; the font check says: {report.detail}"

    if not report.suggestions:
        return f"{line}; {FindHint}"

    return f"{line}; the closest installed names are " + ", ".join(f'"{name}"' for name in report.suggestions)


def ExpectedKnownId(dataList, database: Optional[Database]) -> Optional[int]:
    """The known id Radical Pie writes a slot back as when it resolves it, or None for a slot written by name."""

    value = dataList.values[0]

    if dataList.primitiveType == "int16":
        return value

    if dataList.primitiveType == "uint8":
        return LegacyFonts[value] if 0 <= value < len(LegacyFonts) else None

    if database is not None:
        return database.KnownId(value)

    return {name.lower(): index for index, name in enumerate(KnownFonts)}.get(value.lower())


def Hint(suggestions: tuple, separator: str) -> str:
    """`did you mean "A" or "B"` after the separator, or nothing when there is no suggestion."""

    if not suggestions:
        return ""

    return separator + "did you mean " + " or ".join(f'"{suggestion}"' for suggestion in suggestions)


def Describe(report: SlotReport) -> str:
    """One slot's report as the check prints it: `F 8 s{"NewCM10-Book.ttf"}: will not resolve ...`."""

    return f"F {report.slot} {report.written}: {report.detail}"


ModuleProgram = "python -m Tools.PieFormat.Fonts"


def Usage(program: str) -> str:
    return f"usage: {program} check <file.pie>... | {program} find <word>..."


def FoundLine(name: str, stem: Optional[str], fileName: Optional[str], slug: Optional[Path]) -> str:
    """One font `find` lists: the `F` data lists that name it, its font file, and whether its slug exists.

    `s{"New Computer Modern 10 Book"} or s{"NewCM10-Book"}  font file NewCM10-Book.ttf, slug ready`. The
    file name is where the font comes from and never a form to write, since a name with its extension draws
    Times.
    """

    forms = f's{{"{name}"}}' + (f' or s{{"{stem}"}}' if stem is not None else "")
    source = f"font file {fileName}" if fileName is not None else "shipped with Radical Pie"
    ready = "slug ready" if slug is not None else "no slug yet, imported on first use"

    return f"{forms}  {source}, {ready}"


def Main(arguments: list, program: str) -> int:
    """`check` prints one line per `F` slot and exits 1 when one will not draw in its font; `find` lists fonts."""

    if len(arguments) < 2 or arguments[0] not in ("check", "find"):
        print(Usage(program), file=sys.stderr)

        return 2

    try:
        database = OpenDatabase()
    except FontDatabaseUnreadable as error:
        print(error, file=sys.stderr)

        return 1

    if arguments[0] == "find":
        found = FindFonts(arguments[1:], database)

        for name, stem, fileName, slug in found:
            print(FoundLine(name, stem, fileName, slug))

        if not found:
            print("no installed font has a name or file name holding " + " and ".join(arguments[1:]))

        return 0 if found else 1

    failed = False

    for fileName in arguments[1:]:
        try:
            reports = CheckDesign(Path(fileName).read_text(encoding="utf-8"), database)
        except OSError as error:
            print(f"{fileName}: {error.strerror}", file=sys.stderr)
            failed = True
            continue
        except OpenDdl.PieSyntaxError as error:
            print(f"{fileName}:{error}", file=sys.stderr)
            failed = True
            continue

        if not reports:
            print(f"{fileName}: the design names no font")

        for report in reports:
            print(f"{fileName}: {Describe(report)}")
            failed = failed or not report.drawn

    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(Main(sys.argv[1:], ModuleProgram))

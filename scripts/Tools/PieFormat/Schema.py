"""The Radical Pie structure catalogue as data, taken from References/Docs/Text/FileFormat.md.

Every rule carries the section title of that document it comes from, so a validation error can name
the section its reader must open. Each rule that the specification does not state, and that a fixture
written by Radical Pie proves, carries a comment naming the fixture; the file wins over the document.
Those rules are Br's absent array, Mx's
subgroup minimum, the data lists inside F, P and V, Sb's 'ma' property, Ph's substructures and V's 'bond'
domain. Three more come from a render rather than a fixture, because no fixture in the corpus carries
them: the endpoint and offset properties of Cn, Zg and Qe, the 'line' anchor type on those same three
structures, and the 'pi' and 'co' properties on the four modifier structures, which the specification
offers to the equation category alone.

Where the specification enumerates nothing, this catalogue enumerates nothing: `Gr`'s `al` is
unconstrained here. Every data-list value is held to the range of its primitive type (`IntegerRanges`),
a Unicode character value to the last code point (`UnicodeValueStructures`), and the values the
specification does enumerate to its tables: `Ar`'s arrow and charm types and `Bd`'s bond types, bond
group types, angle group types and angle types. Three exceptions are measurements and
not readings. `V`'s `n` is DesignParameters.Domains, the 347 design parameter names the executable holds,
with the range each is given, because Radical Pie drops a name it does not know without a word (ADR-0008).
`Gr`'s `ba`: the Group menu offers three baseline alignments and the editor writes 'frst' and 'mddl' for
two of them, so those three are the allowed values; Radical Pie itself accepts any value there and renders
the default (ADR-0006). `Ar`'s two data-list enumerations, `ArrowTypes` and `CharmTypes`, are narrower for
the same reason: an arrow type outside the four draws a full-length arrow and a charm outside the forty is
dropped, both without a word (ADR-0007). Each of these rules is narrower than the executable rather than
wider.
`Al`'s `al`, `Ph`'s `t`, `Ng`'s `t`, `Sl`'s `t` and `Bd`'s bond types are narrower than the executable the
same way and needed no decision of their own, because the enumeration each keeps is the specification's;
`Sp`'s `s` carries no bound at all, because the limits the Spaces page states are the Insert Space dialog's.
The 't' of Bx, Kt and En is enumerated by the specification and is narrower than the
executable in the same way, a four-letter value outside the table drawing the default (rendered
2026-09-13), and so are Dv's subgroup types, En's one enclosure per symbol and En's place inside a
symbol, each of which the executable accepts past its own specification.

Four drawing rules come from the Drawing Tools and Editor Window pages and from a render, and not from
the specification, which offers all eight general drawing properties to all eight drawing structures:
`LineFillProperties`, the fill a line object drops; `JoistStrokeProperties`, the width and dashing a
bracket or brace drops; `ZigzagCrashingDash`, the one dash pattern that crashes a zigzag; and
`ShapeStructures`, whose two anchors are opposite corners and cannot be one point. The first two
describe a file Radical Pie renders and ignores part of, which is the class the division and strike
rules belong to: the validator is the only thing that tells the writer the property did nothing.

The anchor table is the one place where a measurement and not a fixture carries the rule.
`AnchorTypeOwners` is the specification's anchor-type table, which says of every type which structures
own it, with the seven bond types the specification omits; `AnchorCounts` and `MatrixAnchorCount` are
the anchor counts of `Skill/RadicalPie/references/AnchorAtlas.md`, measured one render per anchor,
because an index past the last anchor of a type crashes Radical Pie instead of being refused.

An em dash in a property table's Default column is read two ways. For `Mx.r`, `Mx.c`, `M.t` and `V.n`
it means the property is required, because those values are structural and no default would carry a
meaning. For the drawing flags `f` and `s` it means the flag is off, because a bool property written
without a value is true in OpenDDL 3.0, so "off" has no spelling other than leaving the flag out; the
`v` flag of `Cn`, `Qe` and `Zg` writes `false` in that column instead.
"""

from .DesignParameters import Domains as DesignParameters

FileSection = "File Format Specification"

# The one section that is not a heading of FileFormat.md. Radical Pie and InkRadix hand an equation to
# another program inside an XML comment in an SVG, which Docs/ARCHITECTURE.md records under format facts and
# no page of the captured documentation states; the rule it carries is Validator.CheckCarrierComment.
CarrierSection = "SVG comment carrier"

GeneralEquationSection = "General Equation Structure Properties"
GeneralDrawingSection = "General Drawing Structure Properties"

# The five file-level sections, in the order the specification requires.
SectionNames = (
    "design",
    "background drawing",
    "main equation group",
    "annotation",
    "foreground drawing",
)


class PropertyRule:
    """One row of a structure's property table."""

    def __init__(
        self,
        name,
        valueType,
        default,
        section,
        allowedValues=None,
        minimum=None,
        maximum=None,
        minimumExclusive=False,
        required=False,
        requires=None,
    ):
        self.name = name
        self.valueType = valueType
        self.default = default
        self.section = section
        self.allowedValues = allowedValues
        self.minimum = minimum
        self.maximum = maximum
        self.minimumExclusive = minimumExclusive
        self.required = required

        # (otherProperty, allowedValuesOfTheOther): this flag may be true only then. Used by Fr.
        self.requires = requires


class SubstructureRule:
    """One row of a structure's substructure table.

    The target is a structure identifier, the pseudo-identifier "Equation" standing for any structure
    in the equation category, a primitive type name, or "anyPrimitive" for a data list of any type.
    A maximum of None means the specification writes an em dash for it.
    """

    def __init__(
        self,
        target,
        minimum,
        maximum,
        section,
        valueMinimum=None,
        valueMaximum=None,
        subarraySize=None,
    ):
        self.target = target
        self.minimum = minimum
        self.maximum = maximum
        self.section = section
        self.valueMinimum = valueMinimum
        self.valueMaximum = valueMaximum
        self.subarraySize = subarraySize


class StructureRule:
    """Everything the catalogue knows about one structure identifier."""

    def __init__(self, identifier, category, section, properties, substructures, groupTypes, firstChild):
        self.identifier = identifier
        self.category = category
        self.section = section
        self.properties = properties
        self.substructures = substructures

        # (groupType, minimum, maximum) for each type of Gr the structure accepts, 0 being the default type.
        self.groupTypes = groupTypes

        self.firstChild = firstChild


GroupTypes = (
    0,
    "anno",
    "subs",
    "sups",
    "numr",
    "dnom",
    "degr",
    "quot",
    "mdfr",
    "lowr",
    "uppr",
    "labl",
    # The bond structure names four more group types that the group type table omits.
    "uplf",
    "uprt",
    "lwlf",
    "lwrt",
)

# The Group menu's three baseline commands, Align with First Baseline, Align with Last Baseline and Align
# with Middle, which is the matrix element alignment of release 1.14 as well. FileFormat.md names only the
# default 'last'; the other two were measured by driving the editor (Tools/Probe/MatrixAlignmentProbe.py,
# 2026-09-12). Radical Pie never writes 'last', and it drops an explicit one on the next save. It accepts
# any other value and renders the default, so this list is narrower than the executable (ADR-0006).
GroupBaselineAlignments = ("frst", "last", "mddl")

# The four values of an arrow's type array, top to bottom, from the "Ar — Arrow Structure" section.
# Radical Pie 1.15 draws a full-length arrow for any other value and reports nothing, so this list is
# narrower than the executable (ADR-0007, measured 2026-09-13).
ArrowTypes = ("long", "left", "rght", "cent")

# The three words that move the charm cursor inside a charm array. The cursor starts at the right.
CharmAlignments = ("left", "rght", "cent")

# The forty charm types of the charm table in the same section, in the order the table lists them.
# Radical Pie 1.15 drops a value that is not one of these and not an alignment, leaving the shaft bare,
# so this list too is narrower than the executable (ADR-0007). What the catalogue does not encode is the
# table's Left, Right and Interior columns: every one of the forty draws at every one of the three
# positions, so those columns describe the Insert Arrow dialog's palettes and not the format
# (Docs/ARCHITECTURE.md, format facts, measured 2026-09-13).
CharmTypes = (
    "larw",
    "rarw",
    "labr",
    "rabr",
    "luhp",
    "ruhp",
    "ldhp",
    "rdhp",
    "luhb",
    "ruhb",
    "ldhb",
    "rdhb",
    "barr",
    "line",
    "dbln",
    "slsh",
    "dbsl",
    "back",
    "dbbk",
    "exxx",
    "circ",
    "sdcr",
    "squa",
    "sdsq",
    "diam",
    "sddm",
    "ltri",
    "sdlt",
    "rtri",
    "sdrt",
    "luhk",
    "ldhk",
    "ruhk",
    "rdhk",
    "lfsh",
    "rfsh",
    "lulp",
    "ldlp",
    "rulp",
    "rdlp",
)

SymbolRoles = (
    "math",
    "chem",
    "text",
    "func",
    "unit",
    "nmbr",
    "oper",
    "rltn",
    "arrw",
    "bond",
    "unry",
    "pnct",
    "elps",
)

SymbolStyles = (
    "uprt",
    "ital",
    "bold",
    "bitl",
    "mono",
    "grek",
    "itgk",
    "bdgk",
    "bigk",
    "sym1",
    "sym2",
    "nary",
    "gral",
    "scpt",
    "bdsc",
    "frkt",
    "bdfk",
    "doub",
    "sans",
    "itsn",
    "dbsn",
    "bisn",
)

# The specification's domain list holds the first twenty-one of these and omits 'bond'.
# Corpus/Site/Chemistry/FDG.pie lines 5 to 7 write three bond parameters, 'wgap', 'hlln' and 'dlln', in
# that domain (Docs/ARCHITECTURE.md, format facts the specification does not state). The names inside
# each domain are DesignParameters, measured against the executable on 2026-09-13.
ValueDomains = tuple(DesignParameters)

# The index a style map puts in a font slot it does not use (Corpus/Pie/aaa.pie, and every style the
# operator's design fixture maps to fewer than four fonts).
NoFontIndex = 255

# The highest font slot that resolves to a font with no F in the design, measured 2026-09-14 through the
# render pipeline: `M (t='uprt') {u8{n}}` in a design holding nothing else renders for n of 1, 7 and 8,
# each in a different face, and crashes Radical Pie with the access violation 3221225477 for n of 9 and
# 20. Validator.CheckDesignFonts holds a style map's first index to these slots and the ones the design's
# own F structures fill.
HighestFactoryFontSlot = 8

# The range of every integer primitive OpenDDL spells, which Radical Pie reads with the width the type
# names: a value outside it wraps. `M (t='uprt') {u8{-1}}` is the refused `u8{255}` after the wrap and
# crashes, `Sb (co=-1)` is 0xFFFFFFFF and draws white ink on white paper, and `M (t='uprt') {u8{300}}` is
# slot 44 (measured 2026-09-13 and 2026-09-14). The wrap is silent, so the validator is the only reader
# that sees the value the writer meant.
IntegerRanges = {
    "int8": (-128, 127),
    "int16": (-32768, 32767),
    "int32": (-2147483648, 2147483647),
    "int64": (-(2**63), 2**63 - 1),
    "uint8": (0, 255),
    "uint16": (0, 65535),
    "uint32": (0, 4294967295),
    "uint64": (0, 2**64 - 1),
}

# The five structures whose uint32 data list holds Unicode character values, which the specification says
# of each of them. A value above the last code point crashes Radical Pie with the access violation
# 3221225477 before it renders: measured 2026-09-14 on Mk, Br and Pr with 0x110000 and on In with -1,
# which is 0xFFFFFFFF after the wrap. It was not rendered on It, which is here because its uint32 list is
# the same "Unicode value of the character" row of the specification.
UnicodeValueStructures = ("Mk", "Br", "Pr", "In", "It")

MaximumCodePoint = 0x10FFFF

# The fifteen bond types of the "Bd — Bond Structure" section, each of which can be written with its
# first letter capitalised for a long bond. Radical Pie 1.15 draws a value outside the table as a single
# bond and writes it back unchanged, so this enumeration is narrower than the executable the way Ar's two
# are: `u32[2]{{0,'zzzz'}}` and `u32[2]{{0,'sing'}}` both rendered 15.6075 by 9 pt (measured 2026-09-14).
BondTypes = (
    "sing",
    "doub",
    "trip",
    "hevy",
    "wavy",
    "part",
    "prd1",
    "prd2",
    "prt1",
    "prt2",
    "prt3",
    "swgo",
    "swgi",
    "dwgo",
    "dwgi",
)

BondTypeValues = BondTypes + tuple(bondType.capitalize() for bondType in BondTypes)

# The group type in a bond pair names the direction the bond points. 0 is the rightward bond, which has
# no group of its own (Corpus/Site/Chemistry/FDG.pie line 30 writes `{0,'Sing'}`); each of the six others
# names the neighbour group the bond ends at, and a pair whose group the site does not hold draws neither
# the bond nor the atom and reports nothing (measured 2026-09-14, 7.33691 by 9 pt against the control's
# 7.94385 by 28 pt).
BondGroupTypes = (0, "uppr", "uplf", "uprt", "lowr", "lwlf", "lwrt")

# "Angles can be specified only for the upper-left, upper-right, lower-left, and lower-right bonds."
BondAngleGroupTypes = ("uplf", "uprt", "lwlf", "lwrt")

BondAngleTypes = (0, "step", "shal")

LineOffsetTypes = (0, "long", "shrt")

LineEndpointTypes = (0, "sdcr", "sdsq", "wedg", "arr1", "arr2")


def RoutedLineProperties(section):
    """The four endpoint and offset properties of a line, which the specification gives to `Ln` alone.

    Measured 2026-09-12 through the render pipeline: `Cn`, `Zg` and `Qe` each draw the endpoint symbol at
    the end `es` or `ef` names and each shifts its end by `os` or `of`, and Radical Pie writes all four
    back into the comment of the SVG it saves, which is what proves they are properties of those
    structures and not values the reader ignores. A `Jo` keeps `os` and `of` and drops `es` and `ef`, as
    the Drawing Tools page says: a stretched brace takes no endpoint symbol.
    """

    return [
        PropertyRule("es", "uint32", 0, section, allowedValues=LineEndpointTypes),
        PropertyRule("ef", "uint32", 0, section, allowedValues=LineEndpointTypes),
        PropertyRule("os", "uint32", 0, section, allowedValues=LineOffsetTypes),
        PropertyRule("of", "uint32", 0, section, allowedValues=LineOffsetTypes),
    ]


class AnchorTypeRule:
    """One row of the anchor-type table of the "X — Connector Structure" section.

    The row says which structures own the type: every structure of a category apart from the ones
    `excluding` names, the structures `identifiers` names, a group at the file level, or an annotation
    group. `owners` is the phrase an error message prints after the type.
    """

    def __init__(self, owners, category=None, excluding=(), identifiers=(), topLevelGroup=False, annotationGroup=False):
        self.owners = owners
        self.category = category
        self.excluding = excluding
        self.identifiers = identifiers
        self.topLevelGroup = topLevelGroup
        self.annotationGroup = annotationGroup


def MatrixAnchorTypeRule(owners):
    return AnchorTypeRule(owners, identifiers=("Mx",))


def BondAnchorTypeRule(owners):
    return AnchorTypeRule(owners, identifiers=("Bd",))


# The anchor-type table of the "X — Connector Structure" section, which says of every type which
# structures it applies to. An anchor type a structure does not own crashes Radical Pie with an access
# violation rather than raising the invalid-data dialog (Docs/ARCHITECTURE.md, format facts).
#
# The seven bond types are measured rather than specified: the specification's table omits them and
# Skill/RadicalPie/references/AnchorAtlas.md measured all seven on a bond site, four anchors each,
# 2026-09-12.
AnchorTypeOwners = {
    0: AnchorTypeRule(
        "every structure in the equation category except a group, an aligner and a phantom",
        category="equation",
        excluding=("Gr", "Al", "Ph"),
    ),
    "cent": AnchorTypeRule(
        "every structure in the equation category except a group, a begin, an aligner and a phantom",
        category="equation",
        excluding=("Gr", "Bg", "Al", "Ph"),
    ),
    "axis": AnchorTypeRule("a group at the file level", topLevelGroup=True),
    "lmnl": AnchorTypeRule("a group at the file level", topLevelGroup=True),
    "bord": AnchorTypeRule("a group at the file level", topLevelGroup=True),
    "xxx!": AnchorTypeRule("a group at the file level", topLevelGroup=True),
    "yyy!": AnchorTypeRule("a group at the file level", topLevelGroup=True),
    "mtrx": MatrixAnchorTypeRule("a matrix"),
    "cell": MatrixAnchorTypeRule("a matrix"),
    "mrow": MatrixAnchorTypeRule("a matrix"),
    "mcol": MatrixAnchorTypeRule("a matrix"),
    "orow": MatrixAnchorTypeRule("a matrix"),
    "ocol": MatrixAnchorTypeRule("a matrix"),
    "lrow": MatrixAnchorTypeRule("a matrix"),
    "lcol": MatrixAnchorTypeRule("a matrix"),
    "line": AnchorTypeRule(
        "a line, a corner, a zigzag or a quarter ellipse",
        identifiers=("Ln", "Cn", "Zg", "Qe"),
    ),
    "edge": AnchorTypeRule("a rectangle, a rounded rectangle or an ellipse", identifiers=("Rt", "Rr", "El")),
    "jost": AnchorTypeRule("a joist", identifiers=("Jo",)),
    "anno": AnchorTypeRule(
        "a structure in the drawing category or a group of type 'anno'",
        category="drawing",
        annotationGroup=True,
    ),
    "bond": BondAnchorTypeRule("a bond site"),
    "bdup": BondAnchorTypeRule("a bond site"),
    "bdur": BondAnchorTypeRule("a bond site"),
    "bdul": BondAnchorTypeRule("a bond site"),
    "bdlw": BondAnchorTypeRule("a bond site"),
    "bdll": BondAnchorTypeRule("a bond site"),
    "bdlr": BondAnchorTypeRule("a bond site"),
}

# The rails belong to a group at the file level; a connector whose far end names a matrix with a rail
# type crashes Radical Pie (Docs/ARCHITECTURE.md, measured 2026-09-12).
RailAnchorTypes = ("xxx!", "yyy!")

BondAnchorTypes = ("bond", "bdup", "bdur", "bdul", "bdlw", "bdll", "bdlr")

MatrixAnchorTypes = ("mtrx", "cell", "mrow", "mcol", "orow", "ocol", "lrow", "lcol")

# Six of the seven bond types box one neighbour group each, and a direction whose group the bond site
# does not hold crashes Radical Pie (Docs/ARCHITECTURE.md, format facts, measured 2026-09-12). 'bond'
# boxes the whole site and needs no group.
BondAnchorGroupTypes = {
    "bdup": "uppr",
    "bdur": "uprt",
    "bdul": "uplf",
    "bdlw": "lowr",
    "bdll": "lwlf",
    "bdlr": "lwrt",
}

# How many anchors of a type Skill/RadicalPie/references/AnchorAtlas.md measured on each kind of
# structure it probed, 2026-09-12. An index past the last one crashes Radical Pie with an access
# violation, so the count is the range a writer may use. Every drawing structure is here: the atlas
# probed all eight of them, and the 'anno' count is the shape's own, four on a straight line, eight on a
# corner or a zigzag whose legs each carry a pair, four on a quarter ellipse, five on a closed shape and
# one on a joist.
AnchorCounts = {
    "topLevelGroup": {"bord": 4, "lmnl": 4, "xxx!": 10, "yyy!": 10},
    "annotationGroup": {"anno": 2},
    "equationStructure": {0: 4, "cent": 4},
    "Bd": {anchorType: 4 for anchorType in BondAnchorTypes},
    "Ln": {"line": 3, "anno": 4},
    "Cn": {"line": 3, "anno": 8},
    "Zg": {"line": 3, "anno": 8},
    "Qe": {"line": 3, "anno": 4},
    "Jo": {"jost": 1, "anno": 1},
    "Rt": {"edge": 4, "anno": 5},
    "Rr": {"edge": 4, "anno": 5},
    "El": {"edge": 4, "anno": 5},
}

# A structure inside a subgroup keeps indexes 0 and 1 of its own two types; index 2 or 3 there crashes
# (Docs/ARCHITECTURE.md, format facts, and the AnchorAtlas.md correction of 2026-09-12, which puts the
# far row of the type 0 and 'cent' anchors in a top-level group only). A bond site is the exception:
# nested or not, every one of its seven types keeps all four indexes.
NestedEquationAnchorCount = 2


def MatrixAnchorCount(anchorType, rows, columns):
    """How many anchors of a matrix anchor type a matrix of this shape carries.

    Measured on the 3 by 3 matrix of AnchorAtlas.md, where 'cell' numbers the corners of the (r+1) by
    (c+1) grid row-major, 'mrow' puts a point on every vertical grid line of every row and 'mcol' the
    other way round, 'orow' and 'ocol' flank every row and every column, 'lrow' and 'lcol' flank the
    interior grid lines, and 'mtrx' takes the four corners of the whole matrix. The site's larger grids
    reach exactly the last 'cell' this gives: index 80 of an 8 by 8 in Corpus/Site/Exomorphism.pie and
    index 99 of a 9 by 9 in Corpus/Site/OR.pie.
    """

    if anchorType == "cell":
        return (rows + 1) * (columns + 1)

    if anchorType == "mrow":
        return rows * (columns + 1)

    if anchorType == "mcol":
        return columns * (rows + 1)

    if anchorType == "orow":
        return 2 * rows

    if anchorType == "ocol":
        return 2 * columns

    if anchorType == "lrow":
        return 2 * (rows - 1)

    if anchorType == "lcol":
        return 2 * (columns - 1)

    return 4


def EquationProperties():
    return [
        PropertyRule("pi", "int32", 0, GeneralEquationSection, minimum=0, maximum=15),
        PropertyRule("co", "uint32", 0xFF000000, GeneralEquationSection),
    ]


def DrawingProperties():
    return [
        PropertyRule("f", "bool", False, GeneralDrawingSection),
        PropertyRule("s", "bool", False, GeneralDrawingSection),
        PropertyRule("w", "uint8", 0, GeneralDrawingSection, minimum=0, maximum=4),
        PropertyRule("d", "uint8", 0, GeneralDrawingSection, minimum=0, maximum=3),
        PropertyRule("fpi", "int32", 0, GeneralDrawingSection, minimum=0, maximum=15),
        PropertyRule("fco", "uint32", 0xFF000000, GeneralDrawingSection),
        PropertyRule("spi", "int32", 0, GeneralDrawingSection, minimum=0, maximum=15),
        PropertyRule("sco", "uint32", 0xFF000000, GeneralDrawingSection),
    ]


# The line tools: the structures the Drawing Tools page calls line objects, the three joists included.
LineStructures = ("Ln", "Cn", "Zg", "Qe", "Jo")

# "Line objects have a stroke color only and do not use the fill color" (Drawing Tools). Measured
# 2026-09-13 through the render pipeline: `f`, `fpi` and `fco` on an Ln, a Cn, a Zg, a Qe and a Jo each
# rendered the same paths as the plain structure, `fco=0xFFFF0000` leaving the path black, while `sco`
# coloured it. The specification gives all eight general drawing properties to every drawing structure,
# so the file is legal and its fill is silently dropped, which is what the validator reports.
LineFillProperties = ("f", "fpi", "fco")

# "Stroke thickness and dashing ... do not apply to brackets and braces" (Radical Pie Editor Window).
# Measured the same day: `w=4` and `d=3` on a Jo rendered the plain joist, while both moved an Ln, a Cn
# and a Qe.
JoistStrokeProperties = ("w", "d")

# A zigzag with the third dash pattern crashes Radical Pie 1.15 with the access violation 3221225477
# before it saves anything, with or without `s` and with or without `v`, six launches in a row on
# 2026-09-13; `d=1` and `d=2` render, and `d=3` renders on an Ln, a Cn and a Qe.
ZigzagCrashingDash = 3

# The shapes, which the Drawing Tools page draws between two anchors that are opposite corners.
ShapeStructures = ("Rt", "Rr", "El")


def Rule(identifier, category, title, properties=(), substructures=(), groupTypes=None, firstChild=None):
    """Assemble one catalogue entry, adding the general properties that the category brings with it."""

    allProperties = list(properties)

    # The specification offers 'pi' and 'co' to the equation category alone. The four modifiers take
    # them too and colour their own ink and not the symbol's: 'co' on an En, a Ng, a Sl and a Mk each
    # coloured the enclosure, the negation stroke, the slash and the accent red while the symbol stayed
    # black, and pi=5 on an En drew the enclosure in palette colour 5 (rendered 2026-09-13).
    if category in ("equation", "modifier"):
        allProperties += EquationProperties()
    elif category == "drawing":
        allProperties += DrawingProperties()

    return StructureRule(
        identifier,
        category,
        title,
        {rule.name: rule for rule in allProperties},
        tuple(substructures),
        groupTypes,
        firstChild,
    )


def ConnectorSubstructures(title):
    """The connector substructure that the specification gives to every drawing structure."""

    return [SubstructureRule("X", 1, 1, title)]


AlSection = "Al — Aligner Structure"
ArSection = "Ar — Arrow Structure"
BdSection = "Bd — Bond Structure"
BgSection = "Bg — Begin Structure"
BrSection = "Br — Bracket Structure"
BxSection = "Bx — Box Structure"
CnSection = "Cn — Corner Structure"
DSection = "D — Design Structure"
DvSection = "Dv — Division Structure"
ElSection = "El — Ellipse Structure"
EnSection = "En — Enclose Structure"
FSection = "F — Font Structure"
FrSection = "Fr — Fraction Structure"
GrSection = "Gr — Group Structure"
InSection = "In — Integral Structure"
ItSection = "It — Iteration Structure"
JoSection = "Jo — Joist Structure"
KtSection = "Kt — Strike Structure"
LnSection = "Ln — Line Structure"
MSection = "M — Map Structure"
MkSection = "Mk — Mark Structure"
MxSection = "Mx — Matrix Structure"
NgSection = "Ng — Negate Structure"
PSection = "P — Palette Structure"
PhSection = "Ph — Phantom Structure"
PrSection = "Pr — Prime Structure"
QeSection = "Qe — Quarter Ellipse Structure"
RdSection = "Rd — Radical Structure"
RrSection = "Rr — Rounded Rectangle Structure"
RtSection = "Rt — Rectangle Structure"
SbSection = "Sb — Symbol Structure"
ScSection = "Sc — Script Structure"
SlSection = "Sl — Slash Structure"
SpSection = "Sp — Space Structure"
StSection = "St — Stack Structure"
VSection = "V — Value Structure"
WmSection = "Wm — Widemark Structure"
XSection = "X — Connector Structure"
ZgSection = "Zg — Zigzag Structure"


Structures = {
    rule.identifier: rule
    for rule in [
        Rule(
            "Al",
            "equation",
            AlSection,
            # Radical Pie renders an alignment outside the three as 'left' and says nothing, so this
            # enumeration is narrower than the executable, the way Gr's 'ba' is (measured 2026-09-13).
            properties=[PropertyRule("al", "uint32", "left", AlSection, allowedValues=("left", "rght", "cent"))],
        ),
        Rule(
            "Ar",
            "equation",
            ArSection,
            substructures=[
                SubstructureRule("Gr", 0, 2, ArSection),
                # The specification's minimum of two data lists, the arrow types and one charm array.
                # Radical Pie renders an Ar with the type array alone, and with no array at all, drawing
                # a bare shaft; the minimum stays because an arrow with no charm on it is a writer's
                # slip and nothing else reports it (measured 2026-09-13).
                SubstructureRule("uint32", 2, 4, ArSection),
            ],
            # One label of each kind. This is the one rule of the arrow the executable enforces itself:
            # a second Gr (t='uppr') raises the invalid-data dialog (measured 2026-09-13). A group of
            # any other type is accepted there and drawn over the arrow, and is refused here.
            groupTypes=(("uppr", 0, 1), ("lowr", 0, 1)),
        ),
        Rule(
            "Bd",
            "equation",
            BdSection,
            substructures=[
                SubstructureRule("Gr", 1, 7, BdSection),
                SubstructureRule("uint32", 1, 2, BdSection, subarraySize=2),
            ],
            groupTypes=(
                (0, 1, 1),
                ("uppr", 0, 1),
                ("uplf", 0, 1),
                ("uprt", 0, 1),
                ("lowr", 0, 1),
                ("lwlf", 0, 1),
                ("lwrt", 0, 1),
            ),
        ),
        Rule(
            "Bg",
            "equation",
            BgSection,
            properties=[PropertyRule("lg", "float", -1.0, BgSection)],
        ),
        Rule(
            "Br",
            "equation",
            BrSection,
            properties=[
                PropertyRule("as", "bool", False, BrSection),
                PropertyRule("ca", "bool", False, BrSection),
            ],
            substructures=[
                SubstructureRule("Gr", 1, 9, BrSection),
                # The specification gives this array a minimum of 1. Corpus/Pie/eq.pie line 21 writes
                # a Br with no array at all, so the minimum here is 0.
                SubstructureRule("uint32", 0, 1, BrSection, valueMinimum=2, valueMaximum=3),
            ],
            groupTypes=((0, 1, 9),),
        ),
        Rule(
            "Bx",
            "equation",
            BxSection,
            properties=[
                PropertyRule("t", "uint32", "full", BxSection, allowedValues=("full", "lwlf", "lwrt", "uplf", "uprt"))
            ],
            substructures=[SubstructureRule("Gr", 1, 1, BxSection)],
            groupTypes=((0, 1, 1),),
        ),
        Rule(
            "Cn",
            "drawing",
            CnSection,
            properties=[PropertyRule("v", "bool", False, CnSection), *RoutedLineProperties(CnSection)],
            substructures=ConnectorSubstructures(CnSection),
        ),
        Rule(
            "D",
            "design",
            DSection,
            substructures=[
                SubstructureRule("V", 0, None, DSection),
                SubstructureRule("F", 0, 15, DSection),
                # A design holds up to 22 M structures, one per style; the specification's maximum of
                # 21 is one short (probed 2026-09-10, Docs/ARCHITECTURE.md).
                SubstructureRule("M", 0, 22, DSection),
                SubstructureRule("P", 0, 1, DSection),
            ],
        ),
        Rule(
            "Dv",
            "equation",
            DvSection,
            substructures=[SubstructureRule("Gr", 1, 2, DvSection)],
            groupTypes=((0, 1, 1), ("quot", 0, 1)),
        ),
        Rule("El", "drawing", ElSection, substructures=ConnectorSubstructures(ElSection)),
        Rule(
            "En",
            "modifier",
            EnSection,
            properties=[PropertyRule("t", "uint32", "circ", EnSection, allowedValues=("circ", "squa", "rdsq"))],
        ),
        Rule(
            "F",
            "design",
            FSection,
            # F — Font Structure gives the index the range 0 to 15. Slot 0 is the built-in Radical font
            # and no design replaces it: `F (i=0) {s{"Arial"}}` was dropped from the design Radical Pie
            # saved and the styles mapped to slot 0 drew from the Radical font as before (measured
            # 2026-09-13 through the render pipeline, ADR-0008), so the writer's font is lost in silence.
            properties=[PropertyRule("i", "int32", 0, FSection, minimum=1, maximum=15)],
            # F — Font Structure gives F no substructures. Corpus/Pie/rpie.pie writes the font name as
            # a string data list inside it, and each of the 202 font structures in the corpus holds
            # exactly one data list, a string or a uint8 index (corpus census 2026-09-10), holding one
            # value: `F (i=8) {s{}}` is dropped from the design Radical Pie saves without a word, so a
            # style mapped to slot 8 draws from whatever filled it before (measured 2026-09-14).
            substructures=[SubstructureRule("anyPrimitive", 1, 1, FSection, valueMinimum=1, valueMaximum=1)],
        ),
        Rule(
            "Fr",
            "equation",
            FrSection,
            properties=[
                PropertyRule("t", "uint32", "vert", FrSection, allowedValues=("vert", "horz", "diag")),
                PropertyRule("sm", "bool", False, FrSection, requires=("t", ("vert", "diag"))),
                PropertyRule("at", "bool", False, FrSection, requires=("t", ("vert",))),
                PropertyRule("ns", "bool", False, FrSection, requires=("t", ("horz",))),
            ],
            substructures=[SubstructureRule("Gr", 2, 2, FrSection)],
            groupTypes=(("numr", 1, 1), ("dnom", 1, 1)),
        ),
        Rule(
            "Gr",
            "equation",
            GrSection,
            properties=[
                PropertyRule("t", "uint32", 0, GrSection, allowedValues=GroupTypes),
                PropertyRule("al", "uint32", 0, GrSection),
                # A matrix entry's vertical alignment is this property and not one of Mx's own; the
                # editor's Insert Matrix writes 'mddl' into every entry it creates.
                PropertyRule("ba", "uint32", "last", GrSection, allowedValues=GroupBaselineAlignments),
                PropertyRule("as", "float", 1.0, GrSection, minimum=0.0, minimumExclusive=True),
                PropertyRule("ax", "float", 0.0, GrSection),
                PropertyRule("ay", "float", 0.0, GrSection),
            ],
            substructures=[
                SubstructureRule("Equation", 0, None, GrSection),
                SubstructureRule("Bg", 1, None, GrSection),
                SubstructureRule("X", 0, 1, GrSection),
            ],
            firstChild="Bg",
        ),
        Rule(
            "In",
            "equation",
            InSection,
            properties=[
                PropertyRule("sm", "bool", False, InSection),
                PropertyRule("il", "bool", False, InSection),
                PropertyRule("kg", "bool", False, InSection),
                PropertyRule("gr", "bool", False, InSection),
            ],
            substructures=[
                SubstructureRule("Gr", 1, 3, InSection),
                SubstructureRule("uint32", 0, 1, InSection, valueMinimum=1, valueMaximum=1),
            ],
            groupTypes=((0, 1, 1), ("lowr", 0, 1), ("uppr", 0, 1)),
        ),
        Rule(
            "It",
            "equation",
            ItSection,
            properties=[
                PropertyRule("sm", "bool", False, ItSection),
                PropertyRule("il", "bool", False, ItSection),
            ],
            substructures=[
                SubstructureRule("Gr", 1, 4, ItSection),
                SubstructureRule("uint32", 0, 1, ItSection, valueMinimum=1, valueMaximum=1),
            ],
            groupTypes=((0, 1, 1), ("lowr", 0, 1), ("uppr", 0, 1), ("mdfr", 0, 1)),
        ),
        Rule(
            "Jo",
            "drawing",
            JoSection,
            properties=[
                PropertyRule("t", "uint32", "brac", JoSection, allowedValues=("brac", "brck", "shel")),
                PropertyRule("os", "uint32", 0, JoSection, allowedValues=LineOffsetTypes),
                PropertyRule("of", "uint32", 0, JoSection, allowedValues=LineOffsetTypes),
            ],
            substructures=ConnectorSubstructures(JoSection),
        ),
        Rule(
            "Kt",
            "equation",
            KtSection,
            properties=[PropertyRule("t", "uint32", "horz", KtSection, allowedValues=("horz", "lwup", "uplw", "exxx"))],
            substructures=[SubstructureRule("Gr", 1, 1, KtSection)],
            groupTypes=((0, 1, 1),),
        ),
        Rule(
            "Ln",
            "drawing",
            LnSection,
            properties=RoutedLineProperties(LnSection),
            substructures=ConnectorSubstructures(LnSection),
        ),
        Rule(
            "M",
            "design",
            MSection,
            properties=[PropertyRule("t", "uint32", None, MSection, allowedValues=SymbolStyles, required=True)],
            # The first index is the primary font of the style and the rest are its fallbacks, which is why
            # 255, the "no font" index of Corpus/Pie/aaa.pie, belongs in a later slot and not the first:
            # `M (t='uprt') {u8{255}}` and `M (t='uprt') {u8{255,8,0,1}}` each crashed Radical Pie with the
            # access violation 3221225477 before it rendered anything, while `M (t='uprt') {u8{8,255,255,255}}`
            # rendered (measured 2026-09-13). Validator.CheckStyleMapFonts carries that rule.
            substructures=[SubstructureRule("uint8", 1, 1, MSection, valueMinimum=1, valueMaximum=4)],
        ),
        Rule(
            "Mk",
            "modifier",
            MkSection,
            properties=[PropertyRule("un", "bool", False, MkSection)],
            substructures=[SubstructureRule("uint32", 1, 1, MkSection, valueMinimum=1, valueMaximum=1)],
        ),
        Rule(
            "Mx",
            "equation",
            MxSection,
            properties=[
                PropertyRule("r", "int32", None, MxSection, minimum=1, maximum=32, required=True),
                PropertyRule("c", "int32", None, MxSection, minimum=1, maximum=32, required=True),
                # 'al' is the horizontal alignment of the entries. Their vertical alignment, which release
                # 1.14 added, is not here: it is the 'ba' property of each entry's own group.
                PropertyRule("al", "uint32", "cent", MxSection, allowedValues=("cent", "left", "rght")),
                PropertyRule("mb", "bool", False, MxSection),
                PropertyRule("eh", "bool", False, MxSection),
                PropertyRule("ew", "bool", False, MxSection),
                PropertyRule("rg", "bool", False, MxSection),
                PropertyRule("cg", "bool", False, MxSection),
            ],
            # The specification gives this a minimum of 2. Corpus/Pie/eq.pie line 404 writes a one by
            # one matrix with a single group, so the minimum here is 1 and r times c carries the rule.
            substructures=[SubstructureRule("Gr", 1, 1024, MxSection)],
            groupTypes=((0, 1, 1024),),
        ),
        Rule(
            "Ng",
            "modifier",
            NgSection,
            # A negation type outside the three renders as 'frwd' and is written back as a bare `Ng {}`
            # (measured 2026-09-13, Corpus/Pie/NegateTypes.pie), so this enumeration is narrower than
            # the executable, as Al's and Ph's are.
            properties=[PropertyRule("t", "uint32", "frwd", NgSection, allowedValues=("frwd", "bkwd", "vert"))],
        ),
        Rule(
            "P",
            "design",
            PSection,
            # P — Palette Structure gives P no substructures. Corpus/Pie/rpie.pie writes the palette as
            # a uint32 data list inside it, and each of the 23 palettes in the corpus is one such list
            # of exactly sixteen colors (corpus census 2026-09-10), which is the palette index range
            # 0 to 15 that General Equation Structure Properties gives the 'pi' property.
            substructures=[SubstructureRule("uint32", 1, 1, PSection, valueMinimum=16, valueMaximum=16)],
        ),
        Rule(
            "Ph",
            "equation",
            PhSection,
            # A phantom type outside the five renders as 'vert' with no error (measured 2026-09-13),
            # so this enumeration is narrower than the executable, as Al's is.
            properties=[
                PropertyRule("t", "uint32", "vert", PhSection, allowedValues=("vert", "horz", "full", "hzov", "flov"))
            ],
            # The specification gives Ph no substructures. Corpus/DocSvg/image/Phantoms2.pie line 19
            # writes a phantom holding the content it hides directly, a leading Bg and then equation
            # structures, which is the group's own arrangement; Corpus/DocSvg/image/Phantoms1.pie is
            # the same equation with that content visible inside the group. A Bg begins a line, so
            # the count is unbounded here as it is for Gr.
            substructures=[
                SubstructureRule("Equation", 0, None, PhSection),
                SubstructureRule("Bg", 1, None, PhSection),
            ],
            firstChild="Bg",
        ),
        Rule(
            "Pr",
            "equation",
            PrSection,
            properties=[PropertyRule("nb", "bool", False, PrSection)],
            substructures=[SubstructureRule("uint32", 0, 1, PrSection, valueMinimum=1, valueMaximum=1)],
        ),
        Rule(
            "Qe",
            "drawing",
            QeSection,
            properties=[PropertyRule("v", "bool", False, QeSection), *RoutedLineProperties(QeSection)],
            substructures=ConnectorSubstructures(QeSection),
        ),
        Rule(
            "Rd",
            "equation",
            RdSection,
            properties=[PropertyRule("ns", "bool", False, RdSection)],
            substructures=[SubstructureRule("Gr", 1, 2, RdSection)],
            groupTypes=((0, 1, 1), ("degr", 0, 1)),
        ),
        Rule(
            "Rr",
            "drawing",
            RrSection,
            properties=[PropertyRule("r", "uint8", 0, RrSection, minimum=0, maximum=2)],
            substructures=ConnectorSubstructures(RrSection),
        ),
        Rule("Rt", "drawing", RtSection, substructures=ConnectorSubstructures(RtSection)),
        Rule(
            "Sb",
            "equation",
            SbSection,
            properties=[
                PropertyRule("ro", "uint32", "math", SbSection, allowedValues=SymbolRoles),
                PropertyRule("st", "uint32", 0, SbSection, allowedValues=(0,) + SymbolStyles),
                PropertyRule("pf", "bool", False, SbSection),
                PropertyRule("tf", "bool", False, SbSection),
                PropertyRule("sc", "bool", False, SbSection),
                PropertyRule("cf", "bool", False, SbSection),
                PropertyRule("zr", "bool", False, SbSection),
                PropertyRule("nd", "bool", False, SbSection),
                PropertyRule("ns", "bool", False, SbSection),
                PropertyRule("nb", "bool", False, SbSection),
                # The specification omits this flag. Corpus/DocSvg/image/ShiftMathAxis.pie line 15
                # writes it on a symbol; the Symbols documentation page calls it "Shift math axis for
                # capitals".
                PropertyRule("ma", "bool", False, SbSection),
            ],
            substructures=[
                SubstructureRule("string", 1, 1, SbSection, valueMinimum=1, valueMaximum=1),
                SubstructureRule("Mk", 0, None, SbSection),
                SubstructureRule("Ng", 0, None, SbSection),
                SubstructureRule("Sl", 0, None, SbSection),
                SubstructureRule("En", 0, 1, SbSection),
            ],
        ),
        Rule(
            "Sc",
            "equation",
            ScSection,
            properties=[
                PropertyRule("pr", "bool", False, ScSection),
                PropertyRule("ow", "bool", False, ScSection),
                PropertyRule("ns", "bool", False, ScSection),
            ],
            substructures=[SubstructureRule("Gr", 1, 2, ScSection)],
            groupTypes=(("subs", 0, 1), ("sups", 0, 1)),
        ),
        Rule(
            "Sl",
            "modifier",
            SlSection,
            # A slash has no 'vert' type: Ng's third value renders as 'frwd' here and is written back as
            # a bare `Sl {}`, and so is any other value (measured 2026-09-13, Corpus/Pie/SlashTypes.pie).
            properties=[PropertyRule("t", "uint32", "frwd", SlSection, allowedValues=("frwd", "bkwd"))],
        ),
        Rule(
            "Sp",
            "equation",
            SpSection,
            # 's' carries no bound. The Spaces page's 72 mu maximum and −18 mu kern limit belong to
            # the Insert Space dialog: `Sp (s=100.0)` renders a 61.1111 pt gap and `Sp (s=-30.0)` an
            # 18.3333 pt kern (measured 2026-09-13, Corpus/Pie/SpaceBeyondTheDialogLimit.pie). With
            # 't' set the value is a repeating tab stop rather than a width.
            properties=[
                PropertyRule("s", "float", 0.0, SpSection),
                PropertyRule("t", "bool", False, SpSection),
            ],
        ),
        Rule(
            "St",
            "equation",
            StSection,
            properties=[PropertyRule("sm", "bool", False, StSection)],
            substructures=[SubstructureRule("Gr", 1, 3, StSection)],
            groupTypes=((0, 1, 1), ("lowr", 0, 1), ("uppr", 0, 1)),
        ),
        Rule(
            "V",
            "design",
            VSection,
            properties=[
                PropertyRule("d", "uint32", 0, VSection, allowedValues=ValueDomains),
                # The name must exist in the domain, which DesignParameters.Domains enumerates and
                # Validator.CheckDesignParameter holds the structure to, together with the range the
                # dialogs give the parameter (measured 2026-09-13, ADR-0008).
                PropertyRule("n", "uint32", None, VSection, required=True),
            ],
            # V — Value Structure gives V no substructures. Corpus/Pie/test11.pie writes the parameter
            # value as a float data list inside it, and each of the 26 value structures in the corpus
            # holds exactly one data list (corpus census 2026-09-10) holding one value; any primitive
            # type is accepted here because the document says nothing about which types a design
            # parameter can take, and Validator.CheckDesignParameter holds the value to a number.
            # `V (n='fsiz') {f{}}` is dropped from the design Radical Pie saves (measured 2026-09-14).
            substructures=[SubstructureRule("anyPrimitive", 1, 1, VSection, valueMinimum=1, valueMaximum=1)],
        ),
        Rule(
            "Wm",
            "equation",
            WmSection,
            properties=[
                PropertyRule(
                    "t",
                    "uint32",
                    "line",
                    WmSection,
                    allowedValues=(
                        "line",
                        "dlin",
                        "what",
                        "chck",
                        "smil",
                        "frwn",
                        "tild",
                        "brck",
                        "brac",
                        "shel",
                        "larw",
                        "rarw",
                        "barw",
                        "luhp",
                        "ruhp",
                        "buhp",
                        "ldhp",
                        "rdhp",
                        "bdhp",
                    ),
                ),
                PropertyRule("un", "bool", False, WmSection),
                PropertyRule("sm", "bool", False, WmSection),
            ],
            substructures=[SubstructureRule("Gr", 1, 2, WmSection)],
            groupTypes=((0, 1, 1), ("labl", 0, 1)),
        ),
        Rule(
            "X",
            "connector",
            XSection,
            substructures=[
                SubstructureRule("ref", 1, 1, XSection),
                SubstructureRule("uint32", 1, 1, XSection),
                SubstructureRule("int32", 1, 1, XSection),
                SubstructureRule("float", 0, 1, XSection),
            ],
        ),
        Rule(
            "Zg",
            "drawing",
            ZgSection,
            properties=[PropertyRule("v", "bool", False, ZgSection), *RoutedLineProperties(ZgSection)],
            substructures=ConnectorSubstructures(ZgSection),
        ),
    ]
}


def IsCategory(identifier, category):
    rule = Structures.get(identifier)
    return rule is not None and rule.category == category

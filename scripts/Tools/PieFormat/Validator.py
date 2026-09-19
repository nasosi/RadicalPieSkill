"""Validation of a Radical Pie equation against the catalogue in Schema.py.

Validate returns one PieError per violation, each naming the line, the column, the path through the
structure tree, the message and the FileFormat.md section that the rule comes from. An empty list
means the text satisfies every rule the catalogue carries.

ValidateFile reads a .pie file, or a .svg file that carries equations. Radical Pie writes the equation
text into an SVG as the first equation-shaped XML comment, and InkRadix writes it into an
`<inkradix:radicalpie><inkradix:datav1>` element; a composite drawing carries one such carrier per
Radical Pie object. ExtractAllPieFromSvg returns every one of them in document order and ValidateFile
validates each, prefixing the path of every error with the equation index when there is more than one.
ExtractPieFromSvg returns the first, for a caller that needs one equation.

The file must be UTF-8 text without a byte order mark, which ValidateFile reports as one error rather
than raising.

Three rules hold a drawing structure to what the executable does with its properties rather than to
what the specification offers it: a line object drops the fill, a joist drops the stroke width and the
dashing, and a zigzag with the third dash pattern crashes. A fourth holds a shape's two anchors apart,
because one anchor twice is a shape with no area. CheckDrawingProperties and CheckShapeAnchors carry
them, and Schema.py records the render each was measured by.

Anchors are checked in a pass of their own, because a connector's reference is resolved against the
whole file: CollectAnchorTargets indexes every named node, reporting a name given twice, and
CheckAnchors then holds every anchor to the anchor-type table and the measured anchor counts in
Schema.py. An anchor type a structure does not own, and an index past the last anchor of a type, crash
Radical Pie with an access violation instead of raising its invalid-data dialog, so this pass is one of
the things standing between a writer and a crash.

Five more rules stand there, each measured on 2026-09-14 against Radical Pie 1.15 and each carrying the
render in its own doc comment: CheckValueRanges holds every data-list value to the width of its
primitive type and every Unicode character value to the last code point, CheckPropertyRange does the
same for a property whose table row states no range of its own, CheckStyleMapFonts holds a style map's
first index to a slot that holds a font, CheckGroupConnector refuses an X in a group that is not of
type 'anno', and CollectAnchorTargets refuses a repeated name. CheckBondArrays and CheckDesignParameter
cover the other direction, the values Radical Pie reads and then drops without a word.

One rule is about how an equation travels rather than about how it is written: CheckCarrierComment
refuses a text that ends the XML comment the SVG carrier holds an equation in. RefusalMessage is that
whole gate as one string, which every pipeline's command line runs over its .pie files before it
launches anything, because Radical Pie drops a structure it does not know instead of refusing the file.
FirstViolation is the same gate for one equation handed over as text, which is what a pipeline's library
entry point gets, and it gives the first violation alone for an error that names the key beside it.
"""

import codecs
import re
from pathlib import Path

from . import OpenDdl, Schema


class PieError:
    """One violation, ready to print as file:line:col path: message [section]."""

    __slots__ = ("line", "column", "path", "message", "section")

    def __init__(self, line, column, path, message, section):
        self.line = line
        self.column = column
        self.path = path
        self.message = message
        self.section = section

    def __repr__(self):
        return "PieError({}:{} {} {!r} [{}])".format(self.line, self.column, self.path, self.message, self.section)


def FormatValue(value):
    if value is None:
        return "null"

    if value is True:
        return "true"

    if value is False:
        return "false"

    if isinstance(value, str):
        return "'{}'".format(value)

    return str(value)


def FormatValues(values):
    return ", ".join(FormatValue(value) for value in values)


def Step(node):
    """One path element: the identifier, with the group type when the structure carries one."""

    if isinstance(node, OpenDdl.DataList):
        return node.primitiveType

    if "t" in node.properties:
        return "{}(t={})".format(node.identifier, FormatValue(node.properties["t"]))

    return node.identifier


def Join(path, node):
    step = Step(node)
    return step if not path else "{}/{}".format(path, step)


def ValueTypeOf(value):
    """The name the error message gives to the kind of value the text actually carried."""

    if isinstance(value, bool):
        return "a bool"

    if isinstance(value, int):
        return "an integer"

    if isinstance(value, float):
        return "a floating-point number"

    if value is None:
        return "null"

    if isinstance(value, OpenDdl.CharLiteral):
        return "a character literal"

    return "a string"


def Accepts(valueType, value):
    if valueType == "bool":
        # OpenDDL 3.0 admits 0 and 1 as bool literals.
        return isinstance(value, bool) or (isinstance(value, int) and value in (0, 1))

    if valueType == "uint32":
        # A uint32 property carries either a number or a character literal such as 'vert', which the
        # format packs into the integer. A string literal is a different literal and is not accepted.
        return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, OpenDdl.CharLiteral)

    if valueType in ("int32", "uint8"):
        return isinstance(value, int) and not isinstance(value, bool)

    if valueType == "float":
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    return True


def CharLiteralExample(propertyRule):
    """A character literal the error message can show, taken from the default or the enumeration."""

    if isinstance(propertyRule.default, str):
        return propertyRule.default

    if propertyRule.allowedValues is not None:
        for value in propertyRule.allowedValues:
            if isinstance(value, str):
                return value

    return None


def PropertyValueMessage(name, propertyRule, value):
    """The message for a property value of a kind the property does not take."""

    # A string literal reaches here only where a uint32 property wanted a character literal.
    if propertyRule.valueType == "uint32" and isinstance(value, str):
        example = CharLiteralExample(propertyRule)

        if example is None:
            return "property {!r} expects a character literal or an integer, found a string".format(name)

        return "property {!r} expects a character literal such as {}, found a string".format(name, FormatValue(example))

    return "property {!r} expects {}, found {}".format(name, propertyRule.valueType, ValueTypeOf(value))


def CheckProperties(structure, rule, path, errors):
    for name, value in structure.properties.items():
        propertyRule = rule.properties.get(name)

        if propertyRule is None:
            errors.append(
                PieError(
                    structure.line,
                    structure.column,
                    path,
                    "property {!r} is not defined for {}".format(name, structure.identifier),
                    rule.section,
                )
            )
            continue

        if not Accepts(propertyRule.valueType, value):
            errors.append(
                PieError(
                    structure.line,
                    structure.column,
                    path,
                    PropertyValueMessage(name, propertyRule, value),
                    propertyRule.section,
                )
            )
            continue

        # A character literal is packed into the integer the property holds, four characters at most.
        if isinstance(value, OpenDdl.CharLiteral) and len(value) > 4:
            errors.append(
                PieError(
                    structure.line,
                    structure.column,
                    path,
                    "property {!r} takes a character literal of at most four characters, found {}".format(
                        name, FormatValue(value)
                    ),
                    propertyRule.section,
                )
            )
            continue

        if propertyRule.allowedValues is not None and value not in propertyRule.allowedValues:
            errors.append(
                PieError(
                    structure.line,
                    structure.column,
                    path,
                    "property {!r} must be one of {}, found {}".format(
                        name, FormatValues(propertyRule.allowedValues), FormatValue(value)
                    ),
                    propertyRule.section,
                )
            )
            continue

        CheckPropertyRange(structure, propertyRule, value, path, errors)
        CheckPropertyRequires(structure, rule, propertyRule, value, path, errors)

    for name, propertyRule in rule.properties.items():
        if propertyRule.required and name not in structure.properties:
            errors.append(
                PieError(
                    structure.line,
                    structure.column,
                    path,
                    "{} needs property {!r}".format(structure.identifier, name),
                    propertyRule.section,
                )
            )


def CheckPropertyRange(structure, propertyRule, value, path, errors):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return

    limits = Schema.IntegerRanges.get(propertyRule.valueType)

    if limits is not None and propertyRule.minimum is None and propertyRule.maximum is None:
        # The property's own table row gives it no range, so the range is the width of its type.
        # Radical Pie wraps a value past that width instead of refusing it: `Sb (co=-1)` is saved as
        # `co=0xFFFFFFFF` and draws white ink (measured 2026-09-14), which nothing else reports.
        minimum, maximum = limits

        if not minimum <= value <= maximum:
            errors.append(
                PieError(
                    structure.line,
                    structure.column,
                    path,
                    "property {!r} is a {}, whose values are {} to {}, found {}".format(
                        propertyRule.name, propertyRule.valueType, minimum, maximum, FormatValue(value)
                    ),
                    propertyRule.section,
                )
            )

        return

    if propertyRule.minimum is not None and propertyRule.maximum is not None:
        if not propertyRule.minimum <= value <= propertyRule.maximum:
            errors.append(
                PieError(
                    structure.line,
                    structure.column,
                    path,
                    "property {!r} must be in the range {} to {}, found {}".format(
                        propertyRule.name, propertyRule.minimum, propertyRule.maximum, FormatValue(value)
                    ),
                    propertyRule.section,
                )
            )

        return

    if propertyRule.minimum is not None and propertyRule.minimumExclusive and value <= propertyRule.minimum:
        errors.append(
            PieError(
                structure.line,
                structure.column,
                path,
                "property {!r} must be greater than {}, found {}".format(
                    propertyRule.name, propertyRule.minimum, FormatValue(value)
                ),
                propertyRule.section,
            )
        )


def CheckPropertyRequires(structure, rule, propertyRule, value, path, errors):
    if propertyRule.requires is None or not value:
        return

    otherName, allowedValues = propertyRule.requires
    otherRule = rule.properties[otherName]
    otherValue = structure.properties.get(otherName, otherRule.default)

    if otherValue not in allowedValues:
        errors.append(
            PieError(
                structure.line,
                structure.column,
                path,
                "property {!r} can be true only when {!r} is one of {}, found {}".format(
                    propertyRule.name, otherName, FormatValues(allowedValues), FormatValue(otherValue)
                ),
                propertyRule.section,
            )
        )


def MatchingRule(rule, child):
    """The substructure rule that a child falls under, or None when the structure may not hold it."""

    if isinstance(child, OpenDdl.DataList):
        for substructureRule in rule.substructures:
            if substructureRule.target == child.primitiveType:
                return substructureRule

        for substructureRule in rule.substructures:
            if substructureRule.target == "anyPrimitive":
                return substructureRule

        return None

    for substructureRule in rule.substructures:
        if substructureRule.target == child.identifier:
            return substructureRule

    if Schema.IsCategory(child.identifier, "equation"):
        for substructureRule in rule.substructures:
            if substructureRule.target == "Equation":
                return substructureRule

    return None


def TargetName(target):
    if target == "Equation":
        return "equation structure"

    if target == "anyPrimitive":
        return "data list"

    if target in OpenDdl.DataTypeSpellings.values():
        return "{} data list".format(target)

    return "{} substructure".format(target)


def Counted(count, name):
    return "{} {}".format(count, name if count == 1 else name + "s")


def CheckChildren(structure, rule, path, errors):
    counts = {substructureRule.target: 0 for substructureRule in rule.substructures}

    for child in structure.children:
        childRule = MatchingRule(rule, child)

        if childRule is None:
            if isinstance(child, OpenDdl.Structure) and child.identifier not in Schema.Structures:
                # The recursion reports the unknown structure itself; one error is enough.
                continue

            errors.append(
                PieError(
                    child.line,
                    child.column,
                    Join(path, child),
                    "{} may not hold a {}".format(structure.identifier, TargetName(Step(child))),
                    rule.section,
                )
            )
            continue

        counts[childRule.target] += 1

        if isinstance(child, OpenDdl.DataList):
            CheckDataList(child, childRule, structure, Join(path, child), errors)

    for substructureRule in rule.substructures:
        count = counts[substructureRule.target]
        name = TargetName(substructureRule.target)

        if count < substructureRule.minimum:
            errors.append(
                PieError(
                    structure.line,
                    structure.column,
                    path,
                    "{} needs at least {}, found {}".format(
                        structure.identifier, Counted(substructureRule.minimum, name), count
                    ),
                    substructureRule.section,
                )
            )
        elif substructureRule.maximum is not None and count > substructureRule.maximum:
            errors.append(
                PieError(
                    structure.line,
                    structure.column,
                    path,
                    "{} takes at most {}, found {}".format(
                        structure.identifier, Counted(substructureRule.maximum, name), count
                    ),
                    substructureRule.section,
                )
            )

    if rule.firstChild is not None:
        first = structure.children[0] if structure.children else None

        if first is None or isinstance(first, OpenDdl.DataList) or first.identifier != rule.firstChild:
            found = "nothing" if first is None else Step(first)
            errors.append(
                PieError(
                    structure.line,
                    structure.column,
                    path,
                    "the first substructure of {} must be {}, found {}".format(
                        structure.identifier, rule.firstChild, found
                    ),
                    rule.section,
                )
            )


def DataListValues(dataList):
    """Every value of a data list, whether it is written flat or in subarrays."""

    if dataList.subarraySize is None:
        return dataList.values

    return [value for subarray in dataList.values for value in subarray]


def CheckValueRanges(dataList, substructureRule, structure, path, errors):
    """Every value of a data list against the range of its primitive type, and code points against Unicode.

    Radical Pie reads a value with the width its type names and wraps anything past it, which is the
    hole the one guard on a style map's first index had: `M (t='uprt') {u8{-1}}` is the refused
    `u8{255}` after the wrap and crashes Radical Pie with the access violation 3221225477, as does
    `u8{300}`, which is slot 44 (measured 2026-09-14 and 2026-09-13).

    The five structures of Schema.UnicodeValueStructures hold character values rather than numbers, and
    a value past the last code point crashes the same way: `Mk {u32{0x110000}}`, `Br {u32{0x110000,...}}`
    and `Pr {u32{0x110000}}` each exited 3221225477 before rendering, and so did `In { u32{-1} ... }`
    (measured 2026-09-14). A character literal carries no range: the format packs it into the integer.
    """

    limits = Schema.IntegerRanges.get(dataList.primitiveType)

    if limits is None:
        return

    minimum, maximum = limits
    holdsCodePoints = structure.identifier in Schema.UnicodeValueStructures and dataList.primitiveType == "uint32"

    for value in DataListValues(dataList):
        if not isinstance(value, int) or isinstance(value, bool):
            continue

        if not minimum <= value <= maximum:
            errors.append(
                PieError(
                    dataList.line,
                    dataList.column,
                    path,
                    "a {} value is {} to {}, found {}".format(
                        dataList.primitiveType, minimum, maximum, FormatValue(value)
                    ),
                    substructureRule.section,
                )
            )
            continue

        if holdsCodePoints and value > Schema.MaximumCodePoint:
            errors.append(
                PieError(
                    dataList.line,
                    dataList.column,
                    path,
                    "a Unicode character value is 0 to 0x{:X}, found 0x{:X}; a higher one crashes Radical Pie".format(
                        Schema.MaximumCodePoint, value
                    ),
                    substructureRule.section,
                )
            )


def CheckDataList(dataList, substructureRule, structure, path, errors):
    CheckValueRanges(dataList, substructureRule, structure, path, errors)

    if substructureRule.subarraySize != dataList.subarraySize:
        expected = (
            "a flat list"
            if substructureRule.subarraySize is None
            else "subarrays of {}".format(substructureRule.subarraySize)
        )
        errors.append(
            PieError(
                dataList.line,
                dataList.column,
                path,
                "{} needs {} here".format(structure.identifier, expected),
                substructureRule.section,
            )
        )
        return

    count = len(dataList.values)

    if substructureRule.valueMinimum is not None and count < substructureRule.valueMinimum:
        errors.append(
            PieError(
                dataList.line,
                dataList.column,
                path,
                "this {} data list needs at least {}, found {}".format(
                    dataList.primitiveType, Counted(substructureRule.valueMinimum, "value"), count
                ),
                substructureRule.section,
            )
        )

    if substructureRule.valueMaximum is not None and count > substructureRule.valueMaximum:
        errors.append(
            PieError(
                dataList.line,
                dataList.column,
                path,
                "this {} data list takes at most {}, found {}".format(
                    dataList.primitiveType, Counted(substructureRule.valueMaximum, "value"), count
                ),
                substructureRule.section,
            )
        )

    if structure.identifier == "Sb" and dataList.primitiveType == "string":
        if any(value == "" for value in dataList.values):
            errors.append(
                PieError(
                    dataList.line,
                    dataList.column,
                    path,
                    "the text of a symbol must not be the empty string",
                    Schema.SbSection,
                )
            )


def HoldsGroups(rule):
    return any(substructureRule.target in ("Gr", "Equation") for substructureRule in rule.substructures)


def CheckGroupTypes(structure, rule, path, errors):
    """The group type table gives every type but 0 to a subgroup of the structures that name it.

    A structure that holds groups and names no subgroup type, Gr and Ph, therefore takes the default
    type only. The 'anno' type belongs to a top-level group, which CheckFileSections covers.
    """

    if rule.groupTypes is None and not HoldsGroups(rule):
        return

    declaredTypes = (0,) if rule.groupTypes is None else tuple(groupType for groupType, _, _ in rule.groupTypes)
    counts = {groupType: 0 for groupType in declaredTypes}

    for child in structure.children:
        if isinstance(child, OpenDdl.DataList) or child.identifier != "Gr":
            continue

        groupType = child.properties.get("t", 0)

        if groupType not in declaredTypes:
            errors.append(
                PieError(
                    child.line,
                    child.column,
                    Join(path, child),
                    "{} does not take a group of type {}".format(structure.identifier, FormatValue(groupType)),
                    rule.section,
                )
            )
            continue

        counts[groupType] += 1

    if rule.groupTypes is None:
        return

    for groupType, minimum, maximum in rule.groupTypes:
        count = counts[groupType]
        described = "the default type" if groupType == 0 else "type {}".format(FormatValue(groupType))

        if count < minimum:
            errors.append(
                PieError(
                    structure.line,
                    structure.column,
                    path,
                    "{} needs {} of {}, found {}".format(
                        structure.identifier, Counted(minimum, "group"), described, count
                    ),
                    rule.section,
                )
            )
        elif count > maximum:
            errors.append(
                PieError(
                    structure.line,
                    structure.column,
                    path,
                    "{} takes at most {} of {}, found {}".format(
                        structure.identifier, Counted(maximum, "group"), described, count
                    ),
                    rule.section,
                )
            )


def CheckMatrixEntries(structure, path, errors):
    """Mx: one subgroup for each matrix entry, entries listed in row-major order."""

    rows = structure.properties.get("r")
    columns = structure.properties.get("c")

    if not isinstance(rows, int) or isinstance(rows, bool):
        return

    if not isinstance(columns, int) or isinstance(columns, bool):
        return

    # CheckProperties reports a count outside 1 to 32; the entry count would only repeat it.
    if not 1 <= rows <= 32 or not 1 <= columns <= 32:
        return

    entries = sum(
        1 for child in structure.children if isinstance(child, OpenDdl.Structure) and child.identifier == "Gr"
    )

    if entries != rows * columns:
        errors.append(
            PieError(
                structure.line,
                structure.column,
                path,
                "Mx with r={} and c={} needs {} groups, found {}".format(rows, columns, rows * columns, entries),
                Schema.MxSection,
            )
        )


def CheckArrowValues(array, allowed, describe, path, errors):
    """Every value of one of Ar's uint32 arrays is a name the catalogue lists."""

    for value in array.values:
        if value in allowed:
            continue

        errors.append(
            PieError(
                array.line,
                array.column,
                path,
                "{}, found {}".format(describe, FormatValue(value)),
                Schema.ArSection,
            )
        )


def CheckArrowArrays(structure, path, errors):
    """Ar: the first uint32 array holds one to three arrow types, and one charm array follows each arrow.

    The values inside the arrays are held to the catalogue's two enumerations, which is narrower than
    Radical Pie 1.15: an arrow type outside the four draws a full-length arrow and a charm outside the
    forty is dropped, both without a word (ADR-0007, measured 2026-09-13). What is deliberately not
    checked is where a charm sits. The specification's charm table marks each type legal at the left
    end, the right end or the interior, and all forty draw at all three positions, so the columns are
    the Insert Arrow dialog's palettes; the same measurement put five charms at one position, past the
    table's three.
    """

    arrays = [
        child for child in structure.children if isinstance(child, OpenDdl.DataList) and child.primitiveType == "uint32"
    ]

    if not arrays:
        # CheckChildren reports the missing arrays.
        return

    arrows = len(arrays[0].values)

    if not 1 <= arrows <= 3:
        errors.append(
            PieError(
                arrays[0].line,
                arrays[0].column,
                Join(path, arrays[0]),
                "the arrow type array holds one, two, or three values, found {}".format(arrows),
                Schema.ArSection,
            )
        )
        return

    CheckArrowValues(
        arrays[0],
        Schema.ArrowTypes,
        "an arrow type must be one of {}".format(FormatValues(Schema.ArrowTypes)),
        Join(path, arrays[0]),
        errors,
    )

    for array in arrays[1:]:
        CheckArrowValues(
            array,
            Schema.CharmTypes + Schema.CharmAlignments,
            "a charm array holds charm types and the alignments {}".format(FormatValues(Schema.CharmAlignments)),
            Join(path, array),
            errors,
        )

    if len(arrays) != arrows + 1:
        errors.append(
            PieError(
                structure.line,
                structure.column,
                path,
                "Ar with {} needs {} uint32 arrays, the arrow types and one charm array per arrow, found {}".format(
                    Counted(arrows, "arrow"), arrows + 1, len(arrays)
                ),
                Schema.ArSection,
            )
        )


def CheckBondPairs(array, structure, groupTypes, valueTypes, describe, path, errors):
    """One of Bd's two arrays: each pair names a direction the site holds and a value from its table."""

    for pair in array.values:
        groupType, value = pair

        if groupType not in groupTypes:
            errors.append(
                PieError(
                    array.line,
                    array.column,
                    path,
                    "the first value of a pair here is one of {}, found {}".format(
                        FormatValues(groupTypes), FormatValue(groupType)
                    ),
                    Schema.BdSection,
                )
            )
        elif groupType != 0 and not HoldsGroupOfType(structure, groupType):
            errors.append(
                PieError(
                    array.line,
                    array.column,
                    path,
                    "a pair names group type {}, which this bond site does not hold; the bond and the "
                    "atoms at its end are dropped in silence".format(FormatValue(groupType)),
                    Schema.BdSection,
                )
            )

        if value not in valueTypes:
            errors.append(
                PieError(
                    array.line,
                    array.column,
                    path,
                    "{}, found {}".format(describe, FormatValue(value)),
                    Schema.BdSection,
                )
            )


def CheckBondArrays(structure, path, errors):
    """Bd: the first uint32[2] array pairs a direction with a bond type, the second with an angle type.

    The bond types are the fifteen of the specification's table with their capitalised long forms, and a
    value outside them is drawn as a single bond and written back into the saved equation unchanged:
    `u32[2]{{0,'zzzz'}}` and `u32[2]{{0,'sing'}}` each rendered 15.6075 by 9 pt (measured 2026-09-14), so
    this enumeration is narrower than the executable the way Ar's two are (ADR-0007). A pair naming a
    direction whose group the site does not hold is dropped with the atoms at its end: 7.33691 by 9 pt
    against the control's 7.94385 by 28 pt, with the pair written back unchanged (measured 2026-09-14).
    Angles belong to the four diagonal bonds alone, which is the specification's own restriction.
    """

    arrays = [
        child
        for child in structure.children
        if isinstance(child, OpenDdl.DataList) and child.primitiveType == "uint32" and child.subarraySize == 2
    ]

    if not arrays:
        # CheckChildren reports a bond structure with no array and one written as a flat list.
        return

    CheckBondPairs(
        arrays[0],
        structure,
        Schema.BondGroupTypes,
        Schema.BondTypeValues,
        "a bond type is one of the fifteen the specification lists, or one of those with its first "
        "letter capitalised for a long bond",
        Join(path, arrays[0]),
        errors,
    )

    for array in arrays[1:]:
        CheckBondPairs(
            array,
            structure,
            Schema.BondAngleGroupTypes,
            Schema.BondAngleTypes,
            "an angle type is one of {}".format(FormatValues(Schema.BondAngleTypes)),
            Join(path, array),
            errors,
        )


def CheckGroupConnector(structure, path, errors):
    """Gr: an annotation group contains a connector structure, and no other group may hold one.

    The specification's substructure table gives every group an X and says of it only that "an
    annotation group must contain a connector structure". The other half is measured: an X in the main
    equation group, or in any subgroup, exits Radical Pie with the access violation 3221225477 before it
    renders anything (measured 2026-09-14), so the validator is the only thing that refuses it.
    """

    isAnnotation = structure.properties.get("t") == "anno"
    connector = next(
        (child for child in structure.children if isinstance(child, OpenDdl.Structure) and child.identifier == "X"),
        None,
    )

    if isAnnotation and connector is None:
        errors.append(
            PieError(
                structure.line,
                structure.column,
                path,
                "an annotation group must contain an X substructure",
                Schema.GrSection,
            )
        )

    if not isAnnotation and connector is not None:
        errors.append(
            PieError(
                connector.line,
                connector.column,
                Join(path, connector),
                "a connector belongs to a drawing structure or to a group of type 'anno'; an X in any "
                "other group crashes Radical Pie",
                Schema.GrSection,
            )
        )


def GroupHoldsNoContent(group):
    """Whether a Gr's children are its Bg alone, holding no structure that draws anything."""

    return all(isinstance(child, OpenDdl.Structure) and child.identifier == "Bg" for child in group.children)


def BracketDrawsAPairOfGlyphs(structure):
    """Whether a Br draws a glyph on both sides: the case an empty group makes visibly empty.

    Corpus/Pie/eq.pie line 572 writes `Br (pi=5) { u32{0x28,0x00} Gr (ba='mddl') { Bg {} } }`, a
    left-only delimiter whose group is empty on purpose: the right character 0x00 draws nothing on that
    side (Pitfalls.md), so the bracket places one glyph rather than an empty pair, and the number it
    delimits is written as ordinary symbols beside it. A Br with no u32 array is a parenthesis pair
    (Pitfalls.md), both sides drawn, and a Br with a 0 on both sides draws no glyph at all, no
    different from a phantom.
    """

    arrays = (child for child in structure.children if isinstance(child, OpenDdl.DataList))
    array = next((child for child in arrays if child.primitiveType == "uint32"), None)

    if array is None or len(array.values) < 2:
        return True

    left, right = array.values[0], array.values[1]

    return left != 0 and right != 0


def CheckBracketContent(structure, path, errors):
    """Br: a bracket that draws a glyph on both sides around an empty group draws a visible "( )".

    Measured on RadicalPie 1.15, 2026-09-12 (Br — Bracket Structure): an empty bracket renders that
    visible pair rather than nothing. A caller wanting to anchor a line at the end of a term names the
    term's last structure with `$name` instead of wrapping an otherwise-empty Gr in Br to get a target;
    `Pr {}` is the normal, ink-free form of a prime and is not a Br, and an empty St or Gr elsewhere is
    a legitimate invisible anchor because neither one draws glyphs of its own.
    """

    if not BracketDrawsAPairOfGlyphs(structure):
        return

    if any(
        isinstance(child, OpenDdl.Structure) and child.identifier == "Gr" and GroupHoldsNoContent(child)
        for child in structure.children
    ):
        errors.append(
            PieError(
                structure.line,
                structure.column,
                path,
                "a bracket around nothing draws its glyphs; to anchor a line at the end of a term, name "
                "the term's last structure with $name instead",
                Schema.BrSection,
            )
        )


def CheckDesignParameter(structure, path, errors):
    """V: the name must exist in the domain, and its one value must be a number in the dialog's range.

    Measured 2026-09-13 (V — Value Structure, Docs/ARCHITECTURE.md format facts): Radical Pie drops a
    parameter whose name it does not know, and one written in the wrong domain, from the design it saves
    without a word, so a misspelling here has no other reader. It does not clamp a value either:
    `V (d='intg',n='slnt') {f{90.0}}` against a maximum of 20 rendered an SVG of width `INF`.

    A value that is not a number is dropped the same way: `V (n='fsiz') {s{"24.0"}}`, a doubled font
    size, rendered the geometry of the same equation under an empty design and was saved as `D { }`
    (measured 2026-09-14). The count of the values is Schema's own rule on V's data list.
    """

    domain = structure.properties.get("d", 0)
    name = structure.properties.get("n")
    parameters = Schema.DesignParameters.get(domain)

    # CheckProperties reports an unknown domain and a missing or wrongly typed name.
    if parameters is None or not isinstance(name, str):
        return

    if name not in parameters:
        errors.append(
            PieError(
                structure.line,
                structure.column,
                path,
                "the domain {} holds no design parameter named {!r}".format(FormatValue(domain), name),
                Schema.VSection,
            )
        )
        return

    minimum, maximum = parameters[name]

    for child in structure.children:
        if not isinstance(child, OpenDdl.DataList):
            continue

        for value in DataListValues(child):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(
                    PieError(
                        child.line,
                        child.column,
                        Join(path, child),
                        "the design parameter {!r} takes a number, found {}; Radical Pie drops a "
                        "parameter it cannot read".format(name, ValueTypeOf(value)),
                        Schema.VSection,
                    )
                )
                continue

            if not minimum <= value <= maximum:
                errors.append(
                    PieError(
                        child.line,
                        child.column,
                        Join(path, child),
                        "the design parameter {!r} must be in the range {:g} to {:g}, found {}".format(
                            name, minimum, maximum, FormatValue(value)
                        ),
                        Schema.VSection,
                    )
                )


def FilledFontSlots(design):
    """The font slots that hold a font: the factory design's own, and the slot of every F written here.

    A design merges into the factory design, so a slot the file does not name still holds the factory's
    font (Docs/ARCHITECTURE.md, format facts). The F structures of this design add to those slots; the
    later indexes of a style map are its fallbacks and may name any slot, filled or not, because Radical
    Pie fills them from the factory chain itself (`M (t='uprt') {u8{1}}` is saved as `u8{1,1,7,5}`).
    """

    slots = set(range(Schema.HighestFactoryFontSlot + 1))

    for child in design.children:
        if not (isinstance(child, OpenDdl.Structure) and child.identifier == "F"):
            continue

        index = child.properties.get("i")

        if isinstance(index, int) and not isinstance(index, bool):
            slots.add(index)

    return slots


def CheckStyleMapFonts(structure, slots, path, errors):
    """M: the first index of a style map names a slot that holds a font, which 255 never does.

    Measured 2026-09-13 (M — Map Structure): `M (t='uprt') {u8{255}}` and `M (t='uprt') {u8{255,8,0,1}}`
    each crashed Radical Pie with the access violation 3221225477 before it rendered anything, while
    `M (t='uprt') {u8{8,255,255,255}}`, the shape the operator's design fixture writes, rendered.

    Measured 2026-09-14, one render per slot on a design holding the map alone: slots 1, 7 and 8 render,
    each in its own face, and slots 9 and 20 crash with the same access violation. 300, which is slot 44
    after the uint8 wrap, drew every glyph as the missing-glyph box instead (2026-09-13). So a first
    index no font fills is a crash or a page of boxes, and the slots that hold one without an F of their
    own are 0 to Schema.HighestFactoryFontSlot.
    """

    for child in structure.children:
        if not isinstance(child, OpenDdl.DataList) or child.primitiveType != "uint8" or not child.values:
            continue

        index = child.values[0]

        if not isinstance(index, int) or isinstance(index, bool):
            continue

        if index == Schema.NoFontIndex:
            errors.append(
                PieError(
                    child.line,
                    child.column,
                    Join(path, child),
                    "the first index of a style map is its primary font, and {} means no font; put it in a "
                    "later slot".format(Schema.NoFontIndex),
                    Schema.MSection,
                )
            )
            continue

        # CheckValueRanges reports an index outside the uint8 range; this rule reads the slot it wrapped to.
        if index in slots or not 0 <= index <= Schema.IntegerRanges["uint8"][1]:
            continue

        own = sorted(slot for slot in slots if slot > Schema.HighestFactoryFontSlot)
        adds = "adds none" if not own else "adds {}".format(", ".join(str(slot) for slot in own))

        errors.append(
            PieError(
                child.line,
                child.column,
                Join(path, child),
                "the first index of a style map is its primary font, and no font fills slot {}, which "
                "crashes Radical Pie; the factory design fills slots 0 to {} and this design {}".format(
                    index, Schema.HighestFactoryFontSlot, adds
                ),
                Schema.MSection,
            )
        )


def CheckDesignFonts(design, path, errors):
    """D: every style map of the design against the font slots that design fills."""

    slots = FilledFontSlots(design)

    for child in design.children:
        if isinstance(child, OpenDdl.Structure) and child.identifier == "M":
            CheckStyleMapFonts(child, slots, Join(path, child), errors)


ConnectorValueNames = {
    "ref": ("reference", "references"),
    "uint32": ("anchor type", "anchor types"),
    "int32": ("index", "indexes"),
    "float": ("rail offset", "rail offsets"),
}


def CheckConnectorArity(structure, path, errors):
    """X: a drawing structure's connector holds two anchors, an annotation group's holds one.

    Probed against RadicalPie 1.15 on 2026-09-10 (Docs/ARCHITECTURE.md format facts): a drawing
    structure's X with a single anchor crashes Radical Pie with an access violation. The
    specification's substructure minimum and maximum of one for X's ref, uint32, int32 and float
    lists counts the lists, not the values each one holds.
    """

    isAnnotation = structure.identifier == "Gr" and structure.properties.get("t") == "anno"

    if not isAnnotation and not Schema.IsCategory(structure.identifier, "drawing"):
        return

    expected = 1 if isAnnotation else 2
    expectedWord = "one" if isAnnotation else "two"
    plural = "" if isAnnotation else "s"

    for child in structure.children:
        if not (isinstance(child, OpenDdl.Structure) and child.identifier == "X"):
            continue

        connectorPath = Join(path, child)

        for dataList in child.children:
            if not isinstance(dataList, OpenDdl.DataList) or dataList.primitiveType not in ConnectorValueNames:
                continue

            count = len(dataList.values)

            if count == expected:
                continue

            singular, pluralName = ConnectorValueNames[dataList.primitiveType]
            found = "{} {}".format(count, singular if count == 1 else pluralName)

            errors.append(
                PieError(
                    dataList.line,
                    dataList.column,
                    connectorPath,
                    "X inside {} connects {} anchor{}: {} holds {}".format(
                        Step(structure), expectedWord, plural, dataList.primitiveType, found
                    ),
                    Schema.XSection,
                )
            )


def CheckDrawingProperties(structure, path, errors):
    """A drawing property the structure it is written on does nothing with, and the one that crashes.

    A line object draws with its stroke colour and drops the fill (Drawing Tools), and a joist, which
    is a bracket or a brace, drops the stroke width and the dashing as well (Radical Pie Editor
    Window). Radical Pie renders such a file and says nothing, so a writer who asks for a red arrow
    with `fco` gets a black one; the two rules here are the only place that says so. Measured
    2026-09-13, one render per property, in Schema.LineFillProperties and Schema.JoistStrokeProperties.

    The third rule is a crash and not a silence: `Zg (d=3)` exits with an access violation before it
    renders anything.
    """

    if structure.identifier not in Schema.LineStructures:
        return

    isJoist = structure.identifier == "Jo"
    ignored = Schema.LineFillProperties + (Schema.JoistStrokeProperties if isJoist else ())

    for name in ignored:
        if name not in structure.properties:
            continue

        reason = (
            "the stroke width and the dashing of a bracket or a brace"
            if name in Schema.JoistStrokeProperties
            else "the fill of a line object"
        )

        errors.append(
            PieError(
                structure.line,
                structure.column,
                path,
                "{} draws none of {}: {!r} is dropped in silence, so set the stroke instead".format(
                    Step(structure), reason, name
                ),
                Schema.GeneralDrawingSection,
            )
        )

    if structure.identifier == "Zg" and structure.properties.get("d") == Schema.ZigzagCrashingDash:
        errors.append(
            PieError(
                structure.line,
                structure.column,
                path,
                "d={} on a zigzag crashes Radical Pie with an access violation; its dash patterns are 0 to {}".format(
                    Schema.ZigzagCrashingDash, Schema.ZigzagCrashingDash - 1
                ),
                Schema.GeneralDrawingSection,
            )
        )


def CheckShapeAnchors(structure, path, errors):
    """A shape spans two anchors that are opposite corners, so one point twice leaves it no area.

    The Drawing Tools page says the two anchors must differ in both the horizontal and the vertical
    position. Radical Pie renders a shape whose anchors are one point and draws nothing visible
    (measured 2026-09-13: an Rt and an El on one anchor each rendered a path of zero size), which makes
    this the kind of rule only the validator catches. Two anchors that differ in one axis alone are a
    line the writer may have meant, and are left alone.
    """

    for child in structure.children:
        if not (isinstance(child, OpenDdl.Structure) and child.identifier == "X"):
            continue

        lists = {}

        for dataList in child.children:
            if isinstance(dataList, OpenDdl.DataList) and dataList.primitiveType not in lists:
                lists[dataList.primitiveType] = dataList.values

        corners = [lists.get(name) for name in ("ref", "uint32", "int32")]

        if any(values is None or len(values) != 2 for values in corners):
            return  # CheckConnectorArity reports a connector that does not hold two anchors

        if all(values[0] == values[1] for values in corners):
            references, types, indexes = corners

            errors.append(
                PieError(
                    child.line,
                    child.column,
                    Join(path, child),
                    "the two anchors of {} are opposite corners: both name {} {} index {}, "
                    "so the shape has no area".format(
                        Step(structure), references[0], AnchorTypeWord(types[0]), indexes[0]
                    ),
                    Schema.XSection,
                )
            )


class AnchorTarget:
    """A named node as the anchor rules see it, with the two things about its place that matter.

    A group at the file level owns the border, axis, liminal and rail anchors; a structure inside a
    subgroup loses the far row of its own anchors.
    """

    __slots__ = ("node", "isFileLevel", "isNested")

    def __init__(self, node, isFileLevel, isNested):
        self.node = node
        self.isFileLevel = isFileLevel
        self.isNested = isNested


def CollectAnchorTargets(nodes, ancestors, path, targets, errors):
    """Every named node of the file, under the name a connector's ref carries.

    A node is nested when a group that is not itself at the file level encloses it, which is what the
    ancestor chain is read for.

    A name is written once. Radical Pie raises its invalid-data dialog on a file that gives two
    structures the same name, whether or not anything refers to it, while the same file with the second
    name changed renders (measured 2026-09-14), so the second occurrence is reported here and the first
    node keeps the name for the anchor pass.
    """

    for node in nodes:
        if isinstance(node, OpenDdl.DataList):
            continue

        nodePath = Join(path, node)

        if node.name is not None:
            if node.name in targets:
                errors.append(
                    PieError(
                        node.line,
                        node.column,
                        nodePath,
                        "the name {} is given twice; Radical Pie refuses a file that names two structures alike".format(
                            node.name
                        ),
                        Schema.FileSection,
                    )
                )
            else:
                isNested = any(ancestor.identifier == "Gr" for ancestor in ancestors[1:])
                targets[node.name] = AnchorTarget(node, not ancestors, isNested)

        CollectAnchorTargets(node.children, ancestors + (node,), nodePath, targets, errors)


def IsAnnotationGroup(node):
    return node.identifier == "Gr" and node.properties.get("t") == "anno"


def OwnsAnchorType(target, anchorType):
    """Whether the referenced structure owns an anchor type, by the specification's anchor-type table."""

    rule = Schema.AnchorTypeOwners.get(anchorType)

    if rule is None:
        return False

    if rule.topLevelGroup and target.isFileLevel and target.node.identifier == "Gr":
        return True

    if rule.annotationGroup and IsAnnotationGroup(target.node):
        return True

    if target.node.identifier in rule.identifiers:
        return True

    return (
        rule.category is not None
        and Schema.IsCategory(target.node.identifier, rule.category)
        and target.node.identifier not in rule.excluding
    )


def OwnedAnchorTypes(target):
    return tuple(anchorType for anchorType in Schema.AnchorTypeOwners if OwnsAnchorType(target, anchorType))


def MatrixShape(node):
    """A matrix's r and c, or None when either is missing or outside the range CheckProperties covers."""

    rows = node.properties.get("r")
    columns = node.properties.get("c")

    for value in (rows, columns):
        if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 32:
            return None

    return rows, columns


def GroupLineCount(node):
    """How many lines a group holds, which is one per begin structure, the structure that starts a line."""

    return sum(1 for child in node.children if isinstance(child, OpenDdl.Structure) and child.identifier == "Bg")


def AnchorRange(target, anchorType):
    """How many anchors of a type the atlas measured on this structure, and the phrase that places it.

    Returns (None, "") for a matrix whose r or c CheckProperties has already refused, the one case left
    where no count can be named: the atlas measured every anchor type of every drawing structure and of
    the group, and an equation structure owns only type 0 and 'cent'.
    """

    node = target.node

    if target.isFileLevel and node.identifier == "Gr":
        if anchorType == "axis":
            # 'axis' is the type that runs per line, two anchors a line, measured on a one-line and a
            # three-line group (AnchorAtlas.md, 2026-09-12).
            lines = GroupLineCount(node)

            return 2 * lines, " with {}".format(Counted(lines, "line"))

        if IsAnnotationGroup(node) and anchorType in Schema.AnchorCounts["annotationGroup"]:
            return Schema.AnchorCounts["annotationGroup"][anchorType], ""

        return Schema.AnchorCounts["topLevelGroup"].get(anchorType), ""

    if node.identifier == "Mx" and anchorType in Schema.MatrixAnchorTypes:
        shape = MatrixShape(node)

        if shape is None:
            return None, ""

        return Schema.MatrixAnchorCount(anchorType, *shape), " with r={} and c={}".format(*shape)

    if node.identifier in Schema.AnchorCounts and anchorType in Schema.AnchorCounts[node.identifier]:
        return Schema.AnchorCounts[node.identifier][anchorType], ""

    if anchorType in Schema.AnchorCounts["equationStructure"]:
        if target.isNested:
            return Schema.NestedEquationAnchorCount, " inside a subgroup"

        return Schema.AnchorCounts["equationStructure"][anchorType], ""

    return None, ""


def AnchorTypeWord(anchorType):
    return "type 0" if anchorType == 0 else FormatValue(anchorType)


def HoldsGroupOfType(node, groupType):
    return any(
        isinstance(child, OpenDdl.Structure) and child.identifier == "Gr" and child.properties.get("t") == groupType
        for child in node.children
    )


def CheckAnchor(target, reference, anchorType, index, types, indexes, path, errors):
    """One anchor of a connector: a type the structure owns, and an index inside the measured range.

    The types come from the anchor-type table of the "X — Connector Structure" section, with the bond
    family the specification omits. The counts are measured, one render per anchor, in
    Skill/RadicalPie/references/AnchorAtlas.md (2026-09-12): an anchor type a structure does not own and
    an index past the last anchor of a type both crash Radical Pie with an access violation rather than
    raising the invalid-data dialog, so the validator is the only thing that can refuse them.

    A bond anchor type for a direction whose neighbour group the site does not hold crashes the same way
    (Docs/ARCHITECTURE.md, format facts, measured 2026-09-12), which is the third thing checked here.
    """

    if not OwnsAnchorType(target, anchorType):
        owned = OwnedAnchorTypes(target)
        # A modifier, a design structure, an aligner and a phantom carry no anchor at all.
        reason = "it owns {}".format(FormatValues(owned)) if owned else "no anchor type applies to it"

        errors.append(
            PieError(
                types.line,
                types.column,
                path,
                "{} names {}, which has no {} anchor; {}".format(
                    reference, Step(target.node), AnchorTypeWord(anchorType), reason
                ),
                Schema.XSection,
            )
        )
        return

    groupType = Schema.BondAnchorGroupTypes.get(anchorType)

    if groupType is not None and not HoldsGroupOfType(target.node, groupType):
        errors.append(
            PieError(
                types.line,
                types.column,
                path,
                "{} names {}, which holds no group of type {}; its {} anchors box that group".format(
                    reference, Step(target.node), FormatValue(groupType), FormatValue(anchorType)
                ),
                Schema.XSection,
            )
        )
        return

    count, where = AnchorRange(target, anchorType)

    if count is None or 0 <= index < count:
        return

    errors.append(
        PieError(
            indexes.line,
            indexes.column,
            path,
            "{} names {}{}, whose {} anchors are 0 to {}; index {} crashes Radical Pie".format(
                reference, Step(target.node), where, AnchorTypeWord(anchorType), count - 1, index
            ),
            Schema.XSection,
        )
    )


def CheckConnectorAnchors(connector, path, targets, errors):
    """X: every anchor names a node of this file, a type that node owns and an index it has.

    The three lists run in step, one value each per anchor. CheckChildren reports a connector missing a
    list and CheckConnectorArity reports lists of unequal length, so the walk here stops at the shortest.
    """

    lists = {}

    for child in connector.children:
        if isinstance(child, OpenDdl.DataList) and child.primitiveType not in lists:
            lists[child.primitiveType] = child

    references = lists.get("ref")
    types = lists.get("uint32")
    indexes = lists.get("int32")

    if references is None or types is None or indexes is None:
        return

    for at in range(min(len(references.values), len(types.values), len(indexes.values))):
        reference = references.values[at]
        target = targets.get(reference)

        if target is None:
            errors.append(
                PieError(
                    references.line,
                    references.column,
                    path,
                    "{} names no node of this file; an anchor belongs to a named structure".format(
                        "null" if reference is None else reference
                    ),
                    Schema.XSection,
                )
            )
            continue

        CheckAnchor(target, reference, types.values[at], indexes.values[at], types, indexes, path, errors)


def CheckAnchors(nodes, path, targets, errors):
    for node in nodes:
        if isinstance(node, OpenDdl.DataList):
            continue

        nodePath = Join(path, node)

        if node.identifier == "X":
            CheckConnectorAnchors(node, nodePath, targets, errors)

        CheckAnchors(node.children, nodePath, targets, errors)


def CheckStructure(node, path, errors):
    if isinstance(node, OpenDdl.DataList):
        return

    rule = Schema.Structures.get(node.identifier)
    path = Join(path, node)

    if rule is None:
        errors.append(
            PieError(node.line, node.column, path, "unknown structure {!r}".format(node.identifier), Schema.FileSection)
        )
        return

    CheckProperties(node, rule, path, errors)
    CheckChildren(node, rule, path, errors)
    CheckGroupTypes(node, rule, path, errors)

    if node.identifier == "Ar":
        CheckArrowArrays(node, path, errors)

    if node.identifier == "Mx":
        CheckMatrixEntries(node, path, errors)

    if node.identifier == "Bd":
        CheckBondArrays(node, path, errors)

    if node.identifier == "Gr":
        CheckGroupConnector(node, path, errors)

    if node.identifier == "Br":
        CheckBracketContent(node, path, errors)

    if node.identifier == "V":
        CheckDesignParameter(node, path, errors)

    # A style map reads the font slots of the design around it, which is why D and not M dispatches it.
    if node.identifier == "D":
        CheckDesignFonts(node, path, errors)

    if node.identifier in Schema.ShapeStructures:
        CheckShapeAnchors(node, path, errors)

    CheckDrawingProperties(node, path, errors)
    CheckConnectorArity(node, path, errors)

    for child in node.children:
        CheckStructure(child, path, errors)


def SectionOf(node, seenMain, seenAnnotation):
    """Which of the five file-level sections a top-level node belongs to, or None when it belongs to none."""

    if isinstance(node, OpenDdl.DataList):
        return None

    if node.identifier == "D":
        return 0

    if Schema.IsCategory(node.identifier, "drawing"):
        return 4 if seenMain or seenAnnotation else 1

    if node.identifier == "Gr":
        return 3 if node.properties.get("t") == "anno" else 2

    return None


def CheckFileSections(nodes, errors):
    """The five sections of a .pie file occur in the order the specification lists them."""

    highest = 0
    seenDesign = False
    seenMain = False
    seenAnnotation = False

    for node in nodes:
        section = SectionOf(node, seenMain, seenAnnotation)
        path = Join("", node)

        if section is None:
            errors.append(
                PieError(
                    node.line,
                    node.column,
                    path,
                    "{} may not appear at the file level".format(Step(node)),
                    Schema.FileSection,
                )
            )
            continue

        if section < highest:
            errors.append(
                PieError(
                    node.line,
                    node.column,
                    path,
                    "the {} section must precede the {} section".format(
                        Schema.SectionNames[section], Schema.SectionNames[highest]
                    ),
                    Schema.FileSection,
                )
            )
        else:
            highest = section

        # The group type table gives every type but 0 and 'anno' to a subgroup of some structure.
        if node.identifier == "Gr" and node.properties.get("t", 0) not in (0, "anno"):
            errors.append(
                PieError(
                    node.line,
                    node.column,
                    path,
                    "a group at the file level is the main equation group or a group of type 'anno'",
                    Schema.GrSection,
                )
            )

        # File Format Specification: the design section is one section. Every one of the 184 designs
        # in the corpus is a single D at the head of its equation (corpus census 2026-09-10).
        if section == 0:
            if seenDesign:
                errors.append(
                    PieError(
                        node.line,
                        node.column,
                        path,
                        "a file holds one design section",
                        Schema.FileSection,
                    )
                )

            seenDesign = True

        if section == 2:
            if seenMain:
                errors.append(
                    PieError(
                        node.line,
                        node.column,
                        path,
                        "a file holds one main equation group",
                        Schema.FileSection,
                    )
                )

            seenMain = True

        if section == 3:
            seenAnnotation = True

    if not seenMain:
        errors.append(PieError(1, 1, "", "a file needs a main equation group", Schema.FileSection))


# The sequences that end the XML comment the SVG carrier holds an equation in. Measured 2026-09-14 through
# `python -m Tools.Render svg`: a symbol text holding `-->` is refused by Radical Pie itself, which raised
# the "does not contain valid Radical Pie equation data" dialog on both attempts, and one holding `--!>`
# renders (32.9106 by 9 points) but ends the comment for an HTML parser, which reads the rest of the
# equation as markup. A text holding a bare `--` travels and renders (23.2085 by 9 points) and is left alone.
CommentEnders = ("-->", "--!>")


def CheckCarrierComment(text, errors):
    """Nothing in an equation may end the XML comment that carries it to Radical Pie or to Inkscape."""

    for ender in CommentEnders:
        start = text.find(ender)

        while start >= 0:
            lineStart = text.rfind("\n", 0, start) + 1
            errors.append(
                PieError(
                    text.count("\n", 0, start) + 1,
                    start - lineStart + 1,
                    "",
                    "this text holds {!r}, which ends an XML comment; the SVG carrier holds the equation"
                    " in a comment and cannot carry it".format(ender),
                    Schema.CarrierSection,
                )
            )
            start = text.find(ender, start + 1)


def Validate(text):
    """Validate .pie text. Returns the list of PieError, empty when the text satisfies every rule.

    A file nested deeper than the interpreter's stack allows is one violation and not a RecursionError
    traceback, which is what a couple of thousand nested groups used to cost the caller.
    """

    try:
        return Violations(text)
    except RecursionError:
        return [
            PieError(
                1,
                1,
                "",
                "this equation nests structures deeper than the validator reads",
                Schema.FileSection,
            )
        ]


def Violations(text):
    """Every violation of the parsed text, in line order."""

    try:
        nodes = OpenDdl.Parse(text)
    except OpenDdl.PieSyntaxError as error:
        return [PieError(error.line, error.column, "", "syntax error: " + error.message, Schema.FileSection)]

    errors = []
    CheckCarrierComment(text, errors)
    CheckFileSections(nodes, errors)

    for node in nodes:
        CheckStructure(node, "", errors)

    targets = {}
    CollectAnchorTargets(nodes, (), "", targets, errors)
    CheckAnchors(nodes, "", targets, errors)

    errors.sort(key=lambda error: (error.line, error.column))
    return errors


# The comment content opens with the header line or with the design or main group structure itself.
PieCommentPattern = re.compile(r"<!--(\s*(?://\s*Radical Pie Equation|D|Gr)(?![A-Za-z0-9_]).*?)-->", re.DOTALL)

InkRadixPattern = re.compile(r"<inkradix:datav1[^>]*>(.*?)</inkradix:datav1>", re.DOTALL)

XmlEntities = (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'"), ("&amp;", "&"))


def Unescape(text):
    for entity, character in XmlEntities:
        text = text.replace(entity, character)

    return text


def ExtractAllPieFromSvg(svgText):
    """Every equation an SVG carries, as .pie text, in document order.

    Radical Pie writes each equation as an XML comment right after the <desc> element; InkRadix writes
    it into an <inkradix:datav1> element, XML-escaped. A drawing composed of several Radical Pie
    objects carries one such carrier for each of them, in Corpus/Svg/comp.svg three of them.
    """

    carriers = [(match.start(), match.group(1).strip("\r\n")) for match in PieCommentPattern.finditer(svgText)]

    carriers += [(match.start(), Unescape(match.group(1))) for match in InkRadixPattern.finditer(svgText)]

    carriers.sort(key=lambda carrier: carrier[0])

    return [text for _, text in carriers]


def ExtractPieFromSvg(svgText):
    """The first equation an SVG carries, as .pie text, or the empty string when it carries none."""

    equations = ExtractAllPieFromSvg(svgText)

    return equations[0] if equations else ""


def PrefixPath(index, error):
    """The same error with its path prefixed by the index of the equation it came from."""

    path = "#{}".format(index) if not error.path else "#{}/{}".format(index, error.path)

    return PieError(error.line, error.column, path, error.message, error.section)


def ViolationLine(name, error):
    """One violation as every command line of this repository prints it."""

    return "{}:{}:{} {}: {} [{}]".format(name, error.line, error.column, error.path, error.message, error.section)


def FirstViolation(text):
    """The first violation of one equation's text as one line, or the empty string when the text validates.

    What the library entry points of the pipelines refuse with, where the caller handed over text rather than a
    file name: `Tools.Word.Docx.EmbedEquations`, `Tools.PowerPoint.Pptx.EmbedEquations`,
    `Tools.Latex.Build.BuildDocument` and `Tools.Render.Export.Export` each name the key or the file and add
    this. The command lines print every violation of every file through `RefusalMessage` before they get there.
    """

    errors = Validate(text)

    if not errors:
        return ""

    error = errors[0]

    return "{}:{} {}: {} [{}]".format(error.line, error.column, error.path, error.message, error.section)


def RefusalMessage(fileNames):
    """Why a pipeline refuses the equations it was given, or the empty string when every one validates.

    Radical Pie drops a structure it does not know instead of refusing the file, so an equation with one
    typo in a structure name renders as the empty equation, 5.5 by 8 points, and every pipeline reported
    success. Each pipeline's command line runs this over its .pie files before it launches anything, and
    what it prints is the validator's own lines.
    """

    lines = []

    for name in fileNames:
        lines += [ViolationLine(name, error) for error in ValidateFile(name)]

    if not lines:
        return ""

    return "\n".join(["these equations do not validate, so nothing was started:"] + lines)


def ValidateFile(path):
    """Validate a .pie file, or every equation embedded in a .svg file."""

    path = Path(path)
    data = path.read_bytes()

    if data.startswith(codecs.BOM_UTF8):
        return [
            PieError(
                1,
                1,
                "",
                "this file starts with a UTF-8 byte order mark; write it without one",
                Schema.FileSection,
            )
        ]

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        return [PieError(1, 1, "", "this file is not UTF-8 text: {}".format(error.reason), Schema.FileSection)]

    if path.suffix.lower() != ".svg":
        return Validate(text)

    equations = ExtractAllPieFromSvg(text)

    if not equations:
        return [PieError(1, 1, "", "this SVG carries no Radical Pie equation", Schema.FileSection)]

    if len(equations) == 1:
        return Validate(equations[0])

    errors = []

    for index, equation in enumerate(equations, start=1):
        errors += [PrefixPath(index, error) for error in Validate(equation)]

    return errors

"""Tokenizer and parser for the OpenDDL text that Radical Pie writes into .pie files.

The grammar is OpenDDL version 3.0, published at openddl.org; section 10 Formal Grammar gives

    property  ::= identifier ("=" literal)?
    structure ::= data-type (name? "{" data-list? "}" | "[" integer-literal "]" "*"? name? "{" data-array-list? "}")
                | identifier name? ("(" (property ("," property)*)? ")")? "{" structure* "}"

Version 3.0 admits 0 and 1 as bool literals and assigns true to a bool property whose value is
omitted, which is how Radical Pie writes a set flag: `Sp (t) {}` in Corpus/Pie/StyleTestNewCMMath.pie
and `Mx (r=3,c=1,mb)` in Corpus/Pie/eq.pie.

The parser produces Structure and DataList nodes and enforces the grammar only. Every rule about
which structure may hold which child, and which property may take which value, lives in Schema.py.
A property value written as a single-quoted literal is a CharLiteral, because Radical Pie writes a
uint32 property value that way and a string literal is not accepted in its place.

Two grammar forms are refused with a syntax error because no Radical Pie file writes them: the data
state form of a subarray (`float[2]* {...}`) and base64 data lists.
"""


class PieSyntaxError(Exception):
    """A place in the text where the OpenDDL grammar is broken, with its line and column."""

    def __init__(self, message, line, column):
        super().__init__("{}:{}: {}".format(line, column, message))

        self.message = message
        self.line = line
        self.column = column


# Long and short spellings of every OpenDDL data type, mapped to the spelling FileFormat.md uses.
DataTypeSpellings = {
    "bool": "bool",
    "b": "bool",
    "int8": "int8",
    "i8": "int8",
    "int16": "int16",
    "i16": "int16",
    "int32": "int32",
    "i32": "int32",
    "int64": "int64",
    "i64": "int64",
    "uint8": "uint8",
    "u8": "uint8",
    "uint16": "uint16",
    "u16": "uint16",
    "uint32": "uint32",
    "u32": "uint32",
    "uint64": "uint64",
    "u64": "uint64",
    "half": "half",
    "h": "half",
    "float16": "half",
    "f16": "half",
    "float": "float",
    "f": "float",
    "float32": "float",
    "f32": "float",
    "double": "double",
    "d": "double",
    "float64": "double",
    "f64": "double",
    "string": "string",
    "s": "string",
    "ref": "ref",
    "r": "ref",
    "type": "type",
    "t": "type",
    "base64": "base64",
    "z": "base64",
}

IntegerTypes = frozenset(["int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64"])

FloatTypes = frozenset(["half", "float", "double"])

EscapeCharacters = {
    '"': '"',
    "'": "'",
    "?": "?",
    "\\": "\\",
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
}

PunctuationCharacters = "{}()[],=*"

# The grammar spells its identifier and digit classes out, so this lexer does not use str.isalnum.
DigitCharacters = "0123456789"

IdentifierStartCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"

IdentifierCharacters = IdentifierStartCharacters + DigitCharacters

LiteralKindNames = {
    "int": "an integer literal",
    "float": "a floating-point literal",
    "string": "a string literal",
    "bool": "a bool literal",
    "char": "a character literal",
    "name": "a reference",
    "null": "null",
    "identifier": "an identifier",
    "punct": "punctuation",
    "end": "the end of the text",
}


class CharLiteral(str):
    """The text of a single-quoted literal held as a property value, `'math'` and not `"math"`.

    It compares equal to its text, so a rule in Schema.py enumerates plain strings and a path in
    Validator.py prints the same value; the type is what tells the property check which literal the
    text carried.
    """


class Token:
    __slots__ = ("kind", "value", "line", "column")

    def __init__(self, kind, value, line, column):
        self.kind = kind
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return "Token({!r}, {!r}, {}, {})".format(self.kind, self.value, self.line, self.column)


class Structure:
    """One `Identifier $name (properties) { children }` node."""

    __slots__ = ("identifier", "name", "properties", "children", "line", "column")

    def __init__(self, identifier, name, properties, children, line, column):
        self.identifier = identifier
        self.name = name

        # Insertion-ordered, which in Python 3.7 and later is what a plain dict guarantees.
        self.properties = properties

        self.children = children
        self.line = line
        self.column = column

    def __repr__(self):
        return "Structure({!r}, line={})".format(self.identifier, self.line)


class DataList:
    """One primitive data list, `u32{1,2}` or the subarray form `u32[2]{{1,2},{3,4}}`."""

    __slots__ = ("primitiveType", "subarraySize", "values", "line", "column")

    def __init__(self, primitiveType, subarraySize, values, line, column):
        self.primitiveType = primitiveType
        self.subarraySize = subarraySize

        # A flat list of values, or a list of subarrays when subarraySize is set.
        self.values = values

        self.line = line
        self.column = column

    def __repr__(self):
        return "DataList({!r}, {} values, line={})".format(self.primitiveType, len(self.values), self.line)


def Tokenize(text):
    """Split OpenDDL text into tokens, dropping whitespace and both comment forms."""

    tokens = []
    index = 0
    length = len(text)
    line = 1

    # Index of the character before the first one on the current line, so column is index - lineStart.
    lineStart = -1

    while index < length:
        character = text[index]

        if character in " \t\r":
            index += 1
            continue

        if character == "\n":
            index += 1
            line += 1
            lineStart = index - 1
            continue

        column = index - lineStart

        if text.startswith("//", index):
            end = text.find("\n", index)
            index = length if end < 0 else end
            continue

        if text.startswith("/*", index):
            end = text.find("*/", index + 2)

            if end < 0:
                raise PieSyntaxError("unterminated /* comment", line, column)

            for skipped in range(index, end):
                if text[skipped] == "\n":
                    line += 1
                    lineStart = skipped

            index = end + 2
            continue

        if character == '"':
            value = ""

            # The joined literal is reported where it starts, and the lines it spans are counted.
            startLine = line

            # Adjacent string literals are one literal, per the string-literal grammar rule.
            while True:
                piece, index, line, lineStart = ReadString(text, index, line, lineStart, column)
                value += piece
                probe, probeLine, probeLineStart = SkipToLiteral(text, index, line, lineStart)

                if probe < length and text[probe] == '"':
                    index = probe
                    line = probeLine
                    lineStart = probeLineStart
                    continue

                break

            tokens.append(Token("string", value, startLine, column))
            continue

        if character == "'":
            value, index = ReadCharacterLiteral(text, index, line, column)
            tokens.append(Token("char", value, line, column))
            continue

        if character in "$%":
            end = index + 1

            while end < length and (text[end] in IdentifierCharacters or text[end] == "%"):
                end += 1

            if end == index + 1:
                raise PieSyntaxError("a name needs an identifier after {}".format(character), line, column)

            tokens.append(Token("name", text[index:end], line, column))
            index = end
            continue

        if character in DigitCharacters or (character in "+-." and Follows(text, index + 1)):
            kind, value, index = ReadNumber(text, index, line, column)
            tokens.append(Token(kind, value, line, column))
            continue

        if character in IdentifierStartCharacters:
            end = index + 1

            while end < length and text[end] in IdentifierCharacters:
                end += 1

            word = text[index:end]
            index = end

            if word in ("true", "false"):
                tokens.append(Token("bool", word == "true", line, column))
            elif word == "null":
                tokens.append(Token("null", None, line, column))
            else:
                tokens.append(Token("identifier", word, line, column))

            continue

        if character in PunctuationCharacters:
            tokens.append(Token("punct", character, line, column))
            index += 1
            continue

        raise PieSyntaxError("unexpected character {!r}".format(character), line, column)

    tokens.append(Token("end", None, line, length - lineStart))
    return tokens


def Follows(text, index):
    """Whether a sign or a period at index - 1 begins a number."""

    if index >= len(text):
        return False

    if text[index] in DigitCharacters:
        return True

    return text[index] == "." and index + 1 < len(text) and text[index + 1] in DigitCharacters


def SkipToLiteral(text, index, line, lineStart):
    """Advance past whitespace and comments, used to find a string literal continuation.

    Returns the next index, the line and the line start, so a literal joined across lines leaves the
    position of every following token intact.
    """

    length = len(text)

    while index < length:
        if text[index] == "\n":
            index += 1
            line += 1
            lineStart = index - 1
        elif text[index] in " \t\r":
            index += 1
        elif text.startswith("//", index):
            end = text.find("\n", index)
            index = length if end < 0 else end
        elif text.startswith("/*", index):
            end = text.find("*/", index + 2)

            if end < 0:
                return length, line, lineStart

            for skipped in range(index, end):
                if text[skipped] == "\n":
                    line += 1
                    lineStart = skipped

            index = end + 2
        else:
            break

    return index, line, lineStart


def ReadEscape(text, index, line, column):
    """Decode one escape sequence, index pointing at the backslash. Returns the text and the next index."""

    if index + 1 >= len(text):
        raise PieSyntaxError("unterminated escape sequence", line, column)

    character = text[index + 1]

    if character in EscapeCharacters:
        return EscapeCharacters[character], index + 2

    digits = {"x": 2, "u": 4, "U": 6}.get(character)

    if digits is None:
        raise PieSyntaxError("unknown escape sequence \\{}".format(character), line, column)

    body = text[index + 2 : index + 2 + digits]

    if len(body) < digits or any(character not in "0123456789abcdefABCDEF" for character in body):
        raise PieSyntaxError("\\{} needs {} hexadecimal digits".format(character, digits), line, column)

    return chr(int(body, 16)), index + 2 + digits


def ReadString(text, index, line, lineStart, column):
    """Read one double-quoted literal. Returns its text, the next index, the line and the line start."""

    index += 1
    length = len(text)
    pieces = []

    while True:
        if index >= length:
            raise PieSyntaxError("unterminated string literal", line, column)

        character = text[index]

        if character == '"':
            return "".join(pieces), index + 1, line, lineStart

        if character == "\\":
            piece, index = ReadEscape(text, index, line, column)
            pieces.append(piece)
            continue

        if character == "\n":
            raise PieSyntaxError("a string literal may not span lines", line, column)

        pieces.append(character)
        index += 1


def ReadCharacterLiteral(text, index, line, column):
    """Read one single-quoted literal such as 'vert', kept as text rather than packed into an integer."""

    index += 1
    length = len(text)
    pieces = []

    while True:
        if index >= length or text[index] == "\n":
            raise PieSyntaxError("unterminated character literal", line, column)

        character = text[index]

        if character == "'":
            if not pieces:
                raise PieSyntaxError("empty character literal", line, column)

            return "".join(pieces), index + 1

        if character == "\\":
            piece, index = ReadEscape(text, index, line, column)
            pieces.append(piece)
            continue

        pieces.append(character)
        index += 1


def ReadNumber(text, index, line, column):
    """Read one integer or floating-point literal. Returns the token kind, the value and the next index."""

    length = len(text)
    start = index

    if text[index] in "+-":
        index += 1

    sign = -1 if text[start] == "-" else 1

    prefix = text[index : index + 2].lower()

    if prefix in ("0x", "0o", "0b"):
        base = {"0x": 16, "0o": 8, "0b": 2}[prefix]
        digits = {16: "0123456789abcdef", 8: "01234567", 2: "01"}[base]
        index += 2
        body = ""

        while index < length and (text[index].lower() in digits or text[index] == "_"):
            if text[index] != "_":
                body += text[index]

            index += 1

        if not body:
            raise PieSyntaxError("{} literal with no digits".format(prefix), line, column)

        return "int", sign * int(body, base), index

    body = ""
    isFloat = False

    while index < length and (text[index] in DigitCharacters or text[index] == "_"):
        if text[index] != "_":
            body += text[index]

        index += 1

    if index < length and text[index] == ".":
        isFloat = True
        body += "."
        index += 1

        while index < length and (text[index] in DigitCharacters or text[index] == "_"):
            if text[index] != "_":
                body += text[index]

            index += 1

    if index < length and text[index] in "eE":
        isFloat = True
        body += "e"
        index += 1

        if index < length and text[index] in "+-":
            body += text[index]
            index += 1

        exponent = ""

        while index < length and (text[index] in DigitCharacters or text[index] == "_"):
            if text[index] != "_":
                exponent += text[index]

            index += 1

        if not exponent:
            raise PieSyntaxError("exponent with no digits", line, column)

        body += exponent

    if not body or body == ".":
        raise PieSyntaxError("malformed number", line, column)

    if isFloat:
        return "float", sign * float(body), index

    return "int", sign * int(body), index


class Parser:
    """Recursive descent over the token list, producing Structure and DataList nodes."""

    def __init__(self, text):
        self.tokens = Tokenize(text)
        self.index = 0

    def Peek(self):
        return self.tokens[self.index]

    def Take(self):
        token = self.tokens[self.index]

        if token.kind != "end":
            self.index += 1

        return token

    def TakePunctuation(self, character):
        token = self.Peek()

        if token.kind != "punct" or token.value != character:
            raise PieSyntaxError(
                "expected {!r}, found {}".format(character, self.Describe(token)), token.line, token.column
            )

        return self.Take()

    def AtPunctuation(self, character):
        token = self.Peek()
        return token.kind == "punct" and token.value == character

    def Describe(self, token):
        if token.kind == "punct":
            return "{!r}".format(token.value)

        if token.kind == "identifier":
            return "the identifier {!r}".format(token.value)

        return LiteralKindNames[token.kind]

    def ParseFile(self):
        nodes = []

        while self.Peek().kind != "end":
            nodes.append(self.ParseNode())

        return nodes

    def ParseNode(self):
        token = self.Take()

        if token.kind != "identifier":
            raise PieSyntaxError(
                "expected a structure, found {}".format(self.Describe(token)), token.line, token.column
            )

        if token.value in DataTypeSpellings:
            return self.ParseDataListNode(token)

        return self.ParseStructure(token)

    def ParseDataListNode(self, token):
        primitiveType = DataTypeSpellings[token.value]

        if primitiveType == "base64":
            raise PieSyntaxError("base64 data lists are not supported", token.line, token.column)

        subarraySize = None

        if self.AtPunctuation("["):
            self.Take()
            sizeToken = self.Take()

            if sizeToken.kind != "int" or sizeToken.value < 1:
                raise PieSyntaxError("a subarray size must be a positive integer", sizeToken.line, sizeToken.column)

            subarraySize = sizeToken.value
            self.TakePunctuation("]")

        if self.AtPunctuation("*"):
            star = self.Take()
            raise PieSyntaxError("data states are not supported", star.line, star.column)

        if self.Peek().kind == "name":
            self.Take()

        self.TakePunctuation("{")

        if subarraySize is None:
            values = self.ParseValues(primitiveType, "}")
        else:
            values = []

            while not self.AtPunctuation("}"):
                self.TakePunctuation("{")
                subarray = self.ParseValues(primitiveType, "}")
                closing = self.TakePunctuation("}")

                if len(subarray) != subarraySize:
                    raise PieSyntaxError(
                        "a subarray of {} needs {} values, found {}".format(primitiveType, subarraySize, len(subarray)),
                        closing.line,
                        closing.column,
                    )

                values.append(subarray)

                if self.AtPunctuation(","):
                    self.Take()

        self.TakePunctuation("}")
        return DataList(primitiveType, subarraySize, values, token.line, token.column)

    def ParseValues(self, primitiveType, terminator):
        values = []

        while not self.AtPunctuation(terminator):
            values.append(self.ParseLiteral(primitiveType))

            if self.AtPunctuation(","):
                self.Take()
                continue

            break

        return values

    def ParseLiteral(self, primitiveType):
        token = self.Take()

        if primitiveType == "bool":
            if token.kind == "bool":
                return token.value

            if token.kind == "int" and token.value in (0, 1):
                return token.value == 1

        elif primitiveType in IntegerTypes:
            if token.kind == "int":
                return token.value

            if token.kind == "char":
                return token.value

        elif primitiveType in FloatTypes:
            if token.kind == "float":
                return token.value

            if token.kind == "int":
                return float(token.value)

        elif primitiveType == "string":
            if token.kind == "string":
                return token.value

        elif primitiveType == "ref":
            if token.kind == "name":
                return token.value

            if token.kind == "null":
                return None

        elif primitiveType == "type":
            if token.kind == "identifier" and token.value in DataTypeSpellings:
                return DataTypeSpellings[token.value]

        raise PieSyntaxError(
            "expected a {} value, found {}".format(primitiveType, self.Describe(token)), token.line, token.column
        )

    def ParseStructure(self, token):
        name = None

        if self.Peek().kind == "name":
            name = self.Take().value

        properties = {}

        if self.AtPunctuation("("):
            self.Take()

            while not self.AtPunctuation(")"):
                nameToken = self.Take()

                if nameToken.kind != "identifier":
                    raise PieSyntaxError(
                        "expected a property name, found {}".format(self.Describe(nameToken)),
                        nameToken.line,
                        nameToken.column,
                    )

                if nameToken.value in properties:
                    raise PieSyntaxError(
                        "property {!r} is given twice".format(nameToken.value), nameToken.line, nameToken.column
                    )

                if self.AtPunctuation("="):
                    self.Take()
                    properties[nameToken.value] = self.ParsePropertyValue()
                else:
                    # OpenDDL 3.0: a property with no value is true, and Radical Pie relies on it.
                    properties[nameToken.value] = True

                if self.AtPunctuation(","):
                    self.Take()

            self.TakePunctuation(")")

        self.TakePunctuation("{")
        children = []

        while not self.AtPunctuation("}"):
            if self.Peek().kind == "end":
                raise PieSyntaxError("{} is never closed".format(token.value), self.Peek().line, self.Peek().column)

            children.append(self.ParseNode())

        self.TakePunctuation("}")
        return Structure(token.value, name, properties, children, token.line, token.column)

    def ParsePropertyValue(self):
        token = self.Take()

        if token.kind == "char":
            return CharLiteral(token.value)

        if token.kind in ("bool", "int", "float", "string", "name"):
            return token.value

        if token.kind == "null":
            return None

        if token.kind == "identifier" and token.value in DataTypeSpellings:
            return DataTypeSpellings[token.value]

        raise PieSyntaxError(
            "expected a property value, found {}".format(self.Describe(token)), token.line, token.column
        )


def Parse(text):
    """Parse a whole .pie text into the list of its top-level nodes. Raises PieSyntaxError."""

    return Parser(text).ParseFile()

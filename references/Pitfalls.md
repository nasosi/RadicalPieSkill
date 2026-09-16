# Pitfalls

The mistakes that produce a file Radical Pie rejects, crashes on, or renders wrongly without saying so,
and the shape of the messages the validator prints. Read it before handing over a file, and whenever a
validator message or a rendering is not what you expected.

The hints for one domain each: `references/ChemistryHints.md`; `references/AnnotationHints.md` for
annotations, arrows, drawings and rails; `references/LayoutHints.md` for alignment, spacing, brackets,
scripts, matrices and designs; `references/DocumentHints.md` for Word, PowerPoint, LaTeX and SVG output.

Write UTF-8 without a BOM, and keep the header line `// Radical Pie Equation`, as Radical Pie does. A
file the program cannot parse raises a modal dialog saying the file does not contain valid Radical Pie
equation data, so validate before handing a file over.

A file-writing tool can drop a private use character on the way to the disk, and the twelve bond
characters U+EE30 to U+EE3B are in that range: one agent's editing tool wrote U+EE30 away and left
`Sb (ro='bond') {s{""}}` behind, which renders as nothing and is caught by one rule alone, the
validator's "the text of a symbol must not be the empty string". Write any string holding a character
in U+E000 to U+F8FF with Python, and validate the file afterwards.

A symbol's text is a data list, not a property: `Sb {s{"x"}}`, never `Sb (s="x")`. The same goes for a
bracket's characters, `u32{0x28,0x29}`, an iteration's or integral's character, and a mark's or prime's
character.

A text symbol may not hold `-->` or `--!>`: the equation travels to Radical Pie and to Inkscape inside an
XML comment, the SVG carrier, and either sequence ends that comment early. The validator refuses both.

A four-character literal in single quotes is a number, and it must be exactly four characters:
`'vert'`, `'mddl'`, `'sing'`. The validator checks a property value against the specification's list
of allowed values, and inside a data list it checks a connector's anchor types and indexes, an
arrow's arrow types and charms, a bond's group types, bond types and angle types, a design
parameter's name and value, a style map's first font index, every value against the range of its
primitive type, and every character value against the last code point. Copy the four-character
literals from the catalogue.

`It` is for the n-ary symbols alone: the sum, the product, the integral, the big wedge and vee, the
union and the intersection. An ordinary operator with a limit tucked under it is a stack, `St { Gr { Bg
{} Sb (ro='oper') {s{"⩓"}} } Gr (t='lowr') { Bg {} Sb {s{"k"}} } }`, which keeps the operator at its
own size; the same character inside an `It` is drawn at summation size. "Large", "big" or "drawn large"
in a request describes the glyph the author pictures, not the structure, so pick the character the
request names and leave it at operator size unless the request is for an operator over an index set.

Every group starts with `Bg {}`, including every subgroup. No file Radical Pie writes nests a group of
type 0 directly inside another group, so reach for the structure that owns the subgroup you want rather
than a bare group.

Use the mathematical characters, not the typewriter ones: U+2212 for a minus sign, U+00B7 for a centred
dot, U+2026 and U+22EF for ellipses. `references/TexSymbols.md` gives the value for each TeX name. A prime
is not a typed character: it is the `Pr` structure written after the symbol it marks, `Pr {}`, and U+2032,
a single prime, is what the structure draws by default (`references/catalogue/Symbols.md`, `Pr`). Radical
Pie 1.15's own editor writes U+00B7 for a centred dot; files from earlier versions carry U+22C5 instead,
and the editor draws both with the same glyph, so either validates and renders the same.

`\mathbb{1}` and any double-struck letter or digit outside ℕℤℚℝℂ needs its own Mathematical
Alphanumeric code point written with `st='doub'`, since that same code point with `st='uprt'` renders
plain rather than double-struck.

Validator messages have a fixed shape, and the useful part is the path and the section. The
bracketed section names the part of Radical Pie's own format specification the rule comes from; that
document does not ship with the skill, and the structure's entry in
`references/catalogue/` covers the same ground.

```
MyEquation.pie:10:2 Gr/Fr: Fr needs 1 group of type 'dnom', found 0 [Fr — Fraction Structure]
MyEquation.pie:20:3 Gr/Sc/Gr(t='sups'): the first substructure of Gr must be Bg, found Sb [Gr — Group Structure]
```

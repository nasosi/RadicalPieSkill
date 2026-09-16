# Structure Catalogue

Every structure the Radical Pie file format defines, with its properties, its subgroups and a minimal
example that the validator accepts. Derived from the documentation's file format reference and from
the rules the validator encodes in its own schema. Where a rule in this catalogue is looser than the
specification, a note says which fixture written by Radical Pie proves the looser rule; the file the
program writes wins over the document.

Run every example past the validator before trusting a variation on it:

```
python scripts/Validate.py <file>
```

## Contents

| Structure | Category | Purpose |
| --- | --- | --- |
| [Al](Groups.md#al--aligner) | equation | Aligns the same column across the lines of a group. |
| [Ar](Arrows.md#ar--arrow) | equation | A big stretching arrow with charms and labels. |
| [Bd](Bonds.md#bd--bond) | equation | A chemical bond site with up to six neighbours. |
| [Bg](Symbols.md#bg--begin) | equation | Begins a line; the first child of every group. |
| [Br](Brackets.md#br--bracket) | equation | A bracket pair around one or more groups. |
| [Bx](Brackets.md#bx--box) | equation | A box around a group. |
| [Cn](Drawings.md#cn--corner) | drawing | A corner drawing object. |
| [D](Design.md#d--design) | design | The design block: values, fonts, style maps, palette. |
| [Dv](Fractions.md#dv--division) | equation | A long division. |
| [El](Drawings.md#el--ellipse) | drawing | An ellipse drawing object. |
| [En](Brackets.md#en--enclose) | modifier | An enclosure around one symbol. |
| [F](Design.md#f--font) | design | One font of a design. |
| [Fr](Fractions.md#fr--fraction) | equation | A fraction, vertical, horizontal or diagonal. |
| [Gr](Groups.md#gr--group) | equation | A group: the main equation, and every typed subgroup. |
| [In](Operators.md#in--integral) | equation | An integral with optional limits. |
| [It](Operators.md#it--iteration) | equation | A sum, product or other iterated operator. |
| [Jo](Drawings.md#jo--joist) | drawing | A brace or bracket drawing object. |
| [Kt](Brackets.md#kt--strike) | equation | A strike through a group. |
| [Ln](Drawings.md#ln--line) | drawing | A line drawing object. |
| [M](Design.md#m--map) | design | Maps one symbol style to fonts. |
| [Mk](Symbols.md#mk--mark) | modifier | An accent on one symbol. |
| [Mx](Matrices.md#mx--matrix) | equation | A matrix of entry groups. |
| [Ng](Symbols.md#ng--negate) | modifier | A negation stroke through one symbol. |
| [P](Design.md#p--palette) | design | The sixteen palette colours of a design. |
| [Ph](Groups.md#ph--phantom) | equation | Space held without ink. |
| [Pr](Symbols.md#pr--prime) | equation | Prime marks on the preceding structure. |
| [Qe](Drawings.md#qe--quarter-ellipse) | drawing | A quarter ellipse drawing object. |
| [Rd](Fractions.md#rd--radical) | equation | A radical with an optional degree. |
| [Rr](Drawings.md#rr--rounded-rectangle) | drawing | A rounded rectangle drawing object. |
| [Rt](Drawings.md#rt--rectangle) | drawing | A rectangle drawing object. |
| [Sb](Symbols.md#sb--symbol) | equation | One or more characters with one role and one style. |
| [Sc](Symbols.md#sc--script) | equation | A subscript, a superscript, or both. |
| [Sl](Symbols.md#sl--slash) | modifier | A slash through one symbol. |
| [Sp](Symbols.md#sp--space) | equation | A space, a kern, or a tab stop. |
| [St](Groups.md#st--stack) | equation | An expression with a small label above or below. |
| [V](Design.md#v--value) | design | One design parameter. |
| [Wm](Arrows.md#wm--widemark) | equation | A stretching mark over or under a group. |
| [X](Annotations.md#x--connector) | connector | Attaches a drawing or annotation to an anchor. |
| [Zg](Drawings.md#zg--zigzag) | drawing | A zigzag drawing object. |

## How a file is put together

A `.pie` file is OpenDDL text. It opens with the line `// Radical Pie Equation` and holds up to five
sections, which must appear in this order:

1. the design block `D`,
2. drawing structures for the background layer,
3. the main equation group `Gr`,
4. annotation groups `Gr (t='anno')`,
5. drawing structures for the foreground layer.

Only the main equation group is required. The smallest file Radical Pie accepts is `D{} Gr { Bg {} }`.
A generated equation carries an empty `D {}` unless the caller supplies a design, and it then renders at
Radical Pie's factory design wherever it is opened.

Structure syntax is `Identifier (property=value, flag) { children }`. A property written with no value
is true, which is how Radical Pie writes a set flag: `Fr (at)`, `Mx (r=3,c=1,mb)`. A `uint32` property
takes either a number, decimal or `0x` hexadecimal, or a four-character literal in single quotes such
as `'vert'`. Children are further structures and data lists. A data list is written
`type{value, ...}`: `s{"text"}` for a string, `u32{0x7B,0x00}` for uint32 values, `u8{8,0,1,7}`,
`i32{0}`, `f{12.0}`, `ref{$name}`, and `u32[2]{{0,'sing'},{'uppr','doub'}}` for a list of pairs.

Every structure in the equation category also takes these two properties, which this catalogue does
not repeat:

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `pi` | int32 | 0 | Palette index, 0 to 15. |
| `co` | uint32 | 0xFF000000 | Colour as ABGR, alpha always 0xFF. |

Every structure in the drawing category takes these eight, which this catalogue does not repeat
either: `f` and `s` (bool, the fill and stroke flags), `w` (uint8, stroke width index 0 to 4), `d`
(uint8, stroke dash index 0 to 3), `fpi` and `spi` (int32, fill and stroke palette index 0 to 15),
`fco` and `sco` (uint32, fill and stroke colour as ABGR).

Three of the eight reach fewer structures than the specification's table suggests, and the validator
refuses the pairing rather than let it pass in silence. A line object, meaning `Ln`, `Cn`, `Zg`, `Qe`
and `Jo`, has a stroke and no fill: measured 2026-09-13, `f`, `fpi` and `fco` on each of the five
rendered exactly what the plain structure rendered, `fco=0xFFFF0000` leaving the path black while `sco`
coloured it. A `Jo`, which is a stretched bracket, brace or tortoise shell, takes no `w` and no `d`
either: `w=4` and `d=3` moved an `Ln`, a `Cn` and a `Qe` and left the joist alone. Only the three
shapes `Rt`, `Rr` and `El` use all eight, `f` filling them and `s` outlining them. One dash value
crashes: `Zg (d=3)` exits with an access violation before it renders, with or without `s` and with or
without `v`, while `d=1` and `d=2` draw and `d=3` draws on every other line.

Drawing structures inside one section are drawn in the order they are written, and the later one is on
top. Measured the same day: a filled `Rt` written before a filled `El` came out as the rectangle's path
then the ellipse's, and swapping the two structures swapped the paths. That order is what Bring Forward
and Send to Back change in the editor, so a highlight goes before the thing it sits behind and a strike
after it.

The byte order of `co`, `fco` and `sco` is alpha, blue, green, red, low byte red, which is the
reverse of the `#RRGGBB` a stylesheet writes. Radical Pie's own logo colours its radical
`co=0xFFC9906D` (the site's RadicalPie equation, line 14) and renders it `#6D90C9`, a mid blue; a
warm tan brown, `#A67B5B`, is written `0xFF5B7BA6`. Reverse the three bytes of the colour you want and
put `0xFF` in front of them.

Colour a caption with `co` or `pi` on each of its symbols, a line or an arrow with `sco` or `spi`,
and a highlight or a panel with `fco` or `fpi`. The seven indexes the site's own files reach for,
with the colour the factory palette gives each of them: 3 light grey `#C0C0C0` for a rule
or a strike, 4 red `#BA5858` for bond lines, 5 green `#339966` and 6 blue `#0066CC` for arrows and
their captions, 9 pale green `#9ED8A0`, 10 pale blue `#97D7E8` and 11 mauve `#C2A6DD` for fills. A
palette index means whatever the design in force says it means, so a file whose design carries a `P`
takes them from that, while `co` is fixed and a file with no `P` gets these.

Subgroups are `Gr` structures whose `t` property names their role in the parent. Each structure's
section in the family files lists the types it takes and how many of each. The order of the subgroups inside a
structure does not matter: one file Radical Pie wrote puts `'sups'` before `'subs'` in one script and
another puts `'subs'` before `'sups'` in another. This catalogue writes them in the order the
specification lists them.

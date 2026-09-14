# Pitfalls

The mistakes that produce a file Radical Pie rejects, crashes on, or renders wrongly without saying so,
and the shape of the messages the validator prints. Read it before handing over a file, and whenever a
validator message or a rendering is not what you expected.

Write UTF-8 without a BOM, and keep the header line `// Radical Pie Equation`, as Radical Pie does. A
file the program cannot parse raises a modal dialog saying the file does not contain valid Radical Pie
equation data, so validate before handing a file over.

A symbol's text is a data list, not a property: `Sb {s{"x"}}`, never `Sb (s="x")`. The same goes for a
bracket's characters, `u32{0x28,0x29}`, an iteration's or integral's character, and a mark's or prime's
character.

A four-character literal in single quotes is a number, and it must be exactly four characters:
`'vert'`, `'mddl'`, `'sing'`. The validator checks a property value against the specification's list of
allowed values, and of the values inside a data list it checks a connector's anchor types and indexes
alone, so a misspelled bond type or charm type passes it. Copy those from the catalogue.

A skeleton whose branch carbons carry their own substituents takes the long bond kinds, `'Sing'` and
`'Doub'`, on the central carbon's bonds, or the outer atoms crowd the centre; the site's isopropyl
alcohol uses `'Sing'` on all three central bonds.

An atom drawn on a shallow diagonal to the left of a carbon instead of straight to its left means the
atom was put in a `'uplf'` or `'lwlf'` neighbour group. The fix is a bond site of its own before the
carbon, with one rightward bond reaching it.

Matrix entries are listed in row-major order, and the count must equal `r` times `c`. The
specification says column-major and Radical Pie 1.15 does not; reading them in column order
transposes the matrix silently.

A bracket's subgroups carry `ba='mddl'` in every file Radical Pie writes: `Br { Gr (ba='mddl') { Bg {}
... } }`. A bracket with no `u32` array is a parenthesis pair. A zero for the left or right character
draws nothing on that side.

A `Br` whose group holds only its `Bg` draws a visible empty pair of glyphs, so to anchor a line at the
end of a term, name the term's last structure with `$name` instead of wrapping an empty group in `Br`.

Every bracket is a `Br`, a single letter or digit inside included, and never a pair of `Sb (ro='pnct')`
parentheses: the punctuation role spaces its symbol as punctuation, so a `(1)` written that way renders
`( 1 )` and leaves a gap before the full stop after it. The punctuation role is for commas and full
stops. Where the bracketed content carries a superscript, reach for `Br (as)`, the asymmetric extent,
which centres the bracket on its content instead of on the math axis; the site's own brackets round a
raised power are written that way.

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
dot, U+2032 for a prime, U+2026 and U+22EF for ellipses. `references/TexSymbols.md` gives the value for
each TeX name. Radical Pie 1.15's own editor writes U+00B7 for a centred dot; files from earlier
versions carry U+22C5 instead, and the editor draws both with the same glyph, so either validates and
renders the same.

`\mathbb{1}` and any double-struck letter or digit outside ℕℤℚℝℂ needs its own Mathematical
Alphanumeric code point written with `st='doub'`, since that same code point with `st='uprt'` renders
plain rather than double-struck.

A drawing structure's connector holds two anchors, one per end or per opposite corner, and an
annotation group's holds one; giving a drawing structure a single anchor crashes Radical Pie with an
access violation. A structure nested inside a subgroup exposes only anchor indexes 0 and 1, and asking
it for 2 or 3 crashes the program, which is why the validator refuses it. Run annotation
arrows from the term to a rail of the main group, `'xxx!'` index 1 above and index 0 below, which snaps
them vertical, and attach each caption to the far end of its arrow rather than to the term, so the
arrow's length places it. See the `X` section of `references/StructureCatalogue.md` for the anchor
indexes and Examples 23 and 24 for the whole pattern.

An arrow that points into a drawing starts from outside it: from the caption group's own type `0`
anchor, or from a rail with an `f{}` offset that slides the end along it. An arrow whose tail sits on a
symbol next to the target crosses the bonds between the two, which is what happens on a structural
formula when the tail is put on the hydroxyl and the head on the carbon beside it.

An arrow from a note beside one line of a multi-line equation lands on that line's `'axis'` anchor of
the main group, never on a symbol inside the line, or it crosses the line's tail. The catalogue's "A
note beside one line of a multi-line equation" section gives the pairing.

A connector whose far end names a matrix with a rail anchor type, `'xxx!'` or `'yyy!'`, crashes Radical
Pie with an access violation. The rails belong to the top-level group, so the far end of an arrow that
leaves a matrix names the equation group. A caption on a block inside a tiled grid goes on the
rectangle's `'anno'` anchor 4, over the centre; anchor 1 puts it above the rectangle, which is inside
the row above when the blocks tile the grid with no spare row.

An arrow onto a bracketed matrix starts from outside it, on `'orow'` or `'ocol'`, the grid's outer
edge, which clears the bracket; `'mrow'` and `'mcol'` sit on the same row and column midlines but
inside the grid, so an arrow from one of those drives its head straight into the bracket instead of
stopping short of it. Run the arrow on to a rail of the equation, `'xxx!'` or `'yyy!'`, and hang the
caption on its far end, exactly as an arrow onto a term does. The site's Exomorphism equation labels
its picture grid's rows and columns this way, off rail 5.

Two captions on the same rail overlap when their arrows stand closer than the captions are wide, and
nothing but a rendering shows it: send one arrow to the other rail, or align the captions away from each
other (`al='rght'` on the left one, `al='left'` on the right one). Inside a script, write a fraction as
`Fr (t='horz')`; the diagonal kind is cramped at script size. A prompt that calls an exponent's fraction
"slanted" or "small" still means `'horz'`, since `'diag'` shrinks and stacks rather than sitting on one
baseline either side of a slash. The label box paragraph of the `Gr` section and the `Fr` section of the
catalogue say why. Render every annotated equation and look at it before handing it over.

A symbol the surrounding prose mentions is an equation as well. A chapter that sets its display
equations through Radical Pie and writes the letters of its sentences as `\textit{j}`, or as a Word
italic, puts two different fonts on one page. Write the symbol as a one-symbol `.pie` and place it with
an inline `\pie{key}` or `{{pie:key}}`; `references/OutputForms.md` has the sizes measured beside body
text.

Validator messages have a fixed shape, and the useful part is the path and the section:

```
MyEquation.pie:10:2 Gr/Fr: Fr needs 1 group of type 'dnom', found 0 [Fr — Fraction Structure]
MyEquation.pie:20:3 Gr/Sc/Gr(t='sups'): the first substructure of Gr must be Bg, found Sb [Gr — Group Structure]
```

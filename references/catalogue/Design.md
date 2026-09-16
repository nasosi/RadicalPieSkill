# Design

## D — design

The design block. It holds design parameters, the fonts, the mapping from each symbol style to those
fonts, and the palette. A design merges into Radical Pie's factory design one structure at a time: each
`F`, `M`, `P` and `V` overrides one part of it, and every part the block leaves out keeps the factory
value. Measured 2026-09-13: a design naming one font and pointing the upright style at it moved the
upright glyphs and left the Greek, the italic and the integral exactly as an empty design drew them.

An empty `D {}` therefore does not take the design of whatever opens the file. It renders at the factory
design everywhere, 11 point text and the factory palette; the design a user saves as their own default in
the editor applies to a new equation the editor creates and not to a file it reads. Leave the design empty
when the caller supplies none, and write the design into the equation when the document has one.

No properties.

| Substructure | Count | Holds |
| --- | --- | --- |
| `V` | any | One design parameter. |
| `F` | 0 to 15 | One font. |
| `M` | 0 to 22 | One style mapping. |
| `P` | 0 or 1 | The palette. |

A document carries one design by carrying the same `D` block in every equation of it. Settle the block
once, from what the caller asked for, and copy it unchanged into each file; nothing outside the file
carries a design from one equation to the next. The block below is a whole document design, a text font,
the styles that draw from it, a palette and a size:

```pie
// Radical Pie Equation

D
{
	F (i=1) {s{"Cambria"}}
	M (t='uprt') {u8{1}}
	M (t='ital') {u8{1}}
	M (t='bold') {u8{1}}
	M (t='bitl') {u8{1}}
	P {u32{0xFF000000, 0xFF505050, 0xFF808080, 0xFFC0C0C0, 0xFF5858BA, 0xFF669933, 0xFFCC6600, 0xFFE55B90, 0xFF7085FF, 0xFFA0D89E, 0xFFE8D797, 0xFFDDA6C2, 0xFF00C0FF, 0xFF00FCFC, 0xFFA0D0E0, 0xFF4488CC}}
	V (n='fsiz') {f{12.0}}
}
Gr
{
	Bg {}
	Sb (st='bold') {s{"p"}}
	Sb (ro='rltn') {s{"="}}
	Sb {s{"m"}}
	Sb (st='bold') {s{"v"}}
}
```

The operator's design fixture is a full design as Radical Pie saves one: eight `F` structures naming
installed fonts at indexes 8 to 15, an `M` for each of the 21 styles it uses, a `P` of sixteen colours, and
`V (n='fsiz') {f{12.0}}`. Copy a design of that shape whole from the file that holds it rather than
assembling one from parts, because its maps mix the font indexes the design names with low indexes no `F`
in the file names, and which font such a slot resolves to is not readable from the file.

## F — font

One font of a design, named by the index the style maps refer to. The specification gives `F` no
substructures; one of the operator's fixtures writes the font name as a string data list inside it,
and the validator takes one data list, a string name or the registry number Radical Pie writes back,
and refuses an empty one.

Name a font by its family name in a string, `F (i=1) {s{"Cambria"}}`. Radical Pie looks the name up in its
own font registry, imports the font from the machine if it has to, and writes the registry's number back
in place of the name when it saves: the line above came back as `F (i=1) {u8{16}}`, and Arial came back as
6. The documentation's own fixtures carry that numeric form, `F (i=15) {u8{42}}`, which means a different
font on every machine, so write the name and keep the named file as the source.

A name the registry cannot answer is dropped from the design in silence, with no dialog and no error, and
every style mapped to that index falls back to the font it had. Measured 2026-09-13: "Cambria", "Arial",
"Georgia" and "Calibri" each changed the glyphs, while "Consolas", "Times New Roman", "STIX Two Text" and
"Cambria Math" rendered exactly as an empty design did. Render an equation once after naming a font and
compare it against the same equation with `D {}`; if nothing moved, the name did not resolve.

Index 0 is the built-in Radical font, over 1400 mathematical and scientific symbols cut to the metrics
of Times and STIX, with no letters, no digits and no everyday sign such as the percent or the ampersand.
No design replaces it: `F (i=0)` is dropped on save, and the validator refuses it.

Font 0 covers whole ranges of 256 code points and nothing between them: U+0000..00FF, U+0100..01FF,
U+0300..03FF, U+2000..20FF, U+2100..21FF, U+2200..22FF, U+2300..23FF, U+2500..25FF, U+2600..26FF,
U+2700..27FF, U+2900..29FF, U+2A00..2AFF, U+2B00..2BFF, U+EE00..EEFF, U+EF00..EFFF, U+1F700..1F7FF and
U+1F900..1F9FF. A character outside them needs a design font. Measured 2026-09-13 with a design that
leaves the Radical font alone in a style, `M (t='uprt') {u8{0,255,255,255}}`: one character from each
range but U+0300..03FF rendered its glyph, while `A`, `0`, `%`, U+0410, U+2460, U+24B6, U+2800 and
U+1D400 each drew the same 8.5562 by 8 pt hollow box, which is what a character no font in the style's
chain holds comes out as. That box is the sign to give the character a design font. U+0300..03FF holds
combining marks, which draw nothing standing alone and belong in a `Mk`, so the probe says nothing
about that range either way.

The Radical Font page lists U+1CE00..1CEFF, the Unicode 17 asteroids, and U+1F800..1F8FF, the
chemical equation arrows, as covered as well. Radical Pie 1.15 covers the asteroid range in part and
the arrow range not at all in the code points tried: measured 2026-09-14, U+1CEC0, U+1CED0 and
U+1CEF0 each drew a real outline 5.88 to 8.84 pt wide, while U+1CE01, U+1F801, U+1F810 and U+1F8B0
each drew the missing glyph box under the Radical font and under the factory design alike. Render an
asteroid symbol before relying on it, and draw a chemical equation arrow with `Ar` or write it as a
bond character instead.

The private use area U+EE00..U+EE65 is where the font keeps what Unicode has no code point for, in six
families: eight radius symbols at U+EE00, mirrored and inverted geometric shapes at U+EE08 and U+EE52,
twenty-four set relations at U+EE10, the twelve chemical bonds at U+EE30 that the `Sb` entry of
`references/catalogue/Symbols.md` teaches, arrows at U+EE40 and U+EE56, and two spaces, U+EE50 a double em
of exactly 36 math units and U+EE51 a thick space of 5 math units, which rendered 22 and 3.0556 pt wide at
11 pt with no path at all. The 1.14 arrows are U+EE4E, U+EE4F and U+EE5A to U+EE65, and the card suits
U+2660..2667 and musical notes U+2669..266C of the same release sit inside U+2600..26FF, which font 0
covers, so all of them draw with no design font.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `i` | int32 | 0 | Font index, 1 to 15. Slot 0 is the built-in Radical font. |

```pie
// Radical Pie Equation

D
{
	F (i=1) {s{"Cambria"}}
	M (t='uprt') {u8{1}}
}
Gr
{
	Bg {}
	Sb (st='uprt') {s{"a"}}
}
```

## M — map

Maps one symbol style to the fonts that draw it. A design carries at most one `M` per style, one for each
of the 22 styles listed under `Sb` in `references/catalogue/Symbols.md`, and Radical Pie 1.15 keeps 21 of
them: a design carrying all 22 comes back from a save with `M (t='grek')` gone and the other 21 intact,
which is the specification's maximum of 21 (measured 2026-09-14). Greek upright therefore cannot be
remapped by a file the editor has re-saved.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `t` | uint32 | required | The style, one of the style values listed under `Sb` in `references/catalogue/Symbols.md`. |

One `uint8` data list of one to four font indexes. The first is the primary font of the style and the rest
are its fallbacks, tried in order for a character the primary does not hold. An index of 255 means no font
in that slot; 255 in the first slot crashes Radical Pie with an access violation, and so does a first
index naming a slot no font fills, the factory design filling 0 to 8. The validator refuses both.

A map that names fewer than four indexes keeps the factory design's own fallbacks in the slots it leaves
out: `M (t='uprt') {u8{1}}` came back from a save as `u8{1,1,7,5}` and `M (t='doub') {u8{1}}` as
`u8{1,255,255,255}` (measured 2026-09-13). Naming one index is enough to move a style to another font and
keep its fallbacks.

One of the operator's fixtures carries a map for every style it uses, `M (t='ital') {u8{9,0,2,7}}` pointing the
italic style at the font it names at index 9, and `M (t='scpt') {u8{14,6,255,255}}` filling only two
slots. Take the maps of a design across together with its `F` structures; a map on its own names an
index that means nothing in another file.

```pie
// Radical Pie Equation

D
{
	F (i=14) {s{"NewCMMath-Book"}}
	M (t='doub') {u8{14,6,255,255}}
}
Gr
{
	Bg {}
	Sb (st='doub') {s{"ℝ"}}
}
```

## P — palette

The sixteen palette colours of a design, referred to by the `pi` property of an equation structure and
by `fpi` and `spi` of a drawing structure. The specification gives `P` no substructures;
One of the operator's fixtures writes the colours as a `uint32` data list inside it, and the
validator accepts one data list of any type. All sixteen are written, in index order, as ABGR with
`0xFF` in front, and a `P` replaces the whole factory palette rather than part of it.

The factory palette, index 0 to 15, read off one render of sixteen symbols on 2026-09-13: black,
`#505050`, `#808080`, `#C0C0C0`, `#BA5858`, `#339966`, `#0066CC`, `#905BE5`, `#FF8570`, `#9ED8A0`,
`#97D7E8`, `#C2A6DD`, `#FFC000`, `#FCFC00`, `#E0D0A0`, `#B39F80`. An equation that carries no `P` colours
`pi=5` that green and `pi=6` that blue, which is what the site's own arrows and captions rely on. Write a
`P` when the document's palette is its own, and give every index a colour, because the one it replaces is
gone.

No properties.

```pie
// Radical Pie Equation

D
{
	P {u32{0xFF000000, 0xFF3A3A3A, 0xFF777777, 0xFFB9B9B9, 0xFF0D14A6, 0xFF009012, 0xFFAC4E27, 0xFFE24D89, 0xFF8799FF, 0xFFAAE0A9, 0xFFF4D2B7, 0xFFEEACC0, 0xFF86D7FF, 0xFF00E7E7, 0xFFB7DDE9, 0xFF587486}}
}
Gr
{
	Bg {}
	Sb (pi=4) {s{"x"}}
}
```

## V — value

One design parameter, named in a domain. The domains are `0` for common settings, then `'symb'`,
`'mark'`, `'brck'`, `'scpt'`, `'frac'`, `'rdcl'`, `'divs'`, `'wide'`, `'stck'`, `'boxx'`, `'strk'`,
`'arrw'`, `'chrm'`, `'iter'`, `'intg'`, `'mtrx'`, `'line'`, `'jost'`, `'shap'`, `'anno'` and `'bond'`.
The specification's domain table omits `'bond'`; the site's FDG equation writes three parameters in it,
so the file wins.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `d` | uint32 | 0 | The domain. |
| `n` | uint32 | required | The parameter name, a four-character literal. |

The specification gives `V` no substructures; one of the operator's fixtures writes the parameter
value as a float data list inside it, and the validator takes one data list holding one number and
refuses an empty list or a value that is not a number.

The specification prints no parameter name at all. Radical Pie holds 347 of them, and the validator holds
the same table with the range each one is given, so run a name past the validator rather than guessing at
it: a name the domain does not hold, and a name written in the right spelling but the wrong domain, are
dropped from the design Radical Pie saves without a dialog and without an error, and the equation renders
as though the line had never been written. A value outside the parameter's range is not clamped either;
`V (d='intg',n='slnt') {f{90.0}}`, against a maximum of 20, rendered an SVG whose width was `INF`. The
count per domain: 13 common, 11 `'symb'`, 13 `'mark'`, 36 `'brck'`, 13 `'scpt'`, 20 `'frac'`, 19 `'rdcl'`,
8 `'divs'`, 36 `'wide'`, 8 `'stck'`, 5 `'boxx'`, 5 `'strk'`, 17 `'arrw'`, 19 `'chrm'`, 13 `'iter'`,
29 `'intg'`, 7 `'mtrx'`, 27 `'line'`, 15 `'jost'`, 3 `'shap'`, 6 `'anno'` and 24 `'bond'`.

Units follow the parameter. A bound of 1000 is points, and only `'fsiz'` has it; a bound of 45 or 75 is
degrees; a bound of 18 counts math units, an eighteenth of an em each, an em being the font size; the rest
are fractions of an em or plain factors.

A pair of names ending 0 and 1 is one setting at two sizes, the base level and the script level, and not
two sides of one thing. Measured 2026-09-13: `V (d='symb',n='osp0') {f{12.0}}` widened both sides of a
top level `a + b` from 21.9279 to 31.7057 pt and left the same expression inside a superscript
untouched, while `'osp1'` did the reverse.

The 22 domains are not the whole of the two design dialogs. Equation Design has 18 categories in 1.15,
Common through Matrices with Bonds among them, one per domain. Drawing Design has six, Anchors, Rails,
Lines, Joists, Shapes and Annotations, and only the last four have a domain. The Anchors settings, the
distance from a structure to the anchors a drawing attaches to, and the Rails settings, the distance to
each of the five rails on each side, reach no `.pie` file: their names are dropped from a design under
every domain and under none (measured 2026-09-13). So the anchor and rail positions the anchor atlas
gives are the factory ones for every file, whatever design it carries.

The parameters worth reaching for by name, each measured or written by Radical Pie itself:

| Domain | Name | Range | What it changes |
| --- | --- | --- | --- |
| `0` | `'fsiz'` | 1 to 1000 | The base font size in points. The factory value is 11. |
| `0` | `'slnt'` | 0 to 45 | The italic slant angle in degrees. |
| `0` | `'axis'` | 0 to 1 | The math axis height, the line a minus sign and a fraction rule sit on. |
| `0` | `'cptl'` | 0 to 2 | The capital height. |
| `'intg'` | `'slnt'` | -10 to 20 | The integral slant in degrees. At 20 the integral above grew from 19.6 to 25.6 points wide. |
| `'intg'` | `'gext'` | 0 to 18 | The integral stretch, how far the glyph grows for a tall integrand. |
| `'intg'` | `'sbsp'` | 0 to 18 | The gap between the integral and its limits; the site's Gaussian integral writes 6.0. |
| `'intg'` | `'lgsz'` | 0.25 to 4 | The size of the display integral glyph. |
| `'brck'` | `'vtgp'` | 0 to 18 | How far a bracket grows past its content; the site writes 1.0 and 4.0. |
| `'frac'` | `'rule'` | 0.25 to 4 | The thickness of the fraction rule. |
| `'mtrx'` | `'rwgp'` | 0 to 18 | The row gap; the site's exomorphism writes 18.0. |
| `'mtrx'` | `'clgp'` | 0 to 18 | The column gap. |
| `'mtrx'` | `'aspx'` | 0 to 4 | The width the cells are laid out to; the site writes 1.25. |
| `'mtrx'` | `'aspy'` | 0 to 4 | The height they are laid out to; the site writes 0.5. |
| `'rdcl'` | `'rule'` | 0.25 to 4 | The thickness of the radical's bar; the site's own logo writes 2.0. |
| `'bond'` | `'wgap'` | 0.01 to 2 | The gap between the strokes of a double bond; the site's FDG writes 0.09471. |
| `'bond'` | `'hlln'` | 0.25 to 4 | The halved bond length; FDG writes 2.0. |
| `'bond'` | `'dlln'` | 0.25 to 4 | The doubled bond length; FDG writes 2.5. |
| `'symb'` | `'fnsp'` | 0 to 18 | The space on each side of a standard function name. The factory value is 3 mu. |
| `'line'` | `'lngo'` | 0.01 to 2 | How far a `'long'` end overshoots its anchor, 2.6774 pt at the factory design. |
| `'line'` | `'shto'` | 0.01 to 2 | How far a `'shrt'` end undershoots it, the same 2.6774 pt. |

The `'rdcl'` domain answers to eight names worth writing, measured 2026-09-15 on an `Rd` over a single
`x` at the factory 11 pt design. `'rule'`, 0.25 to 4, is the bar. `'rsc0'`, 0.1 to 8, scales the hook at
the foot, which at 8.0 reached 0.85 pt to the left of where the sign had begun. `'rsc1'` and `'rsc2'`,
0.1 to 8 each, are the thickness of the descending and of the ascending stroke of the check mark, 0.78
and 0.52 pt as the factory design draws them and 4.17 pt each at 8.0. `'swd0'` and `'swd1'`, 0.05 to 2
with the factory values 0.10 and 0.1875, are the widths of those same two strokes and are worth 11 pt of
equation width per unit, so `V (d='rdcl',n='swd0') {f{0.20}}` took the equation from 14.2083 to 15.3083
pt. `'vtgp'` and `'vtsp'`, 0 to 18 each, lift the sign off the radicand, 10.0 raising the bar 4.46 pt
through the first and 3.67 pt through the second. The three `'rsc'` names change what is drawn and not
what the equation reserves, and at 1.2 none of them moves a point of the sign as far as 0.18 pt, so a
sign that has to read heavier is written with `'rule'`, `'swd0'` and `'swd1'`.

`'axis'`, `'cptl'` and `'slnt'` do not follow the fonts a design names. The Common pane of the Equation
Design dialog puts an Auto button beside each of the three, which computes it from the first font of the
Upright style, the first Upright font that is not the Radical font, and the first Italic font that is not
the Radical font; the button is the editor's, and nothing in a file does it. Measured 2026-09-13: a
design naming Cambria for the upright style drew a capital `H` 7.3315 pt tall against Times's 7.2832,
and the bond character beside it stayed at 3.6416 pt, half the factory capital height, in both. A design
that changes its fonts and wants the three to match writes them itself.

Take a parameter across to another equation with its value, and change a value only when the caller says
what should look different.

```pie
// Radical Pie Equation

D
{
	V (n='fsiz') {f{12.0}}
}
Gr
{
	Bg {}
	Sb {s{"x"}}
}
```

### The design values of a picture grid

A matrix whose cells hold coloured blocks, arrows or labels rather than numbers is spaced by the design
and not by spacers inside the cells: a `Sp` moves the content of the one cell it stands in, where these
values move every row and column at once. The site's own diagram of an exomorphism, an eight by eight
grid of blocks inside square brackets, carries all four of them, `V (d='mtrx',n='rwgp') {f{18.0}}` for
the gap between rows, `V (d='mtrx',n='aspx') {f{1.25}}` and `V (d='mtrx',n='aspy') {f{0.5}}` for the
proportions the cells are laid out to, and `V (d='brck',n='vtgp') {f{1.0}}` for the brackets around the
grid. The site's nine by nine truth-table grid, also in square brackets, carries `vtgp` at 4.0 and
nothing else. Copy the set across with its values, and reach for one on its own only when the caller
asks for what it changes.

```pie
// Radical Pie Equation

D
{
	V (d='brck',n='vtgp') {f{1.0}}
	V (d='mtrx',n='rwgp') {f{18.0}}
	V (d='mtrx',n='aspx') {f{1.25}}
	V (d='mtrx',n='aspy') {f{0.5}}
}
Gr
{
	Bg {}
	Br
	{
		u32{0x5B,0x5D}
		Gr (ba='mddl')
		{
			Bg {}
			Sp (s=3.0) {}
			Mx (r=2,c=2,eh,ew,rg,cg)
			{
				Gr
				{
					Bg {}
					Sb (co=0xFF85CCC9,st='uprt') {s{"⬛"}}
				}
				Gr
				{
					Bg {}
				}
				Gr
				{
					Bg {}
				}
				Gr
				{
					Bg {}
					Sb (co=0xFFC2A6DD,st='uprt') {s{"⬛"}}
				}
			}
		}
	}
}
```

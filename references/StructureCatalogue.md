# Structure Catalogue

Every structure the Radical Pie file format defines, with its properties, its subgroups and a minimal
example that the validator accepts. Derived from the documentation's file format reference and from
the rules the validator encodes in its own schema. Where a rule in this catalogue is looser than the
specification, a note says which fixture written by Radical Pie proves the looser rule; the file the
program writes wins over the document.

Run every example past the validator before trusting a variation on it:

```
python Skill/RadicalPie/scripts/Validate.py <file>
```

## Contents

| Structure | Category | Purpose |
| --- | --- | --- |
| [Al](#al--aligner) | equation | Aligns the same column across the lines of a group. |
| [Ar](#ar--arrow) | equation | A big stretching arrow with charms and labels. |
| [Bd](#bd--bond) | equation | A chemical bond site with up to six neighbours. |
| [Bg](#bg--begin) | equation | Begins a line; the first child of every group. |
| [Br](#br--bracket) | equation | A bracket pair around one or more groups. |
| [Bx](#bx--box) | equation | A box around a group. |
| [Cn](#cn--corner) | drawing | A corner drawing object. |
| [D](#d--design) | design | The design block: values, fonts, style maps, palette. |
| [Dv](#dv--division) | equation | A long division. |
| [El](#el--ellipse) | drawing | An ellipse drawing object. |
| [En](#en--enclose) | modifier | An enclosure around one symbol. |
| [F](#f--font) | design | One font of a design. |
| [Fr](#fr--fraction) | equation | A fraction, vertical, horizontal or diagonal. |
| [Gr](#gr--group) | equation | A group: the main equation, and every typed subgroup. |
| [In](#in--integral) | equation | An integral with optional limits. |
| [It](#it--iteration) | equation | A sum, product or other iterated operator. |
| [Jo](#jo--joist) | drawing | A brace or bracket drawing object. |
| [Kt](#kt--strike) | equation | A strike through a group. |
| [Ln](#ln--line) | drawing | A line drawing object. |
| [M](#m--map) | design | Maps one symbol style to fonts. |
| [Mk](#mk--mark) | modifier | An accent on one symbol. |
| [Mx](#mx--matrix) | equation | A matrix of entry groups. |
| [Ng](#ng--negate) | modifier | A negation stroke through one symbol. |
| [P](#p--palette) | design | The sixteen palette colours of a design. |
| [Ph](#ph--phantom) | equation | Space held without ink. |
| [Pr](#pr--prime) | equation | Prime marks on the preceding structure. |
| [Qe](#qe--quarter-ellipse) | drawing | A quarter ellipse drawing object. |
| [Rd](#rd--radical) | equation | A radical with an optional degree. |
| [Rr](#rr--rounded-rectangle) | drawing | A rounded rectangle drawing object. |
| [Rt](#rt--rectangle) | drawing | A rectangle drawing object. |
| [Sb](#sb--symbol) | equation | One or more characters with one role and one style. |
| [Sc](#sc--script) | equation | A subscript, a superscript, or both. |
| [Sl](#sl--slash) | modifier | A slash through one symbol. |
| [Sp](#sp--space) | equation | A space, a kern, or a tab stop. |
| [St](#st--stack) | equation | An expression with a small label above or below. |
| [V](#v--value) | design | One design parameter. |
| [Wm](#wm--widemark) | equation | A stretching mark over or under a group. |
| [X](#x--connector) | connector | Attaches a drawing or annotation to an anchor. |
| [Zg](#zg--zigzag) | drawing | A zigzag drawing object. |

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
section below lists the types it takes and how many of each. The order of the subgroups inside a
structure does not matter: one file Radical Pie wrote puts `'sups'` before `'subs'` in one script and
another puts `'subs'` before `'sups'` in another. This catalogue writes them in the order the
specification lists them.

## Al — aligner

Marks a column in a multi-line group. The i-th aligner on every line stands at the same x, and the
span between two consecutive aligners is a box as wide as the widest line's content in that span. The
`al` of the aligner at the right end of a span places that line's content inside the box, and the
property is read line by line, so the three values may differ down one column.

The column does not move when `al` changes; only the material before the aligner does. Measured at the
default design on four lines whose longest left-hand side is 23.96 points wide, the relation after the
aligner starts at 26.8990 points on every line, and the shorter left-hand sides start at 0.0000 with
`'left'`, at 18.5142 with `'rght'`, which puts their right edge on the column, and at 9.8345 with
`'cent'`, which centres them in the box. A line carrying no aligner starts at the line origin and takes
no part in the columns.

| Property | Type | Default | Values |
| --- | --- | --- | --- |
| `al` | uint32 | `'left'` | `'left'`, `'rght'`, `'cent'` |

No subgroups, no data lists. An aligner is written `Al (al='rght') {}`. Radical Pie renders a value
outside the three as `'left'` and reports nothing; the validator refuses it.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb {s{"x"}}
	Al (al='rght') {}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"1"}}
	Bg {}
	Sb {s{"x"}}
	Sb (ro='oper') {s{"+"}}
	Sb {s{"y"}}
	Al (al='rght') {}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"2"}}
}
```

## Ar — arrow

One, two or three stretching arrows drawn as a unit, with charms on them and optional labels above and
below. This is `\xrightarrow` and every reaction arrow. Everything below the subgroup table was
measured on Radical Pie 1.15 by rendering it.

No properties beyond the two every equation structure has. There is no length property and no design
value that sets one; the labels are what set the length.

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr (t='uppr')` | 0 or 1 | The label above. |
| `Gr (t='lowr')` | 0 or 1 | The label below. |

Two to four `uint32` data lists. The first holds one to three arrow types, top to bottom. One further
list follows per arrow, holding that arrow's charms.

| Arrow type | Draws |
| --- | --- |
| `'long'` | The full length of the structure. |
| `'left'` | Short, flush with the left end. |
| `'rght'` | Short, flush with the right end. |
| `'cent'` | Short, centred, short at both ends. |

### How long the arrow comes out

With no label an arrow is 16.5 points long at a 12 point design. With a label it is the label's own
width plus 11 points of shaft at each end, and the wider of the two labels sets it: labels 8.10, 21.60,
59.26 and 88.35 points wide gave arrows 30.10, 43.60, 81.26 and 110.35 points long. A short arrow is
5.5 points shorter than that at each end that is free, so under one 43.60 point label the `'long'`
arrow runs the whole width, the `'left'` arrow stops 5.5 points before the right end and the `'rght'`
arrow starts 5.5 points in.

To set a length directly, put a space in a label and nothing else: `Sp (s=60.0)` alone in a `'lowr'`
group gives an arrow 45.83 points long.

An arrow costs its own width plus 4.89 points of space in the line, and the roles of the symbols
around it change nothing: the same two symbols stand the same distance apart in chemistry roles and in
plain mathematics.

### The charms

A charm list is read in order with a cursor that starts at the right end. `'left'`, `'cent'` and
`'rght'` in the list move the cursor, and every other value drops a charm at the cursor. A `'rght'`
written first changes nothing, an alignment with no charm after it draws nothing, and the cursor may
go back to a position it has already filled and add to it. Charms at one end stack away from that end
and leave the shaft the same length; charms at the centre widen the whole structure once they no
longer fit.

The specification's charm table marks each type legal at the left end, at the right end or in the
interior. Radical Pie draws all forty at all three positions, so those columns are the three palettes
of the Insert Arrow dialog and not a rule of the format. The limit of three charms per position is the
same kind of thing: five arrowheads at the right end all draw. The name of a charm decides its shape
and not where it may go, so `'luhp'` written with the cursor at the right end puts a left-pointing
harpoon at the right end.

| Family | Charms | Each draws |
| --- | --- | --- |
| Arrowheads | `'larw'`, `'rarw'` | A head pointing left, a head pointing right. |
| Heads to a bar | `'labr'`, `'rabr'` | The same head against a crossbar, ↤ and ↦. |
| Harpoons | `'luhp'`, `'ruhp'`, `'ldhp'`, `'rdhp'` | One barb only: pointing left or right, above the shaft or below it. |
| Harpoons to a bar | `'luhb'`, `'ruhb'`, `'ldhb'`, `'rdhb'` | The same four against a crossbar. |
| Bars and lines | `'barr'`, `'line'`, `'dbln'` | A bar, a line, a double line. |
| Strokes | `'slsh'`, `'dbsl'`, `'back'`, `'dbbk'`, `'exxx'` | A slash, a double slash, a backslash, a double backslash, an X. |
| Circles and squares | `'circ'`, `'sdcr'`, `'squa'`, `'sdsq'` | Open and solid circle, open and solid square. |
| Diamonds and triangles | `'diam'`, `'sddm'`, `'ltri'`, `'sdlt'`, `'rtri'`, `'sdrt'` | Open and solid diamond, open and solid triangle pointing left, open and solid triangle pointing right. |
| Hooks | `'luhk'`, `'ldhk'`, `'ruhk'`, `'rdhk'` | The hook of ↪, at the left or the right, curling up or down. |
| Fishtails | `'lfsh'`, `'rfsh'` | The fishtail of ⇜, at the left or the right. |
| Loops | `'lulp'`, `'ldlp'`, `'rulp'`, `'rdlp'` | The loop of ⊸, at the left or the right, above the shaft or below it. |

### The labels

One group of each type. A second group of the same type is the one shape of an arrow Radical Pie
refuses outright, with the invalid data dialog. A group of any other type is accepted by the program
and drawn on top of the arrow, and the validator refuses it.

A label with no `al` is centred over the shaft, which is what a catalyst or a condition wants, so the
`al='cent'` the chemistry examples write changes nothing. `al='left'` and `al='rght'` push the label to
the ends of the stretched width, which is how two labels on one arrow are read apart.

### A labelled reaction arrow

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Ar
	{
		u32{'long'}
		u32{'rarw'}
		Gr (t='uppr')
		{
			Bg {}
			Sb (ro='chem') {s{"Pt"}}
		}
		Gr (t='lowr')
		{
			Bg {}
			Sb (ro='nmbr') {s{"150"}}
			Sb (ro='unit') {s{"°C"}}
		}
	}
}
```

### An equilibrium pair

Two full-length arrows, an upward harpoon pointing right on the upper one and a downward harpoon
pointing left on the lower one. The `'left'` before the lower charm is what puts it at the left end;
without it both harpoons land at the right end and the arrow reads as neither one thing nor the other.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Ar
	{
		u32{'long','long'}
		u32{'ruhp'}
		u32{'left','ldhp'}
	}
}
```

### One harpoon at each end

`'luhp'` draws wherever the cursor is. Here it stands at both ends of one shaft, pointing the same way
twice, which is what the charm table's Left column says cannot happen.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Ar
	{
		u32{'long'}
		u32{'left','luhp','rght','luhp'}
	}
}
```

### A charm on the shaft

An arrowhead at the right end and a cross at the centre, the reaction that does not happen.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Ar
	{
		u32{'long'}
		u32{'rarw','cent','exxx'}
	}
}
```

## Bd — bond

One atom with bonds radiating from it. Molecules are built left to right along the baseline, and any
group of a bond site may hold a further bond site.

No properties beyond the two every equation structure has.

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr` | 1 | The central atom. Required. |
| `Gr (t='uppr')` | 0 or 1 | The atom at the end of the upward bond. |
| `Gr (t='uplf')` | 0 or 1 | Upper left. |
| `Gr (t='uprt')` | 0 or 1 | Upper right. |
| `Gr (t='lowr')` | 0 or 1 | Downward. |
| `Gr (t='lwlf')` | 0 or 1 | Lower left. |
| `Gr (t='lwrt')` | 0 or 1 | Lower right. |

One or two `uint32[2]` data lists of pairs. The first pair list gives (group type, bond type) for each
bond, where a group type of `0` means the rightward bond, which has no group of its own. The bond
types are `'sing'`, `'doub'`, `'trip'`, `'hevy'`, `'wavy'`, `'part'`, `'prd1'`, `'prd2'`, `'prt1'`,
`'prt2'`, `'prt3'`, `'swgo'`, `'swgi'`, `'dwgo'` and `'dwgi'`; capitalising the first letter makes the
bond long, so `'Sing'` is a long single bond. The optional second pair list gives (group type, angle
type) with `'step'` for a steep angle and `'shal'` for a shallow one, and applies only to the four
diagonal directions.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Bd
	{
		u32[2]{{'uppr','sing'},{0,'sing'}}
		Gr
		{
			Bg {}
			Sb (ro='chem') {s{"C"}}
		}
		Gr (t='uppr')
		{
			Bg {}
			Sb (ro='chem') {s{"H"}}
		}
	}
	Sb (ro='chem') {s{"OH"}}
}
```

## Bg — begin

Begins a line. Every group starts with one, and a further `Bg` inside the same group starts another
line, which is how a multi-line equation is written. A blank line, one whose `Bg` is followed straight by
the next `Bg` or the end of the group, still carries its own anchors (1.9.1), so an empty line remains a
valid target for a drawing object or an annotation.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `lg` | float | −1.0 | Line gap before this line, in math units. Negative means the design's gap. |

No subgroups, no data lists. Written `Bg {}`.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='text') {s{"first line"}}
	Bg (lg=24.0) {}
	Sb (ro='text') {s{"second line"}}
}
```

## Br — bracket

A bracket pair around one or more groups, stretched to the height of what it holds. Parentheses,
square brackets, braces, angle brackets, absolute value bars and norm bars are all `Br`.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `as` | bool | false | Asymmetric vertical extent: centre on the content, not on the math axis. |
| `ca` | bool | false | Shift the content so its centre sits on the math axis. |

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr (ba='mddl')` | 1 to 9 | The bracketed material, left to right. |

At most one `uint32` data list of two or three Unicode values: the left character, the right
character, and for a multi-group bracket the character repeated between the groups. Zero for the left
or right character draws nothing on that side, which is how a `cases` brace is written:
`u32{0x7B,0x00}`. Radical Pie writes no data list at all for a plain parenthesis pair, as several of
its own files do throughout; the specification gives the list a minimum of one, and the validator
follows the fixtures instead.

The subgroups carry `ba='mddl'` in every fixture, and nothing else; the specification does not
enumerate the values of `ba`.

Common characters: `0x28`/`0x29` parentheses, `0x5B`/`0x5D` square brackets, `0x7B`/`0x7D` braces,
`0x7C` bar, `0x2016` double bar, `0x27E8`/`0x27E9` angle brackets, `0x230A`/`0x230B` floor,
`0x2308`/`0x2309` ceiling, `0x2997`/`0x2998` tortoise shell.

The tortoise shell pair stretches like the rest, which release 1.2 added. Measured 2026-09-13:
`u32{0x2997,0x2998}` round a single `x` came out 12 pt tall and round a vertical fraction 26 pt, the
same two heights as the parentheses round the same content, and the shell is drawn by the bracket code
rather than fetched from a font, because the Radical font holds neither code point.

`ca` acts only together with `as`. Measured 2026-09-13 on a bracket round `x²`: `Br` and `Br (ca)`
rendered the same paths at 17 pt tall, `Br (as)` 13 pt and `Br (as,ca)` 14 pt. Write `ca` on a bracket
that already carries `as`, where it shifts the content so its centre lands on the math axis.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Br
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sb {s{"x"}}
		}
	}
	Br
	{
		u32{0x7B,0x7D,0x7C}
		Gr (ba='mddl')
		{
			Bg {}
			Sb {s{"x"}}
		}
		Gr (ba='mddl')
		{
			Bg {}
			Sb {s{"x"}}
			Sb (ro='rltn') {s{">"}}
			Sb (ro='nmbr') {s{"0"}}
		}
	}
}
```

## Bx — box

A box drawn around one group, on all four sides or on two. This is `\boxed` and `\fbox`.

| Property | Type | Default | Values |
| --- | --- | --- | --- |
| `t` | uint32 | `'full'` | `'full'`, `'lwlf'`, `'lwrt'`, `'uplf'`, `'uprt'` |

`'lwlf'` draws the bottom and the left side, `'lwrt'` the bottom and the right, `'uplf'` the top and
the left, `'uprt'` the top and the right. The two general equation properties apply: `co` and `pi`
colour the border and leave the boxed material in its own colour.

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr` | 1 | The boxed material. |

Measured on the digits 48 at a 12 pt design, 2026-09-13. The border is 0.52 pt thick and stands 3.06 pt
clear of the content on the left and the right and about 4.1 pt above and below, and the structure
keeps 1.22 pt outside the border on each side, so a box turns an 11 by 9 pt expression into a 19.79 by
18 pt one. A two-sided box reserves the same space as a four-sided one, which is what keeps a column of
boxed lines in line. There is no padding property. A value of `t` outside the five draws the
four-sided box with no word, and no box draws one side alone, so `\overline` is a `Wm`.

Two design values change the box, both measured on 2026-09-13. `V (d='boxx',n='rule')` is the border
thickness in math units, 0.611 pt each at a 12 pt design, so 2.0 draws a 1.22 pt border against the
0.52 pt default. `V (d='boxx',n='vtsp')` is the space above and below the content: 12.0 puts the top
border 15.14 pt above the baseline where the default puts it at 12.08, and 6.0 pulls it in to 11.47.
Neither name is in the documentation, and no name was found for the space to the left and the right;
`'hzgp'`, `'hzsp'`, `'hzpd'`, `'hpad'`, `'pdng'`, `'marg'`, `'clrn'` and nine more render unchanged,
which is what a value name a domain does not have does.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Bx
	{
		Gr
		{
			Bg {}
			Sb {s{"E"}}
			Sb (ro='rltn') {s{"="}}
			Sb {s{"mc"}}
			Sc
			{
				Gr (t='sups')
				{
					Bg {}
					Sb (ro='nmbr') {s{"2"}}
				}
			}
		}
	}
}
```

A corner box with a thicker border, the shape a worked example uses to mark the step it is carrying
forward.

```pie
// Radical Pie Equation

D
{
	V (d='boxx',n='rule') {f{2.0}}
}
Gr
{
	Bg {}
	Bx (t='uplf')
	{
		Gr
		{
			Bg {}
			Sb (ro='nmbr',tf) {s{"48"}}
		}
	}
}
```

## Cn — corner

A corner drawing object: one horizontal leg and one vertical one, horizontal first, or vertical first
with `v`. Drawing structures sit outside the main equation, before it for the background layer and
after it for the foreground layer, and each attaches to two anchors through its connector, one per end
of the corner; see `X` for the rule and the reason a single anchor crashes Radical Pie.

It routes between its two anchors, turning where a straight line would run diagonally, so it reaches a
term the arrow-to-rail form under [Ln](#ln--line) cannot. Reach for it only then: a straight vertical
arrow to a rail is the form to teach.

The specification lists `es`, `ef`, `os` and `of` under `Ln` alone. A corner takes all four, measured
2026-09-12: the head is drawn at the first anchor for `es` and at the second for `ef`, lying along the
leg it sits on, and Radical Pie writes the properties back when it saves the file.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `v` | bool | false | The vertical flag. |
| `es` | uint32 | 0 | Start endpoint: `0`, `'sdcr'`, `'sdsq'`, `'wedg'`, `'arr1'`, `'arr2'`. |
| `ef` | uint32 | 0 | Finish endpoint: same values. |
| `os` | uint32 | 0 | Start offset: `0`, `'long'`, `'shrt'`. |
| `of` | uint32 | 0 | Finish offset: same values. |

| Substructure | Count |
| --- | --- |
| `X` | 1 |

Its own anchors, from `references/AnchorAtlas.md`: `'line'` 0 at the first anchor, 1 at the second and
2 at the turn; `'anno'` 0 and 1 beyond the two ends, 2 and 3 beyond the turn, 4 and 5 either side of
the second leg and 6 and 7 either side of the first.

```pie
// Radical Pie Equation

D
{
}
Gr $main
{
	Bg {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"1"}}
}
Cn (s,v)
{
	X
	{
		ref {$main,$main}
		u32{'bord','bord'}
		i32{0,2}
	}
}
```

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

## Dv — division

A long division: the dividend under the vinculum, with an optional quotient above it. The divisor is
not part of the structure; it is the symbol written before it, and Radical Pie puts no space between
the two.

No properties beyond the two every equation structure has.

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr` | 1 | The dividend. Required. |
| `Gr (t='quot')` | 0 or 1 | The quotient. |

The two groups may be written in either order and render the same equation. The dividend is required:
a division holding only its quotient, holding two dividends, or holding nothing raises the invalid-data
dialog.

Measured on 2026-09-13 at a 12 pt design. The division sign is one path, the hook and the vinculum
together: it reaches 1.93 pt below the baseline, 2.56 pt above the digits, and 0.61 pt past the right
end of the dividend, and it costs 3.86 pt of width. The quotient is right-aligned over the dividend,
always: a one-digit quotient over a four-digit dividend sits over the last digit, and `al` on the
quotient group changes nothing. Whichever of the two is wider sets the length of the vinculum.

The working of a division goes on further lines of the dividend group, one `Bg` per line, and the
division sign grows down over all of them, which is the shape a textbook prints. Digits are not on a
fixed pitch unless you ask for it: the columns of 91 over 21 are 0.2 pt apart with plain numbers and
exactly aligned with `tf`, the strict tabular figures flag, on every `Sb`. A blank column is a
`Ph (t='full')` holding the digit that would have stood there, and a subtraction rule is
`Wm (t='line',un)` around the row above it.

Two design values change the layout, measured the same day and absent from the documentation.
`V (d='divs',n='rule')` is the thickness of the vinculum and `V (d='divs',n='vtsp')` the space between
the quotient and it, 12.0 lifting the quotient 10.63 pt higher than 0.0 does.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='nmbr',tf) {s{"7"}}
	Dv
	{
		Gr
		{
			Bg {}
			Sb (ro='nmbr',tf) {s{"91"}}
		}
		Gr (t='quot')
		{
			Bg {}
			Sb (ro='nmbr',tf) {s{"13"}}
		}
	}
}
```

## El — ellipse

An ellipse drawing object, attached at two opposite corners of its bounding box.

No properties beyond the eight every drawing structure has.

| Substructure | Count |
| --- | --- |
| `X` | 1 |

Border indexes 0 and 3 draw the ellipse, and so do 0 and 1; indexes 0 and 2, or 1 and 3, give the
ellipse a NaN height and must not be used.

```pie
// Radical Pie Equation

D
{
}
Gr $main
{
	Bg {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"1"}}
}
El (s)
{
	X
	{
		ref {$main,$main}
		u32{'bord','bord'}
		i32{0,3}
	}
}
```

## En — enclose

An enclosure around a single symbol. It is a child of the `Sb` it applies to, not a wrapper around it,
and it has no substructures: an `En` holding a group raises the invalid-data dialog.

| Property | Type | Default | Values |
| --- | --- | --- | --- |
| `t` | uint32 | `'circ'` | `'circ'`, `'squa'`, `'rdsq'` |
| `pi` | int32 | 0 | The palette index, 0 to 15. |
| `co` | uint32 | 0xFF000000 | The colour as ABGR. |

The three shapes are a circle, a square and a square with rounded corners, three different paths inside
the same square outline. `pi` and `co` are the general equation properties, which the specification
offers to the equation category and the executable honours on every modifier: they colour the
enclosure and leave the symbol black (measured 2026-09-13).

The enclosure is a fixed size and does not grow with what it encloses. Measured on 2026-09-13, it is a
9.32 pt square stroked 0.52 pt at a 12 pt design, whatever the symbol: a W, 10.15 pt wide, pokes out on
both sides, a √ stands well above and below it, and on a symbol holding several characters it encloses
the first one and the rest run out to the right. It follows the size of its surroundings rather than
its content, 6.06 pt across in a superscript and 20.34 pt at a 24 pt design, and it centres on the
first character's ink. Enclose one character; for a whole expression use a `Bx`.

A symbol takes at most one enclosure. Radical Pie draws two side by side if a file carries two, and it
draws a bare `En` standing in a group as an empty ring, but neither is a shape the specification allows
and the validator refuses both.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='oper') {s{"+"} En (t='circ') {}}
	Sb (ro='nmbr') {s{"1"} En (t='squa') {}}
	Sb (ro='nmbr') {s{"2"} En (t='rdsq',co=0xFF0000FF) {}}
}
```

## F — font

One font of a design, named by the index the style maps refer to. The specification gives `F` no
substructures; one of the operator's fixtures writes the font name as a string data list inside it,
and the validator accepts one data list of any type.

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

The Radical Font page lists U+1CE00..1CEFF, the Unicode 17 asteroids, and U+1F800..1F8FF, the chemical
equation arrows, as covered as well; Radical Pie 1.15 does not have them. Thirty-one code points across
the two ranges each drew the box under the Radical font and under the factory design alike, so a
chemical equation arrow is drawn with `Ar` or written as a bond character instead.

The private use area U+EE00..U+EE65 is where the font keeps what Unicode has no code point for, in six
families: eight radius symbols at U+EE00, mirrored and inverted geometric shapes at U+EE08 and
U+EE52, twenty-four set relations at U+EE10, the twelve chemical bonds at U+EE30 that the `Sb` entry
teaches, arrows at U+EE40 and U+EE56, and two spaces, U+EE50 a double em of exactly 36 math units and
U+EE51 a thick space of 5 math units, which rendered 22 and 3.0556 pt wide at 11 pt with no path at all.
The 1.14 arrows are U+EE4E, U+EE4F and U+EE5A to U+EE65, and the card suits U+2660..2667 and musical
notes U+2669..266C of the same release sit inside U+2600..26FF, which font 0 covers, so all of them
draw with no design font.

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

## Fr — fraction

A fraction. The vertical kind stacks numerator over denominator; the horizontal kind puts them on one
baseline either side of a slash; the diagonal kind raises the numerator and drops the denominator
either side of a slash. Clearing the bar with `at` makes a binomial coefficient, which keeps the
vertical spacing of a fraction.

Inside a superscript or subscript, use the horizontal kind: a diagonal fraction shrinks with the script
and its raised numerator and dropped denominator become cramped and hard to read at that size, while
`Fr (t='horz')` keeps both on the script's baseline, as in `(Z/a_0)^{3/2}` or `e^{-Zr/a_0}`. The
diagonal kind reads well at text size, for a small ratio inside a sentence.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `t` | uint32 | `'vert'` | `'vert'`, `'horz'` or `'diag'`. |
| `sm` | bool | false | Small layout, for inline equations. Only when `t` is `'vert'` or `'diag'`. |
| `at` | bool | false | Atop: no fraction bar. Only when `t` is `'vert'`. |
| `ns` | bool | false | Disable slant kerning. Only when `t` is `'horz'`. |

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr (t='numr')` | 1 | The numerator. |
| `Gr (t='dnom')` | 1 | The denominator. |

Both subgroups take the group alignment `al`, and a fraction's default is centre whichever part is
wider. Write `al='left'` or `al='rght'` on the shorter of the two to line a column of terms up, as the
second fraction below does; leaving `al` out is the same as writing `al='cent'`, measured on the same
fraction.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Fr (at)
	{
		Gr (t='numr')
		{
			Bg {}
			Sb {s{"n"}}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb {s{"k"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Fr (t='diag',sm)
	{
		Gr (t='numr')
		{
			Bg {}
			Sb (ro='nmbr') {s{"1"}}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Fr
	{
		Gr (t='numr',al='left')
		{
			Bg {}
			Sb {s{"x"}}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb {s{"abcd"}}
		}
	}
}
```

## Gr — group

A group holds a run of equation structures. The main equation is a group; so is every typed subgroup
of a structure; so is an annotation.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `t` | uint32 | 0 | The group type, below. |
| `al` | uint32 | 0 | Horizontal alignment: `'left'`, `'cent'`, `'rght'`, and 0 for Align Default. |
| `ba` | uint32 | `'last'` | Baseline alignment: `'frst'` the first line's baseline, `'last'` the last line's, `'mddl'` the middle. It decides which line of a group lines up with what surrounds it, and inside a matrix it is the entry alignment. Every bracket subgroup and every inline group writes `'mddl'`. |
| `as` | float | 1.0 | Adjustment scale, greater than 0. |
| `ax` | float | 0.0 | Nudge along x, in math units. |
| `ay` | float | 0.0 | Nudge along y, in math units. |

The group types are `0` for the main equation and for the primary subgroup of a structure, `'anno'`
for an annotation group at the file level, and `'subs'`, `'sups'`, `'numr'`, `'dnom'`, `'degr'`,
`'quot'`, `'mdfr'`, `'lowr'`, `'uppr'` and `'labl'` for the subgroup of the structure that names each.
The bond structure adds `'uplf'`, `'uprt'`, `'lwlf'` and `'lwrt'`, which the specification's group
type table omits.

| Substructure | Count | Holds |
| --- | --- | --- |
| `Bg` | 1 or more | One per line. The first child of the group must be a `Bg`. |
| equation structures | any | The content. |
| `X` | 0 or 1 | Required in a group of type `'anno'`, which attaches to an anchor. |

A group may be given an OpenDDL name, `Gr $main { ... }`, so that a connector can reference it.

`al` matters where the group is laid out in a box wider than its content, which is a fraction's
numerator or denominator, a matrix entry and an arrow's label. All three values are attested and 0 is
the Align Default the Group menu offers, which the context decides: measured 2026-09-13, a numerator
holding `x` over a denominator holding `abcd` rendered the same paths with no `al`, with `al=0` and
with `al='cent'`, and differently with `'left'` and with `'rght'`, so a fraction's default is centre.
An iteration's limits take their alignment from the context and from nothing else: `al='left'`,
`'cent'` and `'rght'` on a `'lowr'` or an `'uppr'` group each rendered exactly what no `al` rendered,
with the limits above and below and with `il` set, so the centring above and below and the left
alignment inline are the structure's own and cannot be overridden from a file.

`as` steps by one sixteenth. Decrease Size and Increase Size move the group holding the caret by a
sixteenth of its normal size and Reset Size restores it, which is where the values Radical Pie writes
come from: `0.9375` is fifteen sixteenths, one step down, `0.8125` thirteen sixteenths and `0.6875`
eleven sixteenths. Write a sixteenth rather than a round decimal so a group matches one the editor
would have made.

The scale and nudge properties belong to any group, a subgroup of a structure included. No fixture
writes a group of type 0 inside another group, so use the structure that owns the subgroup you want
rather than nesting a bare group.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb {s{"x"}}
	Sc
	{
		Gr (t='sups',ax=0.5)
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Bg (lg=20.0) {}
	Sb {s{"y"}}
}
```

### The label box

A caption on a term is an annotation group at file level, written after the main group and before the
foreground drawing structures. It attaches to the far end of the arrow that points at the term rather
than to the term itself, so the arrow's length sets the distance and no `ax` or `ay` nudge is needed:

```
Gr (as=0.8125,t='anno',al='cent')
{
	Bg {}
	Sb (pi=5,ro='text') {s{"Viscous"}}
	Bg {}
	Sb (pi=5,ro='text') {s{"Diffusion"}}
	X
	{
		ref{$arrow}
		u32{'anno'}
		i32{1}
	}
}
```

Captions on one rail collide when their arrows are closer together than the captions are wide, because
`al='cent'` spreads each caption both ways from its arrow. Radical Pie does not detect the overlap and
the validator cannot; only a rendering shows it. Three remedies, in the order to try them: send one of
the two arrows to the other rail (`'xxx!'` index 0 below instead of 1 above, leaving the arrow from the
term's `'cent'` anchor 0 or a rectangle's `'edge'` anchor 2 instead of 1); align the captions away from
each other, `al='rght'` on the left one so it extends leftwards from its arrow end and `al='left'` on the
right one; or use the site's Rendering equation's second row of rails (`'xxx!'` indexes 7 and 9). A
caption of one short word fits where two lines do not. Always render and look before shipping an
annotated equation.

`al='cent'` centres the caption on the arrow. Radical Pie's own annotated rendering equation writes
`al='rght'` instead on the two captions that hang off its outer rails; the specification enumerates no
values for `al`, so copy one of those two from a fixture rather than inventing a third. A second `Bg`
begins a second line of the caption, one `Bg` per line, and the words are `ro='text'`.
`as` scales the whole caption; `0.8125` is the value Radical Pie's annotated examples use, which sets
the caption below the size of the equation. `pi` on each symbol matches the caption to the colour of its
arrow.

An annotation holds anything the main group holds, so a caption is not restricted to text.
The site's Exomorphism equation labels the parts of a matrix with `Sb {s{"C"}}` under a `'subs'`
script and a `Br` around a bold `m`, and with `Sb (ro='func') {s{"det"}}` in front of that symbol; its
Gaussian Integral equation labels a substitution with the equation `s = −r²` written out as symbols
and a script. Write such a caption as the equation it is rather than as one `'text'` string, and it is
typeset like the equation it labels.

An arrow is not required. A caption hung on a highlight's or a panel's own `'anno'` anchor sits
against it with no stem at all, index 1 above and index 0 below, which is how the site's Amino Acid
equation labels the three groups of an amino acid. Use the arrow when
the term is inside the equation's line and the caption has to stand clear of it, and the bare
annotation when the thing labelled is a box drawn round the term.

Drawing objects and annotations attach to each other to any depth. A drawing structure can take its
anchors from structures named inside an annotation group, and a further annotation then hangs off that
drawing. The site's General Relativity equation is four deep: a line leaves the main group, an
annotation carrying a complete equation hangs on that line, three more lines take their anchors from
symbols named inside that annotation, and a caption hangs on each of them. Every group and structure
something later attaches to needs an OpenDDL name, an annotation group included.

An annotation group is itself a target for `'anno'` 0 and 1, so a caption takes a caption: name the
first one and hang the second on its underside or its top. The site's Circle equation, line 327,
hangs a smaller note (`as=0.875` against `0.9375`) under the caption named on line 316. Give the second one a
smaller `as` so it reads as a note on the first.

The equation grows to include the captions and the arrows: the SVG `viewBox` and the Word object size
follow, while the baseline shift stays that of the equation line.

## In — integral

An integral. The character is a data list, not a symbol, and it defaults to U+222B.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `sm` | bool | false | Small layout, for inline equations. |
| `il` | bool | false | Inline limits: place them to the right instead of above and below. |
| `kg` | bool | false | Keep the font's glyph instead of the shape Radical Pie synthesises. |
| `gr` | bool | false | Grow the sign past the highest and lowest points of the integrand. |

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr` | 1 | The integrand. Required. |
| `Gr (t='lowr')` | 0 or 1 | The lower limit. |
| `Gr (t='uppr')` | 0 or 1 | The upper limit. |

At most one `uint32` data list of one value: the Unicode value of the integral character. Leave it out
for U+222B; `references/TexSymbols.md` gives the value for each of `\iint`, `\oint` and the rest.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	In (il)
	{
		u32{0x222E}
		Gr
		{
			Bg {}
			Sb (st='bold') {s{"F"}}
			Sb (ro='oper') {s{"·"}}
			Sb (st='uprt') {s{"d"}}
			Sb (st='bold') {s{"r"}}
		}
		Gr (t='lowr')
		{
			Bg {}
			Sb {s{"C"}}
		}
	}
}
```

## It — iteration

A sum, product, or any other operator applied over an index set. The character is a data list and
defaults to U+2211. `It` is full size, with `lowr` and `uppr` stacked above and below the sign, unless
the caller asks for an inline-sized operator, which is what `sm` is for.

`It` is for the n-ary signs and for nothing else: the sum, the product, the integral, the big wedge and
vee, the union and the intersection. It draws whatever character it is given at that size, so an
ordinary binary operator with a limit tucked under it, `⩓` with a `k` beneath it, comes out as a
summation-sized glyph. That form is a stack; see the operator-with-a-limit part of the `St` section.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `sm` | bool | false | Small layout, for inline equations. |
| `il` | bool | false | Inline limits: place them to the right instead of above and below. |

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr` | 1 | The iterand. Required, and may be empty. |
| `Gr (t='lowr')` | 0 or 1 | The lower limit. |
| `Gr (t='uppr')` | 0 or 1 | The upper limit. |
| `Gr (t='mdfr')` | 0 or 1 | A modifier at the upper right of the sign, such as a prime or an asterisk. |

At most one `uint32` data list of one value: the Unicode value of the iteration character. Leave it out
for U+2211, and see `references/TexSymbols.md` for `\prod`, `\bigcup` and the rest.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	It
	{
		u32{0x220F}
		Gr
		{
			Bg {}
			Sb {s{"a"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb {s{"k"}}
				}
			}
		}
		Gr (t='lowr')
		{
			Bg {}
			Sb {s{"k"}}
			Sb (ro='rltn') {s{"="}}
			Sb (ro='nmbr') {s{"1"}}
		}
		Gr (t='uppr')
		{
			Bg {}
			Sb {s{"n"}}
		}
	}
}
```

## Jo — joist

A brace or bracket drawn as a drawing object, stretched between anchors.

| Property | Type | Default | Values |
| --- | --- | --- | --- |
| `t` | uint32 | `'brac'` | `'brac'` brace, `'brck'` square bracket, `'shel'` tortoise shell. |
| `os` | uint32 | 0 | Start offset: `0`, `'long'`, `'shrt'`. |
| `of` | uint32 | 0 | Finish offset: same values. |

| Substructure | Count |
| --- | --- |
| `X` | 1 |

A joist takes no endpoint symbol. Writing `es` or `ef` on one is refused by the validator, and Radical
Pie drops the property when it saves the file (measured 2026-09-12). The brace appears on the left of
the line from the first anchor to the second, so drawing it backwards mirrors it. It owns one `'jost'`
anchor at its middle and one `'anno'` anchor beyond that; index 1 of either crashes Radical Pie.

```pie
// Radical Pie Equation

D
{
}
Gr $main
{
	Bg {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"1"}}
}
Jo (s,t='brac')
{
	X
	{
		ref {$main,$main}
		u32{'bord','bord'}
		i32{0,1}
	}
}
```

## Kt — strike

A strike through one group, for cancelling a factor. `\cancel` is `'lwup'`, `\bcancel` is `'uplw'` and
`\xcancel` is `'exxx'`.

| Property | Type | Default | Values |
| --- | --- | --- | --- |
| `t` | uint32 | `'horz'` | `'horz'`, `'lwup'` lower left to upper right, `'uplw'` upper left to lower right, `'exxx'` both. |

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr` | 1 | The struck material. |

The group is required and there is one of it: a strike with no group and a strike with two both raise
the invalid-data dialog. A type outside the four draws the horizontal strike with no word.

Measured on the digits 48 at a 12 pt design, 2026-09-13. `'horz'` is a bar 0.52 pt thick lying on the
math axis, 2.81 pt above the baseline, and it runs 0.61 pt past the content at each end; the strike
costs 1.64 pt of width and no height. `'lwup'` and `'uplw'` run corner to corner of a box that stands
0.66 pt above the digits and 2.64 pt below the baseline, so a diagonal strike makes the line taller;
`'exxx'` draws both diagonals as one path.

The colour is the general equation property on the `Kt` itself: `co` and `pi` colour the stroke and
leave the struck expression in its own colour, which is how a cancellation is marked in red without
touching the digits. The thickness is a design value and not a property, `V (d='strk',n='rule')`, in
math units of 0.611 pt at a 12 pt design: 1.0 draws 0.611 pt, 2.0 draws 1.222 pt and 4.0 draws 2.444 pt
against the 0.52 pt default (measured 2026-09-13). `Kt (w=2)` is ignored and `Kt (w=2.0)` raises the
invalid-data dialog, as an unknown property does.

```pie
// Radical Pie Equation

D
{
	V (d='strk',n='rule') {f{2.0}}
}
Gr
{
	Bg {}
	Kt (t='lwup',co=0xFF0000FF)
	{
		Gr
		{
			Bg {}
			Sb {s{"x"}}
		}
	}
	Kt (t='exxx')
	{
		Gr
		{
			Bg {}
			Sb (ro='nmbr',tf) {s{"48"}}
		}
	}
}
```

## Ln — line

A line drawing object.

`'long'` runs an end past its anchor and `'shrt'` stops it short, on every line tool and on a joist.
Measured 2026-09-13 on a straight line between two anchors 12.8505 pt apart: `os` and `of` both
`'long'` made it 18.2053 pt long and both `'shrt'` made it 7.4957, which is 2.6774 pt at each end
either way, the `'line'` domain's `'lngo'` and `'shto'`. Use `'long'` to take an arrowhead clear of a
glyph it would otherwise touch and `'shrt'` to hold a line off one.

| Property | Type | Default | Values |
| --- | --- | --- | --- |
| `es` | uint32 | 0 | Start endpoint: `0`, `'sdcr'`, `'sdsq'`, `'wedg'`, `'arr1'`, `'arr2'`. |
| `ef` | uint32 | 0 | Finish endpoint: same values. |
| `os` | uint32 | 0 | Start offset: `0`, `'long'`, `'shrt'`. |
| `of` | uint32 | 0 | Finish offset: same values. |

| Substructure | Count |
| --- | --- |
| `X` | 1 |

```pie
// Radical Pie Equation

D
{
}
Gr $main
{
	Bg {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"1"}}
}
Ln (s,ef='arr2',of='long')
{
	X
	{
		ref {$main,$main}
		u32{'bord','bord'}
		i32{0,2}
	}
}
```

### The arrow-to-rail form

An annotation arrow runs from the term to a rail of the main group, `'xxx!'` index 1 above the equation
and index 0 below it. The rail snaps the line straight, so the arrow comes out vertical and every label
on the same side lines up. Give the first anchor to the term, the second to the rail:

- from a symbol, `u32{'cent','xxx!'} i32{1,1}` upwards or `i32{0,0}` downwards;
- from a highlight rectangle, `u32{'edge','xxx!'} i32{3,1}` from its top edge upwards or `i32{2,0}`
  from its bottom edge downwards.

The rail goes on the finish end. The Drawing Tools page says a drawing object starts on an anchor point
and only its finish end may attach to a rail, so both ends cannot be rails, and that is the order the
editor's tool produces. Radical Pie 1.15 is not strict about it: a line whose first anchor is a rail and
whose second is a symbol rendered the same line, and so did one whose two anchors were a horizontal rail
and a vertical rail (measured 2026-09-13). Write the term first all the same, because the rail holds its
position relative to the starting anchor and a rail at the start has no starting anchor to hold it to.

The arrowhead goes on the equation end, which is the start of the line, so it is `es`, not `ef`. Both
`es='arr1'` and `es='arr2'` are heads: the annotated equation Radical Pie's editor produced carries
`arr1`, and Radical Pie's own annotated examples carry `arr2`. Colour the line with `spi`, the stroke
palette index, and give the caption's symbols the same `pi` so the two match. Then attach the caption to
the far end of the arrow with `ref{$arrow} u32{'anno'} i32{1}`.

```pie
// Radical Pie Equation

D
{
}
Rt $box (f,fpi=9)
{
	X
	{
		ref{$plus,$end}
		u32{0,0}
		i32{1,0}
	}
}
Ln $arrow (s,spi=5,es='arr1')
{
	X
	{
		ref{$box,$main}
		u32{'edge','xxx!'}
		i32{3,1}
	}
}
Gr $main
{
	Bg {}
	Sb {s{"a"}}
	Sb $plus (ro='oper') {s{"+"}}
	Sb $end {s{"b"}}
}
Gr (as=0.8125,t='anno',al='cent')
{
	Bg {}
	Sb (pi=5,ro='text') {s{"second"}}
	Bg {}
	Sb (pi=5,ro='text') {s{"term"}}
	X
	{
		ref{$arrow}
		u32{'anno'}
		i32{1}
	}
}
```

A line needs both of its anchors; a single-anchor `Ln` crashes Radical Pie, and the validator refuses
it.

## M — map

Maps one symbol style to the fonts that draw it. A design carries at most one `M` per style, 22 in
all, one for each style listed under `Sb`. The specification's maximum of 21 is one short: a design
carrying all 22 maps survives a save by Radical Pie with every map intact, probed against the
executable.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `t` | uint32 | required | The style, one of the style values listed under `Sb`. |

One `uint8` data list of one to four font indexes. The first is the primary font of the style and the rest
are its fallbacks, tried in order for a character the primary does not hold. An index of 255 means no font
in that slot; 255 in the first slot crashes Radical Pie with an access violation, and the validator
refuses it.

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

## Mk — mark

An accent on a single character: hat, tilde, bar, dot, and the rest of the Unicode combining range
U+0300 to U+0362. A mark is a child of the `Sb` it applies to. Several marks on one symbol stack
outward in the order they are written. A mark applies to one character, so a symbol that carries one
holds one character.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `un` | bool | false | Draw the mark under the character instead of over it. |

One `uint32` data list of one value: the Unicode value of the mark character.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb {s{"a"} Mk {u32{0x302}}}
	Sb (ro='oper') {s{"+"}}
	Sb {s{"b"} Mk {u32{0x303}} Mk (un) {u32{0x323}}}
}
```

## Mx — matrix

A matrix of entry groups, up to 32 by 32. Entries are listed in row-major order: for a two by two
matrix the order is top left, top right, bottom left, bottom right. The specification says
column-major; a three-column matrix of the digits 1 to 6 rendered as 1 2 3 over 4 5 6, so the
executable wins. Brackets are not part of the matrix; wrap it in a `Br`.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `r` | int32 | required | Rows, 1 to 32. |
| `c` | int32 | required | Columns, 1 to 32. |
| `al` | uint32 | `'cent'` | Default entry alignment: `'cent'`, `'left'`, `'rght'`. An entry's own `al` overrides it. |
| `mb` | bool | false | Middle baseline: sit the matrix on its middle rather than on its last row. |
| `eh` | bool | false | Give every row the height of the tallest. |
| `ew` | bool | false | Give every column the width of the widest. |
| `rg` | bool | false | Half the row gap above the first row and below the last. |
| `cg` | bool | false | Half the column gap before the first column and after the last. |

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr` | `r` times `c` | One entry each, row-major. |

The specification gives the subgroup count a minimum of two; one of the operator's fixtures writes a
one by one matrix with a single group, so the validator's minimum is one and the rule that carries the
weight is that the number of groups equals `r` times `c`.

The matrix's `al` is the default for its entries and each entry may say otherwise, which is the Group
menu's alignment commands applied to one cell. Measured 2026-09-13 on a two by two matrix with
`al='left'`: the entry that carried `al='rght'` and the entry that carried `al='cent'` each rendered
its glyph in a different place from the entry that carried none, and the one with `al='cent'` matched
what the whole matrix drew at the default alignment. Set the matrix's `al` for the table and an
entry's own for the exception.

An entry of more than one line sits on its last baseline unless its own group says otherwise. The
choice is the entry group's `ba` property, `'frst'`, `'last'` or `'mddl'`, and no property of the
matrix carries it. Radical Pie writes `ba='mddl'` into every entry Insert Matrix creates, so a matrix
that came out of the editor carries it on every entry; it never writes `'last'`, which is the default,
and it drops an explicit one on the next save. Radical Pie opens a file with any other value in `ba`
and draws the default, so a fourth value is a silent no-op; the validator refuses one.

Measured on the matrix below, whose first entry holds two lines 16.5 pt apart: the single-line entry
beside it sits on the two-line entry's last baseline with no `ba`, 16.5 pt higher on its first baseline
with `'frst'`, and 9.08 pt above the last baseline with `'mddl'`. The alignment moves the entries
inside the row and leaves the size of the equation alone.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Mx (r=1,c=2)
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sb {s{"m"}}
			Bg {}
			Sb {s{"n"}}
		}
		Gr
		{
			Bg {}
			Sb {s{"a"}}
		}
	}
}
```

A picture grid, a matrix of coloured blocks and labels, is spaced by the design values and not by
spacers in its cells: `'rwgp'`, `'aspx'` and `'aspy'` in the `'mtrx'` domain, and `'vtgp'` in the
`'brck'` domain for the brackets around it. The `V` section has the values the site's own grids use and
a fence with all four.

A matrix owns four anchor types of its own beyond `'cell'`, the grid corners the `X` section's table
lists: `'orow'` and `'ocol'` sit past the grid's outer edge, clear of a bracket wrapped round it, one
pair per row or per column; `'mrow'` and `'mcol'` sit on the same row and column midlines measured
inside the grid instead, so the arrowhead lands on the bracket rather than clearing it.
`references/AnchorAtlas.md` measures every index of all four. Point a row-labelling or a
column-labelling arrow at a bracketed matrix from `'orow'` or `'ocol'`, never from `'mrow'` or `'mcol'`,
which would drive the head into the bracket. The site's Exomorphism equation labels the rows and
columns of its picture grid this way, running each arrow from the matrix's `'orow'` or `'ocol'` anchor
to rail 5 of the equation and hanging the caption on the arrow's far end, index 1, so the labels read
outward from the grid.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Mx (r=2,c=2,mb)
	{
		Gr
		{
			Bg {}
			Sb (ro='nmbr') {s{"1"}}
		}
		Gr
		{
			Bg {}
			Sb (ro='nmbr') {s{"0"}}
		}
		Gr
		{
			Bg {}
			Sb (ro='nmbr') {s{"0"}}
		}
		Gr
		{
			Bg {}
			Sb (ro='nmbr') {s{"1"}}
		}
	}
}
```

## Ng — negate

A negation stroke through a single symbol, the way `\notin` is drawn. A child of the `Sb` it applies
to.

| Property | Type | Default | Values |
| --- | --- | --- | --- |
| `t` | uint32 | `'frwd'` | `'frwd'`, `'bkwd'`, `'vert'` |

The stroke is cut to the symbol it crosses and takes no width of its own: `∈` measures 5.5913 pt with
the negation and without it, and the mark takes the box 2 pt below the baseline. It covers the first
character of the string alone, so a symbol holding a run of letters is struck over its first letter and
the rest stand clear; give each letter that takes a stroke an `Sb` of its own. Several `Ng` on one
symbol each draw. A type outside the three renders as `'frwd'` and is written back with no property at
all, so a misspelling is silent and the validator refuses it in the executable's place.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{"∈"} Ng {}}
	Sb (st='doub') {s{"ℚ"}}
	Sb (ro='pnct') {s{","}}
	Sb {s{"y"}}
	Sb (ro='rltn') {s{"∈"} Ng (t='bkwd') {}}
	Sb (st='doub') {s{"ℚ"}}
	Sb (ro='pnct') {s{","}}
	Sb {s{"z"}}
	Sb (ro='rltn') {s{"∈"} Ng (t='vert') {}}
	Sb (st='doub') {s{"ℚ"}}
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

## Ph — phantom

Material that takes up space and draws nothing, so that two parts of an equation come out the same
size. A phantom holds its content directly, beginning with a `Bg`, the way a group does; there is no
`Gr` in between. One of Radical Pie's own files shows the shape with the content removed, and another
is the same equation with the content visible.

The type says which extents are kept. Measured at the default design: a radical over `x` is 14.2083 by
12.00 points, a radical over `xy²` is 22.8962 by 17.00, and a radical over `x` followed by a default
phantom of `y²` is 14.2083 by 17.00, the visible radical's height at the plain radical's width. `'horz'`
is the other half of the same measurement, 22.8962 by 12.00. `'hzov'` and `'flov'` reserve the same box
as `'horz'` and `'full'` and let the following material lie over it, which is how a phantom sets a
minimum width rather than a width.

The reserved height shows only through what sizes itself to it, a radical, a bracket, or the next line
of the group, which a vertical phantom pushes down. Nothing else moves: an exported equation is as wide
as its phantoms make it and only as tall as its ink, so a `'vert'` phantom standing alone changes
neither the width nor the height of the file, and it does not even break the overlap two adjacent
italic letters get. Radical Pie renders a type outside the five as `'vert'` and reports nothing; the
validator refuses it.

A phantom also equalises a matrix cell against its sibling cells: in the middle array of the site's
Frenet equation, the cell holding `κ` follows it with `Ph { Bg {} Pr {} }`, an empty prime,
so that cell is exactly as wide as the cells beside it that carry a real prime. The arrows that fill
the other cells of that same matrix take `st='sym1'`.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `t` | uint32 | `'vert'` | `'vert'` vertical extent only, `'horz'` horizontal only, `'full'` both, `'hzov'` horizontal with the following material overlapping it, `'flov'` both with overlap. |

| Substructure | Count | Holds |
| --- | --- | --- |
| `Bg` | 1 or more | One per line, and the first child. |
| equation structures | any | The hidden content. |

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Rd
	{
		Gr
		{
			Bg {}
			Sb {s{"x"}}
			Ph
			{
				Bg {}
				Sb {s{"y"}}
				Sc
				{
					Gr (t='sups')
					{
						Bg {}
						Sb (ro='nmbr') {s{"2"}}
					}
				}
			}
		}
	}
}
```

## Pr — prime

Prime marks on the structure before it. Up to four primes merge into one `Pr`, and the character says
which kind.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `nb` | bool | false | Disable bold: keep the prime unbolded when the symbol is bold. |

At most one `uint32` data list of one value: the Unicode value of the prime character. Left out it is
U+2032, a single prime. U+2033 is a double prime, U+2034 a triple, U+2057 a quadruple, and U+2035 a
reversed prime.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb {s{"f"}}
	Pr {}
	Sb (ro='oper') {s{"+"}}
	Sb {s{"g"}}
	Pr {u32{0x2033}}
}
```

## Qe — quarter ellipse

A quarter ellipse drawing object.

It routes between its two anchors, leaving the first one horizontally, or vertically with `v`, and
meeting the second from the perpendicular direction. Reach for it only where a straight line would run
diagonally past the material it should avoid.

The specification lists `es`, `ef`, `os` and `of` under `Ln` alone. A quarter ellipse takes all four,
measured 2026-09-12, the same way a corner does.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `v` | bool | false | The vertical flag. |
| `es` | uint32 | 0 | Start endpoint: `0`, `'sdcr'`, `'sdsq'`, `'wedg'`, `'arr1'`, `'arr2'`. |
| `ef` | uint32 | 0 | Finish endpoint: same values. |
| `os` | uint32 | 0 | Start offset: `0`, `'long'`, `'shrt'`. |
| `of` | uint32 | 0 | Finish offset: same values. |

| Substructure | Count |
| --- | --- |
| `X` | 1 |

Its own anchors: `'line'` 0 at the first anchor, 1 at the second and 2 on the arc between them;
`'anno'` 0 and 1 beyond the two ends, 2 outside the arc and 3 inside it.

```pie
// Radical Pie Equation

D
{
}
Gr $main
{
	Bg {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"1"}}
}
Qe (s)
{
	X
	{
		ref {$main,$main}
		u32{'bord','bord'}
		i32{0,2}
	}
}
```

## Rd — radical

A radical: a surd over the radicand, with an optional degree above the hook.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `ns` | bool | false | Disable slant kerning between the surd and the radicand. |

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr` | 1 | The radicand. Required. |
| `Gr (t='degr')` | 0 or 1 | The degree. |

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Rd
	{
		Gr
		{
			Bg {}
			Sb {s{"x"}}
			Sb (ro='oper') {s{"+"}}
			Sb (ro='nmbr') {s{"1"}}
		}
		Gr (t='degr')
		{
			Bg {}
			Sb (ro='nmbr') {s{"3"}}
		}
	}
}
```

## Rr — rounded rectangle

A rounded rectangle drawing object. Its two anchors are opposite corners, and it takes the highlight
form described under [Rt](#rt--rectangle) unchanged: from index 1 of the structure that starts the run
to index 0 of the structure that ends it, filled, in the background layer. `r=1` is the radius Radical
Pie's own annotated rendering equation uses for every highlight, and Example 24 follows it; Example 23
uses square `Rt` boxes instead. Either is correct, so pick one and keep it for the whole equation.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `r` | uint8 | 0 | Radius index, 0 to 2. |

| Substructure | Count |
| --- | --- |
| `X` | 1 |

```pie
// Radical Pie Equation

D
{
}
Gr $main
{
	Bg {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"1"}}
}
Rr (s,r=1)
{
	X
	{
		ref {$main,$main}
		u32{'bord','bord'}
		i32{0,2}
	}
}
```

## Rt — rectangle

A rectangle drawing object. Its two anchors are opposite corners.

Opposite corners means the two must differ in both the horizontal and the vertical position, or the
shape has no area, which holds for `Rr` and `El` as well. The four anchors of one equation structure
all sit at the same horizontal position, so a shape between two of them is a hairline: take the corners
from two different structures, or from a structure and a group anchor. Radical Pie draws a shape whose
two anchors are one point as a path of zero size and reports nothing (measured 2026-09-13), so the
validator refuses the pair rather than let an invisible rectangle through.

No properties beyond the eight every drawing structure has.

| Substructure | Count |
| --- | --- |
| `X` | 1 |

```pie
// Radical Pie Equation

D
{
}
Gr $main
{
	Bg {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"1"}}
}
Rt (s,f,fpi=8)
{
	X
	{
		ref {$main,$main}
		u32{'bord','bord'}
		i32{0,2}
	}
}
```

### The highlight form

A filled rectangle behind a run of the equation is how a term is picked out. Draw it from index 1 of the
structure that starts the run, above that structure's right end, to index 0 of the structure that ends
it, below that structure's right end; the two are opposite corners, so the box spans the run. The start
is the `Bg` of the line or of an inline group when the whole run is to be covered, and the operator
symbol in front of the term when it is not. Write the rectangle in the background layer, before the main group, so
the fill sits behind the glyphs, and give it `f` with an `fpi` palette index instead of a stroke. Put a
`Sp (s=1.5) {}` beside the run when the box needs breathing room, typically inside a bracket, because
the rectangle takes no padding of its own.

```pie
// Radical Pie Equation

D
{
}
Rt (f,fpi=9)
{
	X
	{
		ref{$plus,$end}
		u32{0,0}
		i32{1,0}
	}
}
Gr $main
{
	Bg {}
	Sb {s{"a"}}
	Sb $plus (ro='oper') {s{"+"}}
	Sb $end {s{"b"}}
}
```

## Sb — symbol

One or more adjacent characters that share a role and a style. The role drives spacing and behaviour;
the style drives the glyphs. Everything visible that is not a structure is an `Sb`.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `ro` | uint32 | `'math'` | The role, below. |
| `st` | uint32 | 0 | The style, below. 0 means the default style of the role. |
| `pf` | bool | false | Proportional figures: digits keep their natural widths. |
| `tf` | bool | false | Strict tabular figures: digits share a width and no space is trimmed. |
| `sc` | bool | false | Small caps substitution. |
| `cf` | bool | false | Capital punctuation forms. |
| `zr` | bool | false | Slashed zero. |
| `nd` | bool | false | Disable dotless i and j under a mark. |
| `ns` | bool | false | Disable the italic correction that shifts a mark. |
| `nb` | bool | false | Disable the bold form of a mark on a bold symbol. |
| `ma` | bool | false | Shift the math axis for capitals: raise the symbol to centre it between capitals. |

`ma` is not in the specification's property table. One of Radical Pie's own files writes it,
and the Symbols page of the documentation describes the setting.

Any Unicode character is legal in the string, the planes above the basic multilingual one included, so
an emoji is a symbol like any other. The site's own logo equation sets U+1F967, a slice of pie, under a
radical as `Sb (st='uprt') {s{"🥧"}}`, and its Sun-Earth equation writes the astronomical
signs U+2609 and U+1F728 the same way. Write the character itself in UTF-8, since the format has no
escape, and give a pictographic character `st='uprt'` as those two do rather than leaving it to the
italic default of the `'math'` role.

`pf` and `tf` are the only way a file asks for a digit width. Proportional figures came first, in
version 1.7, "a new option ... that enables proportional figures if they're available in the font";
version 1.15 added the third choice, strict tabular width, and the Symbol properties dialog that offers
the three together, which is what `tf` writes. With neither, digits share one width and the space before the first
and after the last digit of a run is trimmed, which keeps a number tight against what surrounds it.
`pf` gives each digit its natural width, as one of Radical Pie's own files does on the `"11"`
of a numerator. `tf` keeps the shared width and trims nothing, as another does on the same number.
Set one only for a caller who asks for figures to line up or to sit naturally; the default suits an
equation.

Roles:

| Role | For |
| --- | --- |
| `'math'` | A variable, or anything mathematical with no better role. Default style italic. |
| `'nmbr'` | A literal number. |
| `'oper'` | A binary operator. Default style `'sym1'`. |
| `'rltn'` | A binary relation. Default style `'sym1'`. |
| `'unry'` | `∂` and `∇` only. Default style `'sym1'`. Every other unary sign, a leading minus included, is `'oper'`. |
| `'func'` | A standard function name such as sin or log: upright, with 3 mu on each side. |
| `'pnct'` | Punctuation: no space in front of it, 3 mu behind it. |
| `'elps'` | An ellipsis. |
| `'text'` | Running prose. The math fonts, upright by default, with the operator spacing dropped. |
| `'chem'` | A chemical element: upright, with space after a preceding number or variable. |
| `'unit'` | A physical unit. |
| `'arrw'` | An arrow character. Default style `'sym1'`. |
| `'bond'` | A chemical bond character, U+EE30 to U+EE3B below. Default style `'sym1'`. |

`'chem'` is the role the editor gives every Roman letter typed in chemistry mode. The letters stand
upright as element symbols, and space is added before an element name when the symbol in front of it has
the role `'nmbr'` or `'math'`, so a coefficient needs no `Sp` after it:
the site's Photosynthesis equation writes `Sb (ro='nmbr') {s{"6"}}` directly in front of
`Sb (ro='chem') {s{"CO"}}`. The auto subscripting of version 1.15 is an editor convenience with nothing
of its own in the file. What it inserts after an element is an ordinary `Sc` holding a `'subs'` group,
which is what that equation writes after every element and what its FDG equation writes after
`s{"CH"}`. One `Sb` holds as many letters as share the role, `s{"OH"}` among them.

`'bond'` is the role of a bond drawn inside running chemistry, where the bond is a character and not a
`Bd` structure. The Radical font puts twelve of them in the private use area, and they are the
characters to use: U+EE30 single, U+EE31 double, U+EE32 triple, U+EE33 quadruple, U+EE34 partial
single, U+EE35 and U+EE36 the two partial doubles, U+EE37 to U+EE39 the three partial triples, U+EE3A
long single and U+EE3B long double. They are not in Unicode, so write the code point itself in the
UTF-8 string. Two of them draw what nothing else in the format draws: no `Bd` bond type is quadruple,
and the partial forms are dashed. Their distinguishing feature is where they sit: measured 2026-09-13
at the default design and 11 pt, the bar of U+EE30 is centred 3.6416 pt above the baseline, exactly half
the 7.2832 pt capital height of the `H` beside it, while an em dash in the same place sits at 2.7560 pt,
the math axis. So `H—OH` written with an em dash draws its bond 0.886 pt too low, and the long single
bond U+EE3A is 7.5 pt of bond against the em dash's 5.4.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='chem') {s{"H"}}
	Sb (ro='bond') {s{""}}
	Sb (ro='chem') {s{"O"}}
	Sb (ro='bond') {s{""}}
	Sb (ro='chem') {s{"H"}}
	Sb (ro='oper') {s{"+"}}
	Sb (ro='chem') {s{"N"}}
	Sb (ro='bond') {s{""}}
	Sb (ro='chem') {s{"N"}}
	Sb (ro='oper') {s{"+"}}
	Sb (ro='chem') {s{"Re"}}
	Sb (ro='bond') {s{""}}
	Sb (ro='chem') {s{"Re"}}
}
```

`'func'` marks a standard function name and puts 3 mu, 1.8333 pt at the default design, on each side of
it. The space is the `'symb'` domain's `'fnsp'`, whose factory value is those 3 mu: measured
2026-09-13, `V (d='symb',n='fnsp') {f{0.0}}` took `sin x` from 19.5526 to 17.7192 pt and `{f{9.0}}` took
it to 23.2192. The editor
recognises hundreds of names as they are typed, `sin` and `log` among them, and lets a user define more;
none of that reaches the file, where the role is the whole of the feature. Write `ro='func'` on any name
that should behave as a function, a name the editor would not recognise included, and put its letters in
one `Sb`.

Text mode is the `'text'` role, which sets a sentence of prose inside an equation. It draws from the
same fonts as `'math'`: with no `st` it is the upright style, glyph for glyph the render `st='uprt'`
gives, and `ro='text',st='ital'` renders identically to a plain `Sb`, so a letter mentioned inside a
sentence may be written either way. What the role changes is spacing. A binary operator whose left
neighbour carries `ro='text'` loses the 4 mu it takes on each side: `a + b` measures 21.3102 pt with
upright `'math'` letters and 16.4213 pt with `'text'` letters. A `'rltn'` keeps its space either way,
and so does a `'func'`. Words are separated by spaces written inside the string, which every role
keeps, leading, internal and trailing, 2.7500 pt each at the default design. So a prose fragment is one
`Sb` holding `" is a prime number that does not divide "`, and no `Sp` stands between its words.

`'pnct'` takes no space in front of it and 3 mu behind it when a symbol follows, and nothing behind it
at the end of a line. It also drops the half math unit of italic correction that an upright glyph gets
after a math italic: a full stop after an italic `a` measures 8.2500 pt as `'pnct'` and 8.5556 pt as
`st='uprt'`. Use it for a comma inside a sentence, where the 3 mu is the space after the comma, and
leave the closing full stop of a prose equation as `st='uprt'`, which is what the site's own theorem
and convergence statements do.

Styles: `'uprt'` upright, `'ital'` italic, `'bold'`, `'bitl'` bold italic, `'mono'` monospace,
`'grek'` Greek upright, `'itgk'` Greek italic, `'bdgk'` Greek bold, `'bigk'` Greek bold italic,
`'sym1'` and `'sym2'` the two symbol styles, `'nary'` the iteration style, `'gral'` the integral
style, `'scpt'` script, `'bdsc'` bold script, `'frkt'` fraktur, `'bdfk'` bold fraktur, `'doub'`
double-struck, `'sans'` sans-serif upright, `'itsn'` sans-serif italic, `'dbsn'` sans-serif bold,
`'bisn'` sans-serif bold italic.

The default style is `'ital'` for `'math'`, `'sym1'` for the five symbol roles `'oper'`, `'rltn'`,
`'unry'`, `'arrw'` and `'bond'`, and `'uprt'` for the other seven. Measured 2026-09-13, three characters
against every role: a full stop, a capital A and a zero each rendered under each role with no `st` and
then under `st='sym1'`, `'uprt'` and `'ital'`, and the glyph and the advance width of the bare render
matched one of the three every time. The specification gives `'uprt'` for every role but `'math'`,
`'oper'` and `'rltn'`, which is wrong about the other three. Write `st` only to override the default: `Sb (st='bold')` for a bold vector, `Sb (st='doub')` for
a double-struck set, `Sb (st='itgk')` for a small Greek letter, `Sb (st='grek')` for a capital Greek
letter. No role defaults to `'sym2'`: it is a second symbol style with no automatic assignment, so treat
it as free for a caller to assign directly wherever a symbol needs to be told apart from the `'sym1'`
ones.

| Substructure | Count | Holds |
| --- | --- | --- |
| `string` | 1 | The characters. Must not be empty. |
| `Mk` | any | Marks on the character. |
| `Ng` | any | Negation strokes. |
| `Sl` | any | Slashes. |
| `En` | 0 or 1 | An enclosure. |

Several `Mk` on one symbol stack outward in the order they are written, each one clear of the one before
it, upward for a mark over the character and downward for a mark with `un`. In
`Sb {s{"b"} Mk {u32{0x303}} Mk (un) {u32{0x323}}}` the tilde sits over the b and the dot under it; two
`Mk` without `un` put one accent above the other. A symbol that carries a mark carries one character, so
a run of letters splits into one `Sb` for each letter that takes an accent.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='nmbr') {s{"2"}}
	Sb {s{"xy"}}
	Sb (ro='oper') {s{"+"}}
	Sb (ro='func') {s{"cos"}}
	Sb (st='itgk') {s{"θ"}}
	Sb (ro='rltn') {s{"="}}
	Sb (st='grek') {s{"Λ"}}
	Sb (ro='pnct') {s{"."}}
	Bg {}
	Sb (ro='text',st='bold',sc) {s{"Lemma"}}
	Sb (ro='text',st='bold') {s{"."}}
	Sb (ro='text') {s{" For every "}}
	Sb (ro='text',st='ital') {s{"n"}}
	Sb (ro='pnct') {s{","}}
	Sb {s{"n"}}
	Sb (ro='oper') {s{"+"}}
	Sb (ro='nmbr') {s{"1"}}
	Sb (ro='rltn') {s{">"}}
	Sb {s{"n"}}
	Sb (st='uprt') {s{"."}}
}
```

## Sc — script

A subscript, a superscript, or both stacked on each other. The script attaches to the structure before
it, or to the one after it when `pr` is set.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `pr` | bool | false | Preceding script: apply to the structure on the right. |
| `ow` | bool | false | Align the scripts outward, matching the edge away from the symbol. |
| `ns` | bool | false | Disable italic kerning, which otherwise pulls a subscript left. |

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr (t='subs')` | 0 or 1 | The subscript. |
| `Gr (t='sups')` | 0 or 1 | The superscript. |

At least one of the two must be present. To set one script to the right of another instead of stacking
them, put a zero-width space between the two script structures.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb {s{"x"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb {s{"i"}}
		}
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sc (pr)
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='nmbr') {s{"14"}}
		}
	}
	Sb (ro='chem') {s{"C"}}
}
```

## Sl — slash

A slash through a single symbol. A child of the `Sb` it applies to.

| Property | Type | Default | Values |
| --- | --- | --- | --- |
| `t` | uint32 | `'frwd'` | `'frwd'`, `'bkwd'` |

The slash is one fixed size whatever it crosses, 4.83 by 11.72 pt at the default design over an upright
`D` and over an n-ary sum alike, and it takes no width. That is what separates it from `Ng`, whose
stroke is cut to the symbol: over the same `D` the negation runs 6.45 by 10.36 pt. A slash reaches 4 pt
below the baseline and a negation 2. `'vert'` belongs to `Ng` and not here; Radical Pie renders it, and
any other value, as `'frwd'` and writes the structure back with no property at all. A symbol may carry
a slash and a negation together, and each draws.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (st='uprt') {s{"D"} Sl {}}
	Sb (ro='pnct') {s{","}}
	Sb (st='uprt') {s{"D"} Sl (t='bkwd') {}}
}
```

## Sp — space

A space, or a kern when the width is negative. Widths are in math units, 18 to the em, and one math
unit is the design font size divided by eighteen. The default design sets 11 point type, so a math unit
is 0.6111 points there and 18 mu is 11.00 points.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `s` | float | 0.0 | Width in math units. |
| `t` | bool | false | Tabular space: a repeating tab stop rather than a width. |

The TeX widths are 3 mu for `\,`, 4 mu for `\>` and `\:`, 5 mu for `\;`, −3 mu for `\!`, 18 mu for
`\quad` and 36 mu for `\qquad`, and they render 1.8333, 2.4444, 3.0556, −1.8333, 11.0000 and 22.0000
points at the default design. An ordinary word space is 4.5 mu.

Nothing clamps the width. The Insert Space dialog stops at 72 mu and at a kern of −18 mu, and the file
format does not: `Sp (s=100.0)` renders a 61.1111 point gap and `Sp (s=-30.0)` an 18.3333 point kern.
A zero-width space is not a no-op, because it drops the overlap two adjacent italic letters get, which
moves the second letter 0.8593 points to the right at the default design.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb {s{"f"}}
	Br
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sb {s{"x"}}
		}
	}
	Sp (s=18.0) {}
	Sb (ro='text') {s{"for"}}
	Sp (s=3.0) {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{">"}}
	Sb (ro='nmbr') {s{"0"}}
}
```

### The tab

`Sp (t)` is the tab, and with the flag set `s` stops being a width and becomes a stop interval. The
material after the tab starts at the smallest multiple of `s` that lies past the pen, counted from the
start of the line in the group holding the tab. At the default design `Sp (t,s=27.0)` after one letter
puts the next symbol at 16.5000 points, and after three letters, which already reach past that stop, at
33.0000 points. A tab at the start of a line advances a whole stop, and a tab whose pen sits exactly on
a stop advances to the next one, so three tabs of 9 mu in a row step 5.5000, 11.0000 and 16.5000
points. With no `s`, or with `s` zero or negative, the stop is 17.996 points at the default design and
scales with the font size.

Give a tab the column position in math units and every row whose content stops short of it lands on the
same x, which is how the tabbed table in `references/Examples.md` is set. A row that runs past the
position lands on the next multiple and that row alone falls out of register, which is the difference
from an aligner: a tab holds
a grid it was given, an aligner fits the column to the widest line. A tab inside a subgroup counts from
that subgroup's own line origin, and a tab inside an aligner column is laid out before the aligner
moves the run, so the two together leave the stop somewhere other than a multiple of `s`.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb {s{"x"}}
	Sp (t,s=36.0) {}
	Sb (ro='nmbr') {s{"1"}}
	Bg {}
	Sb {s{"y"}}
	Sp (t,s=36.0) {}
	Sb (ro='nmbr') {s{"2"}}
}
```

## St — stack

A full-size expression with a small label above it, below it, or both. This is how `\lim`, `\max` and
an operator with a condition under it are written.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `sm` | bool | false | Tight layout: pull the labels in and set them smaller. |

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr` | 1 | The main expression. Required. |
| `Gr (t='lowr')` | 0 or 1 | The label below. |
| `Gr (t='uppr')` | 0 or 1 | The label above. |

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	St
	{
		Gr
		{
			Bg {}
			Sb (ro='func') {s{"max"}}
		}
		Gr (t='lowr')
		{
			Bg {}
			Sb {s{"i"}}
		}
	}
	Sb {s{"a"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb {s{"i"}}
		}
	}
}
```

### An operator with a limit under it

`\underset{k}{\circ}` and `\mathop{\circ}\limits_k` are a `St` whose main group holds the operator and
whose `'lowr'` group holds the limit. The operator keeps its own size, which is what separates this
from `It`: an `It` draws its character at n-ary size whatever the character is. The example is the
barred wedge of a geometric algebra paper, `⩓` U+2A53 with a subscript index under it.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (st='bold') {s{"a"}}
	St
	{
		Gr
		{
			Bg {}
			Sb (ro='oper') {s{"⩓"}}
		}
		Gr (t='lowr')
		{
			Bg {}
			Sb {s{"k"}}
		}
	}
	Sb (st='bold') {s{"b"}}
}
```

### The inline group

A stack with neither label, `St { Gr (ba='mddl') { Bg {} ... } }`, is the editor's inline group. It adds
no glyph and no spacing, and everything inside it keeps its own anchors, so it exists to give a
connector something to point at. Two uses:

- **A symbol the arrow points at.** Wrap the symbol, name it, and take its `'cent'` anchor, index 1 for
  an arrow that leaves upwards and index 0 for one that leaves downwards. This is the form the editor
  produces when a term is labelled without a highlight, and it is the whole of the mark-up for that
  term: no rectangle, no spacing change.
- **A run that needs a left anchor.** A symbol's type `0` anchors sit at its right end, so a highlight
  that starts at the first symbol of a run cuts that symbol off. Wrap the run and name the inline
  group's `Bg`, `St { Gr { Bg $bgTerm {} Sb {s{"L"}} ... } }`, then start the rectangle at `$bgTerm`
  index 1. The same wrap gives a bracket standing on its own a left anchor.

The example below wraps the `p` of a gradient so that a vertical arrow can leave the symbol's centre for
the rail above the equation.

```pie
// Radical Pie Equation

D
{
}
Ln $arrow (s,es='arr1')
{
	X
	{
		ref{$p,$main}
		u32{'cent','xxx!'}
		i32{1,1}
	}
}
Gr $main
{
	Bg {}
	Sb (ro='oper') {s{"−"}}
	Sb (ro='unry',st='sym1') {s{"∇"}}
	St
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sb $p {s{"p"}}
		}
	}
}
```

### Cancellation with a replacement

`\cancelto{2}{4}`, and `\cancel{4}` on its own, strike the digit with `Kt (t='lwup')` and put the
replacement directly under or over it as an `St`: the `St`'s main `Gr` holds the `Kt`-wrapped digit, and
its `Gr (t='lowr')` or `Gr (t='uppr')` holds the smaller replacement digit. The strike and its
replacement usually share one colour, given with `pi` on each symbol. The example cross-cancels before
multiplying, 3/4 times 2/5, striking the 4 with a small 2 below it and the 2 with a small 1 above it,
which is why the answer comes out 3/10 rather than 6/20.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Fr
	{
		Gr (t='numr')
		{
			Bg {}
			Sb (ro='nmbr') {s{"3"}}
		}
		Gr (t='dnom')
		{
			Bg {}
			St
			{
				Gr
				{
					Bg {}
					Kt (t='lwup')
					{
						Gr
						{
							Bg {}
							Sb (ro='nmbr',pi=5) {s{"4"}}
						}
					}
				}
				Gr (t='lowr')
				{
					Bg {}
					Sb (ro='nmbr',pi=5) {s{"2"}}
				}
			}
		}
	}
	Sb (ro='oper') {s{"·"}}
	Fr
	{
		Gr (t='numr')
		{
			Bg {}
			St
			{
				Gr
				{
					Bg {}
					Kt (t='lwup')
					{
						Gr
						{
							Bg {}
							Sb (ro='nmbr',pi=7) {s{"2"}}
						}
					}
				}
				Gr (t='uppr')
				{
					Bg {}
					Sb (ro='nmbr',pi=7) {s{"1"}}
				}
			}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb (ro='nmbr') {s{"5"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Fr
	{
		Gr (t='numr')
		{
			Bg {}
			Sb (ro='nmbr') {s{"3"}}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb (ro='nmbr') {s{"10"}}
		}
	}
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
value as a float data list inside it, and the validator accepts one data list of any type.

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
| `'rdcl'` | `'rsc1'` | 0.1 to 8 | The scale of the radical glyph; the logo writes 1.2. |
| `'bond'` | `'wgap'` | 0.01 to 2 | The gap between the strokes of a double bond; the site's FDG writes 0.09471. |
| `'bond'` | `'hlln'` | 0.25 to 4 | The halved bond length; FDG writes 2.0. |
| `'bond'` | `'dlln'` | 0.25 to 4 | The doubled bond length; FDG writes 2.5. |
| `'symb'` | `'fnsp'` | 0 to 18 | The space on each side of a standard function name. The factory value is 3 mu. |
| `'line'` | `'lngo'` | 0.01 to 2 | How far a `'long'` end overshoots its anchor, 2.6774 pt at the factory design. |
| `'line'` | `'shto'` | 0.01 to 2 | How far a `'shrt'` end undershoots it, the same 2.6774 pt. |

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

## Wm — widemark

A mark that stretches over or under a whole group: a bar, a hat, an arrow, a brace. Unlike `Mk` it
applies to an expression rather than to one character, and it can carry a label outside it, which is
how `\overbrace{...}^{n}` is written.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `t` | uint32 | `'line'` | The mark, below. |
| `un` | bool | false | Draw it under the expression instead of over it. |
| `sm` | bool | false | Tight layout: move the mark inward where there is room. |

The types are `'line'` a horizontal line, `'dlin'` a double line, `'what'` a hat, `'chck'` a check,
`'smil'` a smile, `'frwn'` a frown, `'tild'` a tilde, `'brck'` a bracket, `'brac'` a brace, `'shel'` a
tortoise shell, `'larw'`, `'rarw'` and `'barw'` arrows, and `'luhp'`, `'ruhp'`, `'buhp'`, `'ldhp'`,
`'rdhp'` and `'bdhp'` harpoons. All nineteen draw a shape of their own. A mark takes no width, and the
height it adds over a single letter at the default design runs from 2 pt for `'line'`, through 3 pt for
the double line and the six harpoons, 4 pt for the hat, the check, the smile, the frown, the tilde and
the three arrows, 5 pt for the bracket and the shell, to 7 pt for the brace.

A type the list does not hold renders as `'barw'`, the two-headed arrow, and Radical Pie keeps the
unknown value in the file it writes back, which is the one place a wrong four-letter name survives a
save. The validator refuses it.

Eight characters are widemarks rather than characters. Typed in MATH or CHEM mode each one creates the
structure below instead of inserting a glyph, which release 1.2 added, so a caller who hands over
`x⏞` means a `Wm`. Rendered side by side on 2026-09-13, each character's own glyph is the shape its
structure draws:

| Character | Structure |
| --- | --- |
| U+23B4 top square bracket | `Wm (t='brck')` |
| U+23B5 bottom square bracket | `Wm (t='brck',un)` |
| U+23DC top parenthesis | `Wm (t='frwn')` |
| U+23DD bottom parenthesis | `Wm (t='smil',un)` |
| U+23DE top curly bracket | `Wm (t='brac')` |
| U+23DF bottom curly bracket | `Wm (t='brac',un)` |
| U+23E0 top tortoise shell bracket | `Wm (t='shel')` |
| U+23E1 bottom tortoise shell bracket | `Wm (t='shel',un)` |

`sm` lowers the mark onto the content where the content leaves room. Over `xy`, whose letters have no
ascender, it takes a hat from 15 to 13 pt of total height, a tilde to 12, a brace from 18 to 16 and a
line from 13 to 11; over content with an ascender it changes those four not at all, and the tilde is
drawn from a narrower shape either way. `un` puts the mark under the content and leaves the box the
same size, moving the baseline shift of a braced letter from 1 to 8 pt.

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr` | 1 | The material under the mark. Required. |
| `Gr (t='labl')` | 0 or 1 | The label outside the mark. |

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Wm (t='line')
	{
		Gr
		{
			Bg {}
			Sb {s{"z"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Wm (t='rarw')
	{
		Gr
		{
			Bg {}
			Sb {s{"v"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Wm (t='what',sm)
	{
		Gr
		{
			Bg {}
			Sb {s{"xy"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Wm (t='brac',un)
	{
		Gr
		{
			Bg {}
			Sb {s{"w"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Wm (t='brac')
	{
		Gr
		{
			Bg {}
			Sb {s{"a"}}
			Sb (ro='oper') {s{"+"}}
			Sb {s{"b"}}
		}
		Gr (t='labl')
		{
			Bg {}
			Sb {s{"n"}}
		}
	}
}
```

## X — connector

Attaches a drawing structure, or an annotation group, to the anchor or anchors that place it. A drawing
structure's connector holds two anchors, one per end of a line, joist, zigzag, corner or quarter
ellipse, or one per opposite corner of a rectangle, rounded rectangle or ellipse; giving it a single
anchor crashes Radical Pie with an access violation, so every drawing example in this catalogue writes
two. An annotation group's connector holds one anchor, because an annotation is placed against the one
thing it labels.

No properties.

| Substructure | Count | Holds |
| --- | --- | --- |
| `ref` | 1 list | The node or nodes that carry the anchor, one name per anchor, by OpenDDL name. |
| `uint32` | 1 list | The anchor types, one per anchor. |
| `int32` | 1 list | The anchor indexes, one per anchor. |
| `float` | 0 or 1 list | Relative offsets, for a rail anchor. |

The specification's minimum and maximum of one for the `ref`, `uint32` and `int32` substructures count
the lists, not the values inside them: a drawing connector's three lists each hold two values, a
one-anchor annotation connector's each hold one.

Anything a connector points at needs an OpenDDL name, so name the pieces you mean to label as you write
them: `Bg $bgTerm {}`, `Sb $p {s{"p"}}`, `Gr $main { ... }`. Radical Pie 1.15 opened, rendered and wrote
back every two-anchor drawing shape in this catalogue unchanged apart from node renaming; on save it
renames every node to `$_0`, `$_1` and so on in the order they appear, so the names an author writes,
`$main` and the rest of this catalogue's names among them, are free, and a file the program wrote has no
readable names left.

### Anchor types

The anchor types are `0` the main anchor, `'cent'` the centre, `'axis'` the math axis and `'lmnl'` the
liminal anchor of a top-level group, `'xxx!'` and `'yyy!'` its horizontal and vertical rails, `'bord'`
its border, `'mtrx'`, `'cell'`, `'mrow'`, `'mcol'`, `'orow'`, `'ocol'`, `'lrow'` and `'lcol'` the
anchors of a matrix, `'line'` the own anchor of a line, corner, zigzag or quarter ellipse, which the
specification gives to line structures alone and 2026-09-12 measured on all four, `'edge'` the edge of a rectangle, rounded rectangle
or ellipse, `'jost'` a joist's anchor, and `'anno'` the annotation anchor of a drawing structure or of
an annotation group, a target type only.

A bond structure adds seven more that the specification's anchor table does not list: `'bond'` boxes
the whole site and `'bdup'`, `'bdur'`, `'bdul'`, `'bdlw'`, `'bdll'` and `'bdlr'` box its `'uppr'`,
`'uprt'`, `'uplf'`, `'lowr'`, `'lwlf'` and `'lwrt'` neighbour groups one at a time. They are how the
chemistry files panel a substituent; `references/Chemistry.md` has the section and the fence.

Three equation structures carry no anchor a drawing can reach. The specification's table gives the main
anchor to every structure in the equation category except a group, an aligner and a phantom, and the
centre anchor to every one except a group, a begin, an aligner and a phantom. So an `Al` and a `Ph` own
nothing at all and cannot be pointed at, and a `Bg` owns the four main anchors of the line it begins and
no centre. Point at the symbol beside the aligner or inside the phantom instead.

A four-letter anchor type the structure does not own crashes Radical Pie with an access violation
rather than raising the invalid-data dialog. The validator refuses a type the referenced structure does
not own and an index past the last anchor of a type, and its error names the types that structure does
own, so write only the names above.

An annotation group's one anchor takes `'bord'`, `'lmnl'` or `0` on a named structure when it hangs off
the equation itself, and `'anno'` when it hangs off a drawing object or another annotation, which is the
usual case: a label belongs to the arrow that points at the term. Putting `'anno'` on the main group's
own connector crashes Radical Pie.

### Anchor indexes, measured

Measured in Radical Pie 1.15; `references/AnchorAtlas.md` has every type and index with its position, including the matrix, group, rail, line and annotation anchors, and the crash index that ends each range (nothing wraps). The forms below are drawn from the operator's annotated Navier-Stokes equation,
which the program itself wrote, the operator's annotated Rendering equation, and the site's own
Rendering example.

| Type | On | Index | Where it sits |
| --- | --- | --- | --- |
| `0` | any named equation structure | 0 | below its right end, the near row |
| `0` | | 1 | above its right end, the near row |
| `0` | | 2 | below its right end, the far row (top-level groups only) |
| `0` | | 3 | above its right end, the far row (top-level groups only) |
| `'cent'` | a symbol or structure | 0 to 3 | the same four rows at its horizontal centre |
| `'edge'` | a rectangle, rounded rectangle or ellipse | 2 | its bottom edge |
| `'edge'` | | 3 | its top edge |
| `'axis'` | the main group | 0 and 1 | the left and the right end of the first line's math axis |
| `'axis'` | | 2 and 3, 4 and 5 | the same two ends of the second line, the third, and so on down |
| `'xxx!'` | the main group | 0 | the horizontal rail below the equation |
| `'xxx!'` | the main group | 1 | the horizontal rail above it |
| `'anno'` | an annotation group | 0 | its underside |
| `'anno'` | an annotation group | 1 | its top |
| `'anno'` | a line | 1 | its far end, the end away from the equation |
| `'anno'` | a rectangle, rounded rectangle or ellipse | 0 to 4 | below it, above it, left, right, over its centre |
| `'anno'` | a corner or a zigzag | 0 to 7 | beyond its two ends, then a pair beside each leg |
| `'anno'` | a quarter ellipse | 0 to 3 | beyond its two ends, outside the arc, inside it |
| `'anno'` | a joist | 0 | the only one |
| `'line'` | a line, corner, zigzag or quarter ellipse | 0 to 2 | its first anchor, its second, and the turn or middle |
| `'jost'` | a joist | 0 | its middle |
| `'bond'` and its six siblings | a bond site | 0 to 3 | the corners of the box: bottom-left, bottom-right, top-left, top-right |

A structure nested inside a subgroup exposes only indexes 0 and 1 of type `0`; index 2 or 3 on a nested
structure crashes Radical Pie instead of raising an error, and the validator reads the nesting and
refuses it. A bond site is the exception: nested or not, every one of its
seven types keeps all four indexes. Index 2 or 3 of `'anno'` on an annotation group crashes; on a
drawing object the annotation anchor runs to 4, which is what the site's Exomorphism equation, written
by Radical Pie, uses to put a caption over a filled rectangle. `Bg` is a structure and carries the anchors of the
line it begins, which is how a highlight comes to cover a whole numerator or a whole bracketed run: name
the `Bg` and take its index 1.

Indexes above 1 on `'xxx!'` are further rails. The site's own Rendering example sends two
arrows up to indexes 7 and 9 to hang a second row of labels clear of the first, and sets `al='rght'` on
those two labels so they read outwards.

`'axis'` is the type that counts lines. A group of one line has two axis anchors, a group of three has
six, measured on a three-line group in `references/AnchorAtlas.md`: 0 and 1 are the left and right end
of the first line, 2 and 3 of the second, 4 and 5 of the third, and 6 crashes. The rails are not per
line. `'xxx!'` runs above and below the whole group and `'yyy!'` to its left and right at the group's
middle height, at the same indexes as on a one-line group. Since a rail takes the coordinate of the
anchor it is paired with, a line from `'axis'` 5 to `'yyy!'` 7 comes out horizontal at the height of the
third line and reaches the fourth rail on the right, which is how a note is put beside one line of a
multi-line equation. A top-level group has no `'cent'` anchor at all; index 0 of it crashes.

A rail anchor snaps the line straight. A line with one end on `'xxx!'` takes the horizontal position of
its other anchor, so an arrow from a term to a rail comes out exactly vertical; that is the form to
reach for, rather than a slanted line from a nudged label.

The example below is an annotation: a second equation attached to the main group's border, one anchor.

```pie
// Radical Pie Equation

D
{
}
Gr $main
{
	Bg {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"1"}}
}
Gr (t='anno')
{
	Bg {}
	Sb (ro='text') {s{"the root"}}
	X
	{
		ref {$main}
		u32{'bord'}
		i32{0}
	}
}
```

### A note beside one line of a multi-line equation

Both ends of the line name the main group: `'axis'` at the index of the line to be annotated, and a
`'yyy!'` rail for the other end, which takes the axis anchor's height and so comes out horizontal beside
that line. The caption hangs on the line's `'anno'` 1 as usual. The site's Gaussian-integral page draws
exactly this, `Ln (s,w=2,spi=10,es='wedg')` from `'axis'` 5 to `'yyy!'` 7 of a three-line group, with the
substitution it used written at the rail. A farther rail index moves the note further out.

```pie
// Radical Pie Equation

D
{
}
Ln $note (s,w=2,spi=10,es='wedg')
{
	X
	{
		ref{$main,$main}
		u32{'axis','yyy!'}
		i32{3,3}
	}
}
Gr $main
{
	Bg {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{"="}}
	Sb {s{"a"}}
	Bg {}
	Sb {s{"y"}}
	Sb (ro='rltn') {s{"="}}
	Sb {s{"b"}}
	Bg {}
	Sb {s{"z"}}
	Sb (ro='rltn') {s{"="}}
	Sb {s{"c"}}
}
Gr (as=0.6875,t='anno',al='cent')
{
	Bg {}
	Sb (pi=10,ro='text') {s{"the middle line"}}
	X
	{
		ref{$note}
		u32{'anno'}
		i32{1}
	}
}
```

### Arrows that meet, and arrows that fan out

The `float` list holds one value per anchor, in points, and the value on a rail anchor slides that end
along the rail while the other end stays where it is; the offset tables of `references/AnchorAtlas.md`
measure the movement. Two jobs use it.

Two arrows meet under one caption when each carries the offset that brings its rail end to the same
point, and the caption hangs on one of the two arrows. The site's ortho-xylene drawing labels both
methyl groups from one label between them, `f{0.0,11.42}` on one arrow and `f{0.0,-17.97}` on the other.
Arrows fan out when the terms stand closer together than their captions are wide: the site's field
equation leans two of its arrows away from their terms with `f{0.0,-20.95}` and `f{0.0,15.23}` and sends
the third straight up to a farther rail. Captions that belong to one side of the line stay on that side:
spread them along the rail, send one to a farther rail or lean the arrows outward, and do not alternate
them above and below the line. Work the numbers out from where the two ends sit, positive to the right,
and look at the rendering.

```pie
// Radical Pie Equation

D
{
}
Ln $left (s,spi=5,es='arr2')
{
	X
	{
		ref{$first,$main}
		u32{'cent','xxx!'}
		i32{1,3}
		f{0.0,16.224}
	}
}
Ln (s,spi=5,es='arr2')
{
	X
	{
		ref{$third,$main}
		u32{'cent','xxx!'}
		i32{1,3}
		f{0.0,-16.224}
	}
}
Gr $main
{
	Bg {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{"="}}
	Sb $first {s{"a"}}
	Sb (ro='oper') {s{"+"}}
	Sb {s{"b"}}
	Sb (ro='oper') {s{"+"}}
	Sb $third {s{"c"}}
}
Gr (as=0.6875,t='anno',al='cent')
{
	Bg {}
	Sb (pi=5,ro='text') {s{"the outer terms"}}
	X
	{
		ref{$left}
		u32{'anno'}
		i32{1}
	}
}
```

### A drawn rail over a span

A run of terms is labelled as a whole by drawing the rail rather than pointing at any one term. A thick
line, `Ln (s,w=4,spi=9)`, runs between the type `0` anchor 3 of the structure that begins the run and
anchor 3 of the one that ends it, the far row above the right end of each. A second line of the same
weight rises from that line's own `'line'` anchor 2, its midpoint, to one of the equation's `'xxx!'`
rails, and the caption hangs on the second line's `'anno'` 1. The result reads as a brace over the span
with a stem to the label, which is how the site's circle equation labels its terms.

```pie
// Radical Pie Equation

D
{
}
Ln $rail (s,w=4,spi=9)
{
	X
	{
		ref{$rel,$third}
		u32{0,0}
		i32{3,3}
	}
}
Ln $stem (s,w=4,spi=9)
{
	X
	{
		ref{$rail,$main}
		u32{'line','xxx!'}
		i32{2,3}
	}
}
Gr $main
{
	Bg {}
	Sb {s{"x"}}
	Sb $rel (ro='rltn') {s{"="}}
	Sb {s{"a"}}
	Sb (ro='oper') {s{"+"}}
	Sb {s{"b"}}
	Sb (ro='oper') {s{"+"}}
	Sb $third {s{"c"}}
}
Gr (as=0.6875,t='anno',al='cent')
{
	Bg {}
	Sb (pi=9,ro='text') {s{"the whole sum"}}
	X
	{
		ref{$stem}
		u32{'anno'}
		i32{1}
	}
}
```

## Zg — zigzag

A zigzag drawing object, dominantly horizontal, or dominantly vertical with `v`.

Radical Pie draws it as three straight legs, horizontal then vertical then horizontal, so it is a Z
route between its two anchors and no kind of wave. It has no amplitude property and no count property:
`Zg` takes `v` and the four line properties and nothing else, measured 2026-09-12. A wavy line is
written as a run of `Wm (t='tild')` widemarks instead, one per hump.

The specification lists `es`, `ef`, `os` and `of` under `Ln` alone. A zigzag takes all four, measured
2026-09-12, the head lying along the leg it sits on.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `v` | bool | false | The vertical flag. |
| `es` | uint32 | 0 | Start endpoint: `0`, `'sdcr'`, `'sdsq'`, `'wedg'`, `'arr1'`, `'arr2'`. |
| `ef` | uint32 | 0 | Finish endpoint: same values. |
| `os` | uint32 | 0 | Start offset: `0`, `'long'`, `'shrt'`. |
| `of` | uint32 | 0 | Finish offset: same values. |

| Substructure | Count |
| --- | --- |
| `X` | 1 |

Its own anchors: `'line'` 0 at the first anchor, 1 at the second and 2 at the middle of the second leg;
`'anno'` 0 and 1 beyond the two ends, 2 and 3 either side of the second leg, 4 and 5 either side of the
first and 6 and 7 either side of the third.

```pie
// Radical Pie Equation

D
{
}
Gr $main
{
	Bg {}
	Sb {s{"x"}}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"1"}}
}
Zg (s)
{
	X
	{
		ref {$main,$main}
		u32{'bord','bord'}
		i32{0,1}
	}
}
```

## Feynman diagrams

A Feynman diagram is a drawing on an invisible grid, not a structure of its own: an `Mx` holds the
grid, `Ln` draws each fermion, a run of `Wm (t='tild')` or a `Zg` draws each boson, and annotation
groups hold the particle labels.

Build the grid first, one `Mx (r,c,eh,ew)` in the main group, `eh` and `ew` so every row and column
takes the size of its widest content. Leave every cell an empty group, `Gr { Bg {} }`; a matrix of
empty cells still has a full grid of corner, row and column anchors (`references/AnchorAtlas.md`), so nothing
inside a cell has to draw for the grid to exist. `V (d='mtrx',n='rwgp') {f{<points>}}` in the design
sets the row pitch and `V (d='mtrx',n='clgp') {f{<points>}}` the column gap, which is how the legs of
the diagram are spaced apart without a spacer symbol in every cell; put a `Sp` in one cell instead
where only that row or column needs to be wider, the way the vertex below widens its middle row to
clear the wavy line. Every leg of the diagram then runs corner to corner, or corner to the grid's
`'mrow'` or `'mcol'` anchors, so the vertices land exactly on the grid regardless of what each cell
draws. `'rwgp'` and `'clgp'` both range 0 to 18, as the `V` table gives; the validator refuses a value
above that.

A fermion is a `Ln` between two grid anchors, with an endpoint symbol at whichever end carries the
arrow: `es='arr2'` at the first anchor the `X` lists or `ef='arr2'` at the second. Order the two
anchors so the arrowhead lands where the physics puts it: the vertex end for a particle entering the
diagram, the far end for one leaving it, whichever of `es` or `ef` that turns out to be.

A photon is a wave, not a `Wm` on its own: a run of six `Wm (t='tild')` widemarks, each holding a group
with one `Sp (s=9.0) {}` and nothing else, makes one continuous wave about as long as the fermion legs
either side of it. Hold the run in an annotation group, `Gr (t='anno',al='left',ay=-8.0)`, attached by
its `X` to the vertex anchor the wave leaves from; `al='left'` starts the wave at that anchor instead of
centring it, and the negative `ay` nudges the whole annotation down by that many math units, which lines
the wave's own baseline up with the vertex height instead of the annotation's default position above it.
Where a diagram wants a step in the line instead of a smooth wave, `Zg`
gives one: it is a three-leg Z route between two anchors and not a wave, so use it for a boson drawn as
a zigzag rather than the tilde run. A scalar is a dashed `Ln`, `Ln (s,d=2)` between the same two kinds
of grid anchors a fermion uses, with no endpoint arrow unless the diagram gives the scalar a direction.

A vertex is nowhere drawn; it is the grid corner or row anchor that two or more legs share, `'cell'` for
a corner of the grid and `'mrow'` or `'mcol'` for the centre of a row or column, so three legs meeting
at one vertex all name the same anchor in their `X`.

Label each leg with an annotation group on its own `'anno'` anchors rather than nudging a symbol into
place: a straight leg (`Ln`, `Cn`, `Zg`, `Qe`) carries `'anno'` 0 beyond its start and 1 beyond its
finish, and the run of `Wm` widemarks that makes a photon is itself a named node, so a caption can hang
off the last widemark's own `0`/`1` anchors the way it hangs off any symbol. Give the caption
`as=0.8125` to set it below the size of the equation, as every other label in this catalogue does.

```pie
// Radical Pie Equation

D
{
	V (d='mtrx',n='rwgp') {f{18.0}}
}
Ln $ein (s,ef='arr2')
{
	X
	{
		ref{$grid,$grid}
		u32{'cell','mrow'}
		i32{6,3}
	}
}
Ln $eout (s,ef='arr2')
{
	X
	{
		ref{$grid,$grid}
		u32{'mrow','cell'}
		i32{3,0}
	}
}
Gr $main
{
	Bg {}
	Mx $grid (r=3,c=1,eh,ew)
	{
		Gr
		{
			Bg {}
			Sp (s=42.0) {}
		}
		Gr
		{
			Bg {}
		}
		Gr
		{
			Bg {}
		}
	}
}
Gr (t='anno',al='left',ay=-8.0)
{
	Bg {}
	Wm (t='tild')
	{
		Gr
		{
			Bg {}
			Sp (s=9.0) {}
		}
	}
	Wm (t='tild')
	{
		Gr
		{
			Bg {}
			Sp (s=9.0) {}
		}
	}
	Wm (t='tild')
	{
		Gr
		{
			Bg {}
			Sp (s=9.0) {}
		}
	}
	Wm (t='tild')
	{
		Gr
		{
			Bg {}
			Sp (s=9.0) {}
		}
	}
	Wm (t='tild')
	{
		Gr
		{
			Bg {}
			Sp (s=9.0) {}
		}
	}
	Wm $photon (t='tild')
	{
		Gr
		{
			Bg {}
			Sp (s=9.0) {}
		}
	}
	X
	{
		ref{$grid}
		u32{'mrow'}
		i32{3}
	}
}
Gr (as=0.8125,t='anno',al='cent')
{
	Bg {}
	Sb {s{"e"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='oper') {s{"−"}}
		}
	}
	X
	{
		ref{$ein}
		u32{'anno'}
		i32{0}
	}
}
Gr (as=0.8125,t='anno',al='cent')
{
	Bg {}
	Sb {s{"e"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='oper') {s{"−"}}
		}
	}
	X
	{
		ref{$eout}
		u32{'anno'}
		i32{1}
	}
}
Gr (as=0.8125,t='anno',al='cent')
{
	Bg {}
	Sb (st='grek') {s{"γ"}}
	X
	{
		ref{$photon}
		u32{0}
		i32{1}
	}
}
```

A QED vertex: an electron in at the grid's bottom-left corner (`'cell'` 6), an electron out at the
top-left corner (`'cell'` 0), both meeting at the right edge of the grid's middle row (`'mrow'` 3), and
a photon leaving that same vertex. The grid is one column of three rows so `'cell'` numbers the four
corners of each row pair in order, top row first; the top cell carries the `Sp (s=42.0)` that sets the
one column's width, which `ew` then holds for every row, opening enough room beside the middle row for
the six-widemark wave, and the other two cells stay empty so the two electron legs have somewhere to
start and finish. Both `Ln` structures take `ef='arr2'`, but `$ein` lists the vertex
second so its arrowhead sits at the vertex, the incoming electron flowing into it, while `$eout` lists
the vertex first so its arrowhead sits at the far corner, the outgoing electron flowing away from the
vertex it leaves. This is `Skill/RadicalPie/references/examples/FeynmanVertex.pie`, Example 33 of
`references/Examples.md`.

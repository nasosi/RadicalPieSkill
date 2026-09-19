# Groups

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

On a derivation whose continuation lines carry no left-hand side, the aligner goes after the relation. A
relation takes its leading space only when something stands before it on the line, so a line that opens
with its aligner and then its relation loses that space and its sign sits 2.643 pt left of the first
line's at the default design. Rendered 2026-09-19 on the three lines of `examples/AlignedDerivation.pie`:
with the aligner in front of each relation the equals signs stood at 36.572, 33.929 and 33.929 pt, and
with the aligner after each relation all three stood at 36.572 pt. The site's own Gaussian integral
derivation is written the second way and renders its three equals signs at 64.959 pt.

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
replacement directly under or over it as an `St`: the `St`'s main `Gr` holds the `Kt`-wrapped digit,
and its `Gr (t='lowr')` or `Gr (t='uppr')` holds the smaller replacement digit. The strike and its
replacement usually share one colour, `pi` on the `Kt` for the stroke and `pi` on the replacement
symbol, which leaves the struck digit in the body colour. The example cross-cancels before
multiplying, 6/5 times 7/9, striking the 6 with a small 2 above it and the 9 with a small 3 below
it, which is why the answer comes out 14/15 rather than 42/45.

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
			St
			{
				Gr
				{
					Bg {}
					Kt (t='lwup',pi=5)
					{
						Gr
						{
							Bg {}
							Sb (ro='nmbr') {s{"6"}}
						}
					}
				}
				Gr (t='uppr')
				{
					Bg {}
					Sb (ro='nmbr',pi=5) {s{"2"}}
				}
			}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb (ro='nmbr') {s{"5"}}
		}
	}
	Sb (ro='oper') {s{"·"}}
	Fr
	{
		Gr (t='numr')
		{
			Bg {}
			Sb (ro='nmbr') {s{"7"}}
		}
		Gr (t='dnom')
		{
			Bg {}
			St
			{
				Gr
				{
					Bg {}
					Kt (t='lwup',pi=6)
					{
						Gr
						{
							Bg {}
							Sb (ro='nmbr') {s{"9"}}
						}
					}
				}
				Gr (t='lowr')
				{
					Bg {}
					Sb (ro='nmbr',pi=6) {s{"3"}}
				}
			}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Fr
	{
		Gr (t='numr')
		{
			Bg {}
			Sb (ro='nmbr') {s{"14"}}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb (ro='nmbr') {s{"15"}}
		}
	}
}
```

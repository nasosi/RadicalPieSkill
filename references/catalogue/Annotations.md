# Annotations

Three forms an annotated equation needs sit with their own structures: the label box under `Gr` and the
inline group under `St` in `references/catalogue/Groups.md`, and the arrow-to-rail form under `Ln` in
`references/catalogue/Drawings.md`.

## X — connector

Attaches a drawing structure, or an annotation group, to the anchor or anchors that place it. A drawing
structure's connector holds two anchors, one per end of a line, joist, zigzag, corner or quarter
ellipse, or one per opposite corner of a rectangle, rounded rectangle or ellipse; giving it a single
anchor crashes Radical Pie with an access violation, so every drawing example in this catalogue writes
two. An annotation group's connector holds one anchor, because an annotation is placed against the one
thing it labels. Those two are the only places an `X` belongs: one written into an ordinary group
crashes Radical Pie the same way, and the validator refuses it.

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
readable names left. No two may be the same: a repeated name raises the invalid-data dialog on open,
and the validator refuses it.

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
| `0` | | 2 | below its right end, the far row (not on a structure nested inside a subgroup) |
| `0` | | 3 | above its right end, the far row (not on a structure nested inside a subgroup) |
| `'cent'` | a symbol or structure | 0 to 3 | the same four rows at its horizontal centre (2 and 3 not on a structure nested inside a subgroup) |
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

A structure nested inside a subgroup exposes only indexes 0 and 1, of type `0` and of `'cent'` alike;
index 2 or 3 of either on a nested structure crashes Radical Pie instead of raising an error, and the
validator reads the nesting and refuses it. A bond site is the exception: nested or not, every one of
its seven types keeps all four indexes. Index 2 or 3 of `'anno'` on an annotation group crashes; on a
drawing object the annotation anchor runs to 4, which is what the site's Exomorphism equation, written
by Radical Pie, uses to put a caption over a filled rectangle. `Bg` is a structure and carries the anchors of the
line it begins, which is how a highlight comes to cover a whole numerator or a whole bracketed run: name
the `Bg` and take its index 1.

Indexes above 1 on `'xxx!'` are further rails. The site's own Rendering example sends two
arrows up to indexes 7 and 9 to hang a second row of labels clear of the first, and sets `al='rght'` on
those two labels so they read outwards.

An annotation group is a top-level group, so it owns `'xxx!'` and `'yyy!'` rails of its own and not only
the main group's. That is how a chain of callouts is built: an arrow from a symbol inside the annotation
to rail 1 of that same annotation group, with its caption on the arrow's far end, index 1 of `'anno'`.
Rendered 2026-09-15 on a two-line general relativity equation, where the definition hanging over the
main equation carries three such arrows, one of them to its own rail 7, and every caption stands clear.

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

## Feynman diagrams

A Feynman diagram is a drawing on an invisible grid, not a structure of its own: an `Mx` holds the
grid, `Ln` draws each fermion, a run of `Wm (t='tild')` or a `Zg` draws each boson, and annotation
groups hold the particle labels.

Build the grid first, one `Mx (r,c,eh,ew)` in the main group, `eh` and `ew` so every row and column
takes the size of its widest content. Leave every cell an empty group, `Gr { Bg {} }`; a matrix of
empty cells still has a full grid of corner, row and column anchors (`references/AnchorAtlas.md`),
so nothing inside a cell has to draw for the grid to exist. `V (d='mtrx',n='rwgp')` in the design
sets the row pitch and `V (d='mtrx',n='clgp')` the column gap, each a float data list of math units,
which is how the legs of the diagram are spaced apart without a spacer symbol in every cell;
put a `Sp` in one cell instead where only that row or column needs to be wider, the way the vertex
below widens its middle row to clear the wavy line. Every leg of the diagram then runs corner to
corner, or corner to the grid's `'mrow'` or `'mcol'` anchors, so the vertices land exactly on the
grid regardless of what each cell draws. `'rwgp'` and `'clgp'` both range 0 to 18, as the `V` table
of `references/catalogue/Design.md` gives; the validator refuses a value above that.

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

Label each leg with an annotation group on its own `'anno'` anchors rather than nudging a symbol
into place: a straight leg (`Ln`, `Cn`, `Zg`, `Qe`) carries `'anno'` 0 beyond its start and 1 beyond
its finish, and the run of `Wm` widemarks that makes a photon is itself a named node, so a caption
can hang off the last widemark's own `0`/`1` anchors the way it hangs off any symbol. Give the
caption `as=0.8125` to set it below the size of the equation, as every other label in this catalogue
does. A particle name is upright whatever its case, which is why the photon below is `Sb (st='grek')
{s{"γ"}}` rather than the `st='itgk'` a small Greek letter takes everywhere else.

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
			Sb (ro='unry') {s{"−"}}
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
			Sb (ro='unry') {s{"−"}}
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
top-left corner (`'cell'` 0), both meeting at the right edge of the grid's middle row (`'mrow'` 3),
and a photon leaving that same vertex. The grid is one column of three rows so `'cell'` numbers the
four corners of each row pair in order, top row first; the top cell carries the `Sp (s=42.0)` that
sets the one column's width, which `ew` then holds for every row, opening enough room beside the
middle row for the six-widemark wave, and the other two cells stay empty so the two electron legs
have somewhere to start and finish. Both `Ln` structures take `ef='arr2'`, but `$ein` lists the
vertex second so its arrowhead sits at the vertex, the incoming electron flowing into it, while
`$eout` lists the vertex first so its arrowhead sits at the far corner, the outgoing electron
flowing away from the vertex it leaves. This is `references/examples/FeynmanVertex.pie`, Example 33
of `references/Examples.md`.

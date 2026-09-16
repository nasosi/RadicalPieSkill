# Drawings

## Cn — corner

A corner drawing object: one horizontal leg and one vertical one, horizontal first, or vertical first
with `v`. Drawing structures sit outside the main equation, before it for the background layer and
after it for the foreground layer, and each attaches to two anchors through its connector, one per end
of the corner; see `X` in `references/catalogue/Annotations.md`
for the rule and the reason a single anchor crashes Radical Pie.

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

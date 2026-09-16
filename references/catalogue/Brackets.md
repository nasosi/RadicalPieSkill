# Brackets

## Br — bracket

A bracket pair around one or more groups, stretched to the height of what it holds. Parentheses,
square brackets, braces, angle brackets, absolute value bars and norm bars are all `Br`.

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `as` | bool | false | Asymmetric vertical extent: centre on the content, not on the math axis. |
| `ca` | bool | false | With `as`, shift the assembly so the bracket's own centre sits on the math axis. |

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
rendered the same paths at 17 pt tall, `Br (as)` 13 pt and `Br (as,ca)` 14 pt. Write `ca` on a
bracket that already carries `as`, where it moves the whole assembly down until the bracket's own
centre lands on the math axis: measured 2026-09-14 round `x²`, the bracket's centre matched the axis
to five decimals and the content's centre stood 0.57 pt below it.

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

Measured on the digits 48 at the factory 11 pt design, 2026-09-13. The border is 0.52 pt thick and
stands 3.06 pt clear of the content on the left and the right and about 4.1 pt above and below, and
the structure keeps 1.22 pt outside the border on each side, so a box turns an 11 by 9 pt expression
into a 20.04 by 18 pt one. A two-sided box reserves the same space as a four-sided one, which is
what keeps a column of boxed lines in line. There is no padding property. A value of `t` outside the
five draws the four-sided box with no word, and no box draws one side alone, so `\overline` is a
`Wm`.

Two design values change the box, both measured on 2026-09-13. `V (d='boxx',n='rule')` is the border
thickness in math units, 0.611 pt each at the factory 11 pt design, so 2.0 draws a 1.22 pt border
against the 0.52 pt default. `V (d='boxx',n='vtsp')` is the space above and below the content: 12.0
puts the top border 15.14 pt above the baseline where the default puts it at 12.08, and 6.0 pulls it
in to 11.47. Neither name is in the documentation, and no name was found for the space to the left
and the right; `'hzgp'`, `'hzsp'`, `'hzpd'`, `'hpad'`, `'pdng'`, `'marg'`, `'clrn'` and nine more
render unchanged, which is what a value name a domain does not have does.

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

The enclosure is a fixed size and does not grow with what it encloses. Measured on 2026-09-13, it is
a 9.32 pt square stroked 0.52 pt at the factory 11 pt design, whatever the symbol: a W, 10.15 pt
wide, pokes out on both sides, a √ stands well above and below it, and on a symbol holding several
characters it encloses the first one and the rest run out to the right. It follows the size of its
surroundings rather than its content, 6.06 pt across in a superscript and 20.34 pt at a 24 pt
design, and it centres on the first character's ink. Enclose one character; for a whole expression
use a `Bx`.

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

Measured on the digits 48 at the factory 11 pt design, 2026-09-13. `'horz'` is a bar 0.52 pt thick
lying on the math axis, 2.81 pt above the baseline, and it runs 0.61 pt past the content at each
end; the strike costs 1.64 pt of width and no height. `'lwup'` and `'uplw'` run corner to corner of
a box that stands 0.66 pt above the digits and 2.64 pt below the baseline, so a diagonal strike
makes the line taller; `'exxx'` draws both diagonals as one path.

The colour is the general equation property on the `Kt` itself: `co` and `pi` colour the stroke and
leave the struck expression in its own colour, which is how a cancellation is marked in red without
touching the digits. The thickness is a design value and not a property, `V (d='strk',n='rule')`, in
math units of 0.611 pt at the factory 11 pt design: 1.0 draws 0.611 pt, 2.0 draws 1.222 pt and 4.0
draws 2.444 pt against the 0.52 pt default (measured 2026-09-13). `Kt (w=2)` is ignored and
`Kt (w=2.0)` raises the invalid-data dialog, as an unknown property does.

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

# Arrows

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

With no label an arrow is 16.5 points long at the factory 11 point design, and every length in this
section scales with the design font size: under a 12 point design the same arrow is 18 points long.
With a label it is the label's own width plus 11 points of shaft at each end, and the
wider of the two labels sets it: labels 8.10, 21.60, 59.26 and 88.35 points wide gave arrows 30.10,
43.60, 81.26 and 110.35 points long. A short arrow is 5.5 points shorter than that at each end that
is free, so under one 43.60 point label the `'long'` arrow runs the whole width, the `'left'` arrow
stops 5.5 points before the right end and the `'rght'` arrow starts 5.5 points in.

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

A label with no `al` is centred over the shaft, which is what a catalyst or a condition wants, so
the `al='cent'` the chemistry examples write changes nothing: measured 2026-09-14, a label written
both ways renders at the same x to four decimals. `al='left'` and `al='rght'` push the label to the
ends of the stretched width, which is how two labels on one arrow are read apart.

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

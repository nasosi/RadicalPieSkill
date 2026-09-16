# Symbols

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
| `'unry'` | `∂`, `∇` and a charge or sign that hangs on a symbol. Default style `'sym1'`. A leading minus in front of an expression is `'oper'`. |
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

Those 3 mu are not always enough to part the name from a `'math'` letter written straight after it.
Measured 2026-09-15: `Sb (ro='func') {s{"mod"}}` with `Sb {s{"p"}}` after it renders `modp`, the ink of
the two 0.593 pt apart, because the italic `p` leans back 1.241 pt into the space the role reserves;
`sin x` in the same position stands 1.495 pt apart and reads as two words. Write `Sp (s=3.0) {}` between
a function name and a letter that follows it directly, which sets the gap to the full 1.8333 pt and took
`mod p` from 26.8895 to 28.1302 pt, the width it has when the letter comes first and the role's leading
space does the work.

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

The fence writes all three full stops, one per case: `ro='pnct'` ends the math line, the bold
`'text'` stop belongs to the word Lemma inside the running text, and the `st='uprt'` stop closes the
prose equation.

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

At least one of the two must be present. Two `Sc` written in a row already sit side by side and do
not stack: measured 2026-09-14 at the factory design, the second's superscript starts exactly where
the first's subscript ends. What stacks one over the other is a single `Sc` holding both groups.
Between two scripts `Sp (s=0.0) {}` adds nothing and a symbol holding U+200B adds 1.2222 pt, so a
gap that is wanted is an `Sp` with a width.

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

Nothing clamps the width. The Insert Space dialog stops at 72 mu and at a kern of −18 mu, and the
file format does not: `Sp (s=100.0)` renders a 61.1111 point gap and `Sp (s=-30.0)` an 18.3333 point
kern. A zero-width space is not always a no-op, because it drops the kern two adjacent italic
letters get, and that kern is the pair's own. Measured at the default design, `f` then `j` moved
3.9961 points, `f` then `a` 2.1270, `x` then `y` 0.8593, `P` then `a` 0.1128, and `v` then `a` and
`a` then `b` not at all.

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

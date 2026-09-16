# Fractions

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

Measured on 2026-09-13 at the factory 11 pt design. The division sign is one path, the hook and the
vinculum together: it reaches 1.93 pt below the baseline, 2.56 pt above the digits, and 0.61 pt past
the right end of the dividend, and it costs 3.86 pt of width. The quotient is right-aligned over the
dividend, always: a one-digit quotient over a four-digit dividend sits over the last digit, and `al`
on the quotient group changes nothing. Whichever of the two is wider sets the length of the
vinculum.

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

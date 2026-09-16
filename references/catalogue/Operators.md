# Operators

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
summation-sized glyph. That form is a stack; see the operator-with-a-limit part of the `St` section
of `references/catalogue/Groups.md`.

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

An empty iterand is legal and reserves a character-wide blank slot beside the sign, so a sum written
with an empty `Gr` and the material after the `It` comes out with a gap after the sign. Put the material
that follows the sign inside the iterand instead: measured 2026-09-15, a Σ over `γm` was 25.9018 pt wide
with the two letters in the iterand and 32.8872 pt with them written after an empty one, and the same
move took a whole ten by ten inertia tensor from 406.02 to 398.557 pt.

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

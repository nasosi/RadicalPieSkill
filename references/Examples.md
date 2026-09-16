# Worked Examples

Thirty-seven equations, easiest first. Each one gives the LaTeX or a description, the complete `.pie`
file, and the decisions that matter in it.

Example 2 is a file Radical Pie itself saved; read it for what the program's own output looks like,
and Example 23 for what it does to the node names in an annotated one. Every example from 8 on is a
file under `references/examples/`, and each one passes the validator. Examples 6, 21, 25 to 32 and 34
are chemistry; `references/Chemistry.md` is the method behind them.

```
python scripts/Validate.py references/examples/QuadraticFormula.pie
```

## 1. A single symbol

`\ne`, on its own.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='rltn') {s{"≠"}}
}
```

The smallest useful file: header line, empty design, one group, the `Bg` that begins its first line,
one symbol. The not-equal sign is one code point, U+2260, and it takes `ro='rltn'` so that Radical Pie
puts relation spacing around it. A bare `Sb {s{"≠"}}` would fall to the `'math'` role and be spaced
as a variable.

## 2. A number and a fraction, with a saved design

`25\frac{x}{2}`, the file Radical Pie itself wrote for it.

```pie
// Radical Pie Equation

D
{
	F (i=8) {s{"NewCM10-Book"}}
	F (i=9) {s{"NewCM10-BookItalic"}}
	F (i=10) {s{"NewCM10-Bold"}}
	F (i=11) {s{"NewCM10-BoldItalic"}}
	F (i=12) {s{"NewCMMath-RadicalPieGreek-Book"}}
	F (i=13) {s{"NewCMMath-RadicalPieGreek-Bold"}}
	F (i=14) {s{"NewCMMath-Book"}}
	F (i=15) {s{"NewCMMath-Bold"}}
	M (t='uprt') {u8{8,0,1,7}}
	M (t='ital') {u8{9,0,2,7}}
	M (t='bold') {u8{10,0,3,7}}
	M (t='bitl') {u8{11,0,4,7}}
	M (t='grek') {u8{8,1,7,5}}
	M (t='itgk') {u8{12,2,7,5}}
	M (t='bdgk') {u8{10,3,7,5}}
	M (t='bigk') {u8{13,4,7,5}}
	M (t='sym1') {u8{14,0,5,7}}
	M (t='sym2') {u8{14,0,5,7}}
	M (t='nary') {u8{14,0,1,5}}
	M (t='gral') {u8{14,0,1,5}}
	M (t='scpt') {u8{14,6,255,255}}
	M (t='bdsc') {u8{15,6,255,255}}
	M (t='frkt') {u8{14,6,255,255}}
	M (t='bdfk') {u8{15,6,255,255}}
	M (t='doub') {u8{14,6,255,255}}
	M (t='sans') {u8{14,6,255,255}}
	M (t='itsn') {u8{14,6,255,255}}
	M (t='dbsn') {u8{15,6,255,255}}
	M (t='bisn') {u8{15,6,255,255}}
	P {u32{0xFF000000, 0xFF3A3A3A, 0xFF777777, 0xFFB9B9B9, 0xFF0D14A6, 0xFF009012, 0xFFAC4E27, 0xFFE24D89, 0xFF8799FF, 0xFFAAE0A9, 0xFFF4D2B7, 0xFFEEACC0, 0xFF86D7FF, 0xFF00E7E7, 0xFFB7DDE9, 0xFF587486}}
	V (n='fsiz') {f{12.0}}
}
Gr
{
	Bg {}
	Sb (ro='nmbr') {s{"25"}}
	Fr
	{
		Gr (t='numr')
		{
			Bg {}
			Sb {s{"x"}}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
}
```

This is what Radical Pie saves when the document carries a design: eight fonts, a style map for each of
the 21 styles, the sixteen palette colours and the font size. A generated equation writes `D {}`
instead and inherits the design of whatever opens it. Note `25` as one `Sb` with `ro='nmbr'`: adjacent
characters that share a role and a style belong in one symbol.

## 3. A binomial coefficient

`\binom{2n}{n} = \frac{(2n)!}{n!\,n!}`, the central binomial coefficient.

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
			Fr (at)
			{
				Gr (t='numr')
				{
					Bg {}
					Sb (ro='nmbr') {s{"2"}}
					Sb {s{"n"}}
				}
				Gr (t='dnom')
				{
					Bg {}
					Sb {s{"n"}}
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
			Br
			{
				Gr (ba='mddl')
				{
					Bg {}
					Sb (ro='nmbr') {s{"2"}}
					Sb {s{"n"}}
				}
			}
			Sb (st='uprt') {s{"!"}}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb {s{"n"}}
			Sb (st='uprt') {s{"!"}}
			Sp (s=3.0) {}
			Sb {s{"n"}}
			Sb (st='uprt') {s{"!"}}
		}
	}
}
```

A binomial coefficient is a vertical fraction with the bar cleared, `Fr (at)`, inside a bracket. The
bracket has no `uint32` data list, which gives parentheses, and a second bracket of the same kind is
what the factorial in the numerator applies to. A factorial is `Sb (st='uprt')`: the role stays
`'math'` so the spacing is right, and only the style is overridden. `Sp (s=3.0)` is the thin space
between the two factorials in the denominator.

## 4. Cases

`\mathrm{sgn}(t) = \begin{cases} 1, & \text{if } t > 0; \\ 0, & \text{if } t = 0; \\ -1, & \text{if } t < 0. \end{cases}`.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='func') {s{"sgn"}}
	Br
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sb {s{"t"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Br
	{
		u32{0x7B,0x00}
		Gr (ba='mddl')
		{
			Bg {}
			Sb (ro='nmbr') {s{"1"}}
			Sb (ro='pnct') {s{","}}
			Al (al='cent') {}
			Sp (s=18.0) {}
			Sb (ro='text') {s{"if "}}
			Sb {s{"t"}}
			Sb (ro='rltn') {s{">"}}
			Sb (ro='nmbr') {s{"0"}}
			Sb (ro='pnct') {s{";"}}
			Bg {}
			Sb (ro='nmbr') {s{"0"}}
			Sb (ro='pnct') {s{","}}
			Al (al='cent') {}
			Sp (s=18.0) {}
			Sb (ro='text') {s{"if "}}
			Sb {s{"t"}}
			Sb (ro='rltn') {s{"="}}
			Sb (ro='nmbr') {s{"0"}}
			Sb (ro='pnct') {s{";"}}
			Bg {}
			Sb (ro='oper') {s{"−"}}
			Sb (ro='nmbr') {s{"1"}}
			Sb (ro='pnct') {s{","}}
			Al (al='cent') {}
			Sp (s=18.0) {}
			Sb (ro='text') {s{"if "}}
			Sb {s{"t"}}
			Sb (ro='rltn') {s{"<"}}
			Sb (ro='nmbr') {s{"0"}}
			Sb (ro='pnct') {s{"."}}
		}
	}
}
```

Three things carry this one. The bracket's `u32{0x7B,0x00}` draws a left brace and nothing on the
right. The single bracket subgroup holds three lines, each begun by its own `Bg`. The `Al (al='cent')`
after each comma lines the three conditions up, and `Sp (s=18.0)` opens a quad of space before the
words. `sgn` is `ro='func'`, which is what gives a function name its upright style and its side
bearings.

## 5. Three aligned lines

Three definitions aligned on their equals signs, their left-hand sides three different widths.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb {s{"a"}}
	Br
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sb {s{"n"}}
		}
	}
	Al (al='cent') {}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"2"}}
	Sb {s{"n"}}
	Sb (ro='oper') {s{"−"}}
	Sb (ro='nmbr') {s{"1"}}
	Bg {}
	Sb {s{"b"}}
	Br
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sb {s{"m"}}
			Sb (ro='pnct') {s{","}}
			Sb {s{"n"}}
		}
	}
	Al (al='cent') {}
	Sb (ro='rltn') {s{"="}}
	Sb {s{"m"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Sb {s{"n"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Bg {}
	Sb {s{"c"}}
	Br
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sb {s{"m"}}
			Sb (ro='pnct') {s{","}}
			Sb {s{"n"}}
			Sb (ro='pnct') {s{","}}
			Sb {s{"p"}}
		}
	}
	Al (al='cent') {}
	Sb (ro='rltn') {s{"="}}
	Sb {s{"mnp"}}
	Sb (ro='oper') {s{"−"}}
	Sb (ro='nmbr') {s{"1"}}
}
```

A multi-line equation is one group with several `Bg` structures, not several groups. The centre aligner
before each `=` puts all three signs in one column and centres each left-hand side in the width the
longest of them needs. `mnp` is one symbol, because three letters that share a role and a style belong
in one.

## 6. A molecule

Dimethyl ether as a structural diagram.

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
		u32[2]{{0,'sing'}}
		Gr
		{
			Bg {}
			Sb (ro='chem') {s{"H"}}
		}
	}
	Bd
	{
		u32[2]{{'uppr','sing'},{'lowr','sing'},{0,'sing'}}
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
		Gr (t='lowr')
		{
			Bg {}
			Sb (ro='chem') {s{"H"}}
		}
	}
	Bd
	{
		u32[2]{{0,'sing'}}
		Gr
		{
			Bg {}
			Sb (ro='chem') {s{"O"}}
		}
	}
	Bd
	{
		u32[2]{{'uppr','sing'},{'lowr','sing'},{0,'sing'}}
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
		Gr (t='lowr')
		{
			Bg {}
			Sb (ro='chem') {s{"H"}}
		}
	}
	Sb (ro='chem') {s{"H"}}
}
```

Each bond site is a `Bd` whose pair list names one bond per direction, with group type `0` for the
rightward bond that has no group of its own. The atoms are `ro='chem'`, which sets them upright. The
molecule reads left to right along the baseline, one bond site per atom that has a neighbour to its
right; the last hydrogen is a plain symbol, because the carbon before it draws the bond that reaches
it.

## 7. A phantom that evens up two radicals

`\sqrt{a^3 b} = a\sqrt{ab}`, first as written, then with a phantom.

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
			Sb {s{"a"}}
			Sc
			{
				Gr (t='sups')
				{
					Bg {}
					Sb (ro='nmbr') {s{"3"}}
				}
			}
			Sb {s{"b"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Sb {s{"a"}}
	Rd
	{
		Gr
		{
			Bg {}
			Sb {s{"ab"}}
		}
	}
}
```

The two radicals come out different heights because the left-hand radicand carries a script: the left
sign reaches 12.3 points above the baseline and the right one 9.99. Adding a phantom of `a^3` to the
right-hand radicand gives both the same vertical extent:

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
			Sb {s{"a"}}
			Sc
			{
				Gr (t='sups')
				{
					Bg {}
					Sb (ro='nmbr') {s{"3"}}
				}
			}
			Sb {s{"b"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Sb {s{"a"}}
	Rd
	{
		Gr
		{
			Bg {}
			Sb {s{"ab"}}
			Ph
			{
				Bg {}
				Sb {s{"a"}}
				Sc
				{
					Gr (t='sups')
					{
						Bg {}
						Sb (ro='nmbr') {s{"3"}}
					}
				}
			}
		}
	}
}
```

The phantom holds its content directly after a `Bg`, with no `Gr` in between. Its default type
`'vert'` claims the height and none of the width, so the right-hand sign rises to 12.3 points and the
equation stays the same width.

## 8. The quadratic formula

File: `examples/QuadraticFormula.pie`

`x_{1,2} = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}`.

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
			Sb (ro='nmbr') {s{"1"}}
			Sb (ro='pnct') {s{","}}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Fr
	{
		Gr (t='numr')
		{
			Bg {}
			Sb (ro='oper') {s{"−"}}
			Sb {s{"b"}}
			Sb (ro='oper') {s{"±"}}
			Rd
			{
				Gr
				{
					Bg {}
					Sb {s{"b"}}
					Sc
					{
						Gr (t='sups')
						{
							Bg {}
							Sb (ro='nmbr') {s{"2"}}
						}
					}
					Sb (ro='oper') {s{"−"}}
					Sb (ro='nmbr') {s{"4"}}
					Sb {s{"ac"}}
				}
			}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
			Sb {s{"a"}}
		}
	}
}
```

The leading minus is `ro='oper'`, the same role as the minus inside the radicand; `'unry'` is reserved
for `∂` and `∇`. Both are U+2212, the minus sign, not the hyphen. `ac` is one symbol, and `2a` is
two, because the digit and the letter have different roles. The subscript that names the two roots is
an ordinary `Sc` holding a `'subs'` group of three symbols, a number, a comma and a number.

## 9. Roots

File: `examples/Roots.pie`

`\sqrt{2}, \sqrt[3]{x}, \sqrt[n]{x+y}`.

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
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='pnct') {s{","}}
	Sp (s=4.5) {}
	Rd
	{
		Gr
		{
			Bg {}
			Sb {s{"x"}}
		}
		Gr (t='degr')
		{
			Bg {}
			Sb (ro='nmbr') {s{"3"}}
		}
	}
	Sb (ro='pnct') {s{","}}
	Sp (s=4.5) {}
	Rd
	{
		Gr
		{
			Bg {}
			Sb {s{"x"}}
			Sb (ro='oper') {s{"+"}}
			Sb {s{"y"}}
		}
		Gr (t='degr')
		{
			Bg {}
			Sb {s{"n"}}
		}
	}
}
```

An nth root is a radical with a `'degr'` subgroup; without one it is a square root. There is no
separate cube-root structure, and the `\cbrt` character in `references/TexSymbols.md` is what the
editor types to insert this same structure.

## 10. A definite integral

File: `examples/DefiniteIntegral.pie`

`\int_0^1 x^2 \, dx = \frac{1}{3}`.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	In
	{
		Gr
		{
			Bg {}
			Sb {s{"x"}}
			Sc
			{
				Gr (t='sups')
				{
					Bg {}
					Sb (ro='nmbr') {s{"2"}}
				}
			}
			Sp (s=3.0) {}
			Sb {s{"d"}}
			Sb {s{"x"}}
		}
		Gr (t='lowr')
		{
			Bg {}
			Sb (ro='nmbr') {s{"0"}}
		}
		Gr (t='uppr')
		{
			Bg {}
			Sb (ro='nmbr') {s{"1"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Fr (sm)
	{
		Gr (t='numr')
		{
			Bg {}
			Sb (ro='nmbr') {s{"1"}}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb (ro='nmbr') {s{"3"}}
		}
	}
}
```

The limits are subgroups of the integral, `'lowr'` and `'uppr'`, not scripts. The integral sign itself
is implicit: leave the `uint32` data list out and it is U+222B. The differential is a plain `'math'`
symbol, italic like any other letter, preceded by a thin space of 3 mu, which is what `\,` means;
upright is a house-style choice the site does not make.

## 11. A sum with limits

File: `examples/SumWithLimits.pie`

`\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}`.

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
		Gr
		{
			Bg {}
			Fr
			{
				Gr (t='numr')
				{
					Bg {}
					Sb (ro='nmbr') {s{"1"}}
				}
				Gr (t='dnom')
				{
					Bg {}
					Sb {s{"n"}}
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
		Gr (t='lowr')
		{
			Bg {}
			Sb {s{"n"}}
			Sb (ro='rltn') {s{"="}}
			Sb (ro='nmbr') {s{"1"}}
		}
		Gr (t='uppr')
		{
			Bg {}
			Sb (st='uprt') {s{"∞"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Fr
	{
		Gr (t='numr')
		{
			Bg {}
			Sb (st='itgk') {s{"π"}}
			Sc
			{
				Gr (t='sups')
				{
					Bg {}
					Sb (ro='nmbr') {s{"2"}}
				}
			}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb (ro='nmbr') {s{"6"}}
		}
	}
}
```

A sum is an iteration, and the summand goes in the iteration's own default subgroup, so the whole
fraction sits under the sign rather than after it. Infinity takes `st='uprt'` and π takes `st='itgk'`,
the Greek italic style that a small Greek letter gets by convention.

## 12. A limit

File: `examples/Limit.pie`

`\lim_{x \to 0} \frac{\sin x}{x} = 1`.

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
			Sb (ro='func') {s{"lim"}}
		}
		Gr (t='lowr')
		{
			Bg {}
			Sb {s{"x"}}
			Sb (ro='arrw') {s{"→"}}
			Sb (ro='nmbr') {s{"0"}}
		}
	}
	Fr
	{
		Gr (t='numr')
		{
			Bg {}
			Sb (ro='func') {s{"sin"}}
			Sb {s{"x"}}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb {s{"x"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"1"}}
}
```

`lim` with something underneath it is a stack: the word in the main subgroup and the condition in
`'lowr'`. Both `lim` and `sin` are `ro='func'`. The arrow is `ro='arrw'`.

## 13. A matrix in brackets

File: `examples/BracketedMatrix.pie`

`\mathbf{A} = \begin{bmatrix} a & b \\ c & d \end{bmatrix}`.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (st='bold') {s{"A"}}
	Sb (ro='rltn') {s{"="}}
	Br
	{
		u32{0x5B,0x5D}
		Gr (ba='mddl')
		{
			Bg {}
			Mx (r=2,c=2)
			{
				Gr
				{
					Bg {}
					Sb {s{"a"}}
				}
				Gr
				{
					Bg {}
					Sb {s{"b"}}
				}
				Gr
				{
					Bg {}
					Sb {s{"c"}}
				}
				Gr
				{
					Bg {}
					Sb {s{"d"}}
				}
			}
		}
	}
}
```

Entries run row-major: a, b, c, d for a matrix read a, b over c, d. The specification calls the
order column-major; Radical Pie 1.15 lays the entries out row by row, and the executable wins.
Getting this backwards transposes the matrix and nothing complains. The brackets are a `Br` around
the matrix with `u32{0x5B,0x5D}`; `pmatrix` is the same with `0x28,0x29`, and `vmatrix` with
`0x7C,0x7C`.

## 14. A second partial derivative

File: `examples/PartialDerivative.pie`

`\frac{\partial^2 u^{\alpha}}{\partial x_i \partial x_j}`.

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
			Sb (ro='unry',st='sym1') {s{"∂"}}
			Sc
			{
				Gr (t='sups')
				{
					Bg {}
					Sb (ro='nmbr') {s{"2"}}
				}
			}
			Sb {s{"u"}}
			Sc
			{
				Gr (t='sups')
				{
					Bg {}
					Sb (st='itgk') {s{"α"}}
				}
			}
		}
		Gr (t='dnom')
		{
			Bg {}
			Sb (ro='unry',st='sym1') {s{"∂"}}
			Sb {s{"x"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb {s{"i"}}
				}
			}
			Sb (ro='unry',st='sym1') {s{"∂"}}
			Sb {s{"x"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb {s{"j"}}
				}
			}
		}
	}
}
```

Each `∂` is `ro='unry',st='sym1'`, the one role the site keeps `'unry'` for; every minus sign, by
contrast, is `ro='oper'`. A script attaches to the structure immediately before it, so the order symbol
then script is what puts the exponent on the right thing; the `2` above the first `∂` is a script on
that symbol alone.

## 15. An overbrace with a label

File: `examples/OverBrace.pie`

`\overbrace{a_1 + \cdots + a_n}^{n \, \text{terms}} = S_n`.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Wm (t='brac')
	{
		Gr
		{
			Bg {}
			Sb {s{"a"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb (ro='nmbr') {s{"1"}}
				}
			}
			Sb (ro='oper') {s{"+"}}
			Sb (ro='elps') {s{"⋯"}}
			Sb (ro='oper') {s{"+"}}
			Sb {s{"a"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb {s{"n"}}
				}
			}
		}
		Gr (t='labl')
		{
			Bg {}
			Sb {s{"n"}}
			Sp (s=3.0) {}
			Sb (ro='text') {s{"terms"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Sb {s{"S"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb {s{"n"}}
		}
	}
}
```

A wide mark stretches to its content, and its `'labl'` subgroup is the material outside the brace,
which is where an `\overbrace` exponent goes. `\underbrace` is the same structure with `un` set. The
ellipsis is `ro='elps'`.

## 16. Vectors and bars

File: `examples/Vector.pie`

`\vec{AB} = \overline{z + w}`.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Wm (t='rarw')
	{
		Gr
		{
			Bg {}
			Sb {s{"AB"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Wm (t='line')
	{
		Gr
		{
			Bg {}
			Sb {s{"z"}}
			Sb (ro='oper') {s{"+"}}
			Sb {s{"w"}}
		}
	}
}
```

`\vec` is a wide mark of type `'rarw'` and `\overline` is one of type `'line'`. Use these when the mark
covers an expression. For a mark over a single character, `\hat{a}` and the like, use `Mk` inside the
symbol instead, which draws a font accent at a fixed size.

## 17. A norm

File: `examples/Norm.pie`

`\|\mathbf{v}\| = \sqrt{\mathbf{v} \cdot \mathbf{v}} \ge 0`.

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
		u32{0x2016,0x2016}
		Gr (ba='mddl')
		{
			Bg {}
			Sb (st='bold') {s{"v"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Rd
	{
		Gr
		{
			Bg {}
			Sb (st='bold') {s{"v"}}
			Sb (ro='oper') {s{"·"}}
			Sb (st='bold') {s{"v"}}
		}
	}
	Sb (ro='rltn') {s{"≥"}}
	Sb (ro='nmbr') {s{"0"}}
}
```

A norm is a bracket whose two characters are both U+2016. A single absolute value is `0x7C,0x7C`.
Bold vectors are `st='bold'` over the default `'math'` role, so they keep variable spacing.

## 18. Primes and accents

File: `examples/PrimesAndMarks.pie`

`f'(x) = 2x, \quad \hat{a} \cdot \tilde{b} \in \mathbb{R}^n`.

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
	Br
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sb {s{"x"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"2"}}
	Sb {s{"x"}}
	Sb (ro='pnct') {s{","}}
	Sp (s=18.0) {}
	Sb {s{"a"} Mk {u32{0x302}}}
	Sb (ro='oper') {s{"·"}}
	Sb {s{"b"} Mk {u32{0x303}}}
	Sb (ro='rltn') {s{"∈"}}
	Sb (st='doub') {s{"ℝ"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb {s{"n"}}
		}
	}
}
```

`Pr {}` puts a single prime on the structure before it, and a `uint32` value in it chooses a double or
triple prime instead. `Mk` carries the Unicode value of a combining accent, U+0302 for a hat and
U+0303 for a tilde. `\mathbb{R}` is `st='doub'` on the code point `ℝ` itself; the style does nothing to
a plain `R`.

## 19. A system of equations under a brace

File: `examples/SystemOfEquations.pie`

`\begin{cases} 2x + y = 5, \\ x - 3y = -1. \end{cases}`.

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
		u32{0x7B,0x00}
		Gr (ba='mddl')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
			Sb {s{"x"}}
			Sb (ro='oper') {s{"+"}}
			Sb {s{"y"}}
			Al (al='rght') {}
			Sb (ro='rltn') {s{"="}}
			Sb (ro='nmbr') {s{"5"}}
			Sb (ro='pnct') {s{","}}
			Bg {}
			Sb {s{"x"}}
			Sb (ro='oper') {s{"−"}}
			Sb (ro='nmbr') {s{"3"}}
			Sb {s{"y"}}
			Al (al='rght') {}
			Sb (ro='rltn') {s{"="}}
			Sb (ro='oper') {s{"−"}}
			Sb (ro='nmbr') {s{"1"}}
			Sb (ro='pnct') {s{"."}}
		}
	}
}
```

The same shape as the cases example: one bracket, `u32{0x7B,0x00}`, one subgroup, two lines, an aligner
before each relation. The sign of `-1` is `ro='oper'`, the same role as the minus in `x - 3y`; a leading
minus takes no special role.

## 20. A multi-line derivation

File: `examples/AlignedDerivation.pie`

Three lines of `(a+b)^2` expanded, aligned on the equals signs.

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
			Sb {s{"a"}}
			Sb (ro='oper') {s{"+"}}
			Sb {s{"b"}}
		}
	}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Al (al='rght') {}
	Sb (ro='rltn') {s{"="}}
	Br
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sb {s{"a"}}
			Sb (ro='oper') {s{"+"}}
			Sb {s{"b"}}
		}
	}
	Br
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sb {s{"a"}}
			Sb (ro='oper') {s{"+"}}
			Sb {s{"b"}}
		}
	}
	Bg {}
	Al (al='rght') {}
	Sb (ro='rltn') {s{"="}}
	Sb {s{"a"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Sb {s{"ab"}}
	Sb (ro='oper') {s{"+"}}
	Sb {s{"ba"}}
	Sb (ro='oper') {s{"+"}}
	Sb {s{"b"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Bg {}
	Al (al='rght') {}
	Sb (ro='rltn') {s{"="}}
	Sb {s{"a"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Sb (ro='nmbr') {s{"2"}}
	Sb {s{"ab"}}
	Sb (ro='oper') {s{"+"}}
	Sb {s{"b"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
}
```

The second and third lines begin with their aligner, so nothing precedes the column and the equals
signs line up under the first one. A right aligner pushes what comes before it against the column,
which is the usual choice for a derivation; a centre aligner centres it, as in example 5.

## 21. A chemical equation

File: `examples/ChemicalReaction.pie`

`2\,\mathrm{H_2} + \mathrm{O_2} \xrightarrow{\text{spark}} 2\,\mathrm{H_2O}`.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='nmbr') {s{"2"}}
	Sb (ro='chem') {s{"H"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Sb (ro='chem') {s{"O"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Ar
	{
		u32{'long'}
		u32{'rarw'}
		Gr (t='uppr')
		{
			Bg {}
			Sb (ro='text') {s{"spark"}}
		}
	}
	Sb (ro='nmbr') {s{"2"}}
	Sb (ro='chem') {s{"H"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='chem') {s{"O"}}
}
```

The reaction arrow is an `Ar` with one full-length arrow and one charm, a right arrowhead, plus an
`'uppr'` label; the label stretches the arrow. Subscript numbers are scripts on the element symbol.
The coefficient needs no space after it: a number before a `'chem'` symbol gets one from the design.

## 22. Text and mathematics together

File: `examples/TextAndMath.pie`

`\text{The kinetic energy is } E = \tfrac{1}{2}mv^2, \text{ with } m = 3\,\mathrm{kg}.`

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='text') {s{"The kinetic energy is "}}
	Sb {s{"E"}}
	Sb (ro='rltn') {s{"="}}
	Fr (sm)
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
	Sb {s{"mv"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='text') {s{", with "}}
	Sb {s{"m"}}
	Sb (ro='rltn') {s{"="}}
	Sb (ro='nmbr') {s{"3"}}
	Sb (ro='unit') {s{"kg"}}
	Sb (st='uprt') {s{"."}}
}
```

Words are `ro='text'`, and the comma, the gap and the trailing space inside the string are how Radical
Pie separates prose from the mathematics on either side of it, the way the site's Convergence
equation and its Theorem equation write it; no separate `'pnct'` sits between them. `kg` is `ro='unit'` with no `Sp` before
it, since the role spaces itself. `Fr (sm)` is the small fraction that belongs in a line of text, and
the closing full stop after math is a plain `st='uprt'` symbol, not `ro='pnct'`.

## 23. An equation with its terms labelled

File: `examples/NavierStokesAnnotated.pie`

The Navier-Stokes momentum equation with each of its five terms named: a highlight behind three of them,
a vertical arrow from each term to a rail, and a caption on the far end of every arrow. Radical Pie
wrote this file, so every node is named `$_0`, `$_1` and so on in the order the nodes appear; the names
an author writes are replaced the first time the program saves.

```pie
// Radical Pie Equation

D
{
}
Ln $_0 (s,es='arr1')
{
	X
	{
		ref{$_13,$_8}
		u32{'cent','xxx!'}
		i32{1,1}
	}
}
Rt $_1 (f,fpi=9)
{
	X
	{
		ref{$_9,$_10}
		u32{0,0}
		i32{1,0}
	}
}
Ln $_2 (s,es='arr1')
{
	X
	{
		ref{$_1,$_8}
		u32{'edge','xxx!'}
		i32{3,1}
	}
}
Ln $_3 (s,es='arr1')
{
	X
	{
		ref{$_16,$_8}
		u32{'cent','xxx!'}
		i32{1,1}
	}
}
Rt $_4 (f,fpi=9)
{
	X
	{
		ref{$_14,$_15}
		u32{0,0}
		i32{1,0}
	}
}
Rt $_5 (f,fpi=10)
{
	X
	{
		ref{$_11,$_12}
		u32{0,0}
		i32{1,0}
	}
}
Ln $_6 (s,es='arr1')
{
	X
	{
		ref{$_5,$_8}
		u32{'edge','xxx!'}
		i32{2,0}
	}
}
Ln $_7 (s,es='arr1')
{
	X
	{
		ref{$_4,$_8}
		u32{'edge','xxx!'}
		i32{2,0}
	}
}
Gr $_8
{
	Bg {}
	Sb (st='itgk') {s{"ρ"}}
	Br
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sp (s=1.5) {}
			Fr
			{
				Gr (t='numr')
				{
					Bg $_9 {}
					Sb (ro='unry',st='sym1') {s{"∂"}}
					Sb (st='bold') {s{"u"}}
				}
				Gr (t='dnom')
				{
					Bg {}
					Sb (ro='unry',st='sym1') {s{"∂"}}
					Sb $_10 {s{"t"}}
				}
			}
			Sb $_11 (ro='oper') {s{"+"}}
			Br $_12
			{
				u32{0x00,0x00}
				Gr (ba='mddl')
				{
					Bg {}
					Br
					{
						Gr (ba='mddl')
						{
							Bg {}
							Sb (st='bold') {s{"u"}}
							Sb (ro='oper') {s{"·"}}
							Sb (ro='unry',st='sym1') {s{"∇"}}
						}
					}
					Sb (st='bold') {s{"u"}}
				}
			}
			Sp (s=1.5) {}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Br
	{
		u32{0x00,0x00}
		Gr (ba='mddl')
		{
			Bg {}
			Sb (ro='oper') {s{"−"}}
			Sb (ro='unry',st='sym1') {s{"∇"}}
			St
			{
				Gr (ba='mddl')
				{
					Bg {}
					Sb $_13 {s{"p"}}
				}
			}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Br
	{
		u32{0x00,0x00}
		Gr (ba='mddl')
		{
			Bg $_14 {}
			Sb (st='itgk') {s{"μ"}}
			Sb (ro='unry',st='sym1') {s{"∇"}}
			Sc
			{
				Gr (t='sups')
				{
					Bg {}
					Sb (ro='nmbr') {s{"2"}}
				}
			}
			Sb $_15 (st='bold') {s{"u"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	St
	{
		Gr (ba='mddl')
		{
			Bg {}
			Sb $_16 (st='bold') {s{"f"}}
		}
	}
}
Gr (t='anno',al='cent')
{
	Bg {}
	Sb (ro='text') {s{"Pressure"}}
	X
	{
		ref{$_0}
		u32{'anno'}
		i32{1}
	}
}
Gr (t='anno',al='cent')
{
	Bg {}
	Sb (ro='text') {s{"Local"}}
	Bg {}
	Sb (ro='text') {s{"acceleration"}}
	X
	{
		ref{$_2}
		u32{'anno'}
		i32{1}
	}
}
Gr (t='anno',al='cent')
{
	Bg {}
	Sb (ro='text') {s{"Body"}}
	Bg {}
	Sb (ro='text') {s{"Force"}}
	X
	{
		ref{$_3}
		u32{'anno'}
		i32{1}
	}
}
Gr (t='anno',al='cent')
{
	Bg {}
	Sb (ro='text') {s{"Convective"}}
	Bg {}
	Sb (ro='text') {s{"Acceleration"}}
	X
	{
		ref{$_6}
		u32{'anno'}
		i32{1}
	}
}
Gr (t='anno',al='cent')
{
	Bg {}
	Sb (ro='text') {s{"Viscous"}}
	Bg {}
	Sb (ro='text') {s{"Diffusion"}}
	X
	{
		ref{$_7}
		u32{'anno'}
		i32{1}
	}
}
```

Read the file in the order of its five sections: the drawing structures of the background layer, the
main group, then the annotation groups. The three `Rt` rectangles come first so that their fill sits
behind the glyphs, `fpi=9` on two of them and `fpi=10` on the third, one colour per kind of term.

Each rectangle runs from index 1 of the structure that starts the run to index 0 of the structure that
ends it, and the choice of start is the whole trick:

- The time derivative is boxed from `$_9`, the `Bg` of the fraction's numerator, to `$_10`, the `t` of
  its denominator. A `Bg` carries the anchors of the line it begins, so starting there covers the
  fraction from its left edge; both nodes sit inside subgroups, where only indexes 0 and 1 exist.
- The convective term is boxed from `$_11`, the `+` in front of it, to `$_12`, the bracket that closes
  it. An operator is a convenient left edge when the term does not start a line.
- The viscous term is boxed from `$_14`, the `Bg` of the group inside its bracket, because the term
  begins with the symbol `μ` and a symbol's anchors are at its right end; starting at the symbol would
  cut the `μ` off.

The two terms with no highlight, the pressure `p` and the body force `f`, are each wrapped in an inline
group, `St { Gr (ba='mddl') { Bg {} Sb $_13 {s{"p"}} } }`. The wrap adds no glyph and no spacing and
leaves the symbol its own anchors, which is what the arrow needs: `u32{'cent','xxx!'} i32{1,1}` leaves
the symbol's centre and ends on the rail above the equation.

Every arrow ends on a rail, `'xxx!'` index 1 above and index 0 below, and the rail snaps the line
straight, so all five come out vertical and the captions on each side line up. The three that start on
a rectangle leave it by an edge, `'edge'` index 3 for the top and index 2 for the bottom, matching the
rail they run to. The arrowhead is `es='arr1'`, on the start of the line, which is the end at the
equation.

The five captions are annotation groups after the main group. Each attaches to its own arrow with
`ref{$_2} u32{'anno'} i32{1}`, the far end of that arrow, so the arrow's length places the caption and
no nudge is needed; `al='cent'` centres the lines over it, and a second `Bg` gives a second line. The
`Sp (s=1.5) {}` at each end of the bracketed run is there for the highlight: a rectangle takes no
padding of its own, and without the space the box would touch the bracket.

## 24. The rendering equation, annotated

File: `examples/RenderingEquationAnnotated.pie`

The rendering equation with five highlights, six arrows and six captions, in three colours. This file
was written by hand, so its nodes carry names that say what they are, `$boxOut`, `$arOut`, `$main`;
Radical Pie replaces them all with `$_0`, `$_1` and so on the first time it saves the file.

```pie
// Radical Pie Equation

D
{
}
Rr $boxOut (f,fpi=9,r=1)
{
	X
	{
		ref{$bgOut,$brOut}
		u32{0,0}
		i32{1,0}
	}
}
Rr $boxEmit (f,fpi=9,r=1)
{
	X
	{
		ref{$bgEmit,$brEmit}
		u32{0,0}
		i32{1,0}
	}
}
Rr $boxBrdf (f,fpi=10,r=1)
{
	X
	{
		ref{$bgInt,$brBrdf}
		u32{0,0}
		i32{1,0}
	}
}
Rr $boxIn (f,fpi=9,r=1)
{
	X
	{
		ref{$bgIn,$brIn}
		u32{0,0}
		i32{1,0}
	}
}
Rr $boxCos (f,fpi=11,r=1)
{
	X
	{
		ref{$bgCos,$brCos}
		u32{0,0}
		i32{1,0}
	}
}
Ln $arOut (s,spi=5,es='arr2')
{
	X
	{
		ref{$boxOut,$main}
		u32{'edge','xxx!'}
		i32{3,1}
	}
}
Ln $arEmit (s,spi=5,es='arr2')
{
	X
	{
		ref{$boxEmit,$main}
		u32{'edge','xxx!'}
		i32{3,1}
	}
}
Ln $arIn (s,spi=5,es='arr2')
{
	X
	{
		ref{$boxIn,$main}
		u32{'edge','xxx!'}
		i32{3,1}
	}
}
Ln $arBrdf (s,spi=6,es='arr2')
{
	X
	{
		ref{$boxBrdf,$main}
		u32{'edge','xxx!'}
		i32{2,0}
	}
}
Ln $arCos (s,spi=7,es='arr2')
{
	X
	{
		ref{$boxCos,$main}
		u32{'edge','xxx!'}
		i32{2,0}
	}
}
Ln $arHemi (s,spi=4,es='arr2')
{
	X
	{
		ref{$symHemi,$main}
		u32{'cent','xxx!'}
		i32{0,0}
	}
}
Gr $main
{
	Bg {}
	St
	{
		Gr
		{
			Bg $bgOut {}
			Sb {s{"L"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb {s{"o"}}
				}
			}
			Br $brOut
			{
				Gr
				{
					Bg {}
					Sb (st='bold') {s{"x"}}
					Sb (ro='pnct') {s{","}}
					Sb (st='itgk') {s{"ω"}}
					Sc
					{
						Gr (t='subs')
						{
							Bg {}
							Sb {s{"o"}}
						}
					}
				}
			}
		}
	}
	Sb (ro='rltn') {s{"="}}
	St
	{
		Gr
		{
			Bg $bgEmit {}
			Sb {s{"L"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb {s{"e"}}
				}
			}
			Br $brEmit
			{
				Gr
				{
					Bg {}
					Sb (st='bold') {s{"x"}}
					Sb (ro='pnct') {s{","}}
					Sb (st='itgk') {s{"ω"}}
					Sc
					{
						Gr (t='subs')
						{
							Bg {}
							Sb {s{"o"}}
						}
					}
				}
			}
		}
	}
	Sb (ro='oper') {s{"+"}}
	In (il)
	{
		Gr
		{
			Bg $bgInt {}
			Sb {s{"f"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb {s{"r"}}
				}
			}
			Br $brBrdf
			{
				Gr
				{
					Bg {}
					Sb (st='bold') {s{"x"}}
					Sb (ro='pnct') {s{","}}
					Sb (st='itgk') {s{"ω"}}
					Sc
					{
						Gr (t='subs')
						{
							Bg {}
							Sb {s{"i"}}
						}
					}
					Sb (ro='pnct') {s{","}}
					Sb (st='itgk') {s{"ω"}}
					Sc
					{
						Gr (t='subs')
						{
							Bg {}
							Sb {s{"o"}}
						}
					}
				}
			}
			Sp (s=3.0) {}
			St
			{
				Gr
				{
					Bg $bgIn {}
					Sb {s{"L"}}
					Sc
					{
						Gr (t='subs')
						{
							Bg {}
							Sb {s{"i"}}
						}
					}
					Br $brIn
					{
						Gr
						{
							Bg {}
							Sb (st='bold') {s{"x"}}
							Sb (ro='pnct') {s{","}}
							Sb (st='itgk') {s{"ω"}}
							Sc
							{
								Gr (t='subs')
								{
									Bg {}
									Sb {s{"i"}}
								}
							}
						}
					}
				}
			}
			Sp (s=3.0) {}
			St
			{
				Gr
				{
					Bg $bgCos {}
					Br $brCos
					{
						Gr
						{
							Bg {}
							Sb (st='bold') {s{"n"}}
							Sb (ro='oper') {s{"·"}}
							Sb (st='itgk') {s{"ω"}}
							Sc
							{
								Gr (t='subs')
								{
									Bg {}
									Sb {s{"i"}}
								}
							}
						}
					}
				}
			}
			Sp (s=3.0) {}
			Sb {s{"d"}}
			Sb (st='itgk') {s{"ω"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb {s{"i"}}
				}
			}
		}
		Gr (t='lowr')
		{
			Bg {}
			Sb $symHemi (st='grek') {s{"Ω"}}
		}
	}
}
Gr (as=0.8125,t='anno',al='cent')
{
	Bg {}
	Sb (pi=5,ro='text') {s{"outgoing"}}
	Bg {}
	Sb (pi=5,ro='text') {s{"radiance"}}
	X
	{
		ref{$arOut}
		u32{'anno'}
		i32{1}
	}
}
Gr (as=0.8125,t='anno',al='cent')
{
	Bg {}
	Sb (pi=5,ro='text') {s{"emitted"}}
	Bg {}
	Sb (pi=5,ro='text') {s{"radiance"}}
	X
	{
		ref{$arEmit}
		u32{'anno'}
		i32{1}
	}
}
Gr (as=0.8125,t='anno',al='cent')
{
	Bg {}
	Sb (pi=5,ro='text') {s{"incoming"}}
	Bg {}
	Sb (pi=5,ro='text') {s{"radiance"}}
	X
	{
		ref{$arIn}
		u32{'anno'}
		i32{1}
	}
}
Gr (as=0.8125,t='anno',al='cent')
{
	Bg {}
	Sb (pi=6,ro='text') {s{"BRDF"}}
	X
	{
		ref{$arBrdf}
		u32{'anno'}
		i32{1}
	}
}
Gr (as=0.8125,t='anno',al='cent')
{
	Bg {}
	Sb (pi=7,ro='text') {s{"cosine"}}
	Bg {}
	Sb (pi=7,ro='text') {s{"factor"}}
	X
	{
		ref{$arCos}
		u32{'anno'}
		i32{1}
	}
}
Gr (as=0.8125,t='anno',al='cent')
{
	Bg {}
	Sb (pi=4,ro='text') {s{"over the"}}
	Bg {}
	Sb (pi=4,ro='text') {s{"hemisphere"}}
	X
	{
		ref{$arHemi}
		u32{'anno'}
		i32{1}
	}
}
```

The highlights are `Rr (f,fpi=...,r=1)`, rounded rather than square, and colour carries the meaning:
`fpi=9` for the three radiance terms, `fpi=10` for the BRDF, `fpi=11` for the cosine factor, with each
arrow's `spi` and each caption's `pi` set to the same index, so a reader follows the colour from the
term to the words.

Every one of the five boxed terms is wrapped in an inline group with a named `Bg`, `$bgOut`, `$bgEmit`,
`$bgIn`, `$bgCos`, and the box runs from that `Bg` at index 1 to the closing bracket of the term at
index 0. Each term begins with a symbol or a bracket, so without the wrap the box would start at the
right end of the first symbol; the wrap is what gives the run a left edge. The BRDF is the exception:
it starts at `$bgInt`, the `Bg` of the integrand itself, because the term is the first thing in the
integrand.

The three radiance terms are labelled from above, `'edge'` index 3 to `'xxx!'` index 1, and the BRDF
and the cosine factor from below, `'edge'` index 2 to `'xxx!'` index 0, which keeps six captions apart
on a single equation. The domain of integration is labelled without a highlight: the arrow leaves the
`Ω` in the integral's `'lowr'` subgroup at `'cent'` index 0, the downward anchor of a symbol, and runs
to the rail below.

The captions are `Gr (as=0.8125,t='anno',al='cent')`, scaled below the size of the equation, one `Bg`
per line, each attached to the far end of its arrow. The site's own Rendering equation adds a second
row to this pattern: two more arrows to `'xxx!'` indexes 7 and 9, rails further out than 1, with
`al='rght'` on their captions. Reach for that when one row of labels cannot hold them all.

The `Sp (s=3.0) {}` between the factors of the integrand separates the highlights; without them the
boxes would meet.

## 25. A reaction with a labelled arrow, in chemistry mode

File: `examples/Photosynthesis.pie`

`6\,\mathrm{CO_2} + 12\,\mathrm{H_2O} \xrightarrow{\text{light}} \mathrm{C_6H_{12}O_6} + 6\,\mathrm{O_2} + 6\,\mathrm{H_2O}`,
photosynthesis in the form that shows the six water molecules the reaction gives back.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='nmbr') {s{"6"}}
	Sb (ro='chem') {s{"CO"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Sb (ro='nmbr') {s{"12"}}
	Sb (ro='chem') {s{"H"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='chem') {s{"O"}}
	Ar
	{
		u32{'long'}
		u32{'rarw'}
		Gr (t='uppr',al='cent')
		{
			Bg {}
			Sb (ro='text') {s{"light"}}
		}
	}
	Sb (ro='chem') {s{"C"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"6"}}
		}
	}
	Sb (ro='chem') {s{"H"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"12"}}
		}
	}
	Sb (ro='chem') {s{"O"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"6"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Sb (ro='nmbr') {s{"6"}}
	Sb (ro='chem') {s{"O"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Sb (ro='nmbr') {s{"6"}}
	Sb (ro='chem') {s{"H"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='chem') {s{"O"}}
}
```

Chemistry mode comes down to these roles and nothing else. Every element letter is `ro='chem'`, which
stands it upright and puts a little space between a preceding number and the element, so the
coefficient `Sb (ro='nmbr') {s{"6"}}` sits directly against `Sb (ro='chem') {s{"CO"}}` with no `Sp`
between them, and letters that share the role share one symbol. Each subscript is an ordinary `Sc`
holding a `'subs'` group, written after the element it counts, which is all that the automatic
subscripting of version 1.15 leaves in the file; `s{"12"}` is one number in one symbol, coefficient or
subscript, never two digits. The reaction arrow is an `Ar` with `'long'` and `'rarw'` in two `u32`
lists and an `'uppr'` label group holding the word light as `ro='text'`, and the label is what
stretches the arrow. `al='cent'` centres the label over the arrow, where Example 21 leaves `al` at its
default.

## 26. A structural formula written from scratch

File: `examples/AceticAcid.pie`

Acetic acid, `\mathrm{CH_3COOH}`, drawn as a structural formula.

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
		u32[2]{{0,'sing'}}
		Gr
		{
			Bg {}
			Sb (ro='chem') {s{"CH"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb (ro='nmbr') {s{"3"}}
				}
			}
		}
	}
	Bd
	{
		u32[2]{{'uprt','doub'},{'lwrt','sing'}}
		Gr
		{
			Bg {}
			Sb (ro='chem') {s{"C"}}
		}
		Gr (t='uprt')
		{
			Bg {}
			Sb (ro='chem') {s{"O"}}
		}
		Gr (t='lwrt')
		{
			Bg {}
			Sb (ro='chem') {s{"OH"}}
		}
	}
}
```

The chain is two bond sites. The first holds the methyl as one group, `CH` with a `'subs'`
script, and its only bond is `{0,'sing'}`, the rightward bond that joins it to the next structure in
the group. The second is the carboxyl carbon: `{'uprt','doub'}` to the oxygen and `{'lwrt','sing'}` to
the hydroxyl, both at the default 45 degrees, and no `0` pair, because nothing follows it.

Radical Pie's own drawing of the same molecule is the site's Acetic Acid equation. It expands
the methyl into a third bond site with `'uppr'` and `'lowr'` hydrogen groups and a hydrogen bonded on
the left, so its picture is four atoms wide and shows the geometry at the methyl carbon. Condensing
that group, as here, keeps the drawing to the part that carries the chemistry. Both files render;
choose per atom. `references/Chemistry.md` covers the choice.

## 27. A benzene ring with one substituent

File: `examples/Toluene.pie`

Toluene, a benzene ring carrying a methyl group.

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
		u32[2]{{'uppr','sing'},{'lwlf','sing'},{'lwrt','doub'}}
		u32[2]{{'lwlf','shal'},{'lwrt','shal'}}
		Gr
		{
			Bg {}
			Sb (ro='chem') {s{"C"}}
		}
		Gr (t='uppr')
		{
			Bg {}
			Bd
			{
				u32[2]{{'uplf','sing'},{'uprt','doub'}}
				u32[2]{{'uplf','shal'},{'uprt','shal'}}
				Gr
				{
					Bg {}
					Sb (ro='chem') {s{"C"}}
				}
				Gr (t='uprt')
				{
					Bg {}
					Bd
					{
						u32[2]{{'uppr','sing'},{'lwrt','sing'}}
						u32[2]{{'lwrt','shal'}}
						Gr
						{
							Bg {}
							Sb (ro='chem') {s{"C"}}
						}
						Gr (t='lwrt')
						{
							Bg {}
							Bd
							{
								u32[2]{{'uprt','sing'}}
								u32[2]{{'uprt','shal'}}
								Gr
								{
									Bg {}
									Sb (ro='chem') {s{"C"}}
								}
								Gr (t='uprt')
								{
									Bg {}
									Sb (ro='chem') {s{"H"}}
								}
							}
						}
						Gr (t='uppr')
						{
							Bg {}
							Sb (ro='chem') {s{"CH"}}
							Sc
							{
								Gr (t='subs')
								{
									Bg {}
									Sb (ro='nmbr') {s{"3"}}
								}
							}
						}
					}
				}
				Gr (t='uplf')
				{
					Bg {}
					Sb (ro='chem') {s{"H"}}
				}
			}
		}
		Gr (t='lwrt')
		{
			Bg {}
			Bd
			{
				u32[2]{{'uprt','sing'},{'lowr','sing'}}
				u32[2]{{'uprt','shal'}}
				Gr
				{
					Bg {}
					Sb (ro='chem') {s{"C"}}
				}
				Gr (t='uprt')
				{
					Bg {}
					Bd
					{
						u32[2]{{'uppr','doub'},{'lwrt','sing'}}
						u32[2]{{'lwrt','shal'}}
						Gr
						{
							Bg {}
							Sb (ro='chem') {s{"C"}}
						}
						Gr (t='uppr')
						{
							Bg {}
						}
						Gr (t='lwrt')
						{
							Bg {}
							Sb (ro='chem') {s{"H"}}
						}
					}
				}
				Gr (t='lowr')
				{
					Bg {}
					Sb (ro='chem') {s{"H"}}
				}
			}
		}
		Gr (t='lwlf')
		{
			Bg {}
			Sb (ro='chem') {s{"H"}}
		}
	}
}
```

Six carbons, six nested bond sites, one closing stub. The root is the lower-left carbon; each
following ring carbon is a bond site inside the previous one's neighbour group, walking up the left
side, across the top and down the right. The sixth bond of the ring is `{'uppr','doub'}` on the
lower-right carbon pointing into `Gr (t='uppr') { Bg {} }`, a group with no atom in it. The stub lands
on the upper-right carbon, which is already drawn at that position, and the ring closes.

Every diagonal ring bond is `'shal'`, which is what makes the hexagon regular; the two vertical bonds
take no angle. The double bonds alternate for a Kekulé structure. The site's Orthoxylene equation
uses `'prd1'` and `'prd2'` on the same skeleton for the delocalised picture. Substituting the ring is
a change to the top carbon's `'uppr'` group alone: the site's Phenol equation puts `OH` there. The
step-by-step recipe is in `references/Chemistry.md`.

## 28. A reaction with a catalyst and a temperature

File: `examples/CatalyticHydrogenation.pie`

`\ce{C2H4 + H2 ->[Pt][150 ^\circ C] C2H6}`, the hydrogenation of ethene.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='chem') {s{"C"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='chem') {s{"H"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"4"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Sb (ro='chem') {s{"H"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Ar
	{
		u32{'long'}
		u32{'rarw'}
		Gr (t='uppr',al='cent')
		{
			Bg {}
			Sb (ro='chem') {s{"Pt"}}
		}
		Gr (t='lowr',al='cent')
		{
			Bg {}
			Sb (ro='nmbr') {s{"150"}}
			Sb (ro='unit') {s{"°C"}}
		}
	}
	Sb (ro='chem') {s{"C"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='chem') {s{"H"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"6"}}
		}
	}
}
```

One `Ar` with one `'long'` arrow, one `'rarw'` charm, and both label groups. The catalyst goes in
`Gr (t='uppr',al='cent')` and the conditions in `Gr (t='lowr',al='cent')`; `al='cent'` centres each
label over the shaft, and the wider of the two labels sets the length of the arrow.

A temperature is two symbols, `ro='nmbr'` for the figure and `ro='unit'` for `°C`, which keeps the
upright style and the thin space between them. The catalyst is `ro='chem'` because it is an element
symbol.

## 29. An equilibrium

File: `examples/AmmoniaEquilibrium.pie`

`\ce{N2 + 3H2 <=>[Fe][450 ^\circ C] 2NH3}`, the Haber process.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='chem') {s{"N"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='oper') {s{"+"}}
	Sb (ro='nmbr') {s{"3"}}
	Sb (ro='chem') {s{"H"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Ar
	{
		u32{'long','long'}
		u32{'ruhp'}
		u32{'left','ldhp'}
		Gr (t='uppr',al='cent')
		{
			Bg {}
			Sb (ro='chem') {s{"Fe"}}
		}
		Gr (t='lowr',al='cent')
		{
			Bg {}
			Sb (ro='nmbr') {s{"450"}}
			Sb (ro='unit') {s{"°C"}}
		}
	}
	Sb (ro='nmbr') {s{"2"}}
	Sb (ro='chem') {s{"NH"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"3"}}
		}
	}
}
```

Two arrows in one `Ar`, so the first `u32` list holds `'long'` twice and two charm lists follow,
one per arrow, top to bottom. The upper arrow takes `'ruhp'`, an upward harpoon pointing right at the
right end. The lower arrow takes `'left','ldhp'`: the alignment cursor starts at the right end of the
shaft, and every charm draws where the cursor is, so the cursor has to be moved first. Written as
`u32{'ldhp'}` alone the lower harpoon lands at the right end under the upper one.

`'ruhp'` over `'ldhp'` puts the two barbs on the outside, which is the ⇌ of chemical equilibrium.
`'ruhp'` over `'luhp'` puts them on the inside and reads as something else. The labels work as in
Example 28 and belong to the whole `Ar`, not to either arrow.

## 30. An orbital diagram

File: `examples/OxygenOrbitals.pie`

The ground-state electron configuration of oxygen, 1s² 2s² 2p⁴.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Mx (r=3,c=4,al='left',eh,ew)
	{
		Gr
		{
			Bg {}
			Sb (ro='text') {s{"2p"}}
		}
		Gr
		{
			Bg {}
			Bx
			{
				Gr
				{
					Bg {}
					Sb (ro='arrw') {s{"↑↓"}}
				}
			}
		}
		Gr
		{
			Bg {}
			Bx
			{
				Gr
				{
					Bg {}
					Sb (ro='arrw') {s{"↑"}}
					Sp (s=0.0) {}
					Ph (t='horz')
					{
						Bg {}
						Sb (ro='arrw') {s{"↓"}}
					}
				}
			}
		}
		Gr
		{
			Bg {}
			Bx
			{
				Gr
				{
					Bg {}
					Sb (ro='arrw') {s{"↑"}}
					Sp (s=0.0) {}
					Ph (t='horz')
					{
						Bg {}
						Sb (ro='arrw') {s{"↓"}}
					}
				}
			}
		}
		Gr
		{
			Bg {}
			Sb (ro='text') {s{"2s"}}
		}
		Gr
		{
			Bg {}
			Bx
			{
				Gr
				{
					Bg {}
					Sb (ro='arrw') {s{"↑↓"}}
				}
			}
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
			Sb (ro='text') {s{"1s"}}
		}
		Gr
		{
			Bg {}
			Bx
			{
				Gr
				{
					Bg {}
					Sb (ro='arrw') {s{"↑↓"}}
				}
			}
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
```

Each orbital is a `Bx` around a group holding its electrons as one `ro='arrw'` symbol, `↑↓` for a
pair and `↑` for a single electron. A box with one arrow in it would come out narrower than a box with
two, so the half-filled boxes carry a `Sp (s=0.0) {}` and `Ph (t='horz')` holding the missing `↓`: the
space drops the arrow role's own gap and the phantom takes the width without drawing, and the three 2p
boxes render at the same 18.1477 pt.

The levels sit on a three by four `Mx`, highest energy at the top, one column for the label and one
for each orbital. Entries are listed row-major, so the order is the 2p label, its three boxes, the 2s
label, its box, two empty entries, and the same again for 1s. An empty entry is `Gr { Bg {} }`.
`al='left'` lines the labels up, `eh` and `ew` keep the grid square. The two unpaired 2p electrons are
Hund's rule, and the file says nothing about it; the arrows are what the reader sees.

## 31. Ions, charges and states of matter

File: `examples/SaltDissolution.pie`

`\ce{NaCl(s) ->[H2O] Na+(aq) + Cl-(aq)}`, sodium chloride dissolving.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='chem') {s{"NaCl"}}
	Sb (ro='unit') {s{"(s)"}}
	Ar
	{
		u32{'long'}
		u32{'rarw'}
		Gr (t='uppr',al='cent')
		{
			Bg {}
			Sb (ro='chem') {s{"H"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb (ro='nmbr') {s{"2"}}
				}
			}
			Sb (ro='chem') {s{"O"}}
		}
	}
	Sb (ro='chem') {s{"Na"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='unry') {s{"+"}}
		}
	}
	Sb (ro='unit') {s{"(aq)"}}
	Sb (ro='oper') {s{"+"}}
	Sb (ro='chem') {s{"Cl"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='unry') {s{"−"}}
		}
	}
	Sb (ro='unit') {s{"(aq)"}}
}
```

A charge is a `Sc` with a `'sups'` group holding the sign as `ro='unry'`, written after the
element the way any superscript is.

A state of matter has no fixture behind it, so the role is chosen by what it does to the spacing
around it. `ro='text'` on `(aq)` swallows the space on both sides of the `'oper'` that follows it, and
`ro='pnct'` swallows the space after it. `ro='unit'` puts a thin space between the ion and its state
and leaves the operator alone, which is the spacing the equation wants. The solvent over the arrow is
an ordinary `'uppr'` label holding a formula rather than a word.

## 32. A saturated ring

File: `examples/Cyclohexanediol.pie`

Cyclohexane-1,2-diol, drawn as a Haworth hexagon with the ring name under it.

```pie
// Radical Pie Equation

D
{
}
Gr (al='cent',ba='frst')
{
	Bg {}
	Bd
	{
		u32[2]{{'uplf','sing'},{'uprt','Sing'},{'lwrt','Sing'}}
		Gr
		{
			Bg {}
			Sb (ro='chem') {s{"C"}}
		}
		Gr (t='uplf',al='rght')
		{
			Bg {}
			Sb (ro='chem') {s{"HO"}}
		}
		Gr (t='uprt')
		{
			Bg {}
			Bd
			{
				u32[2]{{'uppr','sing'},{0,'Sing'}}
				Gr
				{
					Bg {}
					Sb (ro='chem') {s{"C"}}
				}
				Gr (t='uppr')
				{
					Bg {}
					Sb (ro='chem') {s{"OH"}}
				}
			}
		}
		Gr (t='lwrt')
		{
			Bg {}
			Bd
			{
				u32[2]{{0,'Sing'}}
				Gr
				{
					Bg {}
					Sb (ro='chem') {s{"C"}}
				}
			}
		}
	}
	Bd
	{
		u32[2]{{'uplf','Sing'},{'lwlf','Sing'}}
		Gr
		{
			Bg {}
			Sb (ro='chem') {s{"C"}}
		}
		Gr (t='uplf')
		{
			Bg {}
			Sb (ro='chem') {s{"C"}}
		}
		Gr (t='lwlf')
		{
			Bg {}
			Sb (ro='chem') {s{"C"}}
		}
	}
	Bg (lg=30.0) {}
	Sb (ro='text') {s{"Cyclohexane-1,2-diol"}}
}
```

The ring is two bond sites side by side in one group, the construction `references/Chemistry.md`
gives under Saturated and heteroatom rings. The first site owns the left apex and the two atoms
diagonally right of it, and each of those two ends in a `{0,'Sing'}` bond that runs rightwards into
an atom the second site holds, one in its `'uplf'` group and one in its `'lwlf'` group. The second
site owns the right apex and closes both halves with `'uplf','Sing'` and `'lwlf','Sing'`. The
capitalised bond kinds are the long bonds that give the ring its height.

The two hydroxyls sit on adjacent atoms. The one on the left apex goes in its `'uplf'` group with
`al='rght'`, which turns the group round so the bond meets `HO` at its right edge; the one on the
top-left carbon goes in that carbon's `'uppr'` group, which is free because the ring's top edge is
horizontal. No hydrogen is drawn: Radical Pie draws only the bonds a site names, so an implicit
hydrogen is written by leaving it out.

The name under the drawing is a second line of the main group, opened by `Bg (lg=30.0) {}`.
`ba='frst'` puts the equation's baseline on the drawing rather than on the name, which is the
difference between a baseline shift of 50 points and one of 3 for this file, and `al='cent'` centres
both lines.

## 33. A Feynman diagram

File: `examples/FeynmanVertex.pie`

A QED vertex: an electron in, an electron out, and a photon leaving where they meet. `references/catalogue/Annotations.md`, under Feynman diagrams, has the recipe this equation follows.

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

The grid is `references/examples/FeynmanVertex.pie`'s only piece of ink-free structure: a one-column,
three-row `Mx` whose top cell carries the `Sp (s=42.0)` that sets the column wide enough for the wave,
whose middle row is the vertex, and whose outer two `'cell'` corners are where the electron lines start
and finish. `$ein` runs from the bottom-left corner to the vertex with its arrowhead there, `$eout` runs
from the vertex to the top-left corner with its arrowhead there, so both point the way the physics
does: into the vertex on the way in, away from it on the way out. The photon is six `Wm (t='tild')`
widemarks in one annotation group anchored on the vertex, `al='left'` so the wave starts exactly there,
and each of the three legs takes its own caption from an annotation group on its `'anno'` anchor.

## 34. Two labelled arrows in a synthesis

File: `examples/LabelledArrows.pie`

`\ce{C2H4 ->[H3PO4][300 ^\circ C] C2H5OH ->[K2Cr2O7] CH3COOH}`, ethene to ethanol to ethanoic
acid.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb (ro='chem') {s{"C"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='chem') {s{"H"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"4"}}
		}
	}
	Ar
	{
		u32{'long'}
		u32{'rarw'}
		Gr (t='uppr')
		{
			Bg {}
			Sb (ro='chem') {s{"H"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb (ro='nmbr') {s{"3"}}
				}
			}
			Sb (ro='chem') {s{"PO"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb (ro='nmbr') {s{"4"}}
				}
			}
		}
		Gr (t='lowr')
		{
			Bg {}
			Sb (ro='nmbr') {s{"300"}}
			Sb (ro='unit') {s{"°C"}}
		}
	}
	Sb (ro='chem') {s{"C"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sb (ro='chem') {s{"H"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"5"}}
		}
	}
	Sb (ro='chem') {s{"OH"}}
	Ar
	{
		u32{'long'}
		u32{'rarw'}
		Gr (t='uppr')
		{
			Bg {}
			Sb (ro='chem') {s{"K"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb (ro='nmbr') {s{"2"}}
				}
			}
			Sb (ro='chem') {s{"Cr"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb (ro='nmbr') {s{"2"}}
				}
			}
			Sb (ro='chem') {s{"O"}}
			Sc
			{
				Gr (t='subs')
				{
					Bg {}
					Sb (ro='nmbr') {s{"7"}}
				}
			}
		}
	}
	Sb (ro='chem') {s{"CH"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='nmbr') {s{"3"}}
		}
	}
	Sb (ro='chem') {s{"COOH"}}
}
```

The two arrows carry the same `u32{'long'}` and `u32{'rarw'}` and come out different lengths, 40.26
and 46.84 points of shaft, because an arrow is as long as its widest label plus 11 points at each end
and nothing else sets it. Neither label group carries `al`, which centres it; the first arrow's
`'lowr'` group holds the temperature as a number and a unit, and both `'uppr'` groups hold a formula
written the way the line around them is, `ro='chem'` with `Sc` subscripts.

## 35. One design for a whole document

File: `examples/DocumentDesign.pie`

A document whose equations are all set in Cambria at 12 point, with a palette of its own, from
`references/examples/DocumentDesign.pie`. The design block is the whole of it, and every other equation in
that document carries the same block, character for character.

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
	Sb (ro='pnct') {s{","}}
	Sb (ro='text') {s{" so the kinetic energy "}}
	Sb (pi=6) {s{"E"}}
	Sc
	{
		Gr (t='subs')
		{
			Bg {}
			Sb (ro='text') {s{"k"}}
		}
	}
	Sb (ro='rltn') {s{"="}}
	Fr
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
	Sb {s{"m"}}
	Sb {s{"v"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
}
```

`F (i=1)` names the font by its family name and the four `M` structures point the upright, italic, bold and
bold italic styles at it; a style the design does not name keeps the font the factory design gives it, so
the Greek, the symbols and the big operators still come from Radical Pie's own faces. Naming one index in a
map is enough, because Radical Pie fills the three fallback slots from the factory design when it reads the
file. `V (n='fsiz') {f{12.0}}` sets the body size in points, against a factory default of 11, and the `P`
replaces all sixteen palette colours at once, which is what lets `pi=6` mean this document's blue. Hand a
design over as a block like this one and copy it into every equation the document holds; nothing outside
the file carries it, and an equation with an empty `D {}` renders at the factory design instead.

## 36. A worked long division

File: `examples/LongDivision.pie`

`\polylongdiv{91}{7}`, ninety-one divided by seven as a textbook prints it, quotient above the
vinculum and the working under the dividend. The divisor stands outside the `Dv`, each line of the
working is a further `Bg` inside the dividend group, and the division sign grows down over all of
them.

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
			Bg {}
			Wm (t='line',un)
			{
				Gr
				{
					Bg {}
					Sb (ro='nmbr',tf) {s{"7"}}
				}
			}
			Bg {}
			Sb (ro='nmbr',tf) {s{"21"}}
			Bg {}
			Wm (t='line',un)
			{
				Gr
				{
					Bg {}
					Sb (ro='nmbr',tf) {s{"21"}}
				}
			}
			Bg {}
			Ph (t='full')
			{
				Bg {}
				Sb (ro='nmbr',tf) {s{"2"}}
			}
			Sb (ro='nmbr',tf) {s{"0"}}
		}
		Gr (t='quot')
		{
			Bg {}
			Sb (ro='nmbr',tf) {s{"13"}}
		}
	}
}
```

Every number carries `tf`, the strict tabular figures flag, which is what holds the columns in line:
without it the units digit of 21 sits 0.2 points to the right of the units digit of 91. The blank
column on the last line is a `Ph (t='full')` holding the digit that would have stood there, and each
subtraction rule is a `Wm (t='line',un)` around the row above it.

## 37. A table of values set with tabs

File: `examples/TabbedTable.pie`

A table of n, n squared and n factorial, four rows under a header row. Every column stands at a fixed
position because each row steps the same tab interval, which is what `Sp (t)` does and an aligner does
not.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Sb {s{"n"}}
	Sp (t,s=36.0) {}
	Sb {s{"n"}}
	Sc
	{
		Gr (t='sups')
		{
			Bg {}
			Sb (ro='nmbr') {s{"2"}}
		}
	}
	Sp (t,s=36.0) {}
	Sb {s{"n"}}
	Sb (ro='pnct') {s{"!"}}
	Bg {}
	Sb (ro='nmbr') {s{"1"}}
	Sp (t,s=36.0) {}
	Sb (ro='nmbr') {s{"1"}}
	Sp (t,s=36.0) {}
	Sb (ro='nmbr') {s{"1"}}
	Bg {}
	Sb (ro='nmbr') {s{"2"}}
	Sp (t,s=36.0) {}
	Sb (ro='nmbr') {s{"4"}}
	Sp (t,s=36.0) {}
	Sb (ro='nmbr') {s{"2"}}
	Bg {}
	Sb (ro='nmbr') {s{"3"}}
	Sp (t,s=36.0) {}
	Sb (ro='nmbr') {s{"9"}}
	Sp (t,s=36.0) {}
	Sb (ro='nmbr') {s{"6"}}
	Bg {}
	Sb (ro='nmbr') {s{"4"}}
	Sp (t,s=36.0) {}
	Sb (ro='nmbr') {s{"16"}}
	Sp (t,s=36.0) {}
	Sb (ro='nmbr') {s{"24"}}
}
```

Each row is one line of the group, and the two tabs in it carry `s=36.0`, a stop every 36 math units,
which is 22 points at the default design. Every row's second column starts at the 22.0 point stop and
its third at the 44.0 point stop, measured through the render pipeline. Nothing in the file says where column three is: the second
tab lands on the second multiple because every entry in column two stops short of the first one. A
longer entry would push its own row to the next stop and leave that row alone out of register, which is
when to write an `Al` per column instead and let the columns fit the content.

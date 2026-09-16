# Matrices

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
| `mb` | bool | false | Middle baseline: sit the middle of the row baselines on the equation baseline, 0.83 pt from where the matrix sits without it. |
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

A rule dividing a matrix into blocks, the `|` and the `\hline` of a LaTeX `array`, is a drawing object
over the grid: an `Ln (s)` in the background section whose connector names the matrix twice,
`u32{'cell','cell'}`, with the two grid corners the rule runs between. An `r` by `c` matrix has `r`+1 by
`c`+1 corners numbered row by row, so a corner is `rowLine` times (`c`+1) plus `colLine`. Rendered
2026-09-15: on a two by three matrix inside a `Br`, `i32{1,9}` drew the vertical rule after the first
column and `i32{4,7}` the horizontal rule after the first row, and the four rules of a ten by ten ran
`i32{4,114}`, `i32{7,117}`, `i32{44,54}` and `i32{77,87}`. The anchors work on a matrix nested inside a
`Br`, which is where a divided matrix usually sits.

A picture grid, a matrix of coloured blocks and labels, is spaced by the design values and not by spacers
in its cells: `'rwgp'`, `'aspx'` and `'aspy'` in the `'mtrx'` domain, and `'vtgp'` in the `'brck'` domain
for the brackets around it. The `V` section of `references/catalogue/Design.md` has the values the site's
own grids use and a fence with all four.

A matrix owns four anchor types of its own beyond `'cell'`, the grid corners the `X` section's table
(`references/catalogue/Annotations.md`) lists: `'orow'` and `'ocol'` sit past the grid's outer edge, clear
of a bracket wrapped round it, one pair per row or per column; `'mrow'` and `'mcol'` sit on the same row
and column midlines measured inside the grid instead, so the arrowhead lands on the bracket rather than
clearing it. `references/AnchorAtlas.md` measures every index of all four. Point a row-labelling or a
column-labelling arrow at a bracketed matrix from `'orow'` or `'ocol'`, never from `'mrow'` or `'mcol'`,
which would drive the head into the bracket. The site's Exomorphism equation labels the rows and columns of
its picture grid this way, running each arrow from the matrix's `'orow'` or `'ocol'` anchor to rail 5 of
the equation and hanging the caption on the arrow's far end, index 1, so the labels read outward from the
grid.

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

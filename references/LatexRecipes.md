# LaTeX Recipes

Every LaTeX construct that has a Radical Pie counterpart, with the structure to write and the worked
example that shows it. Read it while you are choosing the structures for an equation you hold in LaTeX
or in words.

| LaTeX | Radical Pie | Where to look |
| --- | --- | --- |
| `\frac{a}{b}` | `Fr` with `numr` and `dnom` | Example 8 |
| `\tfrac`, an inline fraction | `Fr (sm)` | Example 22 |
| `a/b` on one line | `Fr (t='horz')` or `Fr (t='diag')` | `references/catalogue/Fractions.md`, `Fr` |
| `\binom{n}{k}` | `Fr (at)` inside a `Br` | Example 3 |
| `x^2`, `x_i`, both at once | `Sc` with `sups`, `subs` | Examples 8, 14 |
| `{}^{14}\mathrm{C}` | `Sc (pr)` before the symbol | `references/catalogue/Symbols.md`, `Sc` |
| `\sqrt{x}` | `Rd` | Example 8 |
| `\sqrt[n]{x}` | `Rd` with a `degr` subgroup | Example 9 |
| `\sum_{}^{}`, `\prod`, `\bigcup` and the other n-ary signs | `It` with `lowr`, `uppr`, character in a `u32` list | Example 11 |
| `\int_{}^{}`, `\oint`, `\iint` | `In` with `lowr`, `uppr`, character in a `u32` list | Example 10 |
| `\lim_{}`, `\max_{}`, `\overset` | `St` with `lowr` or `uppr` | Example 12 |
| `\underset{k}{\circ}`, `\mathop{\circ}\limits_k` | `St` with a `'lowr'` label, which keeps the operator at its own size | `references/catalogue/Groups.md`, `St` |
| `\left( \right)` and every other pair | `Br` with a `u32` character array | Examples 3, 13, 17 |
| `\lfloor x \rfloor`, `\lceil x \rceil` | `Br` with `u32{0x230A,0x230B}` or `u32{0x2308,0x2309}`, never two symbols holding the characters | `references/catalogue/Brackets.md`, `Br` |
| `\lvert x \rvert`, `\lVert x \rVert`, `\abs`, `\norm` | `Br` with `u32{0x7C,0x7C}` or `u32{0x2016,0x2016}` | `references/catalogue/Brackets.md`, `Br` |
| `\begin{cases}` | `Br` with `u32{0x7B,0x00}`, several `Bg`, `Al` | Examples 4, 19 |
| `\pmatrix`, `\bmatrix`, `\vmatrix` | `Mx` inside a `Br`, entries row-major | Example 13 |
| `\begin{array}[t]`, `[b]`, `[c]` nested in one cell | `ba='frst'`, `'last'`, `'mddl'` on that matrix entry's group | `references/catalogue/Matrices.md`, `Mx` |
| `\begin{array}` with a `\|` column rule or an `\hline` | one `Ln (s)` per rule, `u32{'cell','cell'}` on the matrix, between two grid corners | `references/catalogue/Matrices.md`, `Mx` |
| `\overline`, `\underline` | `Wm (t='line')`, `un` for under; a `Bx` draws four sides or two and never one | Example 16 |
| `\vec` | `Wm (t='rarw')`, over a single letter as well, because `Mk`'s range U+0300 to U+0362 holds no arrow | Example 16 |
| `\widehat`, `\widetilde` | `Wm (t='what')`, `Wm (t='tild')` | `references/catalogue/Arrows.md`, `Wm` |
| `\hat{a}`, `\tilde{a}`, `\dot{a}` on one character | `Mk` inside the `Sb` | Example 18 |
| `\overbrace{}^{}`, `\underbrace{}_{}` | `Wm (t='brac')` with a `labl` subgroup | Example 15 |
| `f'`, `f''` | `Pr`, optionally with a character | Example 18 |
| `\xrightarrow{above}[below]`, `\xleftarrow` | `Ar` with `u32{'long'}`, a `'rarw'` or `'left','larw'` charm list, and an `'uppr'` and `'lowr'` group | Examples 21, 28 |
| `\xleftrightarrow{}` | one `'long'` arrow, `u32{'left','larw','rght','rarw'}` | `references/catalogue/Arrows.md`, `Ar` |
| `\rightleftharpoons`, `\ce{<=>}` | two `'long'` arrows, `u32{'ruhp'}` over `u32{'left','ldhp'}`; the plain character ⇌ is a `Sb (ro='rltn')` and does not stretch | Example 29 |
| `\ce{<=>>}`, `\ce{<<=>}` | the same pair with one arrow short, `u32{'long','rght'}` or `u32{'left','long'}` | `references/catalogue/Arrows.md`, `Ar` |
| `\nrightarrow`, `\ce{-/>}` | one `'long'` arrow, `u32{'rarw','cent','slsh'}` | `references/catalogue/Arrows.md`, `Ar` |
| `\ce{->[cat][temp]}` and every other mhchem arrow condition | the `'uppr'` and `'lowr'` groups of the `Ar`, which stretch it | Example 28 |
| Structural formulas and bonds | `Bd`, one per atom with neighbours | `Chemistry.md`; Example 6 |
| `\ce{...}` and anything else mhchem writes | `'chem'` roles, `Sc` subscripts, `Ar`, `Bd` | `Chemistry.md`; Examples 26 to 31 |
| `\,` `\>` or `\:` `\;` `\!` `\quad` `\qquad` | `Sp` with 3, 4, 5, −3, 18 and 36 math units, which come out 1.8333, 2.4444, 3.0556, −1.8333, 11.0 and 22.0 points at the default design | Examples 10, 22 |
| `\mspace{9mu}`, `\hspace{5pt}`, `\kern` | `Sp` with the width in math units, one math unit being the design font size over eighteen; nothing clamps the value | `references/catalogue/Symbols.md`, `Sp` |
| `\begin{tabular}`, a column of aligned values | `Sp (t)` per column with the column position in math units, or an `Al` per column when the columns should fit the content | Example 37 |
| `\text{...}` | `Sb (ro='text')`, punctuation and word gaps kept inside the string | Example 22 |
| An operator word inside running text, `\bmod` | `Sb (ro='func')` | Example 4; the site's Theorem equation |
| Units | `Sb (ro='unit')`, with no `Sp` before it | Example 22 |
| `\mathbf` | `st='bold'`, on any Latin letter | Example 17 |
| `\mathrm` | `st='uprt'` on the symbol; a whole word that reads as an operator takes `ro='func'` instead | Example 22; `references/catalogue/Symbols.md`, `Sb` — roles |
| `\textcolor`, `\color` | `co` on each symbol, ABGR with `0xFF` in front, or `pi` for a palette index; `sco` and `spi` on a line, `fco` and `fpi` on a fill | `references/catalogue/Overview.md`, how a file is put together |
| A thousands separator, `299{,}792{,}458` | the commas inside the number's own string, `Sb (ro='nmbr') {s{"299,792,458"}}`; a `'pnct'` comma is for sentence punctuation and adds 3 mu behind each one | `references/catalogue/Symbols.md`, `Sb` — roles |
| `\mathbb{R}`, `\mathcal{B}` and the rest | `st='doub'`, `'scpt'`, `'bdsc'` on the specific code point the alphabet gives that letter, `ℝ` not `R`; `st='frkt'`, `'sans'`, `'mono'` draw any letter | Example 18; `references/catalogue/Symbols.md`, `Sb` — roles |
| `\mathbb{1}`, or any double-struck letter or digit outside ℕℤℚℝℂ | the Mathematical Alphanumeric code point, `𝟙` is U+1D7D9, with `st='doub'`; the code point alone with `st='uprt'` renders plain | `references/catalogue/Symbols.md`, `Sb` — roles |
| `\cdots` between factors | `Sb (ro='elps') {s{"⋯"}}`, with no operator dot before or after it | `references/catalogue/Symbols.md`, `Sb` — roles |
| `\alpha`, `\Gamma` | `Sb (st='itgk')`, `Sb (st='grek')` | Example 11 |
| `\begin{align}` and other multi-line forms | Several `Bg` in one group, one `Al` per line just after the relation; an `&` in front of a relation maps to an aligner behind it | Examples 5, 20 |
| `\boxed{x}` | `Bx` around the group | `references/catalogue/Brackets.md`, `Bx` |
| `\fbox{text}` | `Bx` around a `Sb (ro='text')`; the border thickness is `V (d='boxx',n='rule')` | `references/catalogue/Brackets.md`, `Bx` |
| A box open on two sides | `Bx (t='lwlf')`, `'lwrt'`, `'uplf'`, `'uprt'` | `references/catalogue/Brackets.md`, `Bx` |
| `\cancel{x}` | `Kt (t='lwup')` | `references/catalogue/Brackets.md`, `Kt` |
| `\bcancel{x}`, `\xcancel{x}` | `Kt (t='uplw')`, `Kt (t='exxx')` | `references/catalogue/Brackets.md`, `Kt` |
| `\sout{x}`, a rule straight through | `Kt (t='horz')` | `references/catalogue/Brackets.md`, `Kt` |
| `\cancelto{2}{4}`, or `\cancel{4}` with a replacement written above or below | the struck digit is `Kt (t='lwup')`; the replacement sits directly under or over it as a `St` whose main line is the struck digit and whose `Gr (t='lowr')` or `Gr (t='uppr')` holds the smaller replacement digit, usually sharing one colour with `pi=` | `references/catalogue/Groups.md`, `St` — cancellation with a replacement |
| `\not` | `Ng` inside the `Sb` | `references/catalogue/Symbols.md`, `Ng` |
| `\phantom`, `\vphantom`, `\hphantom` | `Ph` with `t='full'`, `'vert'` which is the default, `'horz'` | Example 7 |
| `\mathmakebox[w][l]{...}`, a minimum width | `Ph (t='hzov')`, which reserves the box and lets what follows lie over it | `references/catalogue/Groups.md`, `Ph` |
| A long division | `Dv` with a `quot` subgroup, the divisor written before it | `references/catalogue/Fractions.md`, `Dv` |
| `\polylongdiv{91}{7}`, and the `longdiv` form | `Dv` with the quotient in `quot` and every working line a further `Bg` of the dividend group, digits with `tf` | Example 36 |
| A circled or boxed single symbol | `En` inside the `Sb`, fixed size and one per symbol | `references/catalogue/Brackets.md`, `En` |
| Label the terms of an equation (highlight, arrow, caption) | `Rt` or `Rr` behind it, `Ln` to a rail, `Gr (t='anno')` | Examples 23, 24; `references/catalogue/Annotations.md`, `X` |

Every other TeX command maps to a character. `references/TexSymbols.md` lists all of them, generated
from the documentation, with the Unicode value, the character itself, and for the commands that insert a
structure, the structure to write.

## Alignment recipe

A multi-line equation is one group with several `Bg`. What lines the lines up is the aligner, and the
choice is which of the three values to write.

`al='rght'` is `\begin{align}`: the left-hand side of every line is pushed flush against the column, so
the equals signs stand in one line and the terms before them end together. This is the value for a
derivation, one relation carried down through several lines, and it is what the shipped aligned
derivation uses.

`al='cent'` centres each line's left-hand side in the width the longest of them needs, which reads
better where the lines are separate equations or definitions rather than one carried-down relation.
Of the site's six multi-line files, five, including its Maxwell equations, a system of four distinct
equations, are set this way; only its one step-by-step derivation, the Gaussian integral, uses
`al='rght'`, so a system of equations takes `al='cent'`, not `al='rght'`.

`al='left'` leaves the material at the line origin and moves only what follows the aligner. Use it for
a hanging line, a continuation that starts under the column rather than at it.

The three place the same column. Measured at the default design on four lines whose longest left-hand
side is 23.96 points, the relation after the aligner starts at 26.8990 points on all four, and the
short lines' left-hand sides start at 0.0000 with `'left'`, 18.5142 with `'rght'` and 9.8345 with
`'cent'`. The value is per line, so a line that should hang left inside a right-aligned column carries
`al='left'` on its own aligner. A line with no aligner at all starts at the line origin and takes no
part in the columns, which is the way to run one wide line across a block of aligned ones.

Write a second aligner where a second column starts. The span between two aligners is a box as wide as
the widest line's content in that span, and it is the `al` of the aligner at its right end that places
the content inside it. For a table of values whose columns should stand at fixed positions instead of
fitting the content, use the tab, `Sp (t)`, described in `references/catalogue/Symbols.md` under `Sp`.

# Chemistry

How to write the chemistry Radical Pie draws: structural formulas with bond sites, condensed formulas
in chemistry mode, reaction and equilibrium arrows, and orbital diagrams. Every rule below is taken
from a file Radical Pie wrote for the site's chemistry examples, or from a rendering made while
writing this page; each one is cited where it is stated.

## Contents

- [Chemistry mode is four roles](#chemistry-mode-is-four-roles)
- [Charges, isotopes and states of matter](#charges-isotopes-and-states-of-matter)
- [The bond site](#the-bond-site)
- [The fifteen bond kinds](#the-fifteen-bond-kinds)
- [Angles and length](#angles-and-length)
- [Chains and branches](#chains-and-branches)
- [Rings](#rings)
- [Saturated and heteroatom rings](#saturated-and-heteroatom-rings)
- [Placing the atom in a neighbour group](#placing-the-atom-in-a-neighbour-group)
- [Panels and callouts on a bond site](#panels-and-callouts-on-a-bond-site)
- [Reactions](#reactions)
- [Equilibria](#equilibria)
- [Orbital diagrams](#orbital-diagrams)
- [Colour, spacing and the things no fixture shows](#colour-spacing-and-the-things-no-fixture-shows)

## Chemistry mode is four roles

CHEM mode is an editor mode. In the file it survives as nothing but the roles on the symbols, so
writing the file directly means assigning them yourself. Four roles carry a condensed formula.

`ro='chem'` on every element letter. It sets the upright style and puts a little space between a
preceding number and the element, which is why a coefficient needs no `Sp` after it (the
documentation's Role Style page, Chemistry Mode). Letters that share the role share one symbol: the
site's Photosynthesis equation, line 10, writes `Sb (ro='chem') {s{"CO"}}`, one symbol for two
letters, and `Skill/RadicalPie/references/examples/SaltDissolution.pie` writes `s{"NaCl"}` for four.

`ro='nmbr'` on a coefficient, written as a plain symbol before the formula, as the site's
Photosynthesis equation does.

`Sc` with a `'subs'` group on every subscript, written after the element it counts. Version 1.15
subscripts digits automatically as they are typed, and what it leaves in the file is an ordinary
script structure and nothing else: a multi-digit subscript is one symbol, `s{"12"}`, not two digits.
The site's Photosynthesis equation shows both.

Version 1.15 also added `pf` and `tf` on a `Sb`, fine control over the width of its digits: `pf`
gives each digit its own natural width and `tf` keeps every digit the same width and trims no space
around the run, against the default of a shared width with the space at each end of the run trimmed.
Neither is set on a coefficient or a subscript in any of the site's chemistry equations, so leave both
unset unless a caller asks for figures that line up or read naturally.

`ro='oper'` on the `+` between species, as the site's Photosynthesis equation does.

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
	Sb (ro='chem') {s{"O"}}
}
```

## Charges, isotopes and states of matter

A charge is a `Sc` with a `'sups'` group holding the sign as `ro='unry'`, written after the element.
The unary role keeps the sign tight against the number that may precede it.

A mass number is a script attached forwards instead of backwards: `Sc (pr,ns)` before the element.
The site's FDG equation, lines 124 and 144, writes the 18 of fluorine-18 that way. `pr` attaches
the script to what follows, and `ns` disables the mark slant.

None of the site's chemistry equations shows a state of matter, so the role is a choice. Rendering
`Na(aq) + Cl` with the label in each candidate role settles it: with `ro='text'` the `'oper'` that
follows loses its spacing and the result reads `Na(aq)+Cl`; with `ro='pnct'` it loses the space after
the operator; with `ro='unit'` the label gets a thin space before it and the operator keeps its
spacing on both sides, giving `Na (aq) + Cl`. Write a state of matter as `Sb (ro='unit') {s{"(aq)"}}`.
`Skill/RadicalPie/references/examples/SaltDissolution.pie` is the worked case.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
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

## The bond site

A `Bd` is one atom and the bonds that leave it. Seven directions leave an atom
(the documentation's Bonds page). Six of them own a group that holds the atom at the far end:
`'uppr'`, `'uplf'`, `'uprt'`, `'lowr'`, `'lwlf'` and `'lwrt'`. The seventh points right, has no group
of its own, and is named by the group type `0`; it joins the bond site to whatever follows in the
enclosing group.

No direction points left. An atom to the left of a bond site, joined by a horizontal bond, is its own
bond site written before it, and its rightward bond (type `0`) reaches the atom that follows. The
site's Methanol, AceticAcid and EthylAcetate equations all begin this way: a hydrogen bond site with
one rightward bond, then the carbon's bond site. Putting the left atom in `'uplf'` or `'lwlf'` draws
it on a diagonal.

Two data lists configure it.

The first `u32[2]` list holds one pair per bond drawn, each pair a group type and a bond kind. A
neighbour group with no pair in the list gets no bond line. A pair whose group is absent draws a stub
that ends in nothing, which is how a ring is closed.

The second `u32[2]` list is optional and holds one pair per bond whose angle is not the default 45
degrees, each pair a group type and `'step'` or `'shal'`. Only the four diagonals take an angle.

The site's Methanol equation is the smallest complete example: one bond site for the hydrogen
on the left, one for the carbon with its two hydrogens and its rightward bond, and a plain
`Sb (ro='chem') {s{"OH"}}` for the last atom.

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
		u32[2]{{'uppr','sing'},{'lwlf','sing'},{'lwrt','sing'},{0,'sing'}}
		u32[2]{{'lwlf','shal'},{'lwrt','shal'}}
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
		Gr (t='lwlf',al='rght')
		{
			Bg {}
			Sb (ro='chem') {s{"H"}}
		}
		Gr (t='lwrt')
		{
			Bg {}
			Sb (ro='chem') {s{"H"}}
		}
	}
	Sb (ro='chem') {s{"OH"}}
}
```

Radical Pie draws no implicit hydrogens and no bare skeletal vertex. Every atom in the site's
fourteen chemistry equations carries its own letter, and every hydrogen that appears is a group of
its own with its own bond. Leaving a hydrogen out draws nothing in its place, so a structure with
implicit hydrogens is written by simply not giving them bonds. A hydrogen count that belongs to the
label rather than to the drawing goes into the group as text, `s{"CH"}` with a subscript, the way
the site's Acetone equation, line 40, writes a methyl.

## The fifteen bond kinds

Rendering one rightward bond of each kind gives the picture the specification's table names:

| Kind | Drawn |
| --- | --- |
| `'sing'` | One line. |
| `'doub'` | Two lines. |
| `'trip'` | Three lines. |
| `'hevy'` | One thick line. |
| `'wavy'` | One wavy line, for undefined stereochemistry. |
| `'part'` | One dashed line. |
| `'prd1'` | Two lines, the second dashed, on one side of the shaft. |
| `'prd2'` | Two lines, the second dashed, on the other side. |
| `'prt1'` | Three lines, the first dashed. |
| `'prt2'` | Three lines, the last dashed. |
| `'prt3'` | Three lines, the middle one dashed. |
| `'swgo'` | Solid wedge, narrow at the central atom, coming out of the page. |
| `'swgi'` | Solid wedge, narrow at the far atom, going into the page. |
| `'dwgo'` | Dashed wedge outward. |
| `'dwgi'` | Dashed wedge inward. |

`'prd1'` and `'prd2'` differ only in which side of the shaft carries the dashed line, so a
delocalised ring picks the variant that puts the dashed line inside the ring, one bond at a time.
The site's Orthoxylene equation does exactly that: `'prd2'` on the three bonds of one half
and `'prd1'` on the three of the other, which renders as a hexagon with every dashed line inboard.

Capitalising the first letter of a bond kind makes the bond long, `'Sing'` against `'sing'`. Reach for
it when the drawing needs room: the site's Isopropyl Alcohol equation, line 11, uses three long
bonds so the two methyl groups clear the hydroxyl, and the site's FDG equation uses long bonds and a
long heavy bond to make the pyranose ring come out regular.

## Angles and length

The default diagonal is 45 degrees. `'step'` steepens it towards vertical and `'shal'` flattens it
towards horizontal; the defaults are 60 and 30 degrees and the design can change both
(the documentation's Bonds page). Rendering the same bond site at all three angles shows a V that
narrows, stands and spreads.

Two habits in the fixtures are worth copying. A trigonal atom drawn with a bond up and two down uses
`'shal'` on both lower bonds so the three bonds sit near 120 degrees apart (the site's Ammonia
equation, line 12, and its Acetone equation, line 12). A methyl drawn with three hydrogens takes
`'step'` on two of them and `'shal'` on the one pointing away from the rest of the molecule, as both
methyl groups of the site's isopropyl alcohol do.

A request for a wide or a shallow V is `'shal'` on the skeleton bonds themselves, the two that carry
the rest of the molecule, and not on the hydrogens: the site's isopropyl alcohol flattens the
central carbon's two lower bonds, which are the ones the methyl groups hang from, and leaves the
outer hydrogens their own `'step'` and `'shal'`.

A skeleton whose branch carbons carry their own substituents takes the long bond kinds, `'Sing'` and
`'Doub'`, on the central carbon's bonds, or the outer atoms crowd the centre; the site's isopropyl alcohol
writes `'Sing'` on all three of the central carbon's bonds.

## Chains and branches

A chain is a run of bond sites side by side in one group, each joined to the next by its `0` bond.
The site's Ethyl Acetate equation and its R-134a equation are two of these. A run ends where the `0`
bonds stop: the site's R-134a equation ends with a plain `Sb (ro='chem') {s{"H"}}`, and the site's
Ethyl Acetate equation ends with a bond site whose pair list has no `0` in it.

A branch is a bond site nested inside a neighbour group. The site's isopropyl alcohol puts a
whole methyl bond site inside the central carbon's `'lwlf'` group, and the site's Ethyl Acetate
equation puts a three-atom chain inside a `'lwrt'` group. Nesting is the only mechanism; there is no
reference from one bond site to another.

Decide per atom whether to expand it or condense it. The site's Acetic Acid equation spells the
methyl out as a bond site with two hydrogen groups, and the site's Acetone equation writes the same
group as the text `H₃C` inside one neighbour group. Expanding shows the geometry; condensing keeps
the drawing narrow. Example 26 in `Examples.md` writes the condensed acetic acid and sets it against Radical
Pie's expanded one.

## Rings

A ring is a chain of nested bond sites that walks round the ring, plus one closing bond drawn into an
empty group. Walk the ring in one direction, nesting each atom inside the previous atom's neighbour
group, until the last two atoms are adjacent on the page; then give one of them a bond whose group is
present but empty, `Gr (t='uppr') { Bg {} }`. The stub lands on the atom already drawn there.
The site's Phenol equation, lines 99 to 102, is that empty group, and the site's Orthoxylene
equation closes the same way.

Benzene, as both those files draw it, is written from the lower-left carbon:

1. The root bond site is the lower-left carbon: `'uppr'` to the upper-left carbon, `'lwrt'` shallow to
   the bottom carbon, `'lwlf'` shallow to its own hydrogen.
2. Inside `'uppr'`, the upper-left carbon: `'uprt'` shallow to the top carbon, `'uplf'` shallow to its
   hydrogen.
3. Inside `'uprt'`, the top carbon: `'uppr'` to the substituent, `'lwrt'` shallow to the upper-right
   carbon.
4. Inside `'lwrt'`, the upper-right carbon: `'uprt'` shallow to its hydrogen, and nothing else.
5. Back at the root, inside `'lwrt'`, the bottom carbon: `'uprt'` shallow to the lower-right carbon,
   `'lowr'` to its hydrogen.
6. Inside that `'uprt'`, the lower-right carbon: `'lwrt'` shallow to its hydrogen and `'uppr'` to an
   empty group, which is the sixth ring bond closing onto the upper-right carbon.

Alternate `'doub'` and `'sing'` round the six ring bonds for a Kekulé structure, or use `'prd1'` and
`'prd2'` throughout for the delocalised one. Substituting the ring is a change to step 3 alone: the
site's Phenol equation puts `OH` there, `Skill/RadicalPie/references/examples/Toluene.pie` puts `CH₃`.

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
```

## Saturated and heteroatom rings

The walk above gives the hexagon benzene is drawn as, an apex at the top and one at the bottom, and
the fixtures hang one substituent on each ring atom, on the direction that points away from the ring.
A sugar and a saturated ring want two on most atoms, one above the ring and one below it, which needs
the hexagon turned the other way: apexes left and right, top and bottom edges horizontal. Radical Pie
builds that one from two bond sites side by side on one line, each drawing half the ring.

A bond site placed after another on the same line closes a ring. The left site owns the left apex and
the two atoms diagonally right of it; the right site owns the right apex and the two atoms diagonally
left of it; the two halves are joined by the `0` bonds of the left site's branches, which run
rightwards into the atoms the right site holds in its `'uplf'` and `'lwlf'` groups. The hexagon that
comes out has its apexes left and right and its top and bottom edges horizontal, which leaves
`'uppr'` and `'lowr'` free on the four atoms that are not apexes. That is the Haworth projection.

The site's FDG equation is the worked case Radical Pie wrote. Its left site (line 12) runs
`'uprt','Sing'` up to the top-left carbon and `'lwrt','Swgo'` down to the bottom-left one; the
top-left carbon continues with `{0,'Sing'}` (line 30) into the ring oxygen, which the right site
holds in its `'uplf'` group, and the bottom-left carbon continues with `{0,'Hevy'}` (line 68) into
the carbon the right site holds in its `'lwlf'` group. The right site (line 87) closes both with
`'uplf','Sing'` and `'lwlf','Swgo'`. Capitalising a bond kind makes it long, and the long bonds are
what give the ring its height; the heavy and wedge bonds are the Haworth convention for the edge
nearest the reader. The substituents sit in `'uppr'` and `'lowr'` on those four atoms, some of them
inside the ring outline, and the design values `V (d='bond',n='wgap')`, `n='hlln'` and `n='dlln'`
(lines 5 to 7) lengthen the bonds to make room for them. The same file with an empty design renders
117.8 by 130 points instead of 139.7 by 144, and the two substituents inside the ring overlap the
ring bonds. Tune a crowded ring with those three values, or keep the ring's inside empty.

The skeleton below is that construction with nothing on it: six carbons, no substituents, no design.
Example 32 in `Examples.md` is the same ring with two hydroxyls on it.

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
		u32[2]{{'uprt','Sing'},{'lwrt','Sing'}}
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
				u32[2]{{0,'Sing'}}
				Gr
				{
					Bg {}
					Sb (ro='chem') {s{"C"}}
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
}
```

A ring atom that carries nothing is a plain `Sb (ro='chem')` inside the neighbour group; it becomes a
`Bd` of its own as soon as it needs a bond, which is how the two `0` bonds and every substituent are
written. A heteroatom is the same thing with another letter: the site's FDG equation puts `O` in the
right bond site's `'uplf'` group and the ring is a pyranose.

A line of text under the drawing is a second line of the main group, `Bg (lg=30.0) {}` and then the
words as `ro='text'`. `Gr (al='cent',ba='frst')` on the main group centres that line under the
drawing and keeps the equation's baseline on the first line rather than the last.

## Placing the atom in a neighbour group

A neighbour group is laid out as a line of its own, and `al` on the group says where the bond meets
it. A group on the left of the atom that reads right to left, such as `H₃C`, takes `al='rght'` so the
bond touches its right edge, as in the site's Acetone equation. A group under the atom takes
`al='cent'` to sit squarely beneath the bond, as in the site's R-12 equation. The default puts the
bond at the left edge, which is what a group to the right of the atom wants.

## Panels and callouts on a bond site

A bond site carries seven anchor types of its own, which the specification's anchor table does not
list and which every chemistry file Radical Pie wrote uses. Each one boxes one part of the site.

| Anchor type | The box it gives |
| --- | --- |
| `'bond'` | the whole site, the atom and all six neighbour groups |
| `'bdup'` | the `'uppr'` group |
| `'bdur'` | the `'uprt'` group |
| `'bdul'` | the `'uplf'` group |
| `'bdlw'` | the `'lowr'` group |
| `'bdll'` | the `'lwlf'` group |
| `'bdlr'` | the `'lwrt'` group |

Every one of the seven has four anchors, the corners of its box: 0 bottom-left, 1 bottom-right, 2
top-left, 3 top-right, measured in `references/AnchorAtlas.md`. A drawing object connects two
opposite corners, so `u32{'bond','bond'} i32{2,1}` is the box of the whole site and
`u32{'bdur','bdur'} i32{2,1}` the box of the group up and to the right of the atom. Naming two
different types spans from one box to the other: `u32{'bond','bdup'} i32{2,1}` runs from the site's
top-left corner to the bottom-right corner of the group above the atom, which is a panel as wide as
the site and as tall as what stands above it.

Index 4, a direction whose neighbour group is absent, and any four-letter name outside the seven all
crash Radical Pie with an access violation rather than raising the invalid-data dialog, and the
validator refuses all three, so take the name from the table above. A bond site nested
inside a neighbour group keeps all four indexes of every one of these types, which a structure's
type `0` anchors do not.

The site's Orthoxylene equation, lines 6 to 22, draws a dashed rectangle round each methyl,
one with `u32{'bond','bdup'}` and one with `u32{'bdur','bdur'}`; its Amino Acid equation, lines 16 to
42, puts a rounded panel behind each of the three groups of an amino acid. A panel is a drawing object, so it is
written before the main group and its fill sits behind the letters. Its caption needs no arrow: an
annotation group hung on the panel's own `'anno'` anchor sits against it, index 1 above, index 0
below, 2 left, 3 right and 4 over the centre.

Two panels share one caption when the two arrows converge on it. Each arrow runs to the same rail and
carries the `f{}` offset that brings its rail end to the meeting point, `f{0.0,11.42}` on one and
`f{0.0,-17.97}` on the other in the site's ortho-xylene drawing, and the caption hangs on one of the
two arrows. An arrow that points into a drawing starts from open space, the caption group's own type
`0` anchor or a rail, never from a neighbouring atom, or the line crosses the bonds between the two.
The connector section of `references/StructureCatalogue.md` has the fence for both.

```pie
// Radical Pie Equation

D
{
}
Rr $panel (f,fpi=9,s,spi=5)
{
	X
	{
		ref{$amine,$amine}
		u32{'bond','bond'}
		i32{2,1}
	}
}
Gr
{
	Bg {}
	Bd $amine
	{
		u32[2]{{'uplf','sing'},{'lwlf','sing'},{0,'sing'}}
		Gr
		{
			Bg {}
			Sb (ro='chem') {s{"N"}}
		}
		Gr (t='uplf',al='rght')
		{
			Bg {}
			Sb (ro='chem') {s{"H"}}
		}
		Gr (t='lwlf',al='rght')
		{
			Bg {}
			Sb (ro='chem') {s{"H"}}
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
}
Gr (as=0.6875,t='anno',al='cent')
{
	Bg {}
	Sb (ro='text') {s{"amino"}}
	Bg {}
	Sb (ro='text') {s{"group"}}
	X
	{
		ref{$panel}
		u32{'anno'}
		i32{1}
	}
}
```

## Reactions

A reaction arrow is an `Ar`. The first `u32` list holds one entry per arrow, `'long'` for a
full-width arrow. One further `u32` list follows per arrow and holds that arrow's charms, the
arrowheads and other marks on its shaft. A `'uppr'` or `'lowr'` subgroup holds a label, and the label
is what stretches the arrow to fit.

The site's Photosynthesis equation, lines 31 to 40, is the whole pattern: `u32{'long'}`,
`u32{'rarw'}`, and a `'uppr'` group with `al='cent'` holding the word light as `ro='text'`. Put a
catalyst in the upper label and a temperature in the lower one, both `al='cent'`; a temperature is
`ro='nmbr'` followed by `ro='unit'`.
`Skill/RadicalPie/references/examples/CatalyticHydrogenation.pie` is the worked case.

The charm list is read left to right with an alignment cursor that starts at right. `'left'`,
`'cent'` and `'rght'` in the list move the cursor, and every other value drops a charm at the cursor.
Every charm draws wherever the cursor is, so the cursor and nothing else decides which end a charm
lands on: `u32{'rarw'}` alone puts the head at the right end, and a charm meant for the left end needs
the cursor moved first. `references/StructureCatalogue.md` under `Ar` lists all forty charms and the
lengths the labels give the shaft.

## Equilibria

An equilibrium arrow is one `Ar` with two `'long'` arrows and one charm each: a right-pointing harpoon
on the upper arrow and a left-pointing harpoon on the lower one. Give the lower arrow's charm list a
`'left'` before the charm. Without it the cursor is still at the right end and `u32{'luhp'}` draws the
left-pointing harpoon there, both barbs at the same end of the arrow, which is not an equilibrium.

Which harpoon goes below decides how the arrow reads. Rendering the three combinations side by side:
`'ruhp'` over `'left','luhp'` puts both barbs on the inside; `'ruhp'` over `'left','ldhp'` puts them
on the outside and is the ⇌ of chemical equilibrium; `'rarw'` over `'left','larw'` gives the
double-headed ⇄ that some houses use for a reversible step.

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
		Gr (t='uppr',al='cent')
		{
			Bg {}
			Sb (ro='chem') {s{"Fe"}}
		}
	}
}
```

## Orbital diagrams

An orbital is a `Bx` around a group holding the electrons as arrow characters,
`Sb (ro='arrw') {s{"↑↓"}}` for a filled orbital and `s{"↑"}` for a half-filled one. Both arrows go in
one symbol; the box sizes itself to the content.

A half-filled box comes out narrower than a filled one, which makes a row of them ragged. Put a
horizontal phantom of the missing arrow in it, `Ph (t='horz')` holding `s{"↓"}`, and every box in the
row is the same width.

Lay the levels out on an `Mx`, one row per level with the highest energy on top, one column for the
label and one for each orbital. Set `al='left'` so the labels align, `eh` for equal row heights and
`ew` for equal column widths. Level labels are `ro='text'`. Entries are listed row-major: label,
boxes, next label, boxes. An entry with no content is an empty `Gr { Bg {} }`.

`Skill/RadicalPie/references/examples/OxygenOrbitals.pie` is oxygen's ground state on that plan, 1s
and 2s filled and 2p holding one pair and two unpaired electrons.

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
			Sb (ro='arrw') {s{"↑"}}
			Ph (t='horz')
			{
				Bg {}
				Sb (ro='arrw') {s{"↓"}}
			}
		}
	}
}
```

## Colour, spacing and the things no fixture shows

`pi` on a `Bd` sets the palette index of its bond lines while the atom letters stay black. The
site's FDG equation puts `pi=4` on every bond site and renders with red bonds.

The design carries bond values of its own, `V (d='bond',n='wgap')`, `n='hlln'` and `n='dlln'`, as the
site's FDG equation does. The `'bond'` domain is missing from the specification's table of design
domains and the executable both writes and accepts it. Leave the design block empty unless the caller
supplies a design.

`Sb (ro='bond')` is a bond drawn inline between two condensed groups rather than by a bond site. The
site's FDG equation writes it with an empty string, which the specification's `Sb` section forbids
and the executable accepts. What belongs in the string is one of the twelve bond characters the Radical
font keeps in the private use area, U+EE30 single, U+EE31 double, U+EE32 triple, U+EE33 quadruple,
U+EE34 to U+EE39 the partial forms, U+EE3A long single and U+EE3B long double. They are cut for the job:
measured 2026-09-13 at 11 pt, the bar of U+EE30 in `HOH` sits 3.6416 pt above the baseline, half the
capital height of the `H`, while an em dash in the same place sits at 2.7560 pt, the math axis, so
`Sb (ro='bond') {s{"—"}}` draws its bond 0.886 pt low. Write the character itself in the UTF-8 string;
the catalogue's `Sb` entry has the list and a fence. An em dash still renders and still breaks no rule,
and a quadruple or a partial bond has no other spelling at all.

None of the site's chemistry equations draws a lone pair. A mark on the element does it:
`Sb (ro='chem') {s{"N"} Mk {u32{0x308}}}` renders as `N̈`, two dots over the letter. `un` on the mark
puts it under the character instead (catalogue, `Mk`). Dots at the sides of a letter need a different
structure and no fixture shows one.

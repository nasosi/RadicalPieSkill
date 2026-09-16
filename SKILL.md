---
name: radical-pie
description: Write, validate and emit Radical Pie equations, the OpenDDL `.pie` format the Radical Pie equation editor saves, including the SVG comment carrier that Radical Pie and InkRadix exchange and the mapping from LaTeX constructs to Radical Pie structures. Use this whenever the user mentions Radical Pie, a `.pie` file, InkRadix, or the Radical Pie Word or PowerPoint add-in, and whenever an equation has to reach Word, SVG, Inkscape or LaTeX through Radical Pie, including when the user only says "equation" or "formula" alongside any of those. Do not use it for plain LaTeX or MathML work that never touches Radical Pie.
---

# Radical Pie equations

Radical Pie is a Windows equation editor. Its native format is OpenDDL text in a `.pie` file, and the
same text is embedded in the SVG, PDF and EMF files it exports. You can write that text directly, so an
equation can be produced, checked and handed on without opening the editor. Work in this order:
understand the shape of a file, write it, validate it, then emit it in the form the document needs.

## The mental model

A file is a design block followed by one main group:

```pie
// Radical Pie Equation

D
{
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

Five ideas cover almost everything.

**A group is a run of content.** `Gr` holds a sequence of symbols and structures laid out left to right. The main
equation is a group; so is every subgroup inside a structure. The first child of every group is `Bg {}`, which begins a
line. A second `Bg` in the same group begins a second line, and that is how a multi-line equation is written: one group,
several `Bg`, with an `Al` on each line marking the column they align on.

**A symbol is one or more characters with one role and one style.** `Sb {s{"xy"}}` is a symbol whose text is a string
data list. Adjacent characters that share a role and a style belong in the same `Sb`; a change of either starts a new
one. The role drives spacing and behaviour, the style drives the glyphs.

**A structure holds typed subgroups.** `Fr` holds `numr` and `dnom`; `Sc` holds `subs` and `sups`; `Rd`
holds a radicand and an optional `degr`; `It` and `In` hold an iterand or integrand plus `lowr` and
`uppr`; `Dv` holds a dividend and a `quot`; `It` also takes a `mdfr`; `Wm` holds its content and an
optional `labl`. The subgroup's type is its `t` property, and its position in the parent follows from
that type rather than from its order.

**Scripts attach backwards.** `Sc` applies to the structure immediately before it, so a superscript is
written as the base symbol followed by the script structure. Nothing wraps the base. Set `pr` on the
`Sc` to attach it to the structure after it instead, for an isotope number before an element.

**Properties are written in parentheses, data in braces.** `Fr (t='diag',sm)` sets two properties, and a flag written
with no value is true. A four-character literal in single quotes, `'diag'`, is a `uint32` value. Data lists are typed:
`s{"text"}`, `u32{0x5B,0x5D}`, `u8{14,6,255,255}`, `i32{0}`, `f{12.0}`, and `u32[2]{{0,'sing'}}` for a list of pairs.

The five file-level sections, in order, are the design block, background drawing structures, the main group,
annotation groups (`Gr (t='anno')`), and foreground drawing structures; only the main group is required.

## Writing an equation

1. Decide the mathematics first, in LaTeX or in words, and settle what each token is: variable,
   number, operator, relation, function name, unit, text. Where the request leaves a placement open,
   an arrow's end, the term a note points at, take the convention the references give, list every such
   decision in the reply, and ask the caller only when the caller has said to ask.
2. Pick the structures with `references/LatexRecipes.md`, then read the catalogue family file of each one you
   have not used: it lists every property's type, default and allowed values, with a validated example.
3. Write the file: the line `// Radical Pie Equation`, then `D {}`, then the main group, indented with tabs as
   Radical Pie does. Leave the design block empty unless the caller supplies a design; an empty design renders at
   the factory design, and a document's own design goes in every equation of it (`references/OutputForms.md`).
4. Validate it with `python scripts/Validate.py MyEquation.pie`, run from this skill folder with the file's own path,
   absolute or relative to the shell's directory, as every command here is. It prints `OK <file>`, or one line per
   violation as `file:line:col path: message [section]`. The path is the route through the structure tree, such as
   `Gr/Fr/Gr(t='dnom')`, and the section names the specification part the rule comes from. Fix by the path, and read
   that structure's catalogue entry; `references/Pitfalls.md` covers the mistakes those messages report.
5. Render it where Radical Pie is installed, `python scripts/Render.py pdf MyEquation.pie MyEquation.pdf`, a form you
   can look at, and recheck the request clause by clause against the picture: each clause is visible or named as not
   done and why, then emit in the document's form. Where the render is off, read the hints file of the domain it is
   off in. Append one line to `RadicalPieFeedback.md` beside the output when the skill fell short, by the rules in
   `references/Feedback.md`.

## Roles and styles

The role is the single most important choice, because it sets the spacing that makes output look
typeset. Radical Pie assigns these itself while a user types; writing the file, you assign them.

| Content | Role | Note |
| --- | --- | --- |
| Variables, letters, anything with no better role | `'math'` | The default, italic. |
| Digits and numbers | `'nmbr'` | |
| Binary operators, `+ − × · ±` | `'oper'` | Every minus sign, a leading one included. |
| Relations, `= < ≤ ≈ ∈` | `'rltn'` | |
| `∂`, `∇`, and a charge or sign that hangs on a symbol | `'unry'` | Tighter than `'oper'`. |
| Function names, `sin`, `log`, `det`, `lim` | `'func'` | Upright, with space either side. |
| Punctuation | `'pnct'` | Commas and full stops. A bracket is a `Br`, never a `'pnct'` pair. |
| Ellipses, `⋯ ⋮ ⋱` | `'elps'` | Between factors, with no operator dot either side. |
| Words and phrases | `'text'` | |
| Chemical elements | `'chem'` | Upright, spaced after a number. |
| Physical units | `'unit'` | No `Sp` before it; the role spaces itself. |
| Arrow characters | `'arrw'` | |
| Bond characters | `'bond'` | |

Running text keeps its punctuation and word gaps inside the `'text'` string, `"Let "`, `", and let "`;
write no separate `Sp` between words and no `'pnct'` full stop in prose, and give `mod` the role `'func'`.

Each role has a default style, so `st` is only ever written to override it:

| Role | Default style |
| --- | --- |
| `'math'` | `'ital'` italic |
| `'oper'`, `'rltn'`, `'unry'`, `'arrw'`, `'bond'` | `'sym1'` symbol (measured; the specification says otherwise) |
| every other role | `'uprt'` upright |

The overrides that come up most: `st='bold'` for a bold vector, `st='mono'`, `st='sans'`, `st='frkt'`, and
`st='uprt'` on a `'math'` symbol for a factorial. A double-struck, script or bold script character takes the
code point and the style together, `Sb (st='doub') {s{"ℝ"}}`: the styles draw `ℕ ℤ ℚ ℝ ℂ`, the double-struck
digits from U+1D7D8, `ℬ ℋ` and the Script block from U+1D49C, `𝓘` and the Bold Script block from U+1D4D0,
and nothing else, so `R` with `st='doub'` and `𝟙` with `st='uprt'` both render plain. A differential `d` is
plain italic on the site; `st='uprt'` is a house style. The 22 styles are listed in the catalogue's `Sb` entry.

Greek follows mathematical convention and splits by case: a small Greek letter is italic, `st='itgk'`,
and a capital Greek letter is upright, `st='grek'`. The bold pair is `st='bigk'` and `st='bdgk'`.

## Output forms

`references/OutputForms.md` gives every form in full, with the Word placeholder table and each pipeline's checks.

- **A `.pie` file**, the default, handed over as it stands. **The SVG carrier**, either direction: `python scripts/WrapSvg.py Eq.pie Eq.svg`.
- **A rendered SVG, PDF or EMF**, written by Radical Pie: `python scripts/Render.py pdf Eq.pie Eq.pdf`.
- **A Word document** of OLE objects: `python scripts/Word.py embed Draft.docx Out.docx eq=Eq.pie`. **A PowerPoint deck** of the same objects: `python scripts/PowerPoint.py embed Draft.pptx Out.pptx eq=Eq.pie`.
- **A LaTeX document**, a `\pie{key}` each: `python scripts/Latex.py build Draft.tex Out/ eq=Eq.pie`.

## What is in this skill

- `references/catalogue/Overview.md` — how a file is put together, and which family file holds which structure; open it first.
- The catalogue's families, all 39 structures with a validated example each: `references/catalogue/Symbols.md` (Sb, Sp, Bg, Sl, Ng, Pr, Mk, Sc),
  `references/catalogue/Groups.md` (Gr, Al, St, Ph), `references/catalogue/Brackets.md` (Br, Bx, En, Kt), `references/catalogue/Fractions.md` (Fr, Dv, Rd),
  `references/catalogue/Operators.md` (In, It), `references/catalogue/Matrices.md` (Mx), `references/catalogue/Arrows.md` (Ar, Wm), `references/catalogue/Bonds.md` (Bd),
  `references/catalogue/Drawings.md` (Ln, Cn, Qe, Zg, Jo, Rt, Rr, El), `references/catalogue/Annotations.md` (X, and Feynman diagrams), `references/catalogue/Design.md` (D, F, M, P, V).
- `references/LatexRecipes.md` — every LaTeX construct and the structure it becomes.
- `references/Chemistry.md` — skeletal formulas, reactions and orbital diagrams; open it for chemistry.
- `references/Examples.md` — thirty-seven worked equations in order of difficulty; copy the closest one, from `references/examples/*.pie`.
- `references/AnchorAtlas.md` — every anchor type and index with its measured position, for drawings; `references/TexSymbols.md` — every TeX name Radical Pie knows, with its character.
- `references/OutputForms.md` — the SVG carrier, rendering, Word, PowerPoint and LaTeX; open it for the form.
- `references/Pitfalls.md` — the mistakes that produce a rejected, crashing or silently wrong file; the hints for one domain each are `references/ChemistryHints.md`, `references/AnnotationHints.md` (annotations, arrows, drawings, rails), `references/LayoutHints.md` (alignment, spacing, brackets, scripts, matrices, designs) and `references/DocumentHints.md` (Word, PowerPoint, LaTeX, SVG).
- `references/EditorFeatures.md` — what the editor does and leaves out; open it for a missing feature. `references/Feedback.md` — send back what the skill got wrong or what cost time, once the task is done; `references/KnownLimitations.md` — what cannot be fixed here, and is never feedback.
- `scripts/Validate.py` — the validator. Run it on anything you write. `scripts/WrapSvg.py` — the SVG carrier both ways, and `Render.py`, `Word.py`, `PowerPoint.py`, `Latex.py`, the four pipelines.

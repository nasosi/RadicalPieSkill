# Output Forms

Every form an equation can leave in, with the command that produces it and the rules each pipeline
enforces. Read the entry for the form the document needs, once the equation validates.

Every command below runs from this skill folder, with the folder's own Python: the pipelines ship inside it,
under `scripts/Tools`, and `pip install -r requirements.txt` is what they need. Inside the development
repository the same pipelines answer to `python -m Tools.Render`, `Tools.Word`, `Tools.PowerPoint` and
`Tools.Latex`, which is the same code by another name.

## Designs

A design belongs to the document and not to the pipeline, whichever form the equations leave in. Nothing
outside a `.pie` file carries one: an equation with an empty `D {}` renders at Radical Pie's factory
design, 11 point text and the factory palette, wherever it is opened, and the design a user has saved as
their own default in the editor applies to a new equation the editor creates and not to a file it reads.

A caller hands a design over in one of three ways. As a `D` block, copied from an equation the document
already has or from the editor's Settings menu, which is the exact text to use. As a description, "Cambria
at 11 point" or "our house blue for the highlighted terms", which becomes an `F` and its `M` structures, a
`V (n='fsiz')` and a `P`; `references/StructureCatalogue.md` gives each of the four structures and
`references/Examples.md` example 35 is a whole one. Or as nothing at all, which leaves `D {}` in every
equation and the factory design in force.

Settle the block once for the document and copy it, character for character, into every equation written
for that document, before the main group of each. Two equations with different designs sit side by side on
the page in different sizes and faces, and a design that reaches only the display equations leaves the
symbols mentioned in the prose looking like another document's.

Render one equation of the set and look at it before writing the rest. A font name Radical Pie cannot
resolve is dropped in silence and the styles fall back, so an equation that renders exactly as it does with
`D {}` is an equation whose design did not take. Aptos, the default font of both Word and PowerPoint, is
one such name until it is installed the ordinary way: it ships as a cloud font Office downloads on demand
rather than an installed font file, so Radical Pie cannot see it and a design that names it falls back
silently like any other unresolved font.

The editor's own two design routes have no pipeline equivalent. Load Design from Equation reads another
equation file's design parameters straight into the current one, a route open only inside the editor. Load
User Default Design and Save User Default Design keep that saved default in
`%appdata%/RadicalPie/design.pie`, a file the pipeline never reads or writes; a caller who wants that
design in a generated file copies its `D` block instead, as above.

**A `.pie` file.** The default. UTF-8 without a BOM, opening with `// Radical Pie Equation`. Radical
Pie opens it by file argument, and `.pie` is associated with the editor.

**The SVG carrier.** Radical Pie and InkRadix pass an equation as an SVG whose first comment holds the
`.pie` text verbatim. Write one with

```
python scripts/WrapSvg.py MyEquation.pie MyEquation.svg
```

and take an equation back out of any SVG that carries one, Radical Pie's own rendered exports
included, by giving the same script the `.svg` first. Hand the carrier to Inkscape with InkRadix, or to
Radical Pie, which replaces the placeholder box with rendered paths on save and keeps the comment.

**A rendered SVG, PDF or EMF.** The render pipeline drives the installed Radical Pie and writes the file
Radical Pie itself saves, native data embedded:

```
python scripts/Render.py svg MyEquation.pie MyEquation.svg
python scripts/Render.py pdf MyEquation.pie MyEquation.pdf
python scripts/Render.py emf MyEquation.pie MyEquation.emf
```

The SVG command prints width, height and the baseline shift in points, the sum of the SVG's own `viewBox`
minimum y and its height; use the PDF for LaTeX and print, the EMF for Office applications. About one
second per SVG, two per PDF or EMF.

Two vendor fixes shape what these bounds mean. Since 1.9.2 an SVG's left and right bounds are no longer
rounded outward to the whole point, so placing a rendering against surrounding content is exact rather than
off by a fraction of a point. Since 1.7 the bounds of every rendered form account for punctuation placed
next to the equation in another application, spacing it as Radical Pie itself would rather than crowding
it.

**A Word document.** Write the document with placeholders where the equations go, with python-docx or
any other tool, then run the pipeline with one `.pie` file per key:

```
python scripts/Word.py embed Draft.docx Final.docx intro=Intro.pie momentum=Momentum.pie
```

Four placeholder forms, following the recipe on Radical Pie's own Word page:

| Placeholder | What it becomes |
| --- | --- |
| `{{pie:key}}` inside a sentence | An inline equation on the text baseline. |
| `{{pie:key|display}}` alone in its paragraph | The equation centred on its own line, in the `Equation` paragraph style. |
| `{{pie:key|numbered}}` alone in its paragraph | As display, plus `(1)`, `(2)` at the right margin from a `SEQ equation` field, and a bookmark `eq_key` over the number. |
| `{{ref:key}}` in text | A `REF eq_key` field showing that number, so write "see equation ({{ref:momentum}})". |

Radical Pie's own numbering goes one level deeper than the pipeline's flat `(1)`, `(2)`: an `(x.y)` style
swaps the `SEQ equation` field for a second counter, `SEQ chapter \c`, whose `\c` switch reads the running
chapter count without advancing it, for a document that numbers its equations per chapter. Inserted
directly from the ribbon rather than through the pipeline, a new equation's initial base font size is that
of the surrounding text, which a pipeline object never relies on since it always carries the design the
caller hands over, `D {}` and the factory 11 point when none is given.

Word lines a picture's bottom edge up with the text baseline, so Radical Pie lowers a newly embedded object
by adjusting its character font position to sit correctly on the line instead, and types a space right
after the object unless a space or punctuation already follows, since without one the next text typed
would inherit that lowered position. Word can still break the line between an equation and the punctuation
that follows it: put the punctuation inside the equation itself, or insert a U+200D between the two to
hold them together.

A symbol the prose mentions is an equation too. A sentence that says "the quantum number *j*" set with the
text font's italic puts a different glyph on the page from the display equations around it, so write that
symbol as a one-symbol `.pie` and mention it with an inline `{{pie:key}}`; then every glyph in the document
comes from Radical Pie. One file serves every mention of the symbol.

A whole sentence can be one equation as well, which is how a theorem statement keeps its own symbols in the
same fonts as its prose. Set the words as `Sb (ro='text')`, with the spaces written inside the strings, and
a letter inside the sentence as `Sb (ro='text',st='ital')`. The role brings no typeface of its own: it draws
from the same fonts as `'math'`, upright where no `st` says otherwise. What it changes is spacing, and the
catalogue's symbol entry gives the rule.

Each equation becomes a Radical Pie OLE object that the author double-clicks to edit in the editor. A key
is a word (`[A-Za-z][A-Za-z0-9_]*`, at most 37 characters) and doubles as the bookmark name, so choose
descriptive ones: `momentum`, `basel_sum`. The `Equation` style is created if the document lacks it, with
a centre tab at half the text width and a right tab at the full width, computed from the page setup, Normal
set as the style of the paragraph that follows it, and spacing before and after close to the body font
size. The pipeline drives the installed Word and Radical Pie invisibly, about twenty seconds plus a second
per equation, and refuses the job before starting Word when a placeholder has no file, a file no
placeholder, a display placeholder shares its paragraph, or a reference names an equation that is not
numbered. `embed` takes `--timeout <seconds>` (default 120) for a document with many objects, since each
one costs Word and Radical Pie real time to create.

A finished document is checked the same way as a deck, with no Word running:

```
python scripts/Word.py check Document.docx
```

It prints one line per embedded object with its size and whether it was drawn, and a last line with the
count.

**A PowerPoint deck.** Write the deck with a text shape where each equation goes, holding `{{pie:key}}`
and nothing else, then run the pipeline with one `.pie` file per key:

```
python scripts/PowerPoint.py embed Draft.pptx Final.pptx maxwell=Maxwell.pie lorentz=Lorentz.pie
```

Each shape is deleted and an equation object takes its left and top, so place the placeholder where the
equation's top left corner belongs and size the shape to the space you are giving it. The object is a
Radical Pie OLE object of the same class Word gets, editable on a double click through the add-in, and it
carries the key as its shape name, which is what the selection pane and the check below show. PowerPoint's
own installer adds one ribbon button, Radical Pie Equation, rather than Word's three, and opening it
directly gives a new equation the base font size of body level 1 text in the current slide's layout master,
the same size an empty `D {}` pipeline object gets in the table below. PowerPoint OLE embedding needs a
very recent build of Microsoft Office (1.9); an older one may not support it at all.

Four things differ from the Word document, each measured against PowerPoint 16.

| | Word | PowerPoint |
| --- | --- | --- |
| Placeholder | Inline, display or numbered, inside the text | A whole shape; no kinds, no numbering, no `{{ref:...}}` |
| An empty `D {}` | Radical Pie's factory 11 point | The base font size of the slide layout's body text |
| The run | Word is invisible | PowerPoint cannot be hidden; a minimised window is on screen |
| Afterwards | The picture holds | An object can collapse to a blank, so the run is guarded |

The collapse is the bug Radical Pie's own PowerPoint page warns of under "Bugs in PowerPoint". PowerPoint
sizes each equation from a metafile it keeps beside the deck, and when a blank one arrives the object
stands at 5 by 7 points showing nothing, for good: no reopen, no save and no repair pass restores it. A
related but different collapse can hit an object at any later save of the finished deck, not only during
embedding: Radical Pie's own page says closing and reopening the file usually restores the size, and when
it does not, opening the one collapsed equation and saving it repairs that object alone. The pipeline
refuses to hand over a deck with a collapsed object, naming the slide and the key, and the same check reads
any deck later, with no PowerPoint running:

```
python scripts/PowerPoint.py check Final.pptx
```

It prints one line per object, `slide 2 maxwell 379.37 by 202.00 pt drawn`, and exits non-zero when one
says `collapsed`. An object whose equation is empty prints `blank` and is not a collapse. A deck the
operator has edited by hand can be checked the same way; repairing one means opening each equation in the
editor and saving it, which is one object at a time, because PowerPoint refuses the verb on a selection.
Update Design and Update Font Size work the same way, one equation at a time from its own context menu,
since PowerPoint has no multiple selection for either command the way Word does.

**A LaTeX document.** Write ordinary LaTeX with `\usepackage{radicalpie}` and put `\pie{key}` where an
equation goes: inline in a sentence, or inside `equation`, `align` or `\[ \]`, so LaTeX numbers and
references display equations itself with `\label` and `\eqref`. `\eqref` needs its own package, `amsmath`,
in the document's preamble, since plain LaTeX does not define it; the generated `radicalpie.sty` asks for
nothing beyond `\usepackage{graphicx}`, which it loads itself. Then, with one `.pie` file per key:

```
python scripts/Latex.py build Draft.tex Out/ ratio=Ratio.pie quadratic=Quadratic.pie --engine lualatex
```

The build exports each equation to PDF through Radical Pie, measures its baseline shift, writes
`Out/radicalpie.sty` defining `\pie` as an `\includegraphics` raised by that shift, and compiles twice
with pdflatex (and lualatex when asked), stopping on the log's first error. About 2.5 seconds per
equation plus a second per compile. Every `\pie{key}` needs a file and every file a placeholder, checked
before anything launches.

Set the symbols the prose mentions as equations as well, one `.pie` holding one symbol behind an inline
`\pie{key}`, rather than as `\textit{j}` in the text font. Measured on 2026-09-12 in a 12-point document
against Radical Pie's 12-point default design: the inline picture sits on the text baseline, its descender
ending where the text italic's does within a tenth of a point, and an italic `j` came out 4.95 points wide
against the text font's 4.68, the dot riding a little lower. The picture is included at its natural size
and does not follow the surrounding font size: inside `\small` the same letter stayed 4.95 points wide
while the text italic beside it shrank to 4.2, so size the design to the body text rather than the other
way round.

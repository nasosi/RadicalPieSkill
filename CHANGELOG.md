# Changelog

## 1.3.1 — 2026-10-22

- `python scripts/Render.py png Eq.pie Eq.png` renders the equation to a PNG at 300 dpi, through Inkscape 1.x,
  which the skill needs for this form only, and the skill looks at the PNG to check a render.
- A render that fails leaves no output file, so an older picture under the same name is never mistaken for
  the new one.

## 1.3.0 — 2026-10-21

- The skill targets Radical Pie 1.16 and needs it. A design names a font by its full name, as
  `"New Computer Modern 10 Book"`; the stem of a `.ttf` or `.otf` file, `"NewCM10-Book"`, resolves too and
  is saved as the full name. The file name with its extension and the stem of a collection do not resolve.
  `references/catalogue/Design.md` gives the rule and the numbers 1.16 writes back for the fonts it knows.
- `python scripts/Fonts.py find <words>` lists the installed fonts with the full name to write in `F` and the
  file stem that resolves to it. `python scripts/Fonts.py check Eq.pie` says for each font slot of a design
  whether this machine resolves it, to which installed file, whether it still has to be imported, or that
  Radical Pie would draw it in Times, with the closest names.
- A font Radical Pie cannot find is drawn in Times, and 1.16 saves it as Times for good. Render, Word,
  PowerPoint and LaTeX write their output with that slot in Times, print one `warning:` line per slot naming
  the closest installed names, and exit 3. The skill then asks the user whether to use one of those names,
  name another font, or keep Times.
- The first render with a font Radical Pie has not used before is right. The SVG, PDF and EMF pipelines wait
  for the import and take the output from a second launch, so an export no longer crashes, fails with an empty
  message or comes back blank when the design names a new font. If the second launch fails, the first
  launch's output is written with a warning saying so.
- A design can set prose in a text family and the mathematics in a math font: the four text styles
  `'uprx'`, `'itax'`, `'bolx'` and `'bitx'` under `V (n='seps') {b{true}}`, with a recipe for Cambria
  Math and Cambria.
- A math font mapped to the italic, bold, Greek or monospace styles draws the mathematical alphabets for
  plain letters. The old Symbol, MT Extra, Webdings and Wingdings fonts draw at their Unicode code points.
  A style map draws from the fonts it lists and from no other, so a map lists its own fallbacks.
- `Sb (of)` draws oldstyle figures. `Mk` gains the eight marks of the 1.16 palette, and
  `references/catalogue/Design.md` lists the eighteen symbols 1.16 adds at Unicode code points, the shuffle
  product U+29E2 among them. The private use area of the Radical font now runs to U+EE77.
- The validator follows 1.16: an `F` holds one string, a known font's `int16` id (-1 to 83) or a 1.15 `uint8`
  number; up to 26 maps; `V (n='escl')`, the External font scale, 0.5 to 2. A design value is a float data
  list, since Radical Pie drops an integer or double one.
- A render waits, up to its timeout, for a font import another Radical Pie on the machine is running, and
  warns when it starts with one still running. A font import that is running when the interpreter is killed
  now finishes, where it used to leave a broken font file that crashed Radical Pie.
- A font database Radical Pie is rewriting or has left unreadable no longer discards a finished output. The
  closest-name suggestions compare family names only, so a missing "Minion Pro Italic" is offered nothing
  rather than "Inter Italic".
- A new known limitation: a damaged font cache crashes the editor.
- `references/Chemistry.md` says every double bond kind draws two equal strokes and that a request for a
  shortened inner stroke is answered with the equal-stroke bond and the shortfall named. The SVG carrier is
  described as Radical Pie's own, to hand to Radical Pie, Inkscape or a later step.

## 1.2.0 — 2026-09-19

- Word numbers equations per chapter. A `{{chapter}}` in a heading shows the chapter's number, and the
  numbered equations after it read `(1.1)`, `(1.2)`, `(2.1)`, with references following. A draft with no
  marker is numbered `(1)`, `(2)` as before.
- Every program a pipeline starts ends with the interpreter that started it, through a Windows job object, so
  Ctrl-Break, a closed console or a killed interpreter no longer leaves Radical Pie, PowerPoint or Word open.
- Word, PowerPoint and LaTeX write their output only when the run has succeeded. A refused or failed run
  leaves the output path as it was, and a failed LaTeX build leaves no PDF.
- A missing input, or one of another format under a `.docx`, `.pptx` or `.tex` name, is one line naming the
  file. Every pipeline refuses an output path that is one of its own inputs; overwriting any other output is
  still allowed.
- PowerPoint says that Radical Pie cannot read an equation however fast the editor leaves, where it sometimes
  said the editor did not start. The time a Word or PowerPoint run may take now grows with its equations.
- A plus or minus sign is `ro='oper'` everywhere, a charge included, as the site writes it; `'unry'` is for
  `∂` and `∇`. A system of equations takes `al='cent'` and a derivation `al='rght'`.
- On a derivation's continuation lines the aligner goes after the relation, so the equals signs stand in one
  column; Example 20 is corrected and the `Al` entry gives the measurement.
- New in the references: a matrix cell is filled with an `Rt (f)` between its grid corners, never a square
  glyph; prose never wraps, so two lines are two `Bg`; the Methanol example is the site's own file; the
  dashed side of a delocalised ring's bonds is named bond by bond.

## 1.1.1 — 2026-09-19

- A comma or a full stop left after an inline equation on a slide now stands against the equation instead of
  a thin space away from it. `references/OutputForms.md` says to write such a mark inside the equation, as
  its last symbol in the punctuation role.
- An inline equation now takes the space the author wrote beside its placeholder as its gap, where it used to
  add a thin space to it. A sentence written as prose, one space either side, reads with the spacing of a
  word.
- A paragraph is opened for an inline equation only where the equation would come within a sixth of the text
  size of the ink of the line above or the line below, and by what it would intrude on that room. An equation
  at the top or the bottom of its text frame opens nothing.
- A tall equation on the line above or below now counts as that line's ink, so tall equations on consecutive
  bullets clear each other, and the space between two paragraphs is opened once by the larger of their two
  needs.
- An inline equation that does not fit in the room its line has left now moves to the next line, as a word
  that does not fit does, and the run says so. The run no longer refuses a sentence for the width of one
  line; it refuses only an equation wider than the whole text area.
- Equations can now be placed in one of a slide layout's own placeholders. The run turns that shape's shrink
  text on overflow off, so its text keeps the size the equations were drawn for, leaves the shape ungrouped
  because PowerPoint refuses to group a placeholder, and prints a line for each. The text then keeps the size
  the draft gave it, which is the size the equations are drawn at.
- `references/OutputForms.md` now says what size an empty `D {}` comes out at on a slide: an inline equation
  at the size of the run it stands in, a whole-shape one at the layout's body text size. The slide master is
  never edited for it, and an equation wanted at another size carries a `V (n='fsiz')` of its own.
- A deck whose text runs past the bottom of a shape that carries an inline equation is refused rather than
  handed over. The message names the shape, the overflow in points, and the size PowerPoint's shrink text on
  overflow had been showing the text at before the run turned it off, which is a size the box holds.

## 1.1.0 — 2026-09-18

- A `{{pie:key}}` inside a sentence of a PowerPoint text shape now becomes an equation standing on that
  sentence's baseline, with the text continuing after it, at the size of the run it sits in. A placeholder
  that is the whole text of its shape keeps replacing the shape as before.
- A tall equation makes the pipeline open its paragraph, and the run prints what it set on which paragraph,
  along with the form each placeholder took.
- A text shape and the equations placed in it are grouped, so moving the sentence moves its equations.

## 1.0.1 — 2026-09-17

- The PowerPoint pipeline keeps the placeholder's left and top; before, PowerPoint moved every object as
  it drew, centring it on the placeholder's corner.

## 1.0.0 — 2026-09-16

- First stable version. Checked on a fresh Python 3.14 environment installed from `requirements.txt`,
  and in cold sessions of Claude Code with Sonnet and Opus across SVG, Word, PowerPoint and LaTeX.
- The script command lines, the feedback line's five fields and the `radicalpieskill.off` switch, and the
  folder layout, are stable from here; a change to any of them is a new major version.
- The README names Codex, and any other harness that loads skill folders, as untested.

## 0.10.0 — 2026-09-15

- The reference catalogue is reorganised into `references/catalogue/`, one file per structure family
  (symbols, groups, brackets, fractions, operators, matrices, arrows, bonds, drawings, annotations and
  design), with short hint files for chemistry, annotations, layout and document output.
- Layout details that used to cost a retry are now written down: which side of a bond a partial bond's
  dashes fall on, the spacing a function name needs before a letter, the corner arithmetic that rules a
  matrix into blocks, and the phantom that keeps two bracket pairs the same size, among others.
- The feedback route is limited to what the skill actually fell short on, at most three lines a task,
  and can be turned off per project or everywhere with an empty `radicalpieskill.off` file;
  `references/KnownLimitations.md` lists what a feedback line would only repeat.
- The worked examples that used to be the editor's own sample files are replaced by the skill's own,
  validated and rendered equations.
- Every pipeline now refuses a file the format rejects before it opens anything, and ends only the
  programs it started.

## 0.9.2 — 2026-09-14

- Feedback route: `references/Feedback.md`, the issue form, the changelog.
- The documentation pull script lives in the development repository, not in this folder.
- A prime is the `Pr` structure, not a typed character; every worked example in `references/Examples.md`
  names the file it ships beside its heading.

## 0.9.1 — 2026-09-14

- The centred dot is U+00B7, reported by a user.

## 0.9.0 — 2026-09-13

- First public version, checked against Radical Pie 1.15.
- The four pipelines, render, Word, PowerPoint and LaTeX, ship inside the folder.

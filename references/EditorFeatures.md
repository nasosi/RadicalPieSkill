# Editor Features

Several of the features Radical Pie advertises live in the editor and leave nothing in the file. Read
this list when a caller asks for one, say which of these it is and hand over the `.pie` file; do not
model it.

- **The three editing modes**, math, chemistry and plain text. The editor assigns a role and a style to
  each character as it is typed, by the mode. The file carries the result, per symbol, and no mode of its
  own. The skill assigns the roles and styles the mode would have assigned, which is the whole of what
  changes.

  The three roles `'math'`, `'chem'` and `'text'` are what the three modes come down to in the file.
  Math mode gives ordinary content the role `'math'`, italic by default, and gives a number, an
  operator or a relation the role that fits it instead, which is where the mathematical spacing this
  skill writes by hand comes from when a mode is not doing the writing. In
  chemistry mode Radical Pie gives every Roman letter the role `'chem'` and the upright style, and adds
  a little space before an element name that follows a number or a mathematical name, so a coefficient
  needs no `Sp`. In text mode it gives every character the role `'text'` and the upright style, spaces
  and punctuation included, and lays the run out as running text with no mathematical spacing; a
  variable inside such a run is still `ro='text'`, with `st='ital'` written on it.
- **Function name recognition.** The editor auto-detects hundreds of standard function names as they
  are typed, `sin` and `log` among them, and lets a user define more of its own; none of that reaches
  the file, where a name that behaves as a function is an ordinary `Sb` carrying the role `'func'`,
  whether or not the editor would have recognised it.
- **LaTeX and MathML.** Pasting LaTeX into the editor builds the structures it describes (1.8), and on
  Copy the editor puts LaTeX or MathML on the clipboard (1.3, 1.15), writes it into the `<desc>` of an SVG
  as alternative text (1.10, 1.15), and sets it as the alternative text of an equation embedded in Word
  (1.4). The skill goes the other way, LaTeX to structures by the table in `references/LatexRecipes.md`,
  and generates neither LaTeX nor MathML from a `.pie` file. None of that alternative text exists unless
  Generate alternative text is checked in the Editor Configuration dialog; with it unchecked an embedded
  equation or an exported SVG carries none, and Update Design or Update Font Size (below) generate it for
  whichever equations they touch. Whichever form it takes, this text represents the main equation alone
  (1.3): a drawing object or an annotation never reaches the TeX, the MathML or the alternative text, so an
  annotated equation's clipboard copy or embedded alt text describes only what is inside the main group.
- **Clipboard formats.** Cut and Copy put four formats on the clipboard together: the native `.pie` text as
  `application/radical-pie+openddl` (registered with `RegisterClipboardFormat`), an SVG as `image/svg+xml`,
  an EMF as `CF_ENHMETAFILE`, and TeX or MathML as `CF_UNICODETEXT`, whichever the Clipboard text format
  setting picks. Pasting the native format into a running Radical Pie is a second route into the editor,
  alongside the file argument the pipelines use.
- **Obfuscate rectangular paths**, an Editor Configuration setting that rewrites every perfect rectangle in
  an exported SVG, PDF or EMF into a slightly more complex shape covering the same area, a horizontal
  fraction bar, a negative sign and an absolute value bar among the rectangles it catches, because some PDF
  viewers snap a rectangle's corners to the pixel grid. Turn it off on both sides before comparing a
  rendering path by path against Radical Pie's own, or every rectangle differs for a reason that has
  nothing to do with the equation.
- **Populate Matrix**, which copies the cell holding the caret into every empty cell of the same matrix.
  The result is the same `Mx` entries a caller would type into each cell directly, so write the repeated
  cell into every entry that needs it; there is nothing else to model.
- **Office Math conversion.** Inserting a Radical Pie equation with the cursor immediately after an OMML
  equation, or at the start of the line after a displayed one, initialises it from that equation. The
  skill does not read or write OMML.
- **PowerPoint objects** (1.9), inserted by the PowerPoint add-in. The skill's Word pipeline has no
  PowerPoint counterpart, so a request for slides ends with `.pie` files and the add-in.
- **Update Design and Update Font Size**, the two commands that apply the current default design, or the
  surrounding text's font size, to every equation in a Word selection, and generate alternative text for
  them. Restyling a document is that selection and those buttons, not a rewrite of the embedded files.

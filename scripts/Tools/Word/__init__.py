"""The Word pipeline: a document with `{{pie:<key>}}` placeholders becomes a document with Radical Pie
equations, each a true OLE object of class `RadicalPie.Application.1` and double-click editable through the
Radical Pie add-in. A placeholder is inline, `|display` for its own centred line, or `|numbered` for a
centred line with `(n)` at the right margin; `{{ref:<key>}}` becomes a field over that number.

`Docx.EmbedEquations` is the whole of it. Import it as `from Tools.Word.Docx import EmbedEquations`;
`python -m Tools.Word embed <input.docx> <output.docx> <key>=<file.pie> ...` is the command line over the
same function. Both need Word and Radical Pie installed.
"""

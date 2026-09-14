"""The PowerPoint pipeline: a deck whose text shapes hold `{{pie:<key>}}` becomes a deck of Radical Pie
equations, each a true OLE object of class `RadicalPie.Application.1` and double-click editable through the
Radical Pie add-in. A placeholder shape is replaced whole by the object, at the shape's own position; a deck
has no inline equations and no numbering, so the placeholder carries a key and nothing else.

`Pptx.EmbedEquations` is the whole of it and `Pptx.CheckDeck` reads a finished deck without COM, which is
what the collapse guard is made of. Import them as `from Tools.PowerPoint.Pptx import EmbedEquations`;
`python -m Tools.PowerPoint embed <input.pptx> <output.pptx> <key>=<file.pie> ...` and
`python -m Tools.PowerPoint check <deck.pptx>` are the command line over the two. The first needs PowerPoint
and Radical Pie installed; the second needs neither.
"""

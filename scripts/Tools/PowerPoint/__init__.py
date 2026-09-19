"""The PowerPoint pipeline: a deck whose text shapes hold `{{pie:<key>}}` becomes a deck of Radical Pie
equations, each a true OLE object of class `RadicalPie.Application.1` and double-click editable through the
Radical Pie add-in. A placeholder that is the whole text of its shape is replaced whole by the object, at the
shape's own position; one with text before or after it in its paragraph becomes a gap in that sentence with
the object standing on the sentence's baseline, and the shape and its objects are grouped (ADR-0013). A
placeholder carries a key and nothing else: a deck has no numbering and no references.

`Pptx.EmbedEquations` is the whole of it and `Pptx.CheckDeck` reads a finished deck without COM, which is
what the collapse guard is made of. `Inline` holds the measured rules an inline object is placed by and the
two COM calls that reach `TextFrame2`. Import them as `from Tools.PowerPoint.Pptx import EmbedEquations`;
`python -m Tools.PowerPoint embed <input.pptx> <output.pptx> <key>=<file.pie> ...` and
`python -m Tools.PowerPoint check <deck.pptx>` are the command line over the two. The first needs PowerPoint
and Radical Pie installed; the second needs neither.
"""

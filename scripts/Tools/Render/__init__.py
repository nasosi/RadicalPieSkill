"""The render pipeline: `.pie` text to the pictures Radical Pie itself draws.

`Svg.RenderSvg` renders the SVG, `Export.ExportPdf` and `Export.ExportEmf` the files Radical Pie exports, and
`Png.RenderPng` converts the SVG to a PNG with Inkscape. `python -m Tools.Render (svg|png|pdf|emf) <input.pie>
<output>` is the command line over the four.
"""

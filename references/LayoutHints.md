# Layout hints

Matrix entries are listed in row-major order, and the count must equal `r` times `c`. The
specification says column-major and Radical Pie 1.15 does not; reading them in column order
transposes the matrix silently.

A bracket's subgroups carry `ba='mddl'` in every file Radical Pie writes: `Br { Gr (ba='mddl') { Bg {}
... } }`. A bracket with no `u32` array is a parenthesis pair. A zero for the left or right character
draws nothing on that side.

A `Br` whose group holds only its `Bg` draws a visible empty pair of glyphs, so to anchor a line at the
end of a term, name the term's last structure with `$name` instead of wrapping an empty group in `Br`.

Two bracket pairs come out the same size when the shorter one carries a phantom of the taller one's
content at `Ph`'s default, the vertical extent, which is LaTeX's `\vphantom`. A bracket that grows
taller is drawn wider, so all four glyphs then match: measured 2026-09-15 on a transwedge identity,
3.471 by 15.708 pt each. `Ph (t='horz')` reserves the width instead and leaves the height alone, which
shows as a hole inside the bracket and a pair 3.298 by 10.872 pt against its partner's 3.471 by 15.708.

Every bracket is a `Br`, a single letter or digit inside included, and never a pair of `Sb (ro='pnct')`
parentheses: the punctuation role spaces its symbol as punctuation, so a `(1)` written that way renders
`( 1 )` and leaves a gap before the full stop after it. The punctuation role is for commas and full
stops. Where the bracketed content carries a superscript, reach for `Br (as)`, the asymmetric extent,
which centres the bracket on its content instead of on the math axis; the site's own brackets round a
raised power are written that way.

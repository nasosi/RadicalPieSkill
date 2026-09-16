# Annotation hints

A drawing structure's connector holds two anchors, one per end or per opposite corner, and an
annotation group's holds one; giving a drawing structure a single anchor crashes Radical Pie with an
access violation. A structure nested inside a subgroup exposes only anchor indexes 0 and 1, and
asking it for 2 or 3 crashes the program, which is why the validator refuses it. A bond site is the
exception: nested or not, every one of its seven types keeps all four indexes, which is what lets a
panel hang off `u32{'bond','bond'} i32{2,1}` inside a neighbour group. Run annotation arrows from
the term to a rail of the main group, `'xxx!'` index 1 above and index 0 below, which snaps them
vertical, and attach each caption to the far end of its arrow rather than to the term, so the
arrow's length places it. See the `X` section of `references/catalogue/Annotations.md` for the anchor
indexes and Examples 23 and 24 for the whole pattern.

An arrow that points into a drawing starts from outside it: from the caption group's own type `0`
anchor, or from a rail with an `f{}` offset that slides the end along it. An arrow whose tail sits on a
symbol next to the target crosses the bonds between the two, which is what happens on a structural
formula when the tail is put on the hydroxyl and the head on the carbon beside it.

An arrow from a note beside one line of a multi-line equation lands on that line's `'axis'` anchor of the
main group, never on a symbol inside the line, or it crosses the line's tail.
`references/catalogue/Annotations.md`'s "A note beside one line of a multi-line equation" section gives the
pairing.

A connector whose far end names a matrix with a rail anchor type, `'xxx!'` or `'yyy!'`, crashes Radical
Pie with an access violation. The rails belong to the top-level group, so the far end of an arrow that
leaves a matrix names the equation group. A caption on a block inside a tiled grid goes on the
rectangle's `'anno'` anchor 4, over the centre; anchor 1 puts it above the rectangle, which is inside
the row above when the blocks tile the grid with no spare row.

An annotation group is itself a top-level group and carries its own rails, so an arrow that starts at a
symbol inside an annotation runs to that annotation's `'xxx!'` 1 rather than to the equation's, and its
caption hangs on its far end. A second annotation attached to the first caption puts the whole chain
above the equation, which is how one definition is annotated term by term
(`references/catalogue/Annotations.md`, the rail paragraph).

A slanted line's `'anno'` 1 does not sit over its far end: it sits beyond that end along the line's own
direction, 3.53 pt out on the line the anchor atlas measures. A caption shared by two arrows converging
on one point therefore hangs on whichever of the two leans the way the caption should shift. Measured
2026-09-15 on two methyl callouts meeting above a benzene ring: on the right-hand arrow the caption
landed over the drawing with no offset and the equation came out 92.8657 pt wide, and on the left-hand
one the same caption hung out to the right and took it to 108.895 pt.

An arrow onto a bracketed matrix starts from outside it, on `'orow'` or `'ocol'`, the grid's outer
edge, which clears the bracket; `'mrow'` and `'mcol'` sit on the same row and column midlines but
inside the grid, so an arrow from one of those drives its head straight into the bracket instead of
stopping short of it. Run the arrow on to a rail of the equation, `'xxx!'` or `'yyy!'`, and hang the
caption on its far end, exactly as an arrow onto a term does. The site's Exomorphism equation labels
its picture grid's rows and columns this way, off rail 5.

Two captions on the same rail overlap when their arrows stand closer than the captions are wide, and
nothing but a rendering shows it: send one arrow to the other rail, or align the captions away from each
other (`al='rght'` on the left one, `al='left'` on the right one). Inside a script, write a fraction as `Fr
(t='horz')`; the diagonal kind is cramped at script size. A prompt that calls an exponent's fraction
"slanted" or "small" still means `'horz'`, since `'diag'` shrinks and stacks rather than sitting on one
baseline either side of a slash. The label box paragraph of the `Gr` section of
`references/catalogue/Groups.md` and the `Fr` section of `references/catalogue/Fractions.md` say why.
Render every annotated equation and look at it before handing it over.
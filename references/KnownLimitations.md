# Known Limitations

What cannot be fixed on the skill's side, measured against Radical Pie 1.15 and Office 16. Nothing in
this list is feedback: `references/Feedback.md` says to read it before writing a line, and a lesson that
is already here is dropped.

- **Every render opens a window.** Radical Pie has no headless mode, so each render, export and embed puts
  the editor on the desktop for a second or two and closes it again. One program at a time may drive it,
  the foreground window and the clipboard being shared.
- **PowerPoint cannot be hidden.** Word runs invisibly under COM; PowerPoint does not, and its window is
  on the screen, minimised at best, for the length of an embed.
- **A killed interpreter leaves the working copy of a deck behind.** The pipelines end every program they
  start, on success, on failure and on Ctrl-C, and every one of those programs is in a Windows job object
  that ends with the interpreter, so Ctrl-Break, a closed console and a killed process take the editor,
  PowerPoint and Word with them too. What such an end does leave is the file the PowerPoint pipeline was
  building, beside the output path it never wrote, for the user to delete.
- **An inline equation on a slide does not follow the text.** PowerPoint has no inline shape, so an inline
  equation is an object floating over the sentence it was placed in. Editing that sentence afterwards moves
  the text and leaves the equation where it was; the fix is to run the pipeline again on the edited draft.
  The group the pipeline leaves behind is what keeps the two together when the shape itself is moved.
- **Equations in a layout's placeholder are not grouped with it.** PowerPoint refuses to group a placeholder,
  so moving that placeholder leaves its equations behind; a plain text box keeps them together.
- **The PowerPoint collapse is PowerPoint's.** An embedded equation can collapse to a blank 5 by 7 point
  object, which Radical Pie's own PowerPoint page records as a PowerPoint bug. The pipeline detects it and
  refuses the deck; nothing in a `.pie` file prevents it.
- **The editor crashes on the files the validator refuses.** An anchor index a nested structure does not
  own, a drawing connector with one anchor, `Zg (d=3)`, and a style map whose first index names an unfilled
  font slot each exit Radical Pie with an access violation rather than an error. Refusing the file before
  it is opened is the whole defence available from outside the program.
- **A render can time out on a busy machine.** The pipeline waits for the editor's window and for the file
  it writes on a timer rather than a signal, and tries twice. Both attempts can be spent under load, and
  the message says so; the file is not at fault.
- **Two of the editor's own results a file cannot control.** Radical Pie 1.15 drops `M (t='grek')` when it
  loads and saves a design, so a Greek upright mapping does not survive a round trip through the editor.
  A design value outside the dialog's range is not clamped when it arrives in a file, and
  `V (n='slnt') {f{90.0}}` renders an equation of infinite width.

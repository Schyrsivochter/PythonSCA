# PythonSCA
Mark Rosenfelder’s Sound Change Applier, rewritten in Python with a nice GUI.

The PythonSCA is based on Mark Rosenfelder (aka Zompist)’s SCA², implemented in Javascript, which can be found (on his website.)[http://zompist.com/sca2.html]

- Almost fully compatible to Zompist’s SCA². The only exception is the wildcard, which I have not yet implemented, since I don’t need it.
- Native windowed GUI.
- A nice large Apply button, and everything is packed closely (to me it was the main flaw in the SCA² that the Apply button was so small and everything was so far apart), but expands to a side-by-side-view if it gets large.
- Tabs for running multiple SCAs in one window. They can be renamed, restored after closing, and moved around.
- You can save and load rules and lexicons to/from files directly.
- Saves its tabs on exiting and restores them on opening.
- Keyboard shortcut (F9) for applying the rules.
- *Not* highly customisable unless you know Python and Tkinter.
- Has probably loads of bugs, though.

Further information:
- The tabs behave like in a web browser – Ctrl+T opens a new one, Ctrl+W closes the current one; middle click on a tab closes it, middle click on the tab bar opens a new one. They can be switched with Ctrl-PgUp/PgDn. You can’t move them by dragging yet, sorry.
- The standard file extensions are .slx and .sca, not the .lex and .sc from Zompist’s first SCA. I did this for several reasons:
  - Microsoft Office already has a file type with the extension .lex.
  - I don’t like extensions with only two letters.
  - Sound change files created with my SCA might not work with Zomp’s.
- In the "WD" directory you will find files named `__last{number}.slx` and `.sca` respectively. They hold the rules and input lexicons from the last session. You can copy and rename them if you forgot to save something. (Actually, you can do with them what you want, since SCA does not read them – it restores the contents of its last tabs from the `__last.json` file.)
- If you want to see the Python console to debug the program, run `scaguioo.py` directly. (The only thing `scagui.pyw` does is run `scaguioo.py`, but since it has the `pyw` extension, Python hides the console.)
- Ignore the checkbox named Debug. Originally, it makes the rule applying script show debug info, but you probably won’t understand it, and it will be *very* much, if not far too much for Python or for you to handle. So unless you know what you’re doing, leave it alone.
- If you have any ideas or suggestions, feel free to contact me!

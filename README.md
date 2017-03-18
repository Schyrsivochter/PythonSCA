# PythonSCA
## Mark Rosenfelder’s Sound Change Applier, rewritten in Python with a nice GUI.

The PythonSCA is based on Mark Rosenfelder (aka Zompist)’s SCA², implemented in Javascript, which can be found [on his website: http://zompist.com/sca2.html](http://zompist.com/sca2.htm)

Please note that *I am not Mark Rosenfelder or in any way affiliated with him.* This is a personal project.

### Features
- Almost fully compatible to Zompist’s SCA². The only exception is the wildcard, which has not been implemented yet. For details on what it does, see http://zompist.com/scahelp.html.
- Native window GUI.
- A nice large Apply button, and everything is packed closely (to me it was the main flaw in the SCA² that the Apply button was so small and everything was so far apart), but expands to a side-by-side-view if it gets large.
- Tabs for running multiple SCAs in one window. They can be renamed, restored after closing, and moved around.
- You can save and load rules and lexicons to/from files directly.
- Saves its tabs on exiting and restores them on opening.
- Keyboard shortcut (F9) for applying the rules.
- *Not* highly customisable unless you know Python and wx.
- Has probably loads of bugs, though.

### Dependencies
- [Python 3](https://www.python.org/downloads/)
- A compatible version of [wxPython Phoenix](http://wiki.wxpython.org/ProjectPhoenix)

### Installation
1. Download sca.py, scaguioo.py and scagui.pyw.
2. Place them where you want. It’s important that you have them all in the same directory, though, or it won’t work (unless you know enough Python to change my code so the GUI looks for sca.py elsewhere).
3. Run scagui.pyw. It will create a directory with some files when closing for the first time. Leave them there unless you want to start over every time you close and re-open the SCA.

### Further information
- The tabs behave like in a web browser – Ctrl+T opens a new one, Ctrl+W closes the current one; middle click on a tab closes it, middle click on the tab bar opens a new one. They can be switched with Ctrl-PgUp/PgDn. You can’t move them by dragging yet, sorry.
- The standard file extensions are `.slx` and `.sca` (not the `.lex` and `.sc` from Zompist’s first SCA).
- In the ‘pysca’ directory you will find files named `__last{n}.slx` and `__last{n}.sca` with `n`s from 0 to the number of tabs - 1. They hold the rules and input lexicons from the last session. You can copy and rename them if you forgot to save something. (Actually, you can do with them what you want, since SCA does not read them – it restores the contents of its last tabs from the `__last.json` file.)
- If you want to see the Python console to debug the program, run `scaguioo.py` directly. (`scagui.pyw` essentially just runs `scaguioo.py`, but since it has the `pyw` extension, Python hides the console.)
- Ignore the checkbox named Debug. Originally, it makes the rule applying script show debug info, but you probably won’t understand it, and it will be *very* much, if not far too much for Python or for you to handle (that’s why it’s deactivated by default). So unless you know what you’re doing, leave it alone.
- If you have any ideas or suggestions, feel free to contact me!

### Current roadmap
- For the rule applying script `sca.py`:
  - Support for the wildcard `…`

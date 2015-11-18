"""Graphical interface for the PythonSCA.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

SCA² (C) 2012 Mark Rosenfelder aka Zompist (markrose@zompist.com)
Python re-code (C) 2015 Andreas Kübrich aka Schyrsivochter (andreas.kuebrich@kuebrich.de)"""


import os, sys
sys.path.append(os.path.dirname(__file__))
import sca
import tkinter as tk, tkinter.filedialog as filedialog, tkinter.messagebox as messagebox, tkinter.ttk as ttk
import re, json


def toSC(rewrites, categories, rules):
    "Transform lists of rewrites, categories and rules to an SC file."
    return ("\n".join(categories) + "\n\n" + 
            "\n".join(rewrites)   + "\n\n" + 
            "\n".join(rules))

def fromSC(sc):
    "Parse an SC file into lists of rewrites, categories and rules."
    rewrites   = []
    categories = []
    rules      = []
    for line in sc.splitlines():
        if   "=" in line:
            categories.append(line)
        elif "/" in line:
            rules.append(line)
        elif "|" in line:
            rewrites.append(line)
    return rewrites, categories, rules

class SCATab:
    "A tab of the PythonSCA GUI application."

    lastLex = ""
    lastSC = ""

    def applyRules(self):
        "Apply the rules to the input lexicon."
        outputs = self.getSCAConf().sca()
        self.olxTxt.configure(state="normal")
        self.olxTxt.replace("1.0", "end", "\n".join(outputs))
        self.olxTxt.configure(state="disabled")

    def saveSC(self, scPath):
        "Save the rewrites, categories and rules to a file."
        rews  = self.rewTxt.get("1.0","end").strip().splitlines()
        cats  = self.catTxt.get("1.0","end").strip().splitlines()
        rules = self.rulTxt.get("1.0","end").strip().splitlines()
        scContent = toSC(rews, cats, rules)
        with open(scPath, mode=("w" if os.path.isfile(scPath) else "x"), encoding="utf8") as scFile:
            scFile.write(scContent)

    def saveLex(self, lexPath):
        "Save the input lexicon to a file."
        lexContent = self.ilxTxt.get("1.0","end")
        with open(lexPath, mode=("w" if os.path.isfile(lexPath) else "x"), encoding="utf8") as lexFile:
            lexFile.write(lexContent)

    def loadSC(self, scPath):
        "Load the rewrites, categories and rules from a file, if it exists."
        exists = os.path.isfile(scPath)
        if exists:
            with open(scPath, encoding="utf8") as scFile:
                scContent = scFile.read()
            scContent = scContent.replace("\ufeff", "", 1) # get rid of that BOM
            rews, cats, rules = map(lambda l: "\n".join(l), fromSC(scContent))
            self.rewTxt.replace("1.0", "end", rews.strip())
            self.catTxt.replace("1.0", "end", cats.strip())
            self.rulTxt.replace("1.0", "end", rules.strip())
        return exists

    def loadLex(self, lexPath):
        "Load the input lexicon from a file, if it exists."
        exists = os.path.isfile(lexPath)
        if exists:
            with open(lexPath, encoding="utf8") as lexFile:
                lexContent = lexFile.read()
            lexContent = lexContent.replace("\ufeff", "", 1) # get rid of that BOM
            self.ilxTxt.replace("1.0", "end", lexContent.strip())
        return exists

    def setSCAConf(self, conf):
        "Set the tab contents to the settings in an sca.SCAConf object."
        self.rewTxt.replace("1.0", "end", "\n".join(conf.rewrites))
        self.catTxt.replace("1.0", "end", "\n".join(conf.categories))
        self.rulTxt.replace("1.0", "end", "\n".join(conf.rules))
        self.ilxTxt.replace("1.0", "end", "\n".join(conf.inLex))
        if type(conf.outFormat) is int:
            self.outFormat.set(conf.outFormat)
        else:
            self.outFormat.set(3)
            self.customFormat.set(conf.outFormat)
        self.debug.set(conf.debug)
        self.rewOut.set(conf.rewOut)

    def getSCAConf(self):
        "Return an sca.SCAConf object with the tab contents."
        c = sca.SCAConf(rewOut=self.rewOut.get(), debug=self.debug.get())
        of = self.outFormat.get()
        c.outFormat = of if of != 3 else self.customFormat.get()
        c.rewrites   = self.rewTxt.get("1.0", "end").strip().splitlines()
        c.categories = self.catTxt.get("1.0", "end").strip().splitlines()
        c.rules      = self.rulTxt.get("1.0", "end").strip().splitlines()
        c.inLex      = self.ilxTxt.get("1.0", "end").strip().splitlines()
        return c

    def buildCompact(self):
        "Arrange the contents in compact view (in two rows, better for a small window)."
        for widget in self.frm.grid_slaves():
            widget.grid_forget()
        
        self.rewLbl.grid(column=0, row=0           ); self.catLbl.grid(column=1, row=0           ); self.rulLbl.grid(column=2, row=0)
        self.rewTxt.grid(column=0, row=1           ); self.catTxt.grid(column=1, row=1           ); self.rulTxt.grid(column=2, row=1)
        self.optLfm.grid(column=0, row=2, rowspan=2); self.ilxLbl.grid(column=1, row=2           ); self.olxLbl.grid(column=2, row=2)
        pass;                                         self.ilxTxt.grid(column=1, row=3, rowspan=2); self.olxTxt.grid(column=2, row=3, rowspan=2)
        self.appBtn.grid(column=0, row=4, pady=5);

        # all columns should resize
        for c in range(3): self.frm.grid_columnconfigure(c, weight=1, minsize=150)
        for c in range(3, 6): self.frm.grid_columnconfigure(c, weight=0, minsize=0)
        # rows 1 and 4 should resize
        self.frm.grid_rowconfigure(1, weight=1)
        self.frm.grid_rowconfigure(2, weight=0)
        self.frm.grid_rowconfigure(3, weight=0)
        self.frm.grid_rowconfigure(4, weight=1)
        
        # all widgets should resize on row resize
        for widget in self.frm.grid_slaves():
            widget.grid_configure(sticky="nsew", padx=5)
        self.optLfm.grid_configure(pady=5)

        # pack the options into the options panel
        for optWidget in [self.ofmLbl, self.ofmRb1, self.ofmRb2, self.ofmRb3, self.ofmRb4, self.ofmEnt, self.reoChk, self.debChk]:
            optWidget.pack(padx=5, anchor="nw", expand=True)
        self.ofmEnt.pack_configure(fill="x", padx=20) # a bit offset


    def buildExpanded(self):
        "Arrange the contents in expanded view (in one row, ideal for maximised view)."
        for widget in self.frm.grid_slaves():
            widget.grid_forget()
            
        self.optLfm.grid(column=0, row=0, rowspan=2); self.rewLbl.grid(column=1, row=0           ); self.catLbl.grid(column=2, row=0           );
        pass;                                         self.rewTxt.grid(column=1, row=1, rowspan=3); self.catTxt.grid(column=2, row=1, rowspan=3);
        self.appBtn.grid(column=0, row=3, pady=5);

        self.rulLbl.grid(column=3, row=0           ); self.ilxLbl.grid(column=4, row=0           ); self.olxLbl.grid(column=5, row=0           );
        self.rulTxt.grid(column=3, row=1, rowspan=3); self.ilxTxt.grid(column=4, row=1, rowspan=3); self.olxTxt.grid(column=5, row=1, rowspan=3);

        # all columns should resize
        for c in range(6): self.frm.grid_columnconfigure(c, weight=1, minsize=150)
        # row 2 should resize
        self.frm.grid_rowconfigure(1, weight=0)
        self.frm.grid_rowconfigure(2, weight=2)
        self.frm.grid_rowconfigure(3, weight=1)
        self.frm.grid_rowconfigure(4, weight=0)
        
        # all widgets should resize on row resize
        for widget in self.frm.grid_slaves():
            widget.grid_configure(sticky="nsew", padx=5)
        self.optLfm.grid_configure(pady=5)

        # pack the options into the options panel
        for optWidget in [self.ofmLbl, self.ofmRb1, self.ofmRb2, self.ofmRb3, self.ofmRb4, self.ofmEnt, self.reoChk, self.debChk]:
            optWidget.pack(padx=5, anchor="nw", expand=True)
        self.ofmEnt.pack_configure(fill="x", padx=20) # a bit offset

    def build(self, compact=True):
        "Arrange the tab contents either expanded (in one row, ideal for maximised view) or compact (in two rows, better for a small window)."
        if compact: self.buildCompact()
        else:       self.buildExpanded()
        
    def make(self, compact=True):
        "Build the GUI of the tab and arrange them either expanded (in one row, ideal for maximised view) or compact (in two rows, better for a small window)."
        # first two rows
        self.rewLbl = ttk.Label(self.frm, text="Rewrite rules")
        self.rewTxt =  tk.Text(self.frm, borderwidth=1, relief="solid", font="consolas 10")
        self.catLbl = ttk.Label(self.frm, text="Categories")
        self.catTxt =  tk.Text(self.frm, borderwidth=1, relief="solid", font="consolas 10")
        self.rulLbl = ttk.Label(self.frm, text="Sound changes")
        self.rulTxt =  tk.Text(self.frm, borderwidth=1, relief="solid", font="consolas 10")

        # last rows
        self.optLfm = ttk.LabelFrame(self.frm, text="Options", borderwidth=2, relief="groove")
        self.appBtn = ttk.Button(self.frm, text="Apply", command=self.applyRules)
        self.ilxLbl = ttk.Label(self.frm, text="Input lexicon")
        self.ilxTxt =  tk.Text(self.frm, borderwidth=1, relief="solid", font="consolas 10")
        self.olxLbl = ttk.Label(self.frm, text="Output lexicon")
        self.olxTxt =  tk.Text(self.frm, borderwidth=1, relief="flat",  font="consolas 10", state="disabled")

        # the lexicon textareas always scroll together
        self.ilxTxt.configure(yscrollcommand = lambda v, d: self.olxTxt.yview_moveto(v))
        self.olxTxt.configure(yscrollcommand = lambda v, d: self.ilxTxt.yview_moveto(v))

        # Options frame
        self.outFormat = tk.IntVar(self.frm, 0)
        self.rewOut = tk.BooleanVar(self.frm, False)
        self.customFormat = tk.StringVar(self.frm)
        self.debug = tk.BooleanVar(self.frm, False)
        self.ofmLbl = ttk.Label(self.optLfm, text="Output format:")
        self.ofmRb1 = ttk.Radiobutton(self.optLfm, text="output",              variable=self.outFormat, value=0)
        self.ofmRb2 = ttk.Radiobutton(self.optLfm, text="input \u2192 output", variable=self.outFormat, value=1)
        self.ofmRb3 = ttk.Radiobutton(self.optLfm, text="output [input]",      variable=self.outFormat, value=2)
        self.ofmRb4 = ttk.Radiobutton(self.optLfm, text="Custom:",             variable=self.outFormat, value=3)
        self.ofmEnt = ttk.Entry      (self.optLfm,                         textvariable=self.customFormat)
        self.reoChk = ttk.Checkbutton(self.optLfm, text="Rewrite on output",   variable=self.rewOut)
        self.debChk = ttk.Checkbutton(self.optLfm, text="Debug",               variable=self.debug, state="disabled")

        self.ofmEnt.bind("<FocusIn>", lambda e: self.outFormat.set(3)) # check ‘Custom’ if custom format Entry gets the focus

        self.build(compact)

    def __init__(self, master=None, conf=None, compact=True):
        self.frm = ttk.Frame(master)
        self.frm.configure(padding=5)
        self.make(compact)
        if conf is not None:
            self.setSCAConf(conf)


class SCAWin:
    """The PythonSCA GUI application."""

    tabs       = []
    closedTabs = []
    isCompact = False

    scTypes =  [("SCA sound change files", ".sc .sca"),
                ("All files",              ".*"      )]

    lexTypes = [("SCA lexicon files",     ".lex .slx"),
                ("All files",              ".*"      )]


    def curTab(self):
        "Return the SCATab object of the current tab."
        return self.tabs[self.notebook.index("current")]

    def askSaveSC(self):
        tab = self.curTab()
        scPath = filedialog.asksaveasfilename(defaultextension="sca", filetypes=self.scTypes, initialfile=tab.lastSC)
        if scPath:
            tab.saveSC(scPath)
            tab.lastSC = scPath

    def askSaveLex(self):
        tab = self.curTab()
        lexPath = filedialog.asksaveasfilename(defaultextension="slx", filetypes=self.lexTypes, initialfile=tab.lastLex)
        if lexPath:
            tab.saveLex(lexPath)
            tab.lastLex = lexPath

    def askSaveOut(self):
        tab = self.curTab()
        lexPath = filedialog.asksaveasfilename(defaultextension="slx", filetypes=self.lexTypes, initialdir=os.path.dirname(tab.lastLex))
        if lexPath:
            lexContent = tab.olxTxt.get("1.0","end")
            with open(lexPath, mode=("w" if os.path.isfile(lexPath) else "x"), encoding="utf8") as lexFile:
                lexFile.write(lexContent)

    def askOpenSC(self):
        tab = self.curTab()
        scPath = filedialog.askopenfilename(filetypes=self.scTypes, initialfile=tab.lastSC)
        if scPath:
            tab.loadSC(scPath)
            tab.lastSC = scPath

    def askOpenLex(self):
        tab = self.curTab()
        lexPath = filedialog.askopenfilename(filetypes=self.lexTypes, initialfile=tab.lastLex)
        if lexPath:
            tab.loadLex(lexPath)
            tab.lastLex = lexPath

    def clearRules(self):
        "Clear the rewrites, categories and rules fields of the current tab."
        if self.tabs:
            tab = self.curTab()
            tab.rewTxt.delete("1.0", "end")
            tab.catTxt.delete("1.0", "end")
            tab.rulTxt.delete("1.0", "end")

    def newTab(self):
        "Open a new blank tab."
        tab = SCATab(self.notebook, compact=self.isCompact)
        self.notebook.add(tab.frm, text="New tab")
        self.tabs.append(tab)
        self.notebook.select(len(self.tabs)-1)

    def closeTab(self, tabid):
        "Close tab and keep it for restoring."
        if self.tabs:
            no = self.notebook.index(tabid)
            self.closedTabs.append((self.tabs.pop(no), self.notebook.tab(no, option="text")))
            self.notebook.forget(tabid)

    def restoreTab(self):
        "Restore last closed tab."
        if self.closedTabs:
            tab, text = self.closedTabs.pop()
            self.tabs.append(tab)
            self.notebook.add(tab.frm, text=text)
            self.notebook.select(len(self.tabs)-1)

    def renameTab(self, tabid):
        "Open a modal dialog for renaming tab."
        if self.tabs:
            renDlg = tk.Toplevel()
            renDlg.grab_set() # make the dialog modal, i.e. main window cannot get focus
            renDlg.minsize(200, 100)
            renLbl = ttk.Label(renDlg, text="Enter new name:")
            renEnt = ttk.Entry(renDlg)
            renEnt.insert(0, self.notebook.tab(tabid, option="text"))
            def renOk():
                self.notebook.tab(tabid, text=renEnt.get())
                renDlg.destroy()
            renBtn = ttk.Button(renDlg, text="Ok", command=renOk, default="active")
            renDlg.bind("<Return>", lambda e: renOk())
            for widget in [renLbl, renEnt, renBtn]:
                widget.pack(pady=5)
            renEnt.focus()
            renDlg.mainloop()

    def cloneTab(self, tabid):
        "Open a new tab with the same contents as tab."
        otab = self.tabs[tabid]
        ntab = SCATab(self.win, compact=self.isCompact)
        ntab.setSCAConf(otab.getSCAConf())
        self.tabs.append(ntab)
        self.notebook.add(ntab.frm, text=self.notebook.tab(tabid, option="text"))
        self.notebook.select(len(self.tabs)-1)

    def moveTabRight(self, tabid):
        "Swap tab with its right neighbour."
        tabid = self.notebook.index(tabid)
        if tabid < len(self.tabs) - 1:
            self.notebook.insert(tabid+1, tabid)
            self.tabs[tabid], self.tabs[tabid+1] = self.tabs[tabid+1], self.tabs[tabid]
        else:
            self.notebook.insert(0, tabid)
            self.tabs = [tabid] + self.tabs[:-1]

    def moveTabLeft(self, tabid):
        "Swap tab with its left neighbour."
        tabid = self.notebook.index(tabid)
        if tabid > 0:
            self.notebook.insert(tabid-1, tabid)
            self.tabs[tabid], self.tabs[tabid-1] = self.tabs[tabid-1], self.tabs[tabid]
        else:
            self.notebook.insert("end", tabid)
            self.tabs = self.tabs[1:] + [tabid]

    def newTabMenu(self, tabid):
        "Create a new popup menu for tab."
        men = tk.Menu(self.win)
        men.add_command(label="Close tab",  command=(lambda: self.closeTab (tabid)))
        men.add_command(label="Rename tab", command=(lambda: self.renameTab(tabid)))
        men.add_command(label="Clone tab",  command=(lambda: self.cloneTab (tabid)))
        men.add_separator()
        men.add_command(label="Move tab left",  command=(lambda: self.moveTabLeft (tabid)))
        men.add_command(label="Move tab right", command=(lambda: self.moveTabRight(tabid)))
        return men


    def onClose(self):
        "Event handler for closing the window. Includes saving the configuration, the tabs and their contents to the __last files."
        scaDir = os.path.dirname(__file__) + "\\WD"
        scaF = "{}/__last{}.sca"
        slxF = "{}/__last{}.slx"
        jsonPath = scaDir + "/__last.json"
        if not os.path.exists(scaDir):
            os.mkdir(scaDir)

        isMaximised = self.win.state() == "zoomed"
        if isMaximised:
            self.win.state("normal")
            normalGeometry = self.win.geometry()
            self.win.state("zoomed")
        else:
            normalGeometry = self.win.geometry()

        # delete the .sca and .slx files
        for filename in filter(lambda s: re.match("__last\\d*\\.s(ca|lx)", s), os.listdir(scaDir)):
            os.remove(scaDir + "/" + filename)
                    
        # save each of the tabs in a .sca and a .slx file
        for no in range(len(self.tabs)):
            tab = self.tabs[no]
            tab.saveSC (scaF.format(scaDir, no))
            tab.saveLex(slxF.format(scaDir, no))
            
        # save everything in a .json file, too
        jso = {
            "geometry": normalGeometry,
            "curTab": (self.notebook.index("current") if self.tabs else None),
            "isMaximised": isMaximised,
            "tabs": [
                {
                    "name": self.notebook.tab(no, option="text"),
                    "outFormat": conf.outFormat if type(conf.outFormat) == int else 3,
                    "customFormat": conf.outFormat if type(conf.outFormat) == str else "",
                    "rewOut": bool(conf.rewOut),
                    "debug": bool(conf.debug),
                    "rewrites": conf.rewrites,
                    "categories": conf.categories,
                    "rules": conf.rules,
                    "inLex": conf.inLex,
                    "outLex": self.tabs[no].olxTxt.get("1.0", "end").splitlines(),
                    "lastSC": self.tabs[no].lastSC,
                    "lastLex": self.tabs[no].lastLex
                } for no, conf in enumerate(map(lambda t: t.getSCAConf(), self.tabs))
            ]
        }

        with open(jsonPath, mode=("w" if os.path.isfile(jsonPath) else "x"), encoding="utf8") as jsonfile:
            json.dump(jso, jsonfile, indent=2)
            
        self.win.destroy()


    def onClick(self, event):
        "Event handler for any mouse button click."
        x, y, b = event.x, event.y, event.num
        if b == 1: return # left button does nothing
        try:
            tabClicked = self.notebook.index("@{},{}".format(x, y))
            isTab = True
        except tk.TclError:
            tabClicked = -1
            isTab = False
        isTabBar = y < 21
        if b == 2 and isTabBar: # tab bar or tab middle clicked
            if isTab:
                self.closeTab(tabClicked)
            else:
                self.newTab()                
        elif b == 3: # right click
            if isTabBar and isTab: # a tab
                absx, absy = self.win.winfo_pointerxy()
                self.newTabMenu(tabClicked).post(absx, absy)
            elif not isTabBar: # inside the window
                ...

    def onResize(self, event):
        "Event handler for resizing the window."
        c = self.win.winfo_width() < 910
        if self.isCompact != c:
            for tab in self.tabs:
                tab.build(c)
            self.isCompact = c
        if c:
            self.win.minsize(width=460, height=522)
        else:
            self.win.minsize(width=460, height=266)

    def onSwitchRight(self, event):
        'Event handler for the "switch tab right" keyboard shortcut.'
        tabid = self.notebook.index("current")
        if tabid < len(self.tabs) - 1:
            self.notebook.select(tabid+1)
        else:
            self.notebook.select(0)

    def onSwitchLeft(self, event):
        'Event handler for the "switch tab left" keyboard shortcut.'
        tabid = self.notebook.index("current")
        if tabid > 0:
            self.notebook.select(tabid - 1)
        else:
            self.notebook.select(len(self.tabs)-1)

    def build(self):
        """Build the actual GUI with the menu and the tabs, and bind the keyboard shortcuts.
Does not build any tabs or tab contents; that’s the task of newTab() and, ultimately, SCATab.make()."""
        self.notebook = ttk.Notebook(self.win)
        self.notebook.pack(expand=True, fill="both")

        # create a menu bar
        self.barmen = tk.Menu(self.win)

        # create the "rules" menu
        self.rulmen = tk.Menu(self.barmen)
        self.rulmen.add_command(label="Load from file \u2026", command=self.askOpenSC)
        self.rulmen.add_command(label=  "Save to file \u2026", command=self.askSaveSC)
        self.rulmen.add_separator()
        self.rulmen.add_command(label="Clear rewrite rules",      command=(lambda: self.curTab().rewTxt.delete("1.0", "end")))
        self.rulmen.add_command(label="Clear categories",         command=(lambda: self.curTab().catTxt.delete("1.0", "end")))
        self.rulmen.add_command(label="Clear sound change rules", command=(lambda: self.curTab().rulTxt.delete("1.0", "end")))
        self.rulmen.add_command(label="Clear all",                command=self.clearRules)

        # create the "lexicon" menu
        self.lexmen = tk.Menu(self.barmen)
        self.lexmen.add_command(label=     "Load from file \u2026", command=self.askOpenLex)
        self.lexmen.add_command(label= "Save input to file \u2026", command=self.askSaveLex)
        self.lexmen.add_command(label="Save output to file \u2026", command=self.askSaveOut)
        self.lexmen.add_separator()
        self.lexmen.add_command(label="Clear input lexicon", command=(lambda: self.curTab().ilxTxt.delete("1.0", "end")))

        # create the "tab" menu
        self.tabmen = self.newTabMenu("current")
        self.tabmen.add_separator()
        self.tabmen.add_command(label="New tab", command=self.newTab)
        self.tabmen.add_command(label="Restore closed tab", command=self.restoreTab)

        # put them on the menu bar and the menu bar on the window
        self.barmen.add_cascade(menu=self.tabmen, label="Tabs")
        self.barmen.add_cascade(menu=self.rulmen, label="Rules")
        self.barmen.add_cascade(menu=self.lexmen, label="Lexicon")
        self.win.configure(menu=self.barmen)

        self.win.bind("<F9>", lambda e: self.curTab().applyRules())
        self.win.bind("<ButtonPress>", self.onClick)
        self.win.bind("<Control-t>", lambda e: self.newTab())
        self.win.bind("<Control-w>", lambda e: self.closeTab("current"))
        self.win.bind("<Control-Prior>", self.onSwitchLeft)
        self.win.bind("<Control-Next>", self.onSwitchRight)
        self.win.bind("<Control-Alt-Prior>", lambda e: self.moveTabLeft("current"))
        self.win.bind("<Control-Alt-Next>", lambda e: self.moveTabRight("current"))
        self.win.bind("<Configure>", self.onResize)
        self.win.protocol("WM_DELETE_WINDOW", self.onClose)

    def loadLast(self):
        "Load the configuration, the tabs and their contents from the __last files."
        scaDir = os.path.dirname(__file__) + "\\WD"
        # load the .json file
        jsonPath = scaDir + "/__last.json"
        if os.path.isfile(jsonPath):
            with open(jsonPath, encoding="utf8") as jsonFile:
                jso = json.load(jsonFile)
            # restore everything from the .json file
            self.win.geometry(jso["geometry"])
            if jso["isMaximised"]: self.win.state("zoomed")
            for tabJSO in jso["tabs"]:
                # make a new tab
                self.newTab()
                no = self.notebook.index("current")
                tab = self.tabs[no]
                # load the tab options
                self.notebook.tab(no, text=tabJSO["name"])
                tabConf = sca.SCAConf(
                    outFormat = tabJSO["outFormat"] if tabJSO["outFormat"] != 3 else tabJSO["customFormat"],
                    rewOut = tabJSO["rewOut"],
                    debug = tabJSO["debug"],
                    rewrites = tabJSO["rewrites"],
                    categories = tabJSO["categories"],
                    rules = tabJSO["rules"],
                    inLex = tabJSO["inLex"])
                tab.setSCAConf(tabConf)
                tab.lastSC = tabJSO["lastSC"]
                tab.lastLex = tabJSO["lastLex"]
                tab.olxTxt.configure(state="normal")
                tab.olxTxt.replace("1.0", "end", "\n".join(tabJSO["outLex"]))
                tab.olxTxt.configure(state="disabled")
            if jso["curTab"] is not None:
                self.notebook.select(jso["curTab"])
        else:
            self.newTab()
            no = self.notebook.index("current")
            tab = self.tabs[no]
            tab.setSCAConf(sca.example)
            

    def __init__(self):
        self.win = tk.Tk()
        self.win.option_add("*tearOff", False)
        self.win.wm_title("PythonSCA\u00b2")
        self.win.wm_geometry("=910x266")

        self.build()
        self.loadLast()

    def mainloop(self):
        "Call the mainloop of Tk (i.e. start the program)."
        self.win.mainloop()


if __name__ == "__main__":
    scaWin = SCAWin()
    scaWin.mainloop()

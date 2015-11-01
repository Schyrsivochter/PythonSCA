### Created 2015-08-23/11
### Graphical interface for PythonSCA²
###
### Roadmap:
###     • Using a LabelFrame for Options – 2015-08-27/01
###     • F9 as Apply shortcut – 2015-09-05/15
###     • Using Ttk for everything that supports it – 2015-09-23/18
###     • Multiple tabs – 2015-09-28/15
###     • Save tabs on exit and restore on startup – 2015-09-30/16
###     • Save and restore output lexicon too – 2015-10-02/16
###     • Save and restore everything with the JSON – 2015-10-02/16
###     • Ability to restore closed tabs – 2015-10-05/22
###     • Clone tabs – 2015-10-12/17
###     • Move tabs with menu options – 2015-10-12/18
###     • View option: all textareas side by side (for fullscreen view) – 2015-10-21/22
###     • Switch tabs with Ctrl-PgUp/PgDn – 2015-10-26/18
###     • Paned windows for better resize control
###     • Make the Apply button not that sticky

from sys import path
import os
path.append(os.path.dirname(__file__))
import sca

import tkinter as tk, tkinter.filedialog as filedialog, tkinter.messagebox as messagebox, tkinter.ttk as ttk
import re, json


def toSC(rewrites, categories, rules):
    return "\n".join(categories) + "\n\n" + \
           "\n".join(rewrites)   + "\n\n" + \
           "\n".join(rules)

def fromSC(sc):
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

    lastLex = ""

    lastSC = ""

    def applyRules(self):
        outputs = self.getSCAConf().sca()
        self.olxTxt.configure(state="normal")
        self.olxTxt.replace("1.0", "end", "\n".join(outputs))
        self.olxTxt.configure(state="disabled")

    def saveSC(self, scPath):
        rews  = self.rewTxt.get("1.0","end").splitlines()
        cats  = self.catTxt.get("1.0","end").splitlines()
        rules = self.rulTxt.get("1.0","end").splitlines()
        scContent = toSC(rews, cats, rules)
        with open(scPath, mode=("w" if os.path.isfile(scPath) else "x"), encoding="utf8") as scFile:
            scFile.write(scContent)

    def saveLex(self, lexPath):
        lexContent = self.ilxTxt.get("1.0","end")
        with open(lexPath, mode=("w" if os.path.isfile(lexPath) else "x"), encoding="utf8") as lexFile:
            lexFile.write(lexContent)

    def loadSC(self, scPath):
        exists = os.path.isfile(scPath)
        if exists:
            with open(scPath, encoding="utf8") as scFile:
                scContent = scFile.read()
            scContent = scContent.replace("\ufeff","", 1) # get rid of that BOM
            rews, cats, rules = map(lambda l: "\n".join(l), fromSC(scContent))
            self.rewTxt.replace("1.0", "end", rews.strip())
            self.catTxt.replace("1.0", "end", cats.strip())
            self.rulTxt.replace("1.0", "end", rules.strip())
        return exists

    def loadLex(self, lexPath):
        exists = os.path.isfile(lexPath)
        if exists:
            with open(lexPath, encoding="utf8") as lexFile:
                lexContent = lexFile.read()
            lexContent = lexContent.replace("\ufeff","") # get rid of that BOM
            self.ilxTxt.replace("1.0", "end", lexContent.strip())
        return exists

    def setSCAConf(self, conf):
        c = conf
        self.rewTxt.replace("1.0", "end", "\n".join(c.rewrites))
        self.catTxt.replace("1.0", "end", "\n".join(c.categories))
        self.rulTxt.replace("1.0", "end", "\n".join(c.rules))
        self.ilxTxt.replace("1.0", "end", "\n".join(c.inLex))
        if type(c.outFormat) is int:
            self.outFormat.set(c.outFormat)
        else:
            self.outFormat.set(3)
            self.customFormat.set(c.outFormat)
        self.debug.set(c.debug)
        self.rewOut.set(c.rewOut)

    def getSCAConf(self):
        c = sca.SCAConf(rewOut=self.rewOut.get(), debug=self.debug.get())
        of = self.outFormat.get()
        c.outFormat = of if of != 3 else self.customFormat.get()
        c.rewrites = self.rewTxt.get("1.0", "end").strip().splitlines()
        c.categories = self.catTxt.get("1.0", "end").strip().splitlines()
        c.rules = self.rulTxt.get("1.0", "end").strip().splitlines()
        c.inLex = self.ilxTxt.get("1.0", "end").strip().splitlines()
        return c

    def buildCompact(self):
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
        for r in [2, 3]: self.frm.grid_rowconfigure(r, weight=0)
        for r in [1, 4]: self.frm.grid_rowconfigure(r, weight=1)


    def buildExpanded(self):
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
        for r in [1, 4]: self.frm.grid_rowconfigure(r, weight=0)
        self.frm.grid_rowconfigure(2, weight=2)
        self.frm.grid_rowconfigure(3, weight=1)

    def build(self, compact=True):
        if compact: self.buildCompact()
        else:       self.buildExpanded()
        
        # all widgets should resize on row resize
        for widget in self.frm.grid_slaves(): widget.grid_configure(sticky="nsew", padx=5)
        self.optLfm.grid_configure(pady=5)
        
    def make(self, compact=True):
        
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

        self.ofmEnt.bind("<FocusIn>", lambda e: self.outFormat.set(3))

        self.build(compact)

        # pack the options into the options panel
        for optWidget in [self.ofmLbl, self.ofmRb1, self.ofmRb2, self.ofmRb3, self.ofmRb4, self.ofmEnt, self.reoChk, self.debChk]:
            optWidget.pack(padx=5, anchor="nw", expand=True)
        self.ofmEnt.pack_configure(fill="x", padx=20) # a bit offset

    def __init__(self, master=None, conf=None, compact=True):
        self.frm = ttk.Frame(master)
        self.frm.configure(padding=5)
        self.make(compact)
        if conf is not None:
            self.setSCAConf(conf)


class SCAWin:

    tabs       = []
    closedTabs = []
    isCompact = False

    scTypes =  [("SCA sound change files", ".sc .sca"),
                ("All files",              ".*"      )]

    lexTypes = [("SCA lexicon files",     ".lex .slx"),
                ("All files",              ".*"      )]


    def curTab(self):
        return self.tabs[self.notebook.index("current")]

    def askSaveSC(self):
        scPath = filedialog.asksaveasfilename(defaultextension="sca", filetypes=self.scTypes, initialfile=self.curTab().lastSC)
        if scPath:
            self.curTab().saveSC(scPath)
            self.curTab().lastSC = scPath

    def askSaveLex(self):
        lexPath = filedialog.asksaveasfilename(defaultextension="slx", filetypes=self.lexTypes, initialfile=self.curTab().lastLex)
        if lexPath:
            self.curTab().saveLex(lexPath)
            self.curTab().lastLex = lexPath

    def askSaveOut(self):
        lexPath = filedialog.asksaveasfilename(defaultextension="slx", filetypes=self.lexTypes, initialdir=os.path.dirname(self.curTab().lastLex))
        if lexPath:
            lexContent = self.curTab().olxTxt.get("1.0","end")
            with open(lexPath, mode=("w" if os.path.isfile(lexPath) else "x"), encoding="utf8") as lexFile:
                lexFile.write(lexContent)

    def askOpenSC(self):
        scPath = filedialog.askopenfilename(filetypes=self.scTypes, initialfile=self.curTab().lastSC)
        if scPath:
            self.curTab().loadSC(scPath)
            self.curTab().lastSC = scPath

    def askOpenLex(self):
        lexPath = filedialog.askopenfilename(filetypes=self.lexTypes, initialfile=self.curTab().lastLex)
        if lexPath:
            self.curTab().loadLex(lexPath)
            self.curTab().lastLex = lexPath

    def clearRules(self):
        if self.tabs:
            self.curTab().rewTxt.delete("1.0", "end")
            self.curTab().catTxt.delete("1.0", "end")
            self.curTab().rulTxt.delete("1.0", "end")

    def newTab(self):
        tab = SCATab(self.notebook, compact=self.isCompact)
        self.notebook.add(tab.frm, text="New tab")
        self.tabs.append(tab)
        self.notebook.select(len(self.tabs)-1)

    def closeTab(self, tabid):
        if self.tabs:
            no = self.notebook.index(tabid)
            self.closedTabs.append((self.tabs.pop(no), self.notebook.tab(no, option="text")))
            self.notebook.forget(tabid)

    def restoreTab(self):
        if self.closedTabs:
            tab, text = self.closedTabs.pop()
            self.tabs.append(tab)
            self.notebook.add(tab.frm, text=text)
            self.notebook.select(len(self.tabs)-1)

    def renameTab(self, tabid):
        if self.tabs:
            renDlg = tk.Toplevel()
            renDlg.grab_set()
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
        otab = self.tabs[tabid]
        ntab = SCATab(self.win, compact=self.isCompact)
        ntab.setSCAConf(otab.getSCAConf())
        self.tabs.append(ntab)
        self.notebook.add(ntab.frm, text=self.notebook.tab(tabid, option="text"))
        self.notebook.select(len(self.tabs)-1)

    def moveTabRight(self, tabid):
        no = self.notebook.index(tabid)
        if no < len(self.tabs)-1:
            self.notebook.insert(no+1, no)
            self.tabs[no], self.tabs[no+1] = self.tabs[no+1], self.tabs[no]

    def moveTabLeft(self, tabid):
        no = self.notebook.index(tabid)
        if no > 0:
            self.notebook.insert(no-1, no)
            self.tabs[no], self.tabs[no-1] = self.tabs[no-1], self.tabs[no]

    def newTabMenu(self, tabid):
        men = tk.Menu(self.win)
        men.add_command(label="Close tab",  command=(lambda: self.closeTab (tabid)))
        men.add_command(label="Rename tab", command=(lambda: self.renameTab(tabid)))
        men.add_command(label="Clone tab",  command=(lambda: self.cloneTab (tabid)))
        men.add_separator()
        men.add_command(label="Move tab left",  command=(lambda: self.moveTabLeft (tabid)))
        men.add_command(label="Move tab right", command=(lambda: self.moveTabRight(tabid)))
        return men


    def onClose(self):
        scaDir = os.path.dirname(__file__)
        scaF = "{}/__last{}.sca"
        slxF = "{}/__last{}.slx"
        jsonPath = scaDir + "/__last.json"
        files = os.listdir(scaDir)

        isMaximised = self.win.state() == "zoomed"
        if isMaximised:
            self.win.state("normal")
            normalGeometry = self.win.geometry()
            self.win.state("zoomed")
        else:
            normalGeometry = self.win.geometry()

        # delete the .sca and .slx files
        for filename in filter(lambda s: re.match("__last\\d*\\.s(ca|lx)", s), files):
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
                } for no, conf in zip(range(len(self.tabs)), map(lambda t: t.getSCAConf(), self.tabs))
            ]
        }

        with open(jsonPath, mode=("w" if os.path.isfile(jsonPath) else "x"), encoding="utf8") as jsonfile:
            json.dump(jso, jsonfile, indent=2)
            
        self.win.destroy()


    def onClick(self, event):
        x, y, b = event.x, event.y, event.num
        if b == 1: return # left button
        try:
            tabClicked = self.notebook.index("@{},{}".format(x, y))
        except tk.TclError:
            tabClicked = -1
        isTabBar = y < 21
        isTab = tabClicked > -1
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
        tabid = self.notebook.index("current")
        if tabid < len(self.tabs) - 1:
            self.notebook.select(tabid+1)
        else:
            self.notebook.select(0)

    def onSwitchLeft(self, event):
        tabid = self.notebook.index("current")
        if tabid > 0:
            self.notebook.select(tabid - 1)
        else:
            self.notebook.select(len(self.tabs)-1)

    def build(self):

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
        self.win.bind("<Configure>", self.onResize)
        self.win.protocol("WM_DELETE_WINDOW", self.onClose)

    def loadLast(self):
        "load the contents from the __last files"
        scaDir = os.path.dirname(__file__)
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
        self.win.mainloop()


if __name__ == "__main__":
    scaWin = SCAWin()
    scaWin.mainloop()

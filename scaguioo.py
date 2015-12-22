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
import wx
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
        self.olxTxt.ChangeValue("\n".join(outputs))

    def saveSC(self, scPath):
        "Save the rewrites, categories and rules to a file."
        rews  = self.rewTxt.GetValue().strip().splitlines()
        cats  = self.catTxt.GetValue().strip().splitlines()
        rules = self.rulTxt.GetValue().strip().splitlines()
        scContent = toSC(rews, cats, rules)
        with open(scPath, mode=("w" if os.path.isfile(scPath) else "x"),
                  encoding="utf8") as scFile:
            scFile.write(scContent)

    def saveLex(self, lexPath):
        "Save the input lexicon to a file."
        lexContent = self.ilxTxt.GetValue().strip()
        with open(lexPath, mode=("w" if os.path.isfile(lexPath) else "x"),
                  encoding="utf8") as lexFile:
            lexFile.write(lexContent)

    def loadSC(self, scPath):
        "Load the rewrites, categories and rules from a file, if it exists."
        exists = os.path.isfile(scPath)
        if exists:
            with open(scPath, encoding="utf8") as scFile:
                scContent = scFile.read()
            scContent = scContent.replace("\ufeff", "", 1) # get rid of that BOM
            rews, cats, rules = map("\n".join, fromSC(scContent))
            self.rewTxt.ChangeValue(rews.strip())
            self.catTxt.ChangeValue(cats.strip())
            self.rulTxt.ChangeValue(rules.strip())
        return exists

    def loadLex(self, lexPath):
        "Load the input lexicon from a file, if it exists."
        exists = os.path.isfile(lexPath)
        if exists:
            with open(lexPath, encoding="utf8") as lexFile:
                lexContent = lexFile.read()
            lexContent = lexContent.replace("\ufeff", "", 1) # get rid of that BOM
            self.ilxTxt.ChangeValue(lexContent.strip())
        return exists

    def setSCAConf(self, conf):
        "Set the tab contents to the settings in an sca.SCAConf object."
        self.rewTxt.ChangeValue("\n".join(conf.rewrites))
        self.catTxt.ChangeValue("\n".join(conf.categories))
        self.rulTxt.ChangeValue("\n".join(conf.rules))
        self.ilxTxt.ChangeValue("\n".join(conf.inLex))
        if isinstance(conf.outFormat, int):
            btn = [self.ofmRb1, self.ofmRb2,
                   self.ofmRb3, self.ofmRb4][conf.outFormat]
            btn.SetValue(True)
        else:
            self.ofmRb4.SetValue(True) # check "Custom"
            self.ofmEnt.ChangeValue(conf.outFormat)
        self.debChk.SetValue(conf.debug)
        self.reoChk.SetValue(conf.rewOut)

    def getSCAConf(self):
        "Return an sca.SCAConf object with the tab contents."
        c = sca.SCAConf()
        ofms = [self.ofmRb1, self.ofmRb2, self.ofmRb3, self.ofmRb4]
        try:
            of = list(map(wx.RadioButton.GetValue, ofms)).index(True)
        except ValueError:
            of = 0
        c.outFormat = of if of != 3 else self.ofmEnt.GetValue()
        c.rewOut = self.reoChk.GetValue()
        c.debug = self.debChk.GetValue()
        c.rewrites   = self.rewTxt.GetValue().strip().splitlines()
        c.categories = self.catTxt.GetValue().strip().splitlines()
        c.rules      = self.rulTxt.GetValue().strip().splitlines()
        c.inLex      = self.ilxTxt.GetValue().strip().splitlines()
        return c

    def arrangeCompact(self):
        newSizer = self.frm.Sizer is None
        if newSizer:
            self.frm.SetSizer(wx.GridBagSizer(vgap=0, hgap=10))
        sz = self.frm.Sizer
        szOpts = [
            ([self.rewLbl, (0, 0)], {"flag": wx.EXPAND}),
            ([self.catLbl, (0, 1)], {"flag": wx.EXPAND}),
            ([self.rulLbl, (0, 2)], {"flag": wx.EXPAND}),
            ([self.rewTxt, (1, 0)], {"flag": wx.EXPAND}),
            ([self.catTxt, (1, 1)], {"flag": wx.EXPAND}),
            ([self.rulTxt, (1, 2)], {"flag": wx.EXPAND}),
            ([self.optBox, (2, 0)], {"flag": wx.EXPAND|wx.TOP|wx.BOTTOM|wx.LEFT,
                                     "span": wx.GBSpan(2, 1),
                                     "border": 5}),
            ([self.ilxLbl, (2, 1)], {"flag": wx.EXPAND}),
            ([self.olxLbl, (2, 2)], {"flag": wx.EXPAND}),
            ([self.ilxTxt, (3, 1)], {"flag": wx.EXPAND,
                                     "span": wx.GBSpan(2, 1)}),
            ([self.olxTxt, (3, 2)], {"flag": wx.EXPAND,
                                     "span": wx.GBSpan(2, 1)}),
            ([self.appBtn, (4, 0)], {"flag": wx.EXPAND|wx.TOP|wx.BOTTOM|wx.LEFT,
                                     "border": 5})
        ]
        for args, kwargs in szOpts:
            sz.Add(*args, **kwargs)
        for widget in [self.rewTxt, self.catTxt, self.rulTxt,
                       self.ilxTxt, self.olxTxt]:
            widget.SetMinSize(wx.Size(140, 224))

        if newSizer:
            # all columns should resize
            for c in range(3): sz.AddGrowableCol(c, proportion=1)
            # rows 1 and 4 should resize
            sz.AddGrowableRow(1, proportion=1)
            sz.AddGrowableRow(4, proportion=1)

        # pack the options into the options panel
        # use a Sizer inside a Sizer because border
        self.optBox.SetSizer(wx.BoxSizer())
        self.optSiz = wx.BoxSizer(wx.VERTICAL)
        self.optBox.Sizer.Add(self.optSiz, flag=wx.ALL, border=10)
        for optWidget in ([wx.Size(0, 5)] +
                          list(self.optBox.GetChildren()) +
                          [wx.Size(0, 5)]):
            self.optSiz.Add(optWidget, flag=wx.EXPAND|wx.BOTTOM,
                                  border=5)
        szOfmEnt = self.optSiz.GetItem(self.ofmEnt)
        szOfmEnt.SetFlag(wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT) # a bit offset

    def tkbuildExpanded(self):
        "Arrange the contents in expanded view (in one row, ideal for \
maximised view)."
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

    def arrangeExpanded(self):
        ...


    def build(self, compact=True):
        """Build the GUI of the tab and arrange them either expanded (in
one row, ideal for maximised view) or compact (in two rows, better for a
small window).
"""
        edtfont = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,
                          wx.FONTWEIGHT_NORMAL, faceName="Consolas")
        self.rewLbl = wx.StaticText(self.frm, label="Rewrite rules")
        self.rewTxt = wx.TextCtrl(self.frm, style=wx.TE_MULTILINE|wx.TE_CHARWRAP)
        self.rewTxt.SetFont(edtfont)
        self.catLbl = wx.StaticText(self.frm, label="Categories")
        self.catTxt = wx.TextCtrl(self.frm, style=wx.TE_MULTILINE|wx.TE_CHARWRAP)
        self.catTxt.SetFont(edtfont)
        self.rulLbl = wx.StaticText(self.frm, label="Sound changes")
        self.rulTxt = wx.TextCtrl(self.frm, style=wx.TE_MULTILINE|wx.TE_CHARWRAP)
        self.rulTxt.SetFont(edtfont)

        self.optBox = wx.StaticBox(self.frm, label="Options")
        self.appBtn = wx.Button(self.frm, label="Apply")
        self.ilxLbl = wx.StaticText(self.frm, label="Input lexicon")
        self.ilxTxt = wx.TextCtrl(self.frm, style=wx.TE_MULTILINE|wx.TE_CHARWRAP)
        self.ilxTxt.SetFont(edtfont)
        self.olxLbl = wx.StaticText(self.frm, label="Output lexicon")
        self.olxTxt = wx.TextCtrl(self.frm, style = wx.TE_MULTILINE |
                                                       wx.TE_CHARWRAP |
                                                       wx.TE_READONLY )
        self.olxTxt.SetFont(edtfont)

        self.ofmLbl = wx.StaticText(self.optBox, label="Output format")
        self.ofmRb1 = wx.RadioButton(self.optBox, label="output")
        self.ofmRb2 = wx.RadioButton(self.optBox, label="input \u2192 output")
        self.ofmRb3 = wx.RadioButton(self.optBox, label="output [input]")
        self.ofmRb4 = wx.RadioButton(self.optBox, label="Custom:")
        self.ofmEnt = wx.TextCtrl(self.optBox)
        self.reoChk = wx.CheckBox(self.optBox, label="Rewrite on output")
        self.debChk = wx.CheckBox(self.optBox, label="Debug")
        self.debChk.Disable()

        self.frm.Bind(wx.EVT_BUTTON, lambda e: self.applyRules(), self.appBtn)
        # TODO:
        ##self.ilxTxt.Bind(wx.EVT_SCROLLWIN, ...)
        ##self.olxTxt.Bind(wx.EVT_SCROLLWIN, ...)
        # check ‘Custom’ if custom format Entry gets the focus
        self.ofmEnt.Bind(wx.EVT_SET_FOCUS, lambda e: self.ofmRb4.SetValue(True))

        if compact:
            self.arrangeCompact()
        else:
            self.arrangeExpanded()

    def __init__(self, master=None, conf=None, compact=True):
        self.frm = wx.Panel(master.notebook)
        ##self.build(compact)
        self.build(True)
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


    def tabidx(self, tabno):
        return (tabno if tabno < -1 else self.notebook.GetSelection())

    def curTab(self):
        "Return the SCATab object of the current tab."
        return self.tabs[self.notebook.GetSelection()]

    def tkaskSaveSC(self):
        tab = self.curTab()
        scPath = filedialog.asksaveasfilename(defaultextension="sca", filetypes=self.scTypes, initialfile=tab.lastSC)
        if scPath:
            tab.saveSC(scPath)
            tab.lastSC = scPath

    def tkaskSaveLex(self):
        tab = self.curTab()
        lexPath = filedialog.asksaveasfilename(defaultextension="slx", filetypes=self.lexTypes, initialfile=tab.lastLex)
        if lexPath:
            tab.saveLex(lexPath)
            tab.lastLex = lexPath

    def tkaskSaveOut(self):
        tab = self.curTab()
        lexPath = filedialog.asksaveasfilename(defaultextension="slx", filetypes=self.lexTypes, initialdir=os.path.dirname(tab.lastLex))
        if lexPath:
            lexContent = tab.olxTxt.get("1.0","end")
            with open(lexPath, mode=("w" if os.path.isfile(lexPath) else "x"), encoding="utf8") as lexFile:
                lexFile.write(lexContent)

    def tkaskOpenSC(self):
        tab = self.curTab()
        scPath = filedialog.askopenfilename(filetypes=self.scTypes, initialfile=tab.lastSC)
        if scPath:
            tab.loadSC(scPath)
            tab.lastSC = scPath

    def tkaskOpenLex(self):
        tab = self.curTab()
        lexPath = filedialog.askopenfilename(filetypes=self.lexTypes, initialfile=tab.lastLex)
        if lexPath:
            tab.loadLex(lexPath)
            tab.lastLex = lexPath

    def clearRules(self):
        "Clear the rewrites, categories and rules fields of the current tab."
        if self.tabs:
            tab = self.curTab()
            tab.rewTxt.Clear()
            tab.catTxt.Clear()
            tab.rulTxt.Clear()

    def newTab(self):
        "Open a new blank tab."
        tab = SCATab(self, compact=self.isCompact)
        self.tabs.append(tab)
        self.notebook.AddPage(tab.frm, "New tab", select=True)

    def closeTab(self, tabno):
        "Close tab and keep it for restoring."
        if self.tabs:
            print("Closing tab", tabno)
            self.closedTabs.append((
                self.tabs.pop(tabno),
                self.notebook.GetPageText(tabno)
            ))
            self.notebook.RemovePage(tabno)

    def restoreTab(self):
        "Restore last closed tab."
        if self.closedTabs:
            tab, text = self.closedTabs.pop()
            self.tabs.append(tab)
            self.notebook.AddPage(tab.frm, text, select=True)

    def renameTab(self, tabno):
        "Open a modal dialog for renaming tab."
        if self.tabs:
            renDlg = wx.Dialog(self.win, title="Rename tab")
            renDlg.SetMinSize(wx.Size(200, 100))
            renDlg.SetSizer(BoxSizer(wx.VERTICAL))
            renLbl = wx.StaticText(renDlg, label="Enter new name:")
            renEnt = wx.TextCtrl(renDlg, value=self.notebook.GetPageText(tabno))
            renBtn = wx.Button(renDlg, id=wx.ID_OK, label="Ok")
            for widget in [renLbl, renEnt, renBtn]:
                renDlg.Sizer.Add(widget, proportion=1,
                                 flag=wx.ALL|wx.EXPAND, border=5)
            def renOk(event):
                self.notebook.SetPageText(tabno, renEnt.GetValue())
                event.Skip()
            renDlg.Bind(wx.EVT_CLOSE, renOk, id=wx.ID_OK)
            renDlg.ShowModal()

    def cloneTab(self, tabno):
        "Open a new tab with the same contents as tab."
        otab = self.tabs[tabno]
        self.newTab()
        ntab = curTab()
        ntab.setSCAConf(otab.getSCAConf())

    def moveTabRight(self, tabno):
        "Swap tab with its right neighbour."
        tabtext = self.notebook.GetPageText(tabno)
        tab = self.tabs.pop(tabno)
        self.notebook.RemovePage(tabno)
        if tabno < len(self.tabs) - 1:
            self.notebook.InsertPage(tabid+1, tab.frm, tabtext, select=True)
            self.tabs.insert(tab, tabno+1)
        else:
            self.notebook.InsertPage(0, tab.frm, tabtext, select=True)
            self.tabs.insert(0, tab)

    def moveTabLeft(self, tabno):
        "Swap tab with its left neighbour."
        tabtext = self.notebook.GetPageText(tabno)
        tab = self.tabs.pop(tabno)
        self.notebook.RemovePage(tabno)
        if tabno > 0:
            self.notebook.InsertPage(tabno-1, tab.frm, tabtext, select=True)
            self.tabs.insert(tab, tabno-1)
        else:
            self.notebook.AddPage(tab.frm, tabtext, select=True)
            self.tabs.append(tabno)

    def newTabMenu(self, tabno):
        "Create a new popup menu for tab."
        men = wx.Menu()
        clstb = men.Append(wx.ID_ANY, "Close tab")
        rentb = men.Append(wx.ID_ANY, "Rename tab")
        clntb = men.Append(wx.ID_ANY, "Clone tab")
        men.AppendSeparator()
        mvltb = men.Append(wx.ID_ANY, "Move tab left")
        mvrtb = men.Append(wx.ID_ANY, "Move tab right")
        men.Bind(wx.EVT_MENU, lambda e: self.closeTab (self.tabidx(tabno)), clstb)
        men.Bind(wx.EVT_MENU, lambda e: self.renameTab(self.tabidx(tabno)), rentb)
        men.Bind(wx.EVT_MENU, lambda e: self.cloneTab (self.tabidx(tabno)), clntb)
        men.Bind(wx.EVT_MENU, lambda e: self.moveTabLeft (self.tabidx(tabno)), mvltb)
        men.Bind(wx.EVT_MENU, lambda e: self.moveTabRight(self.tabidx(tabno)), mvrtb)
        return men

    def onClose(self, event):
        "Event handler for closing the window. Includes saving the configuration, the tabs and their contents to the __last files."
        scaDir = os.path.dirname(os.path.abspath(__file__)) + "\\WDwxport"
        scaF = "{}\\__last{}.sca"
        slxF = "{}\\__last{}.slx"
        jsonPath = scaDir + "\\__last.json"
        if not os.path.exists(scaDir):
            os.mkdir(scaDir)

        isMaximised = self.win.IsMaximized()
        if isMaximised:
            self.win.Maximize(False)
            normalRect = tuple(self.win.GetRect())
            self.win.Maximize(True)
        else:
            normalRect = tuple(self.win.GetRect())

        # delete the .sca and .slx files
        for filename in filter(lambda s: re.match("__last\\d*\\.s(ca|lx)", s), os.listdir(scaDir)):
            os.remove(scaDir + "/" + filename)

        # save each of the tabs in a .sca and a .slx file
        for no, tab in enumerate(self.tabs):
            tab.saveSC (scaF.format(scaDir, no))
            tab.saveLex(slxF.format(scaDir, no))

        # save everything in a .json file, too
        jso = {
            "rect": normalRect,
            "curTab": (self.notebook.GetSelection() if self.tabs else None),
            "isMaximised": isMaximised,
            "tabs": [
                {
                    "name": self.notebook.GetPageText(no),
                    "outFormat": conf.outFormat if isinstance(conf.outFormat, int) else 3,
                    "customFormat": conf.outFormat if isinstance(conf.outFormat, str) else "",
                    "rewOut": conf.rewOut,
                    "debug": conf.debug,
                    "rewrites": conf.rewrites,
                    "categories": conf.categories,
                    "rules": conf.rules,
                    "inLex": conf.inLex,
                    "outLex": self.tabs[no].olxTxt.GetValue().splitlines(),
                    "lastSC": self.tabs[no].lastSC,
                    "lastLex": self.tabs[no].lastLex
                }
                for no, conf in enumerate(map(lambda t: t.getSCAConf(), self.tabs))
            ]
        }

        with open(jsonPath, mode=("w" if os.path.isfile(jsonPath) else "x"), encoding="utf8") as jsonfile:
            json.dump(jso, jsonfile, indent=2)
        event.Skip()

    def onClick(self, event):
        "Event handler for any mouse button click."
        x, y = event.GetPosition()
        b = event.GetButton()
        if b == wx.MOUSE_BTN_LEFT:
            # left button does nothing
            event.Skip()
            return
        tabClicked, dummy = self.notebook.HitTest(wx.Point(x, y))
        isTab = tabClicked != wx.NOT_FOUND
        isTabBar = y < 21
        if b == wx.MOUSE_BTN_MIDDLE:
            if isTabBar:            # tab bar or tab middle clicked
                if isTab:
                    self.closeTab(tabClicked)
                else:
                    self.newTab()
            else:
                event.Skip()
        elif b == wx.MOUSE_BTN_RIGHT: # right click
            if isTabBar and isTab: # a tab
                self.win.PopupMenu(self.newTabMenu(tabClicked), wx.Point(x, y))
            else:
                event.Skip()

    def onResize(self, event):
        "Event handler for resizing the window."
        willCompact = self.win.Size.Width < 910
        if self.isCompact != willCompact:
            for tab in self.tabs:
                # get rid of the old layout
                tab.frm.Sizer.Clear(delete_windows=True)
                ##tab.build(willCompact)
                tab.build(True)
            self.isCompact = willCompact
        if self.isCompact:
            self.win.SetMinSize(wx.Size(474, 572))
        else:
            ##self.win.SetMinSize(wx.Size(..., ...)) # expanded
            self.win.SetMinSize(wx.Size(474, 572))
        event.Skip()

    def onSwitchRight(self, event):
        'Event handler for the "switch tab right" keyboard shortcut.'
        tabno = self.notebook.GetSelection()
        if tabno < len(self.tabs) - 1:
            self.notebook.SetSelection(tabno + 1)
        else:
            self.notebook.SetSelection(0)

    def onSwitchLeft(self, event):
        'Event handler for the "switch tab left" keyboard shortcut.'
        tabno = self.notebook.GetSelection()
        if tabno > 0:
            self.notebook.SetSelection(tabno - 1)
        else:
            self.notebook.SetSelection(len(self.tabs)-1)

    def onKeyPress(self, event):
        keyEvents = {
            "<F9>": (lambda e: self.curTab().applyRules()),
            "<Control-t>": (lambda e: self.newTab()),
            "<Control-w>": (lambda e: self.closeTab("current")),
            "<Control-Prior>": self.onSwitchLeft,
            "<Control-Next>": self.onSwitchRight,
            "<Control-Alt-Prior>": (lambda e: self.moveTabLeft("current")),
            "<Control-Alt-Next>": (lambda e: self.moveTabRight("current"))
        }
        key = event.GetKeyCode()
        if key in keyEvents:
            keyEvents[key](event)
        else:
            event.Skip()

    def build(self):
        """Build the actual GUI with the menu and the tabs, and bind the keyboard shortcuts.
Do not build any tabs or tab contents; that’s the task of newTab() and, ultimately, SCATab.make()."""
        self.notebook = wx.Notebook(self.win, style=wx.NB_TOP)
        self.win.Sizer.Add(self.notebook, proportion=1, flag=wx.EXPAND)

        # create a menu bar
        self.win.SetMenuBar(wx.MenuBar())

        # create the "rules" menu and bind events
        self.rulmen = wx.Menu()
        loadR = self.rulmen.Append(wx.ID_OPEN, "Load from file \u2026")
        saveR = self.rulmen.Append(wx.ID_SAVEAS, "Save to file \u2026")
        self.rulmen.AppendSeparator()
        clRew = self.rulmen.Append(wx.ID_ANY, "Clear rewrite rules")
        clCat = self.rulmen.Append(wx.ID_ANY, "Clear categories")
        clRul = self.rulmen.Append(wx.ID_ANY, "Clear sound change rules")
        clAll = self.rulmen.Append(wx.ID_ANY, "Clear all")
        #self.win.Bind(wx.EVT_MENU, self.onOpenSC, loadR)
        #self.win.Bind(wx.EVT_MENU, self.onSaveSC, saveR)
        self.win.Bind(wx.EVT_MENU, lambda e: self.curTab().rewTxt.Clear(), clRew)
        self.win.Bind(wx.EVT_MENU, lambda e: self.curTab().catTxt.Clear(), clCat)
        self.win.Bind(wx.EVT_MENU, lambda e: self.curTab().rulTxt.Clear(), clRul)
        self.win.Bind(wx.EVT_MENU, lambda e: self.clearRules, clAll)

        # create the "lexicon" menu and bind events
        self.lexmen = wx.Menu()
        loadL = self.lexmen.Append(wx.ID_ANY,      "Load from file \u2026")
        saveL = self.lexmen.Append(wx.ID_ANY,  "Save input to file \u2026")
        saveO = self.lexmen.Append(wx.ID_ANY, "Save output to file \u2026")
        self.lexmen.AppendSeparator()
        clLex = self.lexmen.Append(wx.ID_ANY, "Clear input lexicon")
        #self.win.Bind(wx.EVT_MENU, self.onOpenLex, loadL)
        #self.win.Bind(wx.EVT_MENU, self.onSaveLex, saveL)
        #self.win.Bind(wx.EVT_MENU, self.onSaveOut, saveO)
        self.win.Bind(wx.EVT_MENU, lambda e: self.curTab().ilxTxt.Clear(), clLex)

        # create the "tab" menu
        self.tabmen = self.newTabMenu(-1)
        self.tabmen.AppendSeparator()
        newtb = self.tabmen.Append(wx.ID_NEW, "New tab")
        rsttb = self.tabmen.Append(wx.ID_ANY, "Restore closed tab")
        self.win.Bind(wx.EVT_MENU, lambda e: self.newTab(), newtb)
        #self.win.Bind(wx.EVT_MENU, self.onRestoreTab, rsttb)

        # put them on the menu bar and the menu bar on the window
        self.win.MenuBar.Append(self.tabmen, "Tabs")
        self.win.MenuBar.Append(self.rulmen, "Rules")
        self.win.MenuBar.Append(self.lexmen, "Lexicon")

        self.win.Bind(wx.EVT_CHAR, self.onKeyPress)
        self.win.Bind(wx.EVT_CLOSE, self.onClose)
        self.win.Bind(wx.EVT_MOUSE_EVENTS, self.onClick)
        self.win.Bind(wx.EVT_SIZE, self.onResize)

    def loadLast(self):
        "Load the configuration, the tabs and their contents from the __last files."
        scaDir = os.path.dirname(os.path.abspath(__file__)) + "\\WDwxport"
        # load the .json file
        jsonPath = scaDir + "\\__last.json"
        try:
            with open(jsonPath, encoding="utf8") as jsonFile:
                jso = json.load(jsonFile)
            # restore everything from the .json file
            if "rect" in jso: self.win.SetRect(jso["rect"])
            if jso["isMaximised"]:
                self.win.SetWindowStyle(self.win.WindowStyle|wx.MAXIMIZE)
            for tabJSO in jso["tabs"]:
                # make a new tab
                self.newTab()
                no = self.notebook.GetSelection()
                tab = self.tabs[no]
                # load the tab options
                self.notebook.SetPageText(no, tabJSO["name"])
                tabConf = sca.SCAConf(
                    outFormat = (tabJSO["outFormat"]
                                 if tabJSO["outFormat"] != 3
                                 else tabJSO["customFormat"]),
                    rewOut = tabJSO["rewOut"],
                    debug = tabJSO["debug"],
                    rewrites = tabJSO["rewrites"],
                    categories = tabJSO["categories"],
                    rules = tabJSO["rules"],
                    inLex = tabJSO["inLex"]
                )
                tab.setSCAConf(tabConf)
                tab.lastSC = tabJSO["lastSC"]
                tab.lastLex = tabJSO["lastLex"]
                tab.olxTxt.SetValue("\n".join(tabJSO["outLex"]))
            if jso["curTab"] is not None:
                self.notebook.SetSelection(jso["curTab"])
            print("Successfully loaded.")
        except FileNotFoundError as e:
            self.newTab()
            no = self.notebook.GetSelection()
            tab = self.tabs[no]
            tab.setSCAConf(sca.example)
            print("Could not load.")
            print(e)

    def __init__(self):
        self.app = wx.App(0) # 1 → stdout and stderr in a window
        self.win = wx.Frame(None, wx.ID_ANY,
                            title="PythonSCA\u00b2", size=wx.Size(460, 522))
        self.app.SetTopWindow(self.win)
        self.win.SetSizer(wx.BoxSizer())
        self.build()
        self.loadLast()
        self.win.Show()
        self.app.MainLoop()


if __name__ == "__main__":
    scaWin = SCAWin()

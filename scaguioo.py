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
        self.frm.SetSizer(wx.GridBagSizer(vgap=0, hgap=10), deleteOld=True)
        sz = self.frm.Sizer
        sz.SetEmptyCellSize(wx.Size(0, 0))
        szOpts = [
            ([self.rewLbl, (0, 0)], {"flag": wx.EXPAND}),
            ([self.catLbl, (0, 1)], {"flag": wx.EXPAND}),
            ([self.rulLbl, (0, 2)], {"flag": wx.EXPAND}),
            ([self.rewTxt, (1, 0)], {"flag": wx.EXPAND}),
            ([self.catTxt, (1, 1)], {"flag": wx.EXPAND}),
            ([self.rulTxt, (1, 2)], {"flag": wx.EXPAND}),
            ([self.optBox, (2, 0)], {"flag": wx.EXPAND|wx.TOP|wx.BOTTOM|wx.LEFT,
                                     "span": (2, 1), "border": 5}),
            ([self.ilxLbl, (2, 1)], {"flag": wx.EXPAND}),
            ([self.olxLbl, (2, 2)], {"flag": wx.EXPAND}),
            ([self.ilxTxt, (3, 1)], {"flag": wx.EXPAND, "span": (2, 1)}),
            ([self.olxTxt, (3, 2)], {"flag": wx.EXPAND, "span": (2, 1)}),
            ([self.appBtn, (4, 0)], {"flag": wx.EXPAND|wx.TOP|wx.BOTTOM|wx.LEFT,
                                     "border": 5})
        ]
        for args, kwargs in szOpts:
            sz.Add(*args, **kwargs)
        for widget in [self.rewTxt, self.catTxt, self.rulTxt,
                       self.ilxTxt, self.olxTxt]:
            widget.SetMinSize(wx.Size(140, 224))

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

    def arrangeExpanded(self):
        self.frm.SetSizer(wx.GridBagSizer(vgap=0, hgap=10), deleteOld=True)
        sz = self.frm.Sizer
        sz.SetEmptyCellSize(wx.Size(0, 0))
        szOpts = [
            ([self.optBox, (0, 0)], {"flag": wx.EXPAND|wx.TOP|wx.BOTTOM|wx.LEFT,
                                     "span": wx.GBSpan(2, 1), "border": 5}),
            ([self.rewLbl, (0, 1)], {"flag": wx.EXPAND}),
            ([self.catLbl, (0, 2)], {"flag": wx.EXPAND}),
            ([self.rulLbl, (0, 3)], {"flag": wx.EXPAND}),
            ([self.ilxLbl, (0, 4)], {"flag": wx.EXPAND}),
            ([self.olxLbl, (0, 5)], {"flag": wx.EXPAND}),
            ([self.rewTxt, (1, 1)], {"flag": wx.EXPAND, "span": (3, 1)}),
            ([self.catTxt, (1, 2)], {"flag": wx.EXPAND, "span": (3, 1)}),
            ([self.rulTxt, (1, 3)], {"flag": wx.EXPAND, "span": (3, 1)}),
            ([self.ilxTxt, (1, 4)], {"flag": wx.EXPAND, "span": (3, 1)}),
            ([self.olxTxt, (1, 5)], {"flag": wx.EXPAND, "span": (3, 1)}),
            ([self.appBtn, (3, 0)], {"flag": wx.EXPAND|wx.TOP|wx.BOTTOM|wx.LEFT,
                                     "border": 5})
        ]
        for args, kwargs in szOpts:
            sz.Add(*args, **kwargs)
        for widget in [self.rewTxt, self.catTxt, self.rulTxt,
                       self.ilxTxt, self.olxTxt]:
            widget.SetMinSize(wx.Size(140, 224))

        # all columns except the first should resize
        for c in range(1, 6): sz.AddGrowableCol(c, proportion=1)
        # rows 2 and 3 should resize
        sz.AddGrowableRow(2, proportion=2)
        sz.AddGrowableRow(3, proportion=1)

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

    def arrange(self, compact):
        if compact:
            self.arrangeCompact()
        else:
            self.arrangeExpanded()

    def build(self, compact=True):
        """Build the GUI of the tab and arrange them either expanded (in
one row, ideal for maximised view) or compact (in two rows, better for a
small window).
"""
        edtfont = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,
                          wx.FONTWEIGHT_NORMAL, faceName="Consolas")
        self.rewLbl = wx.StaticText(self.frm, label="Rewrite rules")
        self.rewTxt = wx.TextCtrl(self.frm, style=wx.TE_MULTILINE|wx.TE_CHARWRAP)
        self.catLbl = wx.StaticText(self.frm, label="Categories")
        self.catTxt = wx.TextCtrl(self.frm, style=wx.TE_MULTILINE|wx.TE_CHARWRAP)
        self.rulLbl = wx.StaticText(self.frm, label="Sound changes")
        self.rulTxt = wx.TextCtrl(self.frm, style=wx.TE_MULTILINE|wx.TE_CHARWRAP)

        self.optBox = wx.StaticBox(self.frm, label="Options")
        self.appBtn = wx.Button(self.frm, label="Apply")
        self.ilxLbl = wx.StaticText(self.frm, label="Input lexicon")
        self.ilxTxt = wx.TextCtrl(self.frm, style=wx.TE_MULTILINE|wx.TE_CHARWRAP)
        self.olxLbl = wx.StaticText(self.frm, label="Output lexicon")
        self.olxTxt = wx.TextCtrl(self.frm, style = wx.TE_MULTILINE |
                                                       wx.TE_CHARWRAP |
                                                       wx.TE_READONLY )

        self.ofmLbl = wx.StaticText(self.optBox, label="Output format")
        self.ofmRb1 = wx.RadioButton(self.optBox, label="output")
        self.ofmRb2 = wx.RadioButton(self.optBox, label="input \u2192 output")
        self.ofmRb3 = wx.RadioButton(self.optBox, label="output [input]")
        self.ofmRb4 = wx.RadioButton(self.optBox, label="Custom:")
        self.ofmEnt = wx.TextCtrl(self.optBox)
        self.reoChk = wx.CheckBox(self.optBox, label="Rewrite on output")
        self.debChk = wx.CheckBox(self.optBox, label="Debug")
        self.debChk.Disable()

        for textw in [self.rewTxt, self.catTxt, self.rulTxt,
                      self.ilxTxt, self.olxTxt]:
            textw.SetFont(edtfont)
            # for some reason, this does not work
            def handleKey(event):
                key = event.GetKeyCode(), event.GetModifiers()
                if key == (ord("A"), wx.MOD_CONTROL):
                    textw.SelectAll()
                else:
                    event.Skip()
            textw.Bind(wx.EVT_KEY_DOWN, handleKey)

        self.frm.Bind(wx.EVT_BUTTON, lambda e: self.applyRules(), self.appBtn)
        # TODO:
        ##self.ilxTxt.Bind(wx.EVT_SCROLLWIN, ...)
        ##self.olxTxt.Bind(wx.EVT_SCROLLWIN, ...)
        # check ‘Custom’ if custom format Entry gets the focus
        self.ofmEnt.Bind(wx.EVT_SET_FOCUS, lambda e: self.ofmRb4.SetValue(True))

        self.arrange(compact)

    def __init__(self, master=None, conf=None, compact=True):
        self.frm = wx.Panel(master.notebook)
        self.build(compact)
        if conf is not None:
            self.setSCAConf(conf)


class SCAWin:
    """The PythonSCA GUI application."""

    tabs       = []
    closedTabs = []
    isCompact = False

    scTypes =  "SCA sound change files (*.sca; *.sc)|*.sca;*.sc|All files (*.*)|*.*"

    lexTypes = "SCA lexicon files (*.slx; *.lex)|*.slx;*.lex|All files (*.*)|*.*"


    def tabidx(self, tabno):
        return (tabno if tabno > -1 else self.notebook.GetSelection())

    def curTab(self):
        "Return the SCATab object of the current tab."
        return self.tabs[self.notebook.GetSelection()]

    def askSaveSC(self):
        tab = self.curTab()
        lastdir, lastfile = os.path.split(tab.lastSC)
        dlg = wx.FileDialog(self.win, defaultDir=lastdir, defaultFile=lastfile,
                wildcard=self.scTypes, style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            scPath = dlg.GetPath()
            tab.saveSC(scPath)
            tab.lastSC = scPath

    def askSaveLex(self):
        tab = self.curTab()
        lastdir, lastfile = os.path.split(tab.lastLex)
        dlg = wx.FileDialog(self.win, defaultDir=lastdir, defaultFile=lastfile,
                wildcard=self.lexTypes, style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            lexPath = dlg.GetPath()
            tab.saveLex(lexPath)
            tab.lastLex = lexPath

    def askSaveOut(self):
        tab = self.curTab()
        lastdir, lastfile = os.path.split(tab.lastLex)
        dlg = wx.FileDialog(self.win, defaultDir=lastdir, defaultFile=lastfile,
                wildcard=self.lexTypes, style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            lexPath = dlg.GetPath()
            lexContent = tab.olxTxt.GetValue()
            with open(lexPath, mode=("w" if os.path.isfile(lexPath) else "x"),
                      encoding="utf8") as lexFile:
                lexFile.write(lexContent)

    def askOpenSC(self):
        tab = self.curTab()
        lastdir, lastfile = os.path.split(tab.lastSC)
        dlg = wx.FileDialog(self.win, defaultDir=lastdir, defaultFile=lastfile,
                            wildcard=self.scTypes, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            scPath = dlg.GetPath()
            tab.loadSC(scPath)
            tab.lastSC = scPath

    def askOpenLex(self):
        tab = self.curTab()
        lastdir, lastfile = os.path.split(tab.lastLex)
        dlg = wx.FileDialog(self.win, defaultDir=lastdir, defaultFile=lastfile,
                            wildcard=self.lexTypes, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            lexPath = dlg.GetPath()
            tab.loadLex(lexPath)
            tab.lastLex = lexPath

    def clearRules(self):
        "Clear the rewrites, categories and rules fields of the current tab."
        if self.tabs:
            tab = self.curTab()
            tab.rewTxt.Clear()
            tab.catTxt.Clear()
            tab.rulTxt.Clear()

    def newTab(self, tabtext="New tab"):
        "Open a new blank tab."
        tab = SCATab(self, compact=self.isCompact)
        self.tabs.append(tab)
        self.notebook.AddPage(tab.frm, tabtext, select=True)

    def closeTab(self, tabno):
        "Close tab and keep it for restoring."
        if self.tabs:
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
            renDlg = wx.TextEntryDialog(self.win, "Enter new name:",
                                        caption="Rename tab",
                                        value=self.notebook.GetPageText(tabno))
            renDlg.ShowModal()
            # self.notebook.SetPageText() won’t work,
            # because of a bug in wxPython
            # that’s why we create a new page with the same content
            tab = self.tabs[tabno]
            # wx.Notebook.SetSelection is also affected by this bug,
            # otherwise we’d use self.notebook.SetSelection(sel)
            sel = self.notebook.GetSelection()
            self.notebook.RemovePage(tabno)
            self.notebook.InsertPage(tabno, tab.frm, text=renDlg.GetValue(),
                                     select=(sel == tabno))

    def cloneTab(self, tabno):
        "Open a new tab with the same contents as tab."
        otab = self.tabs[tabno]
        # For some reason, the SetPageText/SetSelection bug appears here, too.
        # That’s why the new tab will have the name "New tab".
        self.newTab()
        #~ self.newTab(self.notebook.GetPageText(tabno))
        ntab = self.curTab()
        ntab.setSCAConf(otab.getSCAConf())

    def moveTabRight(self, tabno):
        "Swap tab with its right neighbour."
        tabtext = self.notebook.GetPageText(tabno)
        tab = self.tabs.pop(tabno)
        self.notebook.RemovePage(tabno)
        if tabno < len(self.tabs):
            self.notebook.InsertPage(tabno+1, tab.frm, tabtext, select=True)
            self.tabs.insert(tabno+1, tab)
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
            self.tabs.insert(tabno-1, tab)
        else:
            self.notebook.AddPage(tab.frm, tabtext, select=True)
            self.tabs.append(tab)

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
        scaDir = os.path.dirname(os.path.abspath(__file__))
        if os.path.isfile(scaDir): # if it’s packed
            # then the WD is created in the containing folder
            scaDir = os.path.dirname(scaDir)
        scaDir += "\\WD"
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

    def onWinClick(self, event):
        "Event handler for any mouse button click on the window."
        b = event.GetButton()
        pos = event.GetPosition()
        x, y = pos
        if b == wx.MOUSE_BTN_MIDDLE and y <= 21 and y >= 2:
            self.newTab()
        else:
            event.Skip()

    def onNBClick(self, event):
        "Event handler for any mouse button click on the notebook."
        b = event.GetButton()
        if b == wx.MOUSE_BTN_LEFT:
            # left button does nothing
            event.Skip()
            return
        pos = event.GetPosition()
        # HitTest doesn’t work
        tabClicked, dummy = self.notebook.HitTest(pos)
        if b == wx.MOUSE_BTN_MIDDLE:
            self.closeTab(tabClicked)
        elif b == wx.MOUSE_BTN_RIGHT: # right click
            self.win.PopupMenu(self.newTabMenu(tabClicked), pos)

    def onResize(self, event):
        "Event handler for resizing the window."
        willCompact = self.win.Size.Width < 910
        if self.isCompact != willCompact:
            for tab in self.tabs:
                tab.arrange(willCompact)
            self.isCompact = willCompact
        if self.isCompact:
            self.win.SetMinSize(wx.Size(474, 572))
        else:
            self.win.SetMinSize(wx.Size(474, 406))
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
        curTabID = self.notebook.GetSelection()
        keyEvents = {
            (wx.WXK_F9, wx.MOD_NONE):
                lambda e: self.curTab().applyRules(),
            (ord("T"), wx.MOD_CONTROL):
                lambda e: self.newTab(),
            (ord("W"), wx.MOD_CONTROL):
                lambda e: self.closeTab(curTabID),
            (wx.WXK_PAGEUP, wx.MOD_CONTROL): self.onSwitchLeft,
            (wx.WXK_PAGEDOWN, wx.MOD_CONTROL): self.onSwitchRight,
            (wx.WXK_PAGEUP, wx.MOD_CONTROL|wx.MOD_ALT):
                lambda e: self.moveTabLeft(curTabID),
            (wx.WXK_PAGEDOWN, wx.MOD_CONTROL|wx.MOD_ALT):
                lambda e: self.moveTabRight(curTabID)
        }
        key = event.GetKeyCode(), event.GetModifiers()
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
        self.win.Bind(wx.EVT_MENU, lambda e: self.askOpenSC(), loadR)
        self.win.Bind(wx.EVT_MENU, lambda e: self.askSaveSC(), saveR)
        self.win.Bind(wx.EVT_MENU, lambda e: self.curTab().rewTxt.Clear(), clRew)
        self.win.Bind(wx.EVT_MENU, lambda e: self.curTab().catTxt.Clear(), clCat)
        self.win.Bind(wx.EVT_MENU, lambda e: self.curTab().rulTxt.Clear(), clRul)
        self.win.Bind(wx.EVT_MENU, lambda e: self.clearRules(), clAll)

        # create the "lexicon" menu and bind events
        self.lexmen = wx.Menu()
        loadL = self.lexmen.Append(wx.ID_ANY,      "Load from file \u2026")
        saveL = self.lexmen.Append(wx.ID_ANY,  "Save input to file \u2026")
        saveO = self.lexmen.Append(wx.ID_ANY, "Save output to file \u2026")
        self.lexmen.AppendSeparator()
        clLex = self.lexmen.Append(wx.ID_ANY, "Clear input lexicon")
        self.win.Bind(wx.EVT_MENU, lambda e: self.askOpenLex(), loadL)
        self.win.Bind(wx.EVT_MENU, lambda e: self.askSaveLex(), saveL)
        self.win.Bind(wx.EVT_MENU, lambda e: self.askSaveOut(), saveO)
        self.win.Bind(wx.EVT_MENU, lambda e: self.curTab().ilxTxt.Clear(), clLex)

        # create the "tab" menu
        self.tabmen = self.newTabMenu(-1)
        self.tabmen.AppendSeparator()
        newtb = self.tabmen.Append(wx.ID_NEW, "New tab")
        rsttb = self.tabmen.Append(wx.ID_ANY, "Restore closed tab")
        self.win.Bind(wx.EVT_MENU, lambda e: self.newTab(), newtb)
        self.win.Bind(wx.EVT_MENU, lambda e: self.restoreTab(), rsttb)

        # put them on the menu bar and the menu bar on the window
        self.win.MenuBar.Append(self.tabmen, "Tabs")
        self.win.MenuBar.Append(self.rulmen, "Rules")
        self.win.MenuBar.Append(self.lexmen, "Lexicon")

        self.win.Bind(wx.EVT_CHAR_HOOK, self.onKeyPress)
        self.win.Bind(wx.EVT_CLOSE, self.onClose)
        self.win.Bind(wx.EVT_MOUSE_EVENTS, self.onWinClick)
        #~ self.notebook.Bind(wx.EVT_MOUSE_EVENTS, self.onNBClick)
        self.win.Bind(wx.EVT_SIZE, self.onResize)

    def loadLast(self):
        "Load the configuration, the tabs and their contents from the __last files."
        scaDir = os.path.dirname(os.path.abspath(__file__))
        if os.path.isfile(scaDir): # if it’s packed
            # then the WD is looked for in the containing folder
            scaDir = os.path.dirname(scaDir)
        scaDir += "\\WD"
        # load the .json file
        jsonPath = scaDir + "\\__last.json"
        try:
            with open(jsonPath, encoding="utf8") as jsonFile:
                jso = json.load(jsonFile)
            # restore everything from the .json file
            if "rect" in jso: self.win.SetRect(jso["rect"])
            if jso["isMaximised"]:
                self.win.Maximize()
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
        except FileNotFoundError as e:
            self.newTab()
            no = self.notebook.GetSelection()
            tab = self.tabs[no]
            tab.setSCAConf(sca.example)

    def __init__(self):
        self.win = wx.Frame(None, wx.ID_ANY,
                            title="PythonSCA\u00b2", size=wx.Size(460, 522))
        self.win.SetSizer(wx.BoxSizer())
        self.build()
        self.loadLast()

class PythonSCA(wx.App):

    def OnInit(self):
        self.scaWin = SCAWin()
        self.SetTopWindow(self.scaWin.win)
        self.scaWin.win.Show()
        return True

if __name__ == "__main__":
    app = PythonSCA(0)
    app.MainLoop()

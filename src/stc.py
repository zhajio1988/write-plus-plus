"""
stc.py - editor classes for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
NOTE: Parts of this file are based on code from SPE, Editra, and PythonWin
"""

import codecs
import os
import re
import shutil
import sys
import webbrowser
import wx
from io import StringIO
from wx import stc

_ = wx.GetTranslation

class SecondaryEditor(stc.StyledTextCtrl):
    def __init__(self, parent):
        stc.StyledTextCtrl.__init__(self, parent, -1, style=wx.NO_BORDER)
        self._frame = parent._parent

        self._parent = parent
        self.linenumwidth = -1
        self.styling = None

        self.AutoCompSetCancelAtStart(False)
        self.IndicatorSetForeground(2, "#00FF00")
        self.IndicatorSetStyle(2, stc.STC_INDIC_ROUNDBOX)
        self.SetDropTarget(EditorDropTarget(self))
        ##self.SetEdgeColumn(79)
        ##self.SetEdgeMode(stc.STC_EDGE_LINE)
        self.SetFoldFlags(stc.STC_FOLDFLAG_LINEAFTER_CONTRACTED)
        self.SetIndent(4)
        self.SetMouseDwellTime(1000)
        self.SetTabWidth(4)
        self.SetUseTabs(True)
        self.ShowBookmarks(True)

        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(stc.EVT_STC_CALLTIP_CLICK, self.OnCallTipClick)
        self.Bind(stc.EVT_STC_CHARADDED, self.OnCharAdded)
        self.Bind(stc.EVT_STC_DWELLSTART, self.OnDwellStart)
        self.Bind(stc.EVT_STC_DWELLEND, self.OnDwellEnd)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
        self.Bind(stc.EVT_STC_MODIFIED, self.OnModified)
        self.Bind(stc.EVT_STC_START_DRAG, self.OnStartDrag)
        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(stc.EVT_STC_ZOOM, self.OnZoom)

    def OnInit(self):
        again = hasattr(self, "dwelling")
        self.dwelling = False

        self.SetLanguage()
        self.ShowLineNumbers(True)

        if not again:
            self.Bind(stc.EVT_STC_SAVEPOINTLEFT, self.OnSavePointLeft)
            self.Bind(stc.EVT_STC_SAVEPOINTREACHED, self.OnSavePointReached)
            for event, func1, func2 in self._frame._app.plugins.stcevents:
                if func1:
                    func1 = getattr(self._parent.editors[0], func1)
                self._frame._app.plugins.RegisterEvent(event, func1, func2, self)

    def ShowLineNumbers(self, show=True):
        if show:
            self.SetMarginMask(1, 0)
            self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
            self.CalculateLineNumberWidth()
            self.SetMarginWidth(1, self.linenumwidth * len(str(self.GetLineCount())) + 7)
        else:
            self.SetMarginWidth(1, 0)

    def ShowBookmarks(self, show=True):
        if show:
            self.MarkerDefine(0, stc.STC_MARK_SHORTARROW, "#008000", wx.GREEN)
            self.SetMarginMask(2, ~stc.STC_MASK_FOLDERS)
            self.SetMarginSensitive(2, True)
            self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
            self.SetMarginWidth(2, self.GetZoom() + 16)
        else:
            self.SetMarginWidth(2, 0)

    def SetCodeFolding(self, show=True):
        if show:
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED, "#F3F3F3", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "#F3F3F3", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER, "#F3F3F3", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, "#F3F3F3", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "#F3F3F3", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, "#F3F3F3", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, "#F3F3F3", "#808080")
            self.SetMarginMask(3, stc.STC_MASK_FOLDERS)
            self.SetMarginSensitive(3, True)
            self.SetMarginType(3, stc.STC_MARGIN_SYMBOL)
            self.SetMarginWidth(3, self.GetZoom() + 16)
        else:
            self.SetMarginWidth(3, 0)
            for line in range(self.GetLineCount()):
                if self.GetFoldLevel(line) & stc.STC_FOLDLEVELHEADERFLAG:
                    if not self.GetFoldExpanded(line):
                        self.ToggleFold(line)
        self.SetProperty("fold", str(int(show)))

    def SetLanguage(self, language=None, again=False):
        if not language:
            language = self._parent.editors[0].language
        if language not in self._frame.styler.lexers:
            self._frame.styler.lexers[language] = getattr(__import__("syntax.%s" % language), language)
        self.lexer = self._frame.styler.lexers[language]
        if hasattr(self.lexer, "style"):
            language = self.lexer.style
        self.SetLexer(getattr(stc, "STC_LEX_%s" % (language.upper())))
        self.lexer.OnInit(self)
        default = self._frame.styler.GetStylesInfo("default")
        caretforeground = "caretforeground" in default
        if caretforeground:
            self.SetCaretForeground(default["caretforeground"]["fore"])
        caretlineback = "caretlineback" in default
        self.SetCaretLineVisible(caretlineback)
        if caretlineback:
            self.SetCaretLineBackground(default["caretlineback"]["back"])
        for style in default:
            if style != "caretforeground" and style != "caretlineback":
                self.StyleSetSpec(getattr(stc, "STC_STYLE_%s" % (style.upper())), self._frame.styler.FormatStyleInfo(default[style]))
        if language != "null":
            if language in lexers:
                lexer = lexers[language]
            else:
                lexer = language.upper()
            info = self._frame.styler.GetStylesInfo(language)
            for style in info:
                if not style.startswith("_"):
                    self.StyleSetSpec(getattr(stc, "STC_%s_%s" % (lexer, style.upper())), self._frame.styler.FormatStyleInfo(info[style]))
                else:
                    self.StyleSetSpec(getattr(stc, "STC%s" % style.upper()), self._frame.styler.FormatStyleInfo(info[style]))
        if again:
            self.Colourise(0, self.GetTextLength())

    def CalculateLineNumberWidth(self, zoom=0):
        old = self.GetFont()
        self.SetFont(wx.Font(max(1, self._frame.styler.linenumdata[0] + zoom), *self._frame.styler.linenumdata[1:]))
        self.linenumwidth = self.GetTextExtent("1234567890")[0] / 10    # Get the approximate width of one digit
        self.SetFont(old)

    def GetEOLChars(self):
        return ("\r\n", "\r", "\n")[self.GetEOLMode()]

    def Goto(self, line=-1):
        if line == -1:
            count = self.GetLineCount()
            line = wx.GetNumberFromUser(_("Enter a line number between 1 and %d:") % count, _("Go to line:"), _("Go to"), self.GetCurrentLine() + 1, 1, count, self._frame) - 1
        if line >= 0:
            self.EnsureVisible(line)
            self.GotoLine(line)

    def ToggleBookmark(self, line=-1):
        if line == -1:
            line = self.GetCurrentLine()
        if not self.MarkerGet(line):
            self.MarkerAdd(line, 0)
        else:
            self.MarkerDelete(line, 0)

    def NextBookmark(self):
        line = self.GetCurrentLine()
        if line + 1 < self.GetLineCount():
            next = self.MarkerNext(line + 1, 1)
            if next == -1:
                next = self.MarkerNext(1, 1)
        else:
            next = self.MarkerNext(1, 1)
        if next != -1:
            self.Goto(next)

    def PreviousBookmark(self):
        line = self.GetCurrentLine()
        if line > 0:
            previous = self.MarkerPrevious(line - 1, 1)
            if previous == -1:
                previous = self.MarkerPrevious(self.GetLineCount() - 1, 1)
        else:
            previous = self.MarkerPrevious(self.GetLineCount() - 1, 1)
        if previous != -1:
            self.Goto(previous)

    def ProperCase(self):
        self.ReplaceSelection(self.GetSelectedText().title())

    def SentenceCase(self):
        self.ReplaceSelection(self.GetSelectedText().capitalize())

    def Tabify(self):
        info = wx.BusyInfo(_("Tabifying '%s'...") % self._frame.GetEditor().filename)
        selection = self.GetSelectedText()
        eol = self.GetEOLChars()
        if len(selection):
            old = selection.split(eol)
        else:
            old = self.GetText().split(eol)
        width = self.GetIndent()
        spaces = " " * width
        new = []
        for line in old:
            tabs = 0
            while line.startswith(spaces):
                tabs += 1
                line = line[width:]
            new.append(("\t" * tabs) + line)
        self.ReplaceSelection(eol.join(new))
        info.Destroy()

    def Untabify(self):
        info = wx.BusyInfo(_("Untabifying '%s'...") % self._frame.GetEditor().filename)
        selection = self.GetSelectedText()
        eol = self.GetEOLChars()
        if len(selection):
            old = selection.split(eol)
        else:
            old = self.GetText().split(eol)
        width = self.GetIndent()
        new = []
        for line in old:
            spaces = 0
            while line.startswith("\t"):
                spaces += width
                line = line[1:]
            new.append((" " * spaces) + line)
        self.ReplaceSelection(eol.join(new))
        info.Destroy()

    def OnSetFocus(self, event):
        if self._frame.editor != self or not event:
            self.RefreshTitleBar()
            editor = self._parent.editors[0]
            full = self.GetTextLength() > 0
            self._frame.toolbar.EnableTool(wx.ID_PRINT, full)
            undo = editor.CanUndo()
            redo = editor.CanRedo()
            self._frame.toolbar.EnableTool(wx.ID_UNDO, undo)
            self._frame.toolbar.EnableTool(wx.ID_REDO, redo)
            selected = len(self.GetSelectedText()) > 0
            self._frame.toolbar.EnableTool(wx.ID_CUT, selected and not editor.readonly)
            self._frame.toolbar.EnableTool(wx.ID_COPY, selected)
            self._frame.toolbar.EnableTool(wx.ID_PASTE, not editor.readonly)
            self._frame.toolbar.Refresh(False)
            editor.UpdateStatusBar()
            self._frame.menubar.Enable(wx.ID_PRINT, full)
            self._frame.menubar.Enable(wx.ID_PREVIEW, full)
            self._frame.menubar.Enable(wx.ID_UNDO, undo)
            self._frame.menubar.Enable(wx.ID_REDO, redo)
            self._frame.menubar.Enable(wx.ID_CUT, selected and not editor.readonly)
            self._frame.menubar.Enable(wx.ID_COPY, selected)
            self._frame.menubar.Enable(wx.ID_PASTE, not editor.readonly)
            self._frame.menubar.Check(self._frame.menubar.ID_WORDWRAP, self.GetWrapMode())
            self._frame.editor = self
        self._parent.focused = self._parent.editors.index(self)
        event.Skip()

    def RefreshTitleBar(self):
        editor = self._parent.editors[0]
        head, tail = os.path.split(editor.filename)
        if editor.changes:
            tail = "*" + tail
        if editor.new:  # Don't show empty parentheses in the title bar
            self._frame.SetTitle("%s - Write++" % tail)
        elif not editor.readonly:
            self._frame.SetTitle("%s (%s) - Write++" % (tail, head))
        else:
            self._frame.SetTitle(_("%s [read-only] (%s) - Write++") % (tail, head))
        return tail

    def OnKillFocus(self, event):
        self.Cancel()
        self._frame.dragsource = -1
        event.Skip()

    def OnKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_INSERT:
            if not self._frame.editor.GetOvertype():
                self._frame.statusbar.SetStatusText("OVR", 5)
            else:
                self._frame.statusbar.SetStatusText("INS", 5)
        event.Skip()

    def OnLeftUp(self, event):
        self._frame.DoAutohide()
        event.Skip()

    def OnCallTipClick(self, event):
        self.CallTipCancel()

    def OnCharAdded(self, event):
        if event.GetKey() == wx.WXK_RETURN:
            self.lexer.OnNewLine(self)
        self.lexer.OnCharAdded(self)

    def OnDwellStart(self, event):
        if self._frame.IsActive() and hasattr(self.lexer, "OnDwellStart"):
            self.dwelling = self.lexer.OnDwellStart(self, event.GetX(), event.GetY())

    def OnDwellEnd(self, event):
        if self.dwelling:
            self.CallTipCancel()
            self.dwelling = False

    def OnMarginClick(self, event):
        margin = event.GetMargin()
        line = self.LineFromPosition(event.GetPosition())
        if margin == 2:
            self.ToggleBookmark(line)
        elif margin == 3:
            self.ToggleFold(line)

    def OnModified(self, event):
        mod = event.GetModificationType()
        if mod & stc.STC_MOD_INSERTTEXT or mod & stc.STC_MOD_DELETETEXT:
            actual = self.GetMarginWidth(1)
            desired = self.linenumwidth * len(str(self.GetLineCount())) + 7
            if actual > 0 and actual != desired:
                self.SetMarginWidth(1, desired)
            full = self.GetTextLength() > 0
            self._frame.toolbar.EnableTool(wx.ID_PRINT, full)
            undo = self.CanUndo()
            redo = self.CanRedo()
            self._frame.toolbar.EnableTool(wx.ID_UNDO, undo)
            self._frame.toolbar.EnableTool(wx.ID_REDO, redo)
            self._frame.toolbar.Refresh(False)
            self._frame.menubar.Enable(wx.ID_PRINT, full)
            self._frame.menubar.Enable(wx.ID_PREVIEW, full)
            self._frame.menubar.Enable(wx.ID_UNDO, undo)
            self._frame.menubar.Enable(wx.ID_REDO, redo)

    def OnStartDrag(self, event):
        self._frame.dragsource = self._frame.GetTab(self)

    def OnUpdateUI(self, event):
        if self._frame.FindFocus() != self:
            event.Skip()
            return
        pos = self.GetCurrentPos()
        brace1 = -1
        if pos > 0 and chr(self.GetCharAt(pos - 1)) in "(){}[]":
            brace1 = pos - 1
        elif pos > 0 and chr(self.GetCharAt(pos)) in "(){}[]":
            brace1 = pos
        brace2 = -1
        if brace1 != -1:
            brace2 = self.BraceMatch(brace1)
        if brace1 != -1 and brace2 == -1:
            self.BraceBadLight(brace1)
        else:
            self.BraceHighlight(brace1, brace2)
        selection = self.GetSelectedText()
        selected = len(selection)
        if (not selected) and (self.styling or len(selection.split()) > 1):
            self.StartStyling(0, stc.STC_INDICS_MASK)
            self.SetStyling(self.GetTextLength(), 0)
            self.Colourise(0, self.GetTextLength())
            self.styling = None
        elif selected and selection != self.styling:
            first = self.GetFirstVisibleLine()
            visible = self.LinesOnScreen()
            if self.GetLineCount() < visible:
                end = self.GetTextLength()
            else:
                end = self.GetLineEndPosition(first + visible)
            pos2 = self.FindText(self.PositionFromLine(first), end, selection, wx.FR_WHOLEWORD | wx.FR_MATCHCASE)
            start = self.GetSelectionStart()
            while pos2 != -1:
                if pos2 != start:
                    self.StartStyling(pos2, stc.STC_INDICS_MASK)
                    self.SetStyling(selected, stc.STC_INDIC2_MASK)
                    self.styling = selection
                pos2 = self.FindText(pos2 + selected, end, selection, wx.FR_WHOLEWORD | wx.FR_MATCHCASE)
        editor = self._parent.editors[0]
        self._frame.toolbar.EnableTool(wx.ID_CUT, selected and not editor.readonly)
        self._frame.toolbar.EnableTool(wx.ID_COPY, selected)
        self._frame.toolbar.Refresh(False)
        self._frame.statusbar.SetStatusText(_("Ln %d | Col %d | Sel %d") % (self.GetCurrentLine() + 1, self.GetColumn(pos) + 1, selected), 2)
        self._frame.menubar.Enable(wx.ID_CUT, selected and not editor.readonly)
        self._frame.menubar.Enable(wx.ID_COPY, selected)
        event.Skip()

    def OnZoom(self, event):
        zoom = self.GetZoom()
        self.CalculateLineNumberWidth(zoom)
        if self.GetMarginWidth(1) > 0:
            self.SetMarginWidth(1, self.linenumwidth * len(str(self.GetLineCount())) + 7)
        if self.GetMarginWidth(2) > 0:
            self.SetMarginWidth(2, zoom + 16)
        if self.GetMarginWidth(3) > 0:
            self.SetMarginWidth(3, zoom + 12)

    def OnSavePointLeft(self, event):
        editor = self._parent.editors[0]
        editor.changes = True
        filename = self.RefreshTitleBar()
        self._frame.notebook.SetPageText(self._frame.GetTab(self), filename)
        self._frame.toolbar.EnableTool(wx.ID_SAVE, True)
        self._frame.toolbar.EnableTool(self._frame.menubar.ID_SAVEALL, True)
        self._frame.toolbar.Refresh(False)
        self._frame.menubar.Enable(wx.ID_SAVE, True)
        self._frame.menubar.Enable(self._frame.menubar.ID_SAVEALL, True)
        self._frame.menubar.Enable(wx.ID_REVERT, True)

    def OnSavePointReached(self, event):
        editor = self._parent.editors[0]
        editor.changes = False
        filename = self.RefreshTitleBar()
        self._frame.notebook.SetPageText(self._frame.GetTab(self), filename)
        self._frame.toolbar.EnableTool(wx.ID_SAVE, False)
        changes = False
        for i in range(self._frame.notebook.GetPageCount()):
            if self._frame.GetEditor(i).changes:
                changes = True
                break
        self._frame.toolbar.EnableTool(self._frame.menubar.ID_SAVEALL, changes)
        self._frame.toolbar.Refresh(False)
        self._frame.menubar.Enable(wx.ID_SAVE, False)
        self._frame.menubar.Enable(self._frame.menubar.ID_SAVEALL, changes)
        self._frame.menubar.Enable(wx.ID_REVERT, False)
        self._frame.menubar.Enable(wx.ID_REFRESH, True)

class EditorDropTarget(wx.DropTarget):
    def __init__(self, editor):
        wx.DropTarget.__init__(self)
        self._frame = editor._frame

        self.editor = editor
        self.data = wx.DataObjectComposite()
        self.text = wx.TextDataObject()
        self.data.Add(self.text)
        self.filenames = wx.FileDataObject()
        self.data.Add(self.filenames)
        self.SetDataObject(self.data)

    def OnDragOver(self, x, y, default):
        self.GetData()
        if self.text.GetTextLength() > 1:
            result = self.editor.DoDragOver(x, y, default)
            if self._frame.GetTab(self.editor) != self._frame.dragsource:
                return alternate[result]
            return result
        elif len(self.filenames.GetFilenames()):
            return wx.DragCopy
        return default

    def OnData(self, x, y, default):
        self.GetData()
        if self.text.GetTextLength() > 1:
            self.editor.DoDropText(x, y, self.text.GetText())
            self.text.SetText("")
            wx.CallAfter(setattr, self.editor._frame, "dropsource", -1)
            if self._frame.GetTab(self.editor) != self._frame.dragsource:
                return alternate[default]
        else:
            self._frame.OpenFiles(self.filenames.GetFilenames())
        return default

extensions = {"null":"txt", "ada":("ada", "ads", "adb"),
              "actionscript":("as", "mx"), "asm":"asm", "au3":"au3",
              "bash":("sh", "bsh", "csh", "ksh"), "batch":("bat", "cmd", "nt"),
              "c":"c", "caml":("ml", "mli", "sml", "thy"), "cmake":"cmake",
              "cpp":("h", "hpp", "hxx", "cpp", "cxx", "cc"), "csharp":"cs",
              "css":"css", "d":"d", "diff":("diff", "patch"),
              "fortran":("f", "for", "f90", "f95", "f2k"),
              "haskell":("hs", "lhs", "as", "las"),
              "html":("html", "htm", "shtml", "shtm", "xhtml", "hta"),
              "innosetup":"iss", "java":"java", "javascript":"js", "kix":"kix",
              "lisp":("lsp", "lisp"), "lua":"lua", "makefile":"mak",
              "matlab":"m", "nsis":("nsi", "nsh"), "pascal":("pas", "inc"),
              "php":("php", "php3", "phtml"), "perl":("pl", "pm", "plx"),
              "powershell":"ps1",
              "properties":("ini", "inf", "properties", "reg", "url"),
              "ps":"ps", "python":("py", "pyw"), "ruby":("rb", "rbw"),
              "sql":"sql", "smalltalk":"st", "tex":"tex", "vb":("vb", "vbs"),
              "verilog":"v", "vhdl":("vhd", "vhdl"),
              "xml":("xml", "xsml", "xsl", "xsd", "kml", "wsdl"), "yaml":"yml"}
lexers = {"bash":"SH", "batch":"BAT", "cpp":"C", "fortran":"F", "gui4cli":"GC",
          "haskell":"HA", "html":"H", "innosetup":"INNO", "makefile":"MAKE",
          "pascal":"PAS", "perl":"PL", "properties":"PROPS", "python":"P",
          "ruby":"RB", "smalltalk":"ST", "vb":"B", "verilog":"V", "xml":"H"}
alternate = {wx.DragNone:wx.DragNone, wx.DragCopy:wx.DragMove, wx.DragMove:wx.DragCopy, wx.DragCancel:wx.DragCancel}

class PrimaryEditor(SecondaryEditor):
    def __init__(self, parent, filename):
        super(PrimaryEditor, self).__init__(parent)

        self.bom = None
        self.encoding = sys.getdefaultencoding()
        self.raw = False
        self.readonly = False

    def OnInit(self, filename):
        self.askutf = True
        self.filename = filename
        self.keepnonexistent = False
        self.mtime = -1
        self.new = not os.path.exists(filename)

        if not self.new:
            self.changes = False
            self.Load()
            self.EmptyUndoBuffer()
        else:
            self.changes = None # New files have no changes, but should be able to be saved
        for editor in self._parent.editors:
            SecondaryEditor.OnInit(editor)
        self.UpdateStatusBar()

    def SetLanguage(self, language=None):
        extension = os.path.splitext(self.filename)[1].lower()
        if self.new:
            extension = ".txt"
        if not language:
            for language2 in extensions:
                if extension[1:] in extensions[language2]:
                    language = language2
                    break
            if not language:
                language = "null"
        again = hasattr(self, "filetype")
        for editor in self._parent.editors:
            SecondaryEditor.SetLanguage(editor, language, again)
        self.filetype = None
        self.image = wx.Bitmap()
        if len(extension):
            filetype = wx.TheMimeTypesManager.GetFileTypeFromExtension(extension)
            if filetype:
                description = filetype.GetDescription()
                if description:
                    space = description.rfind(" ")
                    if space != -1:
                        self.filetype = description[:space] + description[space:].lower()
                    else:
                        self.filetype = description
                if extension not in (".ani", ".cur", ".ico", ".lnk", ".exe"):   # Extensions with no one icon
                    info = filetype.GetIconInfo()
                    if info and info[0].IsOk():
                        x, y = wx.SystemSettings.GetMetric(wx.SYS_SMALLICON_X), wx.SystemSettings.GetMetric(wx.SYS_SMALLICON_Y)
                        self.image.CopyFromIcon(wx.Icon("%s;%s" % info[1:], wx.BITMAP_TYPE_ICO, x, y))
            if not self.filetype:
                self.filetype = _("%s file") % extension[1:].upper()
        elif not self.filetype:
            self.filetype = _("File")
        if again:
            self._frame.notebook.SetPageBitmap(self._frame.GetTab(self), self.image)
        self.language = language

    def Load(self):
        fileobj = open(self.filename, 'rb')
        try:
            text = fileobj.read()
        finally:
            fileobj.close()
        self.bom = None
        self.encoding = sys.getdefaultencoding()
        for bom in encodings:
            if text.startswith(bom):
                self.bom = bom
                self.encoding = encodings[bom]
                text = text[len(bom):]
                break
        try:
            text2 = text.decode(self.encoding)
        except UnicodeDecodeError:  # If default encoding fails, Latin1 seems to work
            text2 = text.decode("latin_1")
            self.encoding = "latin_1"
        else:
            if (not self.encoding.startswith("utf")) and "\0" in text2:
                for encoding in ("utf_16", "utf_16_be", "utf_16_le", "utf_32", "utf_32_be", "utf_32_le"):
                    try:
                        text2 = text.decode(self.encoding)
                    except UnicodeDecodeError:
                        pass
                    else:
                        self.encoding = encoding
                        break
        self.raw = "\0" in text2 and not self.encoding.startswith("utf")
        if not self.raw:
            self.SetText(text2)
        else:
            text2 = "\0".join(text2) + "\0"
            self.AddStyledText(StringIO(text2.encode(self.encoding)).getvalue())
        self.SetSavePoint()
        self.mtime = os.path.getmtime(self.filename)
        self.readonly = not os.access(self.filename, os.W_OK)
        first = self.GetLine(0)
        for editor in self._parent.editors:
            editor.SetReadOnly(self.readonly)
            if first.endswith("\r\n"):
                editor.SetEOLMode(stc.STC_EOL_CRLF)
            elif first.endswith("\r"):
                editor.SetEOLMode(stc.STC_EOL_CR)
            elif first.endswith("\n"):
                editor.SetEOLMode(stc.STC_EOL_LF)

    def UpdateStatusBar(self, full=True):
        if full:
            self._frame.statusbar.SetStatusText(self.filetype, 0)
        eol = self.GetEOLMode()
        if eol == 0:
            self._frame.statusbar.SetStatusText("Windows", 3)
        elif eol == 1:
            self._frame.statusbar.SetStatusText("Mac", 3)
        elif eol == 2:
            self._frame.statusbar.SetStatusText("Unix", 3)
        self._frame.statusbar.SetStatusText(self.encoding.upper().replace("LATIN", "Latin").replace("_", "-"), 4)
        if self.GetOvertype():
            self._frame.statusbar.SetStatusText("OVR", 5)
        else:
            self._frame.statusbar.SetStatusText("INS", 5)

    def Save(self, create=False):
        if not (os.path.isfile(self.filename) or create):
            self.SaveAs()
            return
        if not self.raw:
            text = self.GetText()
        else:
            length = self.GetTextLength()
            text = self.GetStyledText(0, length)[0:length * 2:2].decode(self.encoding)
        try:
            text = text.encode(self.encoding)   # Encode first to avoid losing file
        except UnicodeEncodeError:  # If there are unicode chars, save as UTF8
            if self.askutf:
                utf = wx.MessageBox(_("This file contains some Unicode characters. Do you want to save it as Unicode?\n\nIf not, the Unicode characters will be replaced with question marks."), "Write++", wx.ICON_QUESTION | wx.YES_NO | wx.CANCEL)
                if utf == wx.YES:
                    self.bom = codecs.BOM_UTF8
                    self.encoding = "utf_8"
                    text = text.encode("utf_8")
                    self._frame.statusbar.SetStatusText("utf-8", 4)
                elif utf == wx.NO:
                    self.askutf = False
                else:
                    return
            if not self.askutf:
                text = text.encode(self.encoding, 'replace')
        if os.path.isfile(self.filename):
            if self._frame._app.settings["BackupType"] == 1:
                shutil.copy(self.filename, "%s.bak" % self.filename)
            elif self._frame._app.settings["BackupType"] == 2:
                bak = re.sub(r'[\\/:*?"<>|]', r'_', "%s.bak" % self.filename.replace("_", "__"))
                shutil.copy(self.filename, os.path.join(self._frame._app.settings["BackupDir"], bak))
        try:
            fileobj = open(self.filename, 'wb')
        except IOError:
            wx.MessageBox(_("Save failed. Please check that this file is not open in another program."), _("Save"), wx.ICON_EXCLAMATION | wx.OK)
            return False
        try:
            if self.bom:
                fileobj.write(self.bom)
            fileobj.write(text)
        finally:
            fileobj.close()
        if create:
            self.new = False
        self.SetSavePoint()
        self._frame.statusbar.SetStatusText(_("Saved '%s'") % os.path.split(self.filename)[1], 0)
        self.keepnonexistent = False
        self.mtime = os.path.getmtime(self.filename)
        return True

    def SaveAs(self):
        if self.new:
            filename = ""
        else:
            filename = self.filename
        dialog = wx.FileDialog(self._frame, defaultDir=os.path.dirname(self.filename), defaultFile=filename, wildcard=self._frame.filetypes, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        dialog.SetFilterIndex(1)
        if dialog.ShowModal() == wx.ID_OK:
            self.filename = dialog.GetPath()
            self.Save(True)
            self.SetLanguage()
            if not len(filename):
                self._frame.notebook.SetRenamable(self._frame.GetTab(self), True)
            self._frame.menubar.recent.AddFile(self.filename)
        dialog.Destroy()

    def Revert(self):
        revert = wx.MessageBox(_("Are you sure you want to revert '%s' to its last save point?") % self.filename, "Write++", wx.ICON_WARNING | wx.YES_NO)
        if revert == wx.YES:
            while self.changes:
                self.Undo()

    def Reload(self):
        self.Load()
        self._frame.statusbar.SetStatusText(_("Reloaded '%s'") % os.path.split(self.filename)[1], 0)
        self.UpdateStatusBar(False)

    def Run(self):
        webbrowser.open(self.filename)

encodings = {codecs.BOM_UTF8:"utf_8", codecs.BOM_UTF16:"utf_16",
             codecs.BOM_UTF16_BE:"utf_16_be", codecs.BOM_UTF16_LE:"utf_16_le",
             codecs.BOM_UTF32:"utf_32", codecs.BOM_UTF32_BE:"utf_32_be",
             codecs.BOM_UTF32_LE:"utf_32_le"}

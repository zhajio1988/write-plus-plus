"""
parent.py - parent frame class for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

import os
import wx
from lxml import etree as ElementTree
from wx.lib.agw import aui

import menu
import notebook
import panes
import search
import syntax
import toolbar

pywin32 = wx.Platform == "__WXMSW__"
if pywin32:
    try:
        import pythoncom
        from win32com.shell import shell
    except ImportError:
        pywin32 = False

_ = wx.GetTranslation
#aui.auibook.AuiTabCtrl.ShowTooltip = lambda self: None

class MainFrame(wx.Frame):
    def __init__(self, app, session=None):
        wx.Frame.__init__(self, None, -1, "Write++", app.settings["WindowPos"], app.settings["WindowSize"])
        self._app = app

        self.dragsource = -1
        self.editor = None
        self.filetypes = "|".join(filters)
        self.new = 0
        self.managers = {}
        self.panedict = {}
        self.rect = wx.Rect(app.settings["WindowPos"], app.settings["WindowSize"])
        self.results = 0
        self.search = search.SearchSystem(self)
        self.session = session
        self.styler = syntax.Styler(self)

        icons = wx.IconBundle()
        icons.AddIcon(os.path.join(app.cwd, "images", "write++-16.png"), wx.BITMAP_TYPE_PNG)
        icons.AddIcon(os.path.join(app.cwd, "images", "write++-32.png"), wx.BITMAP_TYPE_PNG)
        self.SetIcons(icons)
        if app.settings["BackupType"] == 2 and (not os.path.isdir(app.settings["BackupDir"])):
            os.makedirs(app.settings["BackupDir"])
        for direction in (wx.LEFT, wx.RIGHT, wx.TOP, wx.BOTTOM):
            self.managers[direction] = panes.VCPaneManager(self, direction)
        if not self.session:
            self.session = app.settings["SessionFile"]
        firstrun = not len(self.session)
        if not os.path.isfile(self.session):
            self.session = os.path.join(app.userdatadir, "Default.write++")

        self.aui = aui.AuiManager(self, aui.AUI_MGR_DEFAULT | aui.AUI_MGR_USE_NATIVE_MINIFRAMES)
        dockart = self.aui.GetArtProvider()
        dockart._inactive_minimize_bitmap = dockart._inactive_pin_bitmap.ConvertToImage().Rotate90().ConvertToBitmap()
        dockart.SetFont(aui.AUI_DOCKART_CAPTION_FONT, self.GetFont())

        self.menubar = menu.MenuBar(self)
        self.SetMenuBar(self.menubar)

        self.toolbar = toolbar.ToolBar(self)
        self.aui.AddPane(self.toolbar, aui.AuiPaneInfo().Name("toolbar").ToolbarPane().PaneBorder(False).Top().Row(1))

        self.statusbar = self.CreateStatusBar(6)
        self.statusbar.SetStatusWidths([-8, -2, -4, -1, -1, self.statusbar.GetTextExtent("OVR")[0] + 8])

        self.notebook = notebook.MainNotebook(self)
        self.aui.AddPane(self.notebook, aui.AuiPaneInfo().Name("notebook").CenterPane().PaneBorder(False))

        self.filebrowser = panes.FileBrowser(self)
        x, y, width, height = self.filebrowser.toolbar.GetToolRect(self.filebrowser.ID_OPTIONS)
        self.managers[wx.LEFT].AddPane(self.filebrowser, _("File Browser"), self.Bitmap("file-browser"), "filebrowser", x + width + 5)

        self.searchbar = toolbar.SearchBar(self)
        self.aui.AddPane(self.searchbar, aui.AuiPaneInfo().Name("searchbar").ToolbarPane().Gripper(False).Resizable().Bottom().Layer(0).DockFixed().Hide())

        app.plugins.OnInit(self)
        filename = os.path.join(app.userdatadir, "write++.aui")
        if os.path.isfile(filename):
            perspective = open(filename, 'r')
            self.aui.LoadPerspective(perspective.read())
            perspective.close()

        if len(app.frames) == 0 or session:
            self.LoadSession(self.session)
        else:
            self.statusbar.SetStatusText(_("untitled"), 1)
            self.session = ""
        if firstrun:
            welcome = os.path.join(app.cwd, "locale", app.locale.GetCanonicalName(), "readme.txt")
            if not os.path.isfile(welcome):
                welcome = os.path.join(app.cwd, "locale", "en_US", "readme.txt")
            self.OpenFile(welcome)
            editor = self.GetEditor()
            editor.filename = _("Welcome!")
            editor.new = True
            editor.SetReadOnly(True)
            editor.OnSavePointReached(None)
        elif not self.notebook.GetPageCount():
            self.New()
        self.GetEditor().SetFocus()

        for i in self.managers:
            if len(self.managers[i].panes):
                self.managers[i].Realize()
        self.menubar.View.Check(self.menubar.ID_TOOLBAR, self.aui.GetPane("toolbar").IsShown())
        for pane in self.panedict:
            manager = self.managers[self.panedict[pane]]
            self.menubar.View.Check(getattr(self.menubar, "ID_%s" % pane.upper()), pane in manager.visible)
        self.searchbar.SetGripperVisible(False)
        self.aui.Update()
        if app.settings["MaximizeState"]:
            self.Maximize()
            self.Layout()
        app.plugins.PostInit(self)

        self.aui.Bind(aui.EVT_AUI_PANE_BUTTON, self.OnAuiPaneButton)
        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ICONIZE, self.OnIconize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def Bitmap(self, name):
        return wx.Bitmap(os.path.join(self._app.cwd, "images", "%s.png" % name), wx.BITMAP_TYPE_PNG)

    def GetEditor(self, tab=-1):
        if tab == -1:
            tab = self.notebook.GetSelection()
        return self.notebook.GetPage(tab).editors[0]

    def GetTab(self, editor):
        return self.notebook.GetPageIndex(editor._parent)

    def HasSavedOrChanged(self):
        for i in range(self.notebook.GetPageCount()):
            editor = self.GetEditor(i)
            if not (editor.new and editor.changes == None):
                return True
        return False

    def DoAutohide(self):
        for i in self.managers:
            if len(self.managers[i].panes) and self.managers[i].autohide and self.managers[i].current != -1:
                self.managers[i].HidePane(self.managers[i].panes[self.managers[i].current])
                break

    def New(self):
        self.new += 1
        if self.new == 1:
            filename = _("untitled")
        else:
            filename = _("untitled %d") % self.new
        page = notebook.SplitterWindow(self, filename)
        self.notebook.AddPage(page, filename, True, page.editors[0].image)

    def OpenFiles(self, filenames=[], select=True, index=-1):
        if not len(filenames):
            dialog = wx.FileDialog(self, defaultDir=os.path.dirname(self.GetEditor().filename), wildcard=self.filetypes, style=wx.FD_OPEN | wx.FD_MULTIPLE)
            if dialog.ShowModal() == wx.ID_OK:
                filenames = dialog.GetPaths()
            dialog.Destroy()
            if not len(filenames):
                return
        if len(filenames) > 15:
            proceed = wx.MessageBox(_("Opening too many files at once can use an excessive amount of system resources.\nAre you sure that you want to continue?"), "Write++", wx.ICON_WARNING | wx.YES_NO | wx.NO_DEFAULT)
            if proceed != wx.YES:
                return
        if pywin32:
            for i in range(len(filenames)):
                if os.path.splitext(filenames[i])[1] == ".lnk": # Don't open a shortcut, but the file it points to
                    shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
                    shortcut.QueryInterface(pythoncom.IID_IPersistFile).Load(filenames[i])
                    filenames[i] = shortcut.GetPath(shell.SLGP_UNCPRIORITY)[0]
        filenames = self.CheckOpenFiles(filenames)
        for filename in filenames:
            if os.path.isfile(filename):
                if self.notebook.GetPageCount() == 1 and not self.HasSavedOrChanged():
                    self.GetEditor(0).OnInit(filename)
                else:
                    page = notebook.SplitterWindow(self, filename)
                    editor = page.editors[0]
                    title = os.path.split(filename)[1]
                    if editor.changes:
                        title = "*%s" % title
                    if index == -1:
                        self.notebook.AddPage(page, title, select, editor.image)
                        self.notebook.SetRenamable(self.notebook.GetPageCount() - 1, True)
                    else:
                        self.notebook.InsertPage(index, page, title, select, editor.image)
                        self.notebook.SetRenamable(index, True)
                        index += 1
                self.menubar.recent.AddFile(filename)
            elif os.path.isdir(filename):
                filenames2 = []
                for path, dirs, files in os.walk(filename, False):
                    filenames2 += [os.path.join(path, filename2) for filename2 in files]
                self.OpenFiles(filenames2, select, index)
            else:
                create = wx.MessageBox(_("'%s' does not exist.\nWould you like to create it?") % filename, "Write++", wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
                if create == wx.YES:
                    open(filename, 'w').close()
                    self.OpenFile(filename, select, index)
                elif filename in self._app.settings["RecentFiles"]:
                    self.menubar.recent.RemoveFile(filename)

    def OpenFile(self, filename, select=True, index=-1):
        self.OpenFiles([filename], select, index)

    def CheckOpenFiles(self, filenames, switch=True):
        for frame in self._app.frames:
            for i in range(frame.notebook.GetPageCount()):
                editor = frame.GetEditor(i)
                if editor.filename in filenames:
                    if switch:
                        self._app.ShowFrame(frame)
                        frame.notebook.SetSelection(i)
                        wx.CallAfter(editor.SetFocus)
                    filenames.remove(editor.filename)
        return filenames

    def SaveAll(self):
        for i in range(self.notebook.GetPageCount()):
            editor = self.GetEditor(i)
            if editor.changes:
                editor.Save()

    def LoadSession(self, filename=None):
        if not filename:
            dialog = wx.FileDialog(self, _("Load Session"), os.path.dirname(self.session), wildcard=_("Write++ Sessions (*.write++)|*.write++"), style=wx.FD_OPEN)
            if dialog.ShowModal() == wx.ID_OK:
                filename = dialog.GetPath()
            dialog.Destroy()
            if not filename:
                return
        if os.path.isfile(filename):
            root = ElementTree.parse(filename).getroot()
            filenames = self.CheckOpenFiles([element.text for element in root if os.path.isfile(element.text)], False)
            tab = int(root.get("tab"))
            if tab >= len(filenames):
                tab = len(filenames) - 1
            i = 0
            for element in root:
                if element.text not in filenames:
                    continue
                if i < self.notebook.GetPageCount():
                    editor = self.GetEditor(i)
                    editor.OnInit(element.text)
                else:
                    page = notebook.SplitterWindow(self, element.text)
                    editor = page.editors[0]
                    title = os.path.split(editor.filename)[1]
                    if editor.changes:
                        title = "*%s" % title
                    self.notebook.AddPage(page, title, i == tab, editor.image)
                self.notebook.SetRenamable(i, True)
                editor.EnsureVisible(int(element.get("firstvisibleline")) - 1)
                editor.GotoPos(int(element.get("currentposition")))
                editor.SetSelectionStart(int(element.get("selectionstart")))
                editor.SetSelectionEnd(int(element.get("selectionend")))
                i += 1
            while self.notebook.GetPageCount() > len(filenames):
                self.notebook.GetPage(i).Close()
                i -= 1
        self.SetStatusText(os.path.split(filename)[1][:-8], 1)
        self.session = filename

    def SaveSession(self, filename=None):
        if not filename:
            dialog = wx.FileDialog(self, _("Save Session"), os.path.dirname(self.session), os.path.split(self.session)[1], _("Write++ Sessions (*.write++)|*.write++"), wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if dialog.ShowModal() == wx.ID_OK:
                filename = dialog.GetPath()
            dialog.Destroy()
            if not filename:
                return
        root = ElementTree.Element("session", tab=str(self.notebook.GetSelection()))
        for i in range(self.notebook.GetPageCount()):
            page = self.notebook.GetPage(i)
            editor = page.editors[page.focused]
            element = ElementTree.SubElement(root, "file",
                                       firstvisibleline=str(editor.GetFirstVisibleLine() + 1), currentposition=str(editor.GetCurrentPos()),
                                       selectionstart=str(editor.GetSelectionStart()), selectionend=str(editor.GetSelectionEnd()))
            element.text = page.editors[0].filename
        session = open(filename, 'w')
        session.write(ElementTree.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True).decode("utf-8"))
        session.close()
        if filename != self.session:
            self.SetStatusText(os.path.split(filename)[1][:-8], 1)
            self.session = filename

    def Cut(self):
        self.editor.Cut()
        wx.TheClipboard.Flush()

    def Copy(self):
        self.editor.Copy()
        wx.TheClipboard.Flush()

    def ChooseLanguage(self):
        language = syntax.ChooseLanguage(self)
        if language:
            self.GetEditor().SetLanguage(language)

    def ShowToolbar(self, show=True):
        self.aui.GetPane("toolbar").Show(show)
        self.aui.Update()

    def ShowFileBrowser(self, show=True):
        self.managers[self.panedict["filebrowser"]].ShowPane2("filebrowser", show)
        if show:
            self.filebrowser.GetSizer().Layout()    # Adjust overflow state of file browser toolbar
            wx.CallAfter(self.filebrowser.dirctrl.SetFocus)

    def Plugins(self):
        import plugins
        dialog = plugins.PluginDialog(self)
        dialog.Show()

    def StyleEditor(self):
        dialog = syntax.StyleEditor(self)
        dialog.Show()

    def Preferences(self):
        from dialogs import preferences
        dialog = preferences.PreferenceDialog(self)
        dialog.Show()

    def OnAuiPaneButton(self, event):
        name = event.pane.name
        if event.button in (aui.AUI_BUTTON_CLOSE, aui.AUI_BUTTON_PIN, aui.AUI_BUTTON_MINIMIZE):
            self.managers[self.panedict[name]].HidePane(name, event.button)
        else:
            self.aui.OnPaneButton(event)

    def OnActivate(self, event):
        if event.GetActive():
            tab = 0
            while tab < self.notebook.GetPageCount():
                editor = self.GetEditor(tab)
                if not editor.new:
                    if os.path.exists(editor.filename):
                        mtime = os.path.getmtime(editor.filename)
                        if mtime != editor.mtime:
                            if self.notebook.GetSelection() != tab:
                                self.notebook.SetSelection(tab)
                            editor.mtime = mtime
                            load = wx.MessageBox(_("'%s' has been modified by another program.\nDo you want to reload this file?") % editor.filename, "Write++", wx.ICON_WARNING | wx.YES_NO)
                            if load == wx.YES:
                                editor.Reload()
                        readonly = not os.access(editor.filename, os.W_OK)
                        if readonly != editor.readonly:
                            editor.SetReadOnly(readonly)
                            editor.readonly = readonly
                    elif not editor.keepnonexistent:
                        if self.notebook.GetSelection() != tab:
                            self.notebook.SetSelection(tab)
                        editor.keepnonexistent = True
                        keep = wx.MessageBox(_("'%s' has been moved, renamed, or deleted.\nDo you want to keep this file in the editor?") % editor.filename, "Write++", wx.ICON_WARNING | wx.YES_NO)
                        if keep == wx.YES:
                            editor.OnSavePointLeft(None)
                        elif keep == wx.NO:
                            editor._parent.Close()
                            continue
                tab += 1
            self._app.active = self._app.frames.index(self)
        #elif hasattr(self.notebook, "GetPageCount") and self.notebook.GetPageCount() > 0:   # Ignore this event if frame is going to be closed
        #    for editor in self.notebook.GetCurrentPage().editors:
        #        editor.Cancel()
        event.Skip()

    def OnMove(self, event):
        if self.HasCapture():
            self.rect.SetPosition(self.GetPosition())
        event.Skip()

    def OnSize(self, event):
        if self.aui.GetPane("filebrowser").IsShown():   # Adjust overflow state of file browser toolbar if visible
            wx.CallAfter(self.filebrowser.GetSizer().Layout)
        if self.HasCapture():
            self.rect = wx.RectPS(self.GetPosition(), self.GetSize())
        event.Skip()

    def OnIconize(self, event):
        if self._app.settings["MinimizeToTray"] and event.Iconized() and not hasattr(self, "trayicon"):
            self.trayicon = menu.TaskBarIcon(self)
            self.Hide()
        event.Skip()

    def OnClose(self, event):
        for i in range(self.notebook.GetPageCount()):
            editor = self.GetEditor(i)
            if editor.changes:
                save = wx.MessageBox(_("Don't you want to save your changes to '%s'?") % editor.filename, "Write++", wx.ICON_WARNING | wx.YES_NO | wx.CANCEL)
                if save == wx.YES:
                    saved = editor.Save()
                    if not saved:
                        return
                elif save == wx.NO:
                    editor.changes = None   # Do this so that the next check will work properly
                else:
                    return
        if self.HasSavedOrChanged():
            if len(self._app.frames) > 1 and (not len(self.session)):
                for i in range(self.notebook.GetPageCount()):
                    editor = self.GetEditor(i)
                    if not editor.new:
                        self.menubar.recent.AddFile(editor.filename)
            else:
                self.SaveSession(self.session)
        for plugin in self._app.plugins.plugins:
            if hasattr(plugin, "OnCloseFrame"):
                plugin.OnCloseFrame(self)
        self._app.UnInit()
        perspective = open(os.path.join(self._app.userdatadir, "write++.aui"), 'w')
        self.DoAutohide()
        perspective.write(self.aui.SavePerspective())
        perspective.close()
        self.aui.UnInit()
        self._app.CloseFrame(self)


filters = [_(string) for string in ("All Files (*.*)|*.*", "Plain Text (*.txt)|*.txt",
    "Flash ActionScript (*.as;*.mx)|*.as;*.mx",
    "Ada (*.ada;*.ads;*.adb)|*.ada;*.ads;*.adb",
    "Assembly Language Source (*.asm)|*.asm",
    "AutoIt (*.au3)|*.au3",
    "Bash Shell Script (*.bsh;*.sh)|*.bsh;*.sh",
    "Batch (*.bat;*.cmd;*.nt)|*.bat;*.cmd;*.nt",
    "C Source (*.c)|*.c",
    "CAML (*.ml;*.mli;*.sml;*.thy)|*.ml;*.mli;*.sml;*.thy",
    "CMake (*.cmake)|*.cmake",
    "C++ Source (*.h;*.hpp;*.hxx;*.cpp;*.cxx;*.cc)|*.h;*.hpp;*.hxx;*.cpp;*.cxx;*.cc",
    "C# Source (*.cs)|*.cs", "C-Shell Script (*.csh)|*.csh",
    "Cascading Style Sheet (*.css)|*.css",
    "D programming language (*.d)|*.d",
    "Diff (*.diff;*.patch)|*.diff;*.patch",
    "Fortran Source (*.f;*.for;*.f90;*.f95;*.f2k)|*.f;*.for;*.f90;*.f95;*.f2k",
    "Haskell (*.hs;*.lhs;*.as;*.las)|*.hs;*.lhs;*.as;*.las",
    "HTML (*.html;*.htm;*.shtml;*.shtm;*.xhtml;*.hta)|*.html;*.htm;*.shtml;*.shtm;*.xhtml;*.hta",
    "Microsoft INI (*.ini;*.inf;*.reg;*.url)|*.ini;*.inf;*.reg;*.url",
    "Inno Setup Script (*.iss)|*.iss",
    "Java Source (*.java)|*.java", "JavaScript (*.js)|*.js",
    "KiXtart Script (*.kix)|*.kix",
    "Korn Shell Script (*.ksh)|*.ksh", "LaTeX (*.tex)|*.tex",
    "Lisp (*.lsp;*.lisp)|*.lsp;*.lisp", "Lua (*.lua)|*.lua",
    "Make (*.mak)|*.mak", "MatLab (*.m)|*.m",
    "NSIS Script (*.nsi;*.nsh)|*.nsi;*.nsh",
    "Pascal (*.pas;*.inc)|*.pas;*.inc",
    "Perl (*.pl;*.pm;*.plx)|*.pl;*.pm;*.plx",
    "PHP (*.php;*.php3;*.phtml)|*.php;*.php3;*.phtml",
    "Postscript (*.ps)|*.ps", "Windows PowerShell (*.ps1)|*.ps1",
    "Properties (*.properties)|*.properties",
    "Python (*.py;*.pyw)|*.py;*.pyw",
    "Ruby (*.rb;*.rbw)|*.rb;*.rbw", "SQL (*.sql)|*.sql",
    "Smalltalk (*.st)|*.st",
    "Visual Basic (*.vb;*.vbs)|*.vb;*.vbs", "Verilog (*.v)|*.v",
    "VHDL (*.vhd;*.vhdl)|*.vhd;*.vhdl",
    "XML (*.xml;*.xsml;*.xsl;*.xsd;*.kml;*.wsdl)|*.xml;*.xsml;*.xsl;*.xsd;*.kml;*.wsdl",
    "YAML (*.yml)|*.yml")]

"""
preferences.py - preference dialog class for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

import os.path
import wx
from wx.lib.agw.aui import AUI_NB_TAB_FIXED_WIDTH

_ = wx.GetTranslation

class PreferenceDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, _("Preferences"), size=(600, 440))
        self._parent = parent

        self.treebook = wx.Treebook(self, -1)

        self.general = wx.Panel(self.treebook, -1)
        self.MinimizeToTray = wx.CheckBox(self.general, -1, _("Minimize to system tray"))
        self.MinimizeToTray.SetValue(parent._app.settings["MinimizeToTray"])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.MinimizeToTray, 0, wx.ALL, 2)
        self.general.SetSizer(sizer)
        self.treebook.AddPage(self.general, _("General"))

        self.editor = wx.Panel(self.treebook, -1)
        if wx.VERSION_STRING >= "2.9.1.0":
            box = wx.StaticBox(self.editor, -1, _("Backup"))
        else:
            box = self.editor
        self.BackupType = wx.CheckBox(box, -1, _("Backup files before saving them"))
        self.BackupType.SetValue(parent._app.settings["BackupType"] > 0)
        self.BackupType.Bind(wx.EVT_CHECKBOX, self.OnBackupType)
        self.BackupType2 = wx.CheckBox(box, -1, _("Use custom backup directory"))
        self.BackupType2.Enable(parent._app.settings["BackupType"] > 0)
        self.BackupType2.SetValue(parent._app.settings["BackupType"] == 2)
        self.BackupType2.Bind(wx.EVT_CHECKBOX, self.OnBackupType2)
        self.BackupDir = wx.DirPickerCtrl(box, -1, parent._app.settings["BackupDir"], style=wx.DIRP_DEFAULT_STYLE ^ wx.DIRP_DIR_MUST_EXIST)
        self.BackupDir.Enable(parent._app.settings["BackupType"] == 2)
        self.BackupDir.GetChildren()[0].Bind(wx.EVT_KILL_FOCUS, self.OnBackupDirKillFocus)
        sizer = wx.BoxSizer(wx.VERTICAL)
        if wx.VERSION_STRING < "2.9.1.0":
            box = wx.StaticBox(self.editor, -1, _("Backup"))
        sizer2 = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer2.Add(self.BackupType, 0, wx.ALL, 2)
        sizer2.Add(self.BackupType2, 0, wx.ALL, 2)
        sizer2.Add(self.BackupDir, 0, wx.ALL | wx.EXPAND, 2)
        sizer.Add(sizer2, 0, wx.ALL | wx.EXPAND, 2)
        self.editor.SetSizer(sizer)
        self.treebook.AddPage(self.editor, _("Editor"))

        self.appearance = wx.Panel(self.treebook, -1)
        self.FixedTabWidth = wx.CheckBox(self.appearance, -1, _("Make all tabs the same width"))
        self.FixedTabWidth.SetValue(parent._app.settings["FixedTabWidth"])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.FixedTabWidth, 0, wx.ALL, 2)
        self.appearance.SetSizer(sizer)
        self.treebook.AddPage(self.appearance, _("Appearance"))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.treebook, 1, wx.ALL | wx.EXPAND, 2)
        statictext = wx.StaticText(self, -1, _("*Takes effect after you restart Write++"))
        statictext.SetForegroundColour("#808080")
        sizer.Add(statictext, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        sizer2 = wx.StdDialogButtonSizer()
        sizer2.AddButton(wx.Button(self, wx.ID_OK))
        sizer2.AddButton(wx.Button(self, wx.ID_CANCEL))
        sizer2.AddButton(wx.Button(self, wx.ID_APPLY))
        sizer2.Realize()
        sizer.Add(sizer2, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.OnApply, id=wx.ID_APPLY)

    def OnBackupType(self, event):
        self.BackupType2.Enable(event.IsChecked())

    def OnBackupType2(self, event):
        self.BackupDir.Enable(event.IsChecked())

    def OnBackupDirKillFocus(self, event):
        backupdir = self.BackupDir.GetPath()
        if not os.path.isdir(backupdir):
            wx.MessageBox(_("'%s' is not a valid directory.") % backupdir, "Write++", wx.ICON_EXCLAMATION | wx.OK)
            wx.CallAfter(self.treebook.SetSelection, 1)
        event.Skip()

    def OnOk(self, event):
        self.OnApply(event)
        self.Destroy()

    def OnCancel(self, event):
        self.Destroy()

    def OnApply(self, event):
        self._parent._app.settings["MinimizeToTray"] = self.MinimizeToTray.GetValue()
        if not self.BackupType.GetValue():
            self._parent._app.settings["BackupType"] = 0
        elif not self.BackupType2.GetValue():
            self._parent._app.settings["BackupType"] = 1
        else:
            self._parent._app.settings["BackupType"] = 2
        backupdir = self.BackupDir.GetPath()
        if os.path.isdir(backupdir):
            self._parent._app.settings["BackupDir"] = backupdir
        FixedTabWidth = self.FixedTabWidth.GetValue()
        if FixedTabWidth:
            self._parent.notebook.SetAGWWindowStyleFlag(self._parent.notebook.GetAGWWindowStyleFlag() | AUI_NB_TAB_FIXED_WIDTH)
        else:
            self._parent.notebook.SetAGWWindowStyleFlag(self._parent.notebook.GetAGWWindowStyleFlag() ^ AUI_NB_TAB_FIXED_WIDTH)
        self._parent._app.settings["FixedTabWidth"] = FixedTabWidth

"""
toolbar.py - toolbar classes for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
NOTE: Parts of this file are based on code from Editra
"""

import os.path
import sys
import wx
from wx.lib.agw import aui

import menu

_ = wx.GetTranslation

class ToolBar(aui.AuiToolBar):
	def __init__(self, parent):
		super(ToolBar, self).__init__(parent, -1, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
		self._parent = parent
		
		self.AddSimpleTool(wx.ID_NEW, "", parent.Bitmap("new"), _("New (Ctrl+N)"))
		self.AddSimpleTool(wx.ID_OPEN, "", parent.Bitmap("open"), _("Open (Ctrl+O)"))
		self.Bind(aui.EVT_AUITOOLBAR_RIGHT_CLICK, self.OnOpenRecent, id=wx.ID_OPEN)
		self.AddSimpleTool(wx.ID_SAVE, "", parent.Bitmap("save"), _("Save (Ctrl+S)"))
		self.AddSimpleTool(parent.menubar.ID_SAVEALL, "", parent.Bitmap("save-all"), _("Save All (Ctrl+Alt+S)"))
		self.AddSimpleTool(wx.ID_PRINT, "", parent.Bitmap("print"), _("Print (Ctrl+P)"))
		self.AddSeparator()
		self.AddSimpleTool(wx.ID_UNDO, "", parent.Bitmap("undo"), _("Undo (Ctrl+Z)"))
		self.AddSimpleTool(wx.ID_REDO, "", parent.Bitmap("redo"), _("Redo (Ctrl+Y)"))
		self.AddSeparator()
		self.AddSimpleTool(wx.ID_CUT, "", parent.Bitmap("cut"), _("Cut (Ctrl+X)"))
		self.AddSimpleTool(wx.ID_COPY, "", parent.Bitmap("copy"), _("Copy (Ctrl+C)"))
		self.AddSimpleTool(wx.ID_PASTE, "", parent.Bitmap("paste"), _("Paste (Ctrl+V)"))
		self.AddSeparator()
		self.AddSimpleTool(wx.ID_FIND, "", parent.Bitmap("find"), _("Find (Ctrl+F)"))
		self.AddSimpleTool(wx.ID_REPLACE, "", parent.Bitmap("replace"), _("Replace (Ctrl+H)"))
		self.AddSeparator()
		self.AddSimpleTool(wx.ID_ZOOM_IN, "", parent.Bitmap("zoom-in"), _("Zoom In (Ctrl++)"))
		self.AddSimpleTool(wx.ID_ZOOM_OUT, "", parent.Bitmap("zoom-out"), _("Zoom Out (Ctrl+-)"))
		
		self.EnableTool(wx.ID_SAVE, False)
		self.EnableTool(parent.menubar.ID_SAVEALL, False)
		self.Realize()
	
	def GetPopupPos(self, toolbar, id):
		if toolbar.GetToolFits(id):
			x, y, width, height = toolbar.GetToolRect(id)
			return (x, y + height)
		else:
			x, y = toolbar.GetPosition()
			width, height = toolbar.GetSize()
			return (x + width - 16, y + height)
	
	def OnOpenRecent(self, event):
		self.PopupMenu(menu.FileHistory(self._parent, self._parent._app.settings["RecentFiles"]), self.GetPopupPos(self, wx.ID_OPEN))

class SearchBar(aui.AuiToolBar):
	def __init__(self, parent):
		super(SearchBar, self).__init__(parent, -1, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW | aui.AUI_TB_PLAIN_BACKGROUND | aui.AUI_TB_HORZ_TEXT)
		self._parent = parent
		
		self.images = {"info":parent.Bitmap("info"), "wrapped":parent.Bitmap("wrapped")}
		self.lastsearch = None
		self.timer = wx.Timer()
		
		self.AddSimpleTool(wx.ID_CLOSE, "", parent.aui.GetArtProvider()._inactive_close_bitmap, _("Close"))
		self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_CLOSE)
		self.find = wx.SearchCtrl(self, -1, parent._app.settings["QuickFind"], size=(220, -1), style=wx.TE_PROCESS_ENTER)
		self.find.SetDescriptiveText(_("Find..."))
		self.find.GetChildren()[0].SetAcceleratorTable(wx.AcceleratorTable([(wx.ACCEL_CTRL, ord("A"), wx.ID_SELECTALL)]))
		self.AddControl(self.find)
		self.find.Bind(wx.EVT_TEXT, self.OnText)
		self.find.Bind(wx.EVT_TEXT_ENTER, self.OnNext)
		self.find.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancelBtn)
		self.AddSimpleTool(wx.ID_FORWARD, _("Next"), parent.Bitmap("next"), _("Find Next (F3)"))
		self.Bind(wx.EVT_MENU, self.OnNext, id=wx.ID_FORWARD)
		self.AddSimpleTool(wx.ID_BACKWARD, _("Previous"), parent.Bitmap("previous"), _("Find Previous (Shift+F3)"))
		self.Bind(wx.EVT_MENU, self.OnPrevious, id=wx.ID_BACKWARD)
		self.ID_ADVANCED = wx.NewId()
		self.AddSimpleTool(self.ID_ADVANCED, "", parent.Bitmap("find-in-files"), _("Advanced Find (Ctrl+Shift+F)"))
		self.Bind(wx.EVT_MENU, self.OnAdvanced, id=self.ID_ADVANCED)
		self.AddSeparator()
		self.wholeword = wx.CheckBox(self, -1, _("Whole Word"))
		self.AddControl(self.wholeword)
		self.matchcase = wx.CheckBox(self, -1, _("Case Sensitive"))
		self.AddControl(self.matchcase)
		self.AddSpacer(10)
		self.bitmap = wx.StaticBitmap(self, -1, wx.NullBitmap)
		self.AddControl(self.bitmap)
		self.AddSpacer(2)
		self.ID_STATUS = wx.NewId()
		self.AddLabel(self.ID_STATUS, "")
		
		self.Realize()
		self.bitmap.Hide()
		self.UpdateUI()
		
		self.timer.Bind(wx.EVT_TIMER, self.OnTimer)
	
	def Search(self, forward=True, automatic=False):
		query = self.find.GetValue()
		if not len(query):
			return
		old = self._parent.editor.GetCurrentPos()
		if forward and not automatic:
			self._parent.editor.SetCurrentPos(self._parent.editor.GetSelectionEnd())
		else:
			self._parent.editor.SetCurrentPos(self._parent.editor.GetSelectionStart())
		self._parent.editor.SearchAnchor()
		flags = 0
		if self.wholeword.GetValue():
			flags |= wx.FR_WHOLEWORD
		if self.matchcase.GetValue():
			flags |= wx.FR_MATCHCASE
		wrapped = False
		info = (query, self._parent.GetEditor().filename)
		if forward:
			pos = self._parent.editor.SearchNext(flags, query)
			if pos == -1:
				self._parent.editor.SetCurrentPos(0)
				self._parent.editor.SearchAnchor()
				pos = self._parent.editor.SearchNext(flags, query)
				wrapped = info == self.lastsearch
		else:
			pos = self._parent.editor.SearchPrev(flags, query)
			if pos == -1:
				self._parent.editor.SetCurrentPos(self._parent.editor.GetTextLength())
				self._parent.editor.SearchAnchor()
				pos = self._parent.editor.SearchPrev(flags, query)
				wrapped = info == self.lastsearch
		if pos != -1:
			self._parent.editor.EnsureVisible(self._parent.editor.LineFromPosition(pos))
			self._parent.editor.EnsureCaretVisible()
			if wrapped:
				self.bitmap.SetBitmap(self.images["wrapped"])
				self.bitmap.Show()
				self.FindTool(self.ID_STATUS).SetLabel(_("Wrapped around"))
				self._parent.statusbar.SetStatusText(_("Wrapped around"), 0)
			else:
				self.bitmap.Hide()
				self.FindTool(self.ID_STATUS).SetLabel("")
				self._parent.statusbar.SetStatusText(_("Found '%s'") % query, 0)
			self.lastsearch = info
		else:
			wx.Bell()
			self._parent.editor.SetCurrentPos(old)
			self.bitmap.SetBitmap(self.images["info"])
			self.bitmap.Show()
			self.FindTool(self.ID_STATUS).SetLabel(_("Not found"))
			self._parent.statusbar.SetStatusText(_("'%s' not found") % query, 0)
		self.Refresh(False)
		self._parent.search.pattern = None
	
	def UpdateUI(self):
		full = not self.find.IsEmpty()
		self.find.ShowCancelButton(full)
		self.EnableTool(wx.ID_BACKWARD, full)
		self.EnableTool(wx.ID_FORWARD, full)
		self.Refresh(False)
		self._parent.menubar.Enable(self._parent.menubar.ID_FIND_NEXT, full or bool(self._parent.search.pattern))
		self._parent.menubar.Enable(self._parent.menubar.ID_FIND_PREVIOUS, full or bool(self._parent.search.pattern))
	
	def OnClose(self, event):
		self._parent.aui.GetPane("searchbar").Show(False)
		self._parent.aui.Update()
		wx.CallAfter(self._parent.editor.SetFocus)
	
	def OnText(self, event):
		self.UpdateUI()
		self.timer.Start(500, wx.TIMER_ONE_SHOT)
	
	def OnCancelBtn(self, event):
		self.find.ChangeValue("")	# Avoid generating an EVT_TEXT event
		self.UpdateUI()
	
	def OnNext(self, event):
		self.timer.Stop()
		self.Search(True)
	
	def OnPrevious(self, event):
		self.timer.Stop()
		self.Search(False)
	
	def OnAdvanced(self, event):
		self._parent.search.ShowSearchDialog()
	
	def OnTimer(self, event):
		self.timer.Stop()
		self.Search(automatic=True)
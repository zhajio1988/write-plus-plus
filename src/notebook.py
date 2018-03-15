"""
notebook.py - notebook and splitter window classes for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

import os
import wx

import aui
import stc

_ = wx.GetTranslation

class MainNotebook(aui.AuiNotebook):
	def __init__(self, parent):
		style = (aui.AUI_NB_DEFAULT_STYLE ^ aui.AUI_NB_CLOSE_ON_ACTIVE_TAB) | aui.AUI_NB_TAB_EXTERNAL_MOVE | aui.AUI_NB_WINDOWLIST_BUTTON | aui.AUI_NB_CLOSE_ON_ALL_TABS | aui.AUI_NB_SMART_TABS | aui.AUI_NB_USE_IMAGES_DROPDOWN | aui.AUI_NB_TAB_FLOAT | aui.AUI_NB_ORDER_BY_ACCESS
		if parent._app.settings["FixedTabWidth"]:
			style |= aui.AUI_NB_TAB_FIXED_WIDTH
		if wx.Platform == "__WXMAC__":
			style |= aui.AUI_NB_CLOSE_ON_TAB_LEFT
		super(MainNotebook, self).__init__(parent, -1, agwStyle=style)
		self._parent = parent
		
		self.droptarget = False
		self.tooltip = None
		
		self.SetNavigatorIcon(parent.Bitmap("write++-16"))
		self.SetSashDClickUnsplit(True)
		
		tabctrl = self.GetActiveTabCtrl()
		tabctrl.SetDropTarget(NotebookDropTarget(parent))
		tabctrl.Bind(wx.EVT_MOTION, self.OnTabCtrlMotion)
		self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)
		self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
		self.Bind(aui.EVT_AUINOTEBOOK_ALLOW_DND, self.OnAllowDnD)
		self.Bind(aui.EVT_AUINOTEBOOK_DRAG_DONE, self.OnDragDone)
		self.Bind(aui.EVT_AUINOTEBOOK_TAB_RIGHT_UP, self.OnTabRightUp)
		self.Bind(aui.EVT_AUINOTEBOOK_BG_DCLICK, self.OnBgDClick)
		self.Bind(aui.EVT_AUINOTEBOOK_END_LABEL_EDIT, self.OnEndLabelEdit)
	
	def OnTabCtrlMotion(self, event):
		tabctrl = event.GetEventObject()
		tabctrl.OnMotion(event)
		x, y = event.GetX(), event.GetY()
		hide = False
		if not event.LeftDown():
			page = tabctrl.TabHitTest(x, y)
			if not page:
				hide = True
			elif self.tooltip != page.editors[0].filename:
				self.tooltip = page.editors[0].filename
				tabctrl.SetToolTipString(self.tooltip)
		elif self.tooltip:
			hide = True
		if hide:
			self.tooltip = None
			tabctrl.SetToolTipString("")
		event.Skip()
	
	def OnPageClose(self, event):
		editor = self._parent.GetEditor()
		if not (self.GetPageCount() == 1 and editor.new and editor.changes == None):
			self.GetPage(event.GetSelection()).Close()
		event.Veto()
	
	def OnPageChanged(self, event):
		selection = event.GetSelection()
		page = self.GetPage(selection)
		editor = page.editors[page.focused]
		self._parent.toolbar.EnableTool(wx.ID_SAVE, editor.changes != False)
		self._parent.toolbar.Refresh(False)
		if self._parent._app.settings["UpdatePath"]:
			path = self._parent.filebrowser.dirpicker.GetPath()
			filename = self._parent.GetEditor(selection).filename
			if path != os.path.split(filename)[0]:
				self._parent.filebrowser.dirctrl.CollapsePath(path)
			##if wx.VERSION_STRING >= "2.9.0":
			##	self._parent.filebrowser.dirctrl.UnselectAll()
			self._parent.filebrowser.dirctrl.SetPath(filename)
		self._parent.menubar.Enable(wx.ID_SAVE, editor.changes != False)
		self._parent.menubar.Enable(wx.ID_REVERT, editor.changes != False)
		self._parent.menubar.Enable(wx.ID_REFRESH, not editor.new)
		if not page.IsSplit():
			self._parent.menubar.Check(self._parent.menubar.ID_HIDE_2ND, True)
		elif page.GetSplitMode() == wx.SPLIT_VERTICAL:
			self._parent.menubar.Check(self._parent.menubar.ID_SPLIT_V, True)
		else:
			self._parent.menubar.Check(self._parent.menubar.ID_SPLIT_H, True)
		wx.CallAfter(page.editors[page.focused].SetFocus)
		wx.CallAfter(self._parent.DoAutohide)
	
	def OnAllowDnD(self, event):
		source = event.GetDragSource()
		for frame in self._parent._app.frames:
			if frame.notebook == source:
				self.droptarget = True
				event.Allow()
				return
	
	def OnDragDone(self, event):
		if self.droptarget:
			page = self.GetCurrentPage()
			page._parent = self._parent
			for editor in page.editors:
				editor._frame = self._parent
			self.GetPage(event.GetSelection()).editors[page.focused].SetFocus()	 # GetCurrentPage doesn't work here
			self.droptarget = False
		elif self.GetPageCount() == 0:
			self._parent._app.CloseFrame(self._parent)
		else:
			tabctrl = self.GetActiveTabCtrl()
			tabctrl.SetDropTarget(NotebookDropTarget(self._parent))
			tabctrl.Bind(wx.EVT_MOTION, self.OnTabCtrlMotion)
	
	def OnBgDClick(self, event):
		self._parent.New()
	
	def OnTabRightUp(self, event):
		self.context = event.GetSelection()
		menu = wx.Menu()
		menu.Append(wx.ID_CLOSE, _("&Close Tab\tCtrl+W"))
		ID_CLOSE_OTHERS = wx.NewId()
		menu.Append(ID_CLOSE_OTHERS, _("Close &Others"))
		self._parent.Bind(wx.EVT_MENU, self.OnCloseOthers, id=ID_CLOSE_OTHERS)
		ID_CLOSE_LEFT = wx.NewId()
		menu.Append(ID_CLOSE_LEFT, _("Close Tabs to the &Left"))
		self._parent.Bind(wx.EVT_MENU, self.OnCloseLeft, id=ID_CLOSE_LEFT)
		ID_CLOSE_RIGHT = wx.NewId()
		menu.Append(ID_CLOSE_RIGHT, _("Close Tabs to the &Right"))
		self._parent.Bind(wx.EVT_MENU, self.OnCloseRight, id=ID_CLOSE_RIGHT)
		count = self.GetPageCount()
		if count == 1:	# Only one tab
			for id in (wx.ID_CLOSE, ID_CLOSE_OTHERS, ID_CLOSE_LEFT, ID_CLOSE_RIGHT):
				menu.Enable(id, False)
		elif self.context == 0:	# Left-most tab
			menu.Enable(ID_CLOSE_LEFT, False)
		elif self.context == count - 1:	 # Right-most tab
			menu.Enable(ID_CLOSE_RIGHT, False)
		menu.AppendSeparator()
		menu.Append(wx.ID_SAVE, _("&Save\tCtrl+S"))
		editor = self._parent.GetEditor(self.context)
		menu.Enable(wx.ID_SAVE, editor.changes != False)
		menu.Append(wx.ID_REFRESH, _("Re&load\tShift+F5"))
		menu.Enable(wx.ID_REFRESH, not editor.new)
		menu.AppendSeparator()
		menu.Append(wx.ID_NEW, _("&New\tCtrl+N"))
		ID_RENAME = wx.NewId()
		menu.Append(ID_RENAME, _("&Rename"))
		menu.Enable(ID_RENAME, self.IsRenamable(self.context))
		self._parent.Bind(wx.EVT_MENU, self.OnRename, id=ID_RENAME)
		self.PopupMenu(menu)
	
	def OnCloseOthers(self, event):
		self.OnCloseLeft(event)
		self.context = 0
		self.OnCloseRight(event)
	
	def OnCloseLeft(self, event):
		for i in range(self.context):
			self.GetPage(i).Close()
	
	def OnCloseRight(self, event):
		count = self.GetPageCount()
		for i in range(self.context + 1, count - 1):
			self.GetPage(self.context + 1).Close()
		wx.CallAfter(self.GetPage(self.context + 1).Close)	# TODO3: Why is CallAfter needed to close last notebook page?
	
	def OnRename(self, event):
		wx.CallAfter(self.EditTab, self.context)
	
	def OnEndLabelEdit(self, event):
		filename = event.GetLabel().lstrip("*")
		if len(filename):
			editor = self._parent.GetEditor()
			split = os.path.split(editor.filename)
			new = os.path.join(split[0], filename)
			if new != editor.filename:
				os.rename(editor.filename, new)
				self._parent.menubar.recent.RenameFile(editor.filename, new)
				editor.filename = new
				editor.SetLanguage()
				editor.RefreshTitleBar()
				self._parent.statusbar.SetStatusText(_("Renamed '%s' to '%s'") % (split[1], filename), 0)
		wx.CallAfter(self._parent.editor.SetFocus)

class NotebookDropTarget(wx.DropTarget):
	def __init__(self, frame):
		wx.DropTarget.__init__(self)
		self._frame = frame
		
		self.source = -1
		self.tab = -1
		self.timer = wx.Timer()
		
		self.data = wx.DataObjectComposite()
		self.filenames = wx.FileDataObject()
		self.data.Add(self.filenames)
		self.text = wx.TextDataObject()
		self.data.Add(self.text)
		self.SetDataObject(self.data)
		
		self.timer.Bind(wx.EVT_TIMER, self.OnTimer)
	
	def OnEnter(self, x, y, default):
		if self.source == -1:
			self.source = self._frame.notebook.GetSelection()
		return default
	
	def OnLeave(self):
		self.timer.Stop()
	
	def OnDragOver(self, x, y, default):
		self.GetData()
		if self.text.GetTextLength() > 1:
			page = self._frame.notebook.GetActiveTabCtrl().TabHitTest(x, y)
			if not page:
				return wx.DragNone
			tab = self._frame.GetTab(page.editors[0])
			if tab == -1 or (tab == self._frame.notebook.GetSelection() and tab == self.source):
				return wx.DragCancel
			if tab != self.tab:
				self.timer.Start(500, wx.TIMER_ONE_SHOT)
			self.tab = tab
			return stc.alternate[default]
		elif len(self.filenames.GetFilenames()):
			return wx.DragCopy
		return default
	
	def OnData(self, x, y, default):
		self.GetData()
		self.source = -1
		wx.CallAfter(setattr, self, "tab", -1)
		if self.text.GetTextLength() > 1:
			page = self._frame.notebook.GetCurrentPage()
			page.editors[page.focused].AddText(self.text.GetText())
			self.text.SetText("")
			return stc.alternate[default]
		else:
			self._frame.OpenFiles(filenames, index=self.tab)
		return default
	
	def OnTimer(self, event):
		if self._frame.notebook.GetSelection() != self.tab:
			self._frame.notebook.SetSelection(self.tab)

class SplitterWindow(wx.SplitterWindow):
	def __init__(self, parent, filename):
		wx.SplitterWindow.__init__(self, parent, -1, style=wx.SP_3DSASH | wx.SP_NO_XP_THEME)
		self._parent = parent
		
		self.editors = [stc.PrimaryEditor(self, filename)]
		self.editors[0].OnInit(filename)
		self.focused = 0
		
		self.Initialize(self.editors[0])
		self.SetSashGravity(0.5)
		
		self.Bind(wx.EVT_SPLITTER_UNSPLIT, self.OnSplitterUnsplit)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
	
	def Split(self, orientation=wx.VERTICAL):
		if len(self.editors) == 1:
			self.editors.append(stc.SecondaryEditor(self))
			self.editors[1].SetDocPointer(self.editors[0].GetDocPointer())
			self.editors[1].OnInit()
		else:
			self.Unsplit()
		if orientation == wx.VERTICAL:
			self.SplitVertically(*self.editors)
			self._parent.menubar.Check(self._parent.menubar.ID_SPLIT_V, True)
		else:
			self.SplitHorizontally(*self.editors)
			self._parent.menubar.Check(self._parent.menubar.ID_SPLIT_H, True)
	
	def UnSplit(self):
		self.Unsplit()
		self.OnSplitterUnsplit(None)
	
	def OnSplitterUnsplit(self, event):
		self._parent._app.plugins.UnregisterEditor(self.editors[1])
		self.editors.pop(1).Destroy()
		self._parent.menubar.Check(self._parent.menubar.ID_HIDE_2ND, True)
		wx.CallAfter(self.editors[0].SetFocus)
	
	def OnClose(self, event):
		editor = self.editors[0]
		if editor.changes:
			save = wx.MessageBox(_("Don't you want to save your changes to '%s'?") % editor.filename, "Write++", wx.ICON_WARNING | wx.YES_NO | wx.CANCEL)
			if save == wx.YES:
				saved = editor.Save()
				if not saved:
					return
			elif save == wx.CANCEL:
				return
		for editor2 in self.editors:
			self._parent._app.plugins.UnregisterEditor(editor2)
		if os.path.isfile(editor.filename):
			self._parent.menubar.recent.AddFile(editor.filename)
		if self._parent.notebook.GetPageCount() == 1:
			wx.CallAfter(self._parent.New)
		self._parent.notebook.DeletePage(self._parent.GetTab(editor))

class TabTextCtrl(aui.TabTextCtrl):
	def __init__(self, *args):
		aui.TabTextCtrl.__init__(self, *args)
		
		filename = self.GetValue()
		self.asterisk = filename.startswith("*")
		period = filename.rfind(".")
		if period == -1:
			period = len(filename)
		self.SetSelection(0, period)
		
		self.Bind(wx.EVT_TEXT, self.OnText)
	
	def OnText(self, event):
		text = self.GetValue()
		if self.asterisk and not text.startswith("*"):
			self.ChangeValue("*" + text)
			self.SetInsertionPoint(1)

aui.auibook.TabTextCtrl = TabTextCtrl
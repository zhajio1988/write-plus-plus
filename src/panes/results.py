"""
results.py - results pane class for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

import os.path
import wx

import aui

_ = wx.GetTranslation

class ResultsPane(wx.Panel):
	def __init__(self, parent, results):
		wx.Panel.__init__(self, parent, -1)
		self._parent = parent
		
		self.filtertimer = wx.Timer()
		self.results = results
		
		self.toolbar = aui.AuiToolBar(self, -1, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW | aui.AUI_TB_HORZ_TEXT)
		self.filterctrl = wx.SearchCtrl(self.toolbar, -1, size=(220, -1), style=wx.TE_PROCESS_ENTER)
		self.filterctrl.SetDescriptiveText(_("Filter..."))
		self.filterctrl.GetChildren()[0].SetAcceleratorTable(wx.AcceleratorTable([(wx.ACCEL_CTRL, ord("A"), wx.ID_SELECTALL)]))
		self.toolbar.AddControl(self.filterctrl)
		self.filterctrl.Bind(wx.EVT_TEXT, self.OnText)
		self.filterctrl.Bind(wx.EVT_TEXT_ENTER, self.OnFilter)
		self.filterctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancelBtn)
		self.ID_EXCLUDE = wx.NewId()
		self.toolbar.AddCheckTool(self.ID_EXCLUDE, "", parent.Bitmap("exclude"), wx.NullBitmap, _("Exclude Filter"))
		self.Bind(wx.EVT_MENU, self.OnExclude, id=self.ID_EXCLUDE)
		self.toolbar.AddSeparator()
		self.toolbar.AddSimpleTool(wx.ID_SAVE, _("Save"), parent.Bitmap("save"), _("Save Results"))
		self.Bind(wx.EVT_MENU, self.OnSave, id=wx.ID_SAVE)
		self.toolbar.AddSimpleTool(wx.ID_REFRESH, _("Refresh"), parent.Bitmap("refresh"), _("Redo Search"))
		self.Bind(wx.EVT_MENU, self.OnRefresh, id=wx.ID_REFRESH)
		self.toolbar.Realize()
		
		self.tree = wx.TreeCtrl(self, -1, style=wx.NO_BORDER | wx.TR_HAS_BUTTONS | wx.TR_NO_LINES | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_LINES_AT_ROOT | wx.TR_HIDE_ROOT)
		self.root = self.tree.AddRoot("")
		self.tree.SetFont(wx.Font(parent.GetFont().GetPointSize(), wx.TELETYPE, wx.NORMAL, wx.NORMAL))
		self.Load(results, False)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.toolbar, 0, wx.EXPAND)
		sizer.Add(self.tree, 1, wx.EXPAND)
		self.SetSizer(sizer)
		
		self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
		self.filtertimer.Bind(wx.EVT_TIMER, self.OnFilter)
	
	def Load(self, results, clear=True, highlight=False):
		wx.BeginBusyCursor()
		self.tree.Freeze()
		if clear:
			self.tree.DeleteAllItems()
		filterstr = self.filterctrl.GetValue().lower()
		exclude = self.toolbar.GetToolToggled(self.ID_EXCLUDE)
		spaces = " " * self._parent.editor.GetIndent()
		wrapindent = self._parent.editor.GetWrapStartIndent()
		for i in xrange(len(results)):
			if not len(results[i][1]):
				continue
			count = 0
			for line, text, start, end in results[i][1]:
				if (not len(filterstr)) or ((filterstr in text.lower()) != exclude):
					if count == 0:
						filename = results[i][0]
						node = self.tree.AppendItem(self.root, filename, data=wx.TreeItemData((filename,)))
						self.tree.SetItemBold(node)
						self.tree.SetItemTextColour(node, wx.BLUE)
						previous = -1
						if highlight:
							old = -1
							for j in range(len(self.results)):
								if self.results[j][0] == filename:
									old = j
									break
					spaced = text.replace("\t", spaces)
					if line != previous:
						subnode = self.tree.AppendItem(node, "%d: %s" % (line + 1, spaced.strip()), data=wx.TreeItemData((filename, start, end)))
					else:
						subnode = self.tree.AppendItem(node, "%s  %s" % (" " * (len(str(line + 1)) + wrapindent), spaced.rstrip()), data=wx.TreeItemData((filename, start, end)))
					if highlight:
						found = False
						if old != -1:						
							for result in self.results[old][1]:
								if result[0] == line:
									found = True
									break
						if not found:
							self.tree.SetItemBackgroundColour(subnode, wx.YELLOW)
					previous = line
					count += 1
			if count > 0:
				self.tree.SetItemText(node, _("%s (%d hits)") % (filename, count))
				self.tree.Expand(node)
		self.tree.Thaw()
		wx.EndBusyCursor()
	
	def OnText(self, event):
		self.filterctrl.ShowCancelButton(not self.filterctrl.IsEmpty())
		self.filtertimer.Start(500, wx.TIMER_ONE_SHOT)
	
	def OnFilter(self, event):
		self.Load(self.results)
	
	def OnCancelBtn(self, event):
		self.filterctrl.ChangeValue("")	# Avoid generating an EVT_TEXT event
		self.filterctrl.ShowCancelButton(False)
		self.OnFilter(None)
	
	def OnExclude(self, event):
		if not self.filterctrl.IsEmpty():
			self.Load(self.results)
	
	def OnSave(self, event):
		dialog = wx.FileDialog(self._parent, _("Save Find Results"), os.path.dirname(self._parent.editor.filename), "%s.txt" % self._parent.aui.GetPane(self).caption, _("Write++ Find Results (*.txt)|*.txt"), wx.SAVE | wx.OVERWRITE_PROMPT)
		if dialog.ShowModal() == wx.ID_OK:
			fileobj = open(dialog.GetPath(), 'w')
			node, cookie = self.tree.GetFirstChild(self.root)
			while node.IsOk():
				print >> fileobj, self.tree.GetItemText(node)
				subnode, cookie2 = self.tree.GetFirstChild(node)
				while subnode.IsOk():
					print >> fileobj, "\t%s" % self.tree.GetItemText(subnode)
					subnode, cookie2 = self.tree.GetNextChild(node, cookie2)
				node, cookie = self.tree.GetNextChild(self.root, cookie)
			fileobj.close()
			self._parent.statusbar.SetStatusText(_("Saved '%s'") % self._parent.aui.GetPane(self).caption)
		dialog.Destroy()
	
	def OnRefresh(self, event):
		results = self._parent.search.FindAll(*self._parent.search.lastfindall)
		self.Load(results, highlight=True)
		self._parent.search.pdialog.Destroy()
		self.results = results
	
	def OnItemActivated(self, event):
		item = event.GetItem()
		data = self.tree.GetPyData(item)
		if data:
			self._parent.OpenFile(data[0])
			if len(data) > 1:
				self._parent.editor.EnsureVisible(self._parent.editor.LineFromPosition(data[1]))
				self._parent.editor.SetSelection(data[1], data[2])
				self._parent.editor.EnsureCaretVisible()
		if self.tree.GetItemBackgroundColour(item) != wx.NullColour:
			self.tree.SetItemBackgroundColour(item, wx.NullColour)
		event.Skip()
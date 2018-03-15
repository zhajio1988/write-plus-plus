"""
search.py - search dialog classes for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
NOTE: Parts of this file are based on code from PythonWin
"""

import os.path
import re
import unicodedata
import wx
from wx.lib.agw import aui

from stc import encodings

_ = wx.GetTranslation

class SearchDialog(wx.Dialog):
	def __init__(self, parent, find=True, lookin=-1):
		wx.Dialog.__init__(self, parent, -1, _("Find"))
		self._parent = parent
		
		self.lastreplace = None
		self.mode = int(not find)
		
		self.toolbar = aui.AuiToolBar(self, -1, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW | aui.AUI_TB_PLAIN_BACKGROUND | aui.AUI_TB_HORZ_TEXT)
		self.toolbar.AddRadioTool(wx.ID_FIND, _("Find"), parent.Bitmap("find"), wx.NullBitmap)
		self.Bind(wx.EVT_MENU, self.OnShowFind, id=wx.ID_FIND)
		self.toolbar.AddRadioTool(wx.ID_REPLACE, _("Replace"), parent.Bitmap("replace"), wx.NullBitmap)
		self.Bind(wx.EVT_MENU, self.OnShowReplace, id=wx.ID_REPLACE)
		if self.mode == 0:
			self.toolbar.ToggleTool(wx.ID_FIND, True)
		else:
			self.toolbar.ToggleTool(wx.ID_REPLACE, True)
		self.toolbar.AddStretchSpacer(1)
		self.ID_LABEL = wx.NewId()
		self.toolbar.AddLabel(self.ID_LABEL, "", self.toolbar.GetTextExtent(_("Direction:"))[0] - 5)
		self.up = wx.RadioButton(self.toolbar, -1, _("Up"))
		self.toolbar.AddControl(self.up)
		self.down = wx.RadioButton(self.toolbar, -1, _("Down"))
		self.down.SetValue(True)
		self.toolbar.AddControl(self.down)
		self.toolbar.Realize()
		
		self.find = wx.ComboBox(self, -1, choices=parent._app.settings["FindHistory"])
		selection = parent.editor.GetSelectedText()
		if len(selection) == 0:
			self.find.SetValue(parent._app.settings["LastFind"])
		else:
			self.find.SetValue(selection)
		self.Replace = wx.StaticText(self, -1, _("Replace with:"))
		self.replace = wx.ComboBox(self, -1, choices=parent._app.settings["ReplaceHistory"])
		self.replace.SetValue(parent._app.settings["LastReplace"])
		if wx.VERSION_STRING >= "2.9.1.0":
			box = wx.StaticBox(self, -1, _("Options"))
		else:
			box = self
		self.wholeword = wx.CheckBox(box, -1, _("Whole Word"))
		self.matchcase = wx.CheckBox(box, -1, _("Case Sensitive"))
		self.regex = wx.CheckBox(box, -1, _("Regular Expression"))
		self.wrap = wx.CheckBox(box, -1, _("Wrap around"))
		self.wrap.SetValue(True)
		self.include = wx.CheckBox(box, -1, _("Include files without unsaved changes"))
		self.include.SetValue(True)
		self.lookin = wx.RadioBox(self, -1, _("Search in"), choices=[_("Current File"), _("Selected Text"), _("Open Files"), _("Directory")], majorDimension=1, style=wx.RA_SPECIFY_COLS)
		if lookin == -1:
			lookin = len(selection) > 0
		self.lookin.SetSelection(lookin)
		if wx.VERSION_STRING >= "2.9.1.0":
			self.Directory = wx.StaticBox(self, -1, _("Directory"))
		else:
			self.Directory = self
		self.dirpicker = wx.DirPickerCtrl(self.Directory, -1, os.path.split(self._parent.GetEditor().filename)[0], style=wx.DIRP_DEFAULT_STYLE ^ wx.DIRP_DIR_MUST_EXIST)
		self.Filters = wx.StaticText(self.Directory, -1, _("Filters (e.g., *.txt;?.gif):"))
		self.filters = wx.ComboBox(self.Directory, -1, choices=parent._app.settings["FilterHistory"])
		self.filters.SetValue(parent._app.settings["LastFilter"])
		self.exclude = wx.CheckBox(self.Directory, -1, _("Exclude"))
		self.exclude.SetValue(parent._app.settings["FilterExclude"])
		self.button = wx.Button(self, -1, _("Find"))
		self.button2 = wx.Button(self, -1, _("Count"))
		self.button3 = wx.Button(self, -1, _("Replace"))
		self.close = wx.Button(self, wx.ID_CLOSE)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.toolbar, 0, wx.EXPAND)
		sizer2 = wx.FlexGridSizer(cols=2, hgap=2, vgap=3)
		sizer2.AddGrowableCol(1)
		sizer2.Add(wx.StaticText(self, -1, _("Find what:")), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
		sizer2.Add(self.find, 1, wx.EXPAND)
		sizer2.Add(self.Replace, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
		sizer2.Add(self.replace, 1, wx.EXPAND)
		sizer.Add(sizer2, 1, wx.ALL | wx.EXPAND, 5)
		sizer3 = wx.BoxSizer(wx.HORIZONTAL)
		if wx.VERSION_STRING < "2.9.1.0":
			box = wx.StaticBox(self, -1, _("Options"))
		sizer4 = wx.StaticBoxSizer(box, wx.VERTICAL)
		sizer4.Add(self.wholeword, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
		sizer4.Add(self.matchcase, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
		sizer4.Add(self.regex, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
		sizer4.Add(self.wrap, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
		sizer4.Add(self.include, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
		sizer3.Add(sizer4, 1, wx.ALL | wx.EXPAND, 5)
		sizer3.Add(self.lookin, 1, wx.ALL | wx.EXPAND, 5)
		sizer.Add(sizer3, 0, wx.EXPAND)
		if wx.VERSION_STRING < "2.9.1.0":
			self.Directory = wx.StaticBox(self, -1, _("Directory"))
		sizer5 = wx.StaticBoxSizer(self.Directory, wx.VERTICAL)
		sizer5.Add(self.dirpicker, 1, wx.ALL | wx.EXPAND, 1)
		sizer6 = wx.BoxSizer(wx.HORIZONTAL)
		sizer6.Add(self.Filters, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 2)
		sizer6.Add(self.filters, 1, wx.ALL | wx.EXPAND, 2)
		sizer6.Add(self.exclude, 0, wx.ALL | wx.EXPAND, 2)
		sizer5.Add(sizer6, 1, wx.EXPAND)
		sizer.Add(sizer5, 0, wx.ALL | wx.EXPAND, 5)
		sizer7 = wx.BoxSizer(wx.HORIZONTAL)
		sizer7.Add(self.button, 0, wx.ALL | wx.EXPAND, 5)
		sizer7.Add(self.button2, 0, wx.ALL | wx.EXPAND, 5)
		sizer7.Add(self.button3, 0, wx.ALL | wx.EXPAND, 5)
		sizer7.Add(self.close, 0, wx.ALL | wx.EXPAND, 5)
		sizer.Add(sizer7, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.SetSizer(sizer)
		
		if lookin < 2:
			self.toolbar.FindTool(self.ID_LABEL).SetLabel(_("Direction:"))
		self.up.Show(lookin < 2)
		self.down.Show(lookin < 2)
		self.wrap.Hide()	# Sizes the dialog nicely and keeps it from being too narrow
		sizer.Fit(self)
		self.wrap.Show(lookin < 2)
		self.include.Show(lookin > 1)
		if lookin == 3:
			self.include.SetLabel(_("Include subfolders"))
		self.Directory.Enable(lookin == 3)
		self.dirpicker.Enable(lookin == 3)
		for control in (self.Filters, self.filters, self.exclude):
			control.Enable(lookin > 1)
		
		self.lookin.Bind(wx.EVT_RADIOBOX, self.OnLookIn)
		self.button.Bind(wx.EVT_BUTTON, self.OnButton)
		self.button2.Bind(wx.EVT_BUTTON, self.OnButton2)
		self.button3.Bind(wx.EVT_BUTTON, self.OnButton3)
		self.close.Bind(wx.EVT_BUTTON, self.OnClose)
		self.wrap.Bind(wx.EVT_CHECKBOX, self.OnWrap)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
	
	def OnShowFind(self, event):
		self.SetTitle(_("Find"))
		self.Freeze()
		self.Replace.Disable()
		self.replace.Disable()
		self.button.SetDefault()
		self.button2.SetLabel(_("Count"))
		self.button3.SetLabel(_("Find All"))
		self.Layout()
		self.Thaw()
		self.mode = 0
	
	def OnShowReplace(self, event):
		self.SetTitle(_("Replace"))
		self.Freeze()
		self.Replace.Enable()
		self.replace.Enable()
		self.button2.SetLabel(_("Replace"))
		self.button2.SetDefault()
		self.button3.SetLabel(_("Replace All"))
		self.Layout()
		self.Thaw()
		self.mode = 1
	
	def OnLookIn(self, event):
		self.Freeze()
		selection = event.GetSelection()
		if selection < 2:
			self.toolbar.FindTool(self.ID_LABEL).SetLabel(_("Direction:"))
		else:
			self.toolbar.FindTool(self.ID_LABEL).SetLabel("")
		for control in (self.up, self.down, self.wrap):
			control.Show(selection < 2)
		self.include.Show(selection > 1)
		self.Directory.Enable(selection == 3)
		self.dirpicker.Enable(selection == 3)
		if selection == 2:
			self.include.SetLabel(_("Include files without unsaved changes"))
		elif selection == 3:
			self.include.SetLabel(_("Include subfolders"))
		for control in (self.Filters, self.filters, self.exclude):
			control.Enable(selection > 1)
		self.button.Enable(selection < 2)
		self.button2.Enable(selection < 2)
		self.Layout()
		self.Thaw()
	
	def OnButton(self, event):
		text = self.find.GetValue()
		pattern = regex(unicodedata.normalize('NFKD', text), self.matchcase.GetValue(), self.wholeword.GetValue(), not self.regex.GetValue())
		self._parent.search.FindNext(pattern, self._parent.search.CalculateSpan(self), text)
		if text not in self.find.GetStrings():
			self.find.Insert(text, 0)
			if self.find.GetCount() > 10:
				self.find.Delete(10)
		self._parent.menubar.Enable(self._parent.menubar.ID_FIND_NEXT, True)
		self._parent.menubar.Enable(self._parent.menubar.ID_FIND_PREVIOUS, True)
	
	def OnButton2(self, event):
		text = self.find.GetValue()
		pattern = regex(unicodedata.normalize('NFKD', text), self.matchcase.GetValue(), self.wholeword.GetValue(), not self.regex.GetValue())
		span = self._parent.search.CalculateSpan(self)
		if self.mode == 0:
			start, end, dummy = self._parent.search.Find(pattern, span, wrap=False)
			matches = 0
			if not span:
				span = (0, self._parent.editor.GetTextLength())
			while start != -1:
				matches += 1
				start, end, dummy = self._parent.search.Find(pattern, (end + 1, span[1]), wrap=False)
			wx.MessageBox(_("%d occurrences found.") % matches, _("Find"), wx.ICON_INFORMATION | wx.OK)
		else:
			replacement = self.replace.GetValue()
			if self.lastreplace == text:
				text2 = self._parent.search.GetTextRange(self._parent.editor.GetSelection(), self._parent.editor)
				self._parent.editor.ReplaceSelection(pattern.sub(replacement, text2))
			start, end, wrapped = self._parent.search.Find(pattern, span)
			if start != -1:
				self._parent.editor.EnsureVisible(self._parent.editor.LineFromPosition(start))
				self._parent.editor.SetSelection(start, end)
				self._parent.editor.EnsureCaretVisible()
				if wrapped:
					self._parent.statusbar.SetStatusText(_("Wrapped around"), 0)
				self.lastreplace = text
			else:
				wx.MessageBox(_("Could not find '%s'.") % text, _("Replace"), wx.ICON_EXCLAMATION | wx.OK)
		if text not in self.find.GetStrings():
			self.find.Insert(text, 0)
			if self.find.GetCount() > 10:
				self.find.Delete(10)
		if self.mode > 0 and replacement not in self.replace.GetStrings():
			self.replace.Insert(replacement, 0)
			if self.replace.GetCount() > 10:
				self.replace.Delete(10)
	
	def OnButton3(self, event):
		lookin = self.lookin.GetSelection()
		if lookin == 3:
			directory = self.dirpicker.GetPath()
			if not os.path.isdir(directory):
				wx.MessageBox(_("'%s' is not a valid directory.") % directory, "Write++", wx.ICON_EXCLAMATION | wx.OK)
				return
			elif self.mode > 0:
				replace = wx.MessageBox(_("This action cannot be undone.\nAre you sure that you want to continue?"), _("Replace"), wx.ICON_WARNING | wx.YES_NO)
				if replace != wx.YES:
					return
		text = self.find.GetValue()
		pattern = regex(unicodedata.normalize('NFKD', text), self.matchcase.GetValue(), self.wholeword.GetValue(), not self.regex.GetValue())
		filterstr = self.filters.GetValue()
		if self.mode == 0:
			self.Hide()
			results = self._parent.search.FindAll(pattern, lookin, self.dirpicker.GetPath(), filterstr, self.exclude.GetValue(), self.include.GetValue(), text)
			count = 0
			if results:
				for item in results:
					count += len(item[1])
			if count > 0:
				import panes.results
				resultspane = panes.results.ResultsPane(self._parent, results)
				self._parent.search.pdialog.Destroy()
				self._parent.results += 1
				self._parent.managers[wx.BOTTOM].AddPane(resultspane, _("Find Results %d") % self._parent.results, self._parent.Bitmap("find-results"), "~results%s" % self._parent.results, 200, True)
				wx.CallAfter(resultspane.tree.ScrollTo, resultspane.tree.GetFirstChild(resultspane.root)[0])
			else:
				self._parent.search.pdialog.Destroy()
				if results != None:
					wx.MessageBox(_("Could not find '%s'.") % text, _("Find"), wx.ICON_EXCLAMATION | wx.OK)
					self.Show()
				else:
					self.Close()
				return
			self.Close()
		else:
			self.Hide()
			filenames = self._parent.search.GetFilenames(lookin, self.filters.GetValue(), self.exclude.GetValue(), self.include.GetValue(), self.dirpicker.GetPath())
			dialog = wx.ProgressDialog(_("Replacing"), _("Please wait, replacing..."), len(filenames), style=wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)
			i = 0
			replacement = self.replace.GetValue()
			replaced = 0
			for filename in filenames:
				dialog.Update(i)
				tab = -1
				for j in range(self._parent.notebook.GetPageCount()):
					if self._parent.GetEditor(j).filename == filename:
						tab = j
						break
				if tab != -1:
					editor = self._parent.GetEditor(tab)
					if lookin == 1:
						span = editor.GetSelection()
					else:
						span = (0, editor.GetTextLength())
					start, end, dummy = self._parent.search.Find(pattern, span, editor, wrap=False)
					replacement = self.replace.GetValue()
					editor.BeginUndoAction()
					while start != -1:
						editor.SetTargetStart(start)
						editor.SetTargetEnd(end)
						text2 = pattern.sub(replacement, self._parent.search.GetTextRange((start, end), editor))
						editor.ReplaceTarget(text2)
						replaced += 1
						start, end, dummy = self._parent.search.Find(pattern, (end - (end - start) + len(text2), span[1]), editor, wrap=False)
					editor.EndUndoAction()
				else:
					replaced += self.ReplaceInFile(filename, pattern, replacement)
				i += 1
			dialog.Destroy()
			if replaced > 0:
				wx.MessageBox(_("%d occurrences replaced.") % replaced, _("Replace"), wx.ICON_INFORMATION | wx.OK)
			else:
				wx.MessageBox(_("Could not find '%s'.") % text, _("Replace"), wx.ICON_EXCLAMATION | wx.OK)
			self.Show()
			self._parent.search.pattern = pattern
		if text not in self.find.GetStrings():
			self.find.Insert(text, 0)
			if self.find.GetCount() > 10:
				self.find.Delete(10)
		if self.mode > 0 and replacement not in self.replace.GetStrings():
			self.replace.Insert(replacement, 0)
			if self.replace.GetCount() > 10:
				self.replace.Delete(10)
		if filterstr not in self.filters.GetStrings():
			self.filters.Insert(filterstr, 0)
			if self.filters.GetCount() > 10:
				self.filters.Delete(10)
	
	def ReplaceInFile(self, filename, pattern, replacement):
		fileobj = open(filename, 'r+b')
		text = fileobj.read()
		if not len(text):
			fileobj.close()
			return 0
		encoding = wx.GetDefaultPyEncoding()
		for bom in encodings:
			if text.startswith(bom):
				encoding = encodings[bom]
				text = text[len(bom):]
				break
		try:
			text = text.decode(encoding)
		except UnicodeDecodeError:	# If default encoding fails, Latin1 seems to work
			text = text.decode("latin_1")
			encoding = "latin_1"
		text, replaces = pattern.subn(replacement, text)
		if replaces > 0:	# Don't edit the file if nothing was replaced
			fileobj.seek(0)
			fileobj.write(text.encode(encoding))
			fileobj.truncate()
		fileobj.close()
		return replaces
	
	def OnWrap(self, event):
		self._parent.search.wrap = event.IsChecked()
	
	def OnClose(self, event):
		self._parent._app.settings["LastFind"] = self.find.GetValue()
		self._parent._app.settings["FindHistory"] = self.find.GetStrings()
		self._parent._app.settings["LastReplace"] = self.replace.GetValue()
		self._parent._app.settings["ReplaceHistory"] = self.replace.GetStrings()
		self._parent._app.settings["LastFilter"] = self.filters.GetValue()
		self._parent._app.settings["FilterHistory"] = self.filters.GetStrings()
		self._parent._app.settings["FilterExclude"] = self.exclude.GetValue()
		self.Destroy()

def regex(pattern, matchcase=False, wholeword=False, escape=True):
	if escape:
		pattern = re.escape(pattern)
	if wholeword:
		pattern = r'\b%s\b' % pattern
	flags = re.MULTILINE | re.UNICODE
	if not matchcase:
		flags |= re.IGNORECASE
	return re.compile(pattern, flags)
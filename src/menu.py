"""
menu.py - menu and menubar classes for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

import os.path
import webbrowser
import wx

_ = wx.GetTranslation

class FileHistory(wx.Menu):
	def __init__(self, frame, filenames):
		wx.Menu.__init__(self)
		self._frame = frame
		
		self.filedict = {}
		
		for filename in filenames:
			self.AddFile2(filename)
	
	def AddFile(self, filename):
		if not len(filename):
			return
		if filename in self._frame._app.settings["RecentFiles"]:
			self.RemoveFile(filename)
		for frame in self._frame._app.frames:
			frame.menubar.recent.AddFile2(filename)
		self._frame._app.settings["RecentFiles"].append(filename)
		if len(self._frame._app.settings["RecentFiles"]) > 15:
			self.RemoveFile(self._frame._app.settings["RecentFiles"][0])
	
	def AddFile2(self, filename):
		id = wx.NewId()
		self.Insert(0, id, filename)
		self.filedict[id] = filename
		self._frame.Bind(wx.EVT_MENU, self.OnFile, id=id)
	
	def RenameFile2(self, old, new):
		for id in self.filedict:
			if self.filedict[id] == old:
				self.SetLabel(id, new)
				break
	
	def RenameFile(self, old, new):
		if old not in self._frame._app.settings["RecentFiles"]:
			return
		for frame in self._frame._app.frames:
			frame.menubar.recent.RenameFile2(old, new)
		self._frame._app.settings["RecentFiles"][self._frame._app.settings["RecentFiles"].index(old)] = new
	
	def RemoveFile2(self, filename):
		for id in self.filedict:
			if self.filedict[id] == filename:
				self.Delete(id)
				self.filedict.pop(id)
				break
	
	def RemoveFile(self, filename):
		for frame in self._frame._app.frames:
			frame.menubar.recent.RemoveFile2(filename)
		self._frame._app.settings["RecentFiles"].remove(filename)
	
	def OnFile(self, event):
		self._frame.OpenFile(self.filedict[event.GetId()])

class MenuBar(wx.MenuBar):
	def __init__(self, frame):
		wx.MenuBar.__init__(self)
		self._frame = frame
		
		self.File = wx.Menu()
		self.File.Append(wx.ID_NEW, _("&New\tCtrl+N"), _("Creates a new file"))
		frame.Bind(wx.EVT_MENU, self.OnNew, id=wx.ID_NEW)
		self.ID_NEW_FRAME = wx.NewId()
		self.File.Append(self.ID_NEW_FRAME, _("New Window...\tCtrl+Shift+N"))
		frame.Bind(wx.EVT_MENU, self.OnNewFrame, id=self.ID_NEW_FRAME)
		self.File.Append(wx.ID_OPEN, _("&Open...\tCtrl+O"), _("Opens a file"))
		frame.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)
		self.recent = FileHistory(frame, frame._app.settings["RecentFiles"])
		self.File.AppendSubMenu(self.recent, _("Open &Recent"))
		self.File.AppendSeparator()
		self.File.Append(wx.ID_CLOSE, _("&Close\tCtrl+W"), _("Closes the current file"))
		frame.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_CLOSE)
		self.File.Append(wx.ID_SAVE, _("&Save\tCtrl+S"), _("Saves the current file"))
		frame.Bind(wx.EVT_MENU, self.OnSave, id=wx.ID_SAVE)
		self.File.Append(wx.ID_SAVEAS, _("Save &As...\tCtrl+Shift+S"), _("Saves the current file with a different filename"))
		frame.Bind(wx.EVT_MENU, self.OnSaveAs, id=wx.ID_SAVEAS)
		self.ID_SAVEALL = wx.NewId()
		self.File.Append(self.ID_SAVEALL, _("Sa&ve All\tCtrl+Alt+S"), _("Saves all the open files that are modified"))
		frame.Bind(wx.EVT_MENU, self.OnSaveAll, id=self.ID_SAVEALL)
		self.File.AppendSeparator()
		self.ID_LOAD_SESSION = wx.NewId()
		self.File.Append(self.ID_LOAD_SESSION, _("Load Session..."), _("Loads a session"))
		frame.Bind(wx.EVT_MENU, self.OnLoadSession, id=self.ID_LOAD_SESSION)
		self.ID_SAVE_SESSION = wx.NewId()
		self.File.Append(self.ID_SAVE_SESSION, _("Save Session..."), _("Saves the current session"))
		frame.Bind(wx.EVT_MENU, self.OnSaveSession, id=self.ID_SAVE_SESSION)
		self.File.AppendSeparator()
		self.File.Append(wx.ID_REVERT, _("Revert to Saved"), _("Removes all changes made since the file was last saved"))
		frame.Bind(wx.EVT_MENU, self.OnRevert, id=wx.ID_REVERT)
		self.File.Append(wx.ID_REFRESH, _("Re&load\tShift+F5"), _("Reloads the current file from the disk"))
		frame.Bind(wx.EVT_MENU, self.OnReload, id=wx.ID_REFRESH)
		self.File.AppendSeparator()
		self.File.Append(wx.ID_PRINT, _("&Print...\tCtrl+P"), _("Prints the current file"))
		frame.Bind(wx.EVT_MENU, self.OnPrint, id=wx.ID_PRINT)
		self.File.Append(wx.ID_PAGE_SETUP, _("Page Set&up...\tCtrl+Shift+P"), _("Configures page setup"))
		frame.Bind(wx.EVT_MENU, self.OnPageSetup, id=wx.ID_PAGE_SETUP)
		self.File.Append(wx.ID_PREVIEW, _("Print Previe&w...\tCtrl+Alt+P"), _("Previews a printing of the current file"))
		frame.Bind(wx.EVT_MENU, self.OnPrintPreview, id=wx.ID_PREVIEW)
		self.File.AppendSeparator()
		self.ID_OPEN_FOLDER = wx.NewId()
		self.File.Append(self.ID_OPEN_FOLDER, _("Open Containing &Folder...\tCtrl+Shift+O"), _("Browses the folder that the current file is in"))
		frame.Bind(wx.EVT_MENU, self.OnOpenFolder, id=self.ID_OPEN_FOLDER)
		if wx.Platform != "__WXMAC__":
			self.File.AppendSeparator()
		self.File.Append(wx.ID_EXIT, _("E&xit\tAlt+F4"), _("Exits the application and prompts to save files"))
		frame.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
		self.Append(self.File, _("&File"))
		
		self.Edit = wx.Menu()
		self.Edit.Append(wx.ID_UNDO, _("&Undo\tCtrl+Z"), _("Reverses the last action"))
		frame.Bind(wx.EVT_MENU, self.OnUndo, id=wx.ID_UNDO)
		self.Edit.Append(wx.ID_REDO, _("&Redo\tCtrl+Y"), _("Redoes the last action"))
		frame.Bind(wx.EVT_MENU, self.OnRedo, id=wx.ID_REDO)
		self.Edit.AppendSeparator()
		self.Edit.Append(wx.ID_CUT, _("Cu&t\tCtrl+X"), _("Deletes the selected text and copies it to the clipboard"))
		frame.Bind(wx.EVT_MENU, self.OnCut, id=wx.ID_CUT)
		self.Edit.Append(wx.ID_COPY, _("&Copy\tCtrl+C"), _("Copies the selected text to the clipboard"))
		frame.Bind(wx.EVT_MENU, self.OnCopy, id=wx.ID_COPY)
		self.Edit.Append(wx.ID_PASTE, _("&Paste\tCtrl+V"), _("Pastes the contents of the clipboard into the current file"))
		frame.Bind(wx.EVT_MENU, self.OnPaste, id=wx.ID_PASTE)
		self.Edit.AppendSeparator()
		self.case = wx.Menu()
		self.ID_UPPER_CASE = wx.NewId()
		self.case.Append(self.ID_UPPER_CASE, _("&Upper Case\tCtrl+Shift+U"), _("Converts the selected text to UPPER CASE"))
		frame.Bind(wx.EVT_MENU, self.OnUpperCase, id=self.ID_UPPER_CASE)
		self.ID_LOWER_CASE = wx.NewId()
		self.case.Append(self.ID_LOWER_CASE, _("&Lower Case\tCtrl+Shift+L"), _("Converts the selected text to lower case"))
		frame.Bind(wx.EVT_MENU, self.OnLowerCase, id=self.ID_LOWER_CASE)
		self.ID_PROPER_CASE = wx.NewId()
		self.case.Append(self.ID_PROPER_CASE, _("&Proper Case"), _("Converts the selected text to Proper Case"))
		frame.Bind(wx.EVT_MENU, self.OnProperCase, id=self.ID_PROPER_CASE)
		self.ID_SENTENCE_CASE = wx.NewId()
		self.case.Append(self.ID_SENTENCE_CASE, _("&Sentence Case"), _("Converts the selected text to Sentence case"))
		frame.Bind(wx.EVT_MENU, self.OnSentenceCase, id=self.ID_SENTENCE_CASE)
		self.Edit.AppendSubMenu(self.case, _("Convert C&ase"))
		self.whitespace = wx.Menu()
		self.ID_TABIFY = wx.NewId()
		self.whitespace.Append(self.ID_TABIFY, _("&Tabify\tCtrl+Shift+Tab"), _("Converts leading spaces to tabs"))
		frame.Bind(wx.EVT_MENU, self.OnTabify, id=self.ID_TABIFY)
		self.ID_UNTABIFY = wx.NewId()
		self.whitespace.Append(self.ID_UNTABIFY, _("U&ntabify\tCtrl+Shift+Space"), _("Converts leading tabs to spaces"))
		frame.Bind(wx.EVT_MENU, self.OnUntabify, id=self.ID_UNTABIFY)
		self.Edit.AppendSubMenu(self.whitespace, _("&Whitespace"))
		self.Append(self.Edit, _("&Edit"))
		
		self.Search = wx.Menu()
		self.Search.Append(wx.ID_FIND, _("&Find\tCtrl+F"))
		frame.Bind(wx.EVT_MENU, self.OnFind, id=wx.ID_FIND)
		self.ID_FIND_IN_FILES = wx.NewId()
		self.Search.Append(self.ID_FIND_IN_FILES, _("F&ind in Files...\tCtrl+Shift+F"))
		frame.Bind(wx.EVT_MENU, self.OnFindInFiles, id=self.ID_FIND_IN_FILES)
		self.ID_FIND_NEXT = wx.NewId()
		self.Search.Append(self.ID_FIND_NEXT, _("Find &Next\tF3"))
		frame.Bind(wx.EVT_MENU, self.OnFindNext, id=self.ID_FIND_NEXT)
		self.ID_FIND_PREVIOUS = wx.NewId()
		self.Search.Append(self.ID_FIND_PREVIOUS, _("Find &Previous\tShift+F3"))
		frame.Bind(wx.EVT_MENU, self.OnFindPrevious, id=self.ID_FIND_PREVIOUS)
		self.Search.Append(wx.ID_REPLACE, _("&Replace...\tCtrl+H"))
		frame.Bind(wx.EVT_MENU, self.OnReplace, id=wx.ID_REPLACE)
		self.ID_GOTO = wx.NewId()
		self.Search.Append(self.ID_GOTO, _("&Go to...\tCtrl+G"))
		frame.Bind(wx.EVT_MENU, self.OnGoto, id=self.ID_GOTO)
		self.Search.AppendSeparator()
		self.ID_TOGGLE_BOOKMARK = wx.NewId()
		self.Search.Append(self.ID_TOGGLE_BOOKMARK, _("Toggle &Bookmark\tCtrl+F2"))
		frame.Bind(wx.EVT_MENU, self.OnToggleBookmark, id=self.ID_TOGGLE_BOOKMARK)
		self.ID_NEXT_BOOKMARK = wx.NewId()
		self.Search.Append(self.ID_NEXT_BOOKMARK, _("Next Bookmark\tF2"))
		frame.Bind(wx.EVT_MENU, self.OnNextBookmark, id=self.ID_NEXT_BOOKMARK)
		self.ID_PREVIOUS_BOOKMARK = wx.NewId()
		self.Search.Append(self.ID_PREVIOUS_BOOKMARK, _("Previous Bookmark\tShift+F2"))
		frame.Bind(wx.EVT_MENU, self.OnPreviousBookmark, id=self.ID_PREVIOUS_BOOKMARK)
		self.Append(self.Search, _("&Search"))
		
		self.View = wx.Menu()
		self.ID_LANGUAGE = wx.NewId()
		self.View.Append(self.ID_LANGUAGE, _("Set &Language...\tCtrl+Shift+L"))
		frame.Bind(wx.EVT_MENU, self.OnLanguage, id=self.ID_LANGUAGE)
		self.ID_WORDWRAP = wx.NewId()
		self.View.AppendCheckItem(self.ID_WORDWRAP, _("&Word Wrap\tCtrl+E"))
		frame.Bind(wx.EVT_MENU, self.OnWordWrap, id=self.ID_WORDWRAP)
		self.split = wx.Menu()
		self.ID_SPLIT_V = wx.NewId()
		self.split.AppendRadioItem(self.ID_SPLIT_V, _("Split &Vertically\tCtrl+Shift+V"))
		frame.Bind(wx.EVT_MENU, self.OnSplitV, id=self.ID_SPLIT_V)
		self.ID_SPLIT_H = wx.NewId()
		self.split.AppendRadioItem(self.ID_SPLIT_H, _("Split &Horizontally\tCtrl+Shift+H"))
		frame.Bind(wx.EVT_MENU, self.OnSplitH, id=self.ID_SPLIT_H)
		self.ID_HIDE_2ND = wx.NewId()
		self.split.AppendRadioItem(self.ID_HIDE_2ND, _("Hide Second Editor\tCtrl+Shift+W"))
		frame.Bind(wx.EVT_MENU, self.OnHide2nd, id=self.ID_HIDE_2ND)
		self.View.AppendSubMenu(self.split, _("&Split Editor"))
		self.View.AppendSeparator()
		self.View.Append(wx.ID_ZOOM_IN, _("Zoom &In\tCtrl++"))
		frame.Bind(wx.EVT_MENU, self.OnZoomIn, id=wx.ID_ZOOM_IN)
		self.View.Append(wx.ID_ZOOM_OUT, _("Zoom &Out\tCtrl+-"))
		frame.Bind(wx.EVT_MENU, self.OnZoomOut, id=wx.ID_ZOOM_OUT)
		self.View.Append(wx.ID_ZOOM_100, _("Reset Zoom\tCtrl+0"))
		frame.Bind(wx.EVT_MENU, self.OnZoomDefault, id=wx.ID_ZOOM_100)
		self.View.AppendSeparator()
		self.ID_TOOLBAR = wx.NewId()
		self.View.AppendCheckItem(self.ID_TOOLBAR, _("&Toolbar"), _("Shows or hides the toolbar"))
		frame.Bind(wx.EVT_MENU, self.OnToolbar, id=self.ID_TOOLBAR)
		self.View.AppendSeparator()
		self.ID_FILEBROWSER = wx.NewId()
		self.View.AppendCheckItem(self.ID_FILEBROWSER, _("&File Browser\tCtrl+Alt+B"))
		frame.Bind(wx.EVT_MENU, self.OnFileBrowser, id=self.ID_FILEBROWSER)
		self.Append(self.View, _("&View"))
		
		self.Tools = wx.Menu()
		self.ID_RUN = wx.NewId()
		self.Tools.Append(self.ID_RUN, _("&Run\tF5"), _("Runs the current file with the associated application"))
		frame.Bind(wx.EVT_MENU, self.OnRun, id=self.ID_RUN)
		self.Tools.AppendSeparator()
		self.ID_PLUGINS = wx.NewId()
		self.Tools.Append(self.ID_PLUGINS, _("&Plugin Manager..."))
		frame.Bind(wx.EVT_MENU, self.OnPlugins, id=self.ID_PLUGINS)
		self.ID_STYLE_EDITOR = wx.NewId()
		self.Tools.Append(self.ID_STYLE_EDITOR, _("&Style Editor..."))
		frame.Bind(wx.EVT_MENU, self.OnStyleEditor, id=self.ID_STYLE_EDITOR)
		self.Tools.Append(wx.ID_PREFERENCES, _("Pre&ferences..."))
		frame.Bind(wx.EVT_MENU, self.OnPreferences, id=wx.ID_PREFERENCES)
		self.Append(self.Tools, _("&Tools"))
		
		self.Help = wx.Menu()
		self.Help.Append(wx.ID_HELP, _("&Contents...\tF1"), _("Shows the contents of the help file"))
		frame.Bind(wx.EVT_MENU, self.OnHelp, id=wx.ID_HELP)
		self.Help.Append(wx.ID_ABOUT, _("&About..."), _("Displays program information, version number, and copyright"))
		frame.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
		self.Append(self.Help, _("&Help"))
		
		for item in (wx.ID_SAVE, self.ID_SAVEALL, wx.ID_REVERT, wx.ID_REFRESH):
			self.Enable(item, False)
		self.Check(self.ID_HIDE_2ND, True)
	
	def OnNew(self, event):
		self._frame.New()
	
	def OnNewFrame(self, event):
		self._frame._app.NewFrame()
	
	def OnOpen(self, event):
		self._frame.OpenFiles()
	
	def OnClose(self, event):
		self._frame.notebook.GetCurrentPage().Close()
	
	def OnSave(self, event):
		self._frame.GetEditor().Save()
	
	def OnSaveAs(self, event):
		self._frame.GetEditor().SaveAs()
	
	def OnSaveAll(self, event):
		self._frame.SaveAll()
	
	def OnLoadSession(self, event):
		self._frame.LoadSession()
	
	def OnSaveSession(self, event):
		self._frame.SaveSession()
	
	def OnRevert(self, event):
		self._frame.GetEditor().Revert()
	
	def OnReload(self, event):
		self._frame.GetEditor().Reload()
	
	def OnPrint(self, event):
		self._frame._app.printer.Print(self._frame.GetEditor())
	
	def OnPageSetup(self, event):
		self._frame._app.printer.PageSetup()
	
	def OnPrintPreview(self, event):
		self._frame._app.printer.Preview(self._frame.GetEditor())
	
	def OnOpenFolder(self, event):
		webbrowser.open(os.path.dirname(self._frame.GetEditor().filename))

	def OnExit(self, event):
		self._frame._app.CloseAllFrames()

	def OnUndo(self, event):
		self._frame.editor.Undo()

	def OnRedo(self, event):
		self._frame.editor.Redo()

	def OnCut(self, event):
		self._frame.Cut()
	
	def OnCopy(self, event):
		self._frame.Copy()

	def OnPaste(self, event):
		self._frame.editor.Paste()
	
	def OnFind(self, event):
		self._frame.search.QuickFind()
	
	def OnFindInFiles(self, event):
		self._frame.search.ShowSearchDialog(True)
	
	def OnFindNext(self, event):
		self._frame.search.FindNext()
	
	def OnFindPrevious(self, event):
		self._frame.search.FindPrevious()
	
	def OnReplace(self, event):
		self._frame.search.ShowSearchDialog(False)
	
	def OnGoto(self, event):
		self._frame.editor.Goto()
	
	def OnToggleBookmark(self, event):
		self._frame.editor.ToggleBookmark()
	
	def OnNextBookmark(self, event):
		self._frame.editor.NextBookmark()
	
	def OnPreviousBookmark(self, event):
		self._frame.editor.PreviousBookmark()
	
	def OnUpperCase(self, event):
		self._frame.editor.UpperCase()
	
	def OnLowerCase(self, event):
		self._frame.editor.LowerCase()
	
	def OnProperCase(self, event):
		self._frame.editor.ProperCase()
	
	def OnSentenceCase(self, event):
		self._frame.editor.SentenceCase()
	
	def OnTabify(self, event):
		self._frame.editor.Tabify()
	
	def OnUntabify(self, event):
		self._frame.editor.Untabify()
	
	def OnLanguage(self, event):
		self._frame.ChooseLanguage()
	
	def OnWordWrap(self, event):
		self._frame.editor.SetWrapMode(event.IsChecked())
	
	def OnSplitV(self, event):
		self._frame.notebook.GetCurrentPage().Split(wx.VERTICAL)
	
	def OnSplitH(self, event):
		self._frame.notebook.GetCurrentPage().Split(wx.HORIZONTAL)
	
	def OnHide2nd(self, event):
		self._frame.notebook.GetCurrentPage().UnSplit()
	
	def OnZoomIn(self, event):
		self._frame.editor.ZoomIn()
	
	def OnZoomOut(self, event):
		self._frame.editor.ZoomOut()
	
	def OnZoomDefault(self, event):
		self._frame.editor.SetZoom(0)
	
	def OnToolbar(self, event):
		self._frame.ShowToolbar(event.IsChecked())
	
	def OnFileBrowser(self, event):
		self._frame.ShowFileBrowser(event.IsChecked())
	
	def OnRun(self, event):
		self._frame.GetEditor().Run()
	
	def OnPlugins(self, event):
		self._frame.Plugins()
	
	def OnStyleEditor(self, event):
		self._frame.StyleEditor()
	
	def OnPreferences(self, event):
		self._frame.Preferences()
	
	def OnHelp(self, event):
		self._frame._app.helper.ShowHelpFrame()
	
	def OnAbout(self, event):
		self._frame._app.helper.ShowAboutBox()

class TaskBarIcon(wx.TaskBarIcon):
	def __init__(self, frame):
		wx.TaskBarIcon.__init__(self)
		self._frame = frame
		
		self.SetIcon(wx.Icon(os.path.join(frame._app.cwd, "images", "write++-16.png"), wx.BITMAP_TYPE_PNG), frame.GetTitle())
		
		self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.OnRestore)

	def OnRestore(self, event):
		self._frame.Iconize(False)
		self._frame.Show()
		self._frame.Raise()
		self.RemoveIcon()
		wx.CallAfter(self._frame.editor.SetFocus)
		del self._frame.trayicon
	
	def OnNew(self, event):
		self._frame.New()
		self._frame.notebook.SetSelection(self._frame.notebook.GetPageCount() - 1)
		self.OnRestore(event)
	
	def OnNewAndPaste(self, event):
		self._frame.New()
		self._frame.notebook.SetSelection(self._frame.notebook.GetPageCount() - 1)
		self._frame.editor.Paste()
		self.OnRestore(event)
	
	def OnOpen(self, event):
		dialog = wx.FileDialog(self._frame, _("Open"), os.path.dirname(self._frame.GetEditor().filename), wildcard=self._frame.filetypes, style=wx.OPEN | wx.MULTIPLE)
		if dialog.ShowModal() == wx.ID_OK:
			self._frame.OpenFiles(dialog.GetPaths())
			self._frame.notebook.SetSelection(self._frame.notebook.GetPageCount() - 1)
			self.OnRestore(event)
		dialog.Destroy()
	
	def OnFindInFiles(self, event):
		wx.CallAfter(self._frame.search.ShowSearchDialog, lookin=3)
		self.OnRestore(event)
	
	def OnExit(self, event):
		wx.CallAfter(self.RemoveIcon)
		wx.CallAfter(self._frame.Close)
		self.OnRestore(event)

	def CreatePopupMenu(self):
		menu = wx.Menu()
		menu.Append(wx.ID_DEFAULT, _("&Restore"))
		self.Bind(wx.EVT_MENU, self.OnRestore, id=wx.ID_DEFAULT)
		menu.AppendSeparator()
		menu.Append(wx.ID_NEW, _("&New"))
		self.Bind(wx.EVT_MENU, self.OnNew, id=wx.ID_NEW)
		self.ID_NEW_AND_PASTE = wx.NewId()
		menu.Append(self.ID_NEW_AND_PASTE, _("New and &Paste"))
		self.Bind(wx.EVT_MENU, self.OnNewAndPaste, id=self.ID_NEW_AND_PASTE)
		menu.Append(wx.ID_OPEN, _("&Open..."))
		self.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)
		self.ID_FIND_IN_FILES = wx.NewId()
		menu.Append(self.ID_FIND_IN_FILES, _("&Find in Files"))
		self.Bind(wx.EVT_MENU, self.OnFindInFiles, id=self.ID_FIND_IN_FILES)
		menu.AppendSeparator()
		menu.Append(wx.ID_EXIT, _("E&xit"))
		self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
		return menu
"""
__init__.py - syntax functions for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
NOTE: Parts of this package are based on styles from Notepad++
"""

import os
import wx
from lxml import etree as ElementTree

import aui

_ = wx.GetTranslation

class Styler:
	def __init__(self, frame):
		styledir = os.path.join(frame._app.userdatadir, "styles")
		if not os.path.isdir(styledir):
			os.mkdir(styledir)
		filename = os.path.join(frame._app.userdatadir, "styles", "%s.xml" % _("Default"))
		if not os.path.isfile(filename):
			root = ElementTree.parse(os.path.join(frame._app.cwd, "styles.xml")).getroot()
			for element in root.findall(".//default") + [root[0].find("linenumber"), root[0].find("bracelight"), root[0].find("bracebad")]:
				if wx.Platform != "__WXGTK__":
					element.set("face", "Courier New")
					element.set("size", "10")
				else:
					element.set("face", "Monospace")
					element.set("size", "11")
			fileobj = open(filename, 'w')
			fileobj.write(ElementTree.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True))
			fileobj.close()
		self.etree = ElementTree.parse(filename)
		self.root = self.etree.getroot()
		
		self.cache = {"default":{}}
		for child in self.root[0]:
			self.cache["default"][child.tag] = child.attrib
		self.lexers = {}
		self.linenumdata = [9, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ""]
		if "size" in self.cache["default"]["linenumber"]:
			self.linenumdata = [int(self.cache["default"]["linenumber"]["size"]), wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, ""]
			if "modifiers" in self.cache["default"]["linenumber"]:
				if "italic" in self.cache["default"]["linenumber"]["modifiers"]:
					self.linenumdata[2] = wx.ITALIC
				if "bold" in self.cache["default"]["linenumber"]["modifiers"]:
					self.linenumdata[3] = wx.BOLD
				if "underline" in self.cache["default"]["linenumber"]["modifiers"]:
					self.linenumdata[4] = True
			if "face" in self.cache["default"]["linenumber"]:
				self.linenumdata[5] = self.cache["default"]["linenumber"]["face"]
		
		styledir = os.path.join(frame._app.userdatadir, "styles")
		if not os.path.isdir(styledir):
			os.mkdir(styledir)
	
	def GetStylesInfo(self, language, cache=True):
		if language not in self.cache:
			info = {}
			for child in self.root.find("./%s" % language):
				info[child.tag] = child.attrib
				if child.tag != "default":
					for attribute in info["default"]:
						if not (attribute in info[child.tag] or attribute == "modifiers"):
							info[child.tag][attribute] = info["default"][attribute]
			if not cache:
				return info
			self.cache[language] = info
		return self.cache[language]
	
	def FormatStyleInfo(self, info):
		spec = []
		for key in ("fore", "back", "face", "size"):
			if key in info:
				spec.append("%s:%s" % (key, info[key]))
		if "modifiers" in info:
			spec.append(info["modifiers"])
		return ",".join(spec)

def ChooseLanguage(frame):
	dialog = wx.SingleChoiceDialog(frame, _("Select a language:"), _("Set Language"), names)
	language = frame.GetEditor().language
	if language in styles.values():
		for style in styles:
			if styles[style] == language:
				language = style
				break
	dialog.SetSelection([language2.lower() for language2 in names].index(language))
	language = None
	if dialog.ShowModal() == wx.ID_OK:
		language = dialog.GetStringSelection().lower()
		if language in styles:
			language = styles[language]
	dialog.Destroy()
	return language

class StyleEditor(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, _("Style Editor"), size=(600, 440), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self._parent = parent
		
		self.root = self._parent.styler.root[:]
		
		self.toolbar = aui.AuiToolBar(self, -1, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW | aui.AUI_TB_PLAIN_BACKGROUND)
		self.toolbar.AddLabel(-1, _("Theme:"), self.toolbar.GetTextExtent(_("Theme:"))[0] - 5)
		self.themes = wx.Choice(self.toolbar, -1, choices=[_("Default")])
		self.themes.SetSelection(0)
		self.toolbar.AddControl(self.themes)
		self.toolbar.AddSeparator()
		self.toolbar.AddSimpleTool(wx.ID_NEW, "", parent.Bitmap("new-item"), _("New"))
		self.ID_RENAME = wx.NewId()
		self.toolbar.AddSimpleTool(self.ID_RENAME, "", parent.Bitmap("rename"), _("Rename"))
		self.toolbar.EnableTool(self.ID_RENAME, False)
		self.toolbar.AddSimpleTool(wx.ID_DELETE, "", parent.Bitmap("delete"), _("Delete"))
		self.toolbar.EnableTool(wx.ID_DELETE, False)
		self.toolbar.Realize()
		
		self.lexers = wx.Choice(self, -1)
		self.styles = wx.ListBox(self, -1)
		if wx.VERSION_STRING >= "2.9.1.0":
			box = wx.StaticBox(self, -1, _("Color Style"))
		else:
			box = self
		self.foreground = wx.ColourPickerCtrl(box, -1, wx.BLACK, style=wx.CLRP_USE_TEXTCTRL)
		self.background = wx.ColourPickerCtrl(box, -1, wx.WHITE, style=wx.CLRP_USE_TEXTCTRL)
		if wx.VERSION_STRING >= "2.9.1.0":
			box2 = wx.StaticBox(self, -1, _("Font Style"))
		else:
			box2 = self
		self.fonts = sorted(wx.FontEnumerator.GetFacenames())
		self.fontname = wx.Choice(box2, -1, choices=self.fonts)
		self.fontsize = wx.ComboBox(box2, -1, choices=sizes)
		self.bold = wx.CheckBox(box2, -1, _("Bold"))
		self.italic = wx.CheckBox(box2, -1, _("Italic"))
		self.underline = wx.CheckBox(box2, -1, _("Underline"))
		self.eol = wx.CheckBox(box2, -1, _("Eol"))
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.toolbar, 0, wx.EXPAND)
		sizer2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer3 = wx.BoxSizer(wx.VERTICAL)
		sizer3.Add(self.lexers, 0, wx.ALL, wx.EXPAND, 2)
		sizer3.Add(self.styles, 1, wx.ALL | wx.EXPAND, 2)
		sizer2.Add(sizer3, 0, wx.EXPAND)
		sizer4 = wx.BoxSizer(wx.VERTICAL)
		sizer5 = wx.BoxSizer(wx.HORIZONTAL)
		if wx.VERSION_STRING < "2.9.1.0":
			box = wx.StaticBox(self, -1, _("Color Style"))
		sizer6 = wx.StaticBoxSizer(box, wx.VERTICAL)
		if wx.VERSION_STRING < "2.9.1.0":
			box = self
		sizer6.Add(wx.StaticText(box, -1, _("Foreground color:")), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
		sizer6.Add(self.foreground, 1, wx.ALL | wx.EXPAND, 2)
		sizer6.Add(wx.StaticText(box, -1, _("Background color:")), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
		sizer6.Add(self.background, 1, wx.ALL | wx.EXPAND, 2)
		sizer5.Add(sizer6, 0, wx.ALL | wx.EXPAND, 5)
		if wx.VERSION_STRING < "2.9.1.0":
			box2 = wx.StaticBox(self, -1, _("Font Style"))
		sizer7 = wx.StaticBoxSizer(box2, wx.VERTICAL)
		if wx.VERSION_STRING < "2.9.1.0":
			box2 = self
		sizer7.Add(wx.StaticText(box2, -1, _("Font name:")), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
		sizer7.Add(self.fontname, 1, wx.ALL | wx.EXPAND, 2)
		sizer8 = wx.BoxSizer(wx.HORIZONTAL)
		sizer7.Add(wx.StaticText(box2, -1, _("Font size:")), 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
		sizer7.Add(self.fontsize, 1, wx.ALL | wx.EXPAND, 2)
		sizer7.Add(sizer8, 1, wx.ALL | wx.EXPAND, 2)
		sizer9 = wx.BoxSizer(wx.HORIZONTAL)
		sizer9.Add(self.bold, 0, wx.ALL | wx.EXPAND, 2)
		sizer9.Add(self.italic, 0, wx.ALL | wx.EXPAND, 2)
		sizer9.Add(self.underline, 0, wx.ALL | wx.EXPAND, 2)
		sizer9.Add(self.eol, 0, wx.ALL | wx.EXPAND, 2)
		sizer7.Add(sizer9, 1, wx.ALL | wx.EXPAND, 2)
		sizer5.Add(sizer7, 0, wx.ALL | wx.EXPAND, 5)
		sizer4.Add(sizer5, 0, wx.EXPAND)
		sizer2.Add(sizer4, 1, wx.EXPAND)
		sizer.Add(sizer2, 1, wx.EXPAND)
		sizer10 = wx.StdDialogButtonSizer()
		sizer10.AddButton(wx.Button(self, wx.ID_OK))
		sizer10.AddButton(wx.Button(self, wx.ID_CANCEL))
		sizer10.AddButton(wx.Button(self, wx.ID_APPLY))
		sizer10.Realize()
		sizer.Add(sizer10, 0, wx.ALL | wx.EXPAND, 5)
		self.SetSizer(sizer)
		
		for language in [_("Global Styles")] + names[1:]:
			if language == _("Global Styles"):
				lexer = "global"
			else:
				lexer = language.lower()
				if lexer in ("actionscript", "c#", "java", "javascript"):
					lexer = "cpp"
				elif lexer == "php":
					lexer = "html"
				elif lexer in styles:
					lexer = styles[lexer]
			self.lexers.Append(language, lexer)
		self.lexers.SetSelection(0)
		self.SetLexer("global")
		self.SetStyle("global", "default")
		
		self.themes.Bind(wx.EVT_CHOICE, self.OnTheme)
		self.lexers.Bind(wx.EVT_CHOICE, self.OnLexer)
		self.styles.Bind(wx.EVT_LISTBOX, self.OnStyle)
		self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)
		self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
		self.Bind(wx.EVT_BUTTON, self.OnApply, id=wx.ID_APPLY)
	
	def SetLexer(self, lexer):
		self.styles.Clear()
		self.styles.Append("Default", "default")
		styles2 = self._parent.styler.GetStylesInfo(lexer, False).keys()
		styles2.remove("default")
		styles2.sort()
		for style in styles2:
			if not style.startswith("_"):
				self.styles.Append(style.capitalize(), style)
		self.styles.SetSelection(0)
	
	def SetStyle(self, lexer, style):
		info = self._parent.styler.GetStylesInfo(lexer, False)
		if "fore" in info[style]:
			self.foreground.SetColour(info[style]["fore"])
		elif "fore" in info["default"]:
			self.foreground.SetColour(info["default"]["fore"])
		elif "fore" in self._parent.styler.cache["default"]:
			self.foreground.SetColour(self._parent.styler.cache["default"]["fore"])
		else:
			self.foreground.SetColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
		if "back" in info[style]:
			self.background.SetColour(info[style]["back"])
		elif "back" in info["default"]:
			self.background.SetColour(info["default"]["back"])
		elif "back" in self._parent.styler.cache["default"]:
			self.background.SetColour(self._parent.styler.cache["default"]["back"])
		else:
			self.background.SetColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
		if "face" in info[style]:
			self.fontname.SetSelection(self.fonts.index(info[style]["face"]))
		elif "face" in info["default"]:
			self.fontname.SetSelection(self.fonts.index(info["default"]["face"]))
		elif "face" in self._parent.styler.cache["default"]:
			self.fontname.SetSelection(self.fonts.index(self._parent.styler.cache["default"]["face"]))
		if "size" in info[style]:
			self.fontsize.SetValue(info[style]["size"])
		elif "size" in info["default"]:
			self.fontsize.SetValue(info["default"]["size"])
		elif "size" in self._parent.styler.cache["default"]:
			self.fontsize.SetValue(self._parent.styler.cache["default"]["size"])
		for modifier in ("bold", "italic", "underline", "eol"):
			getattr(self, modifier).SetValue(("modifiers" in info[style] and modifier in info[style]["modifiers"]) or \
				("modifiers" in info["default"] and modifier in info["default"]["modifiers"]) or \
				("modifiers" in self._parent.styler.cache["default"] and modifier in self._parent.styler.cache["default"]["modifiers"]))
	
	def OnTheme(self, event):
		enabled = event.GetString() != _("Default")
		self.toolbar.EnableTool(self.ID_RENAME, enabled)
		self.toolbar.EnableTool(wx.ID_DELETE, enabled)
	
	def OnLexer(self, event):
		data = event.GetClientData()
		self.SetLexer(data)
		self.SetStyle(data, "default")
	
	def OnStyle(self, event):
		self.SetStyle(self.lexers.GetClientData(self.lexers.GetSelection()), event.GetClientData())
	
	def OnOk(self, event):
		self.OnApply(event)
		self.Destroy()
	
	def OnCancel(self, event):
		self.Destroy()
	
	def OnApply(self, event):
		pass

names = ["Plain Text", "ActionScript", "Ada", "Assembly", "AutoIt", "Bash",
		 "Batch", "C", "C#", "C++", "C-Shell", "CAML", "CMakeFile", "CSS", "D",
		 "Diff", "Fortran", "Gui4Cli", "Haskell", "HTML", "Inno Setup", "Java",
		 "Javascript", "KiXtart", "Korn", "Lisp", "Lua", "Makefile", "MatLab",
		 "NSIS", "Pascal", "Perl", "PHP", "Postscript", "PowerShell",
		 "Properties", "Python", "Ruby", "Smalltalk", "SQL", "TeX", "Verilog",
		 "VHDL", "Visual Basic", "XML", "YAML"]
sizes = ["8", "9", "10", "11", "12", "14", "16", "18", "20", "22", "24", "26", "28", "36", "48", "72"]
styles = {"plain text":"null", "assembly":"asm", "autoit":"au3", "c":"cpp",
		  "c#":"csharp", "c++":"cpp", "c-shell":"bash", "cmakefile":"cmake",
		  "inno setup":"innosetup", "kixtart":"kix", "korn":"bash",
		  "postscript":"ps", "visual basic":"vb"}
"""
python.py - Python lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
NOTE: Parts of this file are based on code from SPE and PyShell
"""

import inspect
import re
from wx import VERSION_STRING

words = "and as assert break class continue def del elif else except exec False finally for from global if import in is lambda None not or pass print raise return True try while with yield"
words2 = ""

def OnInit(editor):
	editor.SetCodeFolding(True)
	editor.SetIndentationGuides(True)
	editor.SetKeyWords(0, words)
	editor.SetKeyWords(1, words2)
	editor.SetProperty("tab.timmy.whinge.level", "1")

def OnCharAdded(editor):
	pos = editor.GetCurrentPos()
	char = chr(editor.GetCharAt(pos - 1))
	if char in ".(":
		text = editor.GetTextRange(editor.PositionFromLine(editor.GetCurrentLine()), pos).strip().rstrip(".(")
		for i in range(len(text) - 1, -1, -1):
			if re.match(r'[^\w.]', text[i]):
				text = text[i + 1:]
				break
		autocomplete(editor, pos, text, int(char == "("))
	elif char == ")" and editor.CallTipActive():
		editor.CallTipCancel()

def autocomplete(editor, pos, text, mode):
	components = text.split(".")
	if not len(components[0]):
		return
	i = len(components)
	component = None
	while i > 0:
		try:
			component = __import__(".".join(components[:i]))
			break
		except:
			i -= 1
	try:
		if not component:
			component = eval(".".join(components))
			if hasattr(component, "__module__") and component.__module__ != "__builtin__":
				return
		else:
			while len(components) > 1:
				components.pop(0)
				component = getattr(component, components[0])
	except:
		return
	editor.Cancel()
	if mode == 0:
		autocomplist = dir(component)
		if len(autocomplist):
			autocomplist.sort()
			if inspect.isclass(component):
				uninherited = component.__dict__.keys()
				autocomplist = filter(lambda item: item not in uninherited, autocomplist)
				uninherited.sort()
				autocomplist = uninherited + autocomplist
			editor.AutoCompShow(0, " ".join(autocomplist))
	else:
		if inspect.isclass(component) and component.__module__ != "__builtin__":
			component = component.__init__	# Get the docstring from the '__init__' function
		try:
			doc = inspect.getdoc(component)
		except:
			doc = None
		try:
			argspec = inspect.formatargspec(*inspect.getargspec(component))
		except:
			try:
				argspec = inspect.formatargvalues(*inspect.getargvalues(component))
			except:
				if not doc:
					return
				argspec = ""
		name = getattr(component, "__name__", "")
		if len(argspec):
			argspec = re.sub(r'\((\s*)self\s*,\s*', r'(\1', argspec, 1)	# Remove the 'self' arg if it is present
			if mode == 1:
				editor.AddText(argspec[1:])
				editor.SetSelection(pos, pos + len(argspec) - 1)
			argspec = name + argspec
		if doc:
			if doc.lstrip().startswith(name + "("):
				argspec = ""
				doc = re.sub(r'\((\s*)self\s*,\s*', r'(\1', doc, 1)	# Remove the 'self' arg if it is present
			elif len(argspec):
				argspec += "\n\n"
		else:
			doc = ""
		editor.CallTipShow(pos, argspec + doc)

def OnNewLine(editor):
	line = editor.GetCurrentLine()
	if line > 0:
		previous = editor.GetLine(line - 1).strip()
		columns = editor.GetLineIndentation(line - 1)
		width = editor.GetIndent()
		if not editor.GetUseTabs():
			text = " " * columns
			if indent.search(previous):
				text += " " * width
			elif columns > 0 and dedent.match(previous):
				text = text[width:]
		else:
			spaces = columns % width
			columns /= width
			text = "\t" * columns
			if spaces > 0:
				text += " " * spaces
			if indent.search(previous):
				text += "\t"
			elif columns > 0 and dedent.match(previous):
				text = text[1:]
		if len(text):
			editor.AddText(text)

indent = re.compile(r':\s*(#.*)?$')
dedent = re.compile(r'\s*(break|continue|pass|raise|return)\b')

def OnDwellStart(editor, x, y):
	if VERSION_STRING < "2.9.0":
		return False
	pos = editor.CharPositionFromPointClose(x, y)
	if pos != -1:
		line = editor.LineFromPosition(pos)
		text = editor.GetLine(line).strip()
		for i in range(editor.GetColumn(pos) - editor.GetLineIndentation(line), -1, -1):
			try:
				if re.match(r'[^\w.]', text[i]):
					index = text.find("(", i + 1)
					if index != -1:
						autocomplete(editor, pos, text[i + 1:index], 2)
						return True
					else:
						break
			except IndexError:
				return False
	return False

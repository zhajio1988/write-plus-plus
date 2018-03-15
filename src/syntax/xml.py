"""
xml.py - XML lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

def OnInit(editor):
	editor.SetCodeFolding(False)
	editor.SetIndentationGuides(True)
	editor.SetProperty("tab.timmy.whinge.level", "0")

def OnCharAdded(editor):
	pass

def OnNewLine(editor):	
	line = editor.GetCurrentLine()
	if line > 0:
		columns = editor.GetLineIndentation(line - 1)
		if not editor.GetUseTabs():
			text = " " * columns
		else:
			width = editor.GetIndent()
			spaces = columns % width
			columns /= width
			text = "\t" * columns + " " * spaces
		if len(text):
			editor.AddText(text)
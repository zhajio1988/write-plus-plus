"""
gui4cli.py - Gui4Cli lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

globals_ = ""
events = ""
attributes = ""
controls = ""
commands = ""

def OnInit(editor):
	editor.SetCodeFolding(False)
	editor.SetIndentationGuides(False)
	editor.SetKeyWords(0, globals_)
	editor.SetKeyWords(1, events)
	editor.SetKeyWords(2, attributes)
	editor.SetKeyWords(3, controls)
	editor.SetKeyWords(4, commands)
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
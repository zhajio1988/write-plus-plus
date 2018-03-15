"""
matlab.py - MatLab lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

keywords = "break case catch continue else elseif end for function global if otherwise persistent return switch try while"

def OnInit(editor):
	editor.SetCodeFolding(False)
	editor.SetIndentationGuides(False)
	editor.SetKeyWords(0, keywords)
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
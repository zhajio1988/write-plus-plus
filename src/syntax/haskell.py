"""
haskell.py - Haskell lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

keywords = "_ as case class data default deriving do else hiding if import in infix infixl infixr instance let module newtype of proc qualified rec then type where"

def OnInit(editor):
	editor.SetCodeFolding(True)
	editor.SetIndentationGuides(True)
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
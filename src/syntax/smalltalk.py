"""
smalltalk.py - Smalltalk lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

spec_sel = "ifFalse: ifNil: ifNotNil: ifTrue: isNil notNil repeat whileFalse whileFalse: whileTrue whileTrue:"

def OnInit(editor):
	editor.SetCodeFolding(True)
	editor.SetIndentationGuides(True)
	editor.SetKeyWords(0, spec_sel)
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
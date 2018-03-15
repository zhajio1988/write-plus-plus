"""
caml.py - CAML lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

keywords = "and as assert asr begin class constraint do done downto else end exception external false for fun function functor if in include inherit initializer land lazy let lor lsl lsr lxor match method mod module mutable new object of open or private rec sig struct then to true try type val virtual when while with"
keywords2 = "ignore lnot None option pred ref Some succ"
keywords3 = "array bool char float int list string unit"

def OnInit(editor):
	editor.SetCodeFolding(False)
	editor.SetIndentationGuides(False)
	editor.SetKeyWords(0, keywords)
	editor.SetKeyWords(1, keywords2)
	editor.SetKeyWords(2, keywords3)
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
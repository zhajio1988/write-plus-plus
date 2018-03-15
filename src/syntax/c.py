"""
c.py - C lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

style = "cpp"
words = "if else switch case default break goto return for while do continue typedef sizeof NULL"
words2 = "void struct union enum char short int long double float signed unsigned const static extern auto register volatile"

def OnInit(editor):
	editor.SetCodeFolding(True)
	editor.SetIndentationGuides(True)
	editor.SetKeyWords(0, words)
	editor.SetKeyWords(1, words2)
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
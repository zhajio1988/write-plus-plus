"""
javascript.py - Javascript lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

style = "cpp"
words = "abstract boolean break byte case catch char class const continue debugger default delete do double else enum export extends final finally float for function false goto if implements import in instanceof int interface long native new package private protected public prototype return short static super switch synchronized this throw throws transient try typeof true var void volatile while with"

def OnInit(editor):
    editor.SetCodeFolding(False)
    editor.SetIndentationGuides(True)
    editor.SetKeyWords(0, words)
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

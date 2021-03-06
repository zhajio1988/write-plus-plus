"""
java.py - Java lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

style = "cpp"
words = "assert break case continue catch default do else extends for finally false goto instanceof if implements import new null return switch super throw throws try this true while"
words2 = "abstract byte boolean char const class double enum float final int interface long native package private protected public strictfp short static synchronized transient void volatile"

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

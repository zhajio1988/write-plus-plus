"""
batch.py - Batch lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
NOTE: Parts of this file are based on styles from Notepad++
"""

words = "break call com con copy chcp cd chdir choice cls cmdextversion country ctty date del defined dir do echo else erase errorlevel exist exit for goto in if loadfix loadhigh lpt md mkdir move not nul path pause prompt rd rem ren rename rmdir set shift time type ver verify vol"

def OnInit(editor):
    editor.SetCodeFolding(True)
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

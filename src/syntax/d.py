"""
d.py - D lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

words = "abstract alias align asm assert auto body bool break byte case cast catch cdouble cent cfloat char class const continue creal dchar debug default delegate delete deprecated do double else enum export extern false final finally float for foreach foreach_reverse function goto idouble if ifloat import in inout int interface invariant ireal is lazy long mixin module new null out override package pragma private protected public real return scope short static struct super switch synchronized template this throw true try typedef typeid typeof ubyte ucent uint ulong union unittest ushort version void volatile wchar while with"
words2 = ""
words3 = ""
words5 = ""
words6 = ""
words7 = ""

def OnInit(editor):
    editor.SetCodeFolding(False)
    editor.SetIndentationGuides(False)
    editor.SetKeyWords(0, words)
    editor.SetKeyWords(1, words2)
    editor.SetKeyWords(2, words3)
    editor.SetKeyWords(3, words5)
    editor.SetKeyWords(4, words6)
    editor.SetKeyWords(5, words7)
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

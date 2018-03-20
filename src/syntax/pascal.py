"""
pascal.py - Pascal lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

words = "and array asm begin case cdecl class const constructor default destructor div do downto else end end. except exit exports external far file finalization finally for function goto if implementation in index inherited initialization inline interface label library message mod near nil not object of on or out overload override packed pascal private procedure program property protected public published raise read record register repeat resourcestring safecall set shl shr stdcall stored string then threadvar to try type unit until uses var virtual while with write xor"

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

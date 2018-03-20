"""
vb.py - Visual Basic lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

from wx.stc import STC_B_KEYWORD, STC_CASE_MIXED

keywords = "addhandler addressof andalso alias and ansi as assembly attribute auto begin boolean byref byte byval call case catch cbool cbyte cchar cdate cdec cdbl char cint class clng cobj compare const continue cshort csng cstr ctype currency date decimal declare default delegate dim do double each else elseif end enum erase error event exit explicit false finally for friend function get gettype global gosub goto handles if implement implements imports in inherits integer interface is let lib like load long loop lset me mid mod module mustinherit mustoverride mybase myclass namespace new next not nothing notinheritable notoverridable object on option optional or orelse overloads overridable overrides paramarray preserve private property protected public raiseevent readonly redim rem removehandler rset resume return select set shadows shared short single static step stop string structure sub synclock then throw to true try type typeof unload unicode until variant wend when while with withevents writeonly xor"

def OnInit(editor):
    editor.SetCodeFolding(True)
    editor.SetIndentationGuides(True)
    editor.SetKeyWords(0, keywords)
    editor.SetKeyWords(1, "")
    editor.SetKeyWords(2, "")
    editor.SetKeyWords(3, "")
    editor.SetProperty("tab.timmy.whinge.level", "0")
    editor.StyleSetCase(STC_B_KEYWORD, STC_CASE_MIXED)

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


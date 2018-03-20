"""
lisp.py - Lisp lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

keywords = "* + - / < <= = > >= apply array aref append assoc atom and abs backquote boundp break baktrace bignums complement car cdr caar cadr cdar cddr caaar caadr cadar caddr cdaar cdadr cddar cdddr caaaar caaadr caadar caaddr cadaar cadadr caddar cadddr cdaaar cdaadr cdadar cdaddr cddaar cddadr cdddar cddddr cons consp cond case catch cerror continue cos defun defun defmacro delete do dolist dotimes eval evenp eq eql equal error errset evalhook expt exp funcall function float gensym get getf go hash identity intern if integer lambda list last length list length listp let l logand logior logxor lognot logeqv lognand lognor logorc2 logtest logbitp logcount length make make member mapc mapcar mapl maplist mapcan mapcon minusp min max not name nth nthcdr nsubst nsublis nconc numberp null nil oddp or princ plist putprop plusp prog prog1 prog2 progn quote remprop reverse remove rplaca rplacd return rem random set setq setf symbol symbol symbol symbol subst sublis symbolp sin sqrt throw truncate tan value zerop"
keywords_kw = ""

def OnInit(editor):
    editor.SetCodeFolding(True)
    editor.SetIndentationGuides(True)
    editor.SetKeyWords(0, keywords)
    editor.SetKeyWords(1, keywords_kw)
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

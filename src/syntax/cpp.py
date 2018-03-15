"""
cpp.py - C++ lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

words = "and and_eq bitand bitor break case catch compl const_cast continue default delete do dynamic_cast else false for gcnew goto if namespace new not not_eq NULL operator or or_eq reinterpret_cast return sizeof static_cast switch this throw true try typeid typedef using while xor xor_eq"
words2 = "asm auto bool char class const double enum explicit extern float friend inline int long mutable private protected public register short signed static struct template typename union unsigned virtual void volatile"
commentdockeywords = "a addindex addtogroup anchor arg attention author b brief bug c class code date def defgroup deprecated dontinclude e em endcode endhtmlonly endif endlatexonly endlink endverbatim enum example exception f$ f[ f] file fn hideinitializer htmlinclude htmlonly if image include ingroup internal invariant interface latexonly li line link mainpage name namespace nosubgrouping note overload p page par param post preref relates remarks return retval sa section see showinitializer since skip skipline struct subsection test throw throws todo typedef union until var verbatim verbinclude version warning weakgroup $ @ \ &amp; &lt; &gt; # { }"

def OnInit(editor):
	editor.SetCodeFolding(True)
	editor.SetIndentationGuides(True)
	editor.SetKeyWords(0, words)
	editor.SetKeyWords(1, words2)
	editor.SetKeyWords(2, commentdockeywords)
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
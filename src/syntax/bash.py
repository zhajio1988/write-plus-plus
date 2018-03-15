"""
bash.py - Bash lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

words = "alias ar asa awk banner basename bash bc bdiff break bunzip2 bzip2 cal calendar case cat cc cd chmod cksum clear cmp col comm compress continue cp cpio crypt csplit ctags cut date dc dd declare deroff dev df diff diff3 dircmp dirname do done du echo ed egrep elif else env esac eval ex exec exit expand export expr false fc fgrep fi file find fmt fold for function functions getconf getopt getopts grep gres hash head help history iconv id if in integer jobs join kill local lc let line ln logname look ls m4 mail mailx make man mkdir more mt mv newgrp nl nm nohup ntps od pack paste patch pathchk pax pcat perl pg pr print printf ps pwd read readonly red return rev rm rmdir sed select set sh shift size sleep sort spell split start stop strings strip stty sum suspend sync tail tar tee test then time times touch tr trap true tsort tty type typeset ulimit umask unalias uname uncompress unexpand uniq unpack unset until uudecode uuencode vi vim vpax wait wc whence which while who wpaste wstart xargs zcat"

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
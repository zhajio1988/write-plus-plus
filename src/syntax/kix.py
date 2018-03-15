"""
kix.py - KiXtart lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

keywords = "? and beep big break call cd cls color cookie1 copy case debug del dim display do exit each endfunction else endif endselect flushkb for function get gets global go gosub goto if loop md next or password play quit rd redim return run select set setl setm settime shell sleep small until use while"
macros = "abs addkey addprinterconnection addprogramgroup addprogramitem asc ascan at backupeventlog box cdbl chr cint cleareventlog close comparefiletimes createobject cstr dectohex delkey delprinterconnection delprogramgroup delprogramitem deltree delvalue dir enumgroup enumipinfo enumkey enumlocalgroup enumvalue execute exist existkey expandenvironmentvars fix formatnumber freefilehandle getdiskspace getfileattr getfilesize getfiletime getfileversion getobject iif ingroup instr instrrev int isdeclared join kbhit keyexist lcase left len loadhive loadkey logevent logoff ltrim memorysize messagebox open readline readprofilestring readtype readvalue redirectoutput right rnd round rtrim savekey sendkeys sendmessage setascii setconsole setdefaultprinter setfileattr setfocus setoption setsystemstate settitle setwallpaper showprogramgroup shutdown sidtoname split srnd substr trim ubound ucase unloadhive val vartype vartypename writeline writeprofilestring writevalue"
functions = "address build color comment cpu crlf csd curdir date day domain dos error fullname homedir homedrive homeshr hostname inwin ipaddress0 ipaddress1 ipaddress2 ipaddress3 kix lanroot ldomain ldrive lm logonmode longhomedir lserver maxpwage mdayno mhz monthno month msecs pid primarygroup priv productsuite producttype pwage ras result rserver scriptdir scriptexe scriptname serror sid site startdir syslang ticks time userid userlang wdayno wksta wuserid ydayno year"

def OnInit(editor):
	editor.SetCodeFolding(False)
	editor.SetIndentationGuides(False)
	editor.SetKeyWords(0, keywords)
	editor.SetKeyWords(1, macros)
	editor.SetKeyWords(2, functions)
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
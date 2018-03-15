"""
au3.py - AutoIt lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

functions = "abs acos adlibdisable adlibenable asc asin atan autoitsetoption autoitwingettitle autoitwinsettitle bitand bitnot bitor bitshift bitxor blockinput break call cdtray chr clipget clipput controlclick controlcommand controldisable controlenable controlfocus controlgetfocus controlgetpos controlgettext controlhide controlmove controlsend controlsettext controlshow cos dec dircopy dircreate dirmove dirremove drivegetdrive drivegetfilesystem drivegetlabel drivegetserial drivegettype drivesetlabel drivespacefree drivespacetotal drivestatus envget envset envupdate eval exp filechangedir fileclose filecopy filecreateshortcut filedelete fileexists filefindfirstfile filefindnextfile filegetattrib filegetlongname filegetshortname filegetsize filegettime filegetversion fileinstall filemove fileopen fileopendialog fileread filereadline filerecycle filerecycleempty filesavedialog fileselectfolder filesetattrib filesettime filewrite filewriteline guicreate guicreateex guidefaultfont guidelete guigetcontrolstate guihide guimsg guiread guirecvmsg guisendmsg guisetcontrol guisetcontroldata guisetcontrolex guisetcontrolfont guisetcontrolnotify guisetcoord guisetcursor guishow guiwaitclose guiwrite hex hotkeyset inidelete iniread iniwrite inputbox int isadmin isarray isdeclared isfloat isint isnumber isstring log memgetstats mod mouseclick mouseclickdrag mousedown mousegetcursor mousegetpos mousemove mouseup mousewheel msgbox number pixelchecksum pixelgetcolor pixelsearch processclose processexists processsetpriority processwait processwaitclose progressoff progresson progressset random regdelete regenumkey regenumval regread regwrite round run runasset runwait send seterror shutdown sin sleep soundplay soundsetwavevolume splashimageon splashoff splashtexton sqrt statusbargettext string stringaddcr stringformat stringinstr stringisalnum stringisalpha stringisascii stringisdigit stringisfloat stringisint stringislower stringisspace stringisupper stringisxdigit stringleft stringlen stringlower stringmid stringreplace stringright stringsplit stringstripcr stringstripws stringtrimleft stringtrimright stringupper tan timerstart timerstop tooltip traytip ubound urldownloadtofile winactivate winactive winclose winexists wingetcaretpos wingetclasslist wingetclientsize wingethandle wingetpos wingetstate wingettext wingettitle winkill winmenuselectitem winminimizeall winminimizeallundo winmove winsetontop winsetstate winsettitle winwait winwaitactive winwaitclose winwaitnotactive"
keywords = "and byref case continueloop dim do else elseif endfunc endif endselect exit exitloop exit for func global if local next not or return select step then to until wend while"
macros = "@appdatacommondir @appdatadir @autoitversion @commonfilesdir @compiled @computername @comspec @cr @crlf @desktopcommondir @desktopdir @desktopheight @desktopwidth @documentscommondir @error @favoritescommondir @favoritesdir @homedrive @homepath @homeshare @hour @ipaddress1 @ipaddress2 @ipaddress3 @ipaddress4 @lf @logondnsdomain @logondomain @logonserver @mday @min @mon @mydocumentsdir @osbuild @oslang @osservicepack @ostype @osversion @programfilesdir @programscommondir @programsdir @scriptdir @scriptfullpath @scriptname @sec @startmenucommondir @startmenudir @startupcommondir @startupdir @sw_hide @sw_maximize @sw_minimize @sw_restore @sw_show @systemdir @tab @tempdir @userprofiledir @username @wday @windowsdir @workingdir @yday @year"
sent = "{!} {#} {^} {{} {}} {+} {alt} {altdown} {altup} {appskey} {asc} {backspace} {browser_back} {browser_favorites} {browser_forward} {browser_home} {browser_refresh} {browser_search} {browser_stop} {bs} {capslock} {ctrlbreak} {ctrldown} {ctrlup} {del} {delete} {down} {end} {enter} {esc} {escape} {f1} {f10} {f11} {f12} {f2} {f3} {f4} {f5} {f6} {f7} {f8} {f9} {home} {ins} {insert} {lalt} {launch_app1} {launch_app2} {launch_mail} {launch_media} {lctrl} {left} {lshift} {lwin} {lwindown} {media_next} {media_play_pause} {media_prev} {media_stop} {numlock} {numpad0} {numpad1} {numpad2} {numpad3} {numpad4} {numpad5} {numpad6} {numpad7} {numpad8} {numpad9} {numpadadd} {numpaddiv} {numpaddot} {numpadenter} {numpadmult} {numpadsub} {pause} {pgdn} {pgup} {printscreen} {ralt} {rctrl} {right} {rshift} {rwin} {rwindown} {scrolllock} {shiftdown} {shiftup} {sleep} {space} {tab} {up} {volume_down} {volume_mute} {volume_up}"
preprocessors = "#include #include-once"
special = "#endregion #region"
expand = ""

def OnInit(editor):
	editor.SetCodeFolding(False)
	editor.SetIndentationGuides(False)
	editor.SetKeyWords(0, functions)
	editor.SetKeyWords(1, keywords)
	editor.SetKeyWords(2, macros)
	editor.SetKeyWords(3, sent)
	editor.SetKeyWords(4, preprocessors)
	editor.SetKeyWords(5, special)
	editor.SetKeyWords(6, expand)
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
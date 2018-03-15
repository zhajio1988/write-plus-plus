"""
innosetup.py - Inno Setup lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

from wx import stc

sections = "_istool code components custommessages dirs files icons ini installdelete langoptions languages messages registry run setup types tasks uninstalldelete uninstallrun"
keywords = "allowcancelduringinstall allownoicons allowrootdirectory allowuncpath alwaysrestart alwaysshowcomponentslist alwaysshowdironreadypage alwaysshowgrouponreadypage alwaysusepersonalgroup appcomments appcontact appcopyright appenddefaultdirname appenddefaultgroupname appid appmodifypath appmutex appname apppublisher apppublisherurl appreadmefile appsupporturl appupdatesurl appvername appversion architecturesallowed architecturesinstallin64bitmode backcolor backcolor2 backcolordirection backsolid changesassociations changesenvironment compression copyrightfontname copyrightfontsize createappdir createuninstallregkey defaultdirname defaultgroupname defaultuserinfoname defaultuserinfoorg defaultuserinfoserial dialogfontname dialogfontsize direxistswarning disabledirpage disablefinishedpage disableprogramgrouppage disablereadymemo disablereadypage disablestartupprompt diskclustersize diskslicesize diskspanning enablesdirdoesntexistwarning encryption extradiskspacerequired flatcomponentslist infoafterfile infobeforefile internalcompresslevel languagedetectionmethod languagecodepage languageid languagename licensefile lzmanumfastbytes mergeduplicatefiles minversion onlybelowversion outputbasefilename outputdir outputmanifestfile password privilegesrequired reservebytes restartifneededbyrun setupiconfile showcomponentsizes showlanguagedialog showtaskstreelines slicesperdisk solidcompression sourcedir timestamprounding timestampsinutc titlefontname titlefontsize touchdate touchtime uninstallable uninstalldisplayicon uninstalldisplayname uninstallfilesdir uninstalllogmode uninstallrestartcomputer updateuninstalllogappname usepreviousappdir usepreviousgroup useprevioussetuptype useprevioustasks useprevioususerinfo userinfopage usesetupldr versioninfocompany versioninfocopyright versioninfodescription versioninfotextversion versioninfoversion welcomefontname welcomefontsize windowshowcaption windowstartmaximized windowresizable windowvisible wizardimagebackcolor wizardimagefile wizardimagestretch wizardsmallimagefile"
parameters = "afterinstall attribs beforeinstall check comment components copymode description destdir destname excludes extradiskspacerequired filename flags fontinstall groupdescription hotkey infoafterfile infobeforefile iconfilename iconindex key languages licensefile messagesfile minversion name onlybelowversion parameters permissions root runonceid section source statusmsg string subkey tasks type types valuedata valuename valuetype workingdir"
preprocs = "append define dim else emit endif endsub error expr file for if ifdef ifexist ifndef ifnexist include insert pragma sub undef"
keywords_pascal = "begin break case const continue do downto else end except finally for function if of procedure repeat then to try until uses var while with"
keywords_user = ""

def OnInit(editor):
	editor.SetIndent(2)
	editor.SetUseTabs(False)
	editor.SetTabWidth(2)
	editor.SetCodeFolding(False)
	editor.SetIndentationGuides(True)
	editor.SetKeyWords(0, sections)
	editor.SetKeyWords(1, keywords)
	editor.SetKeyWords(2, parameters)
	editor.SetKeyWords(3, preprocs)
	editor.SetKeyWords(4, keywords_pascal)
	editor.SetKeyWords(5, keywords_user)
	editor.SetProperty("tab.timmy.whinge.level", "0")
	for style in (stc.STC_INNO_KEYWORD, stc.STC_INNO_KEYWORD_PASCAL, stc.STC_INNO_KEYWORD_USER, stc.STC_INNO_PARAMETER, stc.STC_INNO_PREPROC, stc.STC_INNO_SECTION):
		editor.StyleSetCase(style, stc.STC_CASE_MIXED)

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
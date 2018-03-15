"""
html.py - HTML lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

attributes = "!doctype a abbr accept accept-charset accesskey acronym action address align alink alt applet archive area article aside audio axis b background base basefont bdo bgcolor big blockquote body border br button canvas caption cellpadding cellspacing center char charoff charset checkbox checked cite class classid clear code codebase codetype col colgroup color cols colspan command compact content contenteditable contextmenu coords data datafld dataformatas datalist datapagesize datasrc datetime dd declare defer del details dfn dir disabled div dl draggable dropzone dt em embed enctype event face fieldset figcaption figure file font footer for form frame frameborder frameset h1 h2 h3 h4 h5 h6 head header height hgroup hidden hr href hreflang hspace html http-equiv i id iframe image img input ins isindex ismap kbd keygen label lang language leftmargin legend li link longdesc map marginheight marginwidth mark marquee maxlength media menu meta meter method multiple name nav noframes nohref noresize noscript noshade nowrap object ol onabort onafterprint onbeforeonload onbeforeprint onblur oncanplay oncanplaythrough onchange onclick oncontextmenu ondblclick ondrag ondragend ondragenter ondragleave ondragover ondragstart ondrop ondurationchange ondurationchange onemptied onended onerror onfocus onformchange onforminput onhaschange oninput oninvalid onkeydown onkeypress onkeyup onload onloadeddata onloadedmetadata onloadstart onmessage onmousedown onmousemove onmouseout onmouseover onmouseup onmousewheel onoffline ononline onpagehide onpageshow onpause onplay onplaying onpopstate onprogress onratechange onreadystatechange onredo onreset onresize onscroll onseeked onseeking onselect onselect onstalled onstorage onsubmit onsubmit onsuspend ontimeupdate onundo onunload onunload onvolumechange onwaiting optgroup option output p param password pre profile progress prompt public q radio readonly rel reset rev rows rowspan rp rt ruby rules s samp scheme scope script section select selected shape size small source span spellcheck src standby start strike strong style sub submit summary sup tabindex table target tbody td text textarea tfoot th thead time title topmargin tr tt type u ul usemap valign value valuetype var version video vlink vspace wbr width xml xmlns"

def OnInit(editor):
	editor.SetCodeFolding(False)
	editor.SetIndentationGuides(True)
	editor.SetKeyWords(0, attributes)
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
"""
ps.py - Postscript lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

keywords = "$error = == abs add aload anchorsearch and arc arcn arcto array ashow astore atan awidthshow begin bind bitshift bytesavailable cachestatus ceiling charpath clear cleardictstack cleartomark clip clippath closefile closepath concat concatmatrix copy copypage cos count countdictstack countexecstack counttomark currentcmykcolor currentcolorspace currentdash currentdict currentfile currentflat currentfont currentgray currenthsbcolor currentlinecap currentlinejoin currentlinewidth currentmatrix currentmiterlimit currentpagedevice currentpoint currentrgbcolor currentscreen currenttransfer cvi cvlit cvn cvr cvrs cvs cvx def defaultmatrix definefont dict dictstack div dtransform dup echo end eoclip eofill eq erasepage errordict exch exec execstack executeonly executive exit exp FontDirectory false file fill findfont flattenpath floor flush flushfile for forall ge get getinterval grestore grestoreall gsave gt idetmatrix idiv idtransform if ifelse image imagemask index initclip initgraphics initmatrix inustroke invertmatrix itransform known kshow le length lineto ln load log loop lt makefont mark matrix maxlength mod moveto mul ne neg newpath noaccess nor not null nulldevice or pathbbox pathforall pop print prompt pstack put putinterval quit rand rcheck rcurveto read readhexstring readline readonly readstring rectstroke repeat resetfile restore reversepath rlineto rmoveto roll rotate round rrand run StandardEncoding save scale scalefont search setblackgeneration setcachedevice setcachelimit setcharwidth setcolorscreen setcolortransfer setdash setflat setfont setgray sethsbcolor setlinecap setlinejoin setlinewidth setmatrix setmiterlimit setpagedevice setrgbcolor setscreen settransfer setvmthreshold show showpage sin sqrt srand stack start status statusdict stop stopped store string stringwidth stroke strokepath sub systemdict token token transform translate true truncate type UserObjects ueofill undefineresource userdict usertime version vmstatus wcheck where widthshow write writehexstring writestring xcheck xor"
keywords2 = "GlobalFontDirectory ISOLatin1Encoding SharedFontDirectory UserObject arct colorimage cshow currentblackgeneration currentcacheparams currentcmykcolor currentcolor currentcolorrendering currentcolorscreen currentcolorspace currentcolortransfer currentdevparams currentglobal currentgstate currenthalftone currentobjectformat currentoverprint currentpacking currentpagedevice currentshared currentstrokeadjust currentsystemparams currentundercolorremoval currentuserparams defineresource defineuserobject deletefile execform execuserobject filenameforall fileposition filter findencoding findresource gcheck globaldict glyphshow gstate ineofill infill instroke inueofill inufill inustroke languagelevel makepattern packedarray printobject product realtime rectclip rectfill rectstroke renamefile resourceforall resourcestatus revision rootfont scheck selectfont serialnumber setbbox setblackgeneration setcachedevice2 setcacheparams setcmykcolor setcolor setcolorrendering setcolorscreen setcolorspace setcolortranfer setdevparams setfileposition setglobal setgstate sethalftone setobjectformat setoverprint setpacking setpagedevice setpattern setshared setstrokeadjust setsystemparams setucacheparams setundercolorremoval setuserparams setvmthreshold shareddict startjob uappend ucache ucachestatus ueofill ufill undef undefinefont undefineresource undefineuserobject upath ustroke ustrokepath vmreclaim writeobject xshow xyshow yshow"
keywords3 = "cliprestore clipsave composefont currentsmoothness findcolorrendering setsmoothness shfill"
keywords4 = ".begintransparencygroup .begintransparencymask .bytestring .charboxpath .currentaccuratecurves .currentblendmode .currentcurvejoin .currentdashadapt .currentdotlength .currentfilladjust2 .currentlimitclamp .currentopacityalpha .currentoverprintmode .currentrasterop .currentshapealpha .currentsourcetransparent .currenttextknockout .currenttexturetransparent .dashpath .dicttomark .discardtransparencygroup .discardtransparencymask .endtransparencygroup .endtransparencymask .execn .filename .filename .fileposition .forceput .forceundef .forgetsave .getbitsrect .getdevice .inittransparencymask .knownget .locksafe .makeoperator .namestring .oserrno .oserrorstring .peekstring .rectappend .runandhide .setaccuratecurves .setblendmode .setcurvejoin .setdashadapt .setdebug .setdefaultmatrix .setdotlength .setfilladjust2 .setlimitclamp .setmaxlength .setopacityalpha .setoverprintmode .setrasterop .setsafe .setshapealpha .setsourcetransparent .settextknockout .settexturetransparent .stringbreak .stringmatch .tempfile .type1decrypt .type1encrypt .type1execchar .unread arccos arcsin copydevice copyscanlines currentdevice finddevice findlibfile findprotodevice flushpage getdeviceprops getenv makeimagedevice makewordimagedevice max min putdeviceprops setdevice"

def OnInit(editor):
    editor.SetCodeFolding(False)
    editor.SetIndentationGuides(False)
    editor.SetKeyWords(0, keywords)
    editor.SetKeyWords(1, keywords2)
    editor.SetKeyWords(2, keywords3)
    editor.SetKeyWords(3, keywords4)
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

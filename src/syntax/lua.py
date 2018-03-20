"""
lua.py - Lua lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

words = "and break do else elseif end false for function if in local nil not or repeat return then true until while"
words2 = "_VERSION _ALERT _ERRORMESSAGE _INPUT _PROMPT _OUTPUT _STDERR _STDIN _STDOUT _G assert collectgarbage call coroutine dofile dostring debug error foreach foreachi gcinfo getn globals getfenv getmetatable ipairs io loadfile loadstring loadlib math newtype next os print pairs pcall rawget rawset require rawegal rawget rawset require sort setfenv setmetatable string tonumber tostring type tinsert tremove table unpack xpcall"
words3 = "abs acos asin atan atan2 ceil cos deg exp floor format frexp gsub ldexp log log10 max min mod math.abs math.acos math.asin math.atan math.atan2 math.ceil math.cos math.deg math.exp math.floor math.frexp math.ldexp math.log math.log10 math.max math.min math.mod math.pi math.rad math.random math.randomseed math.sin math.sqrt math.tan rad random randomseed sin sqrt strbyte strchar strfind strlen strlower strrep strsub strupper string.byte string.char string.dump string.find string.len string.lower string.rep string.sub string.upper string.format string.gfind string.gsub tan table.concat table.foreach table.foreachi table.getn table.sort table.insert table.remove table.setn"
words4 = "appendto closefile clock coroutine.create coroutine.resume coroutine.status coroutine.wrap coroutine.yield date difftime execute exit flush getenv io.close io.flush io.input io.lines io.open io.output io.read io.tmpfile io.type io.write io.stdin io.stdout io.stderr openfile os.clock os.date os.difftime os.execute os.exit os.getenv os.remove os.rename os.setlocale os.time os.tmpname readfrom remove rename read seek setlocale tmpfile tmpname time writeto write"

def OnInit(editor):
    editor.SetCodeFolding(True)
    editor.SetIndentationGuides(True)
    editor.SetKeyWords(0, words)
    editor.SetKeyWords(1, words2)
    editor.SetKeyWords(2, words3)
    editor.SetKeyWords(3, words4)
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

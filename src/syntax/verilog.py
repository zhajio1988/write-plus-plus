"""
verilog.py - Verilog lexer script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>
"""

words = "always and assign attribute begin buf bufif0 bufif1 case casex casez cmos deassign default defparam disable edge else end endattribute endcase endfunction endmodule endprimitive endspecify endtable endtask event for force forever fork function highz0 highz1 if ifnone initial inout input integer join large localparam medium module macromodule nand negedge nmos nor not notif0 notif1 or output parameter pmos posedge primitive pull0 pull1 pulldown pullup rcmos real realtime reg release repeat rnmos rpmos rtran rtranif0 rtranif1 scalared signed small specify specparam strength strong0 strong1 supply0 supply1 table task time tran tranif0 tranif1 tri tri0 tri1 triand trior trireg unsigned vectored wait wand weak0 weak1 while wire wor xnor xor"
words2 = "$bitstoreal $countdrivers $display $dumpall $dumpfile $dumpflush $dumplimit $dumpoff $dumpon $dumpvars $fclose $fdisplay $finish $fmonitor $fopen $fstrobe $fwrite $getpattern $hold $incsave $input $itor $key $list $log $monitor $monitoroff $monitoron $nokey $nolog $period $printtimescale $random $readmemb $readmemh $realtime $realtobits $recovery $reset $restart $rtoi $save $scale $scope $setup $setuphold $showscopes $showvars $skew $sreadmemb $sreadmemh $stime $stop $strobe $time $timeformat $width $write"
words3 = ""

def OnInit(editor):
	editor.SetIndent(2)
	editor.SetUseTabs(False)
	editor.SetTabWidth(2)
	editor.SetCodeFolding(False)
	editor.SetIndentationGuides(False)
	editor.SetKeyWords(0, words)
	editor.SetKeyWords(1, words2)
	editor.SetKeyWords(2, words3)
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
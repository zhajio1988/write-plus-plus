"""
powershell.py - PowerShell lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

keywords = "break continue do else elseif filter for foreach function if in return switch until where while"
cmdlets = "add-content add-history add-member add-pssnapin clear-content clear-item clear-itemproperty clear-variable compare-object convertfrom-securestring convert-path convertto-html convertto-securestring copy-item copy-itemproperty export-alias export-clixml export-console export-csv foreach-object format-custom format-list format-table format-wide get-acl get-alias get-authenticodesignature get-childitem get-command get-content get-credential get-culture get-date get-eventlog get-executionpolicy get-help get-history get-host get-item get-itemproperty get-location get-member get-pfxcertificate get-process get-psdrive get-psprovider get-pssnapin get-service get-tracesource get-uiculture get-unique get-variable get-wmiobject group-object import-alias import-clixml import-csv invoke-expression invoke-history invoke-item join-path measure-command measure-object move-item move-itemproperty new-alias new-item new-itemproperty new-object new-psdrive new-service new-timespan new-variable out-default out-file out-host out-null out-printer out-string pop-location push-location read-host remove-item remove-itemproperty remove-psdrive remove-pssnapin remove-variable rename-item rename-itemproperty resolve-path restart-service resume-service select-object select-string set-acl set-alias set-authenticodesignature set-content set-date set-executionpolicy set-item set-itemproperty set-location set-psdebug set-service set-tracesource set-variable sort-object split-path start-service start-sleep start-transcript stop-process stop-service stop-transcript suspend-service tee-object test-path trace-command update-formatdata update-typedata where-object write-debug write-error write-host write-output write-progress write-verbose write-warning"
aliases = "ac asnp clc cli clp clv cpi cpp cvpa cat cd clear cp cls chdir copy diff del dir epal epcsv echo erase fc fl foreach ft fw gal gc gci gcm gdr ghy gi gl gm gp gps group gsv gsnp gu gv gwmi h history iex ihy ii ipal ipcsv kill lp ls mi mp mount mv move nal ndr ni nv oh popd ps pushd pwd rdr ri rni rnp rp rsnp rv rvpa r rm rmdir rd ren sal sasv sc select si sl sleep sort sp spps spsv sv set tee type where write"

def OnInit(editor):
    editor.SetCodeFolding(True)
    editor.SetIndentationGuides(True)
    editor.SetKeyWords(0, keywords)
    editor.SetKeyWords(1, cmdlets)
    editor.SetKeyWords(2, aliases)
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

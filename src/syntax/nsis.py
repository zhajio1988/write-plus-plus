"""
nsis.py - NSIS lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

functions = "!AddIncludeDir !AddPluginDir !appendfile !cd !define !delfile !echo !else !endif !error !execute !ifdef !ifmacrodef !ifmacrondef !ifndef !include !insertmacro !macro !macroend !packhdr !system !tempfile !undef !verbose !warning Abort AddBrandingImage AddSize AllowRootDirInstall AllowSkipFiles AutoCloseWindow BGFont BGGradient BrandingText BringToFront CRCCheck Call CallInstDLL Caption ChangeUI CheckBitmap ClearErrors CompletedText ComponentText CopyFiles CreateDirectory CreateFont CreateShortCut Delete DeleteINISec DeleteINIStr DeleteRegKey DeleteRegValue DetailPrint DetailsButtonText DirShow DirText DirVar DirVerify DisabledBitmap EnableWindow EnabledBitmap EnumRegKey EnumRegValue Exch Exec ExecShell ExecWait ExpandEnvStrings File FileBufSize FileClose FileErrorText FileOpen FileRead FileReadByte FileSeek FileWrite FileWriteByte FindClose FindFirst FindNext FindWindow FlushINI Function FunctionEnd GetCurInstType GetCurrentAddress GetDLLVersion GetDLLVersionLocal GetDlgItem GetErrorLevel GetFileTime GetFileTimeLocal GetFullPathName GetFunctionAddress GetInstDirError GetLabelAddress GetTempFileName Goto HideWindow Icon IfAbort IfErrors IfFileExists IfRebootFlag IfSilent InitPluginsDir InstProgressFlags InstType InstTypeGetText InstTypeSetText InstallButtonText InstallColors InstallDir InstallDirRegKey IntCmp IntCmpU IntFmt IntOp IsWindow LangString LangStringUP LicenseBkColor LicenseData LicenseForceSelection LicenseLangString LicenseText LoadLanguageFile LockWindow LogSet LogText MessageBox MiscButtonText Name OutFile Page PageEx PageExEnd PluginDir Pop Push Quit RMDir ReadEnvStr ReadINIStr ReadRegDWORD ReadRegStr Reboot RegDLL Rename RequestExecutionLevel ReserveFile Return SearchPath Section SectionDivider SectionEnd SectionGetFlags SectionGetInstTypes SectionGetSize SectionGetText SectionGroup SectionGroupEnd SectionIn SectionSetFlags SectionSetInstTypes SectionSetSize SectionSetText SendMessage SetAutoClose SetBrandingImage SetCompress SetCompressionLevel SetCompressor SetCompressorDictSize SetCtlColors SetCurInstType SetDatablockOptimize SetDateSave SetDetailsPrint SetDetailsView SetErrorLevel SetErrors SetFileAttributes SetFont SetOutPath SetOverwrite SetPluginUnload SetRebootFlag SetShellVarContext SetSilent SetStaticBkColor ShowInstDetails ShowUninstDetails ShowWindow SilentInstall SilentUnInstall Sleep SpaceTexts StrCmp StrCmpS StrCpy StrLen SubSection SubSectionEnd UnRegDLL UninstPage UninstallButtonText UninstallCaption UninstallEXEName UninstallIcon UninstallSubCaption UninstallText VIAddVersionKey VIProductVersion Var WindowIcon WriteINIStr WriteRegBin WriteRegDWORD WriteRegExpandStr WriteRegStr WriteUninstaller XPStyle"
variables = "$0 $1 $2 $3 $4 $5 $6 $7 $8 $9 $APPDATA $CMDLINE $DESKTOP $EXEDIR $HWNDPARENT $INSTDIR $OUTDIR $PROGRAMFILES $QUICKLAUNCH $R0 $R1 $R2 $R3 $R4 $R5 $R6 $R7 $R8 $R9 $SMPROGRAMS $SMSTARTUP $STARTMENU $SYSDIR $TEMP $WINDIR $\\n $\\r ${NSISDIR}"
labels = "ARCHIVE CUR END FILE_ATTRIBUTE_ARCHIVE FILE_ATTRIBUTE_HIDDEN FILE_ATTRIBUTE_NORMAL FILE_ATTRIBUTE_OFFLINE FILE_ATTRIBUTE_READONLY FILE_ATTRIBUTE_SYSTEM FILE_ATTRIBUTE_TEMPORARY HIDDEN HKCC HKCR HKCU HKDD HKEY_CLASSES_ROOT HKEY_CURRENT_CONFIG HKEY_CURRENT_USER HKEY_DYN_DATA HKEY_LOCAL_MACHINE HKEY_PERFORMANCE_DATA HKEY_USERS HKLM HKPD HKU IDABORT IDCANCEL IDIGNORE IDNO IDOK IDRETRY IDYES MB_ABORTRETRYIGNORE MB_DEFBUTTON1 MB_DEFBUTTON2 MB_DEFBUTTON3 MB_DEFBUTTON4 MB_ICONEXCLAMATION MB_ICONINFORMATION MB_ICONQUESTION MB_ICONSTOP MB_OK MB_OKCANCEL MB_RETRYCANCEL MB_RIGHT MB_SETFOREGROUND MB_TOPMOST MB_USERICON MB_YESNO MB_YESNOCANCEL NORMAL OFFLINE READONLY SET SHCTX SW_HIDE SW_SHOWMAXIMIZED SW_SHOWMINIMIZED SW_SHOWNORMAL SYSTEM TEMPORARY all auto both bottom bzip2 checkbox colored current false force hide ifdiff ifnewer lastused leave left listonly lzma nevershow none normal off on pop push radiobuttons right show silent silentlog smooth textonly top true try zlib"

def OnInit(editor):
    editor.SetIndent(2)
    editor.SetUseTabs(False)
    editor.SetTabWidth(2)
    editor.SetCodeFolding(False)
    editor.SetIndentationGuides(True)
    editor.SetKeyWords(0, functions)
    editor.SetKeyWords(1, variables)
    editor.SetKeyWords(2, labels)
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

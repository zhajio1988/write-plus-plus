"""
actionscript.py - ActionScript lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

style = "cpp"
words = "add and break continue case delete do default else eq for function ge gt if ifFrameLoaded in instanceof lt le ne new not on onClipEvent or return switch tellTarget this typeof var void while with"
words2 = "__proto__ _accProps _alpha _currentframe _droptarget _focusrect _framesloaded _global _height _highquality _level _lockroot _name _parent _quality _root _rotation _soundbuftime _target _totalframes _url _visible _width _x _xmouse _xscale _y _ymouse _yscale arguments Accessibility Arguments Array abs acos asin atan atan2 addListener addPage addProperty addRequestHeader allowDomain allowInsecureDomain appendChild apply applyChanges asfunction attachAudio attachMovie attachSound attachVideo activityLevel align allowDomain allowInsecureDomain attributes autoSize avHardwareDisable Boolean Button beginFill beginGradientFill background backgroundColor bandwidth blockIndent bold border borderColor bottomScroll bufferLenght bufferTime builtInItems bullet bytesLoaded bytesTotal constructor class Camera ContextMenu ContextMenuItem CustomActions Color ceil cos call ceil charAt charCodeAt clear clearInterval cloneNode close concat connect copy cos createElement createEmptyMovieClip createTextField createTextNode curveTo callee caller capabilities caption childNodes color condenseWhite contentType currentFps customItems dynamic Date domain duplicateMovieClip data deblocking docTypeDecl duration extends Error exp endFill escape eval evaluate exp endinitclip embedFonts enabled exactSettings false Function floor findText floor fscommand flush fromCharCode firstChild focusEnabled font fps get getAscii getBeginIndex getBounds getBytesLoaded getBytesTotal getCaretIndex getCode getCount getDate getDay getDepth getEndIndex getFocus getFontList getFullYear getHours getInstanceAtDepth getLocal getMilliseconds getMinutes getMonth getNewTextFormat getNextHighestDepth getPan getProggress getProperty getRGB getSeconds getSelected getSelectedText getSize getStyle getStyleNames getSWFVersion getText getTextExtent getTextFormat getTextSnapshot getTime getTimer getTimezoneOffset getTransform getURL getUTCDate getUTCDay getUTCFullYear getUTCHours getUTCMilliseconds getUTCMinutes getUTCMonth getUTCSeconds getVersion getVolume getYear globalToLocal gotoAndPlay gotoAndStop gain globalStyleFormat hasChildNodes hide hideBuiltInItems hitTest hitTestTextNearPos hasAccessibility hasAudio hasAudioEncoder hasEmbeddedVideo hasMP3 hasPrinting hasScreenBroadcast hasScreenPlayback hasStreamingAudio hasStreamingVideo hasVideoEncoder height hitArea hscroll html htmlText implements import interface intrinsic indexOf insertBefore install isActive isDown isToggled include initclip indent index italic instanceof int ignoreWhite isDebugger isDown isFinite italic join Key LoadVars LocalConnection log lastIndexOf lineStyle lineTo list load loadClip loadMovie loadMovieNum loadSound loadVariables loadVariablesNum localToGlobal log language lastChild leading leftMargin length loaded localFileReadDisable Math Microphone Mouse MovieClip MovieClipLoader max min mbchr mblength mbord mbsubstring min MMExecute moveTo manufacturer maxChars maxhscroll maxscroll menu message motionLevel motionTimeout mouseWheelEnabled multiline muted newline null NetConnection NetStream Number nextFrame nextScene name names NaN nextSibling nodeName nodeType nodeValue Object onActivity onChanged onClose onConnect onData onDragOut onDragOver onEnterFrame onID3 onKeyDown onKeyUp onKillFocus onLoad onLoadComplete onLoadError onLoadInit onLoadProgress onLoadStart onMouseDown onMouseMove onMouseUp onMouseWheel onPress onRelease onReleaseOutside onResize onRollOut onRollOver onScroller onSelect onSetFocus onSoundComplete onStatus onUnload onUpdate onXML os private public PrintJob pow parseCSS parseFloat parseInt parseXML pause play pop pow prevScene print printAsBitmap printAsBitmapNum printNum push parentNode password pixelAspectRatio playerType previousSibling prototype quality random round random registerClass removeListener removeMovieClip removeNode removeTextField replaceSel replaceText reverse round rate restrict resolutionX resolutionY rightMargin super static StyleSheet SharedObject Selection Sound Stage String System sin sqrt seek send sendAndLoad setBufferTime set setDate setFocus setFullYear setGain setHours setInterval setMask setMilliseconds setMinutes setMode setMonth setMotionLevel setNewTextFormat setPan setProperty setQuality setRate setRGB setSeconds setSelectColor setSelected setSelection setSilenceLevel setStyle setTextFormat setTime setTransform setUseEchoSuppression setUTCDate setUTCFullYear setUTCHours setUTCMilliseconds setUTCMinutes setUTCMonth setUTCSeconds setVolume setYear shift show showSettings silenceLevel silenceTimeout sin slice sort sortOn splice split sqrt start startDrag stop stopAllSounds stopDrag substr substring swapDepths scaleMode screenColor screenDPI screenResolutionX screenResolutionY scroll selectable separatorBefore showMenu size smoothing status styleSheet true TextField TextFormat TextSnapshot tan tan toggleHighQuality toLowerCase toString toUpperCase trace tabChildren tabEnabled tabIndex tabStops target targetPath text textColor textHeight textWidth time trackAsMenu type undefined unescape uninstall unLoadClip unloadMovie unloadMovieNum unshift unwatch updateAfterEvent updateProperties useEchoSuppression underline url useCodepage useEchoSuppression useHandCursor Void valueOf variable version visible watch width wordWrap XML XMLNode XMLSocket xmlDecl"

def OnInit(editor):
    editor.SetCodeFolding(False)
    editor.SetIndentationGuides(True)
    editor.SetKeyWords(0, words)
    editor.SetKeyWords(1, words2)
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

"""
search.py - search system for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
NOTE: Parts of this file are based on code from Editra
"""

import fnmatch
import os
import unicodedata
import wx

from dialogs import search

_ = wx.GetTranslation

class SearchSystem:
    def __init__(self, frame):
        self._frame = frame

        self.lastfindall = None
        self.pattern = None
        self.pdialog = None
        self.span = None
        self.startpos = -1
        self.text = None
        self.wrap = True

    def CalculateSpan(self, dialog):
        if dialog.lookin.GetSelection() == 1:
            self.span = self._frame.editor.GetSelection()
        else:
            self.span = None
        return self.span

    def Find(self, pattern, span=None, editor=None, forward=True, wrap=True):
        if not editor:
            editor = self._frame.editor
        text = self.GetTextRange(span, editor, forward)
        match = pattern.search(text)
        start = self.startpos
        if not forward:
            previous = match
            while previous:
                match = previous
                previous = pattern.search(text, start + match.end(0))
        if match:
            return (start + match.start(0), start + match.end(0), not wrap)
        elif wrap:
            span = self.span
            if not span:
                span = (0, editor.GetTextLength())
            return self.Find(pattern, span, editor, forward, False) # The wrap parameter avoids infinite loops
        return (-1, -1, self.wrap and not wrap)

    def GetTextRange(self, span=None, editor=None, forward=True):
        if not editor:
            editor = self._frame.editor
        if not span:
            if forward:
                span = (editor.GetCurrentPos(), editor.GetTextLength())
            elif editor.HasSelection():
                span = (0, editor.GetSelectionStart())
            else:
                span = (0, editor.GetCurrentPos())
        self.startpos = span[0]
        if not editor.raw:
            text = editor.GetTextRange(*span)
        else:
            text = editor.GetStyledText(*span)[0:(span[1] - span[0]) * 2:2]
        return unicodedata.normalize('NFKD', text)

    def FindNext(self, pattern=None, span=None, text=None):
        if pattern:
            self.pattern = pattern
        elif not self.pattern:
            self._frame.searchbar.Search(True)
            return
        if text:
            self.text = text
        start, end, wrapped = self.Find(self.pattern, self.span)
        if start != -1:
            self._frame.editor.EnsureVisible(self._frame.editor.LineFromPosition(start))
            self._frame.editor.SetSelection(start, end)
            self._frame.editor.EnsureCaretVisible()
            if wrapped:
                self._frame.statusbar.SetStatusText(_("Wrapped around"), 0)
            else:
                self._frame.statusbar.SetStatusText(_("Found '%s'") % self.text, 0)
        else:
            wx.MessageBox(_("Could not find '%s'.") % self.text, _("Find"), wx.ICON_EXCLAMATION | wx.OK)

    def FindPrevious(self):
        if not self.pattern:
            self._frame.searchbar.Search(False)
            return
        start, end, wrapped = self.Find(self.pattern, self.span, forward=False)
        if start != -1:
            self._frame.editor.EnsureVisible(self._frame.editor.LineFromPosition(start))
            self._frame.editor.SetSelection(start, end)
            self._frame.editor.EnsureCaretVisible()
            if wrapped:
                self._frame.statusbar.SetStatusText(_("Wrapped around"), 0)
            else:
                self._frame.statusbar.SetStatusText(_("Found '%s'") % self.text, 0)
        else:
            wx.MessageBox(_("Could not find '%s'.") % self.text, _("Find"), wx.ICON_EXCLAMATION | wx.OK)

    def FindAll(self, pattern, lookin, directory, filterstr, exclude, include, text):
        filenames = self.GetFilenames(lookin, filterstr, exclude, include, directory)
        self.pdialog = wx.ProgressDialog(_("Searching"), "", len(filenames), style=wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)
        results = []
        for i in range(len(filenames)):
            if lookin < 3:
                filename = os.path.basename(filenames[i])
            else:
                filename = os.path.relpath(filenames[i], directory)
            if not self.pdialog.Update(i, _("Searching in '%s'...") % filename)[0]:
                return None
            tab = -1
            for j in range(self._frame.notebook.GetPageCount()):
                if self._frame.GetEditor(j).filename == filenames[i]:
                    tab = j
                    break
            if tab != -1:
                results.append((filenames[i], []))
                editor = self._frame.GetEditor(tab)
                if lookin == 1:
                    span = editor.GetSelection()
                else:
                    span = (0, editor.GetTextLength())
                start, end, dummy = self.Find(pattern, span, editor, wrap=False)
                previous = -1
                while start != -1:
                    line = editor.LineFromPosition(start)
                    start2, end2 = start, end
                    start, end, dummy = self.Find(pattern, (end + 1, span[1]), editor, wrap=False)
                    next = editor.LineFromPosition(start)
                    if line == next and line != previous:   # First of multiple matches on line
                        span2 = (editor.PositionFromLine(line), start)
                    elif line == previous and line == next: # Between first and last of multiple matches on line
                        span2 = (start2, start)
                    elif line == previous and line != next: # Last of multiple matches on line
                        span2 = (start2, editor.GetLineEndPosition(line))
                    else:
                        span2 = (editor.PositionFromLine(line), editor.GetLineEndPosition(line))
                    if not editor.raw:
                        text = editor.GetTextRange(*span2)
                    else:
                        text = editor.GetStyledText(*span2)[0:(span2[1] - span2[0]) * 2:2]
                    results[-1][1].append((line, text, start2, end2))
                    previous = line
            else:
                results.append((filenames[i], self.FindInFile(filenames[i], pattern)))
        if not self.pdialog.Update(i, _("Please wait, loading results..."))[0]:
            return None
        self.lastfindall = (pattern, lookin, directory, filterstr, exclude, include, text)
        self.pattern = pattern
        self.text = text
        return results

    def GetFilenames(self, lookin, filterstr, exclude, include, directory):
        if lookin < 2:
            return [self._frame.GetEditor().filename]
        if len(filterstr):
            filters = filterstr.split(";")
        else:
            filters = []
        if lookin == 2:
            filenames = []
            for i in range(self._frame.notebook.GetPageCount()):
                editor = self._frame.GetEditor(i)
                if len(filters) and (True in [fnmatch.fnmatch(editor.filename, filterstr) for filterstr in filters]) == exclude:
                    continue
                if (not include) and not editor.changes:
                    continue
                filenames.append(editor.filename)
        else:
            filenames = []
            for path, dirs, files in os.walk(directory):
                for filename in files:
                    if len(filters) and (True in [fnmatch.fnmatch(filename, filterstr) for filterstr in filters]) == exclude:
                        continue
                    filenames.append(os.path.join(path, filename))
                if not include:
                    break
        return filenames

    def FindInFile(self, filename, pattern):
        fileobj = open(filename, 'rb')
        text = fileobj.readlines()
        fileobj.close()
        if not len(text):
            return []
        results = []
        pos = 0
        for i in range(len(text)):
            match = pattern.search(text[i])
            matches = 0
            while match:
                start = match.start(0)
                end = match.end(0)
                match = pattern.search(text[i], end + 1)
                if matches == 0 and match:  # First of multiple matches on line
                    line = text[i][:match.start(0)]
                elif matches > 0 and match: # Between first and last of multiple matches on line
                    line = text[i][start:match.start(0)]
                elif matches > 0:   # Last of multiple matches on line
                    line = text[i][start:]
                else:   # Single match on line
                    line = text[i]
                results.append((i, unicode(line, errors='replace').replace(u'\0', u'\ufffd'), pos + start, pos + end))
                matches += 1
            pos += len(text[i])
        return results

    def QuickFind(self):
        searchbar = self._frame.aui.GetPane("searchbar")
        if not searchbar.IsShown():
            searchbar.Show()
            self._frame.aui.Update()
        self._frame.searchbar.find.SelectAll()
        self.pattern = None
        wx.CallAfter(self._frame.searchbar.find.SetFocus)

    def ShowSearchDialog(self, find=True, lookin=-1):
        dialog = search.SearchDialog(self._frame, find, lookin)
        dialog.Show()
        if find:
            dialog.OnShowFind(None)
        else:
            dialog.OnShowReplace(None)

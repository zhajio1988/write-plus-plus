"""
helper.py - help system for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

import os.path
import webbrowser
import wx
from wx import adv, html

_ = wx.GetTranslation

class HelpSystem(html.HtmlHelpController):
    def __init__(self, app):
        html.HtmlHelpController.__init__(self)
        self._app = app

        self.config = wx.FileConfig(localFilename=os.path.join(app.userdatadir, "help.cfg"))

        self.SetTempDir(os.path.join(app.userdatadir, ""))
        self.SetTitleFormat("%s")
        self.UseConfig(self.config)

        book = os.path.join(app.cwd, "locale", app.locale.GetCanonicalName(), "help", "header.hhp")
        if not os.path.isfile(book):
            book = os.path.join(app.cwd, "locale", "en_US", "help", "header.hhp")
        self.AddBook(book)

    def ShowHelpFrame(self):
        self.DisplayContents()
        self.GetHelpWindow().Bind(html.EVT_HTML_LINK_CLICKED, self.OnHelpHtmlLinkClicked)

    def OnHelpHtmlLinkClicked(self, event):
        href = event.GetLinkInfo().GetHref()
        if href.startswith("http:"):
            webbrowser.open(href)
        else:
            event.Skip()

    def ShowAboutBox(self):
        info = adv.AboutDialogInfo()
        info.SetName("Write++")
        info.SetVersion(self._app.version)
        info.SetCopyright("Copyright (C) 2011-2018 Timothy Johnson. All rights reserved.")
        info.SetDescription(_("A text editor that is free, cross-platform, and open-source."))
        info.SetWebSite("https://github.com/t1m0thyj/write-plus-plus")
        info.SetLicense(license)
        adv.AboutBox(info)

license = """This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

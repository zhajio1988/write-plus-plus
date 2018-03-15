"""
write++.py - main script for Write++
Copyright (C) 2013 Timothy Johnson <timothysw@objectmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import configparser
import getopt
import os
import sys
import wx

import plugins
import debug
import helper
import ipc
import parent
import printing

_version = debug._version = "0.9.9"


class FileConfig(configparser.RawConfigParser):
    def __init__(self, app):
        configparser.RawConfigParser.__init__(self)
        self._app = app

        self.filename = os.path.join(app.userdatadir, "write++.ini")

        self.optionxform = str  # Don't make option names lowercase
        if os.path.isfile(self.filename):
            config = open(self.filename, 'r')
            self.readfp(config)
            config.close()

    def Load(self):
        display = wx.GetDisplaySize()
        best = (int(display[0] * 0.8), int(display[1] * 0.8))
        settings = {"WindowPos":wx.DefaultPosition, "WindowSize":best, "MaximizeState":False,
                    "MinimizeToTray":False, "SessionFile":"", "FixedTabWidth":True,
                    "RecentFiles":[], "PluginList":[], "PluginsEnabled":[],
                    "BackupType":2, "BackupDir":os.path.join(self._app.userdatadir, "backup"),
                    "LeftDocked":["filebrowser"], "RightDocked":[], "TopDocked":[], "BottomDocked":[],
                    "LeftActive":0, "RightActive":-1, "TopActive":-1, "BottomActive":-1,
                    "QuickFind":"", "LastFind":"", "LastReplace":"", "LastFilter":"", "FilterExclude":False,
                    "FindHistory":[], "ReplaceHistory":[], "FilterHistory":[],
                    "ShowHidden":False, "UpdatePath":True, "FilterIndex":0,
                    "FavoriteList":[], "SelectedPaths":[]}
        if self.has_option("Main", "WindowPos"):
            settings["WindowPos"] = map(int, self.getunicode("Main", "WindowPos").split(","))
        if self.has_option("Main", "WindowSize"):
            settings["WindowSize"] = map(int, self.getunicode("Main", "WindowSize").split(","))
        if not (0 - settings["WindowSize"][0] < settings["WindowPos"][0] < display[0] and 0 - settings["WindowSize"][1] < settings["WindowPos"][1] < display[1]):
            settings["WindowPos"] = wx.DefaultPosition
            settings["WindowSize"] = best
        for option in ("MaximizeState", "MinimizeToTray", "FixedTabWidth"):
            if self.has_option("Main", option):
                settings[option] = self.getboolean("Main", option)
        if self.has_option("Main", "SessionFile"):
            settings["SessionFile"] = self.getunicode("Main", "SessionFile")
        if self.has_section("RecentFiles"):
            settings["RecentFiles"] = self.getlist("RecentFiles")
        if self.has_section("Plugins"):
            plugins = [item.split(", ") for item in self.getlist("Plugins")]
            for name, enabled in plugins:
                settings["PluginList"].append(name)
                settings["PluginsEnabled"].append(enabled.lower() == "true")
        if self.has_option("Editor", "BackupType"):
            settings["BackupType"] = self.getint("Editor", "BackupType")
        if self.has_option("Editor", "BackupDir"):
            settings["BackupDir"] = self.getunicode("Editor", "BackupDir")
        for direction in ("Left", "Right", "Top", "Bottom"):
            docked = "%sDocked" % direction
            if self.has_option("Panes", "%s" % docked):
                settings[docked] = self.getunicode("Panes", docked).split(";")
            active = "%sActive" % direction
            if self.has_option("Panes", active):
                settings[active] = self.getint("Panes", active)
        for option in ("QuickFind", "LastFind", "LastReplace", "LastFilter"):
            if self.has_option("Search", option):
                settings[option] = self.getunicode("Search", option)
        if self.has_option("Search", "FilterExclude"):
            settings["FilterExclude"] = self.getboolean("Search", "FilterExclude")
        if self.has_section("Search\\FindHistory"):
            settings["FindHistory"] = self.getlist("Search", "FindHistory")
        if self.has_section("Search\\ReplaceHistory"):
            settings["ReplaceHistory"] = self.getlist("Search", "ReplaceHistory")
        if self.has_section("Search\\FilterHistory"):
            settings["FilterHistory"] = self.getlist("Search", "FilterHistory")
        if self.has_option("Browser", "ShowHidden"):
            settings["ShowHidden"] = self.getboolean("Browser", "ShowHidden")
        if self.has_option("Browser", "UpdatePath"):
            settings["UpdatePath"] = self.getboolean("Browser", "UpdatePath")
        if self.has_option("Browser", "FilterIndex"):
            settings["FilterIndex"] = self.getint("Browser", "FilterIndex")
        if self.has_section("Browser\\FavoriteList"):
            settings["FavoriteList"] = self.getlist("Browser", "FavoriteList")
        if self.has_section("Browser\\SelectedPaths"):
            settings["SelectedPaths"] = self.getlist("Browser", "SelectedPaths")
        return settings

    def getunicode(self, section, option):
        return self.get(section, option).decode("utf_8")

    def getlist(self, section, option=None):
        if option:
            section = "%s\\%s" % (section, option)
        option = "Item1"
        sequence = []
        i = 1
        while self.has_option(section, option):
            sequence.append(self.getunicode(section, option))
            i += 1
            option = "Item%d" % i
        return sequence

    def Save(self, frame):
        if not self.has_section("Main"):
            self.add_section("Main")
        self.set("Main", "WindowPos", ",".join(map(str, frame.rect.GetPosition())))
        self.set("Main", "WindowSize", ",".join(map(str, frame.rect.GetSize())))
        self.set("Main", "MaximizeState", str(frame.IsMaximized()))
        self.set("Main", "MinimizeToTray", str(self._app.settings["MinimizeToTray"]))
        if frame.session:
            self.set("Main", "SessionFile", frame.session)
        self.set("Main", "FixedTabWidth", str(self._app.settings["FixedTabWidth"]))
        self.setlist("RecentFiles", None, self._app.settings["RecentFiles"])
        plugins = []
        for i in range(len(self._app.plugins.names)):
            plugins.append("%s, %s" % (self._app.plugins.names[i], self._app.plugins.enabled[i]))
        self.setlist("Plugins", None, plugins)
        if not self.has_section("Editor"):
            self.add_section("Editor")
        self.set("Editor", "BackupType", str(self._app.settings["BackupType"]))
        self.set("Editor", "BackupDir", self._app.settings["BackupDir"])
        if not self.has_section("Panes"):
            self.add_section("Panes")
        self.set("Panes", "LeftDocked", ";".join(frame.managers[wx.LEFT].GetPanes()))
        self.set("Panes", "RightDocked", ";".join(frame.managers[wx.RIGHT].GetPanes()))
        self.set("Panes", "TopDocked", ";".join(frame.managers[wx.TOP].GetPanes()))
        self.set("Panes", "BottomDocked", ";".join(frame.managers[wx.BOTTOM].GetPanes()))
        self.set("Panes", "LeftActive", str(frame.managers[wx.LEFT].GetCurrent()))
        self.set("Panes", "RightActive", str(frame.managers[wx.RIGHT].GetCurrent()))
        self.set("Panes", "TopActive", str(frame.managers[wx.TOP].GetCurrent()))
        self.set("Panes", "BottomActive", str(frame.managers[wx.BOTTOM].GetCurrent()))
        if not self.has_section("Search"):
            self.add_section("Search")
        self.set("Search", "QuickFind", frame.searchbar.find.GetValue())
        for item in ("Find", "Replace", "Filter"):
            self.set("Search", "Last%s" % item, self._app.settings["Last%s" % item])
        self.set("Search", "FilterExclude", str(self._app.settings["FilterExclude"]))
        self.setlist("Search", "FindHistory", self._app.settings["FindHistory"])
        self.setlist("Search", "ReplaceHistory", self._app.settings["ReplaceHistory"])
        self.setlist("Search", "FilterHistory", self._app.settings["FilterHistory"])
        if not self.has_section("Browser"):
            self.add_section("Browser")
        self.set("Browser", "ShowHidden", str(self._app.settings["ShowHidden"]))
        self.set("Browser", "UpdatePath", str(self._app.settings["UpdatePath"]))
        self.set("Browser", "FilterIndex", str(frame.filebrowser.dirctrl.GetFilterIndex()))
        self.setlist("Browser", "FavoriteList", frame.filebrowser.favorites)
        self.setlist("Browser", "SelectedPaths", frame.filebrowser.dirctrl.GetPaths())
        config = open(self.filename, 'w')
        self.write(config)
        config.close()

    def setlist(self, section, option, value):
        if option:
            section = "%s\\%s" % (section, option)
        if not self.has_section(section):
            self.add_section(section)
        for i in range(len(value)):
            self.set(section, "Item%d" % (i + 1), value[i])

class WritePlusPlus(wx.App):
    def OnInit(self):
        #wx.App.__init__(self)

        self.SetAppName("Write++")
        self.checker = wx.SingleInstanceChecker("write++-%s" % wx.GetUserId(), wx.StandardPaths.Get().GetTempDir())
        self.server = None
        if "--multiple" not in options:
            if not self.checker.IsAnotherRunning():
                self.server = ipc.IPCServer(self)
                if not self.server.socket:
                    self.server = None
            elif ipc.transmit(sys.argv[1:]):
                sys.exit(0)

        if not hasattr(sys, "frozen"):
            self.cwd = os.path.dirname(__file__)
        else:
            self.cwd = os.path.dirname(sys.argv[0])
        if "--datadir" in options:
            self.userdatadir = options["--datadir"]
            if not os.path.isabs(self.userdatadir):
                self.userdatadir = os.path.join(self.cwd, self.userdatadir)
        elif os.path.isfile(os.path.join(self.cwd, "portable.ini")):
            self.userdatadir = self.cwd
        else:
            self.userdatadir = wx.StandardPaths.Get().GetUserDataDir()
        if not os.path.isdir(self.userdatadir):
            os.makedirs(self.userdatadir)

        self.config = FileConfig(self)
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH_US)
        localedir = os.path.join(self.cwd, "locale")
        self.locale.AddCatalogLookupPathPrefix(localedir)
        language = self.locale.GetCanonicalName()
        if os.path.isfile(os.path.join(localedir, language, "LC_MESSAGES", "write++.mo")):
            self.locale.AddCatalog(language)
        self.settings = self.config.Load()
        self.version = _version

        self.helper = helper.HelpSystem(self)
        self.plugins = plugins.PluginManager(self)
        self.printer = printing.Printer(self)

        return True

    def PostInit(self):
        self.frames = []
        session = None
        if "--session" in options:
            session = options["--session"]
            if not os.path.isabs(session):  # Check if path is relative
                session = os.path.join(app.cwd, session)
        self.NewFrame(session)
        if "--systemtray" in options:
            self.frames[0].Iconize()
        for arg in args:
            if os.path.exists(arg):
                self.frames[0].OpenFile(arg)
        if self.server:
            self.server.start()

    def MacNewFile(self):
        self.frames[self.active].New()

    def MacOpenFiles(self, filenames):
        self.frames[self.active].OpenFiles(filename)

    def MacPrintFile(self, filename):
        self.frames[self.active].OpenFile(filename)
        self.frames[self.active].Print()

    def NewFrame(self, session=None):
        for frame in self.frames:
            if frame.session == session:
                self.ShowFrame(frame)
                return
        self.frames.append(parent.MainFrame(self, session))
        self.frames[-1].Show()
        self.active = len(self.frames) - 1

    def ShowFrame(self, frame):
        if not hasattr(frame, "trayicon"):
            frame.Iconize(False)
            frame.Show()
            frame.Raise()
        else:
            frame.trayicon.OnRestore(None)

    def CloseAllFrames(self, restart=False):
        for i in range(len(self.frames) - 1, -1, -1):
            self.frames[i].Close()
        self.restart = restart

    def UnInit(self):
        self.plugins.UnInit()
        if len(self.frames) == 1:
            self.config.Save(self.frames[self.active])
            if hasattr(self, "checker"):
                del self.checker
            del self.helper
            del self.locale
            del self.printer
            if self.server:
                self.server.Quit()

    def CloseFrame(self, frame):
        self.frames.remove(frame)
        frame.Destroy()
        if len(self.frames) or len(self.plugins.failed):
            self.active = min(max(0, self.active - 1), len(self.frames) - 1)
        else:
            self.restart = False
            wx.CallLater(1, self.ExitMainLoop)

def main(restart=False):
    #sys.excepthook = debug.OnError
    global options, args
    if not restart:
        options, args = getopt.getopt(sys.argv[1:], "", ["datadir=", "multiple", "session=", "systemtray"])
    else:
        options, args = getopt.getopt(sys.argv[1:], "", ["datadir=", "multiple"])
    options = dict(options)
    app = WritePlusPlus()#restart)
    app.PostInit()
    if restart:
        app.frames[0].Plugins()
    app.MainLoop()
    if app.restart:
        sys.argv = sys.argv[:1]
        main(True)

if __name__ == "__main__":
    main()
"""
plugins.py - plugin management classes for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

import os
import shutil
import sys
import wx
import zipfile
from lxml import etree as ElementTree
from wx import adv, html

_ = wx.GetTranslation

class PluginManager:
    def __init__(self, app):
        self._app = app

        self.enabled = app.settings["PluginsEnabled"]
        self.events = {}
        self.failed = []
        self.names = app.settings["PluginList"]
        self.states = [0 for i in range(len(self.names))]
        self.stcevents = []
        self.tempdirs = {}

        if len(self.names) > 1:
            info = zip(self.names, self.enabled)
            info.sort(key=lambda item: (not item[1], item[0]))  # Sort plugins by enabled state, then by name
            self.names, self.enabled = map(list, zip(*info))

        plugindir = os.path.join(app.userdatadir, "plugins")
        if not os.path.isdir(plugindir):
            os.mkdir(plugindir)
        sys.path.insert(0, plugindir)

        self.plugins = []
        failed = []
        for i in range(len(self.names)):
            if not self.LoadPlugin(self.names[i], self.enabled[i]):
                failed.append(self.names[i])
        if len(failed):
            failed = "\n".join([" " * 4 + name.replace("_", " ") for name in failed])
            wx.MessageBox(_("The following plugins failed to start and have been disabled:\n\n%s") % failed, "Write++", wx.ICON_WARNING | wx.OK)

    def LoadPlugin(self, name, enabled, index=-1):
        module = getattr(__import__("%s.__init__" % name), "__init__")
        try:
            if index == -1:
                self.plugins.append(module.Plugin(self, name, enabled))
            else:
                self.plugins.insert(index, module.Plugin(self, name, enabled))
        except:
            self.enabled[self.names.index(name)] = False
            self.LoadPlugin(name, False, index)
        else:
            return True
        return False

    def OnInit(self, frame):
        for i in range(len(self.plugins)):
            try:
                self.plugins[i].OnNewFrame(frame)
            except:
                self.enabled[i] = False
                self.failed.append(self.names[i])

    def GetBitmap(self, plugin, name="icon"):
        return wx.Bitmap(os.path.join(self._app.userdatadir, "plugins", plugin, "%s.png" % name), wx.BITMAP_TYPE_PNG)

    def RegisterEvent(self, event, func1, func2, window):
        key = (window, event._getEvtType())
        if key not in self.events:
            self.events[key] = []
            if func1:
                self.events[key].append(func1)
            window.Bind(event, self.OnRegisteredEvent)
        self.events[key].append(func2)

    def OnRegisteredEvent(self, event):
        window = event.GetEventObject()
        while window:
            key = (window, event.GetEventType())
            if key in self.events:
                for func in self.events[key]:
                    func(event)
            window = window.GetParent()
        event.Skip()

    def UnregisterEvent(self, func):
        for event in self.events:
            if func in self.events[event]:
                self.events[event].remove(func)
                if not len(self.events[event]):
                    wx.CallAfter(self.events.pop, event)

    def RegisterEditorEvent(self, event, func1, func2, frame):
        for i in range(frame.notebook.GetPageCount()):
            editor = frame.GetEditor(i)
            if func1:
                self.RegisterEvent(event, getattr(editor, func1), func2, editor)
            else:
                self.RegisterEvent(event, None, func2, editor)
        key = (event, func1, func2)
        if key not in self.stcevents:
            self.stcevents.append(key)

    def UnregisterEditor(self, editor):
        for event in self.events:   # Remove editor bindings from event list
            if event[0] == editor:
                wx.CallAfter(self.events.pop, event)

    def UnregisterEditorEvent(self, event, func):
        for frame in self._app.frames:
            for i in range(frame.notebook.GetPageCount()):
                self.events[(frame.GetEditor(i), event._getEvtType())].remove(func)
        for event2, func1, func2 in self.stcevents:
            if (event2, func2) == (event, func):
                self.stcevents.remove((event2, func1, func2))

    def PostInit(self, frame):
        for i in range(len(self.plugins)):
            try:
                if hasattr(self.plugins[i], "OnNewFrame2"):
                    self.plugins[i].OnNewFrame2(frame)
            except:
                self.enabled[i] = False
                self.failed.append(self.names[i])

    def RemovePlugin(self, name):
        item = self.names.index(name)
        if self.states[item] == 3 and self.enabled[item] and hasattr(self.plugins[item], "OnDisable"):
            self.plugins[item].OnDisable()
        if hasattr(self.plugins[item], "OnRemove"):
            self.plugins[item].OnRemove()
        self.plugins.pop(item)
        self.enabled.pop(item)
        self.names.pop(item)
        self.states.pop(item)

    def UnInit(self):
        if len(self._app.frames) > 1:
            return
        i = 0
        while i < len(self.states):
            if 3 <= self.states[i] <= 5:
                self.RemovePlugin(self.names[i])
            else:
                i += 1
        tempdir = wx.StandardPaths.Get().GetTempDir()
        for name in self.tempdirs:
            shutil.rmtree(os.path.join(tempdir, self.tempdirs[name]), True)
        for plugin in self.plugins:
            plugin.OnExit()

class PluginDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, _("Plugin Manager"), size=(600, 440))
        self._parent = parent

        self._manager = parent._app.plugins
        self.olditems = {}
        self.restart = []
        self.tempdir = wx.StandardPaths.Get().GetTempDir()

        self.listbox = HtmlListBox(self)
        self.listbox.SetDropTarget(PluginDropTarget(self))
        for i in range(len(self._manager.names)):
            if self._manager.states[i] < 3 or self._manager.states[i] == 6:
                root = ElementTree.parse(os.path.join(parent._app.userdatadir, "plugins", self._manager.names[i], "plugin.xml")).getroot()
            else:
                root = ElementTree.parse(os.path.join(self.tempdir, self._manager.tempdirs[self._manager.names[i]], "plugin.xml")).getroot()
            text = "<font><b>%s</b> %s<br>%s</font><div align=right>" % (root[0].text, root[1].text, root[2].text)
            if self._manager.states[i] < 6:
                if self._manager.enabled[i]:
                    if hasattr(self._manager.plugins[i], "OnOptions"):
                        text += _("<a href='%s;0'>Options</a> ") % self._manager.names[i]
                    text += _("<a href='%s;1'>Disable</a> ") % self._manager.names[i]
                else:
                    text = text.replace("<font>", "<font color=gray>").replace("<br>", _(" (disabled)<br>"))
                    text += _("<a href='%s;2'>Enable</a> ") % self._manager.names[i]
                text += _("<a href='%s;3'>Remove</a>") % self._manager.names[i] + " </div>"
            if 1 <= self._manager.states[i] <= 5:
                self.olditems[self._manager.names[i]] = text
                if self._manager.states[i] == 1:
                    text2 = _("<font color=gray>This plugin will be disabled when you restart Write++. <a href=';4'>Restart&nbsp;Now</a> <a href='%s;5'>Undo</a></font><br>") % self._manager.names[i]
                    text = text2 + text[:text.index("<div align=right>")]
                elif self._manager.states[i] == 2:
                    text2 = _("<font color=green>This plugin will be enabled when you restart Write++. <a href=';4'>Restart&nbsp;Now</a> <a href='%s;5'>Undo</a></font><br>") % self._manager.names[i]
                    text = text2 + text[:text.index("<div align=right>")]
                elif self._manager.states[i] == 3:
                    text = _("<font color=gray><b>%s</b> has been removed. <a href=';4'>Restart&nbsp;Now</a> <a href='%s;5'>Undo</a></font>") % (root[0].text, self._manager.names[i])
                else:
                    text = _("<font color=gray><b>%s</b> has been removed. <a href='%s;5'>Undo</a></font>") % (root[0].text, self._manager.names[i])
            elif self._manager.states[i] == 6:
                text2 = _("<font color=green>This plugin will be installed when you restart Write++. <a href=';4'>Restart&nbsp;Now</a> <a href='%s;5'>Undo</a></font><br>") % self._manager.names[i]
                text = text2 + text[:text.index("<div align=right>")]
            self.listbox.items.append(text)
            self.restart.append(root[3].text == "True")
        self.listbox.SetItemCount(len(self.listbox.items))
        self.install = adv.HyperlinkCtrl(self, -1, _("Install plugin from file..."), "", style=wx.NO_BORDER | adv.HL_ALIGN_LEFT)
        self.close = wx.Button(self, wx.ID_CLOSE)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.listbox, 1, wx.ALL | wx.EXPAND, 2)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.install, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer2.Add(self.close, 0, wx.EXPAND)
        sizer.Add(sizer2, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        self.listbox.Bind(html.EVT_HTML_LINK_CLICKED, self.OnLinkClicked)
        self.install.Bind(adv.EVT_HYPERLINK, self.OnHyperlink)
        self.close.Bind(wx.EVT_BUTTON, self.OnClose)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnLinkClicked(self, event):
        name, action = event.GetLinkInfo().GetHref().split(";")
        self.HandleLinkEvent(name, int(action))

    def HandleLinkEvent(self, name, action, update=True):
        if len(name):
            item = self._manager.names.index(name)
        if action == 0: # Options
            self._manager.plugins[item].OnOptions()
        elif action == 1:   # Disable
            self._manager.enabled[item] = False
            self.olditems[name] = self.listbox.items[item]
            if self.restart[item]:
                text = _("<font color=gray>This plugin will be disabled when you restart Write++. <a href=';4'>Restart&nbsp;Now</a> <a href='%s;5'>Undo</a></font><br>") % name
                text2 = self.listbox.items[item]
                self.listbox.items[item] = text + text2[:text2.index("<div align=right>")]
                self._manager.states[item] = 1  # 1 = will be disabled on restart
            else:
                if hasattr(self._manager.plugins[item], "OnDisable"):
                    self._manager.plugins[item].OnDisable()
                self.listbox.items[item] = self.listbox.items[item].replace("<font>", "<font color=gray>", 1).replace("<br>", _(" (disabled)<br>"), 1)
                self.listbox.items[item] = self.listbox.items[item].replace("<div align=right>" + _("<a href='%s;0'>Options</a> ") % name, "<div align=right>")
                self.listbox.items[item] = self.listbox.items[item].replace(_("<a href='%s;1'>Disable</a> ") % name, _("<a href='%s;2'>Enable</a> ") % name)
        elif action == 2:   # Enable
            self._manager.enabled[item] = True
            self.olditems[name] = self.listbox.items[item]
            if self.restart[item]:
                text = _("<font color=green>This plugin will be enabled when you restart Write++. <a href=';4'>Restart&nbsp;Now</a> <a href='%s;5'>Undo</a></font><br>") % name
                text2 = self.listbox.items[item]
                self.listbox.items[item] = text + text2[:text2.index("<div align=right>")]
                self._manager.states[item] = 2  # 2 = will be enabled on restart
            else:
                self._manager.plugins[item].__init__(self._manager, name, True)
                if hasattr(self._manager.plugins[item], "OnNewFrame"):
                    for frame in self._manager._app.frames:
                        self._manager.plugins[item].OnNewFrame(frame)
                if hasattr(self._manager.plugins[item], "OnEnable"):
                    self._manager.plugins[item].OnEnable()
                self.listbox.items[item] = self.listbox.items[item].replace("<font color=gray>", "<font>", 1).replace(_(" (disabled)<br>"), "<br>", 1)
                if hasattr(self._manager.plugins[item], "OnOptions"):
                    self.listbox.items[item] = self.listbox.items[item].replace("<div align=right>", "<div align=right>" + _("<a href='%s;0'>Options</a> ") % name)
                self.listbox.items[item] = self.listbox.items[item].replace(_("<a href='%s;2'>Enable</a> ") % name, _("<a href='%s;1'>Disable</a> ") % name)
        elif action == 3:   # Remove
            plugindir = os.path.join(self._parent._app.userdatadir, "plugins")
            self._manager.tempdirs[name] = "write++-%s" % name
            os.rename(os.path.join(plugindir, name), os.path.join(plugindir, self._manager.tempdirs[name]))
            shutil.move(os.path.join(plugindir, self._manager.tempdirs[name]), self.tempdir)
            self.olditems[name] = self.listbox.items[item]
            if self.restart[item]:
                text = _("<font color=gray><b>%s</b> has been removed. <a href=';4'>Restart&nbsp;Now</a> <a href='%s;5'>Undo</a></font>") % (name.replace("_", " "), name)
                self._manager.states[item] = 3  # 3 = will be disabled and removed on restart
            else:   # Plugins are never completely removed until program shutdown
                if self._manager.enabled[item]:
                    if hasattr(self._manager.plugins[item], "OnDisable"):
                        self._manager.plugins[item].OnDisable()
                    self._manager.states[item] = 4  # 4 = was enabled, will be removed
                else:
                    self._manager.states[item] = 5  # 5 = was disabled, will be removed
                text = _("<font color=gray><b>%s</b> has been removed. <a href='%s;5'>Undo</a></font>") % (name.replace("_", " "), name)
            self.listbox.items[item] = text
        elif action == 4:   # Restart Now
            self._parent._app.CloseAllFrames(True)
        elif action == 5:   # Undo
            if self._manager.states[item] < 6:
                if 3 <= self._manager.states[item] <= 5:
                    plugindir = os.path.join(self._parent._app.userdatadir, "plugins")
                    shutil.move(os.path.join(self.tempdir, self._manager.tempdirs[name]), plugindir)
                    os.rename(os.path.join(plugindir, self._manager.tempdirs[name]), os.path.join(plugindir, name))
                    self._manager.tempdirs.pop(name)
                if self._manager.states[item] == 4:
                    self._manager.plugins[item].__init__(self._manager, name, True)
                    if hasattr(self._manager.plugins[item], "OnNewFrame"):
                        for frame in self._manager._app.frames:
                            self._manager.plugins[item].OnNewFrame(frame)
                    if hasattr(self._manager.plugins[item], "OnEnable"):
                        self._manager.plugins[item].OnEnable()
                self.listbox.items[item] = self.olditems.pop(name)
                self._manager.states[item] = 0
            else:
                shutil.rmtree(os.path.join(self._parent._app.userdatadir, "plugins", name))
                self._manager.RemovePlugin(name)
                self.restart.pop(item)
                self.listbox.items.pop(item)
        if action != 0 and action != 4 and update:  # not Options or Restart Now
            self.listbox.SetItemCount(len(self.listbox.items))
            self.listbox.Refresh()
            self.listbox.Update()

    def InstallPluginFromFile(self, filenames):
        info = []
        try:
            installed = []
            for filename in filenames:
                wzip = zipfile.ZipFile(filename, 'r')
                xml = wzip.open("%splugin.xml" % wzip.namelist()[0], 'r')
                root = ElementTree.fromstring(xml.read())
                xml.close()
                name = root[0].text.replace(" ", "_")
                if name in self._manager.names:
                    item = self._manager.names.index(name)
                    if self._manager.states[item] < 3 or self._manager.states[item] == 6:
                        root2 = ElementTree.parse(os.path.join(self._parent._app.userdatadir, "plugins", name, "plugin.xml")).getroot()
                    else:
                        root2 = ElementTree.parse(os.path.join(wx.StandardPaths.Get().GetTempDir(), self._manager.tempdirs[name], "plugin.xml")).getroot()
                    if root2[1].text == root[1].text:
                        if self._manager.states[item] < 3 or self._manager.states[item] == 6:
                            installed.append("%s %s" % (root2[0].text, root2[1].text))
                        else:
                            self.HandleLinkEvent(name, 5, False)
                        wzip.close()
                        continue
                    else:
                        shutil.rmtree(os.path.join(self._parent._app.userdatadir, "plugins", name))
                        self._manager.states[item] = 3
                        self._manager.RemovePlugin(name)
                        self.restart.pop(item)
                        self.listbox.items.pop(item)
                info.append((wzip, root, name))
            if len(installed):
                installed = "\n".join([" " * 4 + name for name in installed])
                wx.MessageBox(_("The following plugins are already installed:\n\n%s") % installed, _("Plugin Manager"), wx.ICON_EXCLAMATION | wx.OK, self)
            if not len(info):
                return
            names = "\n".join([" " * 4 + item[1][0].text for item in info])
            install = wx.MessageBox(_("Are you sure you want to install the following plugins?\n\n%s") % names, _("Plugin Manager"), wx.ICON_QUESTION | wx.YES_NO, self)
            if install != wx.YES:
                return
            plugindir = os.path.join(self._parent._app.userdatadir, "plugins")
            disabled = 0
            for i in range(len(self._manager.names) - 1, -1, -1):
                if self._manager.enabled[i] or self._manager.states[i] == 1:
                    break
                disabled += 1
            names = self._manager.names[:]
            if disabled > 0:
                names = names[:-disabled]
            if len(info) > 1:
                dialog = wx.ProgressDialog("Write++", "", len(info))
                i = 0
            for wzip, root, name in info:
                if len(info) > 1:
                    dialog.Update(i, _("Installing %s...") % root[0].text)
                    i += 1
                wzip.extractall(plugindir)
                names.append(name)
                names.sort()
                item = names.index(name)
                self._manager.names.insert(item, name)
                self._manager.enabled.insert(item, True)
                restart = root[3].text == "True"
                self._manager.LoadPlugin(name, not restart, item)
                text = "<font><b>%s</b> %s<br>%s</font><div align=right>" % (root[0].text, root[1].text, root[2].text)
                if hasattr(self._manager.plugins[item], "OnInstall"):
                    self._manager.plugins[item].OnInstall()
                if restart:
                    text2 = _("<font color=green>This plugin will be installed when you restart Write++. <a href=';4'>Restart&nbsp;Now</a> <a href='%s;5'>Undo</a></font><br>") % name
                    text = text2 + text[:text.index("<div align=right>")]
                    self._manager.states.insert(item, 6)    # 6 = will be installed on restart
                else:
                    if hasattr(self._manager.plugins[item], "OnNewFrame"):
                        for frame in self._manager._app.frames:
                            self._manager.plugins[item].OnNewFrame(frame)
                    if hasattr(self._manager.plugins[item], "OnEnable"):
                        self._manager.plugins[item].OnEnable()
                    if hasattr(self._manager.plugins[item], "OnOptions"):
                        text += _("<a href='%s;0'>Options</a> ") % name
                    text += _("<a href='%s;1'>Disable</a> ") % name + _("<a href='%s;3'>Remove</a>") % name + " </div>"
                    self._manager.states.insert(item, 0)
                self.listbox.items.insert(item, text)
                self.restart.insert(item, restart)
            self.listbox.SetItemCount(len(self.listbox.items))
            self.listbox.Refresh()
            self.listbox.Update()
            if len(info) > 1:
                dialog.Destroy()
        finally:
            for item in info:
                item[0].close()

    def OnHyperlink(self, event):
        dialog = wx.FileDialog(self._parent, _("Install plugin from file..."), os.path.join(self._parent._app.userdatadir, "plugins"), wildcard=_("Write++ Plugins (*.wzip)|*.wzip"), style=wx.OPEN | wx.MULTIPLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.InstallPluginFromFile(dialog.GetPaths())
        dialog.Destroy()

    def OnClose(self, event):
        self.Destroy()

class HtmlListBox(html.HtmlListBox):
    def __init__(self, parent):
        html.HtmlListBox.__init__(self, parent, -1)
        self._parent = parent

        self.items = []

        self.Bind(wx.EVT_LISTBOX, self.OnListbox)

    def OnDrawSeparator(self, dc, rect, item):
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)))
        dc.DrawLine(0, rect.y + rect.height - 1, rect.width, rect.y + rect.height - 1)
        rect.height -= 1

    def OnGetItem(self, item):
        text = self.items[item]
        if self.IsSelected(item):
            text = text.replace("<font color=gray>", "<font>").replace("<font color=green>", "<font>")
            if self._parent.FindFocus() == self:
                text = "<font color=%s>%s</font>" % (wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT).GetAsString(wx.C2S_HTML_SYNTAX), text)
            else:
                text = "<font color=%s>%s</font>" % (wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOXHIGHLIGHTTEXT).GetAsString(wx.C2S_HTML_SYNTAX), text)
        return text

    def OnListbox(self, event):
        self.SetItemCount(len(self.items))
        self.Update()

class PluginDropTarget(wx.FileDropTarget):
    def __init__(self, dialog):
        wx.FileDropTarget.__init__(self)
        self._dialog = dialog

    def OnDropFiles(self, x, y, filenames):
        filenames = [filename for filename in filenames if os.path.splitext(filename)[1].lower() == ".wzip"]
        self._dialog.InstallPluginFromFile(filenames)
        return wx.DragCopy

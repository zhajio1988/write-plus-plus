"""
__init__.py - pane classes for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

import wx
from wx.lib.agw import aui

class VCPaneManager:
    def __init__(self, frame, direction):
        self._frame = frame

        self.autohide = False
        direction2 = directions[direction].capitalize()
        self.current = frame._app.settings["%sActive" % direction2]
        self.direction = direction
        self.paneinfo = {}
        self.panes = []
        self.selectpane = True
        self.visible = frame._app.settings["%sDocked" % direction2][:]

    def OnInit(self):
        style = aui.AUI_TB_DEFAULT_STYLE
        if self.direction == wx.LEFT or self.direction == wx.RIGHT:
            style |= aui.AUI_TB_VERT_TEXT
        else:
            style |= aui.AUI_TB_HORZ_TEXT
        self.toolbar = aui.AuiToolBar(self._frame, -1, agwStyle=style)

        self.hoveritem = -1
        self.hovertimer = wx.Timer()
        self.hovertimer.Bind(wx.EVT_TIMER, self.OnHoverTimer)
        self.toolbar.Bind(wx.EVT_MENU, self.OnPane)
        self.toolbar.Bind(aui.EVT_AUITOOLBAR_MIDDLE_CLICK, self.OnMiddleClick)
        self.toolbar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.toolbar.Bind(wx.EVT_MOTION, self.OnMotion)

    def OnHoverTimer(self, event):
        if self.autohide:
            self.ShowPane(self.visible[self.hoveritem])

    def OnPane(self, event):
        self.ShowPane(self.panes[event.GetId() - wx.ID_HIGHEST], True)

    def OnMiddleClick(self, event):
        self.HidePane(self.panes[event.GetId() - wx.ID_HIGHEST], aui.AUI_BUTTON_CLOSE)

    def OnLeaveWindow(self, event):
        self.toolbar.OnLeaveWindow(event)
        self.hovertimer.Stop()
        self.hoveritem = -1
        event.Skip()

    def OnMotion(self, event):
        self.toolbar.OnMotion(event)
        if self.autohide:
            item = self.toolbar.FindToolForPosition(event.GetX(), event.GetY())
            if item:
                hoveritem = item.GetId() - wx.ID_HIGHEST
                if hoveritem != self.hoveritem:
                    self.hovertimer.Start(500, wx.TIMER_ONE_SHOT)
                    self.hoveritem = hoveritem
            else:
                self.hovertimer.Stop()
                self.hoveritem = -1
        event.Skip()

    def AddPane(self, window, caption, bitmap, name, bestsize=-1, select=False):
        if not len(self.panes):
            self.OnInit()
        direction = getattr(aui, "AUI_DOCK_%s" % directions[self.direction].upper())
        paneinfo = aui.AuiPaneInfo().Name(name).Caption(caption).Direction(direction).PinButton(True)
        if self.direction == wx.LEFT or self.direction == wx.RIGHT:
            paneinfo.BestSize((bestsize, -1)).Layer(1)
        else:
            paneinfo.BestSize((-1, bestsize)).Layer(3)
        if select:
            paneinfo.DestroyOnClose()
        else:
            paneinfo.Hide()
        self._frame.aui.AddPane(window, paneinfo)
        if name in self.visible:
            self.toolbar.AddCheckTool(wx.ID_HIGHEST + len(self.panes), caption, bitmap, wx.NullBitmap, caption)
        self.paneinfo[name] = (caption, bitmap)
        self.panes.append(name)
        self._frame.panedict[name] = self.direction
        if select:
            self.ShowPane(name)

    def Realize(self, update=False):
        self.current = min(self.current, len(self.visible) - 1)
        if self.current == -1:
            self.autohide = True
        else:
            self.toolbar.ToggleTool(wx.ID_HIGHEST + self.current, True)
        self.toolbar.Realize()
        direction = getattr(aui, "AUI_DOCK_%s" % directions[self.direction].upper())
        paneinfo = aui.AuiPaneInfo().Name("%sdock" % directions[self.direction]).ToolbarPane().Gripper(False).PaneBorder(False).Resizable().Direction(direction).DockFixed()
        if self.direction == wx.LEFT or self.direction == wx.RIGHT:
            paneinfo.Layer(2)
        else:
            paneinfo.Layer(4)
        self._frame.aui.AddPane(self.toolbar, paneinfo.Show(len(self.visible) or not update))
        if self.current != -1:
            self._frame.aui.GetPane(self.visible[self.current]).Show()
        if update:
            self._frame.aui.Update()

    def ShowPane(self, pane, update=True):
        def compare(item1, item2):
            if item1 == item2:
                return 0
            elif item1 == "filebrowser" or ((not item1.startswith("~")) and item2.startswith("~")):
                return -1
            elif item2 == "filebrowser" or (item1.startswith("~") and not item2.startswith("~")):
                return 1
            return cmp(item1, item2)

        if self.autohide and self.current == -1:
            self._frame.DoAutohide()
        index = self.panes.index(pane)
        if pane not in self.visible:
            caption, bitmap = self.paneinfo[pane]
            tool = self.toolbar.AddCheckTool(wx.ID_HIGHEST + index, caption, bitmap, wx.NullBitmap, caption)
            self.visible.append(pane)
            if len(self.visible) > 1:
                self.visible.sort(compare)
                if pane != self.visible[-1]:    # Place new toolbar item in correct position
                    self.toolbar._items.remove(tool)
                    index2 = self.visible.index(pane)
                    self.toolbar._items.insert(index2, tool)
                    for i in range(index2, len(self.visible)):  # Reset IDs of toolbar items to match their new positions
                        self.toolbar.FindToolByIndex(i).SetId(wx.ID_HIGHEST + i)
                self.panes.sort(compare)
            else:
                self.Realize(False)
            if not pane.startswith("~"):    # Panes whose names start with '~' are not saved on program shutdown
                self._frame.menubar.View.Check(getattr(self._frame.menubar, "ID_%s" % pane.upper()), True)
        if self.selectpane:
            if self.current != -1:
                self.toolbar.ToggleTool(wx.ID_HIGHEST + self.current, False)
                self._frame.aui.GetPane(self.visible[self.current]).Hide()
            self.toolbar.ToggleTool(wx.ID_HIGHEST + index, True)
            pane = self._frame.aui.GetPane(pane)
            if self.autohide:
                pane.MinimizeButton(True).PinButton(False).Show()
            else:
                pane.MinimizeButton(False).PinButton(True).Show()
            self.current = index
            wx.CallAfter(pane.window.SetFocus)
        if update:
            self.toolbar.Realize()
            self._frame.aui.Update()

    def HidePane(self, pane, button=-1):
        index = self.panes.index(pane)
        if button == aui.AUI_BUTTON_CLOSE:
            self.toolbar.DeleteTool(wx.ID_HIGHEST + index)
            self._frame.GetSizer().Layout() # Redraw entire toolbar
            self._frame.aui.GetPane(pane).Hide()
            if len(self.visible) == 1:
                self._frame.aui.ClosePane(self._frame.aui.GetPane("%sdock" % directions[self.direction]))
                self.current = -1
            elif self.selectpane:
                self.toolbar.ToggleTool(wx.ID_HIGHEST + index - 1, True)
                self.toolbar.Realize()
                self.ShowPane(self.visible[index - 1], False)
            if not pane.startswith("~"):
                self._frame.menubar.View.Check(getattr(self._frame.menubar, "ID_%s" % pane.upper()), False)
            else:
                self.panes.remove(pane)
            self.visible.remove(pane)
            for i in range(len(self.visible)):  # Reset IDs of toolbar items to match their new positions
                self.toolbar.FindToolByIndex(i).SetId(wx.ID_HIGHEST + i)
        elif button == aui.AUI_BUTTON_PIN:
            self._frame.aui.GetPane(self.visible[self.current]).MinimizeButton(True).PinButton(False)
            self.autohide = True
        elif button == aui.AUI_BUTTON_MINIMIZE:
            self._frame.aui.GetPane(self.visible[self.current]).MinimizeButton(False).PinButton(True)
            self.autohide = False
        else:
            self.toolbar.ToggleTool(wx.ID_HIGHEST + self.current, False)
            self.toolbar.Realize()
            self._frame.aui.GetPane(self.visible[self.current]).Hide()
            self.current = -1
        if self.selectpane or not len(self.visible):
            self._frame.aui.Update()

    def ShowPane2(self, pane, show=True):
        self.selectpane = False
        if show:
            self.ShowPane(pane)
        else:
            self.HidePane(pane, aui.AUI_BUTTON_CLOSE)
        self.selectpane = True

    def DestroyPane(self, pane):
        if pane in self.visible:
            self.ShowPane2(pane, False)
        self._frame.menubar.View.Delete(getattr(self._frame.menubar, "ID_%s" % pane.upper()))
        self.panes.remove(pane)

    def GetPanes(self):
        return [name for name in self.visible if not name.startswith("~")]

    def GetCurrent(self):
        if self.autohide:
            return -1
        return self.current

directions = {wx.LEFT:"left", wx.RIGHT:"right", wx.TOP:"top", wx.BOTTOM:"bottom"}

from panes.browser import *
from panes.results import *

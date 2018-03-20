"""
browser.py - browser pane class for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

import os
import webbrowser
import wx
from wx import adv
from wx.lib.agw import aui

_ = wx.GetTranslation

class FileBrowser(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self._parent = parent

        self.current = -1
        self.favorites = parent._app.settings["FavoriteList"]
        self.history = []

        self.toolbar = aui.AuiToolBar(self, -1, agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW | aui.AUI_TB_HORZ_TEXT)
        self.toolbar.AddSimpleTool(wx.ID_BACKWARD, _("Back"), parent.Bitmap("back"), _("Back"))
        self.toolbar.SetToolDropDown(wx.ID_BACKWARD, True)
        self.toolbar.EnableTool(wx.ID_BACKWARD, False)
        self.Bind(wx.EVT_MENU, self.OnBack, id=wx.ID_BACKWARD)
        self.toolbar.AddSimpleTool(wx.ID_UP, "", parent.Bitmap("up"), _("Up"))
        self.Bind(wx.EVT_MENU, self.OnUp, id=wx.ID_UP)
        self.toolbar.AddSimpleTool(wx.ID_NEW, "", parent.Bitmap("new-folder"), _("New Folder"))
        self.Bind(wx.EVT_MENU, self.OnNew, id=wx.ID_NEW)
        self.toolbar.AddSeparator()
        self.ID_FAVORITES = wx.NewId()
        self.toolbar.AddSimpleTool(self.ID_FAVORITES, "", parent.Bitmap("favorites"), _("Favorites"))
        self.Bind(wx.EVT_MENU, self.OnFavorites, id=self.ID_FAVORITES)
        self.ID_OPTIONS = wx.NewId()
        self.toolbar.AddSimpleTool(self.ID_OPTIONS, "", parent.Bitmap("options"), _("Options"))
        self.Bind(wx.EVT_MENU, self.OnOptions, id=self.ID_OPTIONS)
        self.toolbar.Realize()

        style = wx.DIRP_DEFAULT_STYLE
        if wx.VERSION_STRING >= "2.9.3.0":
            style |= wx.DIRP_SMALL
        self.dirpicker = wx.DirPickerCtrl(self, -1, style=style)

        style = wx.NO_BORDER | wx.DIRCTRL_SHOW_FILTERS | wx.DIRCTRL_EDIT_LABELS
        if wx.VERSION_STRING >= "2.9.0":
            style |= wx.DIRCTRL_MULTIPLE
        self.dirctrl = wx.GenericDirCtrl(self, -1, style=style, filter=parent.filetypes, defaultFilter=parent._app.settings["FilterIndex"])
        for path in parent._app.settings["SelectedPaths"]:
            self.dirctrl.ExpandPath(os.path.dirname(path))
        if wx.VERSION_STRING >= "2.9.0":
            ##self.dirctrl.SelectPaths(parent._app.settings["SelectedPaths"])
            pass
        else:
            if len(parent._app.settings["SelectedPaths"]):
                self.dirctrl.SetPath(parent._app.settings["SelectedPaths"][0])
            self.dirctrl.GetPaths = self.GetPaths2
        self.dirctrl.ShowHidden(parent._app.settings["ShowHidden"])
        path = self.dirctrl.GetPath()
        if os.path.isfile(path):
            path = os.path.dirname(path)
        self.dirpicker.SetPath(path)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar, 0, wx.EXPAND)
        sizer.Add(self.dirpicker, 0, wx.ALL | wx.EXPAND, 1)
        sizer.Add(self.dirctrl, 1, wx.BOTTOM | wx.EXPAND, 1)
        self.SetSizer(sizer)

        self.dirpicker.Bind(wx.EVT_DIRPICKER_CHANGED, self.OnDirPickerChanged)
        self.dirctrl.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginLabelEdit)
        self.dirctrl.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndLabelEdit)
        self.dirctrl.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        self.dirctrl.Bind(wx.EVT_TREE_ITEM_MIDDLE_CLICK, self.OnItemMiddleClick)
        self.dirctrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)

    def GetPaths2(self):
        paths = [self.dirctrl.GetPath()]
        if paths == [""]:
            return []
        return paths

    def OnAdd(self, event):
        paths = self.dirctrl.GetPaths()
        added = 0
        for path in paths:
            if path in self.favorites:
                wx.MessageBox(_("'%s' is already in the favorite list.") % path, "Write++", wx.ICON_EXCLAMATION | wx.OK)
            else:
                self.favorites.append(path)
                added += 1
        if added == 1:
            wx.MessageBox(_("'%s' has been added to the favorite list.") % paths[0], "Write++", wx.ICON_INFORMATION | wx.OK)
        elif added > 0:
            wx.MessageBox(_("%d folders have been added to the favorite list.") % added, "Write++", wx.ICON_INFORMATION | wx.OK)

    def OnManage(self, event):
        dialog = FavoriteManager(self._parent)
        dialog.Show()

    def OnBack(self, event):
        self.toolbar.SetToolSticky(wx.ID_BACKWARD, True)
        menu = wx.Menu()
        for i in range(self.current - 1, -1, -1):
            menu.Append(wx.ID_HIGHEST + i, self.history[i])
            self._parent.Bind(wx.EVT_MENU, self.OnHistoryItem, id=wx.ID_HIGHEST + i)
        self.toolbar.PopupMenu(menu, self._parent.toolbar.GetPopupPos(self.toolbar, wx.ID_BACKWARD))
        self.toolbar.SetToolSticky(wx.ID_BACKWARD, False)

    def OnHistoryItem(self, event):
        self.dirctrl.SetPath(self.history[event.GetId() - wx.ID_HIGHEST])

    def OnUp(self, event):
        self.dirctrl.SetPath(os.path.split(self.dirctrl.GetPath())[0])

    def OnNew(self, event):
        path = self.dirctrl.GetPaths()[0]
        if os.path.isdir(path):
            folder = os.path.join(path, _("New Folder"))
        elif os.path.isfile(path):
            folder = os.path.join(os.path.split(path)[0], _("New Folder"))
        os.makedirs(folder)
        self.dirctrl.SetPath(folder)
        tree = self.dirctrl.GetTreeCtrl()
        tree.EditLabel(tree.GetSelections()[0])

    def OnFavorites(self, event):
        self.toolbar.SetToolSticky(self.ID_FAVORITES, True)
        menu = wx.Menu()
        if len(self.favorites):
            self.ids = {}
            for favorite in self.favorites:
                id = wx.NewId()
                menu.Append(id, favorite)
                self.ids[id] = favorite
                self._parent.Bind(wx.EVT_MENU, self.OnFavorite, id=id)
        else:
            ID_EMPTY = wx.NewId()
            menu.Append(ID_EMPTY, _("(Empty)"))
            menu.Enable(ID_EMPTY, False)
        menu.AppendSeparator()
        ID_ADD = wx.NewId()
        menu.Append(ID_ADD, _("Add to Favorites"))
        self._parent.Bind(wx.EVT_MENU, self.OnAdd, id=ID_ADD)
        paths = []
        self.dirctrl.GetPaths(paths)
        if not len(paths):
            menu.Enable(ID_ADD, False)
        ID_MANAGE = wx.NewId()
        menu.Append(ID_MANAGE, _("Manage Favorites..."))
        self._parent.Bind(wx.EVT_MENU, self.OnManage, id=ID_MANAGE)
        self.toolbar.PopupMenu(menu, self._parent.toolbar.GetPopupPos(self.toolbar, self.ID_FAVORITES))
        self.toolbar.SetToolSticky(self.ID_FAVORITES, False)

    def OnFavorite(self, event):
        self.dirctrl.SetPath(self.ids[event.GetId()])

    def OnOptions(self, event):
        self.toolbar.SetToolSticky(self.ID_OPTIONS, True)
        menu = wx.Menu()
        menu.AppendCheckItem(wx.ID_HIGHEST + 1, _("Show Hidden Files"))
        menu.Check(wx.ID_HIGHEST + 1, self._parent._app.settings["ShowHidden"])
        menu.AppendCheckItem(wx.ID_HIGHEST + 2, _("Update Path on Tab Change"))
        menu.Check(wx.ID_HIGHEST + 2, self._parent._app.settings["UpdatePath"])
        self._parent.Bind(wx.EVT_MENU, self.OnOption, id=wx.ID_HIGHEST + 1, id2=wx.ID_HIGHEST + 2)
        self.toolbar.PopupMenu(menu, self._parent.toolbar.GetPopupPos(self.toolbar, self.ID_OPTIONS))
        self.toolbar.SetToolSticky(self.ID_OPTIONS, False)

    def OnOption(self, event):
        checked = event.IsChecked()
        if event.GetId() - wx.ID_HIGHEST == 1:
            self.dirctrl.ShowHidden(checked)
            self._parent._app.settings["ShowHidden"] = checked
        else:
            self._parent._app.settings["UpdatePath"] = checked

    def OnDirPickerChanged(self, event):
        self.dirctrl.UnselectAll()
        path = event.GetPath()
        self.dirctrl.ExpandPath(path)
        self.dirctrl.SelectPath(path)

    def OnBeginLabelEdit(self, event):
        paths = []
        self.dirctrl.GetPaths(paths)
        self.rename = paths[0]

    def OnEndLabelEdit(self, event):
        if not event.IsEditCancelled():
            os.rename(self.rename, os.path.join(os.path.split(self.rename)[0], event.GetLabel()))

    def OnItemActivated(self, event):
        paths = []
        self.dirctrl.GetPaths(paths)
        filenames = []
        for path in paths:
            if os.path.isfile(path):
                filenames.append(path)
        if len(filenames):
            self._parent.OpenFiles(filenames)
        event.Skip()

    def OnItemMiddleClick(self, event):
        paths = []
        self.dirctrl.GetPaths(paths)
        if os.path.isdir(paths[0]):
            webbrowser.open(paths[0])

    def OnSelChanged(self, event):
        path = self.dirctrl.GetPath()
        if os.path.isdir(path):
            if path not in self.history:
                self.history.append(path)
                if len(self.history) > 15:
                    self.history.pop(0)
                self.current = len(self.history) - 1
            else:
                self.history.remove(path)
                self.history.append(path)
                self.current = len(self.history) - 1
            self.toolbar.EnableTool(wx.ID_BACKWARD, self.current != 0)
            self.toolbar.Refresh(False)
        elif os.path.isfile(path):
            path = os.path.dirname(path)
        self.dirpicker.SetPath(path)
        event.Skip()

class FavoriteManager(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, _("Manage Favorites"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self._parent = parent

        self.favorites = adv.EditableListBox(self, -1, _("Favorite List\n(e.g., C:\\Users\\Username\\Documents)"))
        self.favorites.SetStrings(parent.filebrowser.favorites)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.favorites, 1, wx.ALL | wx.EXPAND, 2)
        sizer2 = wx.StdDialogButtonSizer()
        sizer2.AddButton(wx.Button(self, wx.ID_OK))
        sizer2.AddButton(wx.Button(self, wx.ID_CANCEL))
        sizer2.Realize()
        sizer.Add(sizer2, 0, wx.ALL | wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Layout()

        self.favorites.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEndLabelEdit)
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

    def OnEndLabelEdit(self, event):
        if not event.IsEditCancelled():
            label = event.GetLabel()
            if not os.path.isfile(label):
                wx.MessageBox(_("'%s' is not a valid folder.") % label, _("Manage Favorites"), wx.ICON_EXCLAMATION | wx.OK)
                event.Veto()
            elif label in self.favorites.GetStrings():
                wx.MessageBox(_("'%s' is already in the favorite list."), _("Manage Favorites"), wx.ICON_EXCLAMATION | wx.OK)
                event.Veto()
            else:
                event.Skip()

    def OnOk(self, event):
        self._parent.filebrowser.favorites = self.favorites.GetStrings()
        self.Destroy()

    def OnCancel(self, event):
        self.Destroy()

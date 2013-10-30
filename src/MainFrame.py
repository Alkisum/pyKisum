#!/usr/bin/env python
 
import wx
import os
import wx.lib.mixins.listctrl as listmix
from mutagen.mp3 import MP3
 
class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        
        framebox = wx.BoxSizer(wx.HORIZONTAL)
        treebox = wx.BoxSizer(wx.VERTICAL)
        listbox = wx.BoxSizer(wx.VERTICAL)
        treepanel = wx.Panel(self, -1)
        listpanel = wx.Panel(self, -1)

        self.tree = wx.TreeCtrl(treepanel, 1, wx.DefaultPosition, (-1,-1), wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)
        self.StartBuildFromDir(librarylocation)        
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)
        
        self.list = wx.ListCtrl(listpanel, -1, size=(600, -1), style=wx.LC_REPORT)        
        self.list.InsertColumn(0, '#')
        self.list.InsertColumn(1, 'Title')
        self.list.InsertColumn(2, 'Artist')
        self.list.InsertColumn(3, 'Album')
        self.list.InsertColumn(4, 'Date')
        self.list.InsertColumn(5, 'Length')
        self.InitList()
        
        #sizeexpand = (self.list.GetSize()[0]-170)/3
        self.list.SetColumnWidth(0, 30)
        self.list.SetColumnWidth(1, 300)
        self.list.SetColumnWidth(2, 200)
        self.list.SetColumnWidth(3, 200)
        self.list.SetColumnWidth(4, 60)
        self.list.SetColumnWidth(5, 80)
        
        treebox.Add(self.tree, 1, wx.EXPAND)
        listbox.Add(self.list, 1, wx.EXPAND)
        framebox.Add(treepanel, 1, wx.EXPAND)
        framebox.Add(listpanel, 3, wx.EXPAND)
        treepanel.SetSizer(treebox)
        listpanel.SetSizer(listbox)
        self.SetSizer(framebox)
        self.Centre()
        
    def StartBuildFromDir(self, location):
        rootname = os.path.split(location)
        self.root = self.tree.AddRoot(rootname[1])
        self.rootdir = location
        self.BuildChildrenFromDir(self.root, location)
        
    def BuildChildrenFromDir(self, parent, location):
        dirlisting = os.listdir(location)
        for listing in dirlisting:
            pathinquestion = os.path.join(location, listing)
            if os.path.isfile(pathinquestion):
                extension = os.path.splitext(pathinquestion)
                extension = extension[1]
                if extension == ".mp3":                    
                    itemid = self.tree.AppendItem(parent, listing)
                    if pathinquestion == treeitemselected:
                        self.tree.SelectItem(itemid)
            elif os.path.isdir(pathinquestion):
                newparent = self.tree.AppendItem(parent, listing)
                if pathinquestion == treeitemselected:
                    self.tree.SelectItem(newparent)
                newdir = os.path.join(location, listing)
                self.BuildChildrenFromDir(newparent, newdir)
        
    def OnSelChanged(self, event):
        self.list.DeleteAllItems()
        item = event.GetItem()
        fullpath = []
        while self.tree.GetItemParent(item):
            directory = self.tree.GetItemText(item)
            fullpath.insert(0, directory)
            fullpath.insert(0, '/')
            item = self.tree.GetItemParent(item)
        fullpath.insert(0, librarylocation)
        fullpath = ''.join(fullpath)
        if os.path.isdir(fullpath):
            self.DisplayAllChildren(fullpath)
        else:
            newextension = os.path.splitext(fullpath)
            newextension = newextension[1]
            if newextension == ".mp3":
                self.InsertTagsIntoList(fullpath)
                
    def InitList(self):       
        self.list.DeleteAllItems()
        fullpath = treeitemselected
        if os.path.isdir(fullpath):
            self.DisplayAllChildren(fullpath)
        else:
            newextension = os.path.splitext(fullpath)
            newextension = newextension[1]
            if newextension == ".mp3":
                self.InsertTagsIntoList(fullpath)
        
    def DisplayAllChildren(self, path):
        dirlistingmp3 = os.listdir(path)
        for listingmp3 in dirlistingmp3:
            newdir = os.path.join(path, listingmp3)
            if os.path.isfile(newdir):
                extensionmp3 = os.path.splitext(newdir)
                extensionmp3 = extensionmp3[1]
                if extensionmp3 == ".mp3":
                    self.InsertTagsIntoList(newdir)
            else:                
                self.DisplayAllChildren(newdir)
                
    def InsertTagsIntoList(self, mp3filepath):
        num_items = self.list.GetItemCount()
        audio = MP3(mp3filepath)
        self.list.InsertStringItem(num_items, ''.join(audio["TRCK"]))
        self.list.SetStringItem(num_items, 1, ''.join(audio["TIT2"]))
        self.list.SetStringItem(num_items, 2, ''.join(audio["TPE1"]))
        self.list.SetStringItem(num_items, 3, ''.join(audio["TALB"]))
        self.list.SetStringItem(num_items, 4, audio["TDRC"].text[0].get_text())
        length = audio.info.length
        hours = int(length // 3600)
        minutes = int((length % 3600) // 60)
        seconds = int(length % 60)
        if hours > 0:
            self.list.SetStringItem(num_items, 5, '{0:02d}'.format(hours) + ':{0:02d}'.format(minutes) + ':{0:02d}'.format(seconds))
        else:
            self.list.SetStringItem(num_items, 5, '{0:02d}'.format(minutes) + ':{0:02d}'.format(seconds))

class TestListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(1)
        self.setResizeColumn(2)
        self.setResizeColumn(3)

librarylocation = '/media/data/Programmation/pyKisum/MusicSample'
treeitemselected = '/media/data/Programmation/pyKisum/MusicSample/Airbourne/No Guts. No Glory'
app = wx.App(False)
frame = MainFrame(None, "pyKisum")
frame.Show()
app.MainLoop()
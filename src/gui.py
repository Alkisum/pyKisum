#!/usr/bin/env python
 
import wx
import os
from mutagen.mp3 import MP3
 
class GUI(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        
        #Temporary path of the music library (waiting for the feature to choose graphically the library in the file system) 
        self.librarylocation = '/media/data/Programmation/pyKisum/MusicSample'
        #Temporary path of the last MP3 files displayed in the list (waiting for the feature to read a config file where this path will be written)
        self.lastpathselected = '/media/data/Programmation/pyKisum/MusicSample/Airbourne/No Guts. No Glory'
        
        ''''''''' Top '''''''''
        topsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonpanel = wx.Panel(self, -1)
        self.previousbutton = wx.BitmapButton(buttonpanel, -1, wx.Bitmap('./img/previous.png'), size=(40, 40))
        self.playbutton = wx.BitmapButton(buttonpanel, -1, wx.Bitmap('./img/play.png'), size=(40, 40))
        self.nextbutton = wx.BitmapButton(buttonpanel, -1, wx.Bitmap('./img/next.png'), size=(40, 40))
        buttonsizer.Add(self.previousbutton)
        buttonsizer.Add(self.playbutton, 0, wx.LEFT | wx.RIGHT, 5)
        buttonsizer.Add(self.nextbutton, 0, wx.RIGHT, 5)
        buttonpanel.SetSizer(buttonsizer)
        topsizer.Add(buttonpanel, 1, wx.EXPAND | wx.ALL, 10)
        
        ''''''''' Bottom '''''''''        
        bottomsizer = wx.BoxSizer(wx.VERTICAL)
        treesizer = wx.BoxSizer(wx.VERTICAL)
        listsizer = wx.BoxSizer(wx.VERTICAL)
        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        treepanel = wx.Panel(splitter, -1, style=wx.SUNKEN_BORDER)
        listpanel = wx.Panel(splitter, -1, style=wx.SUNKEN_BORDER)
        splitter.SplitVertically(treepanel, listpanel)

        #Create the Tree containing the file system arborescence
        self.tree = wx.TreeCtrl(treepanel, 1, wx.DefaultPosition, (-1,-1), wx.TR_HIDE_ROOT|  wx.TR_HAS_BUTTONS)
        self.StartBuildFromDir(self.librarylocation)        
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)

        #Create the List containing the MP3 files
        self.list = wx.ListCtrl(listpanel, -1, size=(-1, -1), style=wx.LC_REPORT)        
        self.list.InsertColumn(0, '#')
        self.list.InsertColumn(1, 'Title')
        self.list.InsertColumn(2, 'Artist')
        self.list.InsertColumn(3, 'Album')
        self.list.InsertColumn(4, 'Date')
        self.list.InsertColumn(5, 'Length')        
        self.list.SetColumnWidth(0, 30)
        self.list.SetColumnWidth(1, 300)
        self.list.SetColumnWidth(2, 200)
        self.list.SetColumnWidth(3, 200)
        self.list.SetColumnWidth(4, 60)
        self.list.SetColumnWidth(5, 80)
        self.InitList()
               
        treesizer.Add(self.tree, 1, wx.EXPAND)
        listsizer.Add(self.list, 1, wx.EXPAND)
        treepanel.SetSizer(treesizer)
        listpanel.SetSizer(listsizer)
        bottomsizer.Add(splitter, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        '''''''''Frame'''''''''        
        framesizer = wx.BoxSizer(wx.VERTICAL)        
        framesizer.Add(topsizer, 0)
        framesizer.Add(bottomsizer, 1, wx.EXPAND)        
        self.SetSizer(framesizer)
    
    '''Start to build the file system arborescence in the tree'''
    def StartBuildFromDir(self, directory):
        rootsplit = os.path.split(directory)
        self.rootitem = self.tree.AddRoot(rootsplit[1])
        self.BuildChildrenFromDir(self.rootitem, directory)
        
    '''Build recursively the rest of the tree'''
    def BuildChildrenFromDir(self, parent, directory):
        dirlisting = os.listdir(directory)
        for child in dirlisting:
            fullpath = os.path.join(directory, child)
            if self.IsMP3(fullpath):
                fileitemid = self.tree.AppendItem(parent, child)
                if fullpath == self.lastpathselected:
                        self.tree.SelectItem(fileitemid)
            elif os.path.isdir(fullpath):
                diritemid = self.tree.AppendItem(parent, child)
                if fullpath == self.lastpathselected:
                    self.tree.SelectItem(diritemid)
                newfullpath = os.path.join(directory, child)
                self.BuildChildrenFromDir(diritemid, newfullpath)
    
    '''Action when the selection in the tree changes'''
    def OnSelChanged(self, event):
        self.list.DeleteAllItems()
        item = event.GetItem()
        fullpath = []
        while self.tree.GetItemParent(item):
            directory = self.tree.GetItemText(item)
            fullpath.insert(0, directory)
            fullpath.insert(0, '/')
            item = self.tree.GetItemParent(item)
        fullpath.insert(0, self.librarylocation)
        fullpath = ''.join(fullpath)
        if os.path.isdir(fullpath):
            self.DisplayAllChildren(fullpath)
        elif self.IsMP3(fullpath):
            self.InsertTagsIntoList(fullpath)

    '''Initialize the list with the last MP3 files displayed in this list'''
    def InitList(self):       
        self.list.DeleteAllItems()
        if os.path.isdir(self.lastpathselected):
            self.DisplayAllChildren(self.lastpathselected)
        elif self.IsMP3(self.lastpathselected):
            self.InsertTagsIntoList(self.lastpathselected)
    
    '''Insert all the children of a directory into the list'''
    def DisplayAllChildren(self, directory):
        dirlisting = os.listdir(directory)
        for child in dirlisting:
            fullpath = os.path.join(directory, child)
            if os.path.isdir(fullpath):
                self.DisplayAllChildren(fullpath)
            elif self.IsMP3(fullpath):
                self.InsertTagsIntoList(fullpath)
    
    '''Insert the tags of a MP3 file into the list'''
    def InsertTagsIntoList(self, mp3filepath):
        numitems = self.list.GetItemCount()
        audio = MP3(mp3filepath)
        try:
            self.list.InsertStringItem(numitems, ''.join(audio["TRCK"]))
        except Exception:
            print 'No track'
        self.list.SetStringItem(numitems, 1, ''.join(audio["TIT2"]))
        self.list.SetStringItem(numitems, 2, ''.join(audio["TPE1"]))
        self.list.SetStringItem(numitems, 3, ''.join(audio["TALB"]))
        self.list.SetStringItem(numitems, 4, audio["TDRC"].text[0].get_text())
        length = audio.info.length
        hours = int(length // 3600)
        minutes = int((length % 3600) // 60)
        seconds = int(length % 60)
        if hours > 0:
            self.list.SetStringItem(numitems, 5, '{0:02d}'.format(hours) + ':{0:02d}'.format(minutes) + ':{0:02d}'.format(seconds))
        else:
            self.list.SetStringItem(numitems, 5, '{0:02d}'.format(minutes) + ':{0:02d}'.format(seconds))

    '''Check if the file is a MP3 file'''
    def IsMP3(self, filepath):
        extension = os.path.splitext(filepath)[1]
        return extension == ".mp3"       

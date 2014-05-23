#!/usr/bin/env python

import wx
import os
import ConfigParser
import pygame
import math
from mutagen.mp3 import MP3
from wx.lib.pubsub import Publisher  # pylint: disable-msg=E0611
from ..utils import config
from ..controller import playlist


ID_BUTTON_PREVIOUS = wx.NewId()
ID_BUTTON_PLAY = wx.NewId()
ID_BUTTON_NEXT = wx.NewId()
ID_MENU_ADD_LIBRARY = wx.NewId()
ID_MENU_REFRESH_LIBRARY = wx.NewId()
ID_GAUGE = wx.NewId()
ID_PANEL_BUTTONS = wx.NewId()
ID_PANEL_LIST = wx.NewId()
ID_PANEL_TREE = wx.NewId()
ID_LIST = wx.NewId()
ID_TREE = wx.NewId()


class GUI(wx.Frame):
    """Build the GUI."""

    def __init__(self, parent, title, library):
        """GUI constructor."""

        # Load library controller
        self.lib = library
        # Load playlist controller
        self.playlist = playlist.Playlist()
        # Load configuration file
        conf = config.Config()
        self.configfilepath = conf.get_config_file()
        self.configparser = ConfigParser.ConfigParser()
        self.configparser.read(self.configfilepath)
        self.library_location = self.configparser.get("session", "library")
        self.saved_playlist = self.configparser.get("session", "playlist")

        # Build the GUI
        wx.Frame.__init__(self, parent, title=title)

        # Status Bar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.statusbar.SetStatusWidths([-3, -2, -2])
        # Progress Bar
        self.gauge_counter = 0
        self.gauge = wx.Gauge(self.statusbar, ID_GAUGE,
                              style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        rect = self.statusbar.GetFieldRect(2)
        self.gauge.SetPosition((rect.x + 2, rect.y + 2))
        self.gauge.SetSize((rect.width - 3, rect.height - 3))
        self.gauge.Hide()
        # Create a Publisher listener for the progress bar
        Publisher().subscribe(self.update_gauge, ("update_gauge"))

        # Menu Bar
        # Set up the menu bar
        musicmenu = wx.Menu()
        refresh_library = musicmenu.Append(ID_MENU_REFRESH_LIBRARY,
                                           "Refresh the library",
                                           " Refresh the library")
        add_library = musicmenu.Append(ID_MENU_ADD_LIBRARY, "Add a library",
                                       " Add a library")
        musicmenu.AppendSeparator()
        exit_program = musicmenu.Append(wx.ID_EXIT, "Exit",
                                        " Terminate the program")
        # Create the menu bar
        menubar = wx.MenuBar()
        menubar.Append(musicmenu, "&Music")
        self.SetMenuBar(menubar)

        # Top (control buttons)
        topsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonpanel = wx.Panel(self, ID_PANEL_BUTTONS)
        self.firstsongplayed = True
        self.songisplaying = False
        self.previousbutton = wx.BitmapButton(buttonpanel, ID_BUTTON_PREVIOUS,
                                              wx.Bitmap('./img/previous.png'),
                                              size=(40, 40))
        self.playbutton = wx.BitmapButton(buttonpanel, ID_BUTTON_PLAY,
                                          wx.Bitmap('./img/play.png'),
                                          size=(40, 40))
        self.nextbutton = wx.BitmapButton(buttonpanel, ID_BUTTON_NEXT,
                                          wx.Bitmap('./img/next.png'),
                                          size=(40, 40))
        buttonsizer.Add(self.previousbutton)
        buttonsizer.Add(self.playbutton, 0, wx.LEFT | wx.RIGHT, 5)
        buttonsizer.Add(self.nextbutton, 0, wx.RIGHT, 5)
        buttonpanel.SetSizer(buttonsizer)
        topsizer.Add(buttonpanel, 1, wx.EXPAND | wx.ALL, 10)

        # Bottom (tree and list)
        bottomsizer = wx.BoxSizer(wx.VERTICAL)
        treesizer = wx.BoxSizer(wx.VERTICAL)
        listsizer = wx.BoxSizer(wx.VERTICAL)
        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        treepanel = wx.Panel(splitter, ID_PANEL_TREE, style=wx.SUNKEN_BORDER)
        listpanel = wx.Panel(splitter, ID_PANEL_LIST, style=wx.SUNKEN_BORDER)
        splitter.SplitVertically(treepanel, listpanel)

        # Create the List containing the MP3 files
        self.list = wx.ListCtrl(listpanel, ID_LIST, size=(-1, -1),
                                style=wx.LC_REPORT)
        self.init_list()

        # Create the Tree containing the artists, albums and songs
        self.tree = wx.TreeCtrl(treepanel, ID_TREE, wx.DefaultPosition,
                                (-1, -1), wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS |
                                wx.TR_MULTIPLE)

        treesizer.Add(self.tree, 1, wx.EXPAND)
        listsizer.Add(self.list, 1, wx.EXPAND)
        treepanel.SetSizer(treesizer)
        listpanel.SetSizer(listsizer)
        bottomsizer.Add(splitter, 1,
                        wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Binds
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MENU, self.on_refresh_library, refresh_library)
        self.Bind(wx.EVT_MENU, self.on_add_library, add_library)
        self.Bind(wx.EVT_MENU, self.on_close, exit_program)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING,
                  self.resize_list, splitter)
        '''self.Bind(wx.EVT_BUTTON, self.OnChangeSong, self.previousbutton)
        self.Bind(wx.EVT_BUTTON, self.OnPlay, self.playbutton)
        self.Bind(wx.EVT_BUTTON, self.OnChangeSong, self.nextbutton)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnPlay, self.list)'''
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed, self.tree)

        # Frame
        framesizer = wx.BoxSizer(wx.VERTICAL)
        framesizer.Add(topsizer, 0)
        framesizer.Add(bottomsizer, 1, wx.EXPAND)
        self.SetSizer(framesizer)

        self.display_last_session()

    def on_size(self, event):
        """Update the position and size of the status bar gauge."""
        # wxListCtrl:
        self.resize_list("")
        # Gauge
        rect = self.statusbar.GetFieldRect(2)
        self.gauge.SetPosition((rect.x + 2, rect.y + 2))
        self.gauge.SetSize((rect.width - 3, rect.height - 3))
        # EVT_SIZE propagation stopped -> need to reload the layout
        self.Layout()

    def resize_list(self, event):
        """Resize the list's columns when its container is resized."""
        list_width = self.list.GetSize()[0] - 204
        self.list.SetColumnWidth(0, 20)
        self.list.SetColumnWidth(1, 30)
        self.list.SetColumnWidth(2, math.trunc(list_width * (40.0 / 100)))
        self.list.SetColumnWidth(3, math.trunc(list_width * (30.0 / 100)))
        self.list.SetColumnWidth(4, math.trunc(list_width * (30.0 / 100)))
        self.list.SetColumnWidth(5, 60)
        self.list.SetColumnWidth(6, 80)

    def on_close(self, event):
        """Save the configuration and close the programme."""
        configfile = open(self.configfilepath, 'w')
        self.configparser.set("session", "library", self.library_location)
        self.configparser.set("session", "playlist",
                              self.playlist.get_playlist_id_songs())
        self.configparser.write(configfile)
        self.Destroy()

    def init_list(self):
        """Initialize the list."""
        self.list.InsertColumn(0, '')
        self.list.InsertColumn(1, '#')
        self.list.InsertColumn(2, 'Title')
        self.list.InsertColumn(3, 'Artist')
        self.list.InsertColumn(4, 'Album')
        self.list.InsertColumn(5, 'Date')
        self.list.InsertColumn(6, 'Length')
        self.list.SetColumnWidth(0, 20)
        self.list.SetColumnWidth(1, 30)
        self.list.SetColumnWidth(2, 200)
        self.list.SetColumnWidth(3, 150)
        self.list.SetColumnWidth(4, 150)
        self.list.SetColumnWidth(5, 60)
        self.list.SetColumnWidth(6, 80)

    def display_last_session(self):
        """Initialize tree and list with the elements from last session."""
        if self.library_location:
            self.build_tree()
        if self.saved_playlist:
            #Parse the string: delete "[" and "]"
            song_id_list = self.saved_playlist[1:-1].split(", ")
            songs_to_add = []
            for song_id in song_id_list:
                songs_to_add.append(
                        self.lib.get_data_from_saved_playlist(song_id))
            self.playlist.update_playlist(songs_to_add)
            self.display_playlist()

    '''def OnPlay(self, event):
        """Play and pause mp3."""
        if self.firstsongplayed or (not event.GetId() is ID_BUTTON_PLAY):
            pygame.mixer.init()
            pygame.mixer.music.load(self.GetSongToPlay("play"))
            pygame.mixer.music.play()
            #self.QueuePlaylist(self.GetSongToPlay("play"))
            self.firstsongplayed = False
            self.songisplaying = True
            self.playbutton.SetBitmapLabel(wx.Bitmap('./img/pause.png'))
        else:
            if self.songisplaying:
                pygame.mixer.music.pause()
                self.songisplaying = False
                self.playbutton.SetBitmapLabel(wx.Bitmap('./img/play.png'))
            else:
                pygame.mixer.music.unpause()
                self.songisplaying = True
                self.playbutton.SetBitmapLabel(wx.Bitmap('./img/pause.png'))'''

    '''def OnChangeSong(self, event):
        """Play the previous or next mp3."""
        if self.firstsongplayed:
            pygame.mixer.init()
            if event.GetId() is ID_BUTTON_PREVIOUS:
                pygame.mixer.music.load(self.GetSongToPlay("previous"))
            if event.GetId() is ID_BUTTON_NEXT:
                pygame.mixer.music.load(self.GetSongToPlay("next"))
            pygame.mixer.music.play()
            self.firstsongplayed = False
            self.songisplaying = True
        else:
            if event.GetId() is ID_BUTTON_PREVIOUS:
                pygame.mixer.music.load(self.GetSongToPlay("previous"))
            if event.GetId() is ID_BUTTON_NEXT:
                pygame.mixer.music.load(self.GetSongToPlay("next"))
            pygame.mixer.music.play()
        self.playbutton.SetBitmapLabel(wx.Bitmap('./img/pause.png'))'''

    '''def GetSongToPlay(self, button):
        """Get the index of the song to play."""
        if button is "play":
            index = self.list.GetFirstSelected()
        elif button is "previous":
            index = self.list.GetFirstSelected() - 1
        elif button is "next":
            index = self.list.GetFirstSelected() + 1
        self.list.Select(self.list.GetFirstSelected(), False)
        if index is -1 or index > len(self.pathlist) - 1:
            index = 0       # if no song selected, play the first in the list
        self.list.Select(index, True)
        return self.pathlist[index]'''

    def on_refresh_library(self, event):
        """Refresh the library."""
        if (self.library_location):
            self.gauge_counter = 0
            self.gauge.SetRange(len(os.listdir(self.library_location)))
            self.gauge.Show()
            self.lib.add_library(self.library_location)
            self.build_tree()
            self.statusbar.SetStatusText("", 1)
            self.gauge.Hide()

    def on_add_library(self, event):
        """Add a library by opening a file chooser dialog."""
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            self.library_location = dlg.GetPath()
            self.gauge_counter = 0
            self.gauge.SetRange(len(os.listdir(self.library_location)))
            self.gauge.Show()
            self.lib.add_library(self.library_location)
            self.build_tree()
            self.statusbar.SetStatusText("", 1)
            self.gauge.Hide()
        dlg.Destroy()

    def build_tree(self):
        """Create tree by inserting the songs with their information."""
        self.tree.DeleteAllItems()
        # Add root to tree
        root = os.path.split(self.library_location)
        item_root = self.tree.AddRoot(root[1])
        # Add all artists to tree
        list_artists = self.lib.get_all_artists()
        for artist in list_artists:
            item_artist = self.tree.AppendItem(item_root, artist[1])
            self.tree.SetItemPyData(item_artist, ['Artist', artist[0]])
            # Add all artist's albums to tree
            list_albums = self.lib.get_all_albums_by_artist(artist[0])
            for album in list_albums:
                item_album = self.tree.AppendItem(item_artist, album[1])
                self.tree.SetItemPyData(item_album, ['Album', album[0]])
                # Add all artist's album's songs to tree
                list_songs = self.lib.get_all_songs_by_album(album[0])
                for song in list_songs:
                    # Don't add track if it doesn't exist
                    track = ""
                    if song[1] != "":
                        track = song[1] + " - "
                    item_song = self.tree.AppendItem(
                            item_album, track + song[2])
                    self.tree.SetItemPyData(item_song, ['Song', song[0]])

    def update_gauge(self, msg):
        """Update gauge when loading a library."""
        self.gauge_counter += 1
        self.statusbar.SetStatusText(msg.data, 1)
        self.gauge.SetValue(self.gauge_counter)

    def on_sel_changed(self, event):
        """Update list when the selection in the tree changes."""
        # Update the tree selected item list
        self.playlist.update_item_list(event.GetItem(),
                                       self.tree.GetSelections(),
                                       self.tree.IsSelected(event.GetItem()))
        # Update the playlist
        songs_to_add = []
        for item in self.playlist.get_item_list():
            songs_to_add.append(self.lib.get_data_from_selected_item(
                    self.tree.GetItemPyData(item)))
        self.playlist.update_playlist(songs_to_add)
        # Display the updated playlist in the list
        self.display_playlist()

    def display_playlist(self):
        """Display the playlist in the list."""
        self.list.DeleteAllItems()
        idx = 0
        for item in self.playlist.get_playlist():
            for song in item:
                self.list.InsertStringItem(idx, '')
                self.list.SetStringItem(idx, 1, song[1])
                self.list.SetStringItem(idx, 2, song[2])
                self.list.SetStringItem(idx, 3, song[3])
                self.list.SetStringItem(idx, 4, song[4])
                self.list.SetStringItem(idx, 5, song[5])
                self.list.SetStringItem(idx, 6, song[6])
                idx += 1

    '''def DisplayAllChildren(self, directory):
        """"Insert all the children of a directory into the list."""
        dirlisting = os.listdir(directory)
        for child in dirlisting:
            fullpath = os.path.join(directory, child)
            if os.path.isdir(fullpath):
                self.DisplayAllChildren(fullpath)
            elif self.IsMP3(fullpath):
                self.InsertTagsIntoList(fullpath)

    def InsertTagsIntoList(self, mp3filepath):
        """Insert the tags of a MP3 file into the list."""
        numitems = self.list.GetItemCount()
        self.pathlist.insert(numitems, mp3filepath)
        audio = MP3(mp3filepath)
        self.list.InsertStringItem(numitems, '')
        # TO IMPROVE
        #try:
        self.list.SetStringItem(numitems, 1, ''.join(audio["TRCK"]))
        #except Exception:
            #print 'No track'
        self.list.SetStringItem(numitems, 2, ''.join(audio["TIT2"]))
        self.list.SetStringItem(numitems, 3, ''.join(audio["TPE1"]))
        self.list.SetStringItem(numitems, 4, ''.join(audio["TALB"]))
        self.list.SetStringItem(numitems, 5, audio["TDRC"].text[0].get_text())
        length = audio.info.length
        hours = int(length // 3600)
        minutes = int((length % 3600) // 60)
        seconds = int(length % 60)
        if hours > 0:
            self.list.SetStringItem(numitems, 6,
                                    '{0:02d}'.format(hours) +
                                    ':{0:02d}'.format(minutes) +
                                    ':{0:02d}'.format(seconds))
        else:
            self.list.SetStringItem(numitems, 6,
                                    '{0:02d}'.format(minutes) +
                                    ':{0:02d}'.format(seconds))

    def IsMP3(self, filepath):
        """Check if the file is a MP3 file."""
        extension = os.path.splitext(filepath)[1]
        return extension is ".mp3"'''

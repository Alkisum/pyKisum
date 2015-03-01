#!/usr/bin/env python
# coding=utf-8
"""
Module to handle the Graphical User Interface.
"""
__author__ = "Alkisum"

import wx
import os
import ConfigParser
import math
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as publisher
from ..utils import config
from ..controller import playlist
from src.view import menubar


ID_BUTTON_PREVIOUS = wx.NewId()
ID_BUTTON_PLAY = wx.NewId()
ID_BUTTON_NEXT = wx.NewId()
ID_GAUGE = wx.NewId()
ID_PANEL_BUTTONS = wx.NewId()
ID_PANEL_LIST = wx.NewId()
ID_PANEL_TREE = wx.NewId()
ID_LIST = wx.NewId()
ID_TREE = wx.NewId()
ID_ACC_SELECT_ALL = wx.NewId()

FRAME_WIDTH = 800
FRAME_HEIGHT = 600
SASH_POSITION = FRAME_WIDTH / 4
LIST_WIDTH = FRAME_WIDTH - SASH_POSITION - 29
LIST_FIXED_SIZE = 204


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
        self.config_file_path = conf.get_config_file()
        self.config_parser = ConfigParser.ConfigParser()
        self.config_parser.read(self.config_file_path)
        self.library_location = self.config_parser.get("session", "library")
        self.saved_playlist = self.config_parser.get("session", "playlist")

        # Build the GUI
        wx.Frame.__init__(self, parent, title=title,
                          size=(FRAME_WIDTH, FRAME_HEIGHT))

        # Menu Bar
        menu_bar = menubar.MenuBar()
        self.SetMenuBar(menu_bar.get_menu_bar())

        # Status Bar
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetFieldsCount(3)
        self.status_bar.SetStatusWidths([-3, -2, -2])
        # Progress Bar
        self.gauge_counter = 0
        self.gauge = wx.Gauge(self.status_bar, ID_GAUGE,
                              style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        rect = self.status_bar.GetFieldRect(2)
        self.gauge.SetPosition((rect.x + 2, rect.y + 2))
        self.gauge.SetSize((rect.width - 3, rect.height - 3))
        self.gauge.Hide()
        # Create a Publisher listener for the progress bar
        publisher.subscribe(self.update_gauge, "update_gauge")

        # Bottom (tree and list)
        bottom_sizer = wx.BoxSizer(wx.VERTICAL)
        tree_sizer = wx.BoxSizer(wx.VERTICAL)
        list_sizer = wx.BoxSizer(wx.VERTICAL)
        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        tree_panel = wx.Panel(splitter, ID_PANEL_TREE, style=wx.SUNKEN_BORDER)
        list_panel = wx.Panel(splitter, ID_PANEL_LIST, style=wx.SUNKEN_BORDER)
        splitter.SplitVertically(tree_panel, list_panel)
        splitter.SetSashPosition(SASH_POSITION)

        # Create the List containing the MP3 files
        self.list = wx.ListCtrl(list_panel, ID_LIST, size=(-1, -1),
                                style=wx.LC_REPORT)
        self.init_list()

        # Create the Tree containing the artists, albums and songs
        self.tree = wx.TreeCtrl(tree_panel, ID_TREE, wx.DefaultPosition,
                                (-1, -1), wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS |
                                wx.TR_MULTIPLE)

        tree_sizer.Add(self.tree, 1, wx.EXPAND)
        list_sizer.Add(self.list, 1, wx.EXPAND)
        tree_panel.SetSizer(tree_sizer)
        list_panel.SetSizer(list_sizer)
        bottom_sizer.Add(splitter, 1,
                         wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 10)

        # Shortcuts
        self.Bind(wx.EVT_MENU, self.on_select_all, id=ID_ACC_SELECT_ALL)
        acc_table = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('A'),
                                          ID_ACC_SELECT_ALL)])
        self.SetAcceleratorTable(acc_table)

        # Binds
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MENU, self.on_refresh_library,
                  menu_bar.get_refresh_library_item())
        self.Bind(wx.EVT_MENU, self.on_add_folder,
                  menu_bar.get_add_folder_item())
        self.Bind(wx.EVT_MENU, self.on_close,
                  menu_bar.get_exit_item())
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING,
                  self.resize_list, splitter)
        self.Bind(wx.EVT_TREE_SEL_CHANGED,
                  self.on_sel_changed, self.tree)

        # Frame
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        # frame_sizer.Add(top_sizer, 0)
        frame_sizer.Add(bottom_sizer, 1, wx.EXPAND)
        self.SetSizer(frame_sizer)

        self.display_last_session()

        # Flags
        self.select = True
        self.size_cnt = 0

    def on_size(self, event):
        """Update the position and size of the status bar gauge.
        :param event: event that triggers the function"""
        # List
        self.resize_list("")
        # Gauge
        rect = self.status_bar.GetFieldRect(2)
        self.gauge.SetPosition((rect.x + 2, rect.y + 2))
        self.gauge.SetSize((rect.width - 3, rect.height - 3))
        # EVT_SIZE propagation stopped -> need to reload the layout
        self.Layout()

    def resize_list(self, event):
        """Resize the list's columns when its container is re-sized.
        :param event: event that triggers the function"""
        # Skip the 2 first size events
        if self.size_cnt < 2:
            list_width = LIST_WIDTH - LIST_FIXED_SIZE
            self.size_cnt += 1
        # After the 2 first events, get new list size
        else:
            list_width = self.list.GetSize()[0] - LIST_FIXED_SIZE
        self.list.SetColumnWidth(0, 20)
        self.list.SetColumnWidth(1, 30)
        self.list.SetColumnWidth(2, math.trunc(list_width * (40.0 / 100)))
        self.list.SetColumnWidth(3, math.trunc(list_width * (30.0 / 100)))
        self.list.SetColumnWidth(4, math.trunc(list_width * (30.0 / 100)))
        self.list.SetColumnWidth(5, 60)
        self.list.SetColumnWidth(6, 80)

    def on_close(self, event):
        """Save the configuration and close the programme.
        :param event: event that triggers the function"""
        configfile = open(self.config_file_path, 'w')
        self.config_parser.set("session", "library", self.library_location)
        self.config_parser.set("session", "playlist",
                               self.playlist.get_playlist_id_songs())
        self.config_parser.write(configfile)
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
            # Parse the string: delete "[" and "]"
            song_id_list = self.saved_playlist[1:-1].split(", ")
            songs_to_add = []
            for song_id in song_id_list:
                songs_to_add.append(
                    self.lib.get_data_from_saved_playlist(song_id))
            self.playlist.update_playlist(songs_to_add)
            self.display_playlist()

    def on_refresh_library(self, event):
        """Refresh the library.
        :param event: event that triggers the function"""
        if self.library_location:
            self.gauge_counter = 0
            self.gauge.SetRange(len(os.listdir(self.library_location)))
            self.gauge.Show()
            self.lib.add_library(self.library_location)
            self.build_tree()
            self.status_bar.SetStatusText("", 1)
            self.gauge.Hide()

    def on_add_folder(self, event):
        """Add a library by opening a file chooser dialog.
        :param event: event that triggers the function"""
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            self.library_location = dlg.GetPath()
            self.gauge_counter = 0
            self.gauge.SetRange(len(os.listdir(self.library_location)))
            self.gauge.Show()
            self.lib.add_library(self.library_location)
            self.build_tree()
            self.status_bar.SetStatusText("", 1)
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
        """Update gauge when loading a library.
        :param msg: message to display in the status bar"""
        self.gauge_counter += 1
        self.status_bar.SetStatusText(msg.data, 1)
        self.gauge.SetValue(self.gauge_counter)

    def on_sel_changed(self, event):
        """Update list when the selection in the tree changes.
        :param event: event that triggers the function"""
        if self.select:
            # Update the playlist
            songs_to_add = []
            for item in self.tree.GetSelections():
                if not self.tree.IsSelected(self.tree.GetItemParent(item)):
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

    def on_select_all(self, event):
        """Select all the children (artists) in the tree
        :param event: event that triggers the function"""
        if wx.Window.FindFocus() == self.tree:
            self.select = False
            child = self.tree.GetFirstChild(self.tree.GetRootItem())[0]
            while child.IsOk():
                next_sibling = self.tree.GetNextSibling(child)
                if not next_sibling.IsOk():
                    # Last item to select: allow trigger on_sel_changed
                    self.select = True
                self.tree.SelectItem(child)
                child = next_sibling
        elif wx.Window.FindFocus() == self.list:
            idx = 0
            while idx < self.list.GetItemCount():
                self.list.Select(idx)
                idx += 1

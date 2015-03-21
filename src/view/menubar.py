#!/usr/bin/env python
# coding=utf-8
"""
Module to build the menu bar.
"""
__author__ = "Alkisum"

import wx

ID_ITEM_ADD_LIBRARY = wx.NewId()
ID_ITEM_REFRESH_LIBRARY = wx.NewId()
ID_ITEM_RENAME_ALBUM_DIR = wx.NewId()


class MenuBar(object):
    """Build the menu bar."""

    def __init__(self):
        """MenuBar constructor."""

        # Music menu
        music_menu = wx.Menu()
        self.refresh_library_item = music_menu.Append(ID_ITEM_REFRESH_LIBRARY,
                                                      "Refresh Library",
                                                      " Refresh Library")
        self.add_folder_item = music_menu.Append(ID_ITEM_ADD_LIBRARY,
                                                 "Add a Folder...",
                                                 " Add a Folder...")
        music_menu.AppendSeparator()
        self.exit_item = music_menu.Append(wx.ID_EXIT,
                                           "Exit",
                                           " Terminate the program")

        # Directory menu
        dir_menu = wx.Menu()
        self.rename_album_directory_item = dir_menu.Append(
            ID_ITEM_RENAME_ALBUM_DIR, "Rename Album Directory",
            " Rename Album Directory")

        # Create the menu bar
        self.menu_bar = wx.MenuBar()
        self.menu_bar.Append(music_menu, "&Music")
        self.menu_bar.Append(dir_menu, "&Directory")

    def get_menu_bar(self):
        """Return the menu bar."""
        return self.menu_bar

    def get_refresh_library_item(self):
        """Return the refresh library item."""
        return self.refresh_library_item

    def get_add_folder_item(self):
        """Return the add folder item."""
        return self.add_folder_item

    def get_exit_item(self):
        """Return the exit item."""
        return self.exit_item

    def get_rename_album_directory_item(self):
        """Return the rename album directory item."""
        return self.rename_album_directory_item

    def enable_rename_album_directory_item(self, enabled):
        """Enable or disable the rename album directory item.
        :param enabled: Item enabled if True, disabled if False"""
        self.menu_bar.Enable(ID_ITEM_RENAME_ALBUM_DIR, enabled)
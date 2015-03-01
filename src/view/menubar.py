#!/usr/bin/env python
# coding=utf-8
"""
Module to build the menu bar.
"""
__author__ = "Alkisum"

import wx

ID_MENU_ADD_LIBRARY = wx.NewId()
ID_MENU_REFRESH_LIBRARY = wx.NewId()


class MenuBar():
    """Build the menu bar."""

    def __init__(self):
        """MenuBar constructor."""

        # Menu Bar
        # Set up the menu bar
        music_menu = wx.Menu()
        self.refresh_library_item = music_menu.Append(ID_MENU_REFRESH_LIBRARY,
                                                      "Refresh Library",
                                                      " Refresh Library")
        self.add_folder_item = music_menu.Append(ID_MENU_ADD_LIBRARY,
                                                 "Add a Folder...",
                                                 " Add a Folder...")
        music_menu.AppendSeparator()
        self.exit_item = music_menu.Append(wx.ID_EXIT,
                                           "Exit",
                                           " Terminate the program")
        # Create the menu bar
        self.menu_bar = wx.MenuBar()
        self.menu_bar.Append(music_menu, "&Music")

    def get_menu_bar(self):
        """Return the menu bar."""
        return self.menu_bar

    def get_refresh_library_item(self):
        """Return the refresh library item from menu."""
        return self.refresh_library_item

    def get_add_folder_item(self):
        """Return the add folder item from menu."""
        return self.add_folder_item

    def get_exit_item(self):
        """Return the exit item from menu."""
        return self.exit_item

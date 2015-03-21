#!/usr/bin/env python
# coding=utf-8
"""
Module to make file operations.
"""
__author__ = "Alkisum"

from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as publisher
import os


class FileHandler(object):
    """Class making file operations."""

    def __init__(self):
        """FileHandler constructor."""

    @staticmethod
    def rename_albums(lib, expr):
        """Rename album directories according to the given expression.
        :param lib: library used to get the selected albums
        :param expr: expression given by user"""
        album_list = lib.get_sel_album_list()
        for album in album_list:
            artist_path = lib.get_artist_by_id(album[5])[2].decode('utf-8')
            new_name = expr.replace("%b", album[1].decode('utf-8')) \
                .replace("%d", album[2].decode('utf-8'))
            new_name = FileHandler.format_filename(new_name)
            new_path = artist_path + os.sep + new_name
            # Update progress bar
            publisher.sendMessage("update_gauge", new_name)
            # Rename album directory
            old_path = album[4].decode('utf-8')
            if os.path.exists(old_path):
                os.rename(old_path, new_path)

    @staticmethod
    def format_filename(s):
        """Take a string and return a valid filename constructed from the string.
        Uses a white list approach: any characters not present in valid_chars
        are removed.
        :param s: string to format"""
        valid_chars = "-_.()[]&!' "
        filename = ""
        for c in s:
            if c in valid_chars or c.isalnum():
                filename += c
            else:
                filename += " "
        return filename.strip()

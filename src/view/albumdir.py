#!/usr/bin/env python
# coding=utf-8
"""
Module to display the dialog for renaming album directories.
"""
__author__ = "Alkisum"


import wx


ID_DIALOG = wx.NewId()
ID_TEXT_FIELD = wx.NewId()
ID_IMG_HELP = wx.NewId()
ID_BUTTON_CANCEL = wx.NewId()
ID_BUTTON_RENAME = wx.NewId()

DIALOG_WIDTH = 300
DIALOG_HEIGHT = 70


class AlbumDir(wx.Dialog):
    """Build the Dialog."""

    def __init__(self, parent, title):
        """Dialog constructor."""

        self.parent = parent

        wx.Dialog.__init__(self, parent, ID_DIALOG, title,
                           size=(DIALOG_WIDTH, DIALOG_HEIGHT))

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text_field = wx.TextCtrl(self, ID_TEXT_FIELD)
        png = wx.StaticBitmap(self, ID_IMG_HELP,
                              wx.Bitmap("./img/help.png", wx.BITMAP_TYPE_ANY))
        png.SetToolTip(wx.ToolTip(
            "%a:\tartist\n"
            "%b:\talbum\n"
            "%d:\tdate"
            # "%n:\ttrack\n"
            # "%t:\ttitle"
        ))
        text_sizer.Add(self.text_field, 1, wx.EXPAND | wx.LEFT | wx.TOP, 5)
        text_sizer.Add(png, 0, wx.EXPAND | wx.RIGHT | wx.TOP, 5)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_cancel = wx.Button(self, ID_BUTTON_CANCEL, "Cancel")
        button_rename = wx.Button(self, ID_BUTTON_RENAME, "Rename")
        button_sizer.Add(button_cancel, 1, wx.EXPAND | wx.ALL, 5)
        button_sizer.Add(button_rename, 1, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(text_sizer, 0, wx.EXPAND)
        main_sizer.Add(button_sizer, 1, wx.EXPAND)

        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_BUTTON, self.on_cancel_clicked, button_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_rename_clicked, button_rename)

    def on_cancel_clicked(self, event):
        """Triggered when the cancel button is clicked.
        :param event: event that triggers the function"""
        self.Destroy()

    def on_rename_clicked(self, event):
        """Triggered when the rename button is clicked.
        :param event: event that triggers the function"""
        self.Destroy()
        self.parent.rename_album_directory(self.text_field.GetValue())

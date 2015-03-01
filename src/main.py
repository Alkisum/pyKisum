#!/usr/bin/env python
# coding=utf-8
"""
Main module that initializes the program.
"""
__author__ = "Alkisum"

import wx
from src.model import database
from src.view import gui
from src.controller import library

app = wx.App(False)
db = database.Database()
lib = library.Library(db)
frame = gui.GUI(None, "pyKisum", lib)
frame.SetIcon(wx.Icon('img/icon.ico', wx.BITMAP_TYPE_ICO))
frame.Show()
app.MainLoop()
db.close_database()

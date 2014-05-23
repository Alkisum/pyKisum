#!/usr/bin/env python

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

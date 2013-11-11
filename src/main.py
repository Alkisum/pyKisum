#!/usr/bin/env python

import gui
import database
import wx


app = wx.App(False)
db = database.DataBase()
frame = gui.GUI(None, "pyKisum")
frame.Show()
app.MainLoop()
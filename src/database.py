#!/usr/bin/env python

import sqlite3 as db
import sys

class DataBase():
    def __init__(self):
        connexion = None
        try:
            connexion = db.connect('library.db')
            cursor = connexion.cursor()
            cursor.execute('SELECT SQLITE_VERSION()')
            data = cursor.fetchone()
            print "SQLite version: %s" % data
        except db.Error, e:
            print "Error %s" % e.args[0]
            sys.exit(1)
        finally:
            if connexion:
                connexion.close()
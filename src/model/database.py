#!/usr/bin/env python
# coding=utf-8
"""
Module to handle the database.
Functions are called from the controllers to make operations to database.
"""
__author__ = "Alkisum"

import sqlite3 as db


class Database(object):
    """Class which handles the SQLite database."""

    def __init__(self):
        """Database constructor."""
        self.connection = None
        self.cursor = None
        try:
            self.connect_database()
        except db.Error, e:
            print "Error %s" % e.args[0]
            self.close_database()

    def connect_database(self):
        """Connect to the database."""
        self.connection = db.connect('library.db')
        self.connection.text_factory = str
        self.cursor = self.connection.cursor()

    def is_table_exist(self, table_name):
        """Check if a table exist.
        :param table_name: table name"""
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,))
        return self.cursor.fetchone()

    def create_database(self):
        """Create the database and the tables."""
        self.cursor.execute("DROP TABLE IF EXISTS Artist")
        self.cursor.execute('''CREATE TABLE Artist(
            art_id INTEGER PRIMARY KEY AUTOINCREMENT,
            art_name TEXT,
            art_path TEXT
            )''')
        self.cursor.execute("DROP TABLE IF EXISTS Album")
        self.cursor.execute('''CREATE TABLE Album(
            alb_id INTEGER PRIMARY KEY AUTOINCREMENT,
            alb_name TEXT,
            alb_date TEXT,
            alb_cover TEXT,
            alb_path TEXT,
            alb_art_id INTEGER,
            FOREIGN KEY(alb_art_id) REFERENCES Artist(art_id)
            )''')
        self.cursor.execute("DROP TABLE IF EXISTS Song")
        self.cursor.execute('''CREATE TABLE Song(
            son_id INTEGER PRIMARY KEY AUTOINCREMENT,
            son_track TEXT,
            son_title TEXT,
            son_length TEXT,
            son_path TEXT,
            son_alb_id INTEGER,
            FOREIGN KEY(son_alb_id) REFERENCES Album(alb_id)
            )''')

    def close_database(self):
        """Close the database."""
        if self.connection:
            self.connection.close()

    def insert_artist(self, art_name, art_path):
        """Insert the artist into the database.
        :param art_name: artist name
        :param art_path: artist directory path"""
        self.cursor.execute("INSERT INTO Artist VALUES (?, ?, ?)",
                            (None, art_name, art_path))

    def insert_album(self, alb_name, alb_date, alb_cover, alb_path, alb_art_id):
        """Insert the album into the database.
        :param alb_name: album name
        :param alb_date: album date
        :param alb_cover: album cover
        :param alb_path: album directory path
        :param alb_art_id: artist id"""
        self.cursor.execute("INSERT INTO Album VALUES (?, ?, ?, ?, ?, ?)",
                            (None, alb_name, alb_date, alb_cover, alb_path,
                             alb_art_id,))

    def insert_song(self, son_track, son_title, son_length, son_path,
                    son_alb_id):
        """Insert the song into the database.
        :param son_track: song track
        :param son_title: song title
        :param son_length: song length
        :param son_path: song path
        :param son_alb_id: album id"""
        self.cursor.execute("INSERT INTO Song VALUES (?, ?, ?, ?, ?, ?)",
                            (None, son_track, son_title, son_length,
                             son_path, son_alb_id,))

    def get_last_row_id(self):
        """Return the last inserted row id."""
        return self.cursor.lastrowid

    def get_all_artists(self):
        """Return all the artists."""
        self.cursor.execute("SELECT * FROM Artist ORDER BY art_name")
        return self.cursor.fetchall()

    def get_artist_by_name(self, art_name):
        """Return the artist which matches the given name.
        :param art_name: artist name"""
        self.cursor.execute("SELECT art_id FROM Artist WHERE art_name=?",
                            (art_name,))
        return self.cursor.fetchone()

    def get_artist_by_id(self, art_id):
        """Return the artist that matches the given id.
        :param art_id: artist id"""
        self.cursor.execute("SELECT * FROM Artist WHERE art_id=?",
                            (art_id,))
        return self.cursor.fetchone()

    def get_all_albums_by_artist(self, alb_art_id):
        """Return all the albums attached to the given artist.
        :param alb_art_id: artist id"""
        self.cursor.execute(
            '''SELECT * FROM Album WHERE alb_art_id=?
            ORDER BY alb_date, alb_name''', (alb_art_id,))
        return self.cursor.fetchall()

    def get_album_by_name_and_artist(self, alb_name, alb_art_id):
        """Return the album which matches the given name and artist id.
        :param alb_name: album name
        :param alb_art_id: artist id"""
        self.cursor.execute(
            "SELECT alb_id FROM Album WHERE alb_name=? AND alb_art_id=?",
            (alb_name, alb_art_id,))
        return self.cursor.fetchone()

    def get_album_by_id(self, alb_id):
        """Return the album which matches the album id.
        :param alb_id: album id"""
        self.cursor.execute(
            "SELECT * FROM Album where alb_id=?", (alb_id,))
        return self.cursor.fetchone()

    def get_all_songs_by_album(self, son_alb_id):
        """Return all the songs attached to the given album.
        :param son_alb_id: album id"""
        self.cursor.execute(
            "SELECT * FROM Song WHERE son_alb_id=? ORDER BY son_track",
            (son_alb_id,))
        return self.cursor.fetchall()

    def get_all_info_by_artist(self, art_id):
        """Return all the songs attached to the given artist.
        :param art_id: artist id"""
        self.cursor.execute(
            '''SELECT son_id, son_track, son_title, art_name,
            alb_name, alb_date, son_length
            FROM Song, Album, Artist
            WHERE son_alb_id=alb_id
            AND alb_art_id=art_id
            AND art_id=?
            ORDER BY alb_date, alb_name, son_track''',
            (art_id,))
        return self.cursor.fetchall()

    def get_all_info_by_album(self, alb_id):
        """Return all the songs attached to the given album.
        :param alb_id: album id"""
        self.cursor.execute(
            '''SELECT son_id, son_track, son_title, art_name,
            alb_name, alb_date, son_length
            FROM Song, Album, Artist
            WHERE son_alb_id=alb_id
            AND alb_id=?
            AND alb_art_id=art_id
            ORDER BY alb_date, alb_name, son_track''',
            (alb_id,))
        return self.cursor.fetchall()

    def get_all_info_by_song(self, son_id):
        """Return the song with the given id.
        :param son_id: song id"""
        self.cursor.execute(
            '''SELECT son_id, son_track, son_title, art_name,
            alb_name, alb_date, son_length
            FROM Song, Album, Artist
            WHERE son_id=?
            AND son_alb_id=alb_id
            AND alb_art_id=art_id
            ORDER BY alb_date, alb_name, son_track''',
            (son_id,))
        return self.cursor.fetchall()

    def commit(self):
        """Commit the changes."""
        self.connection.commit()

    def print_database(self):
        """Print information about the database."""
        self.cursor.execute("SELECT * FROM Artist")
        print(self.cursor.fetchall())

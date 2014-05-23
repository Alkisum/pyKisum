#!/usr/bin/env python

import sqlite3 as db


class Database():
    """Class which handles the SQLite database."""

    def __init__(self):
        """Database constructor."""
        self.connexion = None
        self.cursor = None
        try:
            self.connect_database()
        except db.Error, e:
            print "Error %s" % e.args[0]
            self.close_database()

    def connect_database(self):
        """Connect to the database."""
        self.connexion = db.connect('library.db')
        self.cursor = self.connexion.cursor()

    def is_table_exist(self, table_name):
        """Check if a table exist."""
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,))
        return self.cursor.fetchone()

    def create_database(self):
        """Create the database and the tables."""
        self.cursor.execute("DROP TABLE IF EXISTS Artist")
        self.cursor.execute('''CREATE TABLE Artist(
            art_id INTEGER PRIMARY KEY AUTOINCREMENT,
            art_name TEXT
            )''')
        self.cursor.execute("DROP TABLE IF EXISTS Album")
        self.cursor.execute('''CREATE TABLE Album(
            alb_id INTEGER PRIMARY KEY AUTOINCREMENT,
            alb_name TEXT,
            alb_date TEXT,
            alb_cover TEXT,
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
        if self.connexion:
            self.connexion.close()

    def insert_artist(self, art_name):
        """Insert the artist into the database."""
        self.cursor.execute("INSERT INTO Artist VALUES (?, ?)",
                            (None, art_name,))

    def insert_album(self, alb_name, alb_date, alb_cover, alb_art_id):
        """Insert the album into the database."""
        self.cursor.execute("INSERT INTO Album VALUES (?, ?, ?, ?, ?)",
                            (None, alb_name, alb_date, alb_cover,
                             alb_art_id,))

    def insert_song(self, son_track, son_title, son_length, son_path,
                    son_alb_id):
        """Insert the song into the database."""
        self.cursor.execute("INSERT INTO Song VALUES (?, ?, ?, ?, ?, ?)",
                            (None, son_track, son_title, son_length,
                             buffer(son_path), son_alb_id,))

    def get_last_row_id(self):
        """Return the last inserted row id."""
        return self.cursor.lastrowid

    def get_all_artists(self):
        """Return all the artists."""
        self.cursor.execute("SELECT * FROM Artist ORDER BY art_name")
        return self.cursor.fetchall()

    def get_artist_by_name(self, art_name):
        """Return the artist which matches the given name."""
        self.cursor.execute("SELECT art_id FROM Artist WHERE art_name=?",
                            (art_name,))
        return self.cursor.fetchone()

    def get_all_albums_by_artist(self, alb_art_id):
        """Return all the albums attached to the given artist."""
        self.cursor.execute(
            '''SELECT * FROM Album WHERE alb_art_id=?
            ORDER BY alb_date, alb_name''', (alb_art_id,))
        return self.cursor.fetchall()

    def get_album_by_name(self, alb_name, alb_art_id):
        """Return the album which matches the given name and artist id."""
        self.cursor.execute(
            "SELECT alb_id FROM Album WHERE alb_name=? AND alb_art_id=?",
            (alb_name, alb_art_id,))
        return self.cursor.fetchone()

    def get_all_songs_by_album(self, son_alb_id):
        """Return all the songs attached to the given album."""
        self.cursor.execute(
            "SELECT * FROM Song WHERE son_alb_id=? ORDER BY son_track",
            (son_alb_id,))
        return self.cursor.fetchall()

    def get_all_info_by_artist(self, art_id):
        """Return all the songs attached to the given artist."""
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
        """Return all the songs attached to the given album."""
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
        """Return the song with the given id."""
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
        self.connexion.commit()

    def print_database(self):
        """Print information about the database."""
        self.cursor.execute("SELECT * FROM Artist")
        print(self.cursor.fetchall())

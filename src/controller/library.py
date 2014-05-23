'''
Created on 8 mars 2014

@author: Alkisum
'''

import os
from mutagen.mp3 import MP3
from wx.lib.pubsub import Publisher  # pylint: disable-msg=E0611


class Library():
    """Class which controls the library."""

    def __init__(self, pdatabase):
        """Library constructor."""
        self.db = pdatabase
        self.root_directory = ""
        self.check_database()

    def check_database(self):
        """Check if the tables (Artist, Album and Song) exist."""
        if not self.db.is_table_exist("Artist")\
                or not self.db.is_table_exist("Album")\
                or not self.db.is_table_exist("Song"):
            self.db.create_database()

    def get_data_from_selected_item(self, item_info):
        """Return all information concerning the selected item."""
        if item_info[0] == "Artist":
            return self.db.get_all_info_by_artist(item_info[1])
        if item_info[0] == "Album":
            return self.db.get_all_info_by_album(item_info[1])
        if item_info[0] == "Song":
            return self.db.get_all_info_by_song(item_info[1])

    def get_data_from_saved_playlist(self, son_id):
        """Return all the songs to load the saved playlist."""
        return self.db.get_all_info_by_song(son_id)

    def get_all_artists(self):
        """Return all the artists sorted by their name."""
        return self.db.get_all_artists()

    def get_all_albums_by_artist(self, alb_art_id):
        """Return all the artist's albums sorted by their date."""
        return self.db.get_all_albums_by_artist(alb_art_id)

    def get_all_songs_by_album(self, son_alb_id):
        """Return all the album's songs sorted by their track."""
        return self.db.get_all_songs_by_album(son_alb_id)

    def add_library(self, directory):
        """Add a library: create database and insert data."""
        self.db.create_database()
        self.root_directory = directory
        self.browse_directory(directory)
        self.db.commit()

    def browse_directory(self, directory):
        """Browse the library directory and call the insertion function."""
        dirlisting = os.listdir(directory)
        for child in dirlisting:
            if directory == self.root_directory:
                # Update progress bar
                Publisher().sendMessage(("update_gauge"), child)
            fullpath = os.path.join(directory, child)
            if self.is_mp3(fullpath):
                self.insert_mp3_into_database(fullpath)
            elif os.path.isdir(fullpath):
                newfullpath = os.path.join(directory, child)
                self.browse_directory(newfullpath)

    def insert_mp3_into_database(self, mp3filepath):
        """Insert the MP3 tags into the database."""
        # Get all the data from the MP3 tag
        tag = MP3(mp3filepath)
        try:
            artist_name = ''.join(tag["TPE1"])
        except KeyError:
            artist_name = "Unknown artist"
        try:
            album_name = ''.join(tag["TALB"])
        except KeyError:
            album_name = "Unknown album"
        try:
            album_date = tag["TDRC"].text[0].get_text()
        except KeyError:
            album_date = ""
        try:
            album_cover = "Temp cover path"
        except KeyError:
            album_cover = ""
        try:
            song_track = ''.join(tag["TRCK"])
        except KeyError:
            song_track = ""
        try:
            song_title = ''.join(tag["TIT2"])
        except KeyError:
            song_title = "Unknown title"
        try:
            song_length = self.get_length(tag.info.length)
        except KeyError:
            song_length = ""
        # Get the artist's id, insert the artist if it doesn't exist
        artist_id = self.db.get_artist_by_name(artist_name)
        if not artist_id:
            self.db.insert_artist(artist_name)
            artist_id = self.db.get_last_row_id()
        else:
            artist_id = artist_id[0]
        # Get the album's id, insert the album if it doesn't exist
        album_id = self.db.get_album_by_name(album_name, artist_id)
        if not album_id:
            self.db.insert_album(album_name, album_date, album_cover,
                                    artist_id)
            album_id = self.db.get_last_row_id()
        else:
            album_id = album_id[0]
        # Insert the song with the artist's album's id
        self.db.insert_song(song_track, song_title, song_length,
                               mp3filepath, album_id)

    def get_length(self, length):
        """Return a string containing a song's length."""
        hours = int(length // 3600)
        minutes = int((length % 3600) // 60)
        seconds = int(length % 60)
        if hours > 0:
            length = '{0:02d}'.format(hours)\
            + ':{0:02d}'.format(minutes)\
            + ':{0:02d}'.format(seconds)
        else:
            length = '{0:02d}'.format(minutes)\
            + ':{0:02d}'.format(seconds)
        return length

    def is_mp3(self, filepath):
        """Check if the file is a MP3 file."""
        extension = os.path.splitext(filepath)[1]
        return extension == ".mp3"

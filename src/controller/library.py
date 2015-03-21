#!/usr/bin/env python
# coding=utf-8
"""
Module to handle the library.
Functions are called from the view to make database operations.
"""
__author__ = "Alkisum"

import os
from mutagen.mp3 import MP3
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as publisher


class Library(object):
    """Class which controls the library."""

    def __init__(self, data_base):
        """Library constructor."""
        self.db = data_base
        self.root_directory = ""
        self.check_database()
        self.sel_album_list = []
        self.dir_level = 0

    def check_database(self):
        """Check if the tables (Artist, Album and Song) exist."""
        if not self.db.is_table_exist("Artist") \
                or not self.db.is_table_exist("Album") \
                or not self.db.is_table_exist("Song"):
            self.db.create_database()

    def get_data_from_selected_item(self, item_info):
        """Return all information concerning the selected item.
        :param item_info: item to get data from"""
        if item_info[0] == "Artist":
            artist_albums = self.get_all_albums_by_artist(item_info[1])
            for album in artist_albums:
                self.sel_album_list.append(album)
            return self.db.get_all_info_by_artist(item_info[1])
        if item_info[0] == "Album":
            self.sel_album_list.append(self.db.get_album_by_id(item_info[1]))
            return self.db.get_all_info_by_album(item_info[1])
        if item_info[0] == "Song":
            return self.db.get_all_info_by_song(item_info[1])

    def get_data_from_saved_playlist(self, son_id):
        """Return all the songs to load the saved playlist.
        :param son_id: song id"""
        return self.db.get_all_info_by_song(son_id)

    def get_all_artists(self):
        """Return all the artists sorted by their name."""
        return self.db.get_all_artists()

    def get_artist_by_id(self, art_id):
        """Return the artist that matches the given id.
        :param art_id: artist id"""
        return self.db.get_artist_by_id(art_id)

    def get_all_albums_by_artist(self, alb_art_id):
        """Return all the artist's albums sorted by their date.
        :param alb_art_id: album id"""
        return self.db.get_all_albums_by_artist(alb_art_id)

    def get_all_songs_by_album(self, son_alb_id):
        """Return all the album's songs sorted by their track.
        :param son_alb_id: song id"""
        return self.db.get_all_songs_by_album(son_alb_id)

    def add_library(self, directory):
        """Add a library: create database and insert data.
        :param directory: folder to add to database"""
        self.db.create_database()
        self.root_directory = directory
        self.browse_directory(directory)
        self.db.commit()

    def browse_directory(self, directory):
        """Browse the library directory and call the insertion function.
        :param directory: directory to browse"""
        dir_listing = os.listdir(directory)
        child_counter = 0
        for child in dir_listing:
            child_counter += 1
            if directory == self.root_directory:
                self.dir_level = 0
                # Update progress bar
                publisher.sendMessage("update_gauge", child)
            full_path = os.path.join(directory, child)
            if self.is_mp3(full_path):
                if self.dir_level == 2:
                    # When the level is not 2, this means that the mp3 file
                    # doesn't have a structure like artist/album/song.mp3
                    # do not add this mp3 to the database
                    self.insert_mp3_into_database(full_path)
            elif os.path.isdir(full_path):
                new_full_path = os.path.join(directory, child)
                self.dir_level += 1
                self.browse_directory(new_full_path)
            if child_counter == len(dir_listing):
                self.dir_level -= 1

    def insert_mp3_into_database(self, mp3_file_path):
        """Insert the MP3 tags into the database.
        :param mp3_file_path: mp3 file containing tags to add to database"""
        # Get all the data from the MP3 tag
        tag = MP3(mp3_file_path)
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
        # Get paths
        album_path = os.path.abspath(os.path.join(mp3_file_path, os.pardir))
        artist_path = os.path.abspath(os.path.join(album_path, os.pardir))
        # Get the artist's id, insert the artist if it doesn't exist
        artist_id = self.db.get_artist_by_name(artist_name)
        if not artist_id:
            self.db.insert_artist(artist_name, artist_path)
            artist_id = self.db.get_last_row_id()
        else:
            artist_id = artist_id[0]
        # Get the album's id, insert the album if it doesn't exist
        album_id = self.db.get_album_by_name_and_artist(album_name, artist_id)
        if not album_id:
            self.db.insert_album(album_name, album_date, album_cover,
                                 album_path, artist_id)
            album_id = self.db.get_last_row_id()
        else:
            album_id = album_id[0]
        # Insert the song with the artist's album's id
        self.db.insert_song(song_track, song_title, song_length,
                            mp3_file_path, album_id)

    @staticmethod
    def get_length(length):
        """Return a string containing a song's length.
        :param length: length to convert"""
        hours = int(length // 3600)
        minutes = int((length % 3600) // 60)
        seconds = int(length % 60)
        if hours > 0:
            length = '{0:02d}'.format(hours) \
                     + ':{0:02d}'.format(minutes) \
                     + ':{0:02d}'.format(seconds)
        else:
            length = '{0:02d}'.format(minutes) \
                     + ':{0:02d}'.format(seconds)
        return length

    @staticmethod
    def is_mp3(file_path):
        """Check if the file is a MP3 file.
        :param file_path: mp3 file to check"""
        extension = os.path.splitext(file_path)[1]
        return extension == ".mp3"

    def get_sel_album_list(self):
        """Return the list of selected albums."""
        return self.sel_album_list

    def clear_sel_album_list(self):
        """Clear the list of selected albums."""
        del self.sel_album_list[:]

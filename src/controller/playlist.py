#!/usr/bin/env python
# coding=utf-8
"""
Module to handle the playlist.
The playlist is updated according to items selected in the Tree.
"""
__author__ = "Alkisum"


class Playlist(object):
    """Class which controls the playlist."""

    def __init__(self):
        """Playlist constructor."""
        self.item_list = []
        self.playlist = []

    def update_playlist(self, song_list):
        """Update the playlist.
        :param song_list: list of songs to set"""
        del self.playlist[:]
        self.playlist = song_list

    def get_item_list(self):
        """Return the item list."""
        return self.item_list

    def get_playlist(self):
        """Return the playlist."""
        return self.playlist

    def get_playlist_id_songs(self):
        """Return the playlist with the songs id."""
        playlist_id_songs = []
        if self.playlist:
            for playlist_part in self.playlist:
                for song in playlist_part:
                    playlist_id_songs.append(song[0])
        return playlist_id_songs

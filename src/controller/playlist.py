'''
Created on 12 mars 2014

@author: Alkisum
'''

import wx


class Playlist():
    """"Class which controls the playlist."""

    def __init__(self):
        """Playlist constructor."""
        self.item_list = []
        self.playlist = []

    def update_item_list(self, item, selected_items, item_is_selected):
        """Update the item list."""
        if len(selected_items) == 0:
            del self.item_list[:]
        elif len(selected_items) == 1:
            if wx.GetKeyState(wx.WXK_CONTROL):
                if len(self.item_list) > 1:
                    self.item_list = [x for x in self.item_list if x != item]
                else:
                    del self.item_list[:]
                    self.item_list.append(item)
            else:
                del self.item_list[:]
                self.item_list.append(item)
        else:
            if item_is_selected:
                self.item_list.append(item)
            else:
                self.item_list = [x for x in self.item_list if x != item]

    def update_playlist(self, song_list):
        """Update the playlist."""
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

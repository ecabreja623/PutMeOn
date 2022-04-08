"""
This file holds the tests for data_playlists.py
"""

from unittest import TestCase, skip

import data_playlists as dbp
import data_users as dbu

FAKE_USER = "Fake user"
FAKE_PLAYLIST = "Fake playlist"

class DBTestCase(TestCase):
    def setUp(self):
        dbp.empty()
        dbu.empty()

    def tearDown(self):
        pass

# PLAYLIST TESTS
    def test_get_playlists(self):
        """
        Can we fetch playlist db?
        """
        playlists = dbp.get_playlists()
        self.assertIsInstance(playlists, list)

    def test_get_playlists_dict(self):
        """
        Can we fetch playlist db as a dict?
        """
        playlists = dbp.get_playlists_dict()
        self.assertIsInstance(playlists, dict)

    def test_get_playlist(self):
        """
        Can we fetch a playlist from the playlist db?
        """
        dbp.add_playlist(FAKE_PLAYLIST)
        playlist = dbp.get_playlist(FAKE_PLAYLIST)
        self.assertIsInstance(playlist, dict)

    def test_add_playlist(self):
        """
        Can we write to the playlist db?
        """
        dbp.add_playlist(FAKE_PLAYLIST)
        playlist = dbp.get_playlist(FAKE_PLAYLIST)
        self.assertEqual(playlist[dbp.PLNAME], FAKE_PLAYLIST)
    
    def test_delete_playlist(self):
        """
        Can we delete a playlist from the playlist db?
        """
        dbp.add_playlist(FAKE_PLAYLIST)
        ret = dbp.del_playlist(FAKE_PLAYLIST)
        self.assertEqual(ret, dbp.OK)
        self.assertNotIn(FAKE_PLAYLIST, dbp.get_playlists())

    def test_playlist_exists(self):
        """
        Post-condition 1: returns true when a playlist exists, false otherwise
        """
        dbp.add_playlist(FAKE_PLAYLIST)
        self.assertTrue(dbp.playlist_exists(FAKE_PLAYLIST))
        self.assertFalse(dbp.playlist_exists("FOO TRACKS TO BAR TO"))


    def test_update_playlist(self):
        """
        Can we update a playlist?
        """
        dbp.add_playlist(FAKE_PLAYLIST)
        dbp.update_playlist(FAKE_PLAYLIST, {"$push": {"songs":"FAKE SONG"}})
        dbp.update_playlist(FAKE_PLAYLIST, {"$push": {"likes":"FAKE USER"}})
        pl = dbp.get_playlist(FAKE_PLAYLIST)
        self.assertIn("FAKE SONG", pl["songs"])
        self.assertIn("FAKE USER", pl["likes"])
        dbp.update_playlist(FAKE_PLAYLIST, {"$pull": {"songs":"FAKE SONG"}})
        pl = dbp.get_playlist(FAKE_PLAYLIST)
        self.assertNotIn("FAKE SONG", pl["songs"])


    def test_add_song(self):
        """
        we can add a song to a new playlist
        """
        newsong = "SONG"
        newplaylist = "PLAYLIST"
        dbp.add_playlist(newplaylist)
        dbp.add_song(newplaylist, newsong)
        pl = dbp.get_playlist(newplaylist)
        self.assertIn(newsong, pl["songs"])


    def test_rem_song(self):
        """
        we can remove a song from a playlist
        """
        newpl = "PLAYLIST"
        dbp.add_playlist(newpl)
        newsong = "SONG"
        dbp.add_song(newpl, newsong)
        pl = dbp.get_playlist(newpl)
        self.assertIn(newsong, pl['songs'])
        dbp.rem_song(newpl, newsong)
        pl = dbp.get_playlist(newpl)
        self.assertNotIn(newsong, pl['songs'])


    def test_empty(self):
        """
        we can empty the playlist collection
        """
        for i in range(10):
            dbp.add_playlist("PLAYLIST")
        dbp.empty()
        self.assertEqual(len(dbp.get_playlists()), 0)

"""
This file holds the tests for data.py
"""

from unittest import TestCase, skip

import data as db
from db.data import USERNAME

FAKE_USER = "Fake user"
FAKE_PLAYLIST = "Fake playlist"

class DBTestCase(TestCase):
    def setUp(self):
        db.empty()

    def tearDown(self):
        pass

    def test_add_user(self):
        """
        Can we write to the user db?
        """
        db.add_user(FAKE_USER)
        user = db.get_user(FAKE_USER)
        self.assertEqual(user[USERNAME],FAKE_USER)

    def test_get_users(self):
        """
        Can we fetch user db?
        """
        users = db.get_users()
        self.assertIsInstance(users, dict)

    def test_get_user(self):
        """
        Can we fetch a user from the user db?
        """
        db.add_user(FAKE_USER)
        user = db.get_user(FAKE_USER)
        self.assertIsInstance(user, dict)

    def test_delete_user(self):
        """
        Can we delete a user from the user db?
        """
        db.add_user(FAKE_USER)
        ret = db.del_user(FAKE_USER)
        self.assertEqual(ret, db.OK)
        self.assertFalse(FAKE_USER in db.get_users())

    def test_add_user(self):
        """
        Can we write to the user db?
        """
        db.add_user(FAKE_USER)
        user = db.get_user(FAKE_USER)
        self.assertEqual(user[USERNAME],FAKE_USER)
    
    def test_user_exists(self):
        """
        Post-condition 1: returns true when a user exists, false otherwise
        """
        db.add_user(FAKE_USER)
        self.assertTrue(db.user_exists(FAKE_USER))
        self.assertFalse(db.user_exists("FOOBAR JONES"))

    def test_update_user(self):
        """
        Can we update a user?
        """
        db.add_user(FAKE_USER)
        db.update_user(FAKE_USER, {"$push": {"friends":"fake friend"}})
        db.update_user(FAKE_USER, {"$inc": {"numFriends":1}})
        u = db.get_user(FAKE_USER)
        self.assertIn("fake friend", u["friends"])
        self.assertEqual(1, u["numFriends"])
        db.update_user(FAKE_USER, {"$pull": {"friends":"fake friend"}})
        u = db.get_user(FAKE_USER)
        self.assertNotIn("fake friend", u["friends"])

# PLAYLIST TESTS
    def test_get_playlists(self):
        """
        Can we fetch playlist db?
        """
        playlists = db.get_playlists()
        self.assertIsInstance(playlists, dict)

    def test_get_playlist(self):
        """
        Can we fetch a playlist from the playlist db?
        """
        db.add_playlist(FAKE_PLAYLIST)
        playlist = db.get_playlist(FAKE_PLAYLIST)
        self.assertIsInstance(playlist, dict)

    def test_add_playlist(self):
        """
        Can we write to the playlist db?
        """
        db.add_playlist(FAKE_PLAYLIST)
        playlist = db.get_playlist(FAKE_PLAYLIST)
        self.assertEqual(playlist[db.PLNAME], FAKE_PLAYLIST)
    
    def test_delete_playlist(self):
        """
        Can we delete a playlist from the playlist db?
        """
        db.add_playlist(FAKE_PLAYLIST)
        ret = db.del_playlist(FAKE_PLAYLIST)
        self.assertEqual(ret, db.OK)
        self.assertNotIn(FAKE_PLAYLIST, db.get_playlists())

    def test_playlist_exists(self):
        """
        Post-condition 1: returns true when a playlist exists, false otherwise
        """
        db.add_playlist(FAKE_PLAYLIST)
        self.assertTrue(db.playlist_exists(FAKE_PLAYLIST))
        self.assertFalse(db.playlist_exists("FOO TRACKS TO BAR TO"))


    def test_update_playlist(self):
        """
        Can we update a playlist?
        """
        db.add_playlist(FAKE_PLAYLIST)
        db.update_playlist(FAKE_PLAYLIST, {"$push": {"songs":"FAKE SONG"}})
        db.update_playlist(FAKE_PLAYLIST, {"$inc": {"likes":1}})
        pl = db.get_playlist(FAKE_PLAYLIST)
        self.assertIn("FAKE SONG", pl["songs"])
        self.assertEqual(1, pl["likes"])
        db.update_playlist(FAKE_PLAYLIST, {"$pull": {"songs":"FAKE SONG"}})
        pl = db.get_playlist(FAKE_PLAYLIST)
        self.assertNotIn("FAKE SONG", pl["songs"])
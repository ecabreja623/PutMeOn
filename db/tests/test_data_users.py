"""
This file holds the tests for data.py
"""

from unittest import TestCase, skip

import data_users as dbu
import data_playlists as dbp

FAKE_USER = "Fake user"
FAKE_PLAYLIST = "Fake playlist"

class DBTestCase(TestCase):
    def setUp(self):
        dbu.empty()

    def tearDown(self):
        pass

    def test_add_user(self):
        """
        Can we write to the user db?
        """
        dbu.add_user(FAKE_USER)
        user = dbu.get_user(FAKE_USER)
        self.assertEqual(user[dbu.USERNAME],FAKE_USER)

    def test_get_users(self):
        """
        Can we fetch user db?
        """
        users = dbu.get_users()
        self.assertIsInstance(users, dict)

    def test_get_user(self):
        """
        Can we fetch a user from the user db?
        """
        dbu.add_user(FAKE_USER)
        user = dbu.get_user(FAKE_USER)
        self.assertIsInstance(user, dict)

    def test_delete_user(self):
        """
        Can we delete a user from the user db?
        """
        dbu.add_user(FAKE_USER)
        ret = dbu.del_user(FAKE_USER)
        self.assertEqual(ret, dbu.OK)
        self.assertFalse(FAKE_USER in dbu.get_users())

    def test_add_user(self):
        """
        Can we write to the user db?
        """
        dbu.add_user(FAKE_USER)
        user = dbu.get_user(FAKE_USER)
        self.assertEqual(user[dbu.USERNAME],FAKE_USER)
    
    def test_user_exists(self):
        """
        Post-condition 1: returns true when a user exists, false otherwise
        """
        dbu.add_user(FAKE_USER)
        self.assertTrue(dbu.user_exists(FAKE_USER))
        self.assertFalse(dbu.user_exists("FOOBAR JONES"))

    def test_update_user(self):
        """
        Can we update a user?
        """
        dbu.add_user(FAKE_USER)
        dbu.update_user(FAKE_USER, {"$push": {"friends":"fake friend"}})
        dbu.update_user(FAKE_USER, {"$inc": {"numFriends":1}})
        u = dbu.get_user(FAKE_USER)
        self.assertIn("fake friend", u["friends"])
        self.assertEqual(1, u["numFriends"])
        dbu.update_user(FAKE_USER, {"$pull": {"friends":"fake friend"}})
        u = dbu.get_user(FAKE_USER)
        self.assertNotIn("fake friend", u["friends"])

    def test_bef_user(self):
        """
        db can befriend two users
        """
        new1 = "new1"
        new2 = "new2"
        dbu.add_user(new1)
        dbu.add_user(new2)
        dbu.bef_user(new1, new2)
        u1 = dbu.get_user(new1)
        u2 = dbu.get_user(new2)
        self.assertIn(new1, u2["friends"])
        self.assertIn(new2, u1["friends"])
        self.assertEqual(u1["numFriends"], 1)
        self.assertEqual(u2["numFriends"], 1)
    
    def test_unf_user(self):
        """
        db can unfriend two users
        """        
        new1 = "new1"
        new2 = "new2"
        dbu.add_user(new1)
        dbu.add_user(new2)
        dbu.bef_user(new1, new2)
        u1 = dbu.get_user(new1)
        u2 = dbu.get_user(new2)
        dbu.unf_user(new1, new2)
        u1 = dbu.get_user(new1)
        u2 = dbu.get_user(new2)
        self.assertNotIn(new1, u2["friends"])
        self.assertNotIn(new2, u1["friends"])
        self.assertEqual(u1["numFriends"], 0)
        self.assertEqual(u2["numFriends"], 0)
    
    def test_like_playlist(self):
        """
        a user can like a playlist
        """
        newpl = "playlist"
        newuser = "user"
        dbp.add_playlist(newpl)
        dbu.add_user(newuser)
        dbu.like_playlist(newuser, newpl)
        u = dbu.get_user(newuser)
        pl = dbp.get_playlist(newpl)
        self.assertIn(newpl, u["playlists"])
        self.assertIn(newuser, pl["likes"])

    def test_unlike_playlist(self):
        """
        a user can unlike a playlist
        """
        newpl = "playlist"
        newuser = "user"
        dbp.add_playlist(newpl)
        dbu.add_user(newuser)
        dbu.like_playlist(newuser, newpl)
        dbu.unlike_playlist(newuser, newpl)
        u = dbu.get_user(newuser)
        pl = dbp.get_playlist(newpl)
        self.assertNotIn(newpl, u["playlists"])
        self.assertNotIn(newuser, pl["likes"])

    def test_empty(self):
        """
        we can empty the user collection
        """
        for i in range(10):
            dbu.add_user("USER")
        dbu.empty()
        self.assertEqual(len(dbu.get_users()), 0)

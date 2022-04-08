"""
This file holds the tests for data_users.py
"""

from unittest import TestCase, skip

import data_users as dbu
import data_playlists as dbp

FAKE_USER = "Fake user"
FAKE_PASSWORD = "FakePassword"
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
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        user = dbu.get_user(FAKE_USER)
        self.assertEqual(user[dbu.USERNAME],FAKE_USER)

    def test_get_users(self):
        """
        Can we fetch user db?
        """
        users = dbu.get_users()
        self.assertIsInstance(users, list)

    def test_get_users_dict(self):
        """
        Can we fetch user db as a dict?
        """
        users = dbu.get_users_dict()
        self.assertIsInstance(users, dict)

    def test_get_user(self):
        """
        Can we fetch a user from the user db?
        """
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        user = dbu.get_user(FAKE_USER)
        self.assertIsInstance(user, dict)

    def test_delete_user(self):
        """
        Can we delete a user from the user db?
        """
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        ret = dbu.del_user(FAKE_USER)
        self.assertEqual(ret, dbu.OK)
        self.assertFalse(FAKE_USER in dbu.get_users())

    def test_add_user(self):
        """
        Can we write to the user db?
        """
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        user = dbu.get_user(FAKE_USER)
        self.assertEqual(user[dbu.USERNAME],FAKE_USER)
    
    def test_user_exists(self):
        """
        Post-condition 1: returns true when a user exists, false otherwise
        """
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        self.assertTrue(dbu.user_exists(FAKE_USER))
        self.assertFalse(dbu.user_exists("FOOBAR JONES"))

    def test_update_user(self):
        """
        Can we update a user?
        """
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        dbu.update_user(FAKE_USER, {"$push": {"friends":"fake friend"}})
        u = dbu.get_user(FAKE_USER)
        self.assertIn("fake friend", u["friends"])
        dbu.update_user(FAKE_USER, {"$pull": {"friends":"fake friend"}})
        u = dbu.get_user(FAKE_USER)
        self.assertNotIn("fake friend", u["friends"])

    def test_bef_user(self):
        """
        db can befriend two users
        """
        new1 = "new1"
        new2 = "new2"
        dbu.add_user(new1, FAKE_PASSWORD)
        dbu.add_user(new2, FAKE_PASSWORD)
        dbu.bef_user(new1, new2)
        u1 = dbu.get_user(new1)
        u2 = dbu.get_user(new2)
        self.assertIn(new1, u2["friends"])
        self.assertIn(new2, u1["friends"])
    
    def test_unf_user(self):
        """
        db can unfriend two users
        """        
        new1 = "new1"
        new2 = "new2"
        dbu.add_user(new1, FAKE_PASSWORD)
        dbu.add_user(new2, FAKE_PASSWORD)
        dbu.bef_user(new1, new2)
        dbu.unf_user(new1, new2)
        u1 = dbu.get_user(new1)
        u2 = dbu.get_user(new2)
        self.assertNotIn(new1, u2["friends"])
        self.assertNotIn(new2, u1["friends"])
    
    def decf_user(self):
        """
        db can remove users from their friend requests
        """
        new1 = "new1"
        new2 = "new2"
        dbu.add_user(new1, FAKE_PASSWORD)
        dbu.add_user(new2, FAKE_PASSWORD)
        dbu.req_user(new1, new2)
        dbu.dec_req(new2, new1)
        user1, user2 = dbu.get_user(new1), dbu.get_user(new2)
        self.assertNotIn(user1["outgoingRequests"], new2)
        self.assertNotIn(user2["incomingRequests"], new1)


    def test_like_playlist(self):
        """
        a user can like a playlist
        """
        newpl = "playlist"
        newuser = "user"
        dbp.add_playlist(newpl)
        dbu.add_user(newuser, FAKE_PASSWORD)
        dbu.like_playlist(newuser, newpl)
        u = dbu.get_user(newuser)
        pl = dbp.get_playlist(newpl)
        self.assertIn(newpl, u["likedPlaylists"])
        self.assertIn(newuser, pl["likes"])

    def test_unlike_playlist(self):
        """
        a user can unlike a playlist
        """
        newpl = "playlist"
        newuser = "user"
        dbp.add_playlist(newpl)
        dbu.add_user(newuser, FAKE_PASSWORD)
        dbu.like_playlist(newuser, newpl)
        dbu.unlike_playlist(newuser, newpl)
        u = dbu.get_user(newuser)
        pl = dbp.get_playlist(newpl)
        self.assertNotIn(newpl, u["likedPlaylists"])
        self.assertNotIn(newuser, pl["likes"])

    def test_empty(self):
        """
        we can empty the user collection
        """
        for i in range(10):
            dbu.add_user("USER", FAKE_PASSWORD)
        dbu.empty()
        self.assertEqual(len(dbu.get_users()), 0)

    def test_login1(self):
        """
        a user can login
        """
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        check = dbu.login(FAKE_USER, FAKE_PASSWORD)
        self.assertIsInstance(check, str)

    def test_login2(self):
        """
        a user cannot login with incorrect credentials
        """
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        self.assertEqual(dbu.login(FAKE_USER, "1"), dbu.NOT_ACCEPTABLE)

    def test_auth1(self):
        """
        a user can successfully be authorized for a task
        """
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        token = dbu.login(FAKE_USER, FAKE_PASSWORD)
        ret = dbu.check_auth(FAKE_USER, token)
        self.assertTrue(ret)

    def test_auth2(self):
        """
        a user can be unauthorized for a task
        """
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        val = dbu.token.new()
        ret = dbu.check_auth(FAKE_USER, val)
        self.assertFalse(ret)

    def test_getfriends(self):
        """
        a user can get all its friends
        """
        ret = []
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        for i in range(10):
            dbu.add_user(FAKE_USER+str(i), FAKE_PASSWORD)
            dbu.bef_user(FAKE_USER, FAKE_USER+str(i))
            ret.append(dbu.get_user(FAKE_USER+str(i)))
        self.assertEqual(dbu.get_friends(FAKE_USER), ret)

"""
THIS HAS TO BE REWORKED WHEN WE MAKE A USER CREATE PLAYLISTS
    def test_getplaylists_created(self):
        "
        a user can get all the playlists it created
        "
        ret = []
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        for i in range(10):
            dbp.add_playlist(FAKE_PLAYLIST+str(i))
            ret.append(dbp.get_playlist(FAKE_PLAYLIST+str(i)))
        self.assertEqual(dbu.get_created_playlists(FAKE_USER), ret)

    def test_getplaylists_liked(self):
        "
        a user can get all the playlists it created
        "
        ret = []
        dbu.add_user(FAKE_USER, FAKE_PASSWORD)
        for i in range(10):
            dbp.add_playlist(FAKE_PLAYLIST+str(i))
            ret.append(dbp.get_playlist(FAKE_PLAYLIST+str(i)))
        self.assertEqual(dbu.get_created_playlists(FAKE_USER), ret)
"""
    
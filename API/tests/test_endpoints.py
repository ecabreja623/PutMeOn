"""
This file holds the tests for endpoints.py
"""

from unittest import TestCase, skip
from flask_restx import Resource, Api
import random
import werkzeug.exceptions as wz

import API.endpoints as ep
import db.data as db

HUGE_NUM = 1000000000

def new_entity_name(entity_type):
    int_name = random.randint(0,HUGE_NUM)
    return f"new {entity_type}" + str(int_name)


class EndpointTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hello(self):
        hello = ep.HelloWorld(Resource)
        ret = hello.get()
        self.assertIsInstance(ret, dict)
        self.assertIn(ep.HELLO, ret)

    def test_create_user1(self):
        """
        Post-condition 1: create user and check if in db
        """
        cu = ep.CreateUser(Resource)
        new_user = new_entity_name("user")
        ret = cu.post(new_user)
        users = db.get_users()
        self.assertIn(new_user, users)
    
    def test_create_user2(self):
        """
        Post-condition 2: create duplicates and make sure only one appears
        """
        cu = ep.CreateUser(Resource)
        new_user = new_entity_name("user")
        cu.post(new_user)
        try:
            cu.post(new_user)
            self.assertFalse(True)
        except wz.NotAcceptable:
            self.assertFalse(False)

    def test_list_users1(self):
        """
        Post-condition 1: return is a dictionary.
        """
        lu = ep.ListUsers(Resource)
        ret = lu.get()
        self.assertIsInstance(ret, dict)

    def test_list_users2(self):
        """
        Post-condition 2: keys to the dict are strings
        """
        lu = ep.ListUsers(Resource)
        ret = lu.get()
        for key in ret:
            self.assertIsInstance(key, str)

    def test_list_users3(self):
        """
        Post-condition 3: the values in the dict are themselves dicts
        """
        lu = ep.ListUsers(Resource)
        ret = lu.get()
        for val in ret.values():
            self.assertIsInstance(val, dict)

    def test_delete_user1(self):
        """
        Post-condition 1: we can create and delete a user
        """
        new_user = new_entity_name("user")
        db.add_user(new_user)
        du = ep.DeleteUser(Resource)
        du.post(new_user)
        self.assertNotIn(new_user, db.get_users())

    def test_delete_user2(self):
        """
        Post-condition 2: deleting a user that does not exist results in a wz.NotAcceptable error
        """
        new_user = new_entity_name("user")
        du = ep.DeleteUser(Resource)
        try:
            du.post(new_user)
            self.assertFalse(True)
        except wz.NotFound:
            self.assertFalse(False)

    def test_add_friends1(self):
        """
        Post-condition 1: we can make two users friends
        """
        new1 = new_entity_name("user")
        db.add_user(new1)
        new2 = new_entity_name("user")
        db.add_user(new2)
        af = ep.BefriendUser(Resource)
        af.post(new1, new2)
        u1 = db.get_user(new1)
        u2 = db.get_user(new2)
        self.assertIn(new1, u2["friends"])
        self.assertIn(new2, u1["friends"])
        self.assertEqual(u1["numFriends"], 1)
        self.assertEqual(u2["numFriends"], 1)

    def test_add_friends2(self):
        """
        Post-condition 2: attempting to add a friend that is a non-existent user fails
        """
        new1 = new_entity_name("user")
        db.add_user(new1)
        new2 = new_entity_name("user")
        af = ep.BefriendUser(Resource)
        try:
            af.post(new1, new2)
            self.assertFalse(True)
        except wz.NotFound:
            self.assertFalse(False)

    def test_add_friends3(self):
        """
        Post-condition 3: we cannot make two users friends if they are already friends
        """
        new1 = new_entity_name("user")
        db.add_user(new1)
        new2 = new_entity_name("user")
        db.add_user(new2)
        af = ep.BefriendUser(Resource)
        af.post(new1, new2)
        try:
            af.post(new1, new2)
            self.assertFalse(True)
        except wz.NotAcceptable:
            self.assertFalse(False)

    def test_remove_friends1(self):
        """
        Post-condition 1: two friends can remove one another
        """
        new1 = new_entity_name("user")
        db.add_user(new1)
        new2 = new_entity_name("user")
        db.add_user(new2)
        af = ep.BefriendUser(Resource)
        af.post(new1, new2)
        uf = ep.UnfriendUser(Resource)
        uf.post(new1, new2)
        u1 = db.get_user(new1)
        u2 = db.get_user(new2)
        self.assertNotIn(new1, u2["friends"])
        self.assertNotIn(new2, u1["friends"])
        self.assertEqual(u1["numFriends"], 0)
        self.assertEqual(u2["numFriends"], 0)
    
    def test_remove_friends2(self):
        """
        Post-condition 2: two non friends cannot remove one another
        """
        new1 = new_entity_name("user")
        db.add_user(new1)
        new2 = new_entity_name("user")
        db.add_user(new2)
        uf = ep.UnfriendUser(Resource)
        try:
            uf.post(new1, new2)
            self.assertFalse(True)
        except:
            self.assertFalse(False)
    
    def test_remove_friends3(self):
        """
        Post-condition 3: passing a nonexistent user will fail
        """
        new1 = new_entity_name("user")
        db.add_user(new1)
        new2 = new_entity_name("user")
        af = ep.BefriendUser(Resource)
        uf = ep.UnfriendUser(Resource)
        try:
            af.post(new1, new2)
            uf.post(new1, new2)
            self.assertFalse(True)
        except wz.NotFound:
            self.assertFalse(False)

    def test_add_song1(self):
        """
        Post-condition1: we can add a new song to a new playlist
        """
        ap = ep.AddToPlaylist(Resource)
        newsong = new_entity_name("song")
        newplaylist = new_entity_name("playlist")
        db.add_playlist(newplaylist)
        ap.post(newplaylist, newsong)
        pl = db.get_playlist(newplaylist)
        self.assertIn(newsong, pl["songs"])

    def test_add_song2(self):
        """
        Post-condition 2: we cannot add the same song to a playlist twice
        """
        ap = ep.AddToPlaylist(Resource)
        newsong = new_entity_name("song")
        newplaylist = new_entity_name("playlist")
        db.add_playlist(newplaylist)
        ap.post(newplaylist, newsong)
        try:
            ap.post(newplaylist, newsong)
            self.assertFalse(True)
        except wz.NotAcceptable:
            self.assertFalse(False)

    def test_remove_song1(self):
        """
        Post-condition 1: we can remove a song from a playlist given that it is present
        """
        newpl = new_entity_name("playlist")
        db.add_playlist(newpl)
        newsong = new_entity_name("song")
        db.update_playlist(newpl, {"$push": {"songs": newsong}})
        pl = db.get_playlist(newpl)
        self.assertIn(newsong, pl['songs'])
        rs = ep.RemoveFromPlaylist(Resource)
        rs.post(newpl, newsong)
        pl = db.get_playlist(newpl)
        self.assertNotIn(newsong, pl['songs'])

    def test_remove_song2(self):
        """
        Post-condition 2: Removing a song when it is not present results in an error
        """
        newpl = new_entity_name("playlist")
        db.add_playlist(newpl)
        newsong = new_entity_name("song")
        rs = ep.RemoveFromPlaylist(Resource)
        try:
            rs.post(newpl, newsong)
            self.assertFalse(True)
        except wz.NotFound:
            self.assertFalse(False)


    def test_remove_song3(self):
        """
        Post-condition 3: Removing a song from a playlist that doesn't exist results in an error
        """
        newpl = new_entity_name("playlist")
        newsong = new_entity_name("song")
        rs = ep.RemoveFromPlaylist(Resource)
        try:
            rs.post(newpl, newsong)
            self.assertFalse(True)
        except wz.NotFound:
            self.assertFalse(False)

    def test_like_playlist1(self):
        """
        Post-condition1: we can like a playlist from a new user, and have the change reflected in both objects
        """
        lp = ep.LikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        db.add_playlist(newpl)
        db.add_user(newuser)
        lp.post(newuser, newpl)
        u = db.get_user(newuser)
        pl = db.get_playlist(newpl)
        self.assertIn(newpl, u["playlists"])
        self.assertEqual(pl["likes"], 1)

    def test_like_playlist2(self):
        """
        Post-condition2: liking a playlist twice should result in the change only being reflected once
        """
        lp = ep.LikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        db.add_playlist(newpl)
        db.add_user(newuser)
        lp.post(newuser, newpl)
        try:
            lp.post(newuser, newpl)
            self.assertFalse(True)
        except wz.NotAcceptable:
            self.assertFalse(False)
        

    def test_like_playlist3(self):
        """
        Post-condition 3: liking a playlist from a nonexistent user will fail
        """
        lp = ep.LikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        db.add_playlist(newpl)
        try:
            lp.post(newuser, newpl)
            self.assertFalse(True)
        except wz.NotFound:
            self.assertFalse(False)

    def test_like_playlist4(self):
        """
        Post-condition 4: liking a nonexistent playlist will fail
        """
        lp = ep.LikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        db.add_user(newuser)
        try:
            lp.post(newuser, newpl)
            self.assertFalse(True)
        except wz.NotFound:
            self.assertFalse(False)

    def test_unlike_playlist1(self):
        """
        Post-condition 1: a user who has liked a playlist can unlike said playlist
        """
        lp = ep.LikePlaylist(Resource)
        up = ep.UnlikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        db.add_playlist(newpl)
        db.add_user(newuser)
        lp.post(newuser, newpl)
        up.post(newuser, newpl)
        u = db.get_user(newuser)
        pl = db.get_playlist(newpl)
        self.assertNotIn(newpl, u["playlists"])
        self.assertEqual(pl["likes"], 0)
    
    def test_unlike_playlist2(self):
        """
        Post-condition 2: a user who hasn't liked a playlist cannot unlike said playlist
        """
        up = ep.UnlikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        db.add_playlist(newpl)
        db.add_user(newuser)
        try:
            up.post(newuser, newpl)
            self.assertFalse(True)
        except wz.NotFound:
            self.assertFalse(False)

    def test_unlike_playlist3(self):
        """
        Post-condition 3: a nonexistent user cannot unlike a playlist
        """
        up = ep.UnlikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        db.add_playlist(newpl)
        lp = ep.LikePlaylist(Resource)
        try:
            lp.post(newuser, newpl)
            up.post(newuser, newpl)
            self.assertFalse(True)
        except wz.NotFound:
            self.assertFalse(False)

    def test_unlike_playlist4(self):
        """
        Post-condition 4: a user cannot unlike a nonexistent playlist
        """
        lp = ep.LikePlaylist(Resource)
        up = ep.UnlikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        db.add_user(newuser)
        try:
            lp.post(newuser, newpl)
            up.post(newuser, newpl)
            self.assertFalse(True)
        except wz.NotFound:
            self.assertFalse(False)
"""
This file holds the user tests for endpoints.py
"""

from unittest import TestCase, skip
from flask_restx import Resource, Api
import random
import werkzeug.exceptions as wz

import API.endpoints as ep
import db.data_playlists as dbp
import db.data_users as dbu

HUGE_NUM = 1000000000
FAKE_PASSWORD = "FakePassword"

def new_entity_name(entity_type):
    int_name = random.randint(0,HUGE_NUM)
    return f"new {entity_type}" + str(int_name)

def new_entity(entity="U"):
    new = new_entity_name(entity)
    dbu.add_user(new, FAKE_PASSWORD)
    return new

class EndpointTestCase(TestCase):
    def setUp(self):
        dbu.empty()
        dbp.empty()

    def tearDown(self):
        pass

    def test_hello(self):
        hello = ep.HelloWorld(Resource)
        ret = hello.get()
        self.assertIsInstance(ret, dict)
        self.assertIn(ep.HELLO, ret)

    def test_endpoints(self):
        endp = ep.Endpoints(Resource)
        ret = endp.get()
        self.assertIn("Available endpoints", ret)
        self.assertIsInstance(ret["Available endpoints"], list)

    #USER TESTS

    def test_list_users1(self):
        """
        Post-condition 1: return is a list.
        """
        lu = ep.ListUsers(Resource)
        ret = lu.get()
        self.assertIsInstance(ret, list)

    def test_list_users2(self):
        """
        Post-condition 2: users have usernames
        """
        lu = ep.ListUsers(Resource)
        ret = lu.get()
        for obj in ret:
            self.assertIsInstance(obj["userName"], str)

    def test_list_users3(self):
        """
        Post-condition 3: the values in the list are themselves dicts
        """
        lu = ep.ListUsers(Resource)
        ret = lu.get()
        for val in ret:
            self.assertIsInstance(val, dict)

    def test_list_users4(self):
        """
        Post-condition 4: the passwords are strings
        """
        lu = ep.ListUsers(Resource)
        ret = lu.get()
        for obj in ret:
            self.assertIsInstance(obj["password"], str)

    def test_create_user1(self):
        """
        Post-condition 1: create user and check if in db
        """
        cu = ep.CreateUser(Resource)
        new_user = new_entity_name("user")
        ret = cu.post(new_user, FAKE_PASSWORD)
        users = dbu.get_users_dict()
        self.assertIn(new_user, users)
    
    def test_create_user2(self):
        """
        Post-condition 2: create duplicates and make sure only one appears
        """
        cu = ep.CreateUser(Resource)
        new_user = new_entity_name("user")
        cu.post(new_user, FAKE_PASSWORD)
        self.assertRaises(wz.NotAcceptable, cu.post, new_user, FAKE_PASSWORD)

    def test_search_user1(self):
        """
        Post-condition 1: successfully search for a user that exists
        """
        newuser = new_entity_name("user")
        dbu.add_user(newuser, FAKE_PASSWORD)
        su = ep.SearchUser(Resource)
        ret = su.get(newuser)
        self.assertEqual(newuser, ret[dbu.USERNAME])

    def test_search_user2(self):
        """
        Post-condition 2: searching for a user that does not exist returns an error
        """    
        newuser = new_entity_name("user")
        su = ep.SearchUser(Resource)
        self.assertRaises(wz.NotFound, su.get, newuser)

    def test_delete_user1(self):
        """
        Post-condition 1: we can create and delete a user
        """
        new_user = new_entity_name("user")
        dbu.add_user(new_user, FAKE_PASSWORD)
        du = ep.DeleteUser(Resource)
        du.delete(new_user)
        self.assertNotIn(new_user, dbu.get_users())

    def test_delete_user2(self):
        """
        Post-condition 2: deleting a user that does not exist results in a wz.NotAcceptable error
        """
        new_user = new_entity_name("user")
        du = ep.DeleteUser(Resource)
        self.assertRaises(wz.NotFound, du.delete, new_user)

    def test_delete_user3(self):
        """
        Post-condition 3: deleting a user results in friends being removed from its database and it being removed from a playlist's likes
        """
        newuser = new_entity_name("user")
        dbu.add_user(newuser, FAKE_PASSWORD)
        newfriend = new_entity_name("user")
        dbu.add_user(newfriend, FAKE_PASSWORD)
        af = ep.BefriendUser(Resource)
        af.post(newuser, newfriend)
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl)
        lp = ep.LikePlaylist(Resource)
        lp.post(newuser, newpl)
        du = ep.DeleteUser(Resource)
        du.delete(newuser)
        friend = dbu.get_user(newfriend)
        pl = dbp.get_playlist(newpl)
        self.assertNotIn(newuser, friend['friends'])
        self.assertNotIn(newuser, pl['likes'])

    def test_add_friends1(self):
        """
        Post-condition 1: we can make two users friends
        """
        new1 = new_entity_name("user")
        dbu.add_user(new1, FAKE_PASSWORD)
        new2 = new_entity_name("user")
        dbu.add_user(new2, FAKE_PASSWORD)
        dbu.req_user(new2, new1)
        af = ep.BefriendUser(Resource)
        af.post(new1, new2)
        u1 = dbu.get_user(new1)
        u2 = dbu.get_user(new2)
        self.assertIn(new1, u2["friends"])
        self.assertIn(new2, u1["friends"])

    def test_add_friends2(self):
        """
        Post-condition 2: attempting to add a friend that is a non-existent user fails
        """
        new1 = new_entity_name("user")
        dbu.add_user(new1, FAKE_PASSWORD)
        new2 = new_entity_name("user")
        af = ep.BefriendUser(Resource)
        self.assertRaises(wz.NotFound, af.post, new1, new2)

    def test_add_friends3(self):
        """
        Post-condition 3: we cannot make two users friends if they are already friends
        """
        new1 = new_entity_name("user")
        dbu.add_user(new1, FAKE_PASSWORD)
        new2 = new_entity_name("user")
        dbu.add_user(new2, FAKE_PASSWORD)
        dbu.req_user(new2, new1)
        af = ep.BefriendUser(Resource)
        dbu.req_user(new2, new1)
        af.post(new1, new2)
        self.assertRaises(wz.NotAcceptable, af.post, new1, new2)

    def test_add_friends4(self):
        """
        Post-condition 4: A user cannot add themself as a friend
        """
        newuser = new_entity_name("user")
        dbu.add_user(newuser, FAKE_PASSWORD)
        af = ep.BefriendUser(Resource)
        self.assertRaises(wz.NotAcceptable, af.post, newuser, newuser)

    def test_req_friends1(self):
        """
        Post-condition 1: A user can friend request another user
        """
        new1 = new_entity()
        new2 = new_entity()
        rf = ep.RequestUser(Resource)
        rf.post(new1, new2)
        user1 = dbu.get_user(new1)
        user2 = dbu.get_user(new2)
        self.assertIn(new2, user1["outgoingRequests"])
        self.assertIn(new1, user2["incomingRequests"])

    def test_req_friends2(self):
        """
        Post-condition 2: requesting a user fails if you have already done it
        """
        new1 = new_entity()
        new2 = new_entity()
        rf = ep.RequestUser(Resource)
        rf.post(new1, new2)
        user1, user2 = dbu.get_user(new1), dbu.get_user(new2)
        self.assertRaises(wz.NotAcceptable, rf.post, new1, new2)

    def test_req_friends3(self):
        """
        Post-condition 3: A user requesting itself fails
        """
        new1 = new_entity()
        rf = ep.RequestUser(Resource)
        self.assertRaises(wz.NotAcceptable, rf.post, new1, new1)

    def test_req_friends4(self):
        """
        Post-condition 4: requesting a user fails if they have requested you first
        """
        new1 = new_entity()
        new2 = new_entity()
        rf = ep.RequestUser(Resource)
        rf.post(new1, new2)
        self.assertRaises(wz.NotAcceptable, rf.post, new2, new1)

    def test_req_friends5(self):
        """
        Post-condition 5: requesting a user fails if users are already friends
        """
        new1 = new_entity()
        new2 = new_entity()
        dbu.bef_user(new1, new2)
        rf = ep.RequestUser(Resource)
        self.assertRaises(wz.NotAcceptable, rf.post, new1, new2)

    def test_req_friends6(self):
        """
        Post-condition 6: requesting a user fails if either user does not exist
        """
        name1 = new_entity_name('user')
        name2 = new_entity_name('user')
        rf = ep.RequestUser(Resource)
        self.assertRaises(wz.NotFound, rf.post, name1, name2)
        new1 = new_entity()
        self.assertRaises(wz.NotFound, rf.post, new1, name2)
        self.assertRaises(wz.NotFound, rf.post, name1, new1)

    def test_remove_friends1(self):
        """
        Post-condition 1: two friends can remove one another
        """
        new1 = new_entity_name("user")
        dbu.add_user(new1, FAKE_PASSWORD)
        new2 = new_entity_name("user")
        dbu.add_user(new2, FAKE_PASSWORD)
        af = ep.BefriendUser(Resource)
        dbu.req_user(new2, new1)
        af.post(new1, new2)
        uf = ep.UnfriendUser(Resource)
        uf.post(new1, new2)
        u1 = dbu.get_user(new1)
        u2 = dbu.get_user(new2)
        self.assertNotIn(new1, u2["friends"])
        self.assertNotIn(new2, u1["friends"])

    def test_remove_friends2(self):
        """
        Post-condition 2: two non friends cannot remove one another
        """
        new1 = new_entity_name("user")
        dbu.add_user(new1, FAKE_PASSWORD)
        new2 = new_entity_name("user")
        dbu.add_user(new2, FAKE_PASSWORD)
        uf = ep.UnfriendUser(Resource)
        self.assertRaises(wz.NotAcceptable, uf.post, new1, new2)
    
    def test_remove_friends3(self):
        """
        Post-condition 3: passing a nonexistent user will fail
        """
        new1 = new_entity_name("user")
        dbu.add_user(new1, FAKE_PASSWORD)
        new2 = new_entity_name("user")
        uf = ep.UnfriendUser(Resource)
        self.assertRaises(wz.NotFound, uf.post, new1, new2)


    def test_decline_friend_request1(self):
        """
        Post-condition 1: A user can decline a request that has been sent
        """
        new1 = new_entity()
        new2 = new_entity()
        dbu.req_user(new1, new2)
        df = ep.DecRequest(Resource)
        df.post(new2, new1)
        user1, user2 = dbu.get_user(new1), dbu.get_user(new2)
        self.assertNotIn(new2, user1["outgoingRequests"])
        self.assertNotIn(new1, user2["incomingRequests"])


    def test_decline_friend_request2(self):
        """
        Post-condition 2: A user cannot decline a request if neither exist
        """
        new1 = new_entity_name("user")
        new2 = new_entity_name("user")
        df = ep.DecRequest(Resource)
        self.assertRaises(wz.NotFound, df.post, new1, new2)

        
    def test_like_playlist1(self):
        """
        Post-condition1: we can like a playlist from a new user, and have the change reflected in both objects
        """
        lp = ep.LikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl)
        dbu.add_user(newuser, FAKE_PASSWORD)
        lp.post(newuser, newpl)
        u = dbu.get_user(newuser)
        pl = dbp.get_playlist(newpl)
        self.assertIn(newpl, u["likedPlaylists"])
        self.assertIn(newuser, pl["likes"])

    def test_like_playlist2(self):
        """
        Post-condition2: liking a playlist twice should result in the change only being reflected once
        """
        lp = ep.LikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl)
        dbu.add_user(newuser, FAKE_PASSWORD)
        lp.post(newuser, newpl)
        self.assertRaises(wz.NotAcceptable, lp.post, newuser, newpl)

    def test_like_playlist3(self):
        """
        Post-condition 3: liking a playlist from a nonexistent user will fail
        """
        lp = ep.LikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl)
        self.assertRaises(wz.NotFound, lp.post, newuser, newpl)

    def test_like_playlist4(self):
        """
        Post-condition 4: liking a nonexistent playlist will fail
        """
        lp = ep.LikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        dbu.add_user(newuser, FAKE_PASSWORD)
        self.assertRaises(wz.NotFound, lp.post, newuser, newpl)

    def test_unlike_playlist1(self):
        """
        Post-condition 1: a user who has liked a playlist can unlike said playlist
        """
        lp = ep.LikePlaylist(Resource)
        up = ep.UnlikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl)
        dbu.add_user(newuser, FAKE_PASSWORD)
        lp.post(newuser, newpl)
        up.post(newuser, newpl)
        u = dbu.get_user(newuser)
        pl = dbp.get_playlist(newpl)
        self.assertNotIn(newpl, u["likedPlaylists"])
        self.assertNotIn(newuser, pl["likes"])
    
    def test_unlike_playlist2(self):
        """
        Post-condition 2: a user who hasn't liked a playlist cannot unlike said playlist
        """
        up = ep.UnlikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl)
        dbu.add_user(newuser, FAKE_PASSWORD)
        self.assertRaises(wz.NotFound, up.post, newuser, newpl)

    def test_unlike_playlist3(self):
        """
        Post-condition 3: a nonexistent user cannot unlike a playlist
        """
        up = ep.UnlikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl)
        self.assertRaises(wz.NotFound, up.post, newuser, newpl)

    def test_unlike_playlist4(self):
        """
        Post-condition 4: a user cannot unlike a nonexistent playlist
        """
        lp = ep.LikePlaylist(Resource)
        up = ep.UnlikePlaylist(Resource)
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        dbu.add_user(newuser, FAKE_PASSWORD)
        self.assertRaises(wz.NotFound, up.post, newuser, newpl)

    def test_login1(self):
        """
        Post-condition 1: a user can log into their account
        """
        user = new_entity()
        li = ep.LoginUser(Resource)
        assrt = li.get(user, FAKE_PASSWORD)
        self.assertEqual(assrt, user)

    def test_login2(self):
        """
        Post-condition 2: a user cannot log in with an incorrect password
        """
        user = new_entity()
        li = ep.LoginUser(Resource)
        self.assertRaises(wz.NotAcceptable, li.get(user, user))
    
    def test_login3(self):
        """
        Post-condition 3: a user cannot log in with a username that doesn't exist
        """
        user = new_entity_name('user')
        li = ep.LoginUser(Resource)
        self.assertRaises(wz.NotFound, li.get(user, FAKE_PASSWORD))

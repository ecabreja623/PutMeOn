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

FAKE_PLAYLIST = 'Fake Playlist'
FAKE_USER = "FakeUser"

TEST_CLIENT = ep.app.test_client()
HUGE_NUM = 1000000000
FAKE_PASSWORD = "FakePassword"

def login():
    user = new_entity()
    token = dbu.login(user, FAKE_PASSWORD)
    return {dbu.USERNAME: user, dbu.TOKEN: token}

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

    def testHello(self):
        fields = login()
        response = TEST_CLIENT.post("/hello", json=fields)
        self.assertEqual(response.json, {"Hola": "mundo"})

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
        self.assertEqual(newuser, ret[0][dbu.USERNAME])

    def test_search_user2(self):
        """
        Post-condition 2: searching for a user that does not exist returns an empty list
        """    
        su = ep.SearchUser(Resource)
        self.assertEqual(su.get(FAKE_USER), [])

    def test_delete_user1(self):
        """
        Post-condition 1: we can create and delete a user
        """
        body = login()
        TEST_CLIENT.delete(f'/users/delete/{body[dbu.USERNAME]}', json=body)
        self.assertNotIn(body[dbu.USERNAME], dbu.get_users_dict())

    def test_delete_user2(self):
        """
        Post-condition 2: deleting another user fails
        """
        body = login()
        other = login()
        TEST_CLIENT.delete(f'/users/delete/{other[dbu.USERNAME]}', json=body)
        self.assertIn(other[dbu.USERNAME], dbu.get_users_dict())

    def test_delete_user3(self):
        """
        Post-condition 3: deleting a user results in friends being removed from its database and its created playlists being deleted
        """
        body1 = login()
        body2 = login()
        TEST_CLIENT.post(f'/users/{body1[dbu.USERNAME]}/req_friend/{body2[dbu.USERNAME]}')
        TEST_CLIENT.post(f'/users/{body2[dbu.USERNAME]}/add_friend/{body1[dbu.USERNAME]}')
        TEST_CLIENT.post(f'/playlist/create/{body1[dbu.USERNAME]}/{FAKE_PLAYLIST}', json=body1)
        TEST_CLIENT.delete(f'/users/delete/{body1[dbu.USERNAME]}', json=body1)
        self.assertNotIn(body1[dbu.USERNAME], dbu.get_users_dict())
        self.assertNotIn(FAKE_PLAYLIST, dbp.get_playlists_dict())
        self.assertNotIn(body1[dbu.USERNAME], dbu.get_user(body2[dbu.USERNAME])['friends'])


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
        self.assertIsInstance(assrt[dbu.TOKEN], str)

    def test_login2(self):
        """
        Post-condition 2: a user cannot log in with an incorrect password
        """
        user = new_entity()
        li = ep.LoginUser(Resource)
        self.assertRaises(wz.NotAcceptable, li.get, user, user)
    
    def test_login3(self):
        """
        Post-condition 3: a user cannot log in with a username that doesn't exist
        """
        user = new_entity_name('user')
        li = ep.LoginUser(Resource)
        self.assertRaises(wz.NotFound, li.get, user, FAKE_PASSWORD)

    def test_get_friends1(self):
        """
        Post-condition 1: a user that does not exist will return a wz.NotFound error
        """
        user = new_entity_name("user")
        gf = ep.GetFriends(Resource)
        self.assertRaises(wz.NotFound, gf.get, user)

    def test_get_friends2(self):
        """
        Post-condition 2: a user with friends will have these friends in the response
        """
        user1 = new_entity()
        user2 = new_entity()
        ru = ep.RequestUser(Resource)
        ru.post(user1, user2)
        af = ep.BefriendUser(Resource)
        af.post(user2, user1)
        gf = ep.GetFriends(Resource)
        self.assertEqual([dbu.get_user(user1)], gf.get(user2))

    def test_get_likes1(self):
        """
        Post-condition 1: a user that does not exist will return a wz.NotFound error
        """
        user = new_entity_name('user')
        gl = ep.GetLikedPlaylists(Resource)
        self.assertRaises(wz.NotFound, gl.get, user)
    
    def test_get_friends2(self):
        """
        Post-condition 2: a user with liked playlists can get them
        """
        user = new_entity()
        dbp.add_playlist(FAKE_PLAYLIST)
        dbu.like_playlist(user, FAKE_PLAYLIST)
        gl = ep.GetLikedPlaylists(Resource)
        self.assertEqual([dbp.get_playlist(FAKE_PLAYLIST)], gl.get(user))

    def test_get_made1(self):
        """
        Post-condition 1: a user that does not exist will return a wz.NotFound error
        """
        user = new_entity_name('user')
        gp = ep.GetOwnedPlaylists(Resource)
        self.assertRaises(wz.NotFound, gp.get, user)
    
    def test_get_friends2(self):
        """
        Post-condition 2: a user with playlists can get them
        """
        body = login()
        TEST_CLIENT.post(f'/playlists/create/{body[dbu.USERNAME]}/{FAKE_PLAYLIST}', json=body)
        gp = ep.GetOwnedPlaylists(Resource)
        self.assertEqual([dbp.get_playlist(FAKE_PLAYLIST)], gp.get(body[dbu.USERNAME]))

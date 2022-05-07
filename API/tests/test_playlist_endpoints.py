"""
This file holds the user tests for endpoints.py
"""

from unittest import TestCase
from flask_restx import Resource
import random
import werkzeug.exceptions as wz
from tests.test_user_endpoints import FAKE_PLAYLIST

import API.endpoints as ep
import db.data_playlists as dbp
import db.data_users as dbu

HUGE_NUM = 1000000000
FAKE_PASSWORD = "FakePassword"
FAKE_USER = "fake user"

def login():
    user = new_user()
    token = dbu.login(user, FAKE_PASSWORD)
    return {dbu.USERNAME: user, dbu.TOKEN: token}

def new_entity_name(entity_type):
    int_name = random.randint(0,HUGE_NUM)
    return f"new {entity_type}" + str(int_name)

def new_user():
    new = new_entity_name("USER")
    dbu.add_user(new, FAKE_PASSWORD)
    return new

TEST_CLIENT = ep.app.test_client()

class EndpointTestCase(TestCase):
    def setUp(self):
        dbu.empty()
        dbp.empty()

    def tearDown(self):
        pass

    def test_list_playlists1(self):
        """
        Post-condition 1: return is a list.
        """
        lp = ep.ListPlaylists(Resource)
        ret = lp.get()
        self.assertIsInstance(ret, list)

    def test_list_playlists2(self):
        """
        Post-condition 2: all playlists have names
        """
        lp = ep.ListPlaylists(Resource)
        ret = lp.get()
        for pl in ret:
            self.assertIsInstance(pl['playlistName'], str)

    def test_list_playlists3(self):
        """
        Post-condition 3: the values in the list are dicts
        """
        lp = ep.ListPlaylists(Resource)
        ret = lp.get()
        for val in ret:
            self.assertIsInstance(val, dict)

    def test_create_playlist1(self):
        """
        Post-condition 1: create playlist and check if in db
        """
        body = login()
        TEST_CLIENT.post(f'/playlists/create/{body[dbu.USERNAME]}/{FAKE_PLAYLIST}', json=body)
        playlists = dbp.get_playlists_dict()
        self.assertIn(FAKE_PLAYLIST, playlists)
    
    def test_create_playlist2(self):
        """
        Post-condition 2: create duplicates and make sure only one appears
        """
        body = login()
        TEST_CLIENT.post(f'/playlists/create/{body[dbu.USERNAME]}/{FAKE_PLAYLIST}', json=body)
        playlists = dbp.get_playlists_dict()
        self.assertIn(FAKE_PLAYLIST, playlists)
        resp = TEST_CLIENT.post(f'/playlists/create/{body[dbu.USERNAME]}/{FAKE_PLAYLIST}', json=body)
        self.assertEqual(resp.json['message'], 'Playlist already exists.')
        
    def test_search_playlist1(self):
        """
        Post-condition 1: successfully search for a playlist that exists
        """
        newplaylist = new_entity_name("playlist")
        dbp.add_playlist(newplaylist, FAKE_USER)
        sp = ep.SearchPlaylist(Resource)
        ret = sp.get(newplaylist)
        self.assertEqual(newplaylist, ret[0][dbp.PLNAME])

    def test_search_playlist2(self):
        """
        Post-condition 2: searching for a playlist that does not exist returns empty list
        """    
        sp = ep.SearchPlaylist(Resource)
        ret = sp.get('zzzzzzzzzzzzzzzzz')
        self.assertEqual(ret, [])

    def test_delete_playlist1(self):
        """
        Post-condition 1: we can create and delete a playlist
        """
        new_playlist = new_entity_name("playlist")
        dbp.add_playlist(new_playlist, FAKE_USER)
        dp = ep.DeletePlaylist(Resource)
        dp.delete(new_playlist)
        self.assertNotIn(new_playlist, dbp.get_playlists())

    def test_delete_playlist2(self):
        """
        Post-condition 2: deleting a playlist that does not exist results in a wz.NotAcceptable error
        """
        new_playlist = new_entity_name("playlist")
        dp = ep.DeletePlaylist(Resource)
        self.assertRaises(wz.NotFound, dp.delete, new_playlist)

    def test_delete_playlist3(self):
        """
        Post-condition 3: deleting a playlist results in it being removed from the likes of all users who liked it
        """
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl, FAKE_USER)
        dbu.add_user(newuser, FAKE_PASSWORD)
        lp = ep.LikePlaylist(Resource)
        lp.post(newuser, newpl)
        dp = ep.DeletePlaylist(Resource)
        dp.delete(newpl)
        user = dbu.get_user(newuser)
        self.assertNotIn(newpl, user['likedPlaylists'])

    def test_add_song1(self):
        """
        Post-condition1: we can add a new song to a new playlist
        """
        body = login()
        newsong = new_entity_name("song")
        newplaylist = new_entity_name("playlist")
        dbp.add_playlist(newplaylist, body[dbu.USERNAME])
        TEST_CLIENT.post(f"/playlists/{newplaylist}/add_song/{newsong}", json=body)
        pl = dbp.get_playlist(newplaylist)
        self.assertIn(newsong, pl["songs"])

    def test_add_song2(self):
        """
        Post-condition 2: we cannot add the same song to a playlist twice
        """
        body = login()
        newsong = new_entity_name("song")
        newplaylist = new_entity_name("playlist")
        dbp.add_playlist(newplaylist, body[dbu.USERNAME])
        TEST_CLIENT.post(f"/playlists/{newplaylist}/add_song/{newsong}", json=body)
        resp = TEST_CLIENT.post(f"/playlists/{newplaylist}/add_song/{newsong}", json=body)
        self.assertEqual(resp.json['message'], "song already in playlist")

    def test_remove_song1(self):
        """
        Post-condition 1: we can remove a song from a playlist given that it is present
        """
        body = login()
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl, body[dbu.USERNAME])
        newsong = new_entity_name("song")
        dbp.add_song(newpl, newsong)
        pl = dbp.get_playlist(newpl)
        self.assertIn(newsong, pl['songs'])
        TEST_CLIENT.post(f"/playlists/{newpl}/remove_song/{newsong}", json=body)
        pl = dbp.get_playlist(newpl)
        self.assertNotIn(newsong, pl['songs'])

    def test_remove_song2(self):
        """
        Post-condition 2: Removing a song when it is not present results in an error
        """
        body = login()
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl, body[dbu.USERNAME])
        newsong = new_entity_name("song")
        resp =TEST_CLIENT.post(f"/playlists/{newpl}/remove_song/{newsong}", json=body)
        self.assertEqual(resp.json['message'], "song not in playlist")

    def test_remove_song3(self):
        """
        Post-condition 3: Removing a song from a playlist that doesn't exist results in an error
        """
        newpl = new_entity_name("playlist")
        newsong = new_entity_name("song")
        body = login()
        resp =TEST_CLIENT.post(f"/playlists/{newpl}/remove_song/{newsong}", json=body)
        self.assertEqual(resp.json['message'], "Playlist not found.")

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

def new_entity_name(entity_type):
    int_name = random.randint(0,HUGE_NUM)
    return f"new {entity_type}" + str(int_name)


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
        cu = ep.CreatePlaylist(Resource)
        new_playlist = new_entity_name("playlist")
        ret = cu.post(new_playlist)
        playlists = dbp.get_playlists_dict()
        self.assertIn(new_playlist, playlists)
    
    def test_create_playlist2(self):
        """
        Post-condition 2: create duplicates and make sure only one appears
        """
        cu = ep.CreatePlaylist(Resource)
        new_playlist = new_entity_name("playlist")
        cu.post(new_playlist)
        self.assertRaises(wz.NotAcceptable, cu.post, (new_playlist))

    def test_search_playlist1(self):
        """
        Post-condition 1: successfully search for a playlist that exists
        """
        newplaylist = new_entity_name("playlist")
        dbp.add_playlist(newplaylist)
        su = ep.SearchPlaylist(Resource)
        ret = su.get(newplaylist)
        self.assertEqual(newplaylist, ret[dbp.PLNAME])

    def test_search_playlist2(self):
        """
        Post-condition 2: searching for a playlist that does not exist returns an error
        """    
        newplaylist = new_entity_name("playlist")
        su = ep.SearchPlaylist(Resource)
        self.assertRaises(wz.NotFound, su.get, newplaylist)

    def test_delete_playlist1(self):
        """
        Post-condition 1: we can create and delete a playlist
        """
        new_playlist = new_entity_name("playlist")
        dbp.add_playlist(new_playlist)
        du = ep.DeletePlaylist(Resource)
        du.post(new_playlist)
        self.assertNotIn(new_playlist, dbp.get_playlists())

    def test_delete_playlist2(self):
        """
        Post-condition 2: deleting a playlist that does not exist results in a wz.NotAcceptable error
        """
        new_playlist = new_entity_name("playlist")
        du = ep.DeletePlaylist(Resource)
        self.assertRaises(wz.NotFound, du.post, new_playlist)

    def test_delete_playlist3(self):
        """
        Post-condition 3: deleting a playlist results in it being removed from the likes of all users who liked it
        """
        newuser = new_entity_name("user")
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl)
        dbu.add_user(newuser)
        lp = ep.LikePlaylist(Resource)
        lp.post(newuser, newpl)
        dp = ep.DeletePlaylist(Resource)
        dp.post(newpl)
        user = dbu.get_user(newuser)
        self.assertNotIn(newpl, user['likedPlaylists'])

    def test_add_song1(self):
        """
        Post-condition1: we can add a new song to a new playlist
        """
        ap = ep.AddToPlaylist(Resource)
        newsong = new_entity_name("song")
        newplaylist = new_entity_name("playlist")
        dbp.add_playlist(newplaylist)
        ap.post(newplaylist, newsong)
        pl = dbp.get_playlist(newplaylist)
        self.assertIn(newsong, pl["songs"])

    def test_add_song2(self):
        """
        Post-condition 2: we cannot add the same song to a playlist twice
        """
        ap = ep.AddToPlaylist(Resource)
        newsong = new_entity_name("song")
        newplaylist = new_entity_name("playlist")
        dbp.add_playlist(newplaylist)
        ap.post(newplaylist, newsong)
        self.assertRaises(wz.NotAcceptable, ap.post, newplaylist, newsong)

    def test_remove_song1(self):
        """
        Post-condition 1: we can remove a song from a playlist given that it is present
        """
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl)
        newsong = new_entity_name("song")
        dbp.add_song(newpl, newsong)
        pl = dbp.get_playlist(newpl)
        self.assertIn(newsong, pl['songs'])
        rs = ep.RemoveFromPlaylist(Resource)
        rs.post(newpl, newsong)
        pl = dbp.get_playlist(newpl)
        self.assertNotIn(newsong, pl['songs'])

    def test_remove_song2(self):
        """
        Post-condition 2: Removing a song when it is not present results in an error
        """
        newpl = new_entity_name("playlist")
        dbp.add_playlist(newpl)
        newsong = new_entity_name("song")
        rs = ep.RemoveFromPlaylist(Resource)
        self.assertRaises(wz.NotFound, rs.post, newpl, newsong)

    def test_remove_song3(self):
        """
        Post-condition 3: Removing a song from a playlist that doesn't exist results in an error
        """
        newpl = new_entity_name("playlist")
        newsong = new_entity_name("song")
        rs = ep.RemoveFromPlaylist(Resource)
        self.assertRaises(wz.NotFound, rs.post, newpl, newsong)

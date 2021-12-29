"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
"""

# import json
# import os
import db.db_connect as dbc

PLAYLISTS = "playlists"
USERS = "users"

PLNAME = "playlistName"
USERNAME = "userName"

client = dbc.get_client()
if client is None:
    print("FAILED TO CONNECT TO MONGODB")
    exit(1)

OK = 0
NOT_FOUND = 1
DUPLICATE = 2


def get_users():
    """
    returns all users
    """
    return dbc.fetch_all(USERS, USERNAME)


def get_playlists():
    """
    returns all playlists
    """
    return dbc.fetch_all(PLAYLISTS, PLNAME)


def user_exists(username):
    """
    return true/false whether or not user exists
    """
    rec = dbc.fetch_one(USERS, filters={USERNAME: username})
    return rec is not None


def playlist_exists(playlist_name):
    """
    return true/false whether or not playlist exists
    """
    rec = dbc.fetch_one(PLAYLISTS, filters={PLNAME: playlist_name})
    return rec is not None


def get_user(username):
    """
    return a user given a username, else NOT_FOUND
    """
    if user_exists(username):
        return dbc.fetch_one(USERS, filters={USERNAME: username})
    else:
        return NOT_FOUND


def get_playlist(playlist_name):
    """
    returns a playlist given its name, else NOT_FOUND
    """
    if playlist_exists(playlist_name):
        return dbc.fetch_one(PLAYLISTS, filters={PLNAME: playlist_name})
    else:
        return NOT_FOUND


def add_user(username):
    """
    adds a user, returns whether successful or not
    """
    if user_exists(username):
        return DUPLICATE
    else:
        dbc.insert_doc(USERS, {USERNAME: username,
                               "numFriends": 0,
                               "friends": [],
                               "numPlaylists": 0,
                               "playlists": []
                               })
        return OK


def add_playlist(playlist_name):
    """
    creates a playlist, returns whether successful or not
    """
    if playlist_exists(playlist_name):
        return DUPLICATE
    else:
        dbc.insert_doc(PLAYLISTS, {PLNAME: playlist_name,
                                   "likes": [],
                                   "songs": []
                                   })
        return OK


def update_user(user_name, update):
    """
    update an existing user given new data
    """
    if not user_exists(user_name):
        return NOT_FOUND
    else:
        dbc.update_doc(USERS, {USERNAME: user_name}, update)


def update_playlist(playlist_name, update):
    """
    update a playlist given a change
    """
    if not playlist_exists(playlist_name):
        return NOT_FOUND
    else:
        dbc.update_doc(PLAYLISTS, {PLNAME: playlist_name}, update)


def del_user(username):
    """
    delete a user by username
    """
    if user_exists(username):
        dbc.del_one(USERS, filters={USERNAME: username})
        return OK
    else:
        return NOT_FOUND


def del_playlist(playlist_name):
    """
    delete a playlist by playlist name
    """
    if playlist_exists(playlist_name):
        dbc.del_one(PLAYLISTS, filters={PLNAME: playlist_name})
        return OK
    else:
        return NOT_FOUND


def empty():
    """
    empty out the test database
    ONLY IF IN TEST_MODE
    """
    dbc.del_many(USERS)
    dbc.del_many(PLAYLISTS)

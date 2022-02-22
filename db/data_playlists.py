"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
Only for playlist related database calls
"""
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


def get_playlists():
    """
    returns all playlists
    """
    return dbc.fetch_all(PLAYLISTS, PLNAME)


def get_playlists_dict():
    """
    returns all playlists in dictionary form
    """
    return dbc.fetch_all_dict(PLAYLISTS, PLNAME)


def playlist_exists(playlist_name):
    """
    return true/false whether or not playlist exists
    """
    rec = dbc.fetch_one(PLAYLISTS, filters={PLNAME: playlist_name})
    return rec is not None


def get_playlist(playlist_name):
    """
    returns a playlist given its name, else NOT_FOUND
    """
    if playlist_exists(playlist_name):
        return dbc.fetch_one(PLAYLISTS, filters={PLNAME: playlist_name})
    else:
        return NOT_FOUND


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


def update_playlist(playlist_name, update):
    """
    update a playlist given a change
    """
    if not playlist_exists(playlist_name):
        return NOT_FOUND
    else:
        dbc.update_doc(PLAYLISTS, {PLNAME: playlist_name}, update)


def del_playlist(playlist_name):
    """
    delete a playlist by playlist name
    """
    if playlist_exists(playlist_name):
        dbc.del_one(PLAYLISTS, filters={PLNAME: playlist_name})
        return OK
    else:
        return NOT_FOUND


def add_song(pl_name, song_name):
    """
    add a song to a playlist's song list
    """
    update_playlist(pl_name, {"$push": {"songs": song_name}})


def rem_song(pl_name, song_name):
    """
    remove a song from a playlist's song list
    """
    update_playlist(pl_name, {"$pull": {"songs": song_name}})


def empty():
    """
    empty out the playlists in the database
    ONLY IF IN TEST_MODE
    """
    dbc.del_many(PLAYLISTS)

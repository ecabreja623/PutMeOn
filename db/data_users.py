"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
Only for user related database calls
"""

import db.db_connect as dbc
import db.data_playlists as dbp
import db.usertoken as token
import hashlib

PLAYLISTS = "playlists"
USERS = "users"

PLNAME = "playlistName"
USERNAME = "userName"
PASSWORD = "password"
TOKEN = "token"

client = dbc.get_client()
if client is None:
    print("FAILED TO CONNECT TO MONGODB")
    exit(1)

OK = 0
NOT_FOUND = 1
DUPLICATE = 2
NOT_ACCEPTABLE = 3


def sha(string):
    return hashlib.sha256(string.encode()).hexdigest()


def get_users():
    """
    returns all users as a list
    """
    ret = dbc.fetch_all(USERS, USERNAME)
    for user in ret:
        user.pop(PASSWORD)
    return ret


def get_users_dict():
    """
    returns all users as a dict
    """
    ret = dbc.fetch_all_dict(USERS, USERNAME)
    for user in ret:
        ret[user].pop(PASSWORD)
    return ret


def user_exists(username):
    """
    return true/false whether or not user exists
    """
    rec = dbc.fetch_one(USERS, filters={USERNAME: username})
    return rec is not None


def get_user(username):
    """
    return a user given a username, else NOT_FOUND
    """
    if user_exists(username):
        ret = dbc.fetch_one(USERS, filters={USERNAME: username})
        ret.pop(PASSWORD)
        return ret
    else:
        return NOT_FOUND


def add_user(username, password):
    """
    adds a user, returns whether successful or not
    """
    if user_exists(username):
        return DUPLICATE
    else:
        dbc.insert_doc(USERS, {USERNAME: username,
                               PASSWORD: sha(password),
                               "outgoingRequests": [],
                               "incomingRequests": [],
                               "friends": [],
                               "ownedPlaylists": [],
                               "likedPlaylists": [],
                               "token": token.blank(),
                               })
        return OK


def check_password(username, password):
    """
    checks a user's password without potentially exposing it to an endpoint
    """
    user = dbc.fetch_one(USERS, filters={USERNAME: username})
    return sha(password) == user[PASSWORD]


def login(username, password):
    """
    checks if password matches user, gen token if it does
    """
    if not user_exists(username):
        return NOT_FOUND
    if not check_password(username, password):
        return NOT_ACCEPTABLE
    else:
        newtoken = token.new()
        update_user(username, {"$set": {"token": newtoken}})
        return newtoken['id']


def check_auth(username, val):
    """
    check if user is who they claim to be
    """
    valid = val == get_user(username)['token']['id']
    if valid:
        unexpired = token.check(get_user(username)['token'])
        return valid and unexpired
    return False


def update_user(user_name, update):
    """
    update an existing user given new data
    """
    if not user_exists(user_name):
        return NOT_FOUND
    else:
        dbc.update_doc(USERS, {USERNAME: user_name}, update)


def del_user(username):
    """
    delete a user by username
    """
    if user_exists(username):
        dbc.del_one(USERS, filters={USERNAME: username})
        return OK
    else:
        return NOT_FOUND


def bef_user(usern1, usern2):
    """
    befriends 2 users by adding each other to their friends list
    removes both users from existing friend request lists
    """
    update_user(usern2, {"$push": {"friends": usern1}})
    update_user(usern1, {"$push": {"friends": usern2}})
    update_user(usern1, {"$pull": {"incomingRequests": usern2}})
    update_user(usern1, {"$pull": {"outgoingRequests": usern2}})
    update_user(usern2, {"$pull": {"incomingRequests": usern1}})
    update_user(usern2, {"$pull": {"outgoingRequests": usern1}})


def req_user(usern1, usern2):
    """
    adds usern1 to usern2's incoming requests
    adds usern2 to usern1's outgoing requests
    """
    update_user(usern2, {"$push": {"incomingRequests": usern1}})
    update_user(usern1, {"$push": {"outgoingRequests": usern2}})


def dec_req(usern1, usern2):
    """
    removes usern2 from usern1's incoming requests
    removes usern1 from usern2's outgoing requests
    """
    update_user(usern1, {"$pull": {"incomingRequests": usern2}})
    update_user(usern2, {"$pull": {"outgoingRequests": usern1}})


def unf_user(usern1, usern2):
    """
    unfriends 2 users by removing one another from their friends lists
    """
    update_user(usern2, {"$pull": {"friends": usern1}})
    update_user(usern1, {"$pull": {"friends": usern2}})


def get_users_entries(username, param):
    """
    returns a complete list of all users in a user's list
    """
    if not user_exists(username):
        return NOT_FOUND
    else:
        user = get_user(username)
        ret = []
        for friend in user[param]:
            currfriend = get_user(friend)
            ret.append(currfriend)
        return ret


def get_friends(username):
    """
    returns a complete list of a user's friends
    """
    return get_users_entries(username, 'friends')


def get_liked_playlists(username):
    """
    returns a complete list of a user's liked playlists
    """
    return get_users_playlists(username, 'likedPlaylists')


def get_created_playlists(username):
    """
    returns a complete list of a user's created playlists
    """
    return get_users_playlists(username, 'ownedPlaylists')


def get_users_playlists(username, param):
    """
    returns a complete list of all the playlists
    that a user has interacted with in some way
    """
    if not user_exists(username):
        return NOT_FOUND
    else:
        ret = []
        user = get_user(username)
        for playlist in user[param]:
            ret.append(dbp.get_playlist(playlist))
        return ret


def like_playlist(username, playlist_name):
    """
    likes a playlist by adding it to the user's playlists
    also adds the user to the playlist's likes
    """
    dbp.update_playlist(playlist_name, {"$push": {"likes": username}})
    update_user(username, {"$push": {"likedPlaylists": playlist_name}})


def unlike_playlist(username, playlist_name):
    """
    unlikes a playlist by removing it from the user's likes
    also removing the user from the playlist's likes
    """
    dbp.update_playlist(playlist_name, {"$pull": {"likes": username}})
    update_user(username, {"$pull": {"likedPlaylists": playlist_name}})


def create_playlist(username, playlist_name):
    """
    adds a playlist name to a user's created playlists
    """
    update_user(username, {"$push": {"ownedPlaylists": playlist_name}})


def delete_playlist(username, playlist_name):
    """
    deletes a playlist name from a user's created playlists
    """
    update_user(username, {"$pull": {"ownedPlaylists": playlist_name}})


def empty():
    """
    empty out the users in the database
    ONLY IF IN TEST_MODE
    """
    dbc.del_many(USERS)

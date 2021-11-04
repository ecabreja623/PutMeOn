"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
"""

import json
import os

HOME = os.environ["HOME"]

USERS_DB = f"{HOME}/db/users.json"

OK = 0
NOT_FOUND = 1
DUPLICATE = 2


def write_rooms(rooms):
    with open(USERS_DB, 'w') as f:
        json.dump(rooms, f, indent=4)


def get_users():
    """
    A function to return all chat rooms.
    """
    try:
        with open(USERS_DB) as file:
            return json.loads(file.read())
    except FileNotFoundError:
        print("Users db not found.")
        return None


def add_user(username):
    """
    Add a room to the room database.
    Until we are using a real DB, we have a potential
    race condition here.
    """
    users = get_users()
    if users is None:
        return NOT_FOUND
    elif username in users:
        return DUPLICATE
    else:
        users[username] = {"numFriends": 0, "friends": [], "numPlaylists": 0, "playlists": []}
        write_rooms(users)
        return OK
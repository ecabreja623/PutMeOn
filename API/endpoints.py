"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from http import HTTPStatus
from flask import Flask
from flask_restx import Resource, Api
import werkzeug.exceptions as wz
import db.data as db

app = Flask(__name__)
api = Api(app)

HELLO = 'Hola'
WORLD = 'mundo'


@api.route('/hello')
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        It just answers with "hola mundo".
        """
        return {HELLO: WORLD}


@api.route('/endpoints')
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}

# USER METHODS


@api.route('/users/list')
class ListUsers(Resource):
    """
    THis endpoints returns a list of all the users
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        """
        Returns a list of all the users
        """
        users = db.get_users()
        return users


@api.route('/users/create/<username>')
class CreateUser(Resource):
    """
    This class supports adding a user to the database.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, username):
        """
        This method adds a user to the database
        """
        ret = db.add_user(username)
        if ret == db.DUPLICATE:
            raise (wz.NotAcceptable("User already exists."))
        return f"{username} added."


@api.route('/users/search/<username>')
class SearchUser(Resource):
    """
    This class supports finding a user given its username
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def get(self, username):
        """
        This method finds a user in the database
        """
        ret = db.get_user(username)
        if ret == db.NOT_FOUND:
            raise (wz.NotFound("User not found."))
        return ret


@api.route('/users/delete/<username>')
class DeleteUser(Resource):
    """
    This class supports deleting a user from the database.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, username):
        """
        This method deletes a user from the database
        """
        ret = db.get_user(username)
        if ret == db.NOT_FOUND:
            raise (wz.NotFound("User db not found."))
        else:
            unliker = UnlikePlaylist(Resource)
            for pl in ret["playlists"]:
                unliker.post(username, pl)
            unfriender = UnfriendUser(Resource)
            for friend in ret['friends']:
                unfriender.post(username, friend)
            db.del_user(username)
        return f"{username} deleted."


@api.route('/users/<usern1>/add_friend/<usern2>')
class BefriendUser(Resource):
    """
    This class supports two users adding each other as friends
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, usern1, usern2):
        """
        This method adds two users to each others friend lists
        """
        if usern1 != usern2:
            user1, user2 = db.get_user(usern1), db.get_user(usern2)
            if user1 == db.NOT_FOUND or user2 == db.NOT_FOUND:
                raise(wz.NotFound("At least one user not found"))
            elif usern1 in user2["friends"] or usern2 in user1["friends"]:
                raise(wz.NotAcceptable("Users are already friends"))
            else:
                db.update_user(usern2, {"$push": {"friends": usern1}})
                db.update_user(usern1, {"$push": {"friends": usern2}})
                db.update_user(usern2, {"$inc": {"numFriends": 1}})
                db.update_user(usern1, {"$inc": {"numFriends": 1}})
                return "Users added eachother as friends"
        else:
            raise(wz.NotAcceptable("User cannot add themself as a friend"))


@api.route('/users/<usern1>/remove_friend/<usern2>')
class UnfriendUser(Resource):
    """
    This class supports two users removing one another from their friends
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, usern1, usern2):
        """
        This method removes two users from each others friend lists
        """
        user1, user2 = db.get_user(usern1), db.get_user(usern2)
        if user1 == db.NOT_FOUND or user2 == db.NOT_FOUND:
            raise(wz.NotFound("At least one user not found"))
        elif usern1 in user2["friends"] or usern2 in user1["friends"]:
            db.update_user(usern2, {"$pull": {"friends": usern1}})
            db.update_user(usern1, {"$pull": {"friends": usern2}})
            db.update_user(usern2, {"$inc": {"numFriends": -1}})
            db.update_user(usern1, {"$inc": {"numFriends": -1}})
            return "Users removed eachother as friends"
        else:
            raise(wz.NotAcceptable("Users are not friends"))


@api.route('/users/<username>/like_playlist/<playlist_name>')
class LikePlaylist(Resource):
    """
    This class supports a user liking a playlist
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, username, playlist_name):
        """
        This method supports a user liking a playlist
        """
        user, playlist = db.get_user(username), db.get_playlist(playlist_name)
        if user == db.NOT_FOUND:
            raise(wz.NotFound("User not found"))
        elif playlist == db.NOT_FOUND:
            raise(wz.NotFound("Playlist not found"))
        elif playlist_name in user['playlists']:
            raise(wz.NotAcceptable("User has already liked this playlist"))
        else:
            db.update_playlist(playlist_name, {"$inc": {"likes": 1}})
            db.update_user(username, {"$push": {"playlists": playlist_name}})
            db.update_user(username, {"$inc": {"numPlaylists": 1}})
            return f"{username} added {playlist_name} to their playlists"


@api.route('/users/<username>/unlike_playlist/<playlist_name>')
class UnlikePlaylist(Resource):
    """
    This class supports a user unliking a playlist
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, username, playlist_name):
        """
        This method supports a user unliking a playlist
        """
        user, playlist = db.get_user(username), db.get_playlist(playlist_name)
        if user == db.NOT_FOUND:
            raise(wz.NotFound("User not found"))
        elif playlist == db.NOT_FOUND:
            raise(wz.NotFound("Playlist not found"))
        elif playlist_name not in user["playlists"]:
            raise(wz.NotFound("Playlist not in user's likes"))
        else:
            db.update_playlist(playlist_name, {"$inc": {"likes": -1}})
            db.update_user(username, {"$pull": {"playlists": playlist_name}})
            db.update_user(username, {"$inc": {"numPlaylists": -1}})
            return f"{username} removed {playlist_name} from their playlists"

# PLAYLIST METHODS


@api.route('/playlists/list')
class ListPlaylists(Resource):
    """
    THis endpoints returns a list of all the playlists
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        """
        Returns a list of all the playlists
        """
        playlists = db.get_playlists()
        if playlists is None:
            raise (wz.NotFound("Users db not found."))
        else:
            return playlists


@api.route('/playlists/create/<playlist_name>')
class CreatePlaylist(Resource):
    """
    This class supports adding a playlist to the database.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, playlist_name):
        """
        This method adds a playlist to the database
        """
        ret = db.add_playlist(playlist_name)
        if ret == db.NOT_FOUND:
            raise (wz.NotFound("Playlist db not found."))
        elif ret == db.DUPLICATE:
            raise (wz.NotAcceptable("Playlist already exists."))
        return f"{playlist_name} added."


@api.route('/playlists/search/<playlist_name>')
class SearchPlaylist(Resource):
    """
    This class supports finding a playlist given its name
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def get(self, playlist_name):
        """
        This method searches for a playlist in the database
        """
        ret = db.get_playlist(playlist_name)
        if ret == db.NOT_FOUND:
            raise (wz.NotFound("playlist not found."))
        return ret


@api.route('/playlists/delete/<playlist_name>')
class DeletePlaylist(Resource):
    """
    This class supports deleting a playlist from the database.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, playlist_name):
        """
        This method deletes a playlist from the database
        """
        ret = db.get_playlist(playlist_name)
        if ret == db.NOT_FOUND:
            raise (wz.NotFound("Playlist db not found."))
        else:
            up = UnlikePlaylist(Resource)
            for user in db.get_users():
                try:
                    up.post(playlist_name, user)
                except wz.NotFound:
                    pass
            db.del_playlist(playlist_name)
            return f"{playlist_name} deleted."


@api.route('/playlists/<pl_name>/add_song/<song_name>')
class AddToPlaylist(Resource):
    """
    This class supports adding a song to a playlist in the database.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, pl_name, song_name):
        """
        This method adds a song to a playlist in the database
        """
        playlist = db.get_playlist(pl_name)
        if playlist == db.NOT_FOUND:
            raise (wz.NotFound("Playlist db not found."))
        else:
            if song_name in playlist["songs"]:
                raise (wz.NotAcceptable("song already in playlist"))
            else:
                db.update_playlist(pl_name, {"$push": {"songs": song_name}})
                return f"{song_name} added to {pl_name}."


@api.route('/playlists/<pl_name>/remove_song/<song_name>')
class RemoveFromPlaylist(Resource):
    """
    This class supports removing a song from a playlist in the database.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, pl_name, song_name):
        """
        This method removes a song from a playlist in the database
        """
        playlist = db.get_playlist(pl_name)
        if playlist == db.NOT_FOUND:
            raise (wz.NotFound("Playlist not found."))
        else:
            if song_name not in playlist["songs"]:
                raise (wz.NotFound("song not in playlist"))
            else:
                db.update_playlist(pl_name, {"$pull": {"songs": song_name}})
                return f"{song_name} removed from {pl_name}."

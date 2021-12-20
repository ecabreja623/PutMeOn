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
        if users is None:
            raise (wz.NotFound("Users db not found."))
        else:
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
        if ret == db.NOT_FOUND:
            raise (wz.NotFound("User db not found."))
        elif ret == db.DUPLICATE:
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
        ret = db.del_user(username)
        if ret == db.NOT_FOUND:
            raise (wz.NotFound("User db not found."))
        elif ret == db.DUPLICATE:
            raise (wz.NotAcceptable("User already exists."))
        return f"{username} deleted."

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
        ret = db.add_user(playlist_name)
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

@api.route('/users/delete/<playlist_name>')
class DeletePlaylist(Resource):
    """
    This class supports deleting a user from the database.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, playlist_name):
        """
        This method adds a user to the database
        """
        ret = db.del_playlist(playlist_name)
        if ret == db.NOT_FOUND:
            raise (wz.NotFound("Playlist db not found."))
        elif ret == db.DUPLICATE:
            raise (wz.NotAcceptable("Playlist already exists."))
        return f"{playlist_name} deleted."
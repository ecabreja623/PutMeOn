"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from http import HTTPStatus
from flask import Flask, request
from flask_cors import CORS
from flask_restx import Resource, Api, fields
import werkzeug.exceptions as wz
import db.data_playlists as dbp
import db.data_users as dbu

app = Flask(__name__)
api = Api(app)
CORS(app)

user_ns = api.namespace('users', description="User related endpoints")
playlist_ns = api.namespace('playlists',
                            description="Playlist related endpoints")

HELLO = 'Hola'
WORLD = 'mundo'

TOKEN_FIELDS = api.model('User_Token', {
    dbu.USERNAME: fields.String,
    dbu.TOKEN: fields.String
})


def verify_header(json, username=None):
    """
    easier than just writing these 3 lines over and over
    """
    if not username:
        username = json[dbu.USERNAME]
    token = json[dbu.TOKEN]
    name = json[dbu.USERNAME]
    if not dbu.check_auth(name, token) or username != name:
        raise (wz.NotAcceptable("INVALID SESSION"))


@api.route('/hello')
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    @api.expect(TOKEN_FIELDS)
    def post(self):
        """
        A trivial endpoint to see if the server is running.
        It just answers with "hola mundo".
        """
        verify_header(request.json)
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


@user_ns.route('/list')
class ListUsers(Resource):
    """
    THis endpoints returns a list of all the users
    """
    @user_ns.response(HTTPStatus.OK, 'Success')
    @user_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        """
        Returns a list of all the users
        """
        users = dbu.get_users()
        return users


@user_ns.route('/create/<username>_<password>')
class CreateUser(Resource):
    """
    This class supports adding a user to the database.
    """
    @user_ns.response(HTTPStatus.OK, 'Success')
    @user_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @user_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, username, password):
        """
        This method adds a user to the database
        """
        ret = dbu.add_user(username, password)
        if ret == dbu.DUPLICATE:
            raise (wz.NotAcceptable("User already exists."))
        return f"{username} added."


@user_ns.route('/login/<username>_<password>')
class LoginUser(Resource):
    """
    This class supports a user getting authorization from the API
    given the correct username and password
    """
    def get(self, username, password):
        """
        This method supports telling the frontend
        if their authorization details are correct
        returns auth token
        """
        token = dbu.login(username, password)
        if token == dbu.NOT_FOUND:
            raise (wz.NotFound("Username not found"))
        elif token == dbu.NOT_ACCEPTABLE:
            raise (wz.NotAcceptable("Incorrect Password"))
        else:
            return {dbu.TOKEN: token}


@user_ns.route('/get/<username>')
class GetUser(Resource):
    """
    This class supports finding a user given its username
    """
    @user_ns.response(HTTPStatus.OK, 'Success')
    @user_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @user_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def get(self, username):
        """
        This method finds a user in the database
        """
        ret = dbu.get_user(username)
        if ret == dbu.NOT_FOUND:
            raise (wz.NotFound("User not found."))
        return ret


@user_ns.route('/search/<username>')
class SearchUser(Resource):
    """
    This class supports finding a user given its username
    """
    @user_ns.response(HTTPStatus.OK, 'Success')
    @user_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @user_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def get(self, username):
        """
        This method finds a user in the database
        """
        ret = dbu.get_users()
        ret = [user for user in ret if username in user[dbu.USERNAME]]
        if ret == dbu.NOT_FOUND:
            raise (wz.NotFound("User not found."))
        return ret


@user_ns.route('/delete/<username>')
class DeleteUser(Resource):
    """
    This class supports deleting a user from the database.
    """
    @user_ns.response(HTTPStatus.OK, 'Success')
    @user_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @user_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    @user_ns.expect(TOKEN_FIELDS)
    def delete(self, username):
        """
        This method deletes a user from the database
        """
        ret = dbu.get_user(username)
        verify_header(request.json, username)
        if ret == dbu.NOT_FOUND:
            raise (wz.NotFound("User db not found."))
        else:
            deleter = DeletePlaylist(Resource)
            for pl in ret['ownedPlaylists']:
                deleter.delete(pl)
            unliker = UnlikePlaylist(Resource)
            for pl in ret["likedPlaylists"]:
                unliker.post(username, pl)
            unfriender = UnfriendUser(Resource)
            for friend in ret['friends']:
                unfriender.post(username, friend)
            decliner = DecRequest(Resource)
            for friend in ret['outgoingRequests']:
                decliner.post(friend, username)
            for friend in ret['incomingRequests']:
                decliner.post(username, friend)
            dbu.del_user(username)
        return f"{username} deleted."


@user_ns.route('/<usern1>/req_friend/<usern2>')
class RequestUser(Resource):
    """
    this class supports one user sending a friend request to another
    """
    @user_ns.response(HTTPStatus.OK, 'Success')
    @user_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @user_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, usern1, usern2):
        """
        This method adds two users to each others friend lists
        """
        if usern1 != usern2:
            user1, user2 = dbu.get_user(usern1), dbu.get_user(usern2)
            if user1 == dbu.NOT_FOUND or user2 == dbu.NOT_FOUND:
                raise(wz.NotFound("At least one user not found"))
            elif usern1 in user2["friends"] or usern2 in user1["friends"]:
                raise(wz.NotAcceptable("Users are already friends"))
            elif usern1 in user2['outgoingRequests'] or \
                    usern2 in user1['incomingRequests']:
                raise(wz.NotAcceptable(f"{usern2} already sent\
                     {usern1} a friend request"))
            elif usern2 in user1['outgoingRequests'] or \
                    usern1 in user2['incomingRequests']:
                raise(wz.NotAcceptable(f"{usern1} already sent {usern2} \
                    a friend request"))
            else:
                dbu.req_user(usern1, usern2)
                return f"{usern1} sent {usern2} a friend request"
        else:
            raise(wz.NotAcceptable("User cannot send themself \
                a friend request"))


@user_ns.route('/<usern1>/dec_request/<usern2>')
class DecRequest(Resource):
    """
    this class supports one user removing another from their friend requests
    """
    @user_ns.response(HTTPStatus.OK, 'Success')
    @user_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @user_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, usern1, usern2):
        """
        This method removes two users to each others request lists
        """
        if usern1 != usern2:
            user1, user2 = dbu.get_user(usern1), dbu.get_user(usern2)
            if user1 == dbu.NOT_FOUND or user2 == dbu.NOT_FOUND:
                raise(wz.NotFound("At least one user not found"))
            if usern1 in user2['outgoingRequests'] and \
                    usern2 in user1['incomingRequests']:
                dbu.dec_req(usern1, usern2)
                return f"{usern1} removed {usern2} from their friend requests"
            else:
                raise(wz.NotAcceptable(f"{usern2} has not sent \
                    {usern1} a friend request!"))
        else:
            raise(wz.NotAcceptable("User cannot send themself \
                a friend request"))


@user_ns.route('/<usern1>/add_friend/<usern2>')
class BefriendUser(Resource):
    """
    This class supports two users adding each other as friends
    only if user2 has sent user1 a friend request
    """
    @user_ns.response(HTTPStatus.OK, 'Success')
    @user_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @user_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, usern1, usern2):
        """
        This method adds two users to each others friend lists
        """
        if usern1 != usern2:
            user1, user2 = dbu.get_user(usern1), dbu.get_user(usern2)
            if user1 == dbu.NOT_FOUND or user2 == dbu.NOT_FOUND:
                raise(wz.NotFound("At least one user not found"))
            elif usern1 in user2["friends"] or usern2 in user1["friends"]:
                raise(wz.NotAcceptable("Users are already friends"))
            elif usern1 in user2['outgoingRequests'] and \
                    usern2 in user1['incomingRequests']:
                dbu.bef_user(usern1, usern2)
                return f"{usern1} and {usern2} are now friends"
            elif usern2 in user1['outgoingRequests'] and \
                    usern1 in user2['incomingRequests']:
                dbu.bef_user(usern2, usern1)
                return f"{usern2} and {usern1} are now friends"
            else:
                return(wz.NotAcceptable("Neither user has\
                     sent a friend request"))
        else:
            raise(wz.NotAcceptable("User cannot add themself as a friend"))


@user_ns.route('/<usern1>/remove_friend/<usern2>')
class UnfriendUser(Resource):
    """
    This class supports two users removing one another from their friends
    """
    @user_ns.response(HTTPStatus.OK, 'Success')
    @user_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @user_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, usern1, usern2):
        """
        This method removes two users from each others friend lists
        """
        user1, user2 = dbu.get_user(usern1), dbu.get_user(usern2)
        if user1 == dbu.NOT_FOUND or user2 == dbu.NOT_FOUND:
            raise(wz.NotFound("At least one user not found"))
        elif usern1 in user2["friends"] or usern2 in user1["friends"]:
            dbu.unf_user(usern1, usern2)
            return f"{usern1} and {usern2} are no longer friends"
        else:
            raise(wz.NotAcceptable("Users are not friends"))


@user_ns.route('/<username>/like_playlist/<playlist_name>')
class LikePlaylist(Resource):
    """
    This class supports a user liking a playlist
    """
    @user_ns.response(HTTPStatus.OK, 'Success')
    @user_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @user_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, username, playlist_name):
        """
        This method supports a user liking a playlist
        """
        user = dbu.get_user(username)
        playlist = dbp.get_playlist(playlist_name)
        if user == dbu.NOT_FOUND:
            raise(wz.NotFound(f"User {username} not found"))
        elif playlist == dbp.NOT_FOUND:
            raise(wz.NotFound(f"Playlist {playlist_name} not found"))
        elif playlist_name in user['likedPlaylists'] or \
                username in playlist['likes']:
            raise(wz.NotAcceptable(f"{username} has already\
             liked {playlist_name}"))
        else:
            dbu.like_playlist(username, playlist_name)
            return f"{username} added {playlist_name} to their playlists"


@user_ns.route('/<username>/unlike_playlist/<playlist_name>')
class UnlikePlaylist(Resource):
    """
    This class supports a user unliking a playlist
    """
    @user_ns.response(HTTPStatus.OK, 'Success')
    @user_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @user_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, username, playlist_name):
        """
        This method supports a user unliking a playlist
        """
        user = dbu.get_user(username)
        playlist = dbp.get_playlist(playlist_name)
        if user == dbu.NOT_FOUND:
            raise(wz.NotFound(f"User {username} not found"))
        elif playlist == dbp.NOT_FOUND:
            raise(wz.NotFound(f"Playlist {playlist_name} not found"))
        elif playlist_name not in user["likedPlaylists"] or \
                username not in playlist['likes']:
            raise(wz.NotFound(f"{playlist_name} not in {username}'s likes"))
        else:
            dbu.unlike_playlist(username, playlist_name)
            return f"{username} removed {playlist_name} from their playlists"


@user_ns.route('/get_friends/<username>')
class GetFriends(Resource):
    """
    This class supports listing all of a user's friends
    """
    @user_ns.response(HTTPStatus.NOT_FOUND, 'User not found')
    def get(self, username):
        """
        This method supports listing all of a user's friends
        """
        user = dbu.get_user(username)
        if user == dbu.NOT_FOUND:
            raise(wz.NotFound(f"User {username} not found"))
        else:
            return dbu.get_friends(username)


@user_ns.route('/get_owned_playlists/<username>')
class GetOwnedPlaylists(Resource):
    """
    This class supports listing all playlists a user has created
    """
    @user_ns.response(HTTPStatus.NOT_FOUND, 'User not found')
    def get(self, username):
        """
        This method supports listing all the playlists a user created
        """
        user = dbu.get_user(username)
        if user == dbu.NOT_FOUND:
            raise(wz.NotFound(f"User {username} not found"))
        else:
            return dbu.get_created_playlists(username)


@user_ns.route('/get_likes/<username>')
class GetLikedPlaylists(Resource):
    """
    This class supports listing all of a user's liked playlists
    """
    @user_ns.response(HTTPStatus.NOT_FOUND, 'User not found')
    def get(self, username):
        """
        This method supports listing all of a user's liked playlists
        """
        user = dbu.get_user(username)
        if user == dbu.NOT_FOUND:
            raise(wz.NotFound(f"User {username} not found"))
        else:
            return dbu.get_liked_playlists(username)


# PLAYLIST METHODS


@playlist_ns.route('/list')
class ListPlaylists(Resource):
    """
    THis endpoints returns a list of all the playlists
    """
    @playlist_ns.response(HTTPStatus.OK, 'Success')
    @playlist_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        """
        Returns a list of all the playlists
        """
        playlists = dbp.get_playlists()
        if playlists is None:
            raise (wz.NotFound("Users db not found."))
        else:
            return playlists


@playlist_ns.route('/create/<user_name>/<playlist_name>')
class CreatePlaylist(Resource):
    """
    This class supports adding a playlist to the database.
    """
    @playlist_ns.response(HTTPStatus.OK, 'Success')
    @playlist_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @playlist_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    @playlist_ns.expect(TOKEN_FIELDS)
    def post(self, user_name, playlist_name):
        """
        This method adds a playlist to the database
        """
        verify_header(request.json, user_name)
        ret = dbp.add_playlist(playlist_name, user_name)
        if ret == dbp.NOT_FOUND:
            raise (wz.NotFound("Playlist db not found."))
        elif ret == dbp.DUPLICATE:
            raise (wz.NotAcceptable("Playlist already exists."))
        dbu.create_playlist(user_name, playlist_name)
        return f"{user_name} created {playlist_name}."


@playlist_ns.route('/search/<playlist_name>')
class SearchPlaylist(Resource):
    """
    This class supports finding a playlist given its name
    """
    @playlist_ns.response(HTTPStatus.OK, 'Success')
    @playlist_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @playlist_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def get(self, playlist_name):
        """
        This method searches for a playlist in the database
        """
        ret = dbp.get_playlists()
        ret = [pl for pl in ret if playlist_name in pl['playlistName']]
        if ret == dbp.NOT_FOUND:
            raise (wz.NotFound("playlist not found."))
        return ret


@playlist_ns.route('/delete/<playlist_name>')
class DeletePlaylist(Resource):
    """
    This class supports deleting a playlist from the database.
    """
    @playlist_ns.response(HTTPStatus.OK, 'Success')
    @playlist_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @playlist_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def delete(self, playlist_name):
        """
        This method deletes a playlist from the database
        """
        playlist = dbp.get_playlist(playlist_name)
        if playlist == dbp.NOT_FOUND:
            raise (wz.NotFound("Playlist db not found."))
        else:
            up = UnlikePlaylist(Resource)
            for user in playlist['likes']:
                up.post(user, playlist_name)
            dbp.del_playlist(playlist_name)
            return f"{playlist_name} deleted."


@playlist_ns.route('/<pl_name>/add_song/<song_name>')
class AddToPlaylist(Resource):
    """
    This class supports adding a song to a playlist in the database.
    """
    @playlist_ns.response(HTTPStatus.OK, 'Success')
    @playlist_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @playlist_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, pl_name, song_name):
        """
        This method adds a song to a playlist in the database
        """
        playlist = dbp.get_playlist(pl_name)
        if playlist == dbp.NOT_FOUND:
            raise (wz.NotFound("Playlist db not found."))
        else:
            if song_name in playlist["songs"]:
                raise (wz.NotAcceptable("song already in playlist"))
            else:
                dbp.add_song(pl_name, song_name)
                return f"{song_name} added to {pl_name}."


@playlist_ns.route('/<pl_name>/remove_song/<song_name>')
class RemoveFromPlaylist(Resource):
    """
    This class supports removing a song from a playlist in the database.
    """
    @playlist_ns.response(HTTPStatus.OK, 'Success')
    @playlist_ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @playlist_ns.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def post(self, pl_name, song_name):
        """
        This method removes a song from a playlist in the database
        """
        playlist = dbp.get_playlist(pl_name)
        if playlist == dbp.NOT_FOUND:
            raise (wz.NotFound("Playlist not found."))
        else:
            if song_name not in playlist["songs"]:
                raise (wz.NotFound("song not in playlist"))
            else:
                dbp.rem_song(pl_name, song_name)
                return f"{song_name} removed from {pl_name}."

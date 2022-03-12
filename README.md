# Put Me On

API currently hosted on https://put-me-on.herokuapp.com/
Frontend repo at https://github.com/jdahhan/PutMeOn_FrontEnd
frontend deployed to https://putmeon.netlify.app/

## Requirements

- Create a profile page that displays their data
- Search for other users/friends/playlists 
- Create, delete, and update playlists
- List playlists
- Create and delete users 
- List users 
- Add/remove friends
- Like/unlike playlists

## Design

- Use flask_restx to build an API server
- Multiple clients possible -- TBD
- Handle each major requirement with an API endpoint
- Use Test-Driven-Development (TDD) to make sure we have testing
- Use Swagger for initial interaction with server
- Use Swagger, pydoc and good docstrings for documentation
- Use Travis as the CI/CD pipeline
- Use Heroku to deploy the app

- Users can create a user using the '/users/create' endpoint
    - users must pass a unique username 
- Users can delete a user using the '/users/delete' endpoint
- Users can create playlists using the '/playlists/create' 
    - users must pass unique playlist name 
    - user must already exist
- Users can delete their playlist using the '/playlists/delete' endpoint 
- Users can update their playlist using the '/playlists/add_song' and '/playlists/delete_song' endpoints
- Users can search for their friend using the '/users/search' endpoint 
    - user must pass their friend's username 
- Users can search for a playlist using the '/playlists/search' endpoint
- Users can send eachother friend requests using '/users/req_friend' endpoint
    - Each user must not have any pending friend requests from the other
    - Both users cannot already be friends
- Users can add or remove one another as friends using the '/users/add_friend' and 'users/remove_friend' endpoints
    - A user can only add another user if that user has first sent them a friend request.
    - Both users must be distinct and already exist
    - Users cannot be friends prior to adding one another
    - Users must be friends prior to removing one another
- Users can like/unlike a playlist using the 'users/like_playlist' and 'users/unlike_playlist' endpoints
    - Playlist cannot already be liked if user is liking it
    - Playlist must already be liked if user is unliking it

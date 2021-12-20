# Put Me On

## Requirements

- Create a profile page that displays their data
- Search for other users/friends 
- Create, delete, and update playlists
- List playlists
- Create and delete users 
- List users 

## Design

- Use flask_restx to build an API server
- Multiple clients possible -- TBD
- Handle each major requirement with an API endpoint
- Use Test-Driven-Development (TDD) to make sure we have testing
- Use Swagger for initial interaction with server
- Use Swagger, pydoc and good docstrings for documentation
- Use Travis as the CI/CD pipeline
- Use Heroku to deploy the app

- Users can create a user using the '/create_user' endpoint
    - users must pass a unique username 
- Users can delete a user using the '/delete_user' endpoint
- Users can create playlists using the '/create_playlist' 
    - users must pass playlist name 
    - user must already exist
- Users can delete their playlist using the 'delete_playlist' endpoint 
- Users can update their playlist using the 'update_playlist' endpoint
- Users can search for their friend using the 'search' endpoint 
    - user must pass their friend's username 


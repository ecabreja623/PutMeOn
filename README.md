# Put Me On

## Requirements

- Create a profile page that displays their data
- Search for other users/friends 
- Create and delete playlists

## Design

- Use flask_restx to build an API server
- Multiple clients possible -- TBD
- Handle each major requirement with an API endpoint
- Use Test-Driven-Development (TDD) to make sure we have testing
- Use Swagger for initial interaction with server
- Use Swagger, pydoc and good docstrings for documentation
- Use Travis as the CI/CD pipeline
- Use Heroku to deploy the app

- Users can create a profile page using the '/create_page' endpoint
    - users must pass a unique username 
    - this will add to the database a dictionary containing initial information about a user
        - number of friends 
        - list of friends 
        - number of playlists 
        - list of playlists 
- Users can create playlists using the '/create_playlist' 
    - users must pass playlist name 
    - user must already exist
- Users can delete their playlist using the 'delete_playlist' endpint 
- Users can search for their friend using the 'search' endpoint 
    - user must pass their friend's username 


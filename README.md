# SongSpot
### A Spotify Analyzer and Recommendations Generator
CS 310 Final Project (Last Updated: 05-27-2024)

## Functions

Using the SpotifyAPI, SongSpot completes 6 functions:
1. Prints out the user's top 10 artists
2. Prints out the user's top 10 tracks
3. Analyzes the genres of the user's music taste and prints out a list of their top genres
4. Computes the popularity of the user's music taste and prints out a popularity score
5. Generates a user-given number of recommendations
    - No song will be recommended twice in a given session
6. Prints out all songs recommended during the session, and optionally makes them a playlist in the user's Spotify account

Functions 1-5 have the option of analyzing different time ranges (long_term, medium_term, short_term.)

## Technical Details
- The program runs on a Flask application deployed to an EC2 server.
- The UI consists of simple print statements on the Flask client-side.
- Every function utilizes and interacts with the Spotify API and database.
- Functions 3-5 involve computation.
- Functions 5 and 6 utilize RDS.
    - In function 5, recommeded songs are stored in a database and referenced so that no songs are recommeded more than once in a given session
    - In function 6, all the songs recommended during the session are retrieved and printed out. The user can then choose to have SongSpot create a playlist in their account with these songs.
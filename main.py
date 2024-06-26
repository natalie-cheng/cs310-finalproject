#
# Client-side python flask app for songspot
#

import sys
import os
import spotipy
import datatier
from spotipy.oauth2 import SpotifyOAuth

from flask import Flask, request, redirect
from configparser import ConfigParser


############################################################
#
# flask setup, rds setup, spotify authentication
#

# setup flask app
app = Flask(__name__)

# read config file
config = ConfigParser()
config.read('config.ini')

# read rds read-write credentials
rds_endpoint = config.get('rds-read-write', 'endpoint')
rds_portnum = int(config.get('rds-read-write', 'port_number'))
rds_username = config.get('rds-read-write', 'user_name')
rds_pwd = config.get('rds-read-write', 'user_pwd')
rds_dbname = config.get('rds-read-write', 'db_name')

try:
    # open the connection
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    # drop the existing songs table
    sql = "DROP TABLE IF EXISTS songs;"
    datatier.perform_action(dbConn, sql)

    # create an empty songs table
    sql = """
        CREATE TABLE songs(
            song_id     varchar(64) not null,
            track_name  varchar(128) not null,
            artist      varchar(128) not null,
            PRIMARY KEY (song_id)
        );
        """
    datatier.perform_action(dbConn, sql)

except Exception as e:
        print("Error setting up song table:", str(e))

# spotify credentials
CLIENT_ID = config.get('spotify', 'client_id')
CLIENT_SECRET = config.get('spotify', 'client_secret')
REDIRECT_URI = config.get('spotify', 'redirect_uri')

# spotify authentication manager
scope = 'user-top-read playlist-modify-private'
auth_manager = SpotifyOAuth(client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET,
                            redirect_uri=REDIRECT_URI,
                            scope=scope)

# spotipy object
sp = None

# default route
@app.route('/')
def login():
    return redirect(auth_manager.get_authorize_url())

# callback route
@app.route('/callback')
def callback():
    token_info = auth_manager.get_cached_token()
    if not token_info:
        code = request.args.get('code')
        auth_manager.get_access_token(code)
    # if token_info:
    global sp
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return main_menu()

############################################################
#
# main command line menu
#

def main_menu():
    while True:
        print("\nWelcome to SongSpot!")
        print(">> Enter a command:")
        print("   0 => exit")
        print("   1 => top 10 artists")
        print("   2 => top 10 tracks")
        print("   3 => analyze genres")
        print("   4 => analyze popularity")
        print("   5 => generate recommendations")
        print("   6 => print all recommendations")

        cmd = input()

        # commands
        if cmd == '0':
            break
        elif cmd == '1':
            time = input("time range? (long_term, medium_term, short_term)\n")
            print_user_top_items('artists', time)
        elif cmd == '2':
            time = input("time range? (long_term, medium_term, short_term)\n")
            print_user_top_items('tracks', time)
        elif cmd == '3':
            time = input("time range? (long_term, medium_term, short_term)\n")
            analyze_user_genre(time)
        elif cmd == '4':
            time = input("time range? (long_term, medium_term, short_term)\n")
            analyze_user_popularity(time)
        elif cmd == '5':
            time = input("time range? (long_term, medium_term, short_term)\n")
            number = input("how many songs?\n")
            recommend_songs(time, number)
        elif cmd == '6':
            print_all_recommendations()
        else:
            print("invalid command")

    return "done - exit through command line"


############################################################
#
# functions
#

#
# get user top items
#
def get_user_top_items(item_type, time_range='medium_term', limit=10):
    """
    Retrieves top artists or tracks for a user

    Parameters
    ----------
    item_type: artists or tracks
    time_range: long_term, medium_term (default), short_term
    limit: # of items

    Returns
    -------
    list of top items
    """

    if time_range not in ['long_term', 'medium_term', 'short_term']:
        print("invalid time range")
        return

    if item_type == 'artists':
        top_items = sp.current_user_top_artists(time_range=time_range, limit=limit)
    else:
        top_items = sp.current_user_top_tracks(time_range=time_range, limit=limit)
    
    return top_items['items']

#
# print top itmes
#
def print_user_top_items(filter, time = 'medium_term'):
    """
    Print user's top artists or tracks

    Parameters
    ----------
    filter: artists or tracks
    time: time frame

    Returns
    -------
    none
    """

    if filter == 'artists':
        top_artists = get_user_top_items('artists', time)
        if not top_artists: return
        print("\ntop 10 artists:")
        for i, artist in enumerate(top_artists):
            print(f"{i+1}. {artist['name']}")
    
    else:
        top_tracks = get_user_top_items('tracks', time)
        if not top_tracks: return
        print("\ntop 10 tracks:")
        for i, track in enumerate(top_tracks):
            print(f"{i+1}. {track['name']} by {track['artists'][0]['name']}")

#
# analyze user genres
#
def analyze_user_genre(time):
    """
    Extract the genres of the user's music taste

    Parameters
    ----------
    time: time frame to analyze tracks

    Returns
    -------
    none
    """

    top_artists = get_user_top_items('artists', time)
    if not top_artists: return

    genres = []

    for artist in top_artists:
        genres.extend(artist['genres'])
    
    genres = list(set(genres))
    print(f"\ngenres: {', '.join(genres)}")

#
# analyze user popularity
#
def analyze_user_popularity(time):
    """
    Analyze the popularity of the user's music taste

    Parameters
    ----------
    time: time frame to analyze tracks

    Returns
    -------
    none
    """

    top_artists = get_user_top_items('artists', time)
    top_tracks = get_user_top_items('tracks', time)
    if not top_artists or not top_tracks: return
    
    artist_pop = []
    track_pop = []

    # extract the popularity of the user's top artists and tracks
    for artist in top_artists:
        artist_pop.append(artist['popularity'])
    
    for track in top_tracks:
        track_pop.append(track['popularity'])
    
    # calculate averages
    avg_artist_pop = sum(artist_pop) / len(artist_pop) if artist_pop else 0
    avg_track_pop = sum(track_pop) / len(track_pop) if track_pop else 0
    popularity = artist_pop + track_pop
    avg_popularity = sum(popularity) / len(popularity) if popularity else 0
    
    print("\nscale from 0 (least popular) to 100 (most popular)")
    print(f"average artist popularity: {avg_artist_pop}")
    print(f"average song popularity: {avg_track_pop}")
    print(f"general average popularity: {avg_popularity}")

#
# recommend songs
#
def recommend_songs(time, number):
    """
    Generate a recommended playlist of new songs for the user.
    Check if the recommended songs exist in the database ie. have been recommended before
    If so, find new songs to recommend

    Parameters
    ----------
    time: time frame to seed the recommendations
    number: # of songs to recommend

    Returns
    -------
    none
    """

    # cast number for operations
    number = int(number)

    # create seed tracks based on users top 5 tracks
    top_tracks = get_user_top_items('tracks', time, limit=5)
    if not top_tracks: return
    seed_tracks = [track['id'] for track in top_tracks]

    # list of recommended tracks
    recommended_tracks = []
    # loop tracker
    index = 0
    # track recommendations
    tracks = []

    # until there are sufficient recommendations
    while(len(recommended_tracks)<number):
        # get new recommendations if there are none
        if len(tracks)==0:
            recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=number)
            tracks = recommendations['tracks']

        # loop through the recommendations
        for track in tracks:
            # add it if it has not been recommended before
            if not is_track_in_database(track['id']):
                recommended_tracks.append(track)
            # remove this track from the recommendations ie. it's been sorted
            tracks.remove(track)
            
        # check to see the loop hasn't timed out
        # prevent infinite loop if unique recs can't be found
        index += 1
        if index > (number*10):
            return "cannot find recommendations, try again"

    # add new recommended tracks to the database table
    for track in recommended_tracks:
        try:
            # query database
            sql = "INSERT INTO songs (song_id, track_name, artist) VALUES (%s, %s, %s)"
            datatier.perform_action(dbConn, sql, [track['id'], track['name'], track['artists'][0]['name']])

        except Exception as e:
            print("Error inserting song into database:", str(e))

    print("\nrecommended playlist")
    for track in recommended_tracks:
            print(f"- {track['name']} by {track['artists'][0]['name']}")

#
# helper: is track in database
#
def is_track_in_database(song_id):
    """
    Check if a song is in the database

    Parameters
    ----------
    song_id: id of the track to check

    Returns
    -------
    boolean
    """
    
    try:
        # query database
        sql = "SELECT * FROM songs WHERE song_id = %s"
        row = datatier.retrieve_one_row(dbConn, sql, [song_id])

        # return if songs exists in database
        if row: return True
        else: return False

    except Exception as e:
        print("Error checking song in database:", str(e))
        return False

#
# print all the stored recommendations
#
def print_all_recommendations():
    """
    Print all the recommendations stored in RDS

    Parameters
    ----------
    none

    Returns
    -------
    none
    """

    # sql query
    sql = "SELECT * FROM songs"
    rows = datatier.retrieve_all_rows(dbConn, sql)

    # track song ids for playlist
    track_uris = []

    # check if there are recommendations
    if not rows:
        print("\nno recommendations available")
        return

    # print out the songs
    print("\nall recommended songs")
    for row in rows:
        song_id, track_name, artist = row
        print(f"- {track_name} by {artist}")
        # track song ids
        track_uris.append("spotify:track:"+song_id)

    # create playlist?
    print("\nadd this playlist to your spotify account? (yes/no)")
    answer = input()
    if answer not in ["yes","no"]:
        print("invalid answer")
        return
    
    # create the playlist with all the recommended songs
    if answer == "yes":
        # get the current user
        user = sp.me()['id']
        playlist = sp.user_playlist_create(user=user, name="songspot playlist", public=False)
        sp.playlist_add_items(playlist['id'], track_uris)
        print("playlist successfully created")


# run the flask app on port 8888
if __name__ == '__main__':
    app.run(port=8888)
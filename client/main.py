import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from flask import Flask, request, redirect
from configparser import ConfigParser

# Flask app setup
app = Flask(__name__)

# Spotify credentials
SPOTIPY_CLIENT_ID = '620644335758449996fd913e74fb986a'
SPOTIPY_CLIENT_SECRET = '66679493632746768231d6f91375c8e3'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Spotify authentication manager
scope = 'user-top-read playlist-modify-private'
auth_manager = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                            client_secret=SPOTIPY_CLIENT_SECRET,
                            redirect_uri=SPOTIPY_REDIRECT_URI,
                            scope=scope)

# Spotipy object
sp = None

@app.route('/')
def login():
    return redirect(auth_manager.get_authorize_url())

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = auth_manager.get_access_token(code)
    if token_info:
        global sp
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return main_menu()
    return "login success"

def main_menu():
    while True:
        print("Welcome to SongSpot!")
        print(">> Enter a command:")
        print("   0 => exit")
        print("   1 => top artists")
        print("   2 => analyze genres")

        cmd = input()

        if cmd == '0':
            break
        elif cmd == '1':
            print_user_top_items()
        elif cmd == '2':
            analyze_user_taste()
        else:
            print("Invalid command")

    return "done - exit through command line"

def get_user_top_items(item_type='artists', time_range='long_term', limit=10):
    """Retrieve the top artists or tracks for a user."""
    if item_type == 'artists':
        top_items = sp.current_user_top_artists(time_range=time_range, limit=limit)
    else:
        top_items = sp.current_user_top_tracks(time_range=time_range, limit=limit)
    
    return top_items['items']

def print_user_top_items():
    """Print the user's top artists and tracks."""
    top_artists = get_user_top_items('artists')
    top_tracks = get_user_top_items('tracks')
    
    print("Top Artists:")
    for artist in top_artists:
        print(f"- {artist['name']}")

    print("\nTop Tracks:")
    for track in top_tracks:
        print(f"- {track['name']} by {track['artists'][0]['name']}")

def analyze_user_taste():
    """Analyze the genres and popularity of the user's top artists and tracks."""
    top_artists = get_user_top_items('artists')
    top_tracks = get_user_top_items('tracks')
    
    genres = []
    popularity = []

    for artist in top_artists:
        genres.extend(artist['genres'])
        popularity.append(artist['popularity'])
    
    for track in top_tracks:
        popularity.append(track['popularity'])

    genres = list(set(genres))
    avg_popularity = sum(popularity) / len(popularity) if popularity else 0
    
    print(f"Genres: {', '.join(genres)}")
    print(f"Average Popularity: {avg_popularity}")

if __name__ == '__main__':
    app.run(port=8888)
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from flask import Flask, request, redirect
import psycopg2

# Flask app setup
app = Flask(__name__)

# Spotify credentials
SPOTIPY_CLIENT_ID = '620644335758449996fd913e74fb986a'
SPOTIPY_CLIENT_SECRET = 'e067cbb11c054d17857e9dfef4e4816a'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'  # Example Redirect URI

scope = 'user-top-read playlist-modify-private'

auth_manager = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                            client_secret=SPOTIPY_CLIENT_SECRET,
                            redirect_uri=SPOTIPY_REDIRECT_URI,
                            scope=scope)

sp = spotipy.Spotify(auth_manager=auth_manager)

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
    
    print(f"Top Artists:")
    for artist in top_artists:
        print(f"- {artist['name']}")

    print(f"\nTop Tracks:")
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

@app.route('/')
def login():
    return redirect(auth_manager.get_authorize_url())

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = auth_manager.get_access_token(code)
    if token_info:
        sp.auth_manager.cache_handler.save_token_to_cache(token_info)
        print("Welcome to SongSpot!")
        print("Choose what you want to see:")
        print("1. Top Artists")
        choice = input("Enter your choice (1 or 2): ")
        if choice == '1':
            print_user_top_items()
        else:
            print("Invalid choice!")
    return "login successful - return to command line"

if __name__ == '__main__':
    app.run(port=8888)
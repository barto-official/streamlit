import streamlit as st
import os
import requests
import spotipy
import requests
import spotipy.util as util
from find_similar import find_similar_artists
from streamlit.components.v1 import html
from spotipy.oauth2 import SpotifyOAuth
# Authenticate with Spotify API

# Initialize the Web Playback SDK
from IPython.display import display, Javascript
from urllib.parse import quote


client_id = fe29fbb9fa7f4cf4b88ebf90faaeb562
client_secret = 4a50ecae553e45d8b80f0cb1a3fe92d9

# Set page configuration
st.set_page_config(
    page_title="Spotify Artist Search",
    page_icon=":musical_note:",
    layout="wide"
)

#client_credentials_manager = SpotifyClientCredentials(client_id='fe29fbb9fa7f4cf4b88ebf90faaeb562', client_secret='4a50ecae553e45d8b80f0cb1a3fe92d9')
#sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

redirect_uri = 'https://song-recommender2023.herokuapp.com/'
scope = 'user-read-playback-state,user-modify-playback-state,user-read-private'


sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope)
#token_info = []#sp_oauth.get_cached_token()

st.title('Spotify Recommender System')
st.subheader("How it works: \n")
st.write(""" 
        1. Click Login button below to Log into our Spotify.
        2. You may skip the first step but you won't be able to play music.
        3. The Login page will redirect you.
        4. Copy the URL of the redirected page.
        5. Type the name of your favorite artits.
        6. The system will provide 4 Recommended Artist and top songs for each of them.
        7. Play Music and Enjoy!\n\n
        """)

auth_url = sp_oauth.get_authorize_url()
#st.write("Please log in to Spotify using the following link:")
st.markdown(f"<a href='{auth_url}' target='_blank'>Log in with Spotify</a>", unsafe_allow_html=True)
response_url = st.text_input("Enter the URL you were redirected to:")
code = sp_oauth.parse_response_code(response_url)
token_info = sp_oauth.get_access_token(code)

access_token = token_info['access_token']
sp = spotipy.Spotify(auth=access_token)


def init_spotify_player(access_token):
    display(Javascript("""
        require(['https://sdk.scdn.co/spotify-player.js'], function(spotify) {
            window.Spotify = spotify;
            window.Spotify.Player.create({
                name: 'Streamlit Player',
                getOAuthToken: function(cb) { cb('""" + access_token + """'); }
            }).connect();
        });
    """))

init_spotify_player(access_token)

def play_track(access_token, track_uri):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = f"https://api.spotify.com/v1/tracks/{track_uri.split(':')[-1]}"
    response = requests.get(url, headers=headers)
    track_info = response.json()

    if response.status_code == 200 and 'preview_url' in track_info and track_info['preview_url']:
        preview_url = track_info['preview_url']
        st.write("Successfully started playing the track.")
        st.audio(preview_url)
    else:
        st.write(f"Failed to start playing the track. Status code: {response.status_code}")


# Streamlit app code
st.markdown(
    """
    <style>
    .main-container {
        padding: 3rem;
    }
    .title {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .input-container {
        margin-bottom: 2rem;
    }
    .track-container {
        justify-content: space-between;
    }
    .track {
        width: 30%;
        margin-bottom: 2rem;
        border: 1px solid #ddd;
        border-radius: 50px;
        padding: 1rem;
        text-align: center;
    }
    .track-image {
        width: 100%;
        margin-bottom: 1rem;
    }
    .spotify-button {
        background-color: #1DB954;
        color: #fff;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        text-decoration: none;
    }
    widget_style{
            width: 100%;
            height: 100vh;
            border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<div class="title">Spotify Artist Search</div>', unsafe_allow_html=True)

# Get user input for artist name
st.markdown('<div class="input-container">', unsafe_allow_html=True)
artist_name = st.text_input("Enter artist name:")
num_items=6

artist_found = False
if artist_name:
    url = f"https://artists_api-1-g4538820.deta.app/find_similar_artists?artist={artist_name}&num_items={num_items}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": os.environ["DETA_API"]
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        similar_artists = response.json()
        artist_found = True
    else:
        st.write('No author found! Make sure to write the name correctly.')
        artist_found = False

    st.markdown('</div>', unsafe_allow_html=True)
    if artist_found:
        for artist_name in similar_artists[1:]:
            if artist_name:
                # Search for artist
                results = sp.search(q='artist:' + artist_name, type='artist')
                items = results['artists']['items']

                if len(items) > 0:
                    # Get top tracks of artist
                    artist_id = items[0]['id']
                    top_tracks = sp.artist_top_tracks(artist_id)

                    # Output top tracks
                    with st.container():
                        st.markdown('<div class="track-container">', unsafe_allow_html=True)
                        st.write('Author: ', artist_name)
                        i = 0
                        for track in top_tracks['tracks']:
                            if i <= 5:
                                i += 1
                                track_info = track
                                track_name = track_info['name']
                                track_uri = track_info['uri']
                                track_image_url = track_info['album']['images'][0]['url']
                                preview_url = track_info['preview_url']

                                with st.container():
                                    if preview_url is not None:
                                        # Get the Spotify player widget using the Spotify URI
                                        spotify_widget_uri = f"https://open.spotify.com/embed/track/{track_uri.split(':')[-1]}"

                                        # Create the iframe element with the Spotify player widget
                                        spotify_player_html = f"""
                                            <iframe src="{spotify_widget_uri}" width="100%" height="80%" frameborder="0" allowtransparency="true" allow="encrypted-media" style="min-width: 250px; max-width: 440px;"></iframe>
                                        """

                                        # Display the Spotify player widget in your Streamlit app
                                        html(spotify_player_html)
                                    else:
                                        st.write('No preview available')
                            st.markdown('</div>', unsafe_allow_html=True)

            else:
                st.write("No similar artists found.")

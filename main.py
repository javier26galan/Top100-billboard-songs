import urllib
import requests
from bs4 import BeautifulSoup
import base64
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# credential from the api
CLIENT_ID = 'your client id'
CLIENT_SECRET = 'your secret key'
REDIRECT_URI = "https://example.com/callback"

# coding credentials to base64
client_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
client_credentials_base64 = base64.b64encode(client_credentials.encode()).decode()

# define data for the authentication request
auth_url = "https://accounts.spotify.com/authorize"
auth_params = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": "playlist-modify-private"
}
# build the authorization URL
auth_url = auth_url + "?" + urllib.parse.urlencode(auth_params)
print("Go to: ")
print(auth_url)

# introduce de code
authorization_code = input("Put the code: ")

# exchange the code for a token
TOKEN_URL = 'https://accounts.spotify.com/api/token'
auth_headers = {"Authorization": f"Basic {client_credentials_base64}"}
AUTH_DATA = {
    "grant_type": "authorization_code",
    "code": authorization_code,
    "redirect_uri": REDIRECT_URI
}

# making the authentication
token_response = requests.post(TOKEN_URL, headers=auth_headers, data=AUTH_DATA)
auth_data = token_response.json()

# get token
access_token = auth_data["access_token"]

# scraping
URL = "https://www.billboard.com/charts/hot-100/"
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

response = requests.get(f"{URL}/{date}")
website_html = response.text

soup = BeautifulSoup(website_html, "html.parser")
all_songs = soup.find_all(name="h3", class_="c-title")
songs_title = [song.getText().strip() for song in all_songs]


# find songs
# Authentication with client
auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)


# find the song by name and save the URL
songs_url = []
for song in songs_title:
    song_name = song
    results = sp.search(q=song_name, type='track', limit=1)
    # obtain info
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        # to not put an url tha already exist
        if track_uri not in songs_url:
            songs_url.append(track_uri)

    else:
        print("Song didn't found")


# creating playlist
# define data to creating play list
user_id = "your spotify user id"
playlist_name = f"{date} Top 100 Billboard Songs"

# playlist request data
playlist_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
playlist_headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
playlist_content = {
    "name": playlist_name,
    "public": False
}

# make the request
playlist_response = requests.post(playlist_url, headers=playlist_headers, json=playlist_content)
playlist_data = playlist_response.json()
playlist_id = playlist_data['id']

# create the request to add the songs to the playlist
add_tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
add_tracks_headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# slice the list if it's length is superior to 100, cant add more tha 100 songs in a row
if len(songs_url) > 100:
    songs_url = songs_url[:100]

add_tracks_songs = {
    "uris": songs_url
}

# make the request
add_tracks_response = requests.post(add_tracks_url, headers=add_tracks_headers, json=add_tracks_songs)

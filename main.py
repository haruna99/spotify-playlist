import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

BILLBOARD_URL = "https://www.billboard.com/charts/hot-100"

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
year = date.split('-')[0]

response = requests.get(f"{BILLBOARD_URL}/{date}/")
billboard_web = response.text
soup = BeautifulSoup(billboard_web, "html.parser")

songs = soup.select(selector="li #title-of-a-story")
songs_list = [song.getText().strip() for song in songs]


SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")

SCOPE = "playlist-modify-private"
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope="playlist-modify-private",
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]

song_uri = []

for song in songs_list:
    try:
        result = sp.search(q=f"track: {song} year: {year}", type="track")
        uri = result["tracks"]["items"][0]["uri"]
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")
    else:
        song_uri.append(uri)


playlist = sp.user_playlist_create(
    user=user_id,
    name=f"{date} Billboard Hot 100",
    public=False,
    description=f"This is a playlist of the top 100 on Billboard in {date}",
)

sp.playlist_add_items(playlist_id=playlist["id"], items=song_uri)

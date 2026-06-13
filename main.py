from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from rapidfuzz import fuzz
import os
import json
from dotenv import load_dotenv
import time

# global variables
debug = False
dryRun = False
notfound=[]

def load_environment():
    global debug, dryRun
    """Loads environment variables from the .env file."""
    load_dotenv()
    # Set two custom envs
    if(os.getenv("DEBUG") == "True"): 
        debug = True

    if(os.getenv("DRY_RUN") == "True"): 
        dryRun = True

def get_billboard_top_100(date: str) -> dict[str,str]:
    """Scrapes the Billboard Hot 100 songs for a specific date."""
    url = f"https://elpee.jp/hot100/year_end/{date}" # new url
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    song_names = soup.find(name="div", id="playlist-data") # Grab HTML element that has JSON output
    songlist = song_names.get('data-list') # Take the JSON data from the HTML element we pulled
    jsonlist= json.loads(songlist) # Load json data into proper json variable

    apiQueries = dict()

    for song in jsonlist:
        title = song['title']
        artist = song['artist']
        apiQueries[title] = artist

    return apiQueries # returned as {key1:value1,key2:value2,...}

def authenticate_spotify() -> spotipy.Spotify:
    """Authenticates with Spotify and returns a Spotipy client."""
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-private", client_id=os.getenv("CLIENT_ID"), client_secret=os.getenv("CLIENT_SECRET"), redirect_uri=os.getenv("REDIRECT_URI"), cache_path="./token.txt"))
    return sp

def search_spotify_uris(sp: spotipy.Spotify, song_names: dict[str,str]) -> list:
    """Searches for song URIs on Spotify using fuzzy matching when needed."""
    global notfound
    uris = []

    for song in song_names: # map format is {"title":"artist",...}
        try:
            # Attempt exact search first
            result = sp.search(q=f"track:{song} artist:{song_names[song]}", type="track", limit=1)
            items = result["tracks"]["items"]
            if items:
                uri = items[0]["uri"]
                if(debug): print(f"Song {song} by {song_names[song]} was found at {uri}.")
                uris.append(uri)
                continue

            # If not found, use fuzzy matching on broader search
            fallback_result = sp.search(q=song, type="track", limit=5)
            best_match = None
            highest_score = 0

            for item in fallback_result["tracks"]["items"]:
                title = item["name"]
                score = fuzz.ratio(song.lower(), title.lower())
                if score > highest_score:
                    highest_score = score
                    best_match = item

            if best_match and highest_score >= 80:
                if(debug): print(f"Fuzzy matched: '{song}' → '{best_match['name']}' ({highest_score}%)")
                uris.append(best_match["uri"])
            else:
                if(debug): 
                    print(f"{song} not found, even with fuzzy search.")
                titleartist = f"{song} - {song_names[song]}"
                notfound.append(titleartist)

        except Exception as e:
            print(f"Error with {song}: {e}")

    return uris

def create_spotify_playlist(sp: spotipy.Spotify, user_id: str, date: str, uris: list):
    """Creates a new private Spotify playlist and adds the found songs."""
    playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
    sp.playlist_add_items(playlist_id=playlist["id"], items=uris)

    print(f"Playlist '{playlist['name']}' created successfully!\nLive at: {playlist['external_urls']['spotify']}")

def metrics(song_names: dict[str,str], uris: list, timeelapsed: float):
    expectedsongs = len(song_names)
    foundsongs = len(uris)

    print("------------------------------")
    print("Songs Not Found:")
    for song in notfound:
        print(f"- {song}")
    print("------------------------------")
    print("Metrics for script:")
    print(f"Expected Songs: {expectedsongs}\nFound Songs: {foundsongs}\nTime elapsed: {timeelapsed} seconds")
    print("------------------------------")

def main():
    start_time = time.perf_counter()
    load_environment()
    date = input("Which year do you want to travel to? Type the date in this format YYYY: ")
    songs = get_billboard_top_100(date)
    sp = authenticate_spotify()
    user_id = sp.current_user()["id"]
    uris = search_spotify_uris(sp, songs)
    if(dryRun): 
        print("Dry run set to `True`, would've created a playlist of these songs/uris:")
        print(songs)
        print(uris)
    else:
        create_spotify_playlist(sp, user_id, date, uris)
    end_time= time.perf_counter()
    metrics(songs,uris,end_time-start_time)

if __name__ == "__main__":
    main()
from ast import parse
from ctypes import sizeof

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
popularity={}
listresponse={}
PERPAGE=100

def load_environment():
    global debug, dryRun
    """Loads environment variables from the .env file."""
    load_dotenv()
    # Set two custom envs
    if(os.getenv("DEBUG") == "True"): 
        debug = True

    if(os.getenv("DRY_RUN") == "True"): 
        dryRun = True

# Per page defaults to 100
# Search url defaults to `https://api.discogs.com/database/search`
# Genres defaults to hip hop, electronic, pop and rock
# Returns json response of results in pages
def callCogs(year,page,per_page=PERPAGE,search_url="https://api.discogs.com/database/search", genres=["Hip-Hop","Pop"]):
    CONSUMER_KEY=os.getenv("CONSUMER_KEY")
    CONSUMER_SECRET=os.getenv("CONSUMER_SECRET")
    params = {"format":"single","year": year, "per_page": per_page, "page": page, "genre" : genres, "country":"US"} 
    headers = {"User-Agent": "DiscogsToSpotify/0.1 +https://github.com/ikoded/BillboardToSpotifyPlaylist","Authorization" : f"Discogs key={CONSUMER_KEY}, secret{CONSUMER_SECRET}"}
    
    response = requests.get(search_url, headers=headers, params=params)
    jsonresponse = json.loads(response.text)
    return jsonresponse

def parseResults(jsonresults):
    for results in jsonresults["results"]:
        title = results["title"]
        splitlist = title.split("-")
        artist = splitlist[0]
        songname=""

        for item in range(len(splitlist)):
            if(item>0):
                addTarget = splitlist[item] + " "
                songname += addTarget.strip()
        
        listresponse[songname] = artist
        popularity[songname] = results["community"]["have"]

    if(dryRun): print(listresponse)

def getCommunityHaveTop(playlist_size=100):
    max=0
    sortedmap=dict(sorted(popularity.items(), key=lambda item: item[1],reverse=True)) # sort popularity
    cutdownmap=dict(list(sortedmap.items())[:playlist_size])

    print(cutdownmap)
    return cutdownmap

def produceFinalSortedResult(sortedresult):
    finallist={}
    for item in listresponse:
        if item in sortedresult:
            finallist[item] = listresponse[item]

    return finallist

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
    pagenumberPrint=False

    year = input("Which year do you want to travel to? Type the date in this format YYYY: ")
    i = 1
    # PERPAGE global is 100 for now
    url="https://api.discogs.com/database/search"
    while(i!=(PERPAGE+1)):
        discogsresponse = callCogs(year,i,PERPAGE,url,["Hip-Hop","Pop"])
        parseResults(discogsresponse)
        if 'pages' in discogsresponse["pagination"] and not pagenumberPrint:
            print("# of pages to go through: ")
            print(discogsresponse["pagination"]["pages"])
            pagenumberPrint = True

        if 'next' in discogsresponse["pagination"]["urls"]:
            url=discogsresponse["pagination"]["urls"]["next"]
        else:
            print("Exiting Discogs")
            break # end of urls
        i += 1
        time.sleep(1.2) ## rate limit avoidance, 60 per minute so this is 60/1.2=50 requests per minute

    sortedResults=produceFinalSortedResult(getCommunityHaveTop(100)) # 100 playlist size max
    
    sp = authenticate_spotify()
    user_id = sp.current_user()["id"]
    uris = search_spotify_uris(sp,sortedResults)
    if(dryRun): 
        print("Dry run set to `True`, would've created a playlist of these songs/uris:")
        print(sortedResults)
        print(uris)
    else:
        create_spotify_playlist(sp, user_id, year, uris)
    end_time= time.perf_counter()
    metrics(sortedResults,uris,end_time-start_time)

if __name__ == "__main__":
    main()
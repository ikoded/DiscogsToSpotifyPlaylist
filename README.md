# Discogs to Spotify Playlist

Α Python automation project that scrapes Discogs for tracks to make into a Spotify playlist.

> [!IMPORTANT]
>
> This is a fork of the [scraper-api-to-billboard-spotify](https://github.com/Tsaousidis/scraper-api-billboard-to-spotify) repo. That repo has not been updated for a while and Billboard's main website now requires pro membership to read certain charts. I also now use Discogs for grabbing tracks.

## Requirements

Will most likely need to run `python -m pip install -r requirements.txt` to get required packages to run locally. To run locally simply type `python3 ./main.py` after ensuring you have your `CLIENT_ID`, `CLIENT_SECRET`, and `REDIRECT_URI` in env and referring to env section below for all options.

You can use an .env (see EXAMPLE.env at root that you take EXAMPLE off to get working) for all env or set the system level env's like on Windows. Here are the env's you can set in file new line separated:
- DEBUG : Debug statments print
- DRY_RUN : Make the Spotify playlist or not (defaults True)
- CLIENT_ID : Spotify key
- CLIENT_SECRET : Spotify secret
- REDIRECT_URI : Spotify callback URI
- CONSUMER_KEY : Discog application key
- CONSUMER_SECRET : Discog application secret
- CALLBACK_URI : Discog callback URI

## Refactor Author
- [@Koder](https://github.com/ikoded)

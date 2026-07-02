# Billboard 100 to Spotify Playlist

> [!IMPORTANT]
>
> Well that was short lived, seems like the owner of elpee blocked me. While this will still work, be careful not to overuse it 😜
> Stupid me didn't realize they use a api to grab this data, so going to refactor this repo to use that API.

Α Python automation project that scrapes the Billboard Hot 100 chart for a user-specified year and creates a private Spotify playlist with the top 100 songs of that year end (overlap does indeed occur sometimes between years, that is normal). Plans of implementing different playlists you can scrape from this website, please view [Future Development](#future-development).

> [!IMPORTANT]
>
> This is a fork of the [scraper-api-to-billboard-spotify](https://github.com/Tsaousidis/scraper-api-billboard-to-spotify) repo. That  repo has not been updated and the Billboard's main website now requires pro membership to read certain charts.
> I am now using a new website hosted on a Japanese domain [here](https://elpee.jp/hot100/) that is able to be scraped just the same.

## Requirements

Will most likely need to run `python -m pip install -r requirements.txt` to get required packages to run locally. To run locally simply type `python3 ./main.py` after ensuring you have your `CLIENT_ID`, `CLIENT_SECRET`, and `REDIRECT_URI` in env and referring to env section below for all options.

You can use an .env (see EXAMPLE.env at root that you take EXAMPLE off to get working) for all env or set the system level env's like on Windows. Here are the env's you can set in file new line separated with defaults (if applicable):
- DEBUG : False (set output of finding songs or not, noisy)
- DRY_RUN : False (set dry run to not create playlist)
- CLIENT_ID
- CLIENT_SECRET
- REDIRECT_URI

## Future Development

~~Deciding on adding multithreaded implementation to improve performance (sorry I am a C++ loser).  Another good idea is using the new website and pullng other data it has to create other playlists. Could have options on what you want like top 200, global, etc.~~

Current plans have been halted as the owner of the website I use has blocked my IP and while I could circumvent it, I do not care to. So this will work still just be careful not to use it a ton in short succession like I did while development.

## Original Author
- [@Tsaousidis Konstantinos](https://github.com/Tsaousidis)

## Refactor Author
- [@Koder](https://github.com/ikoded)

import os, sys, json, time, datetime
import spotipy, configparser
from spotipy import SpotifyOAuth
from spotipy import SpotifyException
import pandas as pd



# Directory Grabber
if getattr(sys, 'frozen', False):
    # since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    # gets the base directory of the program, where the python .exe resides
    """Directory should be DSI/Data/URImap.exe"""
else:
    # if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    # gets the base directory of the program, where the python .exe resides



# Directory Definitions
uriDir = os.path.join(directory, "URImap.json")
"""the directory where URImap.json should/will live (inside DSI/Data/URImap.json)"""
noURIdir = os.path.join(directory, "URIlist.json")
"""The directory where URIlist.json should/will live (inside DSI/Data/URIlist.json)"""
spCache = os.path.join(directory, "spotifycache.json")
"""the directory where the spotify cache (token) sits in"""


# Config
Config = configparser.ConfigParser(comment_prefixes = ["/", "#"], allow_no_value = True)
# sets up the config reader
ConfigPath = os.path.join(directory, "..", "config.ini")
# calls the pathFinder to give the location of "config.ini"
Config.read(ConfigPath, "utf8")
# reads from the config, saves values below



# Required
sp_client_ID = Config.get("Required", "Spotify_Client_ID")
"""spotify client ID, string"""
sp_client_secret = Config.get("Required", "Spotify_Client_Secret")
"""spotify client secret, string"""
sp_redirect = Config.get("Required", "Spotify_Redirect_URI")
"""spotify redirect URL, string"""
MarketArea = Config.get("Function", "market_Area")
"""The 2-letter country identifier passed to spotify"""
batchSize = Config.get("Function", "batchsize")


# Auth
authorisation = SpotifyOAuth(
    scope = "user-library-read",
    client_id = sp_client_ID, 
    client_secret = sp_client_secret, 
    redirect_uri = sp_redirect,
    cache_path = spCache
    )
# the argument for auth_manager, containing the variables from config + scope of data request

main = spotipy.Spotify(auth_manager = authorisation)
# handles the authentication and user identification on start



# URI directory checkers

if os.path.exists(uriDir):
    # checks if the uri mapping file (URImap.json) exists
    with open(uriDir, "r", encoding="utf-8") as urimap:
        # loads the uri mapping file
        uriMap = json.load(urimap)
        # stores the loaded file as uriMap
else:
    # if the file doesn't exist, creates a new (empty) mapping
    uriMap = {}

with open(noURIdir, "r") as uris:
    # opens the uriList.json file
    uriList = json.load(uris)
    # stores the list in a variable

def Time():
    """Function that returns the current time, formatted"""
    return datetime.datetime.now().strftime("%H:%M:%S")
    # shortens the variable used to call the current timestamp

if not MarketArea:
    # if the config option is empty
    print(f"{Time()} [ERROR]: No market area. Please input it in the config.ini file and try again")


### URI JSON Mapper ###

#endNum = (batchSize * batchNum)
endNum = (batchSize * 1)
# end is the batch

for num, uri in enumerate(uriList[0:endNum]):
    # gets the URI (track ID) for every unique entry in the CSV

    if num == 0:
        # prints on the very first one of the batch
        print(f"{Time()} [INFO]: URI mapping started")

    if num % 50 == 0:
        # prints every 50 tracks
        print(f"{Time()} [INFO]: Mapped {num} out of {endNum}")

    if uri not in uriMap:
        # for every track URI not found in the pre-existing URI mapped JSON file

        try:
            # tries to find it via Spotify
            trackInfo = main.track(uri, MarketArea)
            # requests the track data from Spotify with the ID and market ID
            altURI = f"spotify:track:{trackInfo["id"]}"
            # it stores the "alternate URI" (the ID spotify returns for your market) as a string
            uriMap[uri] = altURI
            # and then stores that inside the URI map file

        except SpotifyException as error:
            # if it fails, saves the error

            if error.http_status == 429:
                # if the error is exactly 429 (rate limit)

                print(f"{Time()} [INFO]: Rate limit exceeded, waiting for cooldown")
                # prints the rate limit info
                retryTimer = int(error.headers["Retry-After"])
                # takes the given retry after timer and saves it

                print(f"{Time()} [INFO]: Cooldown is {retryTimer}")
                # prints the cooldown info

                time.sleep(retryTimer + 5)
                # sleeps for the duration of the cooldown (+5 seconds to ensure the time has passed)

                try:
                    # tries to find it via Spotify (again)
                    trackInfo = main.track(uri, MarketArea)
                    # requests the track data from Spotify with the ID and market ID
                    altURI = f"spotify:track:{trackInfo["id"]}"
                    # it stores the "canonical URI" (the ID spotify returns for your market) as a string
                    uriMap[uri] = altURI
                    # and then stores that inside the URI map file

                except:
                    # if trying again fails
                    print(f"{Time()} [ERROR]: Encountered an error after rate limit. Exiting in 5 seconds\n")
                    time.sleep(5)
                    raise SystemExit
            else:
                print(f"{Time()} [ERROR]: Failure fetching {uri}:\n{error}")
                uriMap[uri] = uri
                # uses the original URI for the current URI

        time.sleep(0.2)
        # waits for half a second per track, to keep the limit low

print(f"{Time()} [INFO]: Batch processing done")


### URI Map Storing ###


with open(uriDir, "w", encoding="utf-8") as newUri:
    # opens the JSON file in write mode
    json.dump(uriMap, newUri, ensure_ascii=False, indent=2)
    # pushes the data from newUri to the JSON file

time.sleep(5)
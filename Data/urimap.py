import os, sys, json, time, datetime
import spotipy, configparser
from spotipy import SpotifyOAuth
from spotipy import SpotifyException
import pandas as pd

URIver = "v0.18.2.0235"

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


# Timestamp
def Time():
    """Function that returns the current time, formatted"""
    return datetime.datetime.now().strftime("%H:%M:%S")
    # shortens the time call into a function with 00:00:00 format


# URI Prerequisites

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

uriLength = (len(uriList) - 1)
# stores the total length of the URI list

currentLength = len(uriMap)
# stores the total length of the URI mapping

if (uriLength - currentLength) < 1:
    # if the URImap is longer than or equal to the uriList
    print(f"{Time()} [EXIT]: The URI mapping already equals the URI list, nothing to map. Exiting in 10 seconds")
    time.sleep(10)
    raise SystemExit

if not MarketArea:
    # if the config option is empty
    print(f"{Time()} [ERROR]: No market area. Please input it in the config.ini file and try again. Exiting in 10 seconds")
    # user inform, wait -> exit
    time.sleep(10)
    raise SystemExit


print(f"{Time()} [START]: Starting URImapper {URIver}")


# Mapper Variables

length = (uriLength - currentLength)
# calculates the length the batch worker has to do

maxLength = 51
# sets a max worker size of 51

if length > maxLength:
    # if the URI list queue exceeds maximum allowed size
    print(f"{Time()} [INFO]: Currently allowed batch size is {maxLength}, but there are more unprocessed URIs. Only processing max batch size")
    # informs user
    taskLength = maxLength
    # sets the task length to the maximum allowed batch size
else:
    # if the URI list queue is shorter than max allowed batch size
    taskLength = length
    # sets the queue length as the max

endNum = (currentLength + taskLength)
# calculates an end point based on the length of the URImap and the task left to do

print(f"{Time()} [INFO]: {uriLength} URIs stored, {currentLength} already mapped")
# user inform, short stop
time.sleep(2)



### URI JSON Mapper ###


for num, uri in enumerate(uriList[0:endNum]):
    # gets the URI (track ID) for every unique entry in the CSV

    if num == 0:
        # prints on the very first one of the batch
        print(f"{Time()} [INFO]: URI mapping started")

    if num % 25 == 0:
        # prints every 25 tracks
        print(f"{Time()} [INFO]: Mapping process: {num} out of {endNum}")

    if num == (endNum-1):
        # prints on the last one of the batch
        print(f"{Time()} [INFO]: Mapping complete")

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

                print(f"{Time()} [WARN]: Rate limit exceeded, waiting for cooldown")
                # prints the rate limit info
                retryTimer = int(error.headers["Retry-After"])
                # takes the given "retry after" timer and saves it
                returnTime = datetime.datetime.fromtimestamp(int(retryTimer + time.time() + 3)).strftime("%H:%M:%S")
                # gets the return time (time the cooldown expires)
                print(f"{Time()} [WARN]: Spotify rate limit exceeded, cooldown is {retryTimer} ({returnTime})")
                # prints the cooldown info
                print(f"{Time()} [EXIT]: Exiting app in 10 minutes automatically...")
                time.sleep(600)
                # sleeps for 600 seconds (10 minutes) to ensure user sees prompt
                raise SystemExit

            else:
                print(f"{Time()} [ERROR]: Failure fetching {uri}:\n{error}")
                uriMap[uri] = uri
                # uses the original URI for the current URI

        time.sleep(0.2)
        # waits for 0.2 seconds per track, to keep the limit low





### URI Map Storing ###


with open(uriDir, "w", encoding="utf-8") as newUri:
    # opens the JSON file in write mode
    json.dump(uriMap, newUri, ensure_ascii=False, indent=2)
    # pushes the data from newUri to the JSON file



print(f"{Time()} [INFO]: Batch processing done")
# user update
time.sleep(2)
print(f"{Time()} [EXIT]: Exiting app in one minute (feel free to close)")
# user update
time.sleep(60)
# wait so it doesn't look like crash
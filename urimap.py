import os, sys, json, time
import spotipy, configparser
from spotipy import SpotifyOAuth
from spotipy import SpotifyException
import pandas as pd



# Directory Grabber
if getattr(sys, 'frozen', False):
    # since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    # gets the base directory of the program, where the python .exe resides
else:
    # if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    # gets the base directory of the program, where the python .exe resides



# Directory Definitions
uriDir = os.path.join(directory, "Discord", "URImap.json")
"""the directory where URImap.json should/will live (inside DSI/Discord/URImap.json)"""
SHAAdir = os.path.join(directory, "..", "Data", "CSV", "dsi.csv")
"""the directory where the CSV is (relative to .exe, it's one folder up and then two deep into Spotify Analyser main folder)"""
spCache = os.path.join(directory, "spotifycache.json")
"""the directory where the spotify cache (token) sits in"""


# Config
Config = configparser.ConfigParser(comment_prefixes = ["/", "#"], allow_no_value = True)
# sets up the config reader
ConfigPath = os.path.join(directory, "config.ini")
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



# Auth
authorisation = SpotifyOAuth(
    scope = "user-library-read", # may use a better match? user library seems wrong...
    client_id = sp_client_ID, 
    client_secret = sp_client_secret, 
    redirect_uri = sp_redirect,
    cache_path = spCache
    )
# the argument for auth_manager, containing the variables from config + scope of data request

main = spotipy.Spotify(auth_manager = authorisation)
# handles the authentication and user identification on start



# SHA CSV reader
if os.path.isfile(SHAAdir):
    # if the grouped.csv file exists
    print("[SHAA] Spotify Analyser functionality enabled\n")
    # informs user SHAA is enabled
    csvReader = pd.read_csv(SHAAdir, encoding="utf-8")
    # opens the CSV file and uses utf-8 encoding to ensure compatibility
    csvReader = csvReader.set_index("URL")
    # sets the track URL as the index



# URI directory checker
if os.path.exists(uriDir):
    # checks if the uri mapping file (URImap.json) exists
    with open(uriDir, "r", encoding="utf-8") as urimap:
        # loads the uri mapping file
        uriMap = json.load(urimap)
        # stores the loaded file as uriMap
else:
    # if the file doesn't exist, creates a new (empty) mapping
    uriMap = {}



### URI JSON Mapper ###

tempUriList = ["spotify:track:1n1y2kFPISpF9WGD3JaFo5", "spotify:track:1qtNuAGt8cpdedYhTFpc3U", "spotify:track:6319BpXP42QAaXeELaPLmU"]
# temp list of URIs
# first is RADWIMPS "suzume" (the japanese 3-character one)
# second is 照井順政 "Toji Fushiguro"
# last is bludnymph "watch me" - this has an alt URI of: spotify:track:34pjQ4XCtI9gX83heBGuw6 (<- has more plays (by a factor of like 250))


daily_limit = 3
# 
startNum = 0

endNum = startNum + (daily_limit-1)
# since it's collecting from a list, takes away 1 (lists start at 0 and go to len-1)
# this way it won't double collect data either

# currently disabled to test with a tempList
#for num, uri in enumerate(csvReader.index.unique()[startNum:endNum]):

for num, uri in (tempUriList[startNum:endNum]):

    # gets the URI (track ID) for every unique entry in the CSV

    if num == startNum:
        # prints on the very first one of the batch
        print("Processing started")
    if num % 50 == 0:
        # prints every 50 tracks
        print(f"Processed {num} out of {len(csvReader.index.unique())}")

    if uri not in uriMap:
        # for every one not found in the pre-existing URI mapped JSON file

        try:
            # tries to find it via Spotify
            trackInfo = main.track(uri)
            # requests the track data from Spotify 
            canonicalUri = trackInfo # TEMPORARILY USES ALL OF THE TRACK INFO JUST TO TEST EXACTLY WHAT IT IS I NEED
            # canonicalUri = f"spotify:track:{trackInfo["id"]}"
            # it stores the "canonical URI" (the ID spotify returns) as a string
            uriMap[uri] = canonicalUri
            # and then stores that inside the URI map file

        except SpotifyException as error:
            # if it fails, saves the error

            if error.http_status == 429:
                # if the error is exactly 429 (rate limit)

                print(f"[INFO] Rate limit exceeded, waiting for cooldown")
                # prints the rate limit info
                retryTimer = int(error.headers["Retry-After"])
                # takes the given retry after timer and saves it

                print(f"[INFO] Cooldown is {retryTimer}")
                # prints the cooldown info

                time.sleep(retryTimer + 5)
                # sleeps for the duration of the cooldown (+5 seconds to ensure)
                try:
                    trackInfo = main.track(uri)
                    # re-tries to get the data from Spotify
                except:
                    # if trying fails
                    print("[ERROR] Encountered an error after rate limit. Exiting in 5 seconds\n")
                    time.sleep(5)
                    raise SystemExit
            else:
                print(f"[ERROR] Failure fetching {uri}:\n{error}")
                uriMap[uri] = uri
                # uses the original URI for the current URI

        time.sleep(0.2)
        # waits for half a second per track, to keep the limit low

print("Batch processing done")


### URI Map Storing ###


with open(uriDir, "w", encoding="utf-8") as newUri:
    # opens the JSON file in write mode
    json.dump(uriMap, newUri, ensure_ascii=False, indent=2)
    # pushes the data from newUri to the JSON file
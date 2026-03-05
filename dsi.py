import pandas as pd
# Required for all the CSV parsing and data grabbing
import configparser, random, subprocess
# Required to read config, choose random pictures and to start the C++ file
import os, sys, time, threading, queue, datetime
# Required for system information, background tasking and queueing
import spotipy, requests, json
# Required for basic function of Spotify data requests and storing
from spotipy.oauth2 import SpotifyOAuth
# Required for authorizing with Spotify
from spotipy.exceptions import SpotifyException
# Required to check for token exceptions (errors)



### Setup Section ###


DSIver = "v0.3.05.0826"
# the program version (y.m.dd.hhmm)


if getattr(sys, "frozen", False):
    # since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    # gets the base directory of the program, where the python .exe resides
else:
    # if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    # gets the base directory of the program, where the python .exe resides


Config = configparser.ConfigParser(comment_prefixes = ["/", "#"], allow_no_value = True)
# sets up the config reader
ConfigPath = os.path.join(directory, "config.ini")
# calls the pathFinder to give the location of "config.ini"
Config.read(ConfigPath, "utf8")
# reads from the config, saves values below



spCache = os.path.join(directory, "Data", "spotifycache.json")
"""The directory where the spotify cache (token) sits in"""
idDir = os.path.join(directory, "Discord", "ids.txt")
"""The directory where ids.txt should/will live (inside DSI/Discord/ids.txt)"""
songDataDir = os.path.join(directory, "Discord", "songData.txt")
"""The directory where songData.txt should/will live (inside DSI/Discord/songData.txt)"""
noURIdir = os.path.join(directory, "Data", "URIlist.json")
"""The directory where URIlist (unfound URIs) should/will live"""
uriDir = os.path.join(directory, "Data", "URImap.json")
"""The directory where URImap.json should/will live (inside DSI/Data/URImap.json)"""
picDir = os.path.join(directory, "pictureList.txt")
"""The directory where pictureList.txt lives (inside DSI/pictureList.txt)"""
SHAAdir = os.path.join(directory, "..", "Data", "CSV", "dsi.csv")
"""The directory where the CSV is (relative to .exe, it's one folder up and then two deep into Spotify Analyser main folder)"""
hourDir = os.path.join(directory, "..", "Data", "CSV", "hours.txt")
"""The directory where the hours.txt file is"""
cppExe = "DSIdiscord.exe"
"""The name of the C++ exe file"""
cppPath = os.path.join(directory, "Discord", cppExe)
"""The full path to the C++ exe"""
cppDir = os.path.dirname(cppPath) 
"""The directory the C++ Exe lives in"""



### Config Section ###



# [Required]
sp_client_ID = Config.get("Required", "Spotify_Client_ID")
"""Spotify Client ID, string"""
sp_client_secret = Config.get("Required", "Spotify_Client_Secret")
"""Spotify Client Secret, string"""
sp_redirect = Config.get("Required", "Spotify_Redirect_URI")
"""Spotify redirect URL, string"""
dc_app_ID = Config.get("Required", "Discord_Application_ID")
"""Discord Application ID, string"""


# [Function]
refreshTime = int(Config.get("Function", "time_Between_Refresh"))
"""program update cycle interval time, integer"""

if refreshTime < 5:
    # if the refresh time is set too low, overrides to safe minimum of 5s
    refreshTime = 5

enablePause = Config.getboolean("Function", "enable_Pause_Behavior")
"""The "paused on" text enabler, boolean"""
pauseStateText = Config.get("Function", "pause_Behavior_Text")
"""The string used for paused status, string"""
enableUpdates = Config.getboolean("Function", "print_Updates")
"""Whether to print updates, boolean"""
enableErrors = Config.getboolean("Function", "print_Errors")
"""Whether to print errors, boolean"""
enableMapping = Config.getboolean("Function", "enable_URI_Mapping")
"""Whether to enable the URI mapping functionality, boolean"""
timestampStyle = Config.get("Function", "timestamp_Style").lower()
"""The timestamp format for system prints, string (Clock, Uptime, Off)"""

startTime = int(datetime.datetime.now().timestamp())
"""The program start time in UNIX"""



def Time():
    """Function that returns the current time, formatted"""
    if timestampStyle == "uptime":
        # if the config option is set to uptime
        currentTime = int(datetime.datetime.now().timestamp())
        # takes the current time when Time() is called
        uptime = currentTime - startTime
        # calculates the seconds apart between current and startup time
        uptimeHr, remainderHr = divmod(uptime, 3600)
        # takes the hours and the remainders
        uptimeMin, uptimeSec = divmod(remainderHr, 60)
        # takes the minutes and seconds from the remainders
        uptimeStr = ("{:02}:{:02}:{:02}".format(int(uptimeHr), int(uptimeMin), int(uptimeSec)))
        return (uptimeStr + " ")
        # shortens the call to system uptime, adds empty space

    elif timestampStyle == "clock":
        # if the config option is set to clock
        return (datetime.datetime.now().strftime("%H:%M:%S") + " ")
         # shortens the call to current system timestamp, adds empty space

    else:
        # if the config option is set to something else, reads as off (thus doesn't add anything)
        return ""
        
   

print(f"{Time()}[START]: Starting DSI {DSIver}\n")
# quick user update on status


# [URL]
smallURL = Config.get("URL", "small_URL")
"""The small picture URL, string"""
spotifyURL = Config.get("URL", "spotify_URL")
"""The type of large image URL to use, string of: (Track, Artist, Album, Playlist)"""


# [Song-Style]
songNameSpacerL = Config.get("Song-Style", "song_Spacer_Left")
"""Spacer between 1st and 2nd field, string"""
songNameSpacerR = Config.get("Song-Style", "song_Spacer_Right")
"""Spacer between 2nd and 3rd field, string"""


# [Song-Format]
preText = Config.get("Song-Format", "pre_Text")
"""Optional text before the first field, string"""
postText = Config.get("Song-Format", "post_Text")
"""Optional text after the last field, string"""
enableSong = Config.getboolean("Song-Format", "enable_Song")
"""Song's state, boolean"""
enableArtist = Config.getboolean("Song-Format", "enable_Artist")
"""Artist's state, boolean"""
enableAlbum = Config.getboolean("Song-Format", "enable_Album")
"""Album's state, boolean"""
albumFallback = Config.get("Song-Format", "album_Fallback_Text")
"""The text to fall back to in case the album gets dropped, string"""


# [Pictures]
picCycleList = Config.get("Pictures", "pictures_To_Cycle")
"""Pictures for large image, list/string/option (File, Spotify)"""

if picCycleList == "File" or picCycleList == "file":
    # checks if the config option is set to "File"
    picCycleList = []
    # empties the variable 
    with open(picDir, "r", encoding="utf-8") as file:
    # opens the pictureList.txt file
        for pics in file:
        # for every picture (line) in the file

            pic = pics.strip()
            # stores one line
            
            if pic.startswith("#") or not pic:
                # if the line starts with # (meaning it's a comment line) or it's empty
                continue
                # skips that line and goes to next one
            
            picCycleList.append(pic)
            # adds the picture to the list

    if enableUpdates:
        # if the update config option is enabled
        print(f"{Time()}[PICT]: Picture list loaded from file\n")

else:
    # if the list is on Spotify (or empty), doesn't modify it
    None


picCycleTime = Config.get("Pictures", "picture_Cycle_Time")
"""Time to wait between picture cycling, int/string (minutes/Song)"""

try:
    # tries to turn the time into minutes (integer and multiplies by 60)
    picCycleTime = (int(picCycleTime) * 60)
except:
    # if it can't, leaves it alone (should be the case when it's set to "Song")
    None

picCycleType = Config.get("Pictures", "picture_Cycle_Behavior").lower()
"""Type of cycling to perform on pictures, string (Random, Sequence, Once, None)"""
smallPic = Config.get("Pictures", "small_Picture_Name").replace('"', '')
"""Name/URL of small picture, string"""
hoverText = Config.get("Pictures", "text_On_Small_Hover")
"""Text to show on small picture hover, string"""


# [SHAA-Song-Function]
songInfoField1 = Config.get("SHAA-Song-Function", "song_Info_First_Field")
"""First state field type, string (Track, Total)"""
songInfoField2 = Config.get("SHAA-Song-Function", "song_Info_Second_Field")
"""Second state field type, string (Track, Total)"""
shaaFallback = Config.get("SHAA-Song-Function", "song_Info_Fallback")
"""Fallback type for both state fields, string (Total, custom)"""
shaaInfoDetails = Config.get("SHAA-Song-Function", "song_Info_Detail_Field")
"""Details field type, string (Hours, Volume, Repeat, Shuffle, custom)"""


# [SHAA-State-Format]
songInfoFormatPlays = Config.get("SHAA-State-Format", "song_Info_Format_First_Field")
"""Text format of the first field, string"""
songInfoSpacer = Config.get("SHAA-State-Format", "song_Info_Spacer")
"""Spacer to place between first and second field, string"""
songInfoFormatMins = Config.get("SHAA-State-Format", "song_Info_Format_Second_Field")
"""Text format of the second field, string"""
songInfoFallback = Config.get("SHAA-State-Format", "song_Info_Fallback_Format")
"""Fallback text for missing song data for both state fields, string"""

songInfoFormatDetails = Config.get("SHAA-Details-Format", "song_Info_Format_Details")
"""Text format of the details field, string"""
songInfoFormatDetailsSpacer = Config.get("SHAA-Details-Format", "song_Info_Format_Details_Spacer")
"""Spacer to place between details field data and string, string"""
songInfoDetailsDoubleSpace = Config.getboolean("SHAA-Details-Format", "song_Info_Double_Space")
"""Whether to add space on either side of the spacer, boolean"""
dsiShoutout = Config.getboolean("SHAA-Details-Format", "dsi_Shoutout")
"""Whether to add a shoutout to DSI at the end of the details section, boolean"""


print(f"{Time()}[CFG]: Configuration loaded\n")
# another quick user update


if not enableUpdates:
    # if console printing is disabled in config
    print(f"{Time()}[CFG]: Console updates disabled in config (print_Updates)\n")
    # prints a quick warning

if not enableErrors:
    # if error printing is disabled in config
    print(f"{Time()}[CFG]: Error printing disabled in config (print_Errors)\n")



### Variable Section ###



# Detail Field Options #
detailOptions = ["hours", "volume", "repeat", "shuffle", "Hours", "Volume", "Repeat", "Shuffle"]
# all possible choices for detail field (hours)

# Picture Queue #
pictureQueue = queue.Queue()
# creates an empty queue for pictures from picCycler to get sent to

# Event Thread #
songEvent = threading.Event()
# creates an empty threading event list for song

picEvent = threading.Event()
# creates an empty threading event list for picturecycler 

spotifyLock = threading.Lock()
# creates a locking method to prevent redundant API calls (or 2 calls at once)

# Auth #
sessionID = requests.Session()
# tells the auth to keep one stable connection, rather than re-connecting every request

authorisation = SpotifyOAuth(
    scope = "user-read-playback-state", 
    client_id = sp_client_ID, 
    client_secret = sp_client_secret, 
    redirect_uri = sp_redirect,
    cache_path = spCache
    )
# the argument for auth_manager, containing the variables from config + scope of data request

main = spotipy.Spotify(auth_manager = authorisation, requests_session = sessionID)
# handles the authentication and user identification on start

# URL List #
spotifyURLlist = ["track", "Track", "album", "Album", "artist", "Artist", "playlist", "Playlist"]
# makes a list of all the possible options for spotify URL types

# Picture Cycling Methods #
pictureBehaviorList = ["random", "sequence", "once", "none"]
# makes a list of all the possible options for picture cycling types

pauseStart = None
# makes a starter variable for when a pause occurred

cppLargeImage = ""
# makes an empty image string, in case it fails to make first load

dsiShoutoutStr = "// Data by DSI"
# a shoutout string to DSI, disabled by default in config

totalHours = 0
# startup variable for total hours

oldCount = 0
# startup variable for song counter

currentInfo = None
# startup song info


### Id Writer ###


def idWriter():
    """Function for writing the ids.txt file"""

    with open(idDir, "w", encoding="utf-8") as txt:
    # opens the ids text file
        content = ("Discord Application ID = " + dc_app_ID + "\n" + "Small Image Filename = " + smallPic)
        # makes a string from the relevant config options
        txt.write(content)
        if enableUpdates:
            print(f"{Time()}[START]: ID file written\n")
        # writes the string to ids.txt at program launch


### Total Hour Grabber ###


def hourGrabber():
    """Function that grabs the total hours from hours.txt file"""
    if os.path.isfile(hourDir):
        # checks if the hours.txt file exists
        with open(hourDir, "r") as hours:
            # if yes, opens the file
            global totalHours
            # grabs total hours variable from global
            totalHours = hours.read()
            # stores the total hours from the file

            try:
                totalHours = float(totalHours)
                # turns the string into a float
                totalHours = (f"{totalHours:,.2f}")
                # turns the float into a formatted string        
                if enableUpdates:
                    print(f"{Time()}[SHAA]: Total hours saved in CSV: {totalHours}")
                    # prints the total hours at start

            except:
                # if the float conversion fails for some reason
                print(f"{Time()}[SHAA]: Error reading the hours.txt file - total hours not set")
                totalHours = 0

        hours.close()
        # closes the file

    else:
        # if the file for SHA doesn't exist
        None
        # there's already a print informing about non-SHAA installation later



### Spotify Data Grabber Function ###



def authPlayback():
    """Function to more "safely" handle Spotify API requests and errors"""
    
    global main
    # takes the global variable and makes it local

    with spotifyLock:
        # uses a threading lock, to prevent multiple requests at once

        tokenRefresh = False
        # a boolean to determine whether to print the token refresh or reconnect text

        for attempt in range(3):
            # tries a max of 3 times to get Spotify data (typically succeeds 1st try, so if it doesn't work in 3, there's a bigger issue)

            try:
                # first tries to send an API request to Spotify
                
                success = main.current_playback()
                # if it works, returns the Spotify playback package (dictionary)

                if attempt != 0 and enableErrors and not tokenRefresh:
                    # if it's not the first attempt, meaning the reconnect attempt print has already been pushed once
                    print(f"{Time()}[INFO]: Reconnect successful!")
                    # prints user update

                elif enableErrors and tokenRefresh:
                    # if the tokenrefresh variable is set to true, that means a connectionerror occurred at least once
                    print(f"{Time()}[INFO]: Token refreshed successfully!")
                    # prints user update

                return success
                # sends back the successfully found dictionary to the calling function (should only be looper)
                

            except (SpotifyException, requests.exceptions.RequestException, ConnectionResetError) as error:
                # if it fails to acquire a Spotify playback package

                if enableErrors:
                    # if error printing is enabled

                    # this section individually checks for 4 separate errors, because they were the most common that I had 
                    # (token refreshing isn't *really* an error but is classed as such internally)
                    # while printing 2-3 lines of error code is "helpful", it doesn't really help when the error is a simple, self-fixing one
                    # this is why these (token expiry, read timeout and 429) are checked for first, so it doesn't print a massive chunk

                    if isinstance(error, requests.exceptions.ConnectionError):
                        # if the error is a connection error (token expired)
                        print(f"{Time()}[INFO]: Refreshing Spotify token")
                        # doesn't sleep because this is a token error and should get fixed nearly instantly
                        # expected to print just about every 3600 seconds (1h)
                        tokenRefresh = True

                    elif isinstance(error, requests.exceptions.ReadTimeout):
                        # if the error is a read timeout (sort of random)
                        print(f"{Time()}[ERROR]: Spotify API timeout, retrying in 5 seconds ({attempt+1}/3)")
                        time.sleep(2)
                        # sleeps for 2 seconds (because there's a function-wide 3-second cooldown added on top)

                    elif isinstance(error, SpotifyException) and error.http_status == 429:
                        # if the error is due to a rate limit (429 error code from Spotify)
                        retryTimer = error.headers.get("Retry-After", 5)
                        # gets the retry cooldown timer (or 5, if none is found)
                        print(f"{Time()}[WARN]: This application is being rate limited by Spotify, retrying in {retryTimer} ({attempt+1}/3)")
                        time.sleep(int(retryTimer)-3)
                        # sleeps for the duration of retryTimer-3 seconds (because there's a function-wide 3-second cooldown added on top)

                    elif isinstance(error, SpotifyException) and error.http_status == 500:
                        # if the error is 500 (internal error fail)
                        print(f"{Time()}[ERROR: Spotify internal error (Code 500). Attempting to reconnect ({attempt+1}/3)]")
                        # should never happen, but very very rarely does
                    else:
                        # if the error is anything else
                        print(f"{Time()}[ERROR]: Spotify errored due to {error}.\n{Time()}[INFO]: Attempting to reconnect ({attempt+1}/3)")

                if attempt == 2:
                    # if it's the last attempt (range(3) = 0,1,2) and it fails
                    print(f"{Time()}[CRITICAL]: All attempts to reconnect failed due to {error}\nPlease manually restart DSI. Exiting...")
                    time.sleep(60)
                    raise SystemExit
                    # prompts user, then exits

                time.sleep(3)
                # waits 3 seconds to give it some time



### SHA(A) Check ### 


if os.path.isfile(SHAAdir):
    # if the grouped.csv file exists
    print(f"{Time()}[SHAA]: Spotify Analyser functionality enabled\n")
    # informs user SHAA is enabled
    csvReader = pd.read_csv(SHAAdir, encoding="utf-8")
    # opens the CSV file and uses utf-8 encoding to ensure compatibility
    csvReader = csvReader.set_index("URI")
    # sets the track URL as the index

    if os.path.exists(noURIdir):
        # checks if the uri file (uriList.json) exists
        with open(noURIdir, "r", encoding="utf-8") as URIs:
            # loads the JSON file of URIs
            uriList = json.load(URIs)
            # stores the loaded file as uriList
            if enableUpdates:
                uriLength = len(uriList)
                print(f"{Time()}[SHAA]: {uriLength} URIs stored")
    else:
        # if file doesn't exist
        uriList = []
        # creates a new, empty list

    if os.path.exists(uriDir):
        # checks if the URI map file (uriMap.json) exists
        with open(uriDir) as maps:
            # loads the URI map file
            uriMap = json.load(maps)
            # stores the loaded file as uriMap
            if enableUpdates:
                uriMLength = len(uriMap)
                print(f"{Time()}[SHAA]: {uriMLength} URIs mapped")
    else:
        # if the file doesn't exist
        uriMap = {}
        # creates a new, empty list


### Background Picture Tasker ###



class Background(threading.Thread):
    """Background thread for picture selection"""
# a class to use background tasking, this way the pictures can cycle outside the main song loop
    def __init__(self, picCycleList, picCycleType, picCycleTime, pictureQueue):
        super().__init__()

        self.picCycleList = picCycleList
        self.picCycleType = picCycleType
        self.picCycleTime = picCycleTime
        self.pictureQueue = pictureQueue
        # takes all the call variables and initialises them in the class

        self.running = True
        # "turns on" the thread

    def run(self):
        """Function that starts picCycler"""
        picEvent.set()
        # runs once at start up, giving the event queue 1 task to start with

    def picCycler(self):
        """The function used to cycle pictures (or set one)"""

        while True:     
        # this function only runs if true, some of the methods below will end it after one cycle

            if self.picCycleList == "Spotify" or self.picCycleList == "spotify":
                # if the cycle type is "Spotify" (in which case the song handles the pictures)
                self.running = False
                False
                # sets both the running status and the "while" to false

                if enableUpdates:
                    print(f"{Time()}[PICT]: Selected picture method is Spotify covers, disabling picture cycler")
                break
                # kills the picture cycler
                
            picEvent.wait()
            # waits for an event in the picture queue (just makes sure there's a task to be done)

            picLength = (len(self.picCycleList) - 1)
            # calculates the length of the picture list (since it's a list, -1)

            if self.picCycleType in pictureBehaviorList and picLength >= 1:
                # checks if the list has more than one picture (can't cycle if not true)

                if self.picCycleType == "random":
                    # if the selected method is "Random"
                    i = random.randint(0, picLength)
                    # picks a random number based on list length (lists start at 0, so -1 to length for position)
                    cppLargeImage = self.picCycleList[i]
                    # chooses the element with the random number
                    if self.pictureQueue.empty():
                        # ensures the queue doesn't already have a picture
                        self.pictureQueue.put(cppLargeImage)
                        # sends the picture to a queue that then reaches song()
                        if enableUpdates:
                            print(f"{Time()}[PICT]: Random picture set")
                            # informs user a new picture is set

                        if picCycleTime == "song" or picCycleTime == "Song":
                            # if the cycle "time" is instead set to "song"
                            picEvent.clear()
                            # empties the queue
                        else:
                            # if the cycle time is a time
                            time.sleep(self.picCycleTime)
                            # sleeps until it's time to change pictures
                            picEvent.clear()
                            # empties the picture event queue
                            self.run()
                            # runs the starter
                    else:
                        time.sleep(10)
                        # if the queue isn't empty, waits 10 seconds then re-runs the picture selection



                if self.picCycleType == "sequence":
                    # if the selected method is "Sequence"
                    for i in range(0, picLength):
                    # repeats this loop for every element in the list (lists start at 0, so -1 to length for position)
                        cppLargeImage = self.picCycleList[i]
                        # selects the picture from the list one by one

                        if self.pictureQueue.empty():
                            # ensures the queue doesn't already have a picture
                            self.pictureQueue.put(cppLargeImage)
                            # sends the picture to a queue that then reaches song()
                            if enableUpdates:
                                print(f"{Time()}[PICT]: Sequential picture set")
                                # informs user a new picture is set
                            if picCycleTime == "song" or picCycleTime == "Song":
                                # if the cycle "time" is instead set to "song"
                                picEvent.clear()
                                # empties the queue
                            else:
                                # if the cycle time is a time
                                time.sleep(self.picCycleTime)
                                # sleeps until it's time to change pictures
                                picEvent.clear()
                                # empties the picture event queue
                                self.run()
                                # runs the starter
                        else:
                            time.sleep(10)
                            # if the queue isn't empty, waits 10 seconds then re-runs the picture selection

                if self.picCycleType == "once":
                    i = random.randint(0, picLength)
                    # picks a random number based on list length
                    cppLargeImage = self.picCycleList[i]
                    # chooses the element with the random number
                    self.pictureQueue.put(cppLargeImage)
                    # sends the picture to a queue that then reaches song()
                    if enableUpdates:
                        print(f"{Time()}[PICT]: Random picture set")
                    self.running = False
                    False
                    # only sets it once, so it stops the background thread

                if self.picCycleType == "none":
                    # if the selected method is None ()
                    cppLargeImage = self.picCycleList[0]
                    # chooses the first picture
                    self.pictureQueue.put(cppLargeImage)
                    # sends the picture to a queue that then reaches song()
                    if enableUpdates:
                        print(f"{Time()}[PICT]: Picture set")
                    self.running = False
                    False
                    # only sets it once, so it stops the background thread

            else:
                # if the method field or picture list is empty
                cppLargeImage = ""
                # sets the picture to nothing (empty shouldn't break Discord)
                self.pictureQueue.put(cppLargeImage)
                # sends the picture to a queue that then reaches song()
                if enableErrors:
                    print(f"{Time()}[PICT]: Invalid picture cycle behavior or no picture set - proceeding without a picture")
                self.running = False
                False
                # doesn't set a picture, doesn't need to - so it stops the background thread



### C++ ###



def runCpp():
    """Function to start the C++ .exe"""
    with subprocess.Popen([cppPath], cwd=cppDir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as cppPrint:
        # opens the C++ exe, passes a directory and takes output from it
        if enableUpdates:
            for lineRaw in cppPrint.stdout:
                line = lineRaw.strip()
                # ensures there's no empty prints
                if line:
                    # every time the C++ file prints something, this program takes it
                    print(f"{Time()}[DISC]: {line.rstrip()}")
                    # prints it after a line ends



### Song Data File Field Selection/Creation ###



def song(pictureQueue):
    """The function that handles all song data gathering and parsing, as well as pushing to C++ via text"""
    global uriList, cppLargeImage, uriMap, totalHours, detailOptions, pauseStart, currentInfo, trackCounter, oldCount
    # pulls some global variables to local

    while True:

        songEvent.wait()
        # waits for looper() to set an event

        songNameList = []
        # creates an empty list for strings to get added into as the loop progresses 

        songStuffList = []
        # creates an empty list for strings to get added into as the loop progresses

        cppLargeHoverList = []
        # creates an empty list for strings to get added into as the loop progresses 

        csFull = currentInfo
        # gets a huge dictionary containing all the information about current song
        # "cs" in the variables just stands for CurrentSong, which, while descriptive, made the later variables insanely long

        if not csFull or not csFull.get("item"):
            # checks if the dictionary is valid and can be called
            time.sleep(5)
            # waits for a few seconds
            continue
            # sends back to the start of song() to restart the song query

        csItem = csFull.get("item")
        # takes the first part of the song's info (leaving out device info and various user states)
        csAlbum = csItem.get("album")
        # takes a smaller part of the song's info (still contains a ton of extra)

        csDevice = csFull.get("device")
        # gets a list of device information

        csName = csItem.get("name")
        # stores the name of the song

        isLocalSong = csItem.get("is_local")
        # checks if the song is a local song (can't use standard API info requests if so)

        if not isLocalSong:
            # these fields are only valid when it's not a local song

            csURI = csItem.get("uri")
            # grabs the URI of the song - which is what determines the song matching

            csImages = csAlbum.get("images")
            # gets the information about the album's images
            csCover = csImages[0].get("url")
            # gets the album cover url (used to pass to Discord if pictureCycle = Spotify)

            csArtists = csAlbum.get("artists")
            # stores all the artists listed on the song
            csArtist = csArtists[0].get("name")
            # stores the first artist's name (in case there's multiple artists, only grabs first)

            csAlbumName = csAlbum.get("name")
            # stores the album name

        csLength = int(csItem.get("duration_ms")/1000)
        # stores the length of the song in seconds
        csProgress = int(csFull.get("progress_ms")/1000)
        # saves the current song progress in seconds

        csUnixStart = int(time.time() - csProgress)
        # stores the start time of the song by taking current time and subtracting progress
        csUnixEnd = (csUnixStart + csLength)
        # stores the end time of the song (by adding up the start + duration)

        csPlayState = bool(csFull.get("is_playing"))
        # grabs the playback state (true/false)

        pauseState = False
        # defaults the pauseState to false

        if not csPlayState:
            # if the song is paused

            if pauseStart is None:
                # if there's no set pause time
                pauseStart = int(time.time())
                # sets the pause time to current time

            pauseState = True
            # sets the pauseState to True

            csUnixStart = 0
            csUnixEnd = 0
            # sets the UNIX timecodes to 0, leading to Discord counting up from paused state

        else:
            # song is playing
            if pauseStart is not None and (trackCounter == oldCount):
                # if there's a set pause time from before (and the song hasn't changed)
                pauseDuration = int(time.time() - pauseStart)
                # calculates the time spent on pause
                csUnixStart += pauseDuration
                csUnixEnd += pauseDuration
                # sets the start and end times to match the time spent paused (by adding the time spent paused)
                pauseStart = None
                # resets the pauseStart to None, so it can get checked again

        if enablePause and not csPlayState:
            # if the pause behavior is enabled and song paused
            songNameList.append(pauseStateText)
            # adds the pause text as the first string in the list (since it goes first)

        if not isLocalSong:
            # can't access these if the playing song is local
            cstrackURL = csItem.get("external_urls")
            # stores the list that contains track's url
            csAlbumLinks = csAlbum.get("external_urls") 
            # stores the list that contains album url
            csArtistLinks = csArtists[0].get("external_urls")
            # stores the list that contains artist's url
            csPlaylist = csFull.get("context")
            # stores the list that contains the playlist url

        if csPlaylist == None:
            # checks if user is playing a playlist
            onPlaylist = False
            # if not, sets onPlaylist to false

        else:
            # if there is a playlist playing
            csPlaylistURL = csPlaylist.get("external_urls")
            # gets the list of external urls attached to that playlist
            onPlaylist = True
            # sets onPlaylist to true

        if spotifyURL in spotifyURLlist:
            # if the selected type of URL is in the valid set

            if spotifyURL == "track" or spotifyURL == "Track":
                # if the config option for url type is set to track
                csURL = cstrackURL.get("spotify")
                # takes the track's URL

            elif spotifyURL == "album" or spotifyURL == "Album":
                # if the config option for url type is set to album
                csURL = csAlbumLinks.get("spotify")
                # takes the album's URL

            elif spotifyURL == "artist" or spotifyURL == "Artist":
                # if the config option for url type is set to artist
                csURL = csArtistLinks.get("spotify")
                # takes the artist's URL

            elif spotifyURL == "playlist" or spotifyURL == "Playlist":
                # if the config option for url type is set to playlist
                if onPlaylist:
                    # takes the playlist's URL
                    csURL = csPlaylistURL.get("spotify")
                else:
                    # the user isn't playing a playlist, but has selected the playlist url config option
                    csURL = smallURL
                    # sets it to smallURL as a fallback                    
                    
        else:
            # if the config option for url type is invalid, defaults to my website :)
            csURL = "https://elleffnotelf.com"




        ### Field Selection and String Merging ###



        ### SHAAless Behavior ###


        if not os.path.isfile(SHAAdir):
            # if not installed as an addon to Spotify Analyser, will not send numbers forward - rather just configured, set fields

            ### Field 1 / Field 2 ###

            songStuffList.append(songInfoField1)
            # adds the user-defined first field to list
            songStuffList.append(songInfoSpacer)
            # adds the spacer to list
            songStuffList.append(songInfoField2)
            # adds the user-defined second field to list
                
            ### Details / Field 3 ###

            if songInfoFormatDetails:
                # if the format option isn't empty
                cppLargeHoverList.append(songInfoFormatDetails)
                # adds to string list

            if songInfoDetailsDoubleSpace:
                # if the double space is enabled
                cppLargeHoverList.append(" ")
                # adds an empty space

            if songInfoFormatDetailsSpacer:
                # if the format spacer option isn't empty
                cppLargeHoverList.append(songInfoFormatDetailsSpacer + " ")
                # adds to string list
            
            if shaaInfoDetails in detailOptions:
                # if the config option matches one of the set defaults

                if shaaInfoDetails == "Volume" or shaaInfoDetails == "volume":
                    # if the config calls for volume
                    try:
                        shaaDetailField = f"{csDevice.get("volume_percent")}%"
                        # takes the volume and makes it a percentage
                    except:
                        shaaDetailField = "some volume"
                        # if it fails, puts a fallback string
                    
                if shaaInfoDetails == "Repeat" or shaaInfoDetails == "repeat":
                    # if the config calls for repeat state
                    try:
                        repeatState = csFull.get("repeat_state")
                        if repeatState:
                            # if repeat state returns True
                            shaaDetailField = "on Repeat"
                                # adds string form
                        else:
                            # if repeat state doesn't return True
                            shaaDetailField = "not on Repeat"
                            # adds string form
                    except:
                        shaaDetailField = "may be on Repeat"
                         # if it fails, puts a fallback string

                if shaaInfoDetails == "Shuffle" or shaaInfoDetails == "shuffle":
                    # if the config calls for shuffle state
                    try:
                        shuffleState = csFull.get("shuffle_state")
                        if shuffleState:
                            # if shuffle state returns True
                            shaaDetailField = "on Shuffle"
                        else:
                            # if shuffle state doesn't return True
                            shaaDetailField = "not on Shuffle"
                    except:
                        shaaDetailField = "may be on Shuffle"
                        # if it fails, puts a fallback string

            else:
                # if the config option doesn't match any of the set defaults
                shaaDetailField = shaaInfoDetails
                # sets the total time to match custom string instead

            cppLargeHoverList.append(shaaDetailField + " ")
            # joins together the list 

            if dsiShoutout:
                cppLargeHoverList.append(dsiShoutoutStr)

        cppLargeHover = "".join(cppLargeHoverList)
        # joins together the details list to one string


        ### SHAA Behavior ###


        if os.path.isfile(SHAAdir):
            # this is the addon part to Spotify (History) Analyser (SHA + addon = SHAA)
            # this data is only entered to rich presence if used with SHA (and installed correctly)
            # checks if the CSV file exists to pull data from (requires one full run of SHA prior)
            
            ### URI Checkpoint ###

            finalURI = csURI
            # creates a new variable with the current song's URI

            if enableMapping:
                # if URI mapping is enabled
                
                altURI = uriMap.get(csURI)
                # creates an alteranate variable from the JSON map by checking with the current URI

                if finalURI in csvReader.index:
                    # checks if the URI is on the CSV (this check is just to prevent double prints)
                    if enableUpdates:
                        print(f"{Time()}[SHAA]: Current song found in CSV")

                if finalURI not in uriList:
                    # if the URI is not in the URI list yet
                    if enableUpdates:
                        print(f"{Time()}[SHAA]: URI not found in list, added to URI list")
                    uriList.append(finalURI)
                    # adds it to the list of URIs

                if finalURI not in csvReader.index and altURI in csvReader.index:
                    # if the URI is not found in the CSV index, but the alt URI is
                    finalURI = altURI
                    # sets the URI to use the alternate instead
                    if enableUpdates:
                        print(f"{Time()}[SHAA]: URI not found in CSV, but mapped URI was")
                   

                    with open(noURIdir, "w", encoding="utf-8") as newUri:
                    # opens the JSON file in write mode
                        json.dump(uriList, newUri, ensure_ascii=False, indent=2)
                        # pushes the data from uriList to the JSON file

                    with open(noURIdir, "r", encoding="utf-8") as URIs:
                        # loads the uri mapping file
                        uriList = json.load(URIs)
                        # stores the loaded file as uriList again, now with the new entry

            if finalURI in csvReader.index:
                # checks if the URI is on the CSV  

                ### Plays / Field 1 ###

                playcount = csvReader.loc[finalURI, "Playcount"]
                playtime = csvReader.loc[finalURI, "Total Time"]
                # sets temp variables that lookup the cells based on the track and columns

                if songInfoField1 == "Track" or songInfoField1 == "track":
                    # if the selected type for first field is Track

                    if isinstance(playcount, pd.Series):
                        # if there's more than one instance of the current song
                        playcountTotal = playcount.sum()
                        # saves the playcount total based on calculated playcounts

                    else:
                        # if there's only one instance of the current song
                        playcountTotal = playcount
                        # saves the total as the playcount of the song

                    shaaPlaycount = f"{playcountTotal:,.0f}"
                    # formats the string properly
                    songStuffList.append(shaaPlaycount)
                    # adds the total playcount to the list

                elif songInfoField1 == "Total" or songInfoField1 == "total":
                    # if the selected type for the first field is Total

                    shaaPlaycount = f"{csvReader["Playcount"].agg("sum"):,.0f}"
                    # adds up *all* the playcounts for all tracks
                    songStuffList.append(shaaPlaycount)

                else: 
                    # if the setting doesn't match either
                    songStuffList.append(songInfoField1)
                    # appends with the user-defined custom text

                ### Field 1 Format ###

                songStuffList.append(songInfoFormatPlays)
                # adds the first field's custom end styling

                ### Spacer ###

                songStuffList.append(songInfoSpacer)
                # adds the spacer to the list

                ### Minutes / Field 2 ###

                if songInfoField2 == "Track" or songInfoField2 == "track":
                    # if the selected type for the second field is Track

                    if isinstance(playtime, pd.Series):
                        # if there's more than one instance of the current song

                        playtimeTotal = (((playtime.sum()) / 1000 ) / 60)
                        # calculates the total playtime
                    
                    else:
                        # if there's only one instance of the current song
                        playtimeTotal = ((playtime / 1000) / 60 )
                        # saves the total as the playtime of the song 

                    shaaPlaytime = f"{playtimeTotal:,.1f}"
                    # formats the string properly
                    songStuffList.append(shaaPlaytime)
                    # adds the total playcount to the list

                elif songInfoField2 == "Total" or songInfoField2 == "total":
                    # if the selected type for the first field is Total

                    shaaPlaytime = f"{((csvReader["Total Time"].agg("sum") / 1000 ) / 60):,.1f}"
                    # adds up *all* the time played (milliseconds/1000 = seconds / 60 = minutes)

                    songStuffList.append(shaaPlaytime)
                    # adds to string list

                else:
                    # if the setting doesn't match either
                    songStuffList.append(songInfoField2)
                    # appends with the user-defined custom text

                ### Field 2 Format ###

                songStuffList.append(songInfoFormatMins)
                # adds the second field's custom end styling
                    
                ### Details / Field 3 / Total Hours ###

                cppLargeHoverList.append(songInfoFormatDetails)
                # adds the field 3 format (start string, default is Total Hours)

                if songInfoDetailsDoubleSpace:
                    # if the double space is enabled
                    cppLargeHoverList.append(" ")
                    # adds a space to the left side of the spacer
                if songInfoFormatDetailsSpacer:
                    # if the spacer isn't empty
                    cppLargeHoverList.append(songInfoFormatDetailsSpacer + " ")
                    # adds the spacer and a space on the right side

                if shaaInfoDetails in detailOptions:
                    # if the config option matches one of the set defaults

                    if shaaInfoDetails == "Hours" or shaaInfoDetails == "hours":
                        # if the config calls for total hours
                        shaaDetailField = totalHours
                        # gets total hours from the hours.txt file 

                    if shaaInfoDetails == "Volume" or shaaInfoDetails == "volume":
                        # if the config calls for volume
                        try:
                            shaaDetailField = f"{csDevice.get("volume_percent")}%"
                            # takes the volume and makes it a percentage
                        except:
                            shaaDetailField = "some volume"
                            # if it fails, puts a fallback string
                    
                    if shaaInfoDetails == "Repeat" or shaaInfoDetails == "repeat":
                        # if the config calls for repeat state
                        try:
                            repeatState = csFull.get("repeat_state")

                            if repeatState:
                                # if repeat state returns True
                                shaaDetailField = "on Repeat"
                                # adds string form
                            else:
                                # if repeat state doesn't return True
                                shaaDetailField = "not on Repeat"
                                # adds string form
                        except:
                            shaaDetailField = "may be on Repeat"
                            # if it fails, puts a fallback string

                    if shaaInfoDetails == "Shuffle" or shaaInfoDetails == "shuffle":
                        # if the config calls for shuffle state
                        try:
                            shuffleState = csFull.get("shuffle_state")

                            if shuffleState:
                                # if shuffle state returns True
                                shaaDetailField = "on Shuffle"
                            else:
                                # if shuffle state doesn't return True
                                shaaDetailField = "not on Shuffle"
                        except:
                            shaaDetailField = "may be on Shuffle"
                            # if it fails, puts a fallback string

                else:
                    # if the config option doesn't match any of the set defaults
                    shaaDetailField = shaaInfoDetails
                    # sets the total time to match custom string instead

                cppLargeHoverList.append(shaaDetailField + " ")
                # joins together the list 

                if dsiShoutout:
                    # if the dsi shoutout option is enabled
                    cppLargeHoverList.append(dsiShoutoutStr)

            ### No Track Match ###

            else:
                # if the track wasn't found in CSV
                if enableUpdates:
                    # if the updates are enabled, lets user know the song wasn't found in CSV
                    print(f"{Time()}[SHAA]: {csName} not found in CSV, using fallback values")
                
                ### Field 1 / Field 2 ###

                if shaaFallback == "Total" or shaaFallback == "total":
                    # if the selected fallback is Total/total
                    shaaPlaycount = f"{csvReader["Playcount"].agg("sum"):,.0f}"
                    # uses the total playcount for all songs
                    shaaPlaytime = f"{((csvReader["Total Time"].agg("sum") / 1000 ) / 60):,.0f}"
                    # uses the total amount of playtime for all songs
                else:
                    # if the selected fallback isn't total
                        shaaPlaycount = shaaFallback
                        shaaPlaytime = shaaFallback
                        # takes the custom string and replaces playcount/time variables with that

                # string constructor
                songStuffList.append(shaaPlaycount)
                # adds to list
                if songInfoFallback:
                    # if the fallback isn't empty
                    songStuffList.append(songInfoFallback)
                    # adds the custom field to string
                songStuffList.append(songInfoFormatPlays)
                # adds the first field end text to list
                songStuffList.append(songInfoSpacer)
                # adds the spacer
                songStuffList.append(shaaPlaytime)
                # adds to list
                if songInfoFallback:
                    # if the fallback isn't empty
                    songStuffList.append(songInfoFallback)
                    # adds the custom field to string
                songStuffList.append(songInfoFormatMins)
                # adds the second field end text to list
                
                ### Details / Field 3 ###

                if songInfoFormatDetails:
                    # if the format option isn't empty
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # adds to string list

                if songInfoDetailsDoubleSpace:
                    # if the double space is enabled
                    cppLargeHoverList.append(" ")
                    # adds an empty space

                if songInfoFormatDetailsSpacer:
                    # if the format spacer option isn't empty
                    cppLargeHoverList.append(songInfoFormatDetailsSpacer + " ")
                    # adds to string list

                if shaaInfoDetails in detailOptions:
                    # if the config option matches one of the set defaults

                    if shaaInfoDetails == "Hours" or shaaInfoDetails == "hours":
                        # if the config calls for total hours
                        shaaDetailField =  f"{( ( (csvReader["Total Time"].agg("sum")/1000) /60) /60):,.2f}"
                        # counts total time (hours) for all songs (milliseconds/1000 = seconds / 60 = minutes / 60 = hours, then rounded), turns into a formatted string

                    if shaaInfoDetails == "Volume" or shaaInfoDetails == "volume":
                        # if the config calls for volume
                        try:
                            shaaDetailField = (csDevice.get("volume_percent")+"%")
                            # takes the volume and makes it a percentage
                        except:
                            shaaDetailField = "some volume"
                            # if it fails, puts a fallback string

                    if shaaInfoDetails == "Repeat" or shaaInfoDetails == "repeat":
                        # if the config calls for repeat state
                        try:
                            repeatState = csFull.get("repeat_state")
                            if repeatState:
                                # if repeat state returns True
                                shaaDetailField = "on Repeat"
                                # adds string form
                            else:
                                # if repeat state doesn't return True
                                shaaDetailField = "not on Repeat"
                                # adds string form
                        except:
                            shaaDetailField = "may be on Repeat"
                            # if it fails, puts a fallback string

                    if shaaInfoDetails == "Shuffle" or shaaInfoDetails == "shuffle":
                        # if the config calls for shuffle state
                        try:
                            shuffleState = csFull.get("shuffle_state")
                            if shuffleState:
                                # if shuffle state returns True
                                shaaDetailField = "on Shuffle"
                            else:
                                # if shuffle state doesn't return True
                                shaaDetailField = "not on Shuffle"
                        except:
                            shaaDetailField = "may be on Shuffle"
                            # if it fails, puts a fallback string

                    else:
                        # if the config option doesn't match any of the set defaults
                        shaaDetailField = shaaInfoDetails
                        # sets the total time to match custom string instead

                cppLargeHoverList.append(shaaDetailField + " ")
                # adds the detail field to the list

                if dsiShoutout:
                    # if the dsi shoutout is enabled
                    cppLargeHoverList.append(dsiShoutoutStr)

            cppLargeHover = "".join(cppLargeHoverList)
            # joins together the detail list of strings (SHAA-only)
            

        ### Song State String Joiner (SHAA and non) ###


        if songStuffList:
            # if there's anything in songStuffList (not empty)
            cppState = " ".join(songStuffList)

        else:
            # if the list *is* empty
            cppState = "An amount of time spent listening"
            # puts a fallback string instead


        ### Song Style ###


        SNSL = True
        # sets a temp flag for the left spacer, just so it can't get double printed

        if preText:
            # if preText has something
            songNameList.append(preText)
            # adds to string

        if enableSong:
            # if song is enabled
            songNameList.append(csName)
            # adds to string
            if songNameSpacerL:
                # if songNameSpacerL(eft) isn't empty
                SNSL = False
                # sets the requirement to add Left Spacer to false, so that it doesn't get added
                if (enableArtist or enableAlbum) or (enableArtist and enableAlbum):
                    # if artist OR album is enabled, OR if both are enabled (aka there's *something* after)
                    songNameList.append(songNameSpacerL)
                    # adds the left spacer, since there's something to the right of it
                else:
                    # if there's nothing after, doesn't add the spacer
                    None

        if enableArtist:
            # if artist is enabled
            songNameList.append(csArtist)
            # adds to string
            if songNameSpacerL and SNSL:
                # if songNameSpacerL(eft) has something and isn't already in
                songNameList.append(songNameSpacerL)
                # adds to string

        if enableAlbum or postText:
            # if there's at least one element after (album is enabled *or* there's a post-text)
            if not enableSong and not enableArtist:
                # if there's no other elements (pre/post texts not counting)
                None
                # does nothing
            else:
                songNameList.append(songNameSpacerR)
                # if there's more than just album, adds the right spacer to string

        if enableAlbum:
            # if album is enabled
            cppAlbumName = csAlbumName
            # sets the final name (not necessary but keeps symmetry)

        if postText:
            # if postText has something
            songNameList.append(postText)
            # adds to string


        ### Song Details Joiner ###


        if songNameList:
            # if there's anything in songNameList (not empty)
            cppSongName = " ".join(songNameList)

        else:
            # if the list *is* empty
            cppSongName = "A song, by an artist, on an album"
            # puts a fallback string instead


        ### Picture Selection ###


        if trackCounter != oldCount and csPlayState:
            # checks if the song has changed (this way it doesn't change the picture when the song gets paused)

            oldCount = trackCounter
            # updates the song counter

            if not pictureQueue.empty():
            # checks pictureQueue to see if it has something
                cppLargeImage = pictureQueue.get()
                # stores the picture from pictureQueue as the picture to send to C++

                if picCycleTime == "song" or picCycleTime == "Song":
                # if the cycle "time" is instead set to "song"

                    picEvent.set()
                    # tells the picture selector to select a new one 
                    # this is because the picture selection happens automatically, except with "song", where it happens on a per-song basis


        ### C++ Text File Writer ###


        if picCycleList == "Spotify" or picCycleList == "spotify":
            # checks if the picture list is set to send pictures from Spotify covers
            cppLargeImage = csCover
            # replaces the image link with the spotify album cover if so

        cppFull = (
                    f"songName = {cppSongName}\n"
                    f"albumName = {cppAlbumName}\n"
                    f"songStuff = {cppState}\n"
                    f"LargeImage = {cppLargeImage}\n"
                    f"LargeText = {cppLargeHover}\n"
                    f"SmallText = {hoverText}\n"
                    f"SpotifyURL = {csURL}\n"
                    f"SmallURL = {smallURL}\n"
                    f"UNIXstart = {str(csUnixStart)}\n"
                    f"UNIXend = {str(csUnixEnd)}\n"
                    f"PauseState = {str(pauseState)}\n"
                    f"AlbumFallback = {albumFallback}" 
                    )
        # merges all the song information together, split by newlines

        with open(songDataDir, "w", encoding="utf-8") as txt:
            # opens the songData text file
            txt.write(cppFull)
            # writes the full song information to the text file, which is read by the C++ program and then sent to Discord RPC
            if enableUpdates:
                print(f"{Time()}[INFO]: Song data file updated")
                # if updates are enabled, prints an update

        songEvent.clear()
        # clears the event queue, ready to get new requests



### Information Checking Loop ###



currentURI = None
# makes the currentSong empty outside the looper so the loop can start and not make it "None" every time its run

pauseUpdated = False
# makes the pause update boolean false so it can start normally

trackCounter = 0
# a counter to track the current song's "ID"

def looper():
    """Function that checks song info on a loop"""
    global currentURI, currentInfo, pauseUpdated, trackCounter
    # grabs the "global" variable (outside the function) as a local variables
    while True:
        # this loop checks if the song playing is the same as the previous update, waits if yes, updates the song to match if not

        info = authPlayback()
        # picks up all the info Spotify sends in an update

        if not info or not info.get("item"):
            # checks if the info has something and if it can be called
            if enableErrors:
                print(f"{Time()}[WARN]: No playing state detected, re-checking in 5 seconds\n")
            time.sleep(5)
            # waits for a few seconds
            continue
        
        currentInfo = info
        # sets the global variable to match

        songURI = (info.get("item")).get("uri")
        # grabs the URI of the song, stores it
        songName = (info.get("item").get("name"))
        # stores name for display purposes
        songProg = ((info.get("progress_ms")) / 1000)
        # grabs the progress of the song at the pull time (ms/1000 = seconds)
        playing = info.get("is_playing")
        # checks the pause state (True if playing, False if not)

        if currentURI is None:
            # when the program first starts, the currentURI will be "None", this updates it
            currentURI = songURI
            # sets the current song to match 
            currentProg = songProg
            # updates the current progress
            trackCounter += 1
            # adds 1 to counter
            picEvent.set()
            # since this only runs when the program first starts, sets an event immediately to picCycler, to grab a new picture
            songEvent.set()
            # since this only runs when the program first starts, sets an event immediately to song, to refresh data
            if enableUpdates:
                print(f"{Time()}[SONG]: First song: {songName}, has been successfully processed\n")
                # if user wants feedback, sends this

        songDur = ((info.get("item")).get("duration_ms")/1000)
        # grabs both the current time and length of the song (in seconds)
        songLeft = (songDur-songProg)
        # calculates the time left on the song

        if (currentURI != songURI) or (songProg < currentProg) or (pauseUpdated and playing):
        # if there's a song change (if the URI or there's somehow less time left than previously) or if the pause has been triggered

            if enableUpdates and not pauseUpdated:
                # if console updates are enabled and this change wasn't triggered by a pause
                print(f"\n{Time()}[SONG]: New song detected: {songName}, duration: {songDur:,.0f} seconds")
                # user update on new song (makes a new line before itself so it separates tracks)
            elif enableUpdates and pauseUpdated:
                # if console updates are enabled and this change *was* triggered by a pause
                print(f"\n{Time()}[SONG]: Unpaused: {songName}")

            currentURI = songURI
            # changes the internal variable to match new song
            currentProg = songProg
            # changes timestamp variable to match
            songEvent.set()
            # sets an event to make song() update the text file

            if pauseUpdated:
                # if it's playing and the pauseUpdate has been set to true
                pauseUpdated = False
                # sets the pauseUpdated to false, so it doesn't run twice
            else:
                # if it's playing but pauseUpdate is false
                trackCounter += 1
                # adds 1 to counter (means track has changed)

            time.sleep(5)
            # waits 5 seconds
            continue
            # sends back to the start of looper to check for a new song (5 second checks after a song change to check for a song skip)

        if not playing and not pauseUpdated:
        # if the song is paused and hasn't yet updated the pause state
            if enablePause:
                # if the pause hasn't been registered yet and the pause behavior is enabled
                songEvent.set()
                # sets an event to make song() update the text file (this way it doesn't spam)
                pauseUpdated = True
                # sets the pause check to True, meaning it has been checked and acted on
                if enableUpdates:
                    # if user updates are on
                    print(f"\n{Time()}[SONG]: Paused on: {songName}")
                    # user inform (new line to split from main updates, only prints once anyway)
            sleepfor = max(refreshTime, 5)
            # sets the sleep timer to the higher of the two (never lets it go <5s)

        else:
        # if the current song is the same, and is not paused
            if songLeft >= refreshTime:
                # checks if there's more song left than the refresh time is set to
                sleepfor = min(songLeft, refreshTime)
                # sleeps for the smaller amount of time between (time left in song) and (config set refresh time)
                sleepfor = max(sleepfor, 5)
                # makes sure the sleep doesn't go under 5 seconds (prevents crazy API pull rates and usage spikes)
            else:
                # if there's less song time left than refresh time (if refreshTime = 15, song will have to be <15)
                sleepfor = max(songLeft, 5)
                # sleeps for the minimum of 5 seconds
                if enableUpdates:
                    print(f"{Time()}[SONG]: New song in {sleepfor:,.0f} seconds")
                    # user inform on new song coming soon

        time.sleep(sleepfor)
        # sleeps for the determined time


### Load Commands ###


idWriter()
# runs the idWriter, which writes the ids.txt file

hourGrabber()
# runs the hourGrabber, which gets total hours from the hours.txt file

bg = Background(picCycleList, picCycleType, picCycleTime, pictureQueue)
# defines the background thread as the class containing all the picture function
# passes the list, type, time and queue

bg.start()
# runs the "background" class, which handles the picture updates

picThread = threading.Thread(target = bg.picCycler)
# creates a thread for the picture changer
picThread.start()
# starts the picture thread

songThread = threading.Thread(target = song, args=(pictureQueue,))
# creates the song thread
songThread.start()
# starts the song thread to get updated info

cppThread = threading.Thread(target = runCpp)
# creates a thread for the C++ program to run in - this way it won't stop the main process

if dc_app_ID and sp_client_ID:
    # if both the Application ID and Spotify Client ID are found
    print(f"{Time()}[START]: Found Discord Application ID and Spotify Client ID, starting Discord RPC process\n")
    # user inform
    time.sleep(3)
    # waits a couple seconds to make sure all details are set before calling
    cppThread.start()
    # starts the C++ thread
else:
    # if both aren't found
    print(f"{Time()}[CRITICAL]: Required fields missing, please enter them in the config.ini file before starting the application! Exiting in 5 seconds...\n")
    # user inform
    time.sleep(5)
    # wait 5 seconds
    raise SystemExit
    # end the program, can't really do much without AppID/Spotify Client ID

looper()
# runs the looper, which manages the song refresh cycles
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


DSIver = "v0.19.2.0634"
# the program version (literally just date/time)
# very useful for debug when I accidentally compile the wrong fucking file


if getattr(sys, 'frozen', False):
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
"""The timestamp format for system prints, string (Clock/Uptime)"""

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
        return uptimeStr
        # shortens the call to system uptime
    else:
        # if the config option is set to something else
        return datetime.datetime.now().strftime("%H:%M:%S")
    # shortens the call to current system timestamp

print(f"{Time()} [INFO]: Starting DSI {DSIver}\n")
# quick user update on status


# [URL]
smallURL = Config.get("URL", "small_URL")
"""The small picture URL, string"""
spotifyURL = Config.get("URL", "spotify_URL")
"""The type of large image URL to use, string of: (Track, Artist, Album, Playlist)"""


# [Song-Style]
songNameSpacerL = Config.get("Song-Style", "song_Spacer_Left")
"""spacer between 1st and 2nd field, string"""
songNameSpacerR = Config.get("Song-Style", "song_Spacer_Right")
"""spacer between 2nd and 3rd field, string"""


# [Song-Format]
preText = Config.get("Song-Format", "pre_Text")
"""optional text before the first field, string"""
postText = Config.get("Song-Format", "post_Text")
"""optional text after the last field, string"""
enableSong = Config.getboolean("Song-Format", "enable_Song")
"""song's state, boolean"""
enableArtist = Config.getboolean("Song-Format", "enable_Artist")
"""artist's state, boolean"""
enableAlbum = Config.getboolean("Song-Format", "enable_Album")
"""album's state, boolean"""
albumDrop = Config.getboolean("Song-Format", "enable_Album_Dropping")
"""whether the album dropping is enabled, boolean"""
albumFallback = Config.get("Song-Format", "album_Fallback_Text")
"""the text to fall back to in case the album gets dropped, string"""


# [Pictures]
picCycleList = Config.get("Pictures", "pictures_To_Cycle")
"""list of pictures, list"""

if picCycleList == "File":
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
        print(f"{Time()} [PICT]: Picture list loaded from file\n")
else:
    # if the option isn't set to file
    picCycleList.replace('"', '').split(", ")
    # replaces quotation marks and splits them into a list with commas

picCycleTime = (int(Config.get("Pictures", "picture_Cycle_Time")) * 60)
"""time to wait between picture cycling (minutes), int"""
picCycleType = Config.get("Pictures", "picture_Cycle_Behavior")
"""type of cycling to perform on pictures, string (Random, Sequence, Once, None)"""
smallPic = Config.get("Pictures", "small_Picture_Name").replace('"', '')
"""name/URL of small picture, string"""
hoverText = Config.get("Pictures", "text_On_Small_Hover")
"""text to show on small picture hover, string"""


# [SHAA-Song-Function]
songInfoField1 = Config.get("SHAA-Song-Function", "song_Info_First_Field")
"""first state field type, string (Track, Total)"""
songInfoField2 = Config.get("SHAA-Song-Function", "song_Info_Second_Field")
"""second state field type, string (Track, Total)"""
shaaFallback = Config.get("SHAA-Song-Function", "song_Info_Fallback")
"""fallback type for both state fields, string (Total, custom)"""
shaaInfoDetails = Config.get("SHAA-Song-Function", "song_Info_Detail_Field")
"""details field type, string (Hours, Volume, Repeat, Shuffle, custom)"""


# [SHAA-State-Format]
songInfoFormatPlays = Config.get("SHAA-State-Format", "song_Info_Format_First_Field")
"""text format of the first field, string"""
songInfoSpacer = Config.get("SHAA-State-Format", "song_Info_Spacer")
"""spacer to place between first and second field, string"""
songInfoFormatMins = Config.get("SHAA-State-Format", "song_Info_Format_Second_Field")
"""text format of the second field, string"""
songInfoFallback = Config.get("SHAA-State-Format", "song_Info_Fallback_Format")
"""fallback text for missing song data for both state fields, string"""

songInfoFormatDetails = Config.get("SHAA-Details-Format", "song_Info_Format_Details")
"""text format of the details field, string"""
songInfoFormatDetailsSpacer = Config.get("SHAA-Details-Format", "song_Info_Format_Details_Spacer")
"""spacer to place between details field data and string, string"""
songInfoDetailsDoubleSpace = Config.getboolean("SHAA-Details-Format", "song_Info_Double_Space")
"""whether to add space on either side of the spacer, boolean"""
dsiShoutout = Config.getboolean("SHAA-Details-Format", "dsi_Shoutout")
"""whether to add a shoutout to DSI at the end of the details section, boolean"""


print(f"{Time()} [CFG]: Configuration loaded\n")
# another quick user update


if not enableUpdates:
    # if console printing is disabled in config
    print(f"{Time()} [CFG]: Console updates disabled in config (print_Updates), working silently\n")
    # prints a quick warning

if not enableErrors:
    # if error printing is disabled in config
    print(f"{Time()} [CFG]: Error printing disabled in config (print_Errors)\n")



### Variable Section ###



# Field 1 & 2 Options #
stateOptions = ["Track", "track", "Total", "total"]
# all possible choices for fields 1 and 2 of song details (plays/minutes)

# Detail Field Options #
detailOptions = ["Hours", "hours", "Volume", "volume", "Repeat", "repeat", "Shuffle", "shuffle"]
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
authorisation = SpotifyOAuth(
    scope = "user-read-playback-state user-library-read", 
    client_id = sp_client_ID, 
    client_secret = sp_client_secret, 
    redirect_uri = sp_redirect,
    cache_path = spCache
    )
# the argument for auth_manager, containing the variables from config + scope of data request

main = spotipy.Spotify(auth_manager = authorisation)
# handles the authentication and user identification on start

# URL List #
spotifyURLlist = ["track", "album", "artist", "playlist", "Track", "Album", "Artist", "Playlist"]
# makes a list of all the possible options for spotify URL types

# Picture Cycling Methods #
pictureBehaviorList = ["random", "sequence", "once", "none", "Random", "Sequence", "Once", "None"]
# makes a list of all the possible options for picture cycling types

pauseStart = None
# makes a starter variable for when a pause occurred

cppLargeImage = ""
# makes an empty image string, in case it fails to make first load

dsiShoutoutStr = "// Data by DSI"
# a shoutout string to DSI, disabled by default in config



### Id Writer ###



def idWriter():
    """Function for writing the ids.txt file"""
    # the function used to write the ids.txt file
    with open(idDir, "w", encoding="utf-8") as txt:
    # opens the ids text file
        content = ("Discord Application ID = " + dc_app_ID + "\n" + "Small Image Filename = " + smallPic + "\n" + "Refresh Time = " + str(refreshTime))
        # makes a string from the relevant config options
        txt.write(content)
        if enableUpdates:
            print(f"{Time()} [INFO]: ID file written\n")
        # writes the string to ids.txt at program launch



### Authentication Method ###



def authPlayback():
    """Function to more "safely" handle API requests/errors"""
    global main, authorisation
    # takes the global variables and makes them local

    with spotifyLock:
        # uses a threading lock, to prevent multiple requests at once

        try:
            # first tries to send an API request to Spotify
            return main.current_playback()
            # if it works, returns the Spotify playback package (dictionary)

        except SpotifyException as error:
            # if it fails to acquire a Spotify package
            if enableErrors:
                # if the error updates are on, prints an error message
                print(f"{Time()} [ERROR]: Spotify token errored, attempting to re-authorize...\nError name: {error}")
        
            token_info = authorisation.get_cached_token()
            # tries to use the cached token to get a new one

            if token_info:
                # if there's a valid cached token to use
                authorisation.refresh_access_token(token_info["refresh_token"])
                # uses the token info to get a refresh token
        
            main = spotipy.Spotify(auth_manager=authorisation)
            # passes the new token to the authorisation manager
            
            return main.current_playback()
            # returns the Spotify package

        except SpotifyException as error:
            # if it still fails
            if error.headers["Connection Aborted"] & enableErrors:
                # if the error is 10054 (forcibly disconnected)
                print(f"{Time()} [WARN]: Disconnected, attempting reconnect...")

            elif enableErrors:
                # if it's not exactly the type
                print(f"{Time()} [ERROR]: {error}")
                # prints error



### Spotify History Analyser ### 


if os.path.isfile(SHAAdir):
    # if the grouped.csv file exists
    print(f"{Time()} [SHAA]: Spotify Analyser functionality enabled\n")
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

            picEvent.wait()
            # waits for an event in the picture queue (just makes sure there's a task to be done)

            picLength = (len(self.picCycleList) - 1)
            # calculates the length of the picture list (since it's a list, -1)

            if self.picCycleType in pictureBehaviorList and picLength >= 1:
                # checks if the list has more than one picture (can't cycle if not true)

                if self.picCycleType == "Random" or self.picCycleType == "random":
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
                            print(f"{Time()} [PICT]: Random picture set")
                            # informs user a new picture is set
            
                    time.sleep(self.picCycleTime)
                    # sleeps until it's time to change pictures
                    picEvent.clear()
                    # empties the picture event queue
                    self.run()
                    # runs the starter

                if self.picCycleType == "Sequence":
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
                                print(f"{Time()} [PICT]: Sequential picture set")
                                # informs user a new picture is set

                        time.sleep(self.picCycleTime)
                        # sleeps until it's time to change pictures
                        picEvent.clear()
                        # empties the picture event queue
                        self.run()
                        # runs the starter

                if self.picCycleType == "Once":
                    i = random.randint(0, picLength)
                    # picks a random number based on list length
                    cppLargeImage = self.picCycleList[i]
                    # chooses the element with the random number
                    self.pictureQueue.put(cppLargeImage)
                    # sends the picture to a queue that then reaches song()
                    if enableUpdates:
                        print(f"{Time()} [PICT]: Random picture set")
                    self.running = False
                    # only sets it once, so it stops the background thread

                if self.picCycleType == "None":
                    # if the selected method is None ()
                    cppLargeImage = self.picCycleList[0]
                    # chooses the first picture
                    self.pictureQueue.put(cppLargeImage)
                    # sends the picture to a queue that then reaches song()
                    if enableUpdates:
                        print(f"{Time()} [PICT]: Picture set")
                    self.running = False
                    # only sets it once, so it stops the background thread

            else:
                # if the method field or picture list is empty
                cppLargeImage = ""
                # sets the picture to nothing (empty shouldn't break Discord)
                self.pictureQueue.put(cppLargeImage)
                # sends the picture to a queue that then reaches song()
                if enableErrors:
                    print(f"{Time()} [PICT]: Invalid picture cycle behavior or no picture set - proceeding without a picture")
                self.running = False
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
                    print(f"{Time()} [C++ ]: {line.rstrip()}")
                    # prints it after a line ends



### Picture Queue ###



def song(pictureQueue):
    """The function that handles all song data gathering and parsing, as well as pushing to C++ via text"""
    global uriList
    # pulls the uriList as a local variable from global
    global cppLargeImage
    # pulls the LargeImage as a local variable from global (this is only used as a fallback, in case picCycler fails)
    global uriMap
    # pulls the uriMap as a local variable from global

    while True:

        songEvent.wait()
        # waits for looper() to set an event

        if not pictureQueue.empty():
            # checks pictureQueue to see if it has something
            cppLargeImage = pictureQueue.get()
            # stores the picture from pictureQueue as the picture to send to C++

        songNameList = []
        # creates an empty list for strings to get added into as the loop progresses 

        songStuffList = []
        # creates an empty list for strings to get added into as the loop progresses

        cppLargeHoverList = []
        # creates an empty list for strings to get added into as the loop progresses 

        csFull = authPlayback()
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

        csURI = csItem.get("uri")
        # grabs the URI of the song - which is what determines the song matching

        csArtists = csAlbum.get("artists")
        # stores all the artists listed on the song
        csArtist = csArtists[0].get("name")
        # stores the first artist's name (in case there's multiple artists, only grabs first)

        csAlbumName = csAlbum.get("name")
        # stores the album name

        csLength = csItem.get("duration_ms")
        # stores the length of the song

        csUnixStart = csFull.get("timestamp")
        # stores the start time of the song
        csUnixEnd = (csUnixStart + csLength)
        # stores the end time of the song (by adding up the start + duration)

        csPlayState = bool(csFull.get("is_playing"))
        # grabs the playback state (true/false)

        if not csPlayState:
            # if the song is paused
            global pauseStart
            # takes the pauseStart from global variable to local

            if pauseStart is None:
                # if there's no set pause time
                pauseStart = time.time()
                # sets the pause time to current time

            csUnixStart = 0
            csUnixEnd = 0
            # sets the UNIX timecodes to 0, leading to Discord counting up from paused state
        else:
            # song is playing

            if pauseStart is not None:
                # if there's a set pause time from before
                pauseDuration = time.time() - pauseStart
                # calculates the time spent on pause
                csUnixStart += (pauseDuration * 1000)
                csUnixEnd += (pauseDuration * 1000)
                # sets the start and end times to match the time spent paused
                pauseStart = None
                # resets the pauseStart to None, so it can get checked again

        if enablePause and not csPlayState:
            # if the pause behavior is enabled and song paused
            songNameList.append(pauseStateText)
            # adds the pause text as the first string in the list (since it goes first)

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
                if onPlaylist == False:
                    # the user isn't playing a playlist, but has selected the playlist url config option
                    csURL = smallURL
                    # sets it to smallURL as a fallback
                elif onPlaylist == True:
                    csURL = csPlaylistURL.get("spotify")
                    # takes the playlist's URL

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

                if finalURI not in csvReader.index and altURI in csvReader.index:
                    # if the URI is not found in the CSV index, but the alt URI is
                    finalURI = altURI
                    print(f"{Time()} [SHAA]: URI not found in CSV, but the mapped URI is. Using mapped URI")
                    # sets the URI to use the alternate instead

                if finalURI not in uriList:
                    # if the URI is not in the URI list yet
                    uriList.append(finalURI)
                    # adds it to the list of URIs

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

                if enableUpdates:
                    print(f"{Time()} [SHAA]: Current song found in CSV")

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
                        shaaDetailField =  f"{( ( (csvReader["Total Time"].agg("sum")/1000) /60) /60):,.2f}"
                        # counts total time (hours) for all songs (milliseconds/1000 = seconds / 60 = minutes / 60 = hours, then rounded), turns into a formatted string

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

            ### No Track Match ###

            else:
                # if the track wasn't found in CSV
                if enableUpdates:
                    # if the updates are enabled, lets user know the song wasn't found in CSV
                    print(f"{Time()} [SHAA]: {csName} not found in CSV, using fallback values")
                
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

        if enableAlbum or not postText == "":
            # if there's at least one element after
            if not enableSong and not enableArtist:
                # if there's no other elements (pre/post texts not counting)
                None
                # does nothing
            else:
                songNameList.append(songNameSpacerR)
                # if there's more than just album, adds the right spacer to string

        if enableAlbum:
            # if artist is enabled
            tempState = " ".join(songNameList)
            # temporarily makes a string out of the list
            if len(tempState) > 113:
                # if the total length of the song state is > 113 characters (5 off from the cutoff)
                if albumDrop:
                    # if album dropping is enabled
                    songNameList.append(albumFallback)
                    # puts the album fallback text in the list instead
                else:
                    songNameList.append(csAlbumName)
                    # uses the album anyway (may get cut off)
            else:
                # if the total length is less than 113
                songNameList.append(csAlbumName)
                # adds to string

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



        ### C++ Text File Writer ###


        cppFull = (
                    f"songName = {cppSongName}\n"
                    f"songStuff = {cppState}\n"
                    f"LargeImage = {cppLargeImage}\n"
                    f"LargeText = {cppLargeHover}\n"
                    f"SmallText = {hoverText}\n"
                    f"SpotifyURL = {csURL}\n"
                    f"SmallURL = {smallURL}\n"
                    f"UNIXstart = {str(csUnixStart)}\n"
                    f"UNIXend = {str(csUnixEnd)}\n"
                    )
        # merges all the song information together and removes empty space

        with open(songDataDir, "w", encoding="utf-8") as txt:
            # opens the songData text file
            txt.write(cppFull)
            # writes the full song information to the text file, which is read by the C++ program and then sent to Discord RPC
            if enableUpdates:
                print(f"{Time()} [INFO]: Song data file updated")
                # if updates are enabled, prints an update

        songEvent.clear()
        # clears the event queue, ready to get new requests



### Information Checking Loop ###



currentSong = None
# makes the currentSong empty outside the looper so the loop can start and not make it "None" every time its run

def looper():
    """Function that checks song info on a loop"""
    global currentSong
    # grabs the "global" (outside the function) as a local variable
    while True:
        # this loop checks if the song playing is the same as the previous update, waits if yes, updates the song to match if not
        info = authPlayback()
        # picks up all the info Spotify sends in an update
        if not info or not info.get("item"):
            # checks if the info has something and if it can be called
            if enableErrors:
                print(f"{Time()} [WARN]: No playing state detected, re-checking in 5 seconds\n")
            time.sleep(5)
            # waits for a few seconds
            continue
        songName = (info.get("item")).get("name")
        # grabs the name of the song, stores it
        playing = info.get("is_playing")
        # checks the pause state (True if playing, False if not)

        if currentSong is None:
            # when the program first starts, the currentSong will be "None", this updates it
            currentSong = songName
            # sets the current song to match 
            picEvent.set()
            # since this only runs when the program first starts, sets an event immediately to picCycler, to grab a new picture
            songEvent.set()
            # since this only runs when the program first starts, sets an event immediately to song, to refresh data
            if enableUpdates:
                print(f"{Time()} [INFO]: First song: {songName} has been successfully processed\n")
                # if user wants feedback, sends this

        songProg = (info.get("progress_ms"))
        songDur = (info.get("item")).get("duration_ms")
        # grabs both the current time and length of the song (in milliseconds)
        songLeft = ((songDur-songProg) / 1000)
        # calculates the time left on the song (in seconds)

        if currentSong != songName:
        # if there's a song change
            if enableUpdates:
                # if console updates are enabled
                print(f"{Time()} [SONG]: New song detected: {songName}, duration: {songLeft:,.0f} seconds")
                # user update on new song
                currentSong = songName
                # changes the internal variable to match new song
                songEvent.set()
                # sets an event to make song() update the text file
                time.sleep(5)
                # waits 5 seconds
                info = authPlayback()
                # re-runs the check (in case the song is skipped)
                songName = (info.get("item")).get("name")
                # gets the new song name
                if currentSong != songName:
                    # if the song has changed in 5 seconds
                    time.sleep(5)
                    # waits another 5 seconds, then sends back to start (this way it does 2 checks in the first 10 seconds after a song change)
                    continue
                    # sends back to start of looper


        if not playing:
        # if the song is paused
            sleepfor = max(refreshTime, 5)
            # sets the sleep timer to the higher of the two (never lets it go <5s)

        else:
        # if the current song is the same, and is not paused
            if songLeft > refreshTime:
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
            # if config option for updates is on
            if not playing:
                # if the song is paused, informs user
                print(f"{Time()} [INFO]: Paused on: {songName}, checking again in {sleepfor:,.0f} seconds")
            else:
                # if song is not paused, informs user
                print(f"{Time()} [INFO]: Song unchanged, checking again in {sleepfor:,.0f} seconds")

        time.sleep(sleepfor)
        # sleeps for the determined time


### Load Commands ###


idWriter()
# runs the idWriter, which writes the ids.txt file

bg = Background(picCycleList, picCycleType, picCycleTime, pictureQueue)
# defines the background thread as the class containing all the picture function
# passes the list, type, time and queue

bg.start()
# runs the "background" class, which handles the picture updates

picThread = threading.Thread(target = bg.picCycler)
# creates a thread for the picture changer
picThread.start()
# starts the thread

songThread = threading.Thread(target = song, args=(pictureQueue,))
# creates the song thread
songThread.start()
# starts the song thread to get updated info

cppThread = threading.Thread(target = runCpp)
# creates a thread for the C++ program to run in - this way it won't stop the main process

if dc_app_ID and sp_client_ID:
    # if both the Application ID and Spotify Client ID are found
    print(f"{Time()} [START]: Found Application ID and Spotify Client ID, starting Discord RPC process\n")
    # user inform
    time.sleep(3)
    # waits a couple seconds to make sure all details are set before calling
    cppThread.start()
    # starts the C++ thread
else:
    # if both aren't found
    print(f"{Time()} [CRITICAL]: Required fields missing, please enter them in the config.ini file before starting the application! Exiting in 5 seconds...\n")
    # user inform
    time.sleep(5)
    # wait 5 seconds
    raise SystemExit
    # end the program, can't really do much without AppID/Spotify Client ID

looper()
# runs the looper, which manages the song refresh cycles
import pandas as pd
# Required for all the CSV parsing and data grabbing
import numpy as np
# Required for checking datatype from CSV
import os, time, configparser, random, threading, queue, sys, subprocess
# Required for background tasks, timestamps, config reading, directory checking, C++ executing
import spotipy
# Required for basic function of Spotify data request
from spotipy.oauth2 import SpotifyOAuth
# Required for authorizing with Spotify



### Setup Section ###



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

idDir = os.path.join(directory, "Discord", "ids.txt")
"""the directory where ids.txt should/will live (inside DSI\Discord\ids.txt)"""
songDataDir = os.path.join(directory, "Discord", "songData.txt")
"""the directory where songData.txt should/will live (inside DSI\Discord\songData.txt)"""
SHAAdir = os.path.join(directory, "..", "Data", "CSV", "grouped.csv")
"""the directory where the CSV is (relative to .exe, it's one folder up and then two deep into Spotify Analyser main folder)"""
cppExe = "DSIdiscord.exe"
"""name of the C++ exe file"""
cppPath = os.path.join(directory, "Discord", cppExe)
"""the full path to the C++ exe"""
cppDir = os.path.dirname(cppPath) 
"""the directory the c++ exe lives in"""

print("[INFO] Starting DSI\n")
# quick user update on status

if os.path.isfile(SHAAdir):
    # if the grouped.csv file exists
    print("[SHAA] Spotify Analyser functionality enabled\n")
    # informs user SHAA is enabled
    csvReader = pd.read_csv(SHAAdir, index_col=0, encoding="utf-8")
    # opens the CSV file and uses column 0 as index (track names)

### Config Section ###



# [Required]
sp_client_ID = Config.get("Required", "Spotify_Client_ID")
"""spotify client ID, string"""
sp_client_secret = Config.get("Required", "Spotify_Client_Secret")
"""spotify client secret, string"""
sp_redirect = Config.get("Required", "Spotify_Redirect_URI")
"""spotify redirect URL, string"""
dc_app_ID = Config.get("Required", "Discord_Application_ID")
"""discord application ID, string"""

# [Function]
refreshTime = int(Config.get("Function", "time_Between_Refresh"))
"""program update cycle interval time, integer"""
if refreshTime < 5:
    # if the refresh time is set too low, overrides to safe minimum of 5s
    refreshTime = 5
enablePause = Config.getboolean("Function", "enable_Pause_Behavior")
"""pause text enabler, boolean"""
pauseStateText = Config.get("Function", "pause_Behavior_Text")
"""pause text, string"""
enableUpdates = Config.getboolean("Function", "print_Updates")
"""print updates, boolean"""
enableErrors = Config.getboolean("Function", "print_Errors")
"""print errors, boolean"""

# [URL]
smallURL = Config.get("URL", "small_URL")
"""small picture URL, string"""
spotifyURL = Config.get("URL", "spotify_URL")
"""large image URL, string (Track, Artist, Album, Playlist)"""

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

# [Pictures]
picCycleList = (Config.get("Pictures", "pictures_To_Cycle").replace('"', '')).split(", ")
"""list of pictures, list"""
picCycleTime = int(Config.get("Pictures", "picture_Cycle_Time"))
"""time to wait between picture cycling, int"""
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
"""details field type, string (Hours, Volume, Popularity, Repeat, Shuffle, custom)"""

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

print("[CFG] Configuration loaded\n")
# another quick user update

if not enableUpdates:
    # if console printing is disabled in config
    print("[CFG] Console updates disabled in config (print_Updates), working silently\n")
    # prints a quick warning

if not enableErrors:
    # if error printing is disabled in config
    print("[CFG] Error printing disabled in config (print_Errors)\n")



### Variable Section ###



# Field 1 & 2 Options #
stateOptions = ["Track", "track", "Total", "total"]
# all possible choices for fields 1 and 2 of song details (plays/minutes)

# Detail Field Options #
detailOptions = ["Hours", "hours", "Volume", "volume", "Popularity", "popularity", "Repeat", "repeat", "Shuffle", "shuffle"]
# all possible choices for detail field (hours)

# Picture Queue #
pictureQueue = queue.Queue()
# creates an empty queue for pictures from picCycler to get sent to

# Event Thread #
songEvent = threading.Event()
# creates an empty threading event list for song

picEvent = threading.Event()
# creates an empty threading event list for picturecycler 

# Auth #
authorization = SpotifyOAuth(scope = "user-read-playback-state", client_id = sp_client_ID, client_secret=sp_client_secret, redirect_uri = sp_redirect)
# the argument for auth_manager, containing the variables from config and scope
main = spotipy.Spotify(auth_manager = authorization)
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
            print("[INFO] ID file written\n")
        # writes the string to ids.txt at program launch



### Background Tasker ###



class Background(threading.Thread):
    """Background thread for picture selection"""
# a class to use background tasking, this way the pictures can cycle outside the main song loop
    def __init__(self, picCycleList, picCycleType, picCycleTime, pictureQueue):
        super().__init__()
        self.picCyclerList = picCycleList
        self.picCyclerType = picCycleType
        self.picCyclerTime = picCycleTime
        self.pictureQueue = pictureQueue
        self.running = True
        # "turns on" the thread

    def run(self):
        # starts up the function
        picEvent.set()
        # runs once at start up, giving the event queue 1 task to start with

    def resumePic(self):
        """Function that adds an event to picturecycler's work queue"""
        picEvent.set()

    def picCycler(self):
        """The function used to cycle pictures (and/or set one)"""

        while True:     
        # this function only runs if true, some of the methods below will end it after one cycle

            picEvent.wait()
            # waits for an event in the picture queue (just makes sure there's a task to be done)

            if picCycleType in pictureBehaviorList and len(picCycleList) >= 1:
                # checks if the list has more than one picture (can't cycle if not true)

                if picCycleType == "Random" or picCycleType == "random":
                    # if the selected method is "Random"
                    i = random.randint(0, (len(picCycleList) -1))
                    # picks a random number based on list length (lists start at 0, so -1 to length for position)
                    cppLargeImage = picCycleList[i]
                    # chooses the element with the random number
                    self.pictureQueue.put(cppLargeImage)
                    # sends the picture to a queue that then reaches song()
                    songEvent.set()
                    # sends an event that tells song() to process
                    if enableUpdates:
                        print("[INFO] Random picture set\n")
                    time.sleep(60 * picCycleTime)
                    # sleeps until it's time to change pictures
                    picEvent.clear()
                    # removes the queue

                if picCycleType == "Sequence":
                    # if the selected method is "Sequence"
                    for i in range(0, (len(picCycleList)-1)):
                    # repeats this loop for every element in the list (lists start at 0, so -1 to length for position)
                        cppLargeImage = picCycleList[i]
                        # selects the picture from the list one by one
                        self.pictureQueue.put(cppLargeImage)
                        # sends the picture to a queue that then reaches song()
                        songEvent.set()
                        # sends an event that tells song() to process
                        if enableUpdates:
                            print("[INFO] Picture set\n")
                        time.sleep(60 * picCycleTime)
                        # sleeps until it's time to change pictures
                        picEvent.clear()
                        # removes the queue

                if picCycleType == "Once":
                    i = random.randint(0,(len(picCycleList)-1))
                    # picks a random number based on list length
                    cppLargeImage = picCycleList[i]
                    # chooses the element with the random number
                    self.pictureQueue.put(cppLargeImage)
                    # sends the picture to a queue that then reaches song()
                    songEvent.set()
                    # sends an event that tells song() to process
                    if enableUpdates:
                        print("[INFO] Random picture set\n")
                    self.running = False
                    # only sets it once, so it stops the background thread

                if picCycleType == "None":
                    # if the selected method is None ()
                    cppLargeImage = picCycleList[0]
                    # chooses the first picture
                    self.pictureQueue.put(cppLargeImage)
                    # sends the picture to a queue that then reaches song()
                    songEvent.set()
                    # sends an event that tells song() to process
                    if enableUpdates:
                        print("[INFO] Picture set\n")
                    self.running = False
                    # only sets it once, so it stops the background thread

            else:
                # if the method field or picture list is empty
                cppLargeImage = ""
                # sets the picture to nothing (empty shouldn't break Discord)
                self.pictureQueue.put(cppLargeImage)
                # sends the picture to a queue that then reaches song()
                songEvent.set()
                # sends an event that tells song() to process
                if enableErrors:
                    print("[WARN] Invalid picture cycle behavior or no picture set\nProceeding without a picture\n")
                self.running = False
                # doesn't set a picture, doesn't need to - so it stops the background thread



### C++ ###



def runCpp():
    """Function to start the C++ .exe"""
    with subprocess.Popen([cppPath], cwd=cppDir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as cppPrint:
        # opens the C++ exe, passes a directory and takes output from it
        if enableUpdates:
            for line in cppPrint.stdout:
                # every time the C++ file prints something, this program takes it
                print("[C++]", line, end="")
                # prints it after a line ends



### Picture Queue ###



def song(pictureQueue):
    """The function that handles all song data gathering and parsing, as well as pushing to C++ via text"""
    global cppLargeImage
    # pulls the LargeImage as a local variable from global

    while True:

        songEvent.wait()
        # waits for looper() (or picCycler) to set an event

        if not pictureQueue.empty():
            # checks pictureQueue to see if it has something
            cppLargeImage = pictureQueue.get()
            # stores the picture from pictureQueue as c++LargeImage

        songNameList = []
        # creates an empty list for strings to get added into as the loop progresses 

        songStuffList = []
        # creates an empty list for strings to get added into as the loop progresses

        cppLargeHoverList = []
        # creates an empty list for strings to get added into as the loop progresses 

        csFull = main.current_playback()
        # gets a huge dictionary containing all the information about current song
        # "cs" in the variables just stands for CurrentSong, which, while descriptive, made the later variables insanely long

        if not csFull or not csFull.get("item"):
            # checks if the dictionary is valid and can be called
            time.sleep(5)
            # waits for a few seconds
            continue

        csItem = csFull.get("item")
        # takes the first part of the song's info (leaving out device info and various user states)
        csAlbum = csItem.get("album")
        # takes a smaller part of the song's info (still contains a ton of extra)

        csDevice = csFull.get("device")
        # gets a list of device information

        csName = csItem.get("name")
        # stores the name of the song
        csArtists = csAlbum.get("artists")
        # stores all the artists listed on the song (in case of multi-artist songs)
        csArtist = csArtists[0].get("name")
        # stores the first artist's name
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
            
            cppLargeHoverList.append(shaaInfoDetails)
            # adds the detail field (from config)

            if dsiShoutout:
                cppLargeHoverList.append(dsiShoutoutStr)

        cppLargeHover = " ".join(cppLargeHoverList)
        # joins together the details list to one string


        ### SHAA Behavior ###


        if os.path.isfile(SHAAdir):
            # this is the addon part to Spotify (History) Analyser (SHA + addon = SHAA)
            # this data is only entered to rich presence if used with SHA (and installed correctly)
            # checks if the CSV file exists to pull data from (requires one full run of SHA prior)
            
            if csName in csvReader.index:
                # checks if any appearance of the track is on the list 

                ### Plays / Field 1 ###

                if songInfoField1 == "Track" or songInfoField1 == "track":
                    # if the selected type for first field is Track
                    if isinstance(csvReader.loc[csName, "Playcount"], np.int64):
                        # if there's exactly one instance of the current song (returns as a number)
                        shaaPlaycount = f"{(csvReader.loc[csName, "Playcount"]):,.0f}"
                        # finds total times the song has been played, turns into formatted string
                        songStuffList.append(shaaPlaycount)
                        # adds to string list

                    elif isinstance(csvReader.loc[csName, "Playcount"], pd.Series):
                        # if there's more than one instance of the same song, calculates playcount for all instances
                        pcVar = csvReader.loc[csName, "Playcount"]
                        # finds all instances of total times the song has been played
                        shaaPlaycount = f"{pcVar.sum():,.0f}"
                        # finds total number of plays for all instances of current track, turns into string
                        songStuffList.append(shaaPlaycount)
                        # adds to string list

                elif songInfoField1 == "Total" or songInfoField1 == "total":
                    # if the selected type for the first field is Total
                    shaaPlaycount = f"{csvReader["Playcount"].agg("sum"):,.0f}"
                    # adds up *all* the playcounts for all tracks
                    songStuffList.append(shaaPlaycount)

                else: 
                    # if it doesn't match either
                    songStuffList.append(songInfoField1)
                    # appends with the user-defined custom text

                songStuffList.append(songInfoFormatPlays)
                # adds the first field's custom end styling

                ### Spacer ###

                songStuffList.append(songInfoSpacer)
                # adds the spacer to the list

                ### Minutes / Field 2 ###

                if songInfoField2 == "Track" or songInfoField2 == "track":
                    # if the selected type for the second field is Track
                    if isinstance(csvReader.loc[csName, "Total Time"], np.int64):
                        # if there's exactly one instance of the current song (returns as a number)
                        shaaPlaytime = f"{( ( (csvReader.loc[csName, "Total Time"]) / 1000) / 60):,.1f}"
                        # finds total time played (min) for current song (milliseconds / 1000 = seconds / 60 = minutes), turns into a formatted string
                        songStuffList.append(shaaPlaytime)
                        # adds to string list

                    elif isinstance(csvReader.loc[csName, "Total Time"], pd.Series):
                        # if there's more than one instance of the same song, calculates playtime for all instances
                        ttVar = csvReader.loc[csName, "Total Time"]
                        shaaPlaytime = f"{((ttVar.sum() / 1000 )/ 60):,.1f}"
                        # finds total time played (min) for all instances of current song (milliseconds / 1000 = seconds / 60 = minutes), turns into a formatted string
                        songStuffList.append(shaaPlaytime)
                        # adds to string list

                elif songInfoField2 == "Total" or songInfoField2 == "total":
                    # if the selected type for the first field is Total
                    shaaPlaytime = f"{((csvReader["Total Time"].agg("sum") / 1000 ) / 60):,.0f}"
                    # adds up *all* the time played (milliseconds/1000 = seconds / 60 = minutes)
                    songStuffList.append(shaaPlaytime)
                    # adds to string list
                else:
                    # if it doesn't match either
                    songStuffList.append(songInfoField2)
                    # appends with the user-defined custom text

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
                    
                    if shaaInfoDetails == "Popularity" or shaaInfoDetails == "popularity":
                        # if the config calls for popularity
                        try:
                            shaaDetailField = csItem.get("popularity")
                            # takes the popularity rating
                        except:
                            shaaDetailField = "somewhat popular"
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

                cppLargeHoverList.append(shaaDetailField)
                # joins together the list 

                if dsiShoutout:
                    cppLargeHoverList.append(dsiShoutoutStr)


            ### No Track Match ###


            else:
                # if the track wasn't found in CSV
                if enableUpdates:
                    # if the updates are enabled, lets user know the song wasn't found in CSV
                    print(f"[WARN] {csName} not found in CSV, using fallback values.\n")
                
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

                    if shaaInfoDetails == "Popularity" or shaaInfoDetails == "popularity":
                        # if the config calls for popularity
                        try:
                            shaaDetailField = csItem.get("popularity")
                            # takes the popularity rating
                        except:
                            shaaDetailField = "somewhat popular"
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

                cppLargeHoverList.append(shaaDetailField)
                # adds the detail field to the list

                if dsiShoutout:
                    cppLargeHoverList.append(dsiShoutoutStr)

            cppLargeHover = " ".join(cppLargeHoverList)
            # joins together the detail list of strings (SHAA-only)
            

        ### Song Stuff String Joiner ###


        cppState = " ".join(songStuffList)
        # joins together the song information


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
            songNameList.append(csAlbumName)
            # adds to string

        if postText:
            # if postText has something
            songNameList.append(postText)
            # adds to string

        cppSongName = " ".join(songNameList)
        # takes the list of strings from above and joins it together 


        ### C++ Text File Writer ###


        cppFull = (
                    "songName = " + cppSongName + "\n" + 
                    "songStuff = " + cppState + "\n" +
                    "LargeImage = " + cppLargeImage + "\n" +
                    "LargeText = " + cppLargeHover + "\n" +
                    "SmallText = " + hoverText + "\n" +
                    "SpotifyURL = " + csURL + "\n" +
                    "SmallURL = " + smallURL + "\n" +
                    "UNIXstart = " + str(csUnixStart) + "\n" +
                    "UNIXend = " + str(csUnixEnd)
                    )
        # merges all the song information together

        with open(songDataDir, "w", encoding="utf-8") as txt:
            # opens the songData text file
            txt.write(cppFull)
            # writes the full song information to the text file, which is read by the C++ program and then sent to Discord RPC
            if enableUpdates:
                print("[INFO] Song data file updated\n")
        songEvent.clear()
        # clears the event queue, ready to get new requests



### Information Checking Loop ###



currentSong = None
# makes the currentSong empty outside the looper so the loop can start and not make it "None" every time its run

def looper():
    """Function that checks song info on a loop"""
    global currentSong
    while True:
        # this loop checks if the song playing is the same as the previous update, waits if yes, updates the song to match if not
        info = main.current_playback()
        # picks up all the info Spotify sends in an update
        if not info or not info.get("item"):
            # checks if the info has something and if it can be called
            if enableErrors:
                print("[WARN] No playing state detected, re-checking in 5 seconds\n")
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
            # calls for the C++ program to start as a subprocess of this program, passing its output
            picEvent.set()
            # since this only runs when the program first starts, sets an event immediately to picCycler, to grab a new picture (breaks if none is set)
            songEvent.set()
            # since this only runs when the program first starts, sets an event immediately to song, to refresh data
            if enableUpdates:
                print("[INFO] First song processed\n")
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
                print(f"[INFO] New song found: {songName}\n")
                # user update
                currentSong = songName
                # changes the internal variable to match new song
                songEvent.set()
                # sets an event to make song() update the text file

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
                print(f"[INFO] Paused on: {songName}, checking again in {sleepfor} seconds\n")
            else:
                # if song is not paused, informs user
                print(f"[INFO] Song unchanged, checking again in {sleepfor} seconds\n")

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
# creates a thread for the C++ program

if dc_app_ID and sp_client_ID:
    # if both the Application ID and Spotify Client ID are found
    print("[START] Found Application ID and Spotify Client ID, starting Discord RPC process\n")
    # user inform
    time.sleep(3)
    # waits a couple seconds to make sure all details are set before calling
    cppThread.start()
    # starts the C++ thread
else:
    # if both aren't found
    print("[CRITICAL] Application ID/Spotify ID missing, please enter them in the config.ini file before starting the application\nExiting in 5 seconds...\n")
    # user inform
    time.sleep(5)
    # wait 5 seconds
    raise SystemExit
    # end the program, can't really do much without AppID/Spotify Client ID

looper()
# runs the looper, which manages the song refresh cycles
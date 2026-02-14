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
    # bundled with pyInstaller, so it's "frozen"
    directory = os.path.dirname(sys.executable)
    # gets the base directory of the program, where the python .exe resides
else:
    # if somehow not in a bundled state
    directory = os.path.dirname(__file__)
    # gets the base directory of the program, where the python .exe resides

Config = configparser.ConfigParser(comment_prefixes = ["/", "#"], allow_no_value = True)
# sets up the config reader
ConfigPath = os.path.join(directory, "config.ini")
# calls the pathFinder to give the location of "config.ini"
Config.read(ConfigPath, "utf8")
# reads from the config, saves values below

idDir = os.path.join(directory, "Discord", "ids.txt")
# the directory where ids.txt should/will live (inside DSI\Discord\ids.txt)
songDataDir = os.path.join(directory, "Discord", "songData.txt")
# the directory where songData.txt should/will live (inside DSI\Discord\songData.txt)
SHAAdir = os.path.join(directory, "..", "Data", "CSV", "grouped.csv")
# the directory where the CSV is (relative to .exe, it's one folder up and then two deep into Spotify Analyser main folder)
cppExe = "DSIdiscord.exe"
# name of the C++ exe file
cppPath = os.path.join(directory, "Discord", cppExe)
# the full path to the C++ exe
cppDir = os.path.dirname(cppPath) 
# the directory the c++ exe lives in

print("Starting DSI\n")
# quick user update on status

if os.path.isfile(SHAAdir):
    # if the grouped.csv file exists
    print("Spotify Analyser functionality enabled\n")
    # informs user SHAA is enabled



### Config Section ###



# [Required]
sp_client_ID = Config.get("Required", "Spotify_Client_ID")
sp_client_secret = Config.get("Required", "Spotify_Client_Secret")
sp_redirect = Config.get("Required", "Spotify_Redirect_URI")
dc_app_ID = Config.get("Required", "Discord_Application_ID")

# [Function]
refreshTime = int(Config.get("Function", "time_Between_Refresh"))
if refreshTime < 5:
    # if the refresh time is set too low, overrides to safe minimum of 5s
    refreshTime = 5
enablePause = Config.getboolean("Function", "enable_Pause_Behavior")
pauseStateText = Config.get("Function", "pause_Behavior_Text")
enableUpdates = Config.getboolean("Function", "print_Updates")

# [URL]
smallURL = Config.get("URL", "small_URL")
spotifyURL = Config.get("URL", "spotify_URL")

# [Song-Style]
songNameSpacerL = Config.get("Song-Style", "song_Spacer_Left")
songNameSpacerR = Config.get("Song-Style", "song_Spacer_Right")

# [Song-Format]
preText = Config.get("Song-Format", "pre_Text")
postText = Config.get("Song-Format", "post_Text")
enableSong = Config.getboolean("Song-Format", "enable_Song")
enableArtist = Config.getboolean("Song-Format", "enable_Artist")
enableAlbum = Config.getboolean("Song-Format", "enable_Album")

# [Pictures]
picCycleList = (Config.get("Pictures", "pictures_To_Cycle").replace('"', '')).split(", ")
picCycleTime = int(Config.get("Pictures", "picture_Cycle_Time"))
picCycleType = Config.get("Pictures", "picture_Cycle_Behavior")
smallPic = Config.get("Pictures", "small_Picture_Name").replace('"', '')
hoverText = Config.get("Pictures", "text_On_Small_Hover")

# [SHAA-Song-Info]
shaalessField = Config.get("SHAA-Song-Info", "song_Info_Empty_Field")
songInfoField1 = Config.get("SHAA-Song-Info", "song_Info_First_Field")
songInfoField2 = Config.get("SHAA-Song-Info", "song_Info_Second_Field")
songInfoSpacer = Config.get("SHAA-Song-Info", "song_Info_Spacer")
songInfoFormatPlays = Config.get("SHAA-Song-Info", "song_Info_Format_Plays")
songInfoFormatMins = Config.get("SHAA-Song-Info", "song_Info_Format_Mins")
songInfoFormatHours = Config.get("SHAA-Song-Info", "song_Info_Format_Hours")
songInfoFormatHourSpacer = Config.get("SHAA-Song-Info", "song_Info_Format_Hour_Spacer")
songInfoHourDoubleSpace = Config.getboolean("SHAA-Song-Info", "song_Info_Double_Space")



print("Configuration loaded\n")
# another quick user update

if not enableUpdates:
    # if console printing is disabled in config
    print("Console updates disabled in config (print_Updates), working silently\n")
    # prints a quick warning



### Variable Section ###



# Picture Queue #
pictureQueue = queue.Queue()
# creates an empty queue for pictures from picCycler to get sent to

# Event Thread #
event = threading.Event()
# creates an empty threading event list

# Auth String #
main = spotipy.Spotify(auth_manager = SpotifyOAuth(scope = "user-read-playback-state", client_id = sp_client_ID, client_secret = sp_client_secret, redirect_uri = sp_redirect))
# handles the authentication and user identification on start

# URL List #
spotifyURLlist = ["track", "album", "artist", "playlist", "Track", "Album", "Artist", "Playlist"]
# makes a list of all the possible options for spotify URL types

# Picture Cycling Methods #
pictureBehaviorList = ["random", "sequence", "once", "none", "Random", "Sequence", "Once", "None"]
# makes a list of all the possible options for picture cycling types



### Id Writer ###



def idWriter():
    # the function used to write the ids.txt file
    with open(idDir, "w", encoding="utf-8") as txt:
    # opens the ids text file
        content = ("Discord Application ID = " + dc_app_ID + "\n" + "Small Image Filename = " + smallPic + "\n" + "Refresh Time = " + str(refreshTime))
        # makes a string from the relevant config options
        txt.write(content)
        if enableUpdates:
            print("ID file written\n")
        # writes the string to ids.txt at program launch



### Background Tasker ###



class Background(threading.Thread):
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
        # creates a starter for picCycler
        while self.running:
        # runs the picCycler while the thread is active
            self.picCycler()

    def picCycler(self):
    # the function used to cycle pictures (and/or set one)
        while True:

            if picCycleType in pictureBehaviorList and len(picCycleList) >= 1:
                # checks if the list has more than one picture (can't cycle if not true)

                if picCycleType == "Random" or picCycleType == "random":
                    # if the selected method is "Random"
                    i = random.randint(0,(len(picCycleList)-1))
                    # picks a random number based on list length
                    cppLargeImage = picCycleList[i]
                    # chooses the element with the random number
                    self.pictureQueue.put(cppLargeImage)
                    # sends the picture to a queue that then reaches song()
                    event.set()
                    # sends an event that tells song() to process
                    time.sleep(60 * picCycleTime)
                    # sleeps until it's time to change pictures
                    print("Updating picture\n")

                if picCycleType == "Sequence":
                    # if the selected method is "Sequence"
                    for i in range(0, (len(picCycleList)-1)):
                    # repeats this loop for every element in the list (sleeping in between)
                        cppLargeImage = picCycleList[i]
                        # selects the picture from the list one by one
                        self.pictureQueue.put(cppLargeImage)
                        # sends the picture to a queue that then reaches song()
                        event.set()
                        # sends an event that tells song() to process
                        time.sleep(60 * picCycleTime)
                        # sleeps until it's time to change pictures
                        print("Updating picture\n")

                if picCycleType == "Once":
                    i = random.randint(0,(len(picCycleList)-1))
                    # picks a random number based on list length
                    cppLargeImage = picCycleList[i]
                    # chooses the element with the random number
                    self.pictureQueue.put(cppLargeImage)
                    # sends the picture to a queue that then reaches song()
                    event.set()
                    # sends an event that tells song() to process
                    self.running = False
                    # only sets it once, so it stops the background thread

                if picCycleType == "None":
                    # if the selected method is None ()
                    cppLargeImage = picCycleList[0]
                    # chooses the first picture
                    self.pictureQueue.put(cppLargeImage)
                    # sends the picture to a queue that then reaches song()
                    event.set()
                    # sends an event that tells song() to process
                    self.running = False
                    # only sets it once, so it stops the background thread

            else:
                # if the method field or picture list is empty
                cppLargeImage = ""
                # sets the picture to nothing (empty shouldn't break Discord)
                self.pictureQueue.put(cppLargeImage)
                # sends the picture to a queue that then reaches song()
                event.set()
                # sends an event that tells song() to process
                self.running = False
                # doesn't really set a picture, so it stops the background thread



### C++ ###



def runCpp():
    # the C++ starter
    with subprocess.Popen([cppPath], cwd=cppDir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as cppPrint:
        # opens the C++ exe, passes a directory and takes output from it
        for line in cppPrint.stdout:
            # every time the C++ file prints something, this program takes it
            print(line, end="")
            # prints it after a line ends



### Picture Queue ###



def song(pictureQueue):
# the function used to handle all the song data gathering and parsing, as well as pushing to C++ via text
    while True:

        event.wait()
        # waits for looper() (or picCycler) to set an event

        if not pictureQueue.empty():
            # checks pictureQueue to see if it has something
            cppLargeImage = pictureQueue.get()
            # stores the picture from pictureQueue as c++LargeImage

        songNameList = []
        # creates an empty list for strings to get added into as the loop progresses 

        songStuffList = []
        # creates an empty list for strings to get added into as the loop progresses

        cppHoursList = []
        # creates an empty list for strings to get added into as the loop progresses 

        csFull = main.current_playback()
        # gets a huge dictionary containing all the information about current song
        # "cs" in the variables just stands for CurrentSong, which, while descriptive, made the later variables insanely long

        csItem = csFull.get("item")
        # takes the first part of the song's info (leaving out device info and various user states)
        csAlbum = csItem.get("album")
        # takes a smaller part of the song's info (still contains a ton of extra)

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

        csPauseState = bool(csFull.get("is_playing"))
        # grabs the playback state (true/false)

        if enablePause and not csPauseState:
            # if the pause behavior is enabled and the playback state is false (paused)
                csUnixStart = 0
                csUnixEnd = 0
                # sets the UNIX timecodes to 0, leading to Discord counting up from paused state
                songNameList.append(pauseStateText)
                # adds the paused state pretext to the list of strings

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

        elif not csPlaylist == None:
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
                    # sets it to my website as a fallback
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
            shaaPlaycount = shaalessField
            # replaces playcount with user defined field
            if shaalessField:
                # only adds the playcount if it's not empty
                songStuffList.append(shaaPlaycount)
            # adds the playcount to list
            if songInfoFormatPlays:
                # only adds the format if it's not empty
                songStuffList.append(songInfoFormatPlays)
                # adds the user defined field 1 format to list
            songStuffList.append(songInfoSpacer)
            # adds the spacer to list
            shaaPlaytime = shaalessField
            # replaces playtime with user defined field
            if shaalessField:
                # only adds the playtime if it's not empty
                songStuffList.append(shaaPlaytime)
            # adds the playtime to list
            if songInfoFormatMins:
                # only adds the format if it's not empty
                songStuffList.append(songInfoFormatMins)
                # adds the user defined field 2 format to list

            shaaTotalTime = shaalessField
            # replaces total hours with user defined field

        ### SHAA Behavior ###

        if os.path.isfile(SHAAdir):
            # this is the addon part to Spotify (History) Analyser (SHA + addon = SHAA)
            # this data is only entered to rich presence if used with SHA (and installed correctly)
            # checks if the CSV file exists to pull data from (requires one full run of SHA prior)

            csvReader = pd.read_csv(SHAAdir, index_col=0)
            # opens the CSV file and uses column 0 as index (track names)

            if csName in csvReader.index:
                # checks if any appearance of the track is on the list 

                ### Field 1 ###

                if songInfoField1 == "Track":
                    # if the selected type for first field is Track
                    if isinstance(csvReader.loc[csName, "Playcount"], np.int64):
                        # if there's exactly one instance of the current song (returns as a number)
                        shaaPlaycount = f"{(csvReader.loc[csName, "Playcount"]):,.0f} "
                        # finds total times the song has been played, turns into formatted string
                        songStuffList.append(shaaPlaycount)
                        # adds to string list

                    elif isinstance(csvReader.loc[csName, "Playcount"], pd.Series):
                        # if there's more than one instance of the same song, calculates playcount for all instances
                        pcVar = csvReader.loc[csName, "Playcount"]
                        # finds all instances of total times the song has been played
                        shaaPlaycount = f"{pcVar.sum():,.0f} "
                        # finds total number of plays for all instances of current track, turns into string
                        songStuffList.append(shaaPlaycount)
                        # adds to string list

                if songInfoField1 == "Total":
                    # if the selected type for the first field is Total
                    shaaPlaycount = f"{csvReader["Playcount"].agg("sum"):,.0f} "
                    # adds up *all* the playcounts for all tracks
                    songStuffList.append(shaaPlaycount)

                else: 
                    # if the songInfoField1 is something else
                    shaaPlaycount = ""
                    songStuffList.append(shaaPlaycount)

                songStuffList.append(songInfoFormatPlays)
                # adds the first field's custom styling

                ### Spacer ###

                songStuffList.append(songInfoSpacer)

                ### Field 2 ###

                if songInfoField2 == "Track":
                    # if the selected type for the second field is Track
                    if isinstance(csvReader.loc[csName, "Total Time"], np.int64):
                        # if there's exactly one instance of the current song (returns as a number)
                        shaaPlaytime = f"{( ( (csvReader.loc[csName, "Total Time"]) / 1000) / 60):,.1f} "
                        # finds total time played (min) for current song (milliseconds / 1000 = seconds / 60 = minutes), turns into a formatted string
                        songStuffList.append(shaaPlaytime)
                        # adds to string list

                    elif isinstance(csvReader.loc[csName, "Total Time"], pd.Series):
                        # if there's more than one instance of the same song, calculates playtime for all instances
                        ttVar = csvReader.loc[csName, "Total Time"]
                        shaaPlaytime = f"{((ttVar.sum() / 1000 )/ 60):,.1f} "
                        # finds total time played (min) for all instances of current song (milliseconds / 1000 = seconds / 60 = minutes), turns into a formatted string
                        songStuffList.append(shaaPlaytime)
                        # adds to string list

                if songInfoField2 == "Total":
                    # if the selected type for the first field is Total
                    shaaPlaytime = f"{((csvReader["Total Time"].agg("sum") / 1000 ) / 60):,.0f} "
                    # adds up *all* the time played (milliseconds/1000 = seconds / 60 = minutes)
                    songStuffList.append(shaaPlaytime)
                    # adds to string list
                else:
                    # if it doesn't match either, makes it an empty string
                    shaaPlaytime = ""
                    songStuffList.append(shaaPlaytime)
                    # adds to string list

                ### Total Hours ###

                shaaTotalTime =  f"{( ( (csvReader["Total Time"].agg("sum")/1000) /60) /60):,.2f}"
                # counts total time (hours) for all songs (milliseconds/1000 = seconds / 60 = minutes / 60 = hours, then rounded), turns into a formatted string

            ### No Track Match ###

            else:
                # in case the song has never been played before (or doesn't appear in the CSV)
                shaaPlaycount = "0 "
                shaaPlaytime = "0 "
                # makes the playcount and playtime for that song 0

            

        ### Song Stuff String Joiner ###



        cppSongStuff = " ".join(songStuffList)
        # joins together the song information
        # default appearance: " N/A plays ※ N/A minutes " , " Total Hours: N/A "



        ### Song Style ###



        SNSL = True
        # sets a temp flag for the left spacer, just so it can't get double printed

        if not preText == "":
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

        if not postText == "":
            # if postText has something
            songNameList.append(postText)
            # adds to string

        cppSongName = " ".join(songNameList)
        # takes the list of strings from above and joins it together 

        ### Total Hours ###

        if songInfoFormatHours:
            # if the format option isn't empty
            cppHoursList.append(songInfoFormatHours)
            # adds to string list

        if songInfoHourDoubleSpace:
            # if the double space is enabled
            cppHoursList.append(" ")
            # adds an empty space

        if songInfoFormatHourSpacer:
            # if the format spacer option isn't empty
            cppHoursList.append(songInfoFormatHourSpacer + " ")
            # adds to string list

        cppHoursList.append(shaaTotalTime)
        # total time is unavoidable, adds to end

        cppHours = "".join(cppHoursList)
        # joins together the total hours list of strings


        ### C++ Text File Writer ###



        cppFull = (
                    "songName = " + cppSongName + "\n" + 
                    "songStuff = " + cppSongStuff + "\n" +
                    "LargeImage = " + cppLargeImage + "\n" +
                    "LargeText = " + cppHours + "\n" +
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
                print("Song data file updated\n")
        event.clear()
        # clears the event queue, ready to get new requests



### Information Checking Loop ###



currentSong = None
# makes the currentSong empty outside the looper so the loop can start and not make it "None" every time its run

def looper():
    # this loop checks if the song playing is the same as the previous update, waits if yes, updates the song to match if not
    info = main.current_playback()
    # picks up all the info Spotify sends in an update
    songName = (info.get("item")).get("name")
    # grabs the name of the currently playing song
    global currentSong
    if currentSong is None:
        # when the program first starts, the currentSong will be "None", this updates it
        currentSong = songName
        if enableUpdates:
            print("First song processed\n")
            # if user wants feedback, sends this
        # calls for the C++ program to start as a subprocess of this program, passing its output
        event.set()
        # since this only runs when the program first starts, sets an event immediately
    songProg = (info.get("progress_ms"))
    songDur = (info.get("item")).get("duration_ms")
    # grabs both the current time and length of the song (in milliseconds)
    songLeft = ((songDur-songProg) / 1000)
    # calculates the time left on the song (in seconds)

    if currentSong == songName:
        # current song is the same as the last time
        if enableUpdates:
            print("The song changes in", songLeft, "seconds", "\n")
        if songLeft > refreshTime:
            time.sleep(refreshTime)
            # sleeps for as long as the config setting sets
            looper()
        if songLeft <= refreshTime:
            time.sleep(songLeft)
            # if the song has less than the refresh time, only waits the remainder of the song
            looper()

    if currentSong != songName:
        # song is not the same as it was last time it was checked
        if enableUpdates:
            print("New song found, writing file\n")
        event.set()
        # starts the song status updater
        currentSong = songName
        # updates the current song to match
        time.sleep(3)
        # sleeps for a few seconds to let other parts work
        looper()
        # re-runs looper, which now has the new song name



### Load Commands ###



idWriter()
# runs the idWriter, which writes the ids.txt file

songThread = threading.Thread(target=song, args=(pictureQueue,))
# creates the song thread
songThread.start()
# starts the song thread to get updated info

cppThread = threading.Thread(target = runCpp)
# creates a thread for the C++ program

picCyclerThread = Background(picCycleList, picCycleType, picCycleList, pictureQueue)
# creates the picture cycler

picCyclerThread.start()
# runs the picture cycler thread

if dc_app_ID and sp_client_ID:
    # if both the Application ID and Spotify Client ID are found (only these 2 because the odds of user adding only 1 Spotify argument of 3 seems low)
    print("Found Application ID and Spotify Client ID, starting Discord RPC process\n")
    # user inform
    time.sleep(2)
    # waits a couple seconds
    cppThread.start()
    # starts the C++ thread
elif not dc_app_ID and not sp_client_ID:
    # if discord and/or spotify client ids not found
    print("Application ID/Spotify ID missing, please enter them in the config.ini file before starting the application\nExiting in 5 seconds...")
    # user inform
    time.sleep(5)
    # wait 5 seconds
    raise SystemExit
    # end the program, can't really do much without AppID/Spotify Client ID

looper()
# runs the looper, which manages the song refresh cycles
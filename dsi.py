import pandas as pd
import numpy as np
import os, time, configparser, spotipy, random, threading, queue
from spotipy.oauth2 import SpotifyOAuth

import APItokens

# all this will be deleted and the "devDir" will be replaced by the mainDir's path below
devDir = "S:/Spotify Analyzer/Data/CSV/grouped.csv"
# the directory used during development (will be deleted)
mainDir = "../Data/CSV/grouped.csv"
# the directory used after installation (this addon installs into Spotify Analyzer/DSI/)

Config = configparser.ConfigParser(comment_prefixes=["/", "#"], allow_no_value=True)
Config.read('./config.ini', "utf8")
# this opens the config file to be checked later

sp_client_ID = APItokens.client_ID
# the "client ID" token inside Spotify Dashboard (replace with "PLACE CLIENT ID HERE")
sp_client_secret =  APItokens.client_secret 
# the "client secret" token inside Spotify Dashboard (replace with "PLACE CLIENT SECRET HERE")
sp_redirect = APItokens.redirect
# the URL for the Spotify redirect, also inside Spotify Dashboard (replace with "PLACE REDIRECT URL HERE")
dc_app_ID = APItokens.dcID
picCycleList = APItokens.picList
smallPic = APItokens.smallPic

### Config section - Pulls config info from config.ini

# [Required]
# sp_client_ID = Config.get("Required", "Spotify_Client_ID")
# sp_client_secret = Config.get("Required, Spotify_Client_Secret")
# sp_redirect = Config.get("Required", "Spotify_Redirect_URI")
# dc_app_ID = Config.get("Required", Discord_Application_ID)

# [Function]
refreshTime = int(Config.get("Function", "time_between_refresh"))

# [URL]
smallURL = Config.get("URL", "small_URL")
spotifyURL = Config.get("URL", "spotify_URL")

# [Song-Style]
songNameSpacerL = Config.get("Song-Style", "song_Spacer_Left")
songNameSpacerR = Config.get("Song-Style", "song_Spacer_Right")

# [Song-Format]
preText = Config.get("Song-Format", "preText")
postText = Config.get("Song-Format", "postText")
songOrder = Config.get("Song-Format", "song_format")

# [Pictures]
# picCycleList = Config.get("Pictures", "pictures_to_cycle")
picCycleTime = int(Config.get("Pictures", "picture_cycle_time"))
picCycleType = Config.get("Pictures", "picture_cycle_behavior")
# smallPic = Config.get("Pictures", "small_picture_name")
hoverText = Config.get("Pictures", "text_on_small_hover")

# [SHAA-Song-Info]
shaalessPlaycount = shaalessPlaytime = shaalessTotalTime = Config.get("SHAA-Song-Info", "song_Info_Empty_Field")
songInfoSpacer = Config.get("SHAA-Song-Info", "song_Info_Spacer")
songInfoFormatPlays = Config.get("SHAA-Song-Info", "song_Info_Format_Plays")
songInfoFormatMins = Config.get("SHAA-Song-Info", "song_Info_Format_Mins")
songInfoFormatHours = Config.get("SHAA-Song-Info", "song_Info_Format_Hours")
songInfoFormatHourSpacer = Config.get("SHAA-Song-Info", "song_Info_Format_Hour_Spacer")

##
# if you know what you're doing, you can further customise the look of the output below (lines 126 and beyond)
##



# Picture Queue
pictureQueue = queue.Queue()
# creates an empty queue for pictures from picCycler to get sent to

# Event Thread
event = threading.Event()
# creates an empty threading event list

# Auth String
main = spotipy.Spotify(auth_manager = SpotifyOAuth(scope = "user-read-playback-state", client_id = sp_client_ID, client_secret = sp_client_secret, redirect_uri = sp_redirect))
# handles the authentication and user identification on start



def idWriter():
    # the function used to write the ids.txt file
    with open("ids.txt", "w", encoding="utf-8") as txt:
    # opens the ids text file
        content = ("Discord Application ID = " + dc_app_ID + "\n" + "Small Image Filename = " + smallPic + "\n" + "Refresh Time = " + str(refreshTime))
        # makes a string from the relevant config options
        txt.write(content)
        # writes the string to ids.txt at program launch



class Background(threading.Thread):
# a class to use background tasking, this way the pictures can cycle outside the main loop
    def __init__(self, picCycleList, picCycleType, picCycleTime, pictureQueue):
        super().__init__()
        self.picCyclerList = picCycleList
        self.picCyclerType = picCycleType
        self.picCyclerTime = picCycleTime
        self.pictureQueue = pictureQueue
        self.running = True
        # "turns on" the thread

    def run(self):
        while self.running:
        # runs the picCycler while the thread is active
            self.picCycler()

    def picCycler(self):
    # the function used to cycle pictures (and/or set one)
        while True:

            if picCycleType == "Random" and len(picCycleList) > 1:
                # if the selected method is "Random", and the list has more than 1 element
                i = random.randint(0,(len(picCycleList)-1))
                # picks a random number based on list length
                cppLargeImage = picCycleList[i] # this needs to get passed to song somehow, someway
                # chooses the element with the random number
                self.pictureQueue.put(cppLargeImage)
                # sends the picture to a queue that then reaches song()
                event.set()
                # sends an event that tells song() to process
                time.sleep(60 * picCycleTime)
                # sleeps until it's time to change pictures
        
            elif picCycleType == "Random" and len(picCycleList) == 1:
                # if the selected method is "Random", but the list has only 1 element
                cppLargeImage = picCycleList[0]
                # sets the picture to the first (only) element
                self.pictureQueue.put(cppLargeImage)
                # sends the picture to a queue that then reaches song()
                event.set()
                # sends an event that tells song() to process
                # doesn't ever update, because there's nothing to update

            elif picCycleType == "Random" and len(picCycleList) < 1:
                # if the selected method is "Random", but the list is empty
                cppLargeImage = ""
                # sets the picture to nothing (this won't break Discord)
                self.pictureQueue.put(cppLargeImage)
                # sends the picture to a queue that then reaches song()
                event.set()
                # sends an event that tells song() to process
                # doesn't ever update, because there's nothing to update

            if picCycleType == "Sequence":
                for i in range(0, (len(picCycleList)-1)):
                    cppLargeImage = picCycleList[i]
                    # selects the picture from the list one by one
                    self.pictureQueue.put(cppLargeImage)
                    # sends the picture to a queue that then reaches song()
                    event.set()
                    # sends an event that tells song() to process
                    time.sleep(60 * picCycleTime)
                    # sleeps until it's time to change pictures

            if picCycleType == "RandomOnce" and len(picCycleList) >= 1:
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
            
            if picCycleType == "None" or len(picCycleList) < 1:
                # if the selected method is "None", or the list is empty
                cppLargeImage = ""
                # sets the picture to nothing (this won't break Discord)
                self.pictureQueue.put(cppLargeImage)
                # sends the picture to a queue that then reaches song()
                event.set()
                # sends an event that tells song() to process
                self.running = False
                # only sets it once, so it stops the background thread



def song(pictureQueue):
# the function used to handle all the song data gathering and parsing, as well as pushing to C++ via text
    while True:

        event.wait()
        # waits for looper() (or picCycler) to set an event

        if not pictureQueue.empty():
            # checks pictureQueue to see if it has something
            cppLargeImage = pictureQueue.get()
            # stores the picture from pictureQueue as c++LargeImage
        
        csFull = main.current_playback()
        # gets a huge dictionary containing all the information about current song
        # "cs" in the variables just stands for CurrentSong, which, while descriptive, made the later variables insanely long

        csShort = csFull.get("item")
        # takes the first part of the song's info (leaving out device info and various user states)
        cs = csShort.get("album")
        # takes a smaller part of the song's info (still contains a ton of extra)

        csName = csShort.get("name")
        # stores the name of the song
        csArtists = cs.get("artists")
        # stores all the artists listed on the song (in case of multi-artist songs)
        csArtist = csArtists[0].get("name")
        # stores the first artist name
        csAlbum = cs.get("name")
        # stores the album name

        csLength = csShort.get("duration_ms")
        # stores the length of the song

        csUnixStart = csFull.get("timestamp")
        # stores the start time of the song
        csUnixEnd = (csUnixStart + csLength)
        # stores the end time of the song (by adding up the start + duration)

        csRawURL = csShort.get("external_urls")
        csURL = csRawURL.get("spotify")
        # takes the track URL

        if os.path.exists(devDir):
            # this is the addon part to Spotify (History) Analyser (SHA + addon = shaa)
            # this data is only entered to rich presence if used with SHA (and installed correctly)
            # checks if the CSV file exists to pull data from (requires one full run of SHA prior)
            csvReader = pd.read_csv(devDir, index_col=0)
            # opens the CSV file and uses column 0 as index (track names)
            if csName in csvReader.index:
                # checks if any appearance of the song is on the list
                if isinstance(csvReader.loc[csName, "Playcount"], np.int64):
                    # if there's exactly one instance of the current song
                    shaaPlaycount = str((csvReader.loc[csName, "Playcount"]).astype(int))
                    # takes the number of plays as a string

                elif isinstance(csvReader.loc[csName, "Playcount"], pd.Series):
                    # if there's more than one instance of the same song, calculates playcount for all instances
                    pcVar = csvReader.loc[csName, "Playcount"]
                    shaaPlaycount = str(pcVar.sum())
                    # finds total number of plays for all instances of current song, turns into string

                if isinstance(csvReader.loc[csName, "Total Time"], np.int64):
                    # if there's exactly one instance of the current song
                    shaaPlaytime = f"{( ( (csvReader.loc[csName, "Total Time"]) / 1000) / 60):,.1f}"
                    # finds total time played (min) for current song (milliseconds/1000 = seconds / 60 = minutes), turns into a formatted string

                elif isinstance(csvReader.loc[csName, "Total Time"], pd.Series):
                    # if there's more than one instance of the same song, calculates playtime for all instances
                    ttVar = csvReader.loc[csName, "Total Time"]
                    shaaPlaytime = f"{((ttVar.sum() / 1000 )/ 60):,.1f}"
                    # finds total time played (min) for all instances of current song (milliseconds/1000 = seconds / 60 = minutes), turns into a formatted string

            else:
                # in case the song has never been played before (or doesn't appear in the CSV)
                shaaPlaycount = "0"
                shaaPlaytime = "0"
                # makes the playcount and playtime for that song 0
        
            shaaTotalTime =  f"{( ( (csvReader["Total Time"].agg("sum")/1000) /60) /60):,.2f}"
            # counts total time (hours) for all songs (milliseconds/1000 = seconds / 60 = minutes / 60 = hours, then rounded), turns into a formatted string

            cppSongStuff = (shaaPlaycount + " " + songInfoFormatPlays + " " + songInfoSpacer + " " + shaaPlaytime + " " + songInfoFormatMins)
            # joins together the playcount and time
            # default appearance: " 1,234 plays x 5,678 minutes "

        else:
            # if not installed as an addon to Spotify Analyser, will not send numbers forward, rather just configured, set fields
            shaaPlaycount = shaalessPlaycount
            shaaPlaytime = shaalessPlaytime
            shaaTotalTime = shaalessTotalTime
            # gives them string values based on user configured input

            cppSongStuff = (shaaPlaycount + " " + songInfoFormatPlays + " " + songInfoSpacer + " " + shaaPlaytime + " " + songInfoFormatMins)
            # joins together the song information without Spotify Analyser
            # default appearance: " N/A plays x N/A minutes " , " Total Hours: N/A "


        ### songOrder splicing, need to set up a pre-check to see if it only contains 1, 2 or 3
        # may also need to check if the spacers are empty and only push empty spaces if not
        # in fact, just print one space by default (left side) and then add one to spacers if they're not empty

        ### Left Spacer ###

        if len(songNameSpacerL) >= 1:
            # if the left spacer has at least one character, adds a space after to ensure proper formatting
            cppSNSL = (songNameSpacerL + " ")
            # sets the "C++ Song Name Spacer Left" to have an extra space after

        elif len(songNameSpacerL) < 1:
            # the left spacer has nothing, ensures it doesn't print extra space
            cppSNSL = ""
            # sets the "C++ Song Name Spacer Left" to have nothing

        ### Right Spacer ### 

        if len(songNameSpacerR) >= 1:
            # if the right spacer has at least one character, adds a space after to ensure proper formatting
            cppSNSR = (songNameSpacerR + " ")
            # sets the "C++ Song Name Spacer Right" to have an extra space after

        elif len(songNameSpacerL) < 1:
            # the right spacer has nothing, ensures it doesn't print extra space
            cppSNSR = ""
            # sets the "C++ Song Name Spacer Right" to have nothing
        
        ### Song Order ###

        if len(songOrder) > 3:
            # more than 3 integers were given, falls back to a max of 3
            print(">3")
            # cppSongName = (csName + " " + songNameSpacerL + " " + csArtist + " " + songNameSpacerR + " " + csAlbum)

        elif len(songOrder) == 3:
            # 3 integers are given, need to make a for loop probably that takes all the 1s and spits out a song, then spacer, then next digit
            print("3")

        elif len(songOrder) == 2:
            # 2
            print("2")
        
        elif len(songOrder) == 1:
            # 1 integer was given, the order is just that digit
            print("1")
        
        elif len(songOrder) < 1:
            # none were given, defaults to default behavior
            cppSongName = (csName + " " + cppSNSL + csArtist + " " + cppSNSR +  csAlbum)

        # after that, need to add the pre and post-text if they're not empty

        cppSongName = (csName + " " + songNameSpacerL + " " + csArtist + " " + songNameSpacerR + " " + csAlbum)
        # joins together the song name, artist and album (with customisable spacers) for C++ (CPP) text file

        print(cppSongName)

        ### Total Hours ###

        cppSIFHS = (songInfoFormatHourSpacer).replace('"', '')
        # removes the quotation marks from the spacer (they are required to pass extra space through)

        cppHours = (songInfoFormatHours + cppSIFHS + shaaTotalTime)
        # creates a short string for total hours

        print(cppHours)

        ### Text File Writer ###

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

        with open("songData.txt", "w", encoding="utf-8") as txt:
            # opens the songData text file
            txt.write(cppFull)
            # writes the full song information to the text file, which is read by the C++ program and then sent to Discord RPC

        event.clear()
        # clears the event queue


currentSong = None
# makes the currentSong empty outside the looper so the loop can start and not make it "None" every time its run

def looper():
    # this loop checks if the song playing is the same as the previous update, does nothing if yes, updates the song to match if not
    info = main.current_playback()
    # picks up all the info Spotify sends in an update
    songName = (info.get("item")).get("name")
    # grabs the name of the currently playing song
    global currentSong
    if currentSong is None:
        # when the program first starts, the currentSong will be "None", this updates it
        currentSong = songName
        # since this only runs when the program first starts, calls the song updater right away
        event.set()
    songProg = (info.get("progress_ms"))
    songDur = (info.get("item")).get("duration_ms")
    # grabs both the current time and length of the song (in milliseconds)
    songLeft = ((songDur-songProg) / 1000)
    # calculates the time left on the song (in seconds)

    if currentSong == songName:
        # current song is the same as the last time
        print("the song is still the same for", songLeft, "seconds")
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
        print("new song - re-running")
        event.set()
        # starts the song status updater
        currentSong = songName
        # updates the current song to match
        time.sleep(3)
        # sleeps for a few seconds to let other parts work
        looper()
        # re-runs looper, which now has the new song name


### runs at script start:

songThread = threading.Thread(target=song, args=(pictureQueue,))
# creates the song thread
songThread.start()
# creates the song thread

picCyclerThread = Background(picCycleList, picCycleType, picCycleList, pictureQueue)
# creates the picture cycler

idWriter()
# runs the idWriter, which writes the ids.txt file

picCyclerThread.start()
# runs the picture cycler thread

looper()
# runs the looper, which manages the song refresh cycles
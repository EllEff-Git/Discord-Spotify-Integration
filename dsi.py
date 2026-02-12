import pandas as pd
import numpy as np
import os, time, configparser, spotipy
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

# sp_client_ID = Config.get("Required", "Spotify_Client_ID")
# sp_client_secret = Config.get("Required, Spotify_Client_Secret")
# sp_redirect = Config.get("Required", "Spotify_Redirect_URI")
shaalessPlaycount = shaalessPlaytime = shaalessTotalTime = Config.get("SHAA-Song-Info", "song_Info_Empty_Field")
smallURL = Config.get("URL", "small_URL")
songNameSpacerL = Config.get("Song-Styling", "song_Spacer_Left")
songNameSpacerR = Config.get("Song-Styling", "song_Spacer_Right")
songInfoSpacer = Config.get("SHAA-Song-Info", "song_Info_Spacer")
songInfoFormatPlays = Config.get("SHAA-Song-Info", "song_Info_Format_Plays")
songInfoFormatMins = Config.get("SHAA-Song-Info", "song_Info_Format_Mins")

# if you know what you're doing, you can further customise the look of the output below (lines 126 and beyond)



main = spotipy.Spotify(auth_manager = SpotifyOAuth(scope = "user-read-playback-state", client_id = sp_client_ID, client_secret = sp_client_secret, redirect_uri = sp_redirect))
# handles the authentication and user identification on start



def song():

    csFull = main.current_playback()
    # stores a huge dictionary containing all the information about current song
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

    # csProgressMin, csProgressSec = divmod(int(csFull.get("progress_ms")/1000),60)
    # stores track progress and converts to minutes:seconds (debug)
    # csDurationMin, csDurationSec = divmod(int(csShort.get("duration_ms")/1000),60)
    # stores track duration and converts to minutes:seconds (debug)

    # csImages = cs.get("images")
    # stores the info about all the images tied to the song
    # csAlbumCover = csImages[0].get("url")
    # stores the link to the album cover
    # not used for now, since you can't dynamically update Discord Rich Presence icons

    csLength = csShort.get("duration_ms")
    # stores the length of the song
    csProgress = int(csFull.get("progress_ms") / 1000)
    # stores the current progress of the song (in seconds)

    csUnixStart = csFull.get("timestamp")
    # stores the start time of the song
    csUnixEnd = csUnixStart + csLength
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
                # finds total time played (min) for current song (milliseconds/1000 = seconds / 60 = minutes), turns into string

            elif isinstance(csvReader.loc[csName, "Total Time"], pd.Series):
                # if there's more than one instance of the same song, calculates playtime for all instances
                ttVar = csvReader.loc[csName, "Total Time"]
                shaaPlaytime = f"{((ttVar.sum() / 1000 )/ 60):,.1f}"
                # finds total time played (min) for all instances of current song (milliseconds/1000 = seconds / 60 = minutes), turns into string

        else:
            # in case the song has never been played before (or doesn't appear in the CSV)
            shaaPlaycount = "0"
            shaaPlaytime = "0"
            # makes the playcount and playtime for that song 0
        
        shaaTotalTime =  f"{( ( (csvReader["Total Time"].agg("sum")/1000) /60) /60):,.2f}"

        # counts total time (hours) for all songs (milliseconds/1000 = seconds / 60 = minutes / 60 = hours, then rounded), turns into string

        cppSongStuff = (shaaPlaycount + " " + songInfoFormatPlays + " " + songInfoSpacer + " " + shaaPlaytime + " " + songInfoFormatMins)
        # joins together the playcount and time
        # default appearance: " 1,234 plays x 5,678 minutes "

    else:
        # if not installed as an addon to Spotify Analyser, will not send numbers forward, rather just empty fields (can be user-replaced with any valid string)
        shaaPlaycount = shaalessPlaycount
        shaaPlaytime = shaalessPlaytime
        shaaTotalTime = shaalessTotalTime
        cppSongStuff = (shaaPlaycount + " " + songInfoFormatPlays + " " + songInfoSpacer + " " + shaaPlaytime + " " + songInfoFormatMins)
        # joins together the song information without Spotify Analyser
        # default appearance: " N/A plays x N/A minutes " , " Total Hours: N/A "



    cppSongName = (csName + " " + songNameSpacerL + " " + csArtist + " " + songNameSpacerR + " " + csAlbum)
    # joins together the song name, artist and album (with customisable spacers) for C++ (CPP) text file

    cppHours = ("Total Hours: " + shaaTotalTime)
    # creates a short string for total hours

    print(cppSongName, "\n", cppSongStuff, "\n", cppHours, "\n", csURL, "\n", str(csUnixStart), "\n", str(csUnixEnd))

    cppFull = (
                "songName = " + cppSongName + "\n" + 
                "songStuff = " + cppSongStuff + "\n" +
                "LargeText = " + cppHours + "\n" +
                "SmallText = Spotify" + "\n" +
                "SpotifyURL = " + csURL + "\n" +
                "SmallURL = " + smallURL + "\n" +
                "UNIXstart = " + str(csUnixStart) + "\n" +
                "UNIXend = " + str(csUnixEnd)
                )

    with open("songData.txt", "w", encoding="utf-8") as txt:
        # opens the songData text file
        txt.write(cppFull)
        print(txt)
        # writes the full song information to the text file, which is read by the C++ program and then sent to Discord RPC
     
    # TESTING AREA: (used to print/debug)
    # print(csFull)
    # print(cppFull)
    # print("Song name: ", csName, ", Artist name: ", csArtist, ", Album name: ", csAlbum, ", Progress is at: ", csProgressMin,":","%02d" % (csProgressSec,), " out of ", csDurationMin,":","%02d" % (csDurationSec,), sep="")
    # print(shaaPlaycount, "times played", shaaPlaytime, "minutes listened to", shaaTotalTime, "hours listened to (total)")
    # print("song ending timestamp:", csUnix)



currentSong = None
# makes the currentSong empty outside the loop so the loop can start and not make it "None" every time its run

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
        song()
    songProg = (info.get("progress_ms"))
    songDur = (info.get("item")).get("duration_ms")
    # grabs both the current time and length of the song (in milliseconds)
    songLeft = ((songDur-songProg)/1000)
    # calculates the time left on the song (in seconds)

    if currentSong == songName:
        # current song is the same as the last time
        print("the song is still the same for", songLeft, "seconds")
        if songLeft > 10:
            time.sleep(10)
            # sleeps for 10 seconds
            looper()
        if songLeft <= 10:
            time.sleep(songLeft)
            # if the song has <10 seconds, doesn't wait 10 seconds
            looper()

    if currentSong != songName:
        # song is not the same as it was last time it was checked
        print("new song - re-running")
        song()
        # starts the song status updater
        currentSong = songName
        # updates the current song to match
        time.sleep(3)
        # sleeps for a few seconds to let other parts work
        looper()
        # re-runs looper, which now has the new song name



looper()
# once all the above stuff has processed, starts the looper (a few seconds after dsi.py load)
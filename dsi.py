import pandas as pd
import APItokens, os, time
import spotipy
from spotipy.oauth2 import SpotifyOAuth


###
# user input area V
####

sp_client_ID = APItokens.client_ID
# the "client ID" token inside Spotify Dashboard (replace with "PLACE CLIENT ID HERE")
sp_client_secret =  APItokens.client_secret 
# the "client secret" token inside Spotify Dashboard (replace with "PLACE CLIENT SECRET HERE")
sp_redirect = APItokens.redirect
# the URL for the Spotify redirect, also inside Spotify Dashboard (replace with "PLACE REDIRECT URL HERE")

disc_application = APItokens.discAppID
# discord client ID (replace with "PLACE DISCORD APPLICATION ID HERE")

###
# user input area ^
###



main = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-read-playback-state", client_id=sp_client_ID, client_secret=sp_client_secret, redirect_uri=sp_redirect))
# handles the authentication and user identification



# all this will be deleted and the "devDir" will be replaced by the mainDir's path below
devDir = "S:/Spotify Analyzer/Data/CSV/grouped.csv"
# the directory used during development (will be deleted)
mainDir = "../Data/CSV/grouped.csv"
# the directory used after installation (this addon installs into Spotify Analyzer/DSI/)



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
    # stores the info about the first artist
    # csArtist = csArtistRaw.get("name")
    # stores the artist name
    csAlbum = cs.get("name")
    # stores the album name

    csProgressMin, csProgressSec = divmod(int(csFull.get("progress_ms")/1000),60)
    # stores track progress and converts to minutes:seconds 
    csDurationMin, csDurationSec = divmod(int(csShort.get("duration_ms")/1000),60)
    # stores track duration and converts to minutes:seconds

    csImages = cs.get("images")
    # stores the info about all the images tied to the song
    csAlbumCover = csImages[0].get("url")
    # stores the link to the album cover
    # not used for now, since you can't dynamically update Discord Rich Presence icons

    csLength = int(csShort.get("duration_ms")/1000)
    # stores the length of the song (in seconds)
    csUnix = int(time.time()+csLength)
    # turns the length of the song into a UNIX timestamp
    # which is then passed to Discord as an "end timestamp", showing when the song ends



    if os.path.exists(devDir):
        # this is the addon part to Spotify (History) Analyser (SHA + addon = shaa)
        # this data is only entered to rich presence if used with SHA (and installed correctly)
        # checks if the CSV file exists to pull data from (requires one full run of SHA prior)
        csvReader = pd.read_csv(devDir, index_col=0)
        # opens the CSV file and uses column 0 as index (track names)
        shaaPlaycount = (csvReader.loc[csName, "Playcount"]).astype(int)
        # finds total number of plays for current song
        shaaPlaytime = round( ( (csvReader.loc[csName, "Total Time"]) / 1000) / 60)
        # finds total time played (min) for current song (milliseconds/1000 = seconds / 60 = minutes)
        shaaTotaltime = round( ( ( (csvReader["Total Time"].agg("sum")/1000) /60) /60) )
        # counts total time (h) for all songs (milliseconds/1000 = seconds / 60 = minutes / 60 = hours, then rounded)
    else:
        # None
        print("CSV file not found, additional functionality not enabled")


    # TESTING AREA: (used to print/debug)
    # print(csShort)
    print("Song name: ", csName, ", Artist name: ", csArtist, ", Album name: ", csAlbum, ", Progress is at: ", csProgressMin,":","%02d" % (csProgressSec,), " out of ", csDurationMin,":","%02d" % (csDurationSec,), sep="")
    print(shaaPlaycount, "times played", shaaPlaytime, "minutes listened to", shaaTotaltime, "hours listened to (total)")
    print("song ending timestamp:", csUnix)



currentSong = None
# makes the currentSong empty outside the loop so the loop can start and not make it "None" every time its run

def looper():
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


"""
something along the lines of:

[Listening to <song> by <artist>]
[total track playtime: <total>, track played <count> times.]
[total playtime on Spotify: <time> hours]
"""

# below is a chunk of code that Discord uses for rich presence

"""
static void UpdatePresence()
{
    DiscordRichPresence discordPresence;
    memset(&discordPresence, 0, sizeof(discordPresence));
    discordPresence.state = "Listening to";
    discordPresence.details = "Competitiveo";
    discordPresence.startTimestamp = 1507665886;
    discordPresence.endTimestamp = 1507665887;
    discordPresence.largeImageText = "Numbani";
    discordPresence.smallImageText = "Rogue - Level 100";
    discordPresence.partyMax = 5;
    discordPresence.joinSecret = "MTI4NzM0OjFpMmhuZToxMjMxMjM= ";
    Discord_UpdatePresence(&discordPresence);
}
"""
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

disc_client_ID = APItokens.discClient_ID
# discord client ID (replace with "PLACE DISCORD CLIENT ID HERE")
disc_client_secret = APItokens.discClient_secret
# discord client secret key (replace with "PLACE DISCORD SECRET KEY HERE")

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

    if os.path.exists(devDir):
        # this is the addon part to Spotify (History) Analyser (SHA + addon = shaa)
        # this data is only entered to rich presence if used with SHA
        # checks if the CSV file exists to pull data from)
        csvReader = pd.read_csv(devDir, index_col=0)
        # opens the CSV file and uses column 0 as index (track names)
        shaaPlaycount = int(csvReader.loc[csName, "Playcount"])
        # finds total number of plays for current song
        shaaPlaytime = round( ( (csvReader.loc[csName, "Total Time"]) / 1000) / 60)
        # finds total time played (min) for current song (milliseconds/1000 = seconds / 60 = minutes)
        shaaTotaltime = round( ( ( (csvReader["Total Time"].agg("sum")/1000) /60) /60) )
        # counts total time (h) for all songs (milliseconds/1000 = seconds / 60 = minutes / 60 = hours, then rounded)
    else:
        # None
        print("CSV file not found, additional functionality not enabled")

    discordPresence()
    # once everything else has run, calls discordPresence



    def discordPresence():
        # this function takes all the data from song() and pushes it to Discord
        # defined inside song() because it needs access to variables, but defined as its own function because idk honestly, could just be a part of song()
        print("Hello, you made it here! This does nothing, but it works!")



    # TESTING AREA: (used to print/debug)
    # print(csShort)
    print("Song name: ", csName, ", Artist name: ", csArtist, ", Album name: ", csAlbum, ", Progress is at: ", csProgressMin,":",csProgressSec, " out of ", csDurationMin,":",csDurationSec, ", Album cover: ", csAlbumCover, sep="")
    print(shaaPlaycount, shaaPlaytime, shaaTotaltime)



currentSong = None
# makes the currentSong empty outside the loop so the loop can start and not make it "None" every time its run

def looper():
    info = main.current_playback()
    # picks up all the info Spotify sends in an update
    songName = (info.get("item")).get("name")
    # grabs the name of the currently playing song
    global currentSong
    if currentSong is None:
        currentSong = songName
    # makes a loop that calls for a new song if the previous ends (more or less)
    songProg = (info.get("progress_ms"))
    songDur = (info.get("item")).get("duration_ms")
    # grabs both the current time of the song and the length
    songLeft = ((songDur-songProg)/1000)+1
    # grabs the time left on the song and adds 1 second (to allow for some headroom)

    if currentSong == songName:
        print("song is still same, sleeping for", songLeft, "seconds")
        time.sleep(songLeft)
        # puts the loop to sleep until the song ends, since there's no new information
        looper()
        # re-runs once the timer ends, now should have a new song

    if currentSong != songName:
        print("new song - re-running")
        song()
        # starts the song parser
        currentSong = songName
        # updates the current song
        time.sleep(5)
        # sleeps for a few seconds to let other parts work
        looper()
        # re-runs looper, which now has the new song name



looper()
# once all the above stuff has processed, starts the looper (on py load)



# once the spotify -> py stuff works, go to https://discord.com/developers/docs/activities/overview to see how to get from py -> discord

"""
something along the lines of:

[Listening to <song> by <artist>]
[total track playtime: <total>, track played <count> times.]
[total playtime on Spotify: <time> hours]


maybe in the future it could have its own GUI that determines what the data looks like, not sure
"""

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
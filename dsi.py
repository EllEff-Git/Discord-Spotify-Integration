import pandas as pd
import APItokens
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# to run, use: (including the &)
"""
& C:/Users/LP/AppData/Local/Programs/Python/Python314/python.exe "s:/Spotify Analyzer/DSI/dsi.py"
"""

###

scope = "user-read-playback-state"
# sets the scope for what information is being requested

sp_client_ID = APItokens.client_ID
# the "client ID" token inside Spotify Dashboard
sp_client_secret =  APItokens.client_secret 
# the "client secret" token inside Spotify Dashboard
sp_redirect = APItokens.redirect
# the URL for the Spotify token redirect

disc_client_ID = "x"
# discord client ID

###

main = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=sp_client_ID, client_secret=sp_client_secret, redirect_uri=sp_redirect))
# handles the authentication and user identification

def onSongChange():
    # songName.get
    # picks up the name of the current song
    devDir = "S:/Spotify Analyzer/Data/CSV/grouped.csv"
    # the directory used during development
    mainDir = "../Data/CSV/grouped.csv"
    # the directory used after installation (installs into Spotify Analyzer/DSI/)
    allTracks = pd.read_csv(devDir, 'r')
    # 
    # if allTracks(songName) exists:
    #    songName.playtime get


# every 5 seconds or so?
csFull = main.current_playback()
# returns a huge dictionary containing all the information about current song
# "cs" in the variables just stands for CurrentSong, which, while descriptive, made the later variables insanely long

csShort = csFull.get("item")
# takes the first part of the song's info (leaving out device info and various user states)
cs = csShort.get("album")
# takes a smaller part of the song's info (still contains a ton of extra)

csName = csShort.get("name")
# stores the name of the song (currently the name of the album)
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

# TESTING AREA: (used to print/debug)
# print(csShort)
print("Song name:", csName, ", Artist name:", csArtist, ", Album name:", csAlbum, ", Progress is at:", csProgressMin,":",csProgressSec, "out of", csDurationMin,":",csDurationSec, "Album cover:", csAlbumCover)


# tempSong = currentSong

# if currentSong != tempSong:
#    onSongChange()
# else:
#    None



# once the spotify -> py stuff works, go to https://discord.com/developers/docs/activities/overview to see how to get from py -> discord

# example return:
"""
{'device': {'id': '4b1a77568e47c1357c0548164d19fee305da43af', 'is_active': True, 'is_private_session': False, 'is_restricted': False, 'name': 'TASKSLAYER', 'supports_volume': True, 'type': 'Computer', 'volume_percent': 0}, 
'shuffle_state': True, 'smart_shuffle': False, 'repeat_state': 'context', 'is_playing': True, 'timestamp': 1770667401996, 
'context': {'external_urls': {'spotify': 'https://open.spotify.com/playlist/0z01MP5zevCgLTRRXZfngw'}, 'href': 'https://api.spotify.com/v1/playlists/0z01MP5zevCgLTRRXZfngw', 'type': 'playlist', 'uri': 'spotify:playlist:0z01MP5zevCgLTRRXZfngw'}, 
'progress_ms': 129059, 'item': {'album': {'album_type': 'single', 'artists': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/61GAisNXTGSK0ZKtPYIEEy'}, 'href': 'https://api.spotify.com/v1/artists/61GAisNXTGSK0ZKtPYIEEy', 'id': '61GAisNXTGSK0ZKtPYIEEy', 'name': 'Elizabeth Wong', 'type': 'artist', 'uri': 'spotify:artist:61GAisNXTGSK0ZKtPYIEEy'}], 
'available_markets': ['AR', 'AU', 'AT', 'BE', 'BO', 'BR', 'BG', 'CA', 'CL', 'CO', 'CR', 'CY', 'CZ', 'DK', 'DO', 'DE', 'EC', 'EE', 'SV', 'FI', 'FR', 'GR', 'GT', 'HN', 'HK', 'HU', 'IS', 'IE', 'IT', 'LV', 'LT', 'LU', 'MY', 'MT', 'MX', 'NL', 'NZ', 'NI', 'NO', 'PA', 'PY', 'PE', 'PH', 'PL', 'PT', 'SG', 'SK', 'ES', 'SE', 'CH', 'TW', 'TR', 'UY', 'US', 'GB', 'AD', 'LI', 'MC', 'ID', 'JP', 'TH', 'VN', 'RO', 'IL', 'ZA', 'SA', 'AE', 'BH', 'QA', 'OM', 'KW', 'EG', 'MA', 'DZ', 'TN', 'LB', 'JO', 'PS', 'IN', 'BY', 'KZ', 'MD', 'UA', 'AL', 'BA', 'HR', 'ME', 'MK', 'RS', 'SI', 'KR', 'BD', 'PK', 'LK', 'GH', 'KE', 'NG', 'TZ', 'UG', 'AG', 'AM', 'BS', 'BB', 'BZ', 'BT', 'BW', 'BF', 'CV', 'CW', 'DM', 'FJ', 'GM', 'GE', 'GD', 'GW', 'GY', 'HT', 'JM', 'KI', 'LS', 'LR', 'MW', 'MV', 'ML', 'MH', 'FM', 'NA', 'NR', 'NE', 'PW', 'PG', 'PR', 'WS', 'SM', 'ST', 'SN', 'SC', 'SL', 'SB', 'KN', 'LC', 'VC', 'SR', 'TL', 'TO', 'TT', 'TV', 'VU', 'AZ', 'BN', 'BI', 'KH', 'CM', 'TD', 'KM', 'GQ', 'SZ', 'GA', 'GN', 'KG', 'LA', 'MO', 'MR', 'MN', 'NP', 'RW', 'TG', 'UZ', 'ZW', 'BJ', 'MG', 'MU', 'MZ', 'AO', 'CI', 'DJ', 'ZM', 'CD', 'CG', 'IQ', 'LY', 'TJ', 'VE', 'ET', 'XK'], 
'external_urls': {'spotify': 'https://open.spotify.com/album/5dGtE202T3nGy1mIIZEcSE'}, 'href': 'https://api.spotify.com/v1/albums/5dGtE202T3nGy1mIIZEcSE', 'id': '5dGtE202T3nGy1mIIZEcSE', 'images': [{'height': 640, 'url': 'https://i.scdn.co/image/ab67616d0000b273171bd639d9fad3faeebefda0', 'width': 640}, {'height': 300, 'url': 'https://i.scdn.co/image/ab67616d00001e02171bd639d9fad3faeebefda0', 'width': 300}, {'height': 64, 'url': 'https://i.scdn.co/image/ab67616d00004851171bd639d9fad3faeebefda0', 'width': 64}], 'name': 'Kid I Used to Be.', 'release_date': '2019-10-11', 'release_date_precision': 'day', 'total_tracks': 1, 'type': 'album', 'uri': 'spotify:album:5dGtE202T3nGy1mIIZEcSE'}, 'artists': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/61GAisNXTGSK0ZKtPYIEEy'}, 'href': 'https://api.spotify.com/v1/artists/61GAisNXTGSK0ZKtPYIEEy', 'id': '61GAisNXTGSK0ZKtPYIEEy', 'name': 'Elizabeth Wong', 'type': 'artist', 'uri': 'spotify:artist:61GAisNXTGSK0ZKtPYIEEy'}], 'available_markets': ['AR', 'AU', 'AT', 'BE', 'BO', 'BR', 'BG', 'CA', 'CL', 'CO', 'CR', 'CY', 'CZ', 'DK', 'DO', 'DE', 'EC', 'EE', 'SV', 'FI', 'FR', 'GR', 'GT', 'HN', 'HK', 'HU', 'IS', 'IE', 'IT', 'LV', 'LT', 'LU', 'MY', 'MT', 'MX', 'NL', 'NZ', 'NI', 'NO', 'PA', 'PY', 'PE', 'PH', 'PL', 'PT', 'SG', 'SK', 'ES', 'SE', 'CH', 'TW', 'TR', 'UY', 'US', 'GB', 'AD', 'LI', 'MC', 'ID', 'JP', 'TH', 'VN', 'RO', 'IL', 'ZA', 'SA', 'AE', 'BH', 'QA', 'OM', 'KW', 'EG', 'MA', 'DZ', 'TN', 'LB', 'JO', 'PS', 'IN', 'BY', 'KZ', 'MD', 'UA', 'AL', 'BA', 'HR', 'ME', 'MK', 'RS', 'SI', 'KR', 'BD', 'PK', 'LK', 'GH', 'KE', 'NG', 'TZ', 'UG', 'AG', 'AM', 'BS', 'BB', 'BZ', 'BT', 'BW', 'BF', 'CV', 'CW', 'DM', 'FJ', 'GM', 'GE', 'GD', 'GW', 'GY', 'HT', 'JM', 'KI', 'LS', 'LR', 'MW', 'MV', 'ML', 'MH', 'FM', 'NA', 'NR', 'NE', 'PW', 'PG', 'PR', 'WS', 'SM', 'ST', 'SN', 'SC', 'SL', 'SB', 'KN', 'LC', 'VC', 'SR', 'TL', 'TO', 'TT', 'TV', 'VU', 'AZ', 'BN', 'BI', 'KH', 'CM', 'TD', 'KM', 'GQ', 'SZ', 'GA', 'GN', 'KG', 'LA', 'MO', 'MR', 'MN', 'NP', 'RW', 'TG', 'UZ', 'ZW', 'BJ', 'MG', 'MU', 'MZ', 'AO', 'CI', 'DJ', 'ZM', 'CD', 'CG', 'IQ', 'LY', 'TJ', 'VE', 'ET', 'XK'], 'disc_number': 1, 'duration_ms': 251050, 'explicit': False, 'external_ids': {'isrc': 'QZHN61982448'}, 'external_urls': {'spotify': 'https://open.spotify.com/track/6Cg2uCG1A1fm4j4B1or5n3'}, 'href': 'https://api.spotify.com/v1/tracks/6Cg2uCG1A1fm4j4B1or5n3', 'id': '6Cg2uCG1A1fm4j4B1or5n3', 'is_local': False, 'name': 'Kid I Used to Be.', 'popularity': 22, 'preview_url': None, 'track_number': 1, 'type': 'track', 'uri': 'spotify:track:6Cg2uCG1A1fm4j4B1or5n3'}, 'currently_playing_type': 'track', 'actions': {'disallows': {'resuming': True}}}
"""


"""
also, sort of unrelated to this project, but a richdiscordpresence tool that takes the data from this (grouped.csv)
then replaces the default discord spotify integration with mine

something along the lines of:

[Listening to <song> by <artist>]
[total track playtime: <total>, track played <count> times.]
[total playtime on Spotify: <time> hours]



requires python tool, Discord integration and Spotify API (which I have access to)

I guess it could be considered an "addon" for the analyzer, since it can't work on its own 
    (well it could, but what's the point of getting the spotify song and name when spotify/discord integration already does that)

basic idea:
while currentSong == storedSong:
    None
(some loop in the background checking for songname based on updates, hits an update to currentSong, breaking the ==, thus calling onSongRefresh())
else:
    onSongRefresh():
        get.songName
        data.get(fromCSV)
        writePresence
        storedSong = songName

and then update the song timer separately


maybe in the future it could have its own GUI that determines what the data looks like, not sure
"""
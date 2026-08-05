import pandas as pd
# Required for all the CSV parsing and data grabbing
import random, subprocess
# Required to choose random pictures and to start the C++ file
import os, sys, time, threading, queue, datetime
# Required for system information, background tasking and queueing
import spotipy, requests, json, logging
# Required for basic function of Spotify data requests and storing
from spotipy.oauth2 import SpotifyOAuth
# Required for authorizing with Spotify
from spotipy.exceptions import SpotifyException
# Required to check for exceptions (errors)
from collections import deque
# Required for "console-like" UI logging
import struct, psutil
# Required for C++ communication and management
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required for the main window
from flask import Flask
# Required for cross-communication between DSI and SBO



### Version ###



DSIver = "0.8.5.1101"
"""The program version (Y.M.DD.HHMM)"""



### Directory Grab ###



directory = None
"""The base directory of the program, where DSI.exe resides"""
iconPath = None
"""The path of the app icon png"""
splashPath = None
"""The path of the splash screen png"""
yellowStatusPath = None
"""The yellow status icon png path"""
redStatusPath = None
"""The red status icon png path"""
greenStatusPath = None
"""The green status icon png path"""


if getattr(sys, "frozen", False):
# since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    iconPath = os.path.join(sys._MEIPASS, "dsiIcon.png")
    splashPath = os.path.join(sys._MEIPASS, "dsiSplash.png")
    # reassigns the path variables accordingly
    yellowStatusPath = os.path.join(sys._MEIPASS, "dsiStatusYellow.png")
    redStatusPath = os.path.join(sys._MEIPASS, "dsiStatusRed.png")
    greenStatusPath = os.path.join(sys._MEIPASS, "dsiStatusGreen.png")
    # reassigns the status icon paths
else:
# if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    iconPath = os.path.join(directory, "icons", "dist", "dsiIcon.png")
    splashPath = os.path.join(directory, "icons", "dist", "dsiSplash.png")
    # reassigns the path variables accordingly
    yellowStatusPath = os.path.join(directory, "icons", "dist", "dsiStatusYellow.png")
    redStatusPath = os.path.join(directory, "icons", "dist", "dsiStatusRed.png")
    greenStatusPath = os.path.join(directory, "icons", "dist", "dsiStatusGreen.png")
    # reassigns the status icon paths

dataDir = os.path.join(directory, "Data")
# the Data folder directory

if not os.path.exists(dataDir):
# if there's no Data folder
    try:
    # tries
        os.mkdir(dataDir)
        # makes a Data directory
    except:
    # if it can't
        None
        # does nothing




### Config ###



functionConfigPath = os.path.join(directory, "Data", "functionConfig.json")
"""The DSI functionality config json file"""
functionConfigWin = os.path.join(directory, "Qt", "Func_Qt", "funcWindow.exe")
"""The DSI functionality configurator program/window"""

dsiConfigPath = os.path.join(directory, "Data", "config.json")
"""The DSI configuration json file"""
dsiConfigWindow = os.path.join(directory, "Qt", "DSI_Qt", "dsiWindow.exe")
"""The DSI configurator program/window"""

secretConfigPath = os.path.join(directory, "Data", "secretConfig.json")
"""The main configuration file, contains client secret info"""

shaaConfigPath = os.path.join(directory, "Data", "shaaConfig.json")
"""The SHAA x DSI configuration json file"""

statsPath = os.path.join(directory, "Data", "statistics.json")
"""The DSI statistics file path"""

### Token/ID ###

spCache = os.path.join(directory, "Data", "spotifycache.json")
"""The directory where the spotify cache (token) sits in"""
idDir = os.path.join(directory, "Discord", "ids.txt")
"""The directory where ids.txt should/will live (inside DSI/Discord/ids.txt)"""

### Song Details ###

noURIpath = os.path.join(directory, "Data", "URIlist.json")
"""The path to where URIlist (unfound URIs) should/will live"""
uriPath = os.path.join(directory, "Data", "URImap.json")
"""The path to where URImap.json should/will live (inside DSI/Data/URImap.json)"""
blacklistPath = os.path.join(directory, "Data", "blacklist.json")
"""The path to where the song blacklist.json should/will live (inside DSI/Data/blacklist.json)"""

### Spotify History Analyser (Addon) ###

SHAAdir = os.path.join(directory, "..", "Data", "CSV", "dsi.csv")
"""The directory where the CSV is (relative to .exe, it's one folder up and then two deep into Spotify Analyser main folder)"""
timeDir = os.path.join(directory, "..", "Data", "CSV", "totalTimes.txt")
"""The directory where the totalTimes.txt file is"""

### Customisation ###

picDir = os.path.join(directory, "pictureList.txt")
"""The directory where pictureList.txt lives (inside DSI/pictureList.txt)"""

### C++ Locations ###

cppExe = "DSIdiscord.exe"
"""The name of the C++ exe file"""
cppPath = os.path.join(directory, "Discord", cppExe)
"""The full path to the C++ exe"""
cppDir = os.path.dirname(cppPath) 
"""The directory the C++ exe lives in"""

### GitHub URL ###

gURL = "https://api.github.com/repos/EllEff-Git/Discord-Spotify-Integration/tags"
"""The GitHub URL to make update check requests to"""



### Global Variables ###



functionConfig = {}
"""The config file for functionality"""
secretConfig = {}
"""The config file with client IDs and such"""
jsonConfig = {}
"""The config file with DSI customisation config"""
shaaConfig = {}
"""The config file specifically for SHA(A) features"""
blacklist = {}
"""The blacklist of songs from blacklist.json"""
uriList = None
"""The list of URIs from uriList.json"""

sp_client_ID = None
"""Spotify Client ID, string"""
sp_client_secret = None
"""Spotify Client Secret, string"""
sp_redirect = None
"""Spotify redirect URL, string"""
dc_app_ID = None
"""Discord Application ID, string"""

skipConfigWindow = False
"""Whether to skip the configuration window or not, bool"""
consoleLength = 25
"""The stored line amount for the pseudo-console, int"""
hostData = True
"""Whether to host the parsed Spotify data locally, bool"""
refreshTime = 10.0
"""Program update cycle interval time, float/int"""

enablePause = True
"""The "paused on" text enabler, boolean"""
pauseStateText = "Paused on:"
"""The string used for paused status, string"""
enableUpdates = True
"""Whether to print updates, boolean"""
enableErrors = True
"""Whether to print errors, boolean"""
enableMapping = True
"""Whether to enable the URI mapping functionality, boolean"""
timestampStyle = "Uptime"
"""The timestamp format for system prints, string (System Time, Uptime, Off)"""

startTime = int(datetime.datetime.now().timestamp())
"""The program start time in UNIX"""

smallURL = ""
"""The small picture URL, string"""
spotifyURL = "Track"
"""The type of large image URL to use, string of: (Track, Artist, Album, Playlist)"""

songNameSpacerL = "\u227a"
"""Spacer between 1st and 2nd field, string"""
songNameSpacerR = "\u227b"
"""Spacer between 2nd and 3rd field, string"""

preText = ""
"""Optional text before the first field, string"""
postText = ""
"""Optional text after the last field, string"""
enableSong = True
"""Song's state, boolean"""
enableArtist = True
"""Artist's state, boolean"""
enableAlbum = True
"""Album's state, boolean"""
albumFallback = "An album"
"""The text to fall back to in case the album gets dropped, string"""

picCycleList = "Spotify"
"""Pictures for large image, option (File, Spotify)"""
picCycleTime = 10
"""Time to wait between picture cycling, int/string (minutes/Song)"""
picCycleType = "Random"
"""Type of cycling to perform on pictures, string (Random, Sequence, Once, None)"""

smallPic = ""
"""Name/URL of small picture, string"""
hoverText = ""
"""Text to show on small picture hover, string"""

songInfoField1 = "Track"
"""First state field type, string (Track, Total)"""
songInfoField2 = 0
"""Second state field type, int"""
# 0-1 is minutes (track first), 2-3 is hours, 4-5 is seconds
shaaFallbackTotal = False
"""Whether to fall back to total numbers, boolean"""
shaaFallback = "Total"
"""The fallback type (total or string)"""
shaaInfoDetails = "Hours"
"""Details field type, string (Hours, Minutes, Seconds, Volume, Repeat, Shuffle, Cycle, custom)"""
songInfoFormatPlays = "plays"
"""Text format of the first field, string"""
songInfoSpacer = "※"
"""Spacer to place between first and second field, string"""
songInfoFormatMins = "minutes"
"""Text format of the second field, string"""
songInfoFallback = "total"
"""Fallback text for missing song data for both state fields, string"""
songInfoFormatTextFirst = True
"""The order the number and text fall to (boolean, True = text first)"""
songInfoFormatDetails = "Total Hours"
"""Text format of the details field, string"""
songInfoFormatDetailsSpacer = ":"
"""Spacer to place between details field data and string, string"""
songInfoDetailsDoubleSpace = False
"""Whether to add space on either side of the spacer, boolean"""
dsiShoutout = False
"""Whether to add a shoutout to DSI at the end of the details section, boolean"""
# uses "default" options (most of these shouldn't get accessed if SHAA isn't enabled anyway, but some do)


# Detail Field Options #
detailOptions = ["hours", "minutes", "seconds", "volume", "repeat", "shuffle", "cycle",
                 "Hours", "Minutes", "Seconds", "Volume", "Repeat", "Shuffle", "Cycle"]
"""All possible choices for detail field (hours) that doesn't include custom string"""

# URL List #
spotifyURLlist = ["track", "Track", "album", "Album", "artist", "Artist", "playlist", "Playlist"]
"""A list of all the possible options for spotify URL types"""

# Picture Cycling Methods #
pictureBehaviorList = ["random", "sequence", "once", "none"]
"""A list of all the possible options for picture cycling types"""

pauseStart = None
"""Makes a starter variable that stores a timestamp when a pause occurs"""

currentInfo = None
"""Song info dictionary"""

cppFull = None
"""Currently playing song dict sent to the C++ program"""

blacklistInfo = None
"""Dictionary containing the current song's info"""

currentURI = None
"""The current song's track URI"""

cppLargeImage = ""
"""Makes an empty image string, in case it fails to make first load"""

pauseUpdated = False
"""A check to see if the pause state has been registered properly"""

totalHours = totalMinutes = totalSeconds = 0
"""Variables for total hours, minutes and seconds"""

oldCount = trackCounter = 0
"""Variables to track 'song IDs'"""

noPlayCounter = 0
"""Variable to check how many times in a row playing state has been off (nothing playing)"""

cycleCount = 0
"""Variable to check the cycle count of hours, minutes and seconds (if enabled)"""

timePlayed = 0
"""Variable to store total playtime during DSI uptime"""

lastPlayStamp = 0
"""Variable to store timestamp for playtime calculation"""

csName = csArtist = ""
"""The current song/artist name"""

dsiShoutoutStr = "// Data by DSI"
"""A shoutout string to DSI, disabled by default in config"""

disableShaa = False
"""Boolean to check whether SHA(A) functionality should be disabled or not"""

cppProgram = None
"""The C++ program subprocess (gets defined in its function)"""

cppFails = 0
"""How many asset failures have been detected from the C++ subprocess"""



### Flask (Network Host) ###

flaskLog = logging.getLogger("werkzeug")
# targets the Flask logger
flaskLog.setLevel(logging.ERROR)
# sets the logging level to error-only (ignores harmless prints)

localSPData = Flask(__name__)
# creates a locally-run network app to host Spotify data at

@localSPData.route("/spData")
def spData():
# Spotify data page
    return json.dumps(cppFull)
    # turns the C++ dictionary into a json format, sends to the /spData page

@localSPData.route("/version")
def version():
# Spotify data version page
    return json.dumps(cppFull.get("Track ID", 0))
    # turns the single key value into a page (that SBO can check easier)

def runSPData():
# Spotify data page runner
    localSPData.run(host="127.0.0.1", port=41809)
    # runs the Flask app on the local network (127.0.0.1:41809/spData)



### Main Window ###



class DSI_MainWindow(QMainWindow):
    """The main window class"""
    labelSwap = pyqtSignal(str, int)
    # a pyQt signal to swap the label
    readyTag = pyqtSignal()
    # a signal to signal the readiness state of the window
    blacklistTag = pyqtSignal(str, str, str)
    # a signal to call the song blacklist manager
    detailTag = pyqtSignal(str, int)
    # a signal to call the song detail manager
    programReady = pyqtSignal()
    # a signal to signal the readiness state of the program

    def __init__(self):
        super().__init__()



    ### Init / Basic ###

        self.version = DSIver
        # stores the version in self
        self.mainIcon = iconPath
        # the program's main icon
        self.yellowStatus = QIcon(yellowStatusPath)
        self.redStatus = QIcon(redStatusPath)
        self.greenStatus = QIcon(greenStatusPath)
        # the status icons
        self.programName = f"DSI Loader"
        # stores the program name

        self.windowSizeX = max(900, int(startApp.primaryScreen().size().width() / 2))
        self.windowSizeY = max(800, int(startApp.primaryScreen().size().height() / 2))
        # base window sizes (uses the larger of the two, 900/800 or ~50% of the monitor's width/height)

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(self.windowSizeX, self.windowSizeY))
        # the window size minimums

    ### UI Element Base ###

        self.container = QWidget()
        # a container to hold elements
        self.mainLayout = QGridLayout()
        # new grid layout to put elements into
        self.mainLayout.setSpacing(25)
        # sets spacing of 25px between elements

        self.mainLayout.setRowMinimumHeight(0, 50)
        self.mainLayout.setRowMinimumHeight(1, 150)
        self.mainLayout.setRowMinimumHeight(2, 100)
        self.mainLayout.setRowMinimumHeight(3, 50)
        self.mainLayout.setRowMinimumHeight(4, 50)
        self.mainLayout.setRowMinimumHeight(5, 50)
        # sets the minimum height for rows

        self.mainLayout.setColumnMinimumWidth(0, 150)
        self.mainLayout.setColumnMinimumWidth(1, 200)
        self.mainLayout.setColumnMinimumWidth(2, 300)
        self.mainLayout.setColumnMinimumWidth(3, 200)
        self.mainLayout.setColumnMinimumWidth(4, 150)
        # sets the minimum width for columns

        self.mainLayout.setColumnStretch(0, 0)
        self.mainLayout.setColumnStretch(1, 1)
        self.mainLayout.setColumnStretch(2, 1)
        self.mainLayout.setColumnStretch(3, 1)
        self.mainLayout.setColumnStretch(4, 0)
        # allows columns 1, 2 and 3 (center) to stretch

        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setRowStretch(2, 1)
        # allows rows 1 (console) and 2 (center) to stretch

        self.container.setLayout(self.mainLayout)
        # sets the container to use layout

    ### Main Label ("Console") ###

        self.consoleScroll = QScrollArea()
        # a console-like scrollable area
        self.consoleScroll.setWidgetResizable(True)
        # allows the widget to be resized
        self.consoleScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # disables the scroll bar
        self.consoleScroll.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        # allows the scroll area to resize on window expand
        self.consoleScroll.setMinimumSize(400, 525)
        # sets a minimum height
        self.consoleScroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                padding-top: 15px;
                padding-bottom: 15px;
            }
        """)
        # sets a custom style to add some space between the edges and the text
        self.mainLayout.addWidget(self.consoleScroll, 1, 1, 3, 3)
        # adds the label to the main layout (top middle)

        self.mainLabel = QLabel()
        # a label to hold the main information about current process
        self.mainLabel.setText("DSI starter window")
        # initial text
        self.mainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        # centers the label to the bottom
        self.mainLabel.setWordWrap(True)
        # makes the text wrap if it's too wide
        self.mainLabel.setMinimumWidth(400)
        # sets a minimum size for the label
        self.consoleScroll.setWidget(self.mainLabel)
        # sets the console to use the mainLabel

    ### Exit Button ###

        self.bottomButtonLayout = QGridLayout()
        # a layout for the bottom middle buttons
        self.mainLayout.addLayout(self.bottomButtonLayout, 5, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout to the bottom middle of the main layout

        self.exitButton = QPushButton("Exit")
        # a button to exit the program
        self.exitButton.setToolTip("Close the program and save progress")
        # tooltip
        self.exitButton.setFixedSize(150, 50)
        # sets size
        self.bottomButtonLayout.addWidget(self.exitButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the button to the button layout (bottom middle)

    ### Re-run DiscordRPC Button ###

        self.rerunRPCbutton = QPushButton("Re-run DiscordRPC")
        # a button to restart the Discord RPC
        self.rerunRPCbutton.setToolTip("Re-run the Discord RPC subprocess again")
        # tooltip
        self.rerunRPCbutton.setFixedSize(150, 50)
        # sets size
        self.rerunRPCbutton.hide()
        # hides the button by default
        self.rerunRPCbutton.clicked.connect(lambda: self.restarter("C++", True))
        # pressing the button -> runs the restarter function
        self.bottomButtonLayout.addWidget(self.rerunRPCbutton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the button to the button layout (top middle)
        

    ### Hideable/Showable Elements ###

        self.userInputField = QLineEdit()
        # creates a new QLineEdit for user to input into
        self.userInputField.setToolTip("Write here")
        # tooltip
        self.userInputField.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # alings to center
        self.userInputField.setFixedSize(300, 30)
        # sets size
        self.mainLayout.addWidget(self.userInputField, 2, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the qline to layout (middle middle)
        self.userInputField.hide()
        # hides by default

        self.submitButton = QPushButton("Submit")
        # makes a new button to save the iput
        self.submitButton.setToolTip("Enter text")
        # tooltip
        self.submitButton.setFixedSize(60, 35)
        # sets size
        self.mainLayout.addWidget(self.submitButton, 2, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds the button to layout (middle right)
        self.submitButton.hide()
        # hides by default

    ### Version Tag ###

        self.versionTag = QLabel(f"DSI v{self.version}\n ")
        # label for the semantic version
        self.versionTag.setToolTip("Current DSI version")
        # tooltip
        self.versionTag.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        # aligns the text itself to the left
        self.versionTag.setOpenExternalLinks(True)
        # allows opening links (in case of new update)
        self.mainLayout.addWidget(self.versionTag, 5, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds to the bottom left corner

    ### Song Detail Elements ###

        self.songDetailLayout = QGridLayout()
        # the layout all the song detail items sit in

        self.mainLayout.addLayout(self.songDetailLayout, 4, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds the layout to the 2nd to bottom row in the left column

        self.songCounter = QLabel()
        # details label
        self.songCounter.setMaximumSize(150, 60)
        # sets max size
        self.songCounter.setToolTip("Current DSI session stats")
        # tooltip
        self.songCounter.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # aligns left
        self.songDetailLayout.addWidget(self.songCounter, 0, 0)
        # adds the counter

        self.globalSongCounter = QLabel()
        # global details label
        self.globalSongCounter.setMaximumSize(150, 60)
        # sets max size
        self.globalSongCounter.setToolTip("Global DSI stats")
        # tooltip
        self.globalSongCounter.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # aligns left
        self.songDetailLayout.addWidget(self.globalSongCounter, 0, 0)
        # adds the global counter
        self.globalSongCounter.hide()
        # hides the stats by default

        self.globalStats = statsWriter("Load")
        # loads the old statistics from file, stores in variable

        globalTimePlayed = self.globalStats["Time Played"]
        # loads the total time played
        globalTimeString = f"{(globalTimePlayed / 3600):,.1f}"
        # splits the seconds into hours

        globalAvgDuration = self.globalStats["Avg Duration"]
        # grabs the average duration seconds from variable

        if globalAvgDuration >= 60:
        # if the average duration is over a minute
            gAvgMin, gAvgSec = divmod(globalAvgDuration, 60)
            # divides the seconds to minutes and seconds
            globalAvgString = f"{gAvgMin}:{gAvgSec:02d}"
            # forms a string from the two
        else:
        # if the average duration is less than a minute
            globalAvgString = f"0:{globalAvgDuration:02d}"
            # forms a string from just the duration, leading 0 added
        
        globalSongsPlayed = self.globalStats["Songs Played"]
        # grabs the songs played count from global stats variable
        
        self.globalSongCounter.setText(f"Songs played: {globalSongsPlayed:,.0f}\nTime played: {globalTimeString} hours\nAverage duration: {globalAvgString}")
        # sets the counter text to match

    ### Function Elements ###

        self.functionLayout = QGridLayout()
        # a layout that holds functional buttons
        self.mainLayout.addLayout(self.functionLayout, 4, 4, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout to the main in the mirrored spot bottom row, right column

        self.swapStatsButton = QPushButton("Swap Statistics")
        # a button to swap between global and session statistics
        self.swapStatsButton.setFixedSize(125, 40)
        # sets fixed size
        self.swapStatsButton.setToolTip("Swap statistics view between global and session")
        # tooltip

        self.swapStatsButton.clicked.connect(lambda: self.songDetails("Swap"))
        # connects the button click to the details swapping
        self.swapStatsButton.hide()
        # hides the button on start

        self.debugInfoButton = QPushButton("Song Details")
        # a button to display API-level details about the song
        self.debugInfoButton.setFixedSize(125, 40)
        # sets fixed size
        self.debugInfoButton.setToolTip("Display details about the currently playing song")
        # tooltip

        self.debugInfoButton.clicked.connect(self.songDetailsWindow)
        # connects the button click to the detail display
        self.debugInfoButton.hide()
        # hides the button on start

        self.functionLayout.addWidget(self.swapStatsButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.functionLayout.addWidget(self.debugInfoButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the buttons

    ### Status Elements ###

        self.statusLayout = QGridLayout()
        # a layout that holds the status elements

        self.mainLayout.addLayout(self.statusLayout, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout to the main in the middle right position

        self.spotifyStatusIcon = QPushButton()
        # the Spotify API status indicator
        self.spotifyStatusIcon.setIcon(self.greenStatus)
        self.spotifyStatusIcon.setIconSize(QSize(16,16))
        # forms the icon
        self.spotifyStatusIcon.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
        """)
        # makes the button part invisible
        self.spotifyStatusIcon.setFixedSize(18, 18)
        # sets the max size of the button slightly larger than the icon
        self.statusLayout.addWidget(self.spotifyStatusIcon, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds the icon to the top left corner

        self.spotifyStatusLabel = QLabel("Spotify API")
        # the Spotify API status label
        self.spotifyStatusLabel.setToolTip("Spotify API status indicator")
        # tooltip
        self.spotifyStatusLabel.setMinimumSize(70, 30)
        # sets minimum size
        self.statusLayout.addWidget(self.spotifyStatusLabel, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the label next to its icon (right side)

        self.discordStatusIcon = QPushButton()
        # the Discord API status indicator
        self.discordStatusIcon.setIcon(self.greenStatus)
        self.discordStatusIcon.setIconSize(QSize(16,16))
        # forms the icon
        self.discordStatusIcon.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
        """)
        # makes the button part invisible
        self.discordStatusIcon.setFixedSize(18, 18)
        # sets the max size of the button slightly larger than the icon
        self.statusLayout.addWidget(self.discordStatusIcon, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds the icon to the bottom left corner

        self.discordStatusLabel = QLabel("Discord API")
        # the Discord API status label
        self.discordStatusLabel.setToolTip("Discord API status indicator")
        # tooltip
        self.discordStatusLabel.setMinimumSize(70, 30)
        # sets minimum size
        self.statusLayout.addWidget(self.discordStatusLabel, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the label next to its icon (right side)

        self.spotifyStatusIcon.hide()
        self.spotifyStatusLabel.hide()
        self.discordStatusIcon.hide()
        self.discordStatusLabel.hide()
        # hides the statuses until they become useful
    
    ### Blacklist Elements ###

        self.blacklistLayout = QGridLayout()
        # the layout all the blacklist items sit in

        self.blacklistButtonLayout = QGridLayout()
        # the layout the buttons sit in

        self.mainLayout.addLayout(self.blacklistLayout, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout to the center of the top row

        self.blacklistLayout.addLayout(self.blacklistButtonLayout, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the button layout under the song name

        self.blacklistSpacer = QSpacerItem(250, 25)
        # a spacer to push the song name down a bit
        self.blacklistLayout.addItem(self.blacklistSpacer, 0, 0)
        # adds the spacer above the label

        self.blacklistSongName = QLabel()
        # the label that stores the song name
        self.blacklistSongName.setMinimumSize(400, 50)
        # sets a size so it doesn't fidget
        self.blacklistSongName.setWordWrap(True)
        # allows text to wrap if it's too long
        self.blacklistSongName.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns the text to the center of the field
        self.blacklistLayout.addWidget(self.blacklistSongName, 1, 0)
        # adds the song name to the middle
        self.blacklistSongName.setToolTip("Currently playing song")
        # tooltip

        self.blacklistAddButton = QPushButton("Blacklist")
        # the button that adds a song to the blacklist
        self.blacklistButtonLayout.addWidget(self.blacklistAddButton, 0, 1)
        # adds the add button to the right side
        self.blacklistAddButton.setToolTip("Blacklist current song")
        # tooltip
        self.blacklistAddButton.setMinimumSize(60, 30)
        # sets minimum size

        self.blacklistRemoveButton = QPushButton("Unblacklist")
        # the button that removes a song from the blacklist
        self.blacklistButtonLayout.addWidget(self.blacklistRemoveButton, 0, 1)
        # adds the remove button to the right side
        self.blacklistRemoveButton.setToolTip("Remove the current song from blacklist")
        # tooltip
        self.blacklistRemoveButton.setMinimumSize(60, 30)
        # sets minimum size

        self.blacklistStarButton = QPushButton("Favorite")
        # the button that favorites a song
        self.blacklistButtonLayout.addWidget(self.blacklistStarButton, 0, 0)
        # adds the star button to the left side
        self.blacklistStarButton.setToolTip("Favorite the current song")
        # tooltip
        self.blacklistStarButton.setMinimumSize(60, 30)
        # sets minimum size

        self.blacklistUnstarButton = QPushButton("Unfavorite")
        # the button that unfavorites a song
        self.blacklistButtonLayout.addWidget(self.blacklistUnstarButton, 0, 0)
        # adds the unstar button to the left side
        self.blacklistUnstarButton.setToolTip("Unfavorite the current song")
        # tooltip
        self.blacklistUnstarButton.setMinimumSize(60, 30)
        # sets minimum size

    ### Intermediary ###

        self.setCentralWidget(self.container)
        # sets the container to fill the window
        self.labelSwap.connect(self.changeLabel)
        # connects the label swap signal to the change label function
        self.readyTag.connect(startStart)
        # connects the ready tag to the program logic starter
        self.programReady.connect(self.programReadyState)
        # connects the program ready tag to the program ready state function
        self.exitButton.clicked.connect(lambda: self.stopper("Shut Down"))
        # connects the exit button to the program stopping function

    ### Blacklist Intermediary ###

        self.blacklistTag.connect(self.blacklistManager)
        # connects the blacklist tag to the blacklist manager
        self.blacklistAddButton.clicked.connect(lambda: self.blacklistIntermediary("Add"))
        # connects the add button to the intermediary function with command add
        self.blacklistRemoveButton.clicked.connect(lambda: self.blacklistIntermediary("Remove"))
        # connects the remove button to the intermediary function with command remove
        self.blacklistStarButton.clicked.connect(lambda: self.blacklistIntermediary("Star"))
        # connects the star button to the intermediary function with command star
        self.blacklistUnstarButton.clicked.connect(lambda: self.blacklistIntermediary("Unstar"))
        # connects the unstar button to the intermediary function with command unstar

    ### Line "Storage" ###

        self.multiLabel = False
        # sets the multi-string label to false to begin with
        self.lines = deque(maxlen = consoleLength)
        # creates a "deque" to hold lines (strings), to form a "pseudo-console"

    ### Run Arguments ###

        self.checkUpdate()
        # runs the GitHub update check

        self.blacklistButtons("init")
        # calls the blacklist button decider with init command (hides all buttons)

        self.requiredItemCheck()
        # runs the required items function to check IDs


### Update Checker ###

    def checkUpdate(self):
        """Function that checks if there's a new version of the program"""

        updateAvailable = 0
        # update check, defaults to 0
        # 0 = no update, 1 = update, 2 = program newer than github

        try:
        # tries to get tags
            gitTags = requests.get(
                gURL,
                headers={"User-Agent": "DSI"},
                timeout=5)
            # the request to get the github tags

            if gitTags.status_code == 200:
            # 200 is all good
                tags = gitTags.json()
                # grabs the json dictionary

                latestTagRaw = str(tags[0]["name"])
                # grabs the 0th element's name (latest)
                latestTag = latestTagRaw.replace("v", "").strip()
                # strips the v(ersion) identifier, cleans up
                latestList = latestTag.split(".")
                # splits the latest tag into a list of date elements (year num, month, day, hour/min)
                currentList= self.version.split(".")
                # splits the current tag into a list of date elements

                if latestList[0] == currentList[0]:
                # if the year elements are the same
                    if latestList[1] == currentList[1]:
                    # if the month elements are the same
                        if latestList[2] == currentList[2]:
                        # if the day elements are the same
                            if latestList[3] == currentList[3]:
                            # if the hour elements are the same
                                updateAvailable = 0
                                # sets to 0 (no update)
                            elif latestList[3] > currentList[3]:
                            # if the latest is newer than current
                                updateAvailable = 1
                                # sets the boolean to True
                            else:
                            # current is newer than latest
                                updateAvailable = 2
                                # sets the check to 2
                        elif latestList[0] > currentList[0]:
                        # if the latest is newer than current
                            updateAvailable = 1
                            # sets the boolean to True
                        else:
                        # current is newer than latest
                            updateAvailable = 2
                            # sets the check to 2
                    elif latestList[1] > currentList[1]:
                    # if the latest is newer than current
                        updateAvailable = 1
                        # sets the boolean to True
                    else:
                    # current is newer than latest
                        updateAvailable = 2
                        # sets the check to 2
                elif latestList[0] > currentList[0]:
                # if the latest is newer than current
                    updateAvailable = 1
                    # sets the boolean to True
                else:
                # current is newer than latest
                    updateAvailable = 2
                    # sets the check to 2

                if updateAvailable == 1:
                # if there's a newer version (higher number)
                    latestURL = "https://github.com/EllEff-Git/Discord-Spotify-Integration/releases/latest"
                    # the URL to set
                    self.versionTag.setText(
                        f'DSI v{self.version}<br>'
                        f'Update available: '
                        f'<a href="{latestURL}">'
                        f'{latestTagRaw}'
                        f'</a>'
                    )
                    # updates text to include a prompt + link to the newest update
                elif updateAvailable == 2:
                # if the current is higher than the latest github release (test build)
                    self.versionTag.setText(f"DSI v{self.version}\nBleeding Edge!")
                    # you should never see this, this is a testing tag
                else:
                # if the version == latest
                    self.versionTag.setText(f"DSI v{self.version}\nLatest")
                    # updates text
            else:
            # status code is not 200 (error, something else)
                self.versionTag.setText(f"DSI v{self.version}\nUpdate check failed")
                # error prompt
        except:
        # didn't go through at all
            self.versionTag.setText(f"DSI v{self.version}\nUpdate check failed")
            # error prompt

### Label Changer ###

    def changeLabel(self, text: str, msgType: int):
        """Function to change the passed label"""
        if timestampStyle != "off":
        # ensures the option isn't off or empty
            time = (self.Time() + "\n")
        # stores the time string with a spacer
        else:
        # if it is
            time = ""
            # stores empty string

        if msgType == 0:
        # type 0 is "all ok"
            None
            # doesn't do anything to the message
        elif msgType == 1:
        # type 1 is "required"
            text = f"{time}{text}"
            # adds the timestamp (if enabled)
        elif msgType == 2 or msgType == 3:
        # type 2 is "error", 3 is "song-related"
            text = f"\n{time}{text}"
            # adds a new line before
        elif msgType == 4:
        # type 4 is critical error
            text = f"\n\nCRITICAL ERROR:\n{time}{text}\n\n"
            # adds a lot of space to ensure attention

        if self.multiLabel:
        # if the boolean for multi-labeling (several lines at once) is enabled (the program has reached startup)
            self.lines.append(text)
            # adds the line to the deque of lines
            fullString = ("\n".join(self.lines))
            # joins the lines together by newlines
            self.mainLabel.setText(f"{fullString}")
            # sets the text to match
        else:
        # if the boolean is off
            self.mainLabel.setText(f"{text}")
            # sets the passed label's text to the passed text string

        QTimer.singleShot(500, self.autoScroll)
        # runs the autoscroller after half a second to let the text sit

### Icon Changer ###

    def iconChanger(self, widget: str, status: str):
        """A function to change the status icons"""
        if status == "Green":
        # green status = green icon
            icon = self.greenStatus
            # sets the green status icon as active
        elif status == "Yellow":
        # yellow status = yellow icon
            icon = self.yellowStatus
            # sets the yellow status icon as active
        elif status == "Red":
            icon = self.redStatus
            # sets the red status icon as active

        if widget == "Spotify":
        # if the widget in question is the Spotify API icon
            self.spotifyStatusIcon.setIcon(icon)
            # sets the Spotify API status icon to match
        elif widget == "Discord":
        # if the widget in question is the Discord API icon
            self.discordStatusIcon.setIcon(icon)
            # sets the Discord API status icon to match

### Song Details ###

    def songDetails(self, action:str = None):
        """A function to manage the song detail statistics (duration, averages...)"""
        global timePlayed, lastPlayStamp
        # global -> local

        timeNow = int(time.time())
        # stores the current UNIX timestamp
        timePlayed += int(timeNow - lastPlayStamp)
        # adds the amount of time between the last update and the current time
        lastPlayStamp = timeNow
        # sets the stamp to match current time (next time there'll be a difference)

        if trackCounter > 1:
        # if it's not the first song
            avgDuration = int(timePlayed / (trackCounter - 1))
            # calculates the average playback time of songs (in seconds)
        else:
        # if it is
            avgDuration = int(timePlayed)
            # just uses the time played

        if avgDuration >= 60:
        # if the average duration is over a minute
            avgMin, avgSec = divmod(avgDuration, 60)
            # divides the seconds to minutes and seconds
            avgString = f"{avgMin}:{avgSec:02d}"
            # forms a string from the two
        else:
        # if the average duration is less than a minute
            avgString = f"0:{avgDuration:02d}"
            # forms a string from just the duration, leading 0 added

        if timePlayed >= 3600:
        # if the time played exceeds 60 minutes (3600 seconds)
            if timePlayed >= 3960:
            # if the time exceeds 1.1 hours (3600 + 360)
                formatTimePlayed = f"{float(timePlayed / 3600):,.1f} hours"
                # formats the time played from seconds to hours (1 decimal point)
            else:
            # if it's between 1 hour and 1.1 hours (uses singular form)
                formatTimePlayed = f"1 hour"
                # same thing, but with no plural
        elif timePlayed < 119:
        # if the time is under 2 minutes
            formatTimePlayed = f"1 minute"
            # sets preset string
        else:
        # if the time doesn't exceed an hour
            formatTimePlayed = f"{int(timePlayed / 60)} minutes"
            # formats the time played from seconds to minutes

        self.songCounter.setText(f"Songs played: {trackCounter:,.0f}\nTime played: {formatTimePlayed}\nAverage duration: {avgString}")
        # sets the counter text to match

        if action == "Swap":
        # if the action is to swap the counters from session to global
            if self.songCounter.isVisible():
            # if the song counter (session) is visible
                self.songCounter.hide()
                self.globalSongCounter.show()
                # swaps them around
            else:
            # if it's not visible
                self.globalSongCounter.hide()
                self.songCounter.show()
                # swaps them around (opposite)



### Song Details Window ###

    def songDetailsWindow(self):
        """A function to display a small window containing song details"""

        info = QDialog(self)
        # makes a dialog window
        info.setWindowTitle(f"Details for {cppFull["Song Raw"]}")
        # sets the window title based on currently variable-stored song
        info.resize(400, 120)
        # window size

        infoText = (f"Song: {cppFull["Song Raw"]} by {cppFull["Artist"]}\n"
        f"Album: {cppFull["Album"]}\n"
        f"Spotify URI: {cppFull["URI"]}\n"
        f"Statistics: {cppFull["Playcount"]} plays, {cppFull["Playtime"]} minutes")
        # makes a text field with details about the current song

        details = QPlainTextEdit(info)
        # makes the field of text inside the info window (easy to copy from)
        details.setReadOnly(True)
        # read-only
        details.setPlainText(infoText)
        # sets the song details in the text field

        detailWindowLayout = QVBoxLayout(info)
        # adds a layout to the window
        detailWindowLayout.addWidget(details)
        # adds the text field

        info.exec()
        # executes (shows)



### Auto-Scroll ###

    def autoScroll(self):
        """A function to scroll the 'console' to the bottom"""

        scroller = self.consoleScroll.verticalScrollBar()
        # definition
        scroller.setValue(scroller.maximum())
        # uses the max value (pushes to bottom)

### Blacklist Manager ###

    def blacklistManager(self, action:str, track:str, uri:str):
        """A function to manage the blacklist of songs"""

        if action == "New Song":
        # if the action is to check a new song (song changed)
            if uri in blacklist:
            # if the passed URI exists in the blacklist
                status = blacklist[uri]["status"]
                # grabs the stored "status" of the uri (starred, blacklisted)
            else:
            # if the URI doesn't exist in the blacklist
                status = "none"
                # sets the status to none

            try:
            # tries to grab the artist
                artist = csArtist
                # grabs the artist name from the global variable
            except:
            # if it fails (sometimes Spotify gives some empty data)
                artist = "An Artist"
                # preset string

            self.blacklistSongName.setText(f"Currently playing:\n{track} by {artist}")
            # sets the current song name to the track

        elif action == "Remove" or action == "Unstar":
        # if the action is to remove the song from the blacklist or unfavorite it
            blacklist[uri] = {"status":"none"}
            # sets the blacklist entry for the URI to none
            status = "none"
            # sets the status to none, too
            if action == "Remove":
            # if the action is to unblacklist
                self.labelSwap.emit(f"Removed {track} from blacklist", 3)
                # user update
            else:
            # if it's not (then it's unstar)
                self.labelSwap.emit(f"Removed {track} from favorites", 3)
                # user update

        elif action == "Add":
        # if the action is to add the song to the blacklist
            blacklist[uri] = {"status":"blacklisted"}
            # sets the blacklist entry for the URI to blacklisted
            status = "blacklisted"
            # sets the status to blacklisted, too
            self.labelSwap.emit(f"Blacklisted {track}", 3)
            # user update

        elif action == "Star":
        # if the action is to favorite the song
            whitelistManager("Add")
            # calls the "whitelistManager" (same blacklist, just for starred items, because there's some limitations)
            status = "starred"
            # sets the status to blacklisted, too

        self.blacklistButtons(status)
        # calls the blacklist button manager to hide/show the relevant buttons for the song

### Blacklist Intermediary ###

    def blacklistIntermediary(self, action:str):
        """A function that grabs the song name and URI to pass to manager"""
        
        songName = csName
        # grabs the current text from the currently playing song (name)
        songURI = currentURI
        # grabs the global value of the current URI

        self.blacklistManager(action, songName, songURI)
        # calls the manager with the passed action, song name and URI

### Blacklist Button Visibility ###

    def blacklistButtons(self, status: str):
        """A function to show/hide buttons based on the context"""
        self.blacklistAddButton.hide()
        self.blacklistRemoveButton.hide()
        self.blacklistStarButton.hide()
        self.blacklistUnstarButton.hide()
        # when called, hides the elements first

        if status == "blacklisted":
        # if the song is already in the list of blacklisted songs
            self.blacklistRemoveButton.show()
            # enables the button to remove the song from the blacklist
            self.blacklistStarButton.show()
            # enables the star button

        elif status == "none":
        # if the song has no status
            self.blacklistAddButton.show()
            # shows the blacklist add button
            self.blacklistStarButton.show()
            # shows the star button

        elif status == "starred":
        # if the song is starred
            self.blacklistAddButton.show()
            # shows the blacklist add button
            self.blacklistUnstarButton.show()
            # shows the unstar button

        elif status == "init":
        # if the status is init, just means it's running on startup
            self.blacklistSongName.hide()
            # hides the song name field, too

### Blacklist Writer ###

    def blacklistWriter(self):
        """A function to write the blacklist of songs to file"""
        global blacklist
        # global -> local

        with open(blacklistPath, "w", encoding="utf-8") as blkList:
        # opens the blacklist file in write mode
            json.dump(blacklist, blkList, indent=3)
            # dumps the blacklist to file
        
        self.labelSwap.emit("Blacklist file updated!", 3)
        # user update

### Program Closer ###

    def stopper(self, severity: str):
        """A function to close the program gracefully, saving progress"""
        global blacklist, uriList
        # global -> local

        self.blacklistButtons("init")
        # calls the button manager with init (hides all)

        self.labelSwap.emit("Saving session details...", 3)
        # user update

        self.blacklistWriter()
        # calls the blacklist writer to save the blacklist
        uriWriter(uriList)
        # calls the URI writer with the current list of URIs to save it
        statsWriter("Save")
        # calls the statistics writer with Save

        if severity == "Shut Down":
        # if the passed severity is to shut down everything (otherwise this can be used as a "quicksave" function)

            self.labelSwap.emit("Shutting down...", 3)
            # user update

            cppThreadEvent.set()
            # tells the cppThread to stop
            if cppThread.is_alive():
            # checks if the thread is alive
                try:
                # tries to wait for the end
                    self.labelSwap.emit("Waiting for the Discord component to shut down...", 3)
                    # user update
                    while cppThread.is_alive():
                    # while the C++ thread is still active
                        for attempt in range(25):
                        # tries 25 times (5 seconds)
                            cppThread.join(timeout=0.2)
                            # waits 0.2 seconds per attempt to check if the thread is dead already 
                            startApp.processEvents()
                            # lets the window keep going
                        break
                        # if it goes over the attempts, breaks
                except RuntimeError:
                # if it fails
                    pass
                    # moves on

            songThreadEvent.set()
            # tells the song thread to stop
            if songThread.is_alive():
            # checks if the thread is alive
                try:
                    songThread.join(timeout=1)
                    # waits for the thread to close
                except RuntimeError:
                # if it fails
                    pass
                    # moves on

            self.close()
            # closes the window
            startApp.quit()
            # quits the application
            raise SystemExit
            # stops everything

### Program Component Restarter ###

    def restarter(self, function: str, status: bool):
        """A function to restart specific functions in case they fail"""

        if function == "C++":
        # if the passed function is the C++ thread 
            if cppThread.is_alive():
            # checks if the thread is still alive
                cppThreadEvent.set()
                # stops it by setting the flag
                cppThread.join()
                # waits for the thread to stop
            if status:
            # if the bool is True, and it's asking to restart (not just turn off)
                cppThread.start()
                # starts the thread
                self.rerunRPCbutton.hide()
                # ensures the RPC button is hidden, since the program is running
        
        elif function == "Song":
        # if the passed function is the Song thread
            if songThread.is_alive():
            # checks if the thread is still alive
                songThreadEvent.set()
                # stops it by setting the flag
                songThread.join()
                # waits for the thread to stop
            if status:
            # if the bool is True, and it's asking to restart (not just turn off)
                songThread.start()
                # starts the thread

### Required Stuff Grab ###

    def requiredItemCheck(self):
        """A function to check required items (IDs, etc)"""
        global secretConfig
        # global -> local

        self.show()
        # shows the main program window

        if os.path.exists(secretConfigPath):
        # if the "secret" configuration file does exist
            try:
            # tries to read the config file (try because it could fail)
                with open(secretConfigPath, "r", encoding="utf-8") as scrtCfg:
                # opens the SHAA config
                    secretConfig = json.load(scrtCfg)
                    # stores the loaded config
                    self.requiredItemGrab()
                    # calls the next stage
            except:
            # if the file can't be found/opened
                self.requiredItemsFail(2)
                # calls the fail function to reconstruct
        else:
        # if the file doesn't exist
            self.requiredItemsFail(1)
            # calls the fail function to reconstruct

    def requiredItemGrab(self):
        """A function to grab and push the required items, when they're found"""
        global sp_client_ID, sp_client_secret, sp_redirect, dc_app_ID
        # global -> local

        try:
        # tries to grab the IDs and such
            sp_client_ID = secretConfig["Spotify_Client_ID"]
            sp_client_secret = secretConfig["Spotify_Client_Secret"]
            sp_redirect = secretConfig["Spotify_Redirect_URI"]
            dc_app_ID = secretConfig["Discord_Application_ID"]
            # updates all the global variables
            self.labelSwap.emit("All required items loaded successfully, proceeding...", 0)
            # user update
            self.configRun()
            # moves to next stage
        except:
        # if it fails (something's wrong with the file/input)
            self.requiredItemsFail(2)
            # calls the fail function to reconstruct

    def requiredItemsFail(self, state):
        """A function to handle missing required items (re-input)"""
        global secretConfig, sp_client_ID, sp_client_secret, sp_redirect, dc_app_ID
        # global -> local

        if state == 1:
        # state 1 is no file exists (first time or deleted file)
            self.labelSwap.emit("No required config found, please enter required information:", 0)
            # user inform

            sp_client_ID = self.requiredItemInput("sp_Client_ID")
            secretConfig["Spotify_Client_ID"] = sp_client_ID
            # stores the client ID 

            sp_client_secret = self.requiredItemInput("sp_client_secret")
            secretConfig["Spotify_Client_Secret"] = sp_client_secret
            # stores the client secret

            sp_redirect = self.requiredItemInput("sp_redirect")
            secretConfig["Spotify_Redirect_URI"] = sp_redirect
            # stores the redirect URL

            dc_app_ID = self.requiredItemInput("dc_app_ID")
            secretConfig["Discord_Application_ID"] = dc_app_ID
            # stores the discord application ID

            # calls the required item input to construct a UI with input, stores return
            
        elif state == 2:
        # state 2 is the file has an issue, but exists (missing info?)
            try:
            # tries to read the config file (try because it could fail)
                with open(secretConfigPath, "r", encoding="utf-8") as scrtCfg:
                # opens the SHAA config
                    secretConfig = json.load(scrtCfg)
                    # stores the loaded config
            except:
            # if it can't open the file
                None
                # does nothing, because the map remains empty

            try:
            # tries to grab the item from stored config
                sp_client_ID = secretConfig["Spotify_Client_ID"]
            except:
            # if it can't
                sp_client_ID = self.requiredItemInput("sp_Client_ID")
                # calls the input field to grab a new one instead
                secretConfig["Spotify_Client_ID"] = sp_client_ID
                # stores the client ID 
            try:
            # tries to grab the item from stored config
                sp_client_secret = secretConfig["Spotify_Client_Secret"]
            except:
                sp_client_secret = self.requiredItemInput("sp_client_secret")
                # calls the input field to grab a new one instead
                secretConfig["Spotify_Client_Secret"] = sp_client_secret
                # stores the client secret
            try:
            # tries to grab the item from stored config
                sp_redirect = secretConfig["Spotify_Redirect_URI"]
            except:
                sp_redirect = self.requiredItemInput("sp_redirect")
                # calls the input field to grab a new one instead
                secretConfig["Spotify_Redirect_URI"] = sp_redirect
                # stores the redirect URL

            try:
            # tries to grab the item from stored config
                dc_app_ID = secretConfig["Discord_Application_ID"]
            except:
                dc_app_ID = self.requiredItemInput("dc_app_ID")
                # calls the input field to grab a new one instead
                secretConfig["Discord_Application_ID"] = dc_app_ID
                # stores the discord application ID

        self.userInputField.hide()
        self.submitButton.hide()
        # hides the button and input field once done

        with open(secretConfigPath, "w", encoding="utf-8") as scrtCfg:
        # opens the secret config/makes new one
            json.dump(secretConfig, scrtCfg, indent=3)
            # saves the config to file

        self.labelSwap.emit("Required items stored successfully, proceeding...", 0)
        # user update

        self.configRun()
        # moves to next stage

    def requiredItemInput(self, field):
        """Function to prompt user for a required item"""

        self.userInputField.setText("")
        # clears the text

        if field == "sp_Client_ID":
        # if the requested field is spotify client id
            fieldString = "Spotify Client ID"
            # forms a user-readable string

        elif field == "sp_client_secret":
        # if the requested field is
            fieldString = "Spotify Client Secret"
            # forms a user-readable string

        elif field == "sp_redirect":
        # if the requested field is
            fieldString = "Spotify Redirect URI"
            # forms a user-readable string

        elif field == "dc_app_ID":
        # if the requested field is discord app id
            fieldString = "Discord Application ID"
            # forms a user-readable string

        self.labelSwap.emit(f"Please enter your {fieldString}", 1)
        # sets the label to request for the passed info

        self.userInputField.show()
        # unhides the input field
        self.userInputField.setPlaceholderText(fieldString)
        # sets the field string to be placeholder (background) text for the input
        self.submitButton.show()
        # shows the submit button

        inputLoop = QEventLoop()
        # creates a pyqt event loop
        self.submitButton.clicked.connect(inputLoop.quit)
        # connects the submit button to stop the loop
        inputLoop.exec()
        # runs until the button is pressed

        userInputTemp = self.inputGrabber()
        # calls the input grabber to get the text from the input field
        userInput = userInputTemp.strip()
        # removes potential whitespace at start/end

        if userInput == "" or userInput == None:
        # if the returned user input field is empty
            self.labelSwap.emit(f"{fieldString} can't be empty", 2)
            # user inform
        else:
        # if there's something
            return userInput
            # returns to calling function

    def inputGrabber(self):
        """Function to grab the user input field text and return it"""
        return self.userInputField.text()
        # just grabs the text from the user input field and returns it

### UI Class -> Config ###

    def configRun(self): 
        """Function to run the configuration window(s)"""
        global functionConfig, jsonConfig, shaaConfig, disableShaa, skipConfigWindow
        # global -> local

        if os.path.exists(functionConfigPath):
        # if the functionality-related config exists
            self.labelSwap.emit("Found functionality configuration, reading...", 0)
            # user update
            try:
            # tries to open the json file
                with open(functionConfigPath, "r", encoding="utf-8") as fncCfg:
                # opens the config file in read mode
                    functionConfig = json.load(fncCfg)
                    # stores the loaded json file as functionConfig
            except Exception as err:
            # if there's an error
                self.labelSwap.emit(f"Error reading the configuration file: {err}", 2)
                # user inform            
            try:
            # tries to read the config
                skipCfgWin = functionConfig.get("disableCfgWin", False)
                # whether to prompt user with config window or not, boolean
                if skipCfgWin:
                # if the boolean is True
                    self.labelSwap.emit("Configuration found and skipping is enabled, proceeding...", 0)
                    # user update
            except:
            # if it can't be read
                skipCfgWin = False
                # sets to true if it can't be grabbed
                self.labelSwap.emit("Could not skip config...", 2)
                # user update
        else:
        # if the config file doesn't exist
            skipCfgWin = False
            # sets the config to false

        if not skipCfgWin:
        # if the file doesn't exist or config needs to be rechecked
            self.hide()
            # hides the mainWindow (otherwise appears frozen)
            mainConfig = subprocess.run([functionConfigWin], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            # runs the functionality configurator (as blocking), continues task once it's done writing config
            if not mainConfig.returncode == 1:
            # checks if the return code isn't 1 (0 is bad, 1 is good)
                self.show()
                # re-shows itself
                self.labelSwap.emit(f"Configuration complete, proceeding...", 0)
                # sends the return code

        if os.path.exists(dsiConfigPath):
        # checks if the config already exists (not first time) and the skipping is enabled
            self.labelSwap.emit("Found customisation configuration, reading...", 0)
            # user update
            try:
            # tries to open the json file
                with open(dsiConfigPath, "r", encoding="utf-8") as jsCfg:
                # opens the config file in read mode
                    jsonConfig = json.load(jsCfg)
                    # stores the loaded json file as jsonConfig
            except Exception as err:
            # if there's an error
                self.labelSwap.emit(f"Error reading the configuration file: {err}", 2)
                # user inform
        else:
        # if the dsi configuration doesn't exist
            self.hide()
            # hides the mainWindow (otherwise appears frozen)
            dsiConfig = subprocess.run([dsiConfigWindow], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            # runs the dsi configurator (as blocking), continues task once it's done writing config
            if not dsiConfig.returncode == 1:
            # checks if the return code isn't 1 (0 is bad, 1 is good)
                self.show()
                # re-shows itself
                self.labelSwap.emit(f"Customisation configuration complete, proceeding...", 0)
                # sends the return code

        if os.path.exists(shaaConfigPath):
        # if the shaa configuration file does exist
            try:
            # tries to read the SHAA config file (try because it's not necessary, can be skipped)
                with open(shaaConfigPath, "r", encoding="utf-8") as shaaCfg:
                # opens the SHAA config
                    shaaConfig = json.load(shaaCfg)
                    # stores the loaded 
                    disableShaa = False
                    # keeps shaa enabled
                    self.labelSwap.emit("SHAA successfully detected, enabling SHAA...", 0)
                    # user update
            except:
            # if the file can't be opened
                disableShaa = True
                # disables SHAA-related functions
                self.labelSwap.emit("SHAA not installed (successfully), skipping...", 0)
                # user update
        else:
        # if the file doesn't exist
            disableShaa = True
            # disables SHAA-related functions
            self.labelSwap.emit("SHAA not installed, skipping...", 0)
            # user update

        QTimer.singleShot(1500, self.mainConfigLoad)
        # runs the next stage

### Config Load ###
    
    def mainConfigLoad(self):
        """Function that loads and stores the config options"""
        global refreshTime, enablePause, pauseStateText, enableUpdates, enableErrors
        global enableMapping, timestampStyle, startTime, consoleLength, hostData
        # global -> local

        refreshTime = functionConfig.get("refreshTime", 10.0)
        # grabs the refresh time from config
        try:
        # tries to
            refreshTime = float(refreshTime)
            # turns the time into a float
            if refreshTime < 3.0:
            # if the refresh time is set too low
                refreshTime = 3
                # overrides to safe minimum of 3s  
        except:
        # if it fails
            refreshTime = 10.0
            # fallback value of 10.0

        enablePause = jsonConfig.get("enablePause", True)
        pauseStateText = jsonConfig.get("pauseText", "Paused on:")
        enableUpdates = functionConfig.get("printUpdates", True)
        enableErrors = functionConfig.get("printErrors", True)
        enableMapping = functionConfig.get("enableURI", True)
        timestampStyle = functionConfig.get("clockStyle", "Uptime")
        consoleLength = functionConfig.get("consoleLength", 25)
        hostData = functionConfig.get("hostData", True)
        # loads all options from configs

        self.labelSwap.emit("Main configuration loaded, proceeding...", 0)
        # user update
        QTimer.singleShot(1500, self.customConfigLoad)
        # runs the next stage

    def customConfigLoad(self):
        """Function that loads and stores the customisation config options"""
        global smallURL, spotifyURL, songNameSpacerL, songNameSpacerR, preText, postText, enableSong, enableArtist, enableAlbum, albumFallback, picCycleList
        # global -> local

        smallURL = jsonConfig.get("smallPicURL", None)
        if smallURL is None:
        # if the smallURL is empty
            smallURL = "https://github.com/EllEff-Git/Discord-Spotify-Integration"
            # shameless plug <3 (only applies if there's no defined URL)
        spotifyURL = jsonConfig.get("spotifyURLType", "Track")
        songNameSpacerL = jsonConfig.get("spacerL", "\u227a")
        songNameSpacerR = jsonConfig.get("spacerR", "\u227b")
        preText = jsonConfig.get("preText", "")
        postText = jsonConfig.get("postText", "")
        enableSong = jsonConfig.get("enableSong", True)
        enableArtist = jsonConfig.get("enableArtist", True)
        enableAlbum = jsonConfig.get("enableAlbum", True)
        albumFallback = jsonConfig.get("albumFallback", "A playlist")
        picCycleList = jsonConfig.get("pictureCycleType", "Spotify")
        # grabs each option from config, loads into global var

        self.labelSwap.emit("Customisation configurations loaded, proceeding...", 0)
        # user update
        QTimer.singleShot(1500, self.finalConfigLoad)
        # runs the next stage

    def finalConfigLoad(self):
        """Function that loads the last part of the config"""
        global picCycleList, picCycleTime, picCycleType, smallPic, hoverText

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
                self.labelSwap.emit("Picture list loaded from file", 0)
                # user update
        else:
        # if the list is on Spotify (or empty), doesn't modify it
            None

        picCycleTime = jsonConfig.get("pictureCycleTime", 10)
        try:
        # tries to turn the time into minutes (ensures integer type, multiplies by 60)
            picCycleTime = (int(picCycleTime) * 60)
        except:
        # if it can't, leaves it alone (should be the case when it's set to "Song")
            None

        picCycleType = jsonConfig.get("pictureCycleBehavior", "Random")
        smallPic = jsonConfig.get("smallPic", "")
        hoverText = jsonConfig.get("smallPicHover", "Spotify")
        # loads last settings

        QTimer.singleShot(500, self.shaaConfigLoad)
        # calls the shaa config loader

### SHAA Config Load ###

    def shaaConfigLoad(self):
        """Function to load and store the SHAA config options"""
        global songInfoField1, songInfoField2, shaaFallbackTotal, shaaFallback, shaaInfoDetails, songInfoFallback
        global songInfoFormatPlays, songInfoSpacer, songInfoFormatMins, songInfoFormatTextFirst, songInfoFormatDetails
        global songInfoFormatDetailsSpacer, songInfoDetailsDoubleSpace, dsiShoutout
        # a lot of global -> local

        if not disableShaa:
        # if the SHAA-related stuff isn't disabled

            songInfoField1 = shaaConfig.get("songInfoField1", "Track")
            songInfoField2 = shaaConfig.get("songInfoField2", 0)
            shaaFallbackTotal = shaaConfig.get("songInfoFallbackTotal", True)
            if shaaFallbackTotal:
            # if the fallback total usage is enabled
                shaaFallback = "Total"
                # sets the string to "Total"
            else:
                shaaFallback = shaaConfig.get("songInfoFallbackText", "")
                # gets the custom string from the shaa config

            shaaInfoDetails = shaaConfig.get("songInfoDetails", "Cycle")
            if shaaInfoDetails == "Custom":
            # if the details field is set to custom
                shaaInfoDetails = shaaConfig.get("songInfoDetailsCustomText", "")
                # uses the custom string from the config
                songInfoFallback = ""
                # uses empty string (custom string defined above)
            else:
            # if the field isn't custom, uses "total" as an additional string
                songInfoFallback = "total"

            songInfoFormatDetails = shaaConfig.get("songInfoDetailsText", "Total Hours")
            songInfoFormatPlays = shaaConfig.get("songInfoFormatPlays", "plays")
            songInfoSpacer = shaaConfig.get("songInfoFormatSpacer", "\u203b")
            songInfoFormatMins = shaaConfig.get("songInfoFormatMins", "minutes")
            songInfoFormatTextFirst = shaaConfig.get("songInfoDetailsTextFirst", True)
            songInfoFormatDetailsSpacer = shaaConfig.get("songInfoDetailsSpacer", ":")
            songInfoDetailsDoubleSpace = shaaConfig.get("songInfoDetailsDoubleSpace", False)
            dsiShoutout = shaaConfig.get("dsiShoutout", True)
            # grabs everything from config

        else:
        # if the disableShaa is set to True
            None
            # does nothing, because those settings are already set above

        QTimer.singleShot(1500, self.updateWarning)
        # calls the next stage (warnings regarding missing debug)

### Update Prints ###

    def updateWarning(self):
        if not enableUpdates:
        # if console printing is disabled in config
            self.labelSwap.emit("Update logging disabled in config", 0)
            # user update
            QTimer.singleShot(1000, self.errorWarning)
            # calls the error warning function
        else:
            self.errorWarning()
            # calls the error warning function

### Error Prints ###

    def errorWarning(self):
        if not enableErrors:
        # if error printing is disabled in config
            self.labelSwap.emit("Error logging disabled in config", 0)
            # user update
            QTimer.singleShot(1500, self.idWriter)
            # calls the next stage (id writer)
        else:
            self.idWriter()
            # calls the next stage (id writer)

### Time String ###

    def Time(self):
        """Function that returns the time formatted"""
        if timestampStyle == "Uptime":
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
            # the uptime of the program, format of HH:MM:SS
            return (uptimeStr + " ")
            # shortens the call to system uptime, adds empty space

        elif timestampStyle == "System Time":
        # if the config option is set to clock
            return (datetime.datetime.now().strftime("%H:%M:%S") + " ")
            # shortens the call to current system timestamp, adds empty space

        else:
        # if the config option is set to something else, reads as off (thus doesn't add anything)
            return ""
        
### ID Writer ###

    def idWriter(self):
        """Function for writing the ids.txt file"""
        # these are things the C++ program uses "statically" (they can't change during operation)
        with open(idDir, "w", encoding="utf-8") as txt:
        # opens the ids text file
            content = ("Discord Application ID = " + dc_app_ID + "\n" 
                    + "Small Image Filename = " + smallPic + "\n" 
                    + "Album Fallback = " + albumFallback)
            # makes a string from the relevant config options
            txt.write(content)
            # writes the config to file
            if enableUpdates:
            # if updates are enabled
                self.labelSwap.emit("Updated ID file for Discord...", 0)
            # writes the string to ids.txt at program launch

        if not disableShaa:
        # if SHAA compat isn't disabled
            QTimer.singleShot(2000, self.timeGrabber)
            # calls the next stage (timeGrabber)
        else:
            QTimer.singleShot(1000, self.readyStateReadier)
            # skips timeGrabber

### Total Time Grabber ###

    def timeGrabber(self):
        """Function that grabs the total time counts from totalTimes.txt file"""
        global totalHours, totalMinutes, totalSeconds, disableShaa
        # global -> local
        self.labelSwap.emit("Grabbing total times from file...", 0)
        # user update

        if os.path.isfile(timeDir):
        # checks if the totalTimes.txt file exists
            with open(timeDir, "r") as times:
            # if yes, opens the file
                totalTimes = times.readlines()
                # stores the total times from the file
                counter = 0
                # keeps a counter to check line number
                for line in totalTimes:
                # checks all lines in the file
                    if "=" in line:
                    # if "=" is present in the line
                        x, number = line.split("= ", 1)
                        # strips and splits the line, stores both sides
                        if counter == 0:
                            totalHours = number.strip()
                        elif counter == 1:
                            totalMinutes = number.strip()
                        elif counter == 2:
                            totalSeconds = number.strip()
                        # checks line number and saves the appropriate variable 
                        counter += 1
                        # adds 1 to move to next variable next cycle
                try:
                # tries to convert the strings to floats
                    totalHours = float(totalHours)
                    totalMinutes = float(totalMinutes)
                    totalSeconds = float(totalSeconds)
                    # turns the strings into floats
                    totalHours = (f"{totalHours:,.2f}")
                    totalMinutes = (f"{totalMinutes:,.0f}")
                    totalSeconds = (f"{totalSeconds:,.0f}")
                    # turns the floats into formatted strings (2 decimal points for hours, 0 for the other two)
                    if enableUpdates:
                    # if updates are enabled
                        self.labelSwap.emit(f"Times saved: {totalHours} hours = {totalMinutes} minutes = {totalSeconds} seconds", 0)
                        # prints the total times at start
                except:
                # if the float conversion fails for some reason
                    self.labelSwap.emit(f"Error reading totalTimes.txt file - total times not set...", 2)
                    # user update on error
                    disableShaa = True
                    # disables SHAA functionality (can't access files)

            times.close()
            # closes the file
        else:
        # if the file for SHA doesn't exist
            if not disableShaa:
            # if SHAA isn't disabled
                self.labelSwap.emit("Could not find totalTimes.txt file, please ensure proper SHAA installation...", 2)
                # there's already a print informing about non-SHAA installation later
                disableShaa = True
                # disables SHAA functionality (can't access files)

        QTimer.singleShot(2500, self.readyStateReadier)
        # calls the next stage 

### Ready State Setter ###

    def readyStateReadier(self):
        """Function that finalizes the window class' progress"""
        self.multiLabel = True
        # sets the boolean to true, allowing further "prints" to utilise more than 1 line of output
        self.lines = deque(maxlen = consoleLength)
        # redefines the line variable again with the correct console length from config

        self.setWindowTitle(f"Discord Spotify Integration")
        # sets a new title (starter -> real)

        self.userInputField.deleteLater()
        self.submitButton.deleteLater()
        # deletes the now useless buttons

        self.mainLayout.setColumnMinimumWidth(1, 0)
        self.mainLayout.setColumnMinimumWidth(2, 400)
        self.mainLayout.setColumnMinimumWidth(3, 0)
        # sets the minimum width for columns

        self.mainLayout.setColumnStretch(0, 0)
        self.mainLayout.setColumnStretch(1, 0)
        self.mainLayout.setColumnStretch(2, 0)
        self.mainLayout.setColumnStretch(3, 0)
        self.mainLayout.setColumnStretch(4, 0)
        # stops each column from expanding on their own

        self.blacklistSongName.show()
        # enables the song name field

        self.readyTag.emit()
        # sends a signal to the ready tag to allow progress (starts the threads)

### Program Ready State ###

    def programReadyState(self):
        """Function that activates things after the rest of the program is caught up"""

        self.swapStatsButton.show()
        self.debugInfoButton.show()
        # enables the function buttons button

        self.spotifyStatusIcon.show()
        self.spotifyStatusLabel.show()
        self.discordStatusIcon.show()
        self.discordStatusLabel.show()
        # enables all the status icons



### Global Objects ###



pictureQueue = queue.Queue()
"""An empty queue for pictures from picCycler to get sent to"""

songEvent = threading.Event()
"""An empty threading event list for song"""

picEvent = threading.Event()
"""An empty threading event list for picturecycler """

spotifyLock = threading.Lock()
"""A locking method to prevent redundant API calls (or 2 calls at once)"""

sessionID = requests.Session()
"""Tells the auth to keep one stable connection, rather than re-connecting every request"""

authorisation = None
"""The argument for auth_manager, containing the variables from config + scope of data request"""

main = None
"""Handles the authentication and user identification"""



def eventer():
    """Function that reassigns the required global objects"""
    global authorisation, main
    # grabs the global variables for the spotify auth

    authorisation = SpotifyOAuth(
        scope = "user-read-playback-state", 
        client_id = sp_client_ID, 
        client_secret = sp_client_secret, 
        redirect_uri = sp_redirect,
        cache_path = spCache
        )
    # this assignment can only be made *after* the client UI window runs (because that handles the config -> global var)

    main = spotipy.Spotify(auth_manager = authorisation)#, requests_session = sessionID)
    # same deal with this



### Spotify Data Grabber Function ###



def authPlayback():
    """Function to more "safely" handle Spotify API requests and errors"""
    
    global main
    # takes the global variable for the OAuth

    with spotifyLock:
    # uses a threading lock, to prevent multiple requests at once (shouldn't really happen, but prevents double-access bugs/crashes)

        tokenRefresh = False
        # a boolean to determine whether to print the token refresh or reconnect text (gets reset for every request)

        for attempt in range(3):
        # tries a max of 3 times to get Spotify data (typically succeeds 1st try, so if it doesn't work in 3, there's a bigger issue)

            try:
            # first tries to send an API request to Spotify

                success = main.current_playback()
                # if it works, returns the Spotify playback package (dictionary)

                if attempt != 0 and enableErrors and not tokenRefresh:
                # if it's not the first attempt, meaning the reconnect attempt print has already been pushed once (and the error isn't due to token)
                    mainWin.labelSwap.emit("Reconnect successful!", 0)
                    # prints user update
                    mainWin.iconChanger("Spotify", "Green")
                    # ensures the icon is green

                elif enableErrors and tokenRefresh:
                # if the tokenrefresh flag is set to true, that means a connectionError occurred at least once
                    mainWin.labelSwap.emit("Token refreshed successfully!", 0)
                    # prints user update with more specific info
                    mainWin.iconChanger("Spotify", "Green")
                    # ensures the icon is green

                return success
                # sends back the successfully found dictionary to the calling function (should only be looper)
                

            except Exception as error:
            # if it fails to acquire a Spotify playback package

                # this section individually checks for a few specific errors, because they were the most common that I had 
                # (token refreshing isn't *really* an error but is classed as such internally)
                # while printing 2-3 lines of error code is "helpful", it doesn't really help when the error is a simple, "self-fixing" one

                if isinstance(error, requests.exceptions.ConnectionError):
                # if the error is a connection error (more than likely due to token expiry)
                    if enableErrors:
                    # if error-printing is enabled
                        mainWin.labelSwap.emit(f"Refreshing Spotify token...", 1)
                        # doesn't sleep because this is a token error and should get "fixed" nearly instantly
                        # expected to print just about every 3600 seconds (1h)
                    tokenRefresh = True
                    # sets the tokenRefresh flag to true so the next print is more relevant (purely QoL)

                elif isinstance(error, requests.exceptions.ReadTimeout):
                # if the error is a read timeout (sort of random)
                    if enableErrors:
                    # if error-printing is enabled
                        mainWin.labelSwap.emit(f"Spotify API timeout.\nRetrying in 5 seconds ({attempt+1}/3)", 2)
                        # user inform
                    time.sleep(2)
                    # sleeps for 2 seconds (because there's a function-wide 3-second cooldown added on top)
                    mainWin.iconChanger("Spotify", "Yellow")
                    # ensures the icon is yellow

                elif isinstance(error, SpotifyException) and error.http_status == 429:
                # if the error is due to a rate limit (429 error code from Spotify)
                    retryTimer = error.headers.get("Retry-After", 5)
                    # gets the retry cooldown timer (or 5, if none is found)
                    if enableErrors:
                    # if error-printing is enabled
                        mainWin.labelSwap.emit(f"This application is being rate limited by Spotify.\nRetrying in {retryTimer} ({attempt+1}/3)", 2)
                        # user inform that should include a timer (sometimes it's weird, negative or doesn't exist)
                    time.sleep(int(retryTimer))
                    # sleeps for the duration of retryTimer (+3s due to global cooldown)
                    mainWin.iconChanger("Spotify", "Yellow")
                    # ensures the icon is yellow

                elif isinstance(error, SpotifyException) and (error.http_status == 500 or error.http_status == 503):
                # if the error is 500 (internal error fail)
                    if enableErrors:
                    # if error-printing is enabled
                        mainWin.labelSwap.emit(f"Spotify internal error.\nAttempting to reconnect ({attempt+1}/3)", 2)
                        # "should never happen" (according to Spotify docs), but does occasionally (typically Spotify-side maintenance or servers down)
                    mainWin.iconChanger("Spotify", "Yellow")
                    # ensures the icon is yellow

                elif isinstance(error, SpotifyException) and (error.http_status == 401):
                # if the error is 401 (access token error, forbidden action, etc)
                    if enableErrors:
                    # if error-printing is enabled
                        mainWin.labelSwap.emit(f"Spotify access error.\nAttempting to reconnect ({attempt+1}/3)", 2)
                        # user inform on token error
                    mainWin.iconChanger("Spotify", "Yellow")
                    # sets the icon yellow to indicate some type of error
                    time.sleep(1)
                    # waits a second

                elif isinstance(error, SpotifyException) and (error.http_status == 400):
                # if the error is 400 (access denied, token expired)
                    if error.headers.get("error") and error.headers.get("error") == "invalid_grant":
                    # if the error header is given and its reason is "invalid_grant" (refresh token expired)
                        mainWin.labelSwap.emit(f"Spotify refresh token expired, please re-login", 2)
                        # user update on login requirement (doesn't consider errors because this requires user interaction)
                        spotifyLogin()
                        # calls the spotify re-login to delete the cache file and force a login
                        tokenRefresh = True
                        # sets the token boolean to True (QoL)
                    else:
                    # not that error, likely just temporary
                        if enableErrors:
                        # if error-printing is enabled
                            mainWin.labelSwap.emit(f"Spotify error: {error}.\nAttempting to reconnect ({attempt+1}/3)", 2)
                            # generic user update

                else:
                # if the error is anything else
                    if enableErrors:
                    # if error-printing is enabled
                        mainWin.labelSwap.emit(f"Spotify error: {error}.\nAttempting to reconnect ({attempt+1}/3)", 2)
                        # generic user update
                    mainWin.iconChanger("Spotify", "Yellow")
                    # ensures the icon is yellow

                if attempt == 2:
                # if it's the last attempt (range(3) = 0,1,2) and it fails
                    mainWin.labelSwap.emit(f"All attempts to reconnect failed due to {error}\nExiting...", 4)
                    # user update
                    mainWin.iconChanger("Spotify", "Red")
                    # calls the icon changer with red icon
                    time.sleep(600)
                    # waits 10 minutes
                    mainWin.stopper()
                    # prompts user, then exits

                time.sleep(3)
                # waits 3 seconds to give it some time



def spotifyLogin():
    """Function to (re)connect to a Spotify account"""
    global authorisation, main
    # global -> local

    with spotifyLock:
    # uses the thread lock to prevent it from accessing the API while this is reconnecting

        if os.path.exists(spCache):
        # if there's a spotify token cache file
            os.remove(spCache)
            # deletes it

        time.sleep(5)
        # waits a short amount of time

        eventer()
        # calls the eventer to re-create a spotipy instance (to ideally remove old, cached credentials from use)



### SHA(A) Check ### 



def shaaCheck():
    """Function that loads CSV stuff related to the SHA(A)"""
    global uriList, csvReader, uriMap
    # loads globals to manipulate

    if os.path.isfile(SHAAdir) and not disableShaa:
    # if the grouped.csv file exists and SHAA-functionality isn't disabled
        mainWin.labelSwap.emit("Spotify Analyser (Addon) functionality enabled", 0)
        # informs user SHAA is enabled
        csvReader = pd.read_csv(SHAAdir, encoding="utf-8")
        # opens the CSV file and uses utf-8 encoding to ensure compatibility
        csvReader = csvReader.set_index("URI")
        # sets the track URL as the index

        if os.path.exists(noURIpath):
        # checks if the uri file (uriList.json) exists
            with open(noURIpath, "r", encoding="utf-8") as URIs:
                # loads the JSON file of URIs
                uriList = json.load(URIs)
                # stores the loaded file as uriList
                if enableUpdates and enableMapping:
                # if the user prints and mapping options are enabled
                    uriLength = len(uriList)
                    # stores the length of the unmapped URI list
                    mainWin.labelSwap.emit(f"{uriLength} URIs stored", 1)
                    # helper print (if using the URI mapper)
        else:
        # if file doesn't exist
            uriList = []
            # creates a new, empty list

        if os.path.exists(uriPath):
        # checks if the URI map file (uriMap.json) exists
            with open(uriPath) as maps:
            # loads the URI map file
                uriMap = json.load(maps)
                # stores the loaded file as uriMap
                if enableUpdates and enableMapping:
                # if the user prints and mapping options are enabled
                    uriMLength = len(uriMap)
                    # stores the length of the mapped URIs
                    mainWin.labelSwap.emit(f"{uriMLength} URIs mapped", 1)
                    # user inform
        else:
        # if the file doesn't exist
            uriMap = {}
            # creates a new, empty list



def uriWriter(URIs: list):
    """Function that writes the current URI list to file"""
    with open(noURIpath, "w", encoding="utf-8") as nURI:
    # opens the unfound URI file in write mode
        json.dump(URIs, nURI, indent=3)
        # "dumps" the list of URIs into the file (with indent)



def statsWriter(action: str):
    """Function that adds the current stats to file"""
    if os.path.exists(statsPath):
    # if the statistics file exists
        with open(statsPath) as stats:
        # opens the statistics file in read mode
            globalStats = json.load(stats)
            # loads the global (across sessions) statistics
    else:
    # if the file doesn't exist
        globalStats = {
            "Songs Played": 0,
            "Time Played": 0,
            "Avg Duration": 0,
            }
        # sets default 0 values for all statistics
    
    if action == "Load":
    # if the action is to load
        return globalStats
        # returns the dictionary

    elif action == "Save":
    # if the action is to save
        globalSongsPlayed = globalStats["Songs Played"]
        globalTimePlayed = globalStats["Time Played"]
        # grabs each statistic individually
        
        totalSongsPlayed = int(globalSongsPlayed + trackCounter)
        # adds up the total amount of songs played
        totalTimePlayed = int(globalTimePlayed + timePlayed)
        # adds up the total time spent playing
        if totalSongsPlayed > 1:
        # if there's been at least 1 song
            totalAvgDuration = int(totalTimePlayed / (totalSongsPlayed - 1))
            # calculates the total average duration (seconds)
        else:
        # if not
            totalAvgDuration = totalTimePlayed
            # just takes the time played

        totalStats = {
            "Songs Played": totalSongsPlayed,
            "Time Played": totalTimePlayed,
            "Avg Duration": totalAvgDuration
            }
        # forms a new dictionary with the new stats

        with open(statsPath, "w", encoding="utf-8") as stats:
        # opens the statistics file in write mode
            json.dump(totalStats, stats, indent=3)
            # dumps the statistics to file



def blacklistReader():
    """Function that reads the current blacklist of songs from file"""
    global blacklist
    # global -> local

    if os.path.exists(blacklistPath):
    # if the blacklist file exists
        try:
        # tries to open it
            with open(blacklistPath, "r", encoding="utf-8") as blkList:
            # opens the blacklist file in read mode
                blacklist = json.load(blkList)
                # reads the blacklist from file and stores in a global variable
        except:
        # if it fails
            blacklist = {}
            # creates an empty map
    else:
    # if it doesn't (first time/deleted)
        blacklist = {}
        # creates an empty map instead



def whitelistManager(action: str) -> list | None:
    """Function that handles the 'whitelist' management"""
    global blacklist
    # global -> local

    favoriteList = []
    # a new empty list for the favorite songs to go into

    for uri, statusDict in blacklist.items():
    # goes through each URI and its status in the blacklist
        if statusDict.get("status") == "starred":
        # if the status is "starred"
            favoriteList.append(statusDict)
            # adds the info dictionary to the favorite list
    
    if action == "Add":
        if len(favoriteList) == 10:
        # if there's 10 items already in the list
            mainWin.labelSwap.emit("The favorited song list is full!\nPlease remove one before favoriting this song.", 2)
            # user update
        else:
        # if there's not 10
            blacklist[currentURI] = {
                "status": "starred",
                "info": blacklistInfo
                }
            # forms a new blacklist entry with the current song's info
            mainWin.labelSwap.emit(f"Added {blacklistInfo["Song Name"]} to favorite list!", 3)
            # user update
        
    elif action == "List":
    # if the action is to list
        return favoriteList
        # simply returns the list



### Background Picture Tasker ###



class pictureClass(threading.Thread):
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
                    mainWin.labelSwap.emit("Selected picture method is Spotify covers, disabling picture cycler", 0)
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
                            mainWin.labelSwap.emit("Random picture set", 1)
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
                                mainWin.labelSwap.emit("Sequential picture set", 1)
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
                        # if the queue isn't empty
                            time.sleep(10)
                            # if the queue isn't empty, waits 10 seconds then re-runs the picture selection

                if self.picCycleType == "once":
                # if the selected method is just to set one random picture
                    i = random.randint(0, picLength)
                    # picks a random number based on list length
                    cppLargeImage = self.picCycleList[i]
                    # chooses the element with the random number
                    self.pictureQueue.put(cppLargeImage)
                    # sends the picture to a queue that then reaches song()
                    if enableUpdates:
                        mainWin.labelSwap.emit("Random picture set", 1)
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
                        mainWin.labelSwap.emit("Picture set", 1)
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
                # if error logging is enabled
                    mainWin.labelSwap.emit("Invalid picture cycle behavior or no picture set - proceeding without a picture", 2)
                    # user inform
                self.running = False
                False
                # doesn't set a picture, doesn't need to - so it stops the background thread



### C++ ###



def runCpp(event):
    """Function to run the C++ / Discord RPC program"""
    global cppProgram, cppFails
    # global -> local
    
    for process in psutil.process_iter():
    # goes through the list of active processes
        try:
        # tries to kill matching names
            if process.name() == cppExe or process.name() == "DSIdiscord":
            # if the process name matches the DSIdiscord.exe name (or without the .exe)
                process.kill()
                # stops the process (sometimes when DSI is quit without the exit button, the discord subprocess doesn't die, and breaks the API connection when opening a new instance)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
        # if it fails due to missing process or access denied
            pass
            # doesn't do anything (can't do anything)

    cppProgram = subprocess.Popen([cppPath], cwd=cppDir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0, creationflags=subprocess.CREATE_NO_WINDOW)
    # opens the C++/Discord exe, passes the current working directory and captures output, errors and allows input

    def cppQueueManager(output: any, cppQueue: any):
        """Function to manage the C++ output queue"""
        for line in iter(output.readline, b''):
        # for every line in the output
            cppQueue.put(line)
            # puts the line into a queue
        output.close()
        # stops listening

    cppQueue = queue.Queue()
    # creates a queue for C++ output
    threading.Thread(target = cppQueueManager, daemon=True, args=(cppProgram.stdout, cppQueue,)).start()
    # makes a thread for the C++ queue manager, passes the C++ output and the queue

    while True:
    # while the process is running
        if cppThreadEvent.is_set():
        # if the event is set
            cppProgram.terminate()
            # kills the C++ program
            try:
            # checks for response
                cppProgram.wait(timeout=2)
                # waits 2 seconds
            except subprocess.TimeoutExpired:
            # if it fails
                cppProgram.kill()
                # kills the C++ program
            break
            # stops

        try:
        # tries to grab a new line from the cppQueue 
            lineRaw = cppQueue.get(timeout=0.5)
            # grabs the raw printed line from C++ (waits 500ms per check)
        except queue.Empty:
        # if the queue is empty
            if cppProgram.poll() is not None:
            # if there's no output and the program isn't responding
                break
                # stops
            continue
            # resets the loop

        if enableUpdates and lineRaw:
        # if user prints are enabled and there's something to print
            line = lineRaw.decode("utf-8", errors="ignore").strip()
            # decodes bytes -> text, ignores any errors and removes whitespace
            if line:
            # every time the C++ file sends something as output, this program takes it
                if "RPC started" in line:
                # if the line is about the startup info
                    mainWin.labelSwap.emit(line, 3)
                    # updates the console with code 3 (newline)
                else:
                # if it's anything else
                    mainWin.labelSwap.emit(line, 0)
                    # code 0 is nothing extra
            
                if "updated" in line:
                # if the line contains "updated" (means the RPC update went through)
                    mainWin.iconChanger("Discord", "Green")
                    # ensures the icon is green
                    cppFails = 0
                    # resets fails
                elif "failed" in line.lower():
                # if the line contains "failed"/"Failed" (means the RPC update didn't go through)
                    mainWin.iconChanger("Discord", "Yellow")
                    # ensures the icon is yellow
                elif "api asset" in line.lower():
                # if the line contains "API asset" (means RPC failed because of Discord's API refusing to set the assets)
                    mainWin.iconChanger("Discord", "Yellow")
                    # ensures the API icon is now yellow
                    cppFails += 1
                    # adds 1 to the fail counter
                    if cppFails >= 3:
                    # if the fail counter climbs above 3
                        cppFails = 0
                        # resets to 0
                        mainWin.iconChanger("Discord", "Red")
                        # ensures the API icon is now red
                        mainWin.labelSwap.emit(f"Shut down Discord RPC due to Discord API errors, please press the 'Re-run DiscordRPC' to restart, or manually exit and restart DSI", 3)
                        # sends a user log to inform user
                        mainWin.rerunRPCbutton.show()
                        # enables the button to allow user to restart RPC
                        cppThreadEvent.set()
                        # sets an event, telling the loop to close the subprocess

    cppProgram.wait()
    # waits for the program to close

def cppPackets(packet: dict):
    """Function to send packets to the C++ program"""
    dataPacket = json.dumps(packet).encode("utf-8")
    # converts the passed argument into json
    cppProgram.stdin.write(struct.pack("!I", len(dataPacket)))
    # sends the byte length of the packet
    cppProgram.stdin.write(dataPacket)
    # writes the packet to the C++ program (sends)
    cppProgram.stdin.flush()
    # ensures all messages are sent



### Song Data File Field Selection/Creation ###



def song(pictureQueue, event):
    """The function that handles all song data gathering and parsing"""
    global uriList, cppLargeImage, uriMap, totalHours, totalMinutes, totalSeconds, detailOptions, pauseStart, currentInfo
    global trackCounter, oldCount, cycleCount, blacklistInfo, hoverText, smallURL, timePlayed, csName, csArtist, cppFull
    # global -> local

    while not songThreadEvent.is_set():
    # while the event isn't set, keeps looping

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

        shaaPlaytimeMin = None
        shaaPlaycountSong = None
        shaaPlaytime = None
        # starts up variables as None

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

        csUnixStart = int(time.time() - csProgress + 2)
        # stores the start time of the song by taking current time and subtracting progress
        # adds 2 seconds to shift the Discord timestamps to be slightly behind Spotify (they were a bit ahead before, actually)
        # this way, there shouldn't be a situation where Discord claims the song has ended when it's still playing on Spotify
        csUnixEnd = (csUnixStart + csLength)
        # stores the end time of the song (by adding up the start + duration)

        csPlayState = bool(csFull.get("is_playing"))
        # grabs the playback state (true/false)

        if not csPlayState:
        # if the song is paused

            if pauseStart is None:
            # if there's no set pause time
                pauseStart = int(time.time() + 4)
                # sets the pause time to current time
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
                timePlayed -= pauseDuration
                # removes the paused duration from the total time played

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
            # sets url


        ### SHAAless Behavior ###


        if not os.path.isfile(SHAAdir) or disableShaa:
        # if not installed as an addon to Spotify Analyser, will not send numbers forward - rather just configured, set fields

        ### Field 1 / Field 2 ###

            songStuffList.append(songInfoFallback)
            # adds the user-defined first field to list
            songStuffList.append(songInfoSpacer)
            # adds the spacer to list
            songStuffList.append(songInfoFallback)
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

                if shaaInfoDetails.lower() == "volume":
                # if the config calls for volume
                    try:
                    # tries to get the volume (not supported by all devices)
                        shaaDetailField = f"{csDevice.get("volume_percent")}%"
                        # takes the volume and makes it a percentage
                    except:
                    # if it can't
                        shaaDetailField = "some volume"
                        # puts a fallback string
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # uses the user-formatted detail text
                
                elif shaaInfoDetails.lower() == "repeat":
                # if the config calls for repeat state
                    try:
                    # tries to get the repeat state boolean (some devices don't support)
                        repeatState = csFull.get("repeat_state")
                        # grabs the boolean

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
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # uses the user-formatted detail text

                elif shaaInfoDetails.lower() == "shuffle":
                # if the config calls for shuffle state
                    try:
                    # tries to get the shuffle state boolean (some devices don't support)
                        shuffleState = csFull.get("shuffle_state")
                        # grabs the boolean

                        if shuffleState:
                            # if shuffle state returns True
                            shaaDetailField = "on Shuffle"
                            # adds string form
                        else:
                            # if shuffle state doesn't return True
                            shaaDetailField = "not on Shuffle"
                            # adds string form
                    except:
                        shaaDetailField = "may be on Shuffle"
                        # if it fails, puts a fallback string
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # uses the user-formatted detail text

            else:
                # if the config option doesn't match any of the set defaults
                shaaDetailField = shaaInfoDetails
                # sets the total time to match custom string instead

            cppLargeHoverList.append(shaaDetailField + " ")
            # joins together the list 

            if dsiShoutout:
            # if the DSI shoutout tag is enabled
                cppLargeHoverList.append(dsiShoutoutStr)
                # adds the string (// data by DSI)

            cppLargeHover = "".join(cppLargeHoverList)
            # joins together the details list to one string


    ### URI Reassignment ###

        finalURI = csURI
        # creates a new variable with the current song's URI
        altURI = None
        # creates a new variable to store a mapped version of the song's URI

    ### SHAA Behavior ###

        if os.path.isfile(SHAAdir) and not disableShaa:
        # this is the addon part to Spotify (History) Analyser (SHA + addon = SHAA)
        # this data is only entered to rich presence if used with SHA (and installed correctly)
        # checks if the CSV file exists to pull data from (requires one full run of SHA prior)
            
        ### URI Checkpoint ###

            if enableMapping:
            # if URI mapping is enabled
                
                altURI = uriMap.get(csURI)
                # creates an alteranate variable from the JSON map by checking with the current URI

                if finalURI not in uriList:
                # if the URI is not in the URI list yet
                    if enableUpdates:
                    # if the user updates are enabled
                        mainWin.labelSwap.emit("Song URI not found in list, added to URI map list", 0)
                        # user update
                    uriList.append(finalURI)
                    # adds it to the list of URIs

                if (finalURI not in csvReader.index) and (altURI in csvReader.index):
                # if the URI is not found in the CSV index, but the alternate URI is
                    finalURI = altURI
                    # sets the URI to use the alternate instead
                    if enableUpdates:
                    # if the user updates are enabled
                        mainWin.labelSwap.emit("Using song stats from mapped URI", 0)
                        # user update

            if finalURI in csvReader.index:
            # checks if the URI is in the CSV
                if enableUpdates:
                # if the user updates are enabled
                    mainWin.labelSwap.emit(f"Song stats found", 0)
                    # user update

            ### Plays / Field 1 ###

                playcount = csvReader.loc[finalURI, "Playcount"]
                playtime = csvReader.loc[finalURI, "Total Time"]
                # sets temp variables that lookup the cells based on the track and columns

                if songInfoField1 == "Track":
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
                    # adds the track's playcount to the list
                    shaaPlaycountSong = shaaPlaycount
                    # copies the variable

                elif songInfoField1 == "Total":
                # if the selected type for the first field is Total

                    shaaPlaycount = f"{csvReader["Playcount"].agg("sum"):,.0f}"
                    # adds up *all* the playcounts for all tracks
                    songStuffList.append(shaaPlaycount)
                    # adds the total playcount to the list

            ### Field 1 Format ###

                songStuffList.append(songInfoFormatPlays)
                # adds the first field's custom end styling

            ### Spacer ###

                songStuffList.append(songInfoSpacer)
                # adds the spacer to the list

            ### Minutes / Field 2 ###

                if songInfoField2 in [0, 2, 4]:
                # if the selected type for the second field is 0 (track minutes), 2 (track hours) or 4 (track seconds)

                    if isinstance(playtime, pd.Series):
                    # if there's more than one instance of the current song
                        playtimeTotal = int((playtime.sum()) / 1000)
                        # calculates the total playtime (seconds)
                    else:
                    # if there's only one instance of the current song
                        playtimeTotal = int(playtime / 1000)
                        # saves the total as the playtime of the song

                    shaaPlaytimeMin = f"{(playtimeTotal / 60):,.1f}"
                    # stores a second variable for minutes (for details window)

                    if songInfoField2 == 0:
                    # track minutes
                        playtimeTotal = (playtimeTotal / 60)
                        # divides the seconds into minutes
                    
                    elif songInfoField2 == 2:
                    # track hours
                        playtimeTotal = (playtimeTotal / 3600)
                        # divides the seconds into hours

                    shaaPlaytime = f"{playtimeTotal:,.1f}"
                    # formats the string properly
                    songStuffList.append(shaaPlaytime)
                    # adds the total playcount to the list

                elif songInfoField2 in [1, 3, 5]:
                # if the selected type for the first field is 1 (total minutes), 3 (total hours) or 5 (total seconds)

                    shaaPlaytime = int(csvReader["Total Time"].agg("sum") / 1000)
                    # adds up *all* the time played (milliseconds/1000 = seconds)

                    if songInfoField2 == 1:
                    # total minutes
                        shaaPlaytime = (shaaPlaytime / 60)
                        # divides the seconds into minutes

                    elif songInfoField2 == 3:
                    # total hours
                        shaaPlaytime = (shaaPlaytime / 3600)
                        # divides the seconds into hours

                    shaaPlaytime = f"{shaaPlaytime:,.1f}"
                    # formats the string properly

                    songStuffList.append(shaaPlaytime)
                    # adds to string list

                ### Field 2 Format ###

                songStuffList.append(songInfoFormatMins)
                # adds the second field's custom end styling
                    
        ### Details / Field 3 / Total Hours ###

            if shaaInfoDetails in detailOptions:
            # if the config option matches one of the set defaults

                if shaaInfoDetails.lower() == "hours":
                # if the config calls for total hours
                    shaaDetailField = totalHours
                    # gets total hours
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # uses the user-formatted one

                elif shaaInfoDetails.lower() == "minutes":
                # if the config calls for total minutes
                    shaaDetailField = totalMinutes
                    # gets total minutes
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # uses the user-formatted one

                elif shaaInfoDetails.lower() == "seconds":
                # if the config calls for total seconds
                    shaaDetailField = totalSeconds
                    # gets total seconds
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # uses the user-formatted one

                elif shaaInfoDetails.lower() == "cycle":
                # if the config calls for cycle
                    if cycleCount == 0:
                    # on the first cycle, uses hours
                        shaaDetailField = totalHours
                        # sets the field to be total hours
                        cycleCount += 1
                        # adds 1 to counter
                        cppLargeHoverList.append("Total Hours")
                        # adds the string
                    elif cycleCount == 1:
                    # on the second cycle, uses minutes
                        shaaDetailField = totalMinutes
                        # sets the field to be total minutes
                        cycleCount += 1
                        # adds 1 to counter
                        cppLargeHoverList.append("Total Minutes")
                        # adds the string
                    elif cycleCount == 2: 
                    # on the third (last) cycle, uses seconds
                        shaaDetailField = totalSeconds
                        # sets the field to be total seconds
                        cycleCount = 0
                        # resets to 0 for next cycle 
                        cppLargeHoverList.append("Total Seconds")
                        # adds the string

                elif shaaInfoDetails.lower() == "volume":
                # if the config calls for volume
                    try:
                    # tries to get the volume (not supported by all devices)
                        shaaDetailField = f"{csDevice.get("volume_percent")}%"
                        # takes the volume and makes it a percentage
                    except:
                    # if it can't
                        shaaDetailField = "some volume"
                        # puts a fallback string
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # uses the user-formatted detail text
                
                elif shaaInfoDetails.lower() == "repeat":
                # if the config calls for repeat state
                    try:
                    # tries to get the repeat state boolean (some devices don't support)
                        repeatState = csFull.get("repeat_state")
                        # grabs the boolean

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
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # uses the user-formatted detail text

                elif shaaInfoDetails.lower() == "shuffle":
                # if the config calls for shuffle state
                    try:
                    # tries to get the shuffle state boolean (some devices don't support)
                        shuffleState = csFull.get("shuffle_state")
                        # grabs the boolean

                        if shuffleState:
                            # if shuffle state returns True
                            shaaDetailField = "on Shuffle"
                            # adds string form
                        else:
                            # if shuffle state doesn't return True
                            shaaDetailField = "not on Shuffle"
                            # adds string form
                    except:
                        shaaDetailField = "may be on Shuffle"
                        # if it fails, puts a fallback string
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # uses the user-formatted detail text

            else:
            # if the config option doesn't match any of the set defaults
                shaaDetailField = shaaInfoDetails
                # sets the total time to match custom string instead
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

            cppLargeHoverList.append(shaaDetailField + " ")
            # adds the detail field text and a space

            if dsiShoutout:
            # if the dsi shoutout option is enabled
                cppLargeHoverList.append(dsiShoutoutStr)
                # adds the shoutout string (// data by DSI)

            cppLargeHover = "".join(cppLargeHoverList)
            # joins together the list

        ### No Track Match ###

            if finalURI not in csvReader.index:
            # if the track wasn't found in CSV
                if enableUpdates:
                # if the updates are enabled
                    mainWin.labelSwap.emit(f"{csName} not found in CSV, using fallback values", 1)
                    # lets user know the song wasn't found in CSV
                
                ### Field 1 / Field 2 ###

                if shaaFallback == "Total":
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

        if not disableShaa:
        # if shaa is enabled (not disabled)
            mainWin.blacklistTag.emit("New Song", csName, finalURI)
            # sends a signal to the blacklist manager to change the name and information

        if finalURI in blacklist:
        # if the song('s URI) is in the blacklist
            if blacklist[finalURI]["status"] == "blacklisted":
            # if the song's URI in the blacklist returns a blacklisted value
                favoriteList = whitelistManager("List")
                # calls the whitelistmanager to list current favorite songs, stores it

                if len(favoriteList) > 0:
                # if there's more than 0 items in the list
                    pickedSong = random.choice(favoriteList)
                    # gets a random song from the list of favorite songs
                    mainWin.labelSwap.emit("This song is blacklisted, using a favorited song instead...", 0)
                    # user inform
                    cppReplace = pickedSong["info"]
                    # gets the song's full dictionary
                    cppSongName = cppReplace["Song"]
                    cppAlbumName = cppReplace["Album"]
                    cppState = cppReplace["State"]
                    cppLargeImage = cppReplace["Large Image"]
                    cppLargeHover = cppReplace["Large Text"]
                    hoverText = cppReplace["Small Text"]
                    csURL = cppReplace["Spotify URL"]
                    smallURL = cppReplace["Small URL"]
                    # grabs all the relevant details that will replace the current song's information
                else:
                    mainWin.labelSwap.emit("This song is blacklisted, but no favorited songs found!\nPlease favorite at least one song to utilize blacklisting!", 2)
                    # user update

        cppFull = {
            "Song": cppSongName,
            "Album": cppAlbumName,
            "State": cppState,
            "Large Image": cppLargeImage,
            "Large Text": cppLargeHover,
            "Small Text": hoverText,
            "Spotify URL": csURL,
            "Small URL": smallURL,
            "UNIX Start": csUnixStart,
            "UNIX End": csUnixEnd,
            "Pause": (not csPlayState),
            "Song Raw": csName,
            "Artist": csArtist,
            "Track ID": trackCounter,
            "URI": finalURI,
            "Playcount": (shaaPlaycountSong if shaaPlaycountSong is not None else "N/A"),
            "Playtime": (shaaPlaytimeMin if shaaPlaytimeMin is not None else "N/A"),
            "SHAA": (not disableShaa)
        }
        # forms a dictionary of the current song's full info (sent to C++ and to Flask app, if enabled)

        blacklistInfo = {
            "Song Name": csName,
            "Artist Name": csArtist,
            "Song": cppSongName,
            "Album": cppAlbumName,
            "State": cppState,
            "Large Image": cppLargeImage,
            "Large Text": cppLargeHover,
            "Small Text": hoverText,
            "Spotify URL": csURL,
            "Small URL": smallURL
        }
        # forms a smaller dictionary of the current song's info (this is just for the "blacklist" preview)

        cppPackets(cppFull)
        # sends the formed dictionary to the C++ program

        mainWin.songDetails()
        # calls the song details function to update the visuals

        songEvent.clear()
        # clears the event queue, ready to get new requests



### Information Checking Loop ###



def looper():
    """Function that checks song info on a loop"""
    global currentURI, currentInfo, pauseUpdated, trackCounter, noPlayCounter, lastPlayStamp
    # global -> local

    while True:
    # this loop checks if the song playing is the same as the previous update, waits if yes, updates the song to match if not

        info = authPlayback()
        # picks up all the info Spotify sends in an update

        if not info or not info.get("item"):
            # checks if the info "package" has something and if it contains valid information
            if noPlayCounter >= 3:
            # if the counter has reached 3, meaning it's been 3 attempts in a row
                mainWin.labelSwap.emit("No songs detected for 15 seconds, lowering API rate and disabling logging until playback continues", 2)
                # user inform on change of process
                time.sleep(15)
                # waits for 15 seconds (3x slower API rate)
                continue
                # resets back to looper start
            else:
            # if the counter is less than 3
                mainWin.labelSwap.emit("No playing state detected, re-checking in 5 seconds", 2)
                # user inform
                time.sleep(5)
                # waits for a few seconds
                noPlayCounter += 1
                # adds 1 to the counter
                continue
                # resets back to looper start
        
        currentInfo = info
        # sets the global variable to match

        noPlayCounter = 0
        # resets the "no playing state" counter to 0, since the loop has progressed here

        songURI = (info.get("item")).get("uri")
        # grabs the URI of the song, stores it
        songName = (info.get("item").get("name"))
        # stores name for display purposes
        songProg = ((info.get("progress_ms")) / 1000)
        # grabs the progress of the song at the pull time (ms/1000 = seconds)
        songStart = int(time.time() - songProg)
        # stores the start time of the song by taking current time and subtracting progress
        playing = info.get("is_playing")
        # checks the pause state (True if playing, False if not)

        if currentURI is None:
            # when the program first starts, the currentURI will be "None", this updates it
            currentURI = songURI
            # sets the current song to match 
            storedStart = songStart
            # updates the timestamp to match
            trackCounter += 1
            # adds 1 to counter
            lastPlayStamp = songStart
            # sets the first song's start time as the initial timestamp for stats calculation
            mainWin.programReady.emit()
            # tells the program ready state function to enable post-process items
            picEvent.set()
            # since this only runs when the program first starts, sets an event immediately to picCycler, to grab a new picture
            songEvent.set()
            # since this only runs when the program first starts, sets an event immediately to song, to refresh data
            if enableUpdates:
            # if updates are enabled
                mainWin.labelSwap.emit(f"First song: {songName}, has been successfully processed", 3)
                # if user wants feedback, sends this

        songDur = ((info.get("item")).get("duration_ms")/1000)
        # grabs both the current time and length of the song (in seconds)
        songLeft = (songDur-songProg)
        # calculates the time left on the song

        if (currentURI != songURI) or ((songStart-15) > storedStart) or (pauseUpdated and playing):
        # if there's a song change (if the URI has changed or the start timestamp is higher than the stored timestamp) or if the pause has been triggered

            if enableUpdates and not pauseUpdated:
                # if console updates are enabled and this change wasn't triggered by a pause
                mainWin.labelSwap.emit(f"New song: {songName}, duration: {songDur:,.0f} seconds", 3)
                # user update on new song
            elif enableUpdates and pauseUpdated and playing:
                # if console updates are enabled and this change *was* triggered by a pause
                mainWin.labelSwap.emit(f"Unpaused: {songName}", 3)
                # user update on unpause

            currentURI = songURI
            # changes the internal variable to match new song
            storedStart = songStart
            # changes timestamp variable to match
            songEvent.set()
            # sets an event to make song() update the presence info

            if pauseUpdated and playing:
                # if it's playing and the pauseUpdate has been set to true
                pauseUpdated = False
                # sets the pauseUpdated to false, so it doesn't run twice
            elif not pauseUpdated and playing:
                # if it's playing but pauseUpdate is false
                trackCounter += 1
                # adds 1 to counter (means track has changed)

            time.sleep(2)
            # waits 2 seconds
            continue
            # sends back to the start of looper to check for a new song (5 second checks after a song change to check for a song skip)

        if not playing and not pauseUpdated:
        # if the song is paused and hasn't yet updated the pause state
            if enablePause:
                # if the pause hasn't been registered yet and the pause behavior is enabled
                songEvent.set()
                # sets an event to make song() update the presence info (this way it doesn't spam)
                pauseUpdated = True
                # sets the pause check to True, meaning it has been checked and acted on
                if enableUpdates:
                    # if user updates are on
                    mainWin.labelSwap.emit(f"Paused on: {songName}", 3)
                    # user inform (new line to split from main updates, only prints once anyway)
            sleepfor = refreshTime
            # sets the sleep timer to the config-set refresh time

        else:
        # if the current song is the same, and is not paused
            if songLeft > refreshTime:
                # checks if there's more song left than the refresh time is set to
                sleepfor = refreshTime
                # sets the sleep timer to the config-set refresh time
            else:
                # if there's less song time left than refresh time (eg. if refreshTime = 15, song will have to be <15)
                sleepfor = (songLeft + 1)
                # sleeps for the rest of the song (+1s to ensure the song has ended)
                # balance between accuracy and avoiding crazy rates

        time.sleep(sleepfor)
        # sleeps for the determined time



### Load Commands ###



bg = pictureClass(picCycleList, picCycleType, picCycleTime, pictureQueue)
# defines the background thread as the class containing all the picture function
# passes the list, type, time and queue

picThread = threading.Thread(target = bg.picCycler, daemon=True)
# creates a thread for the picture changer

songThreadEvent = threading.Event()
# a threading event used to close the songThread
songThread = threading.Thread(target = song, daemon=True, args=(pictureQueue, songThreadEvent,))
# creates the song thread

cppThreadEvent = threading.Event()
# a threading event used to close the cppThread
cppThread = threading.Thread(target = runCpp, daemon=True, args=(cppThreadEvent,))
# creates a thread for the C++ program to run in - this way it won't stop the main process

spDataThread = threading.Thread(target = runSPData, daemon=True)
# creates a thread for the localhost Spotify data to update with


### Start Functions ###



def startStart():
    """The function that starts the starter"""
    threading.Thread(target=mainStart, daemon=True).start()
    # runs the runner in a thread

def mainStart():
    """The function that starts the actual program logic"""

    shaaCheck()
    # runs the SHA(A) checker function first, to load global variables

    blacklistReader()
    # runs the blacklist reader to get the blacklist

    eventer()
    # runs the event reassigner (the spotify authorisation stuff)

    bg.start()
    # runs the "background" class, which handles the picture updates

    picThread.start()
    # starts the picture thread

    songThread.start()
    # starts the song thread to get updated info

    if hostData:
    # if the boolean for sharing data is enabled
        spDataThread.start()
        # starts the spotify data thread
        mainWin.labelSwap.emit(f"Hosting parsed Spotify data locally", 1)
        # user inform

    if dc_app_ID and sp_client_ID:
        # if both the Application ID and Spotify Client ID are found
        mainWin.labelSwap.emit(f"Found Discord Application ID and Spotify Client ID, starting Discord RPC process", 1)
        # user inform
        time.sleep(2)
        # waits a couple seconds to make sure all details are set before calling
        cppThread.start()
        # starts the C++ thread
    else:
        # if both aren't found
        mainWin.labelSwap.emit("Configuration error! Delete the config file if this error persists! Exiting...", 2)
        # user inform
        time.sleep(60)
        # wait 60 seconds
        raise SystemExit
        # end the program, can't really do much without AppID/Spotify Client ID

    looper()
    # runs the looper, which manages the song refresh cycles



### Window Start ###


startApp = QApplication(sys.argv)
# base app instance (passes command line arguments)
mainWin = DSI_MainWindow()
# creates a window instance for the main window
sys.exit(startApp.exec())
# exceutes the app task (runs the QApplication)
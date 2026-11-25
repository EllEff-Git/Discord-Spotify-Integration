import pandas as pd
# Required for all the CSV parsing and data grabbing
import random, subprocess
# Required to choose random pictures and to start the C++ file
import os, sys, time, threading, queue
# Required for system information, background tasking and queueing
import spotipy, requests, json, logging, socket, unicodedata
# Required for basic function of Spotify data requests and storing
from spotipy.oauth2 import SpotifyOAuth
# Required for authorizing with Spotify
from spotipy.exceptions import SpotifyException
# Required to check for exceptions (errors)
from collections import deque
# Required for "console-like" UI logging
import struct, psutil
# Required for C++ communication and management
from datetime import datetime
# Required for timestamping
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required for the main window
from flask import Flask
# Required for cross-communication between DSI and SBO
from DSIver import Version
# Version manager



### Version ###

DSIver = str(Version)
"""The program version (Y.M.DD.HHMM)"""



### Directory Grab ###

directory = os.path.dirname(sys.executable)
"""The base directory of the program, where DSI.exe resides"""
iconPath = os.path.join(sys._MEIPASS, "dsiIcon.png")
"""The path of the app icon png"""

yellowStatusPath = os.path.join(sys._MEIPASS, "dsiStatusYellow.png")
"""The yellow status icon png path"""
redStatusPath = os.path.join(sys._MEIPASS, "dsiStatusRed.png")
"""The red status icon png path"""
greenStatusPath = os.path.join(sys._MEIPASS, "dsiStatusGreen.png")
"""The green status icon png path"""

qtFolderPath = os.path.join(directory, "runtime", "Qt")
"""The folder that contains all the Qt window folders/executables (DSI/runtime/Qt)"""
configFolderPath = os.path.join(os.environ["LOCALAPPDATA"], "DSI")
"""The folder path that should contain all the configuration files"""

os.makedirs(configFolderPath, exist_ok=True)
# makes all the directories leading up to the config folder (it's okay if they already exist)



### Config ###

funcConfigPath = os.path.join(configFolderPath, "functionConfig.json")
"""The DSI functionality config json file"""
funcConfigExePath = os.path.join(qtFolderPath, "funcWindow", "funcWindow.exe")
"""The DSI functionality configurator program/window"""

dsiConfigPath = os.path.join(configFolderPath, "config.json")
"""The DSI configuration json file"""
dsiConfigExePath = os.path.join(qtFolderPath, "dsiWindow", "dsiWindow.exe")
"""The DSI configurator program/window"""

shaaConfigPath = os.path.join(configFolderPath, "shaaConfig.json")
"""The SHAA x DSI configuration json file"""
shaaConfigExePath = os.path.join(qtFolderPath, "shaaWindow", "shaaWindow.exe")
"""The SHAA x DSI configurar program/window"""

secretConfigPath = os.path.join(configFolderPath, "secretConfig.json")
"""The main configuration file, contains client secret info"""

statsPath = os.path.join(configFolderPath, "statistics.json")
"""The DSI statistics file path"""

### Token/ID ###

spCache = os.path.join(configFolderPath, "spotifycache.json")
"""The directory where the spotify cache (token) sits in"""
idDir = os.path.join(configFolderPath, "discordIDs.json")
"""The directory where discordIDs.json lives (inside DSI/Discord/discordIDs.json)"""

### Song Details ###

uriMapExePath = os.path.join(directory, "urimap", "urimap.exe")
"""The path to where the URImap.exe program lives"""
noURIpath = os.path.join(configFolderPath, "URIlist.json")
"""The path to where URIlist (unfound URIs) lives"""
uriPath = os.path.join(configFolderPath, "URImap.json")
"""The path to where URImap.json lives"""
blacklistPath = os.path.join(configFolderPath, "blacklist.json")
"""The path to where the song blacklist.json lives"""

### Spotify History Analyser (Addon) ###

SHAAdir = os.path.join(configFolderPath, "dsi.csv")
"""The directory where the CSV is"""
timeDir = os.path.join(configFolderPath, "totalTimes.json")
"""The directory where the totalTimes.json file is"""

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
dsiVisualConfig = {}
"""The config file with DSI customisation config"""
shaaConfig = {}
"""The config file specifically for SHA(A) features"""

blacklist = {}
"""The blacklist of songs from blacklist.json"""
maplessURIs = {}
"""The dictionaries of URIs from uriList.json"""

spotifyClientID = None
"""Spotify Client ID, string"""
spotifyClientSecret = None
"""Spotify Client Secret, string"""
spotifyRedirect = None
"""Spotify redirect URL, string"""
discordAppID = None
"""Discord Application ID, string"""

skipConfigWindow = False
"""Whether to skip the configuration window or not, bool"""
consoleLength = 25
"""The stored line amount for the pseudo-console, int"""
hostData = True
"""Whether to host the parsed Spotify data locally, bool"""
addressType = "Device"
"""Whether to host the data at device-only accessible or local network-accessible address"""
refreshTime = 10.0
"""Program update cycle interval time, float/int"""
autoSaveTimer = 2
"""Program auto-save timer, hours/int (0 = disabled)"""
autoRestart = True
"""Program automatic restart (for Spotify API errors only), boolean"""
savePosData = True
"""Whether to save the window position and sizes to file at exit"""

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

startTime = int(datetime.now().timestamp())
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
"""Second state field type, int (0-1 = minutes, 2-3 = hours, 4-5 = seconds (track is even, total is odd))"""
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
enableFirstTime = True
"""Whether to enable first time listening custom string"""
firstTimeFormat = "Listening for the first time!"
"""Custom string to use when listening for the first time, string"""
enableTopHour = False
"""Whether to enable top hour listening custom string, boolean"""
topHourFormat = "Listening at peak hours"
"""Custom string to use when listening at top hour, string"""
enableTopItems = True
"""Whether to enable top track prefixes, boolean"""
dsiShoutout = False
"""Whether to add a shoutout to DSI at the end of the details section, boolean"""


detailOptions = ["Hours", "Minutes", "Seconds", "Cycle", "Volume", "Repeat", "Shuffle"]
"""All possible choices for detail field (hours) that doesn't include custom string"""
spotifyURLlist = ["Track", "Album", "Artist", "Playlist"]
"""A list of all the possible options for spotify URL types"""
pictureBehaviorList = ["Random", "Sequence", "Once", "None"]
"""A list of all the possible options for picture cycling types"""

pauseStart = None
"""Makes a starter variable that stores a timestamp when a pause occurs"""
currentInfo = None
"""Song info dictionary"""
cppFull = {}
"""Currently playing song dict sent to the C++ program"""
blacklistInfo = None
"""Dictionary containing the current song's info"""
currentURI = None
"""The current song's track URI"""
deviceName = None
"""The currently playing device's name (str)"""
volumeLevel = None
"""The currently playing device's Spotify volume (percent, int)"""
cppLargeImage = ""
"""Makes an empty image string, in case it fails to make first load"""
pauseUpdated = False
"""A check to see if the pause state has been registered properly"""
totalHours = totalMinutes = totalSeconds = totalPlays = 0
"""Variables for total hours, minutes, seconds and plays"""
totalAverage = "0:00"
"""Variable to store the total historical average playtime to playcount"""
topHour = {}
"""Variable to store the top hour and its playcount ({hour: count})"""
topTracks = topArtists = topAlbums = {}
"""Dictionaries that store the URIs to each top X item(s) and their ranks in the respective dictionary"""

oldCount = trackCounter = 0
"""Variables to track 'song IDs'"""
noPlayCounter = 0
"""Variable to check how many times in a row playing state has been off (nothing playing)"""
cycleCount = 0
"""Variable to check the cycle count of hours, minutes and seconds (if enabled)"""
timePlayed = 0
"""Variable to store total playtime during DSI uptime"""
lastPlayStamp = time.time()
"""Variable to store timestamp for playtime calculation"""
storedStart = time.time()
"""Variable to store the start time of the current track"""
lastDSIsave = time.time()
"""Variable to store the last time DSI was auto-saved"""

csName = csSongName = csArtistName = csAlbumName = ""
"""The current song/artist/album name"""
csArtistURL = csAlbumURL = csPlaylistURL = ""
"""The current artist/album/playlist URL"""
dsiShoutoutStr = "// Data by DSI"
"""A shoutout string to DSI, disabled by default in config"""
disableShaa = False
"""Boolean to check whether SHA(A) functionality should be disabled or not"""
cppProgram = None
"""The C++ program subprocess (gets defined in its function)"""
stopLooper = False
"""Boolean (flag) to stop the looper from running"""



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
    return localSPData.response_class(
        json.dumps(cppFull, indent=2),
        mimetype="application/json")
    # turns the C++ dictionary into a json format, sends to the /spData page

@localSPData.route("/version")
def version():
# Spotify data version page
    return json.dumps(cppFull.get("Track ID", 0))
    # turns the single key value into a page (that SBO can check easier)

def runSPData():
# Spotify data page runner
    spPort = 41809
    # pre-determined port

    if addressType == "Device":
    # if the config option is set to Device-only
        address = "127.0.0.1"
        # uses device-only address
    else:
    # not device-only
        tempSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # forms a temporary socket connection (IPv4 + UDP ^)
        address = "0.0.0.0"
        # hosted address
        try:
        # quick connection check
            tempSocket.connect(("8.8.8.8", 80))
            # checks Google's DNS port
            address = tempSocket.getsockname()[0]
            # grabs the first element of the returned tuple of (IP, port)
        finally:
        # when done (or exception)
            tempSocket.close()
            # closes
    mainWin.labelSwap.emit(f"Hosting parsed Spotify data at {address}:{spPort}/spData", 1)
    # user inform
    localSPData.run(host=address, port=spPort)
    # runs the Flask app on the local network (ADD:PORT with /spData and /version)



### Main Window ###

class DSI_MainWindow(QMainWindow):
    """The main window class"""

    labelSwap = pyqtSignal(str, int)
    # a pyQt signal to swap the label
    readyTag = pyqtSignal()
    # a signal to signal the readiness state of the window
    blacklistTag = pyqtSignal(str, str, str)
    # a signal to call the song blacklist manager
    blacklistTagFull = pyqtSignal(str, str, str, dict)
    # a signal to call the song blacklist manager with the full details
    detailTag = pyqtSignal(str, int)
    # a signal to call the song detail manager
    programReady = pyqtSignal()
    # a signal to signal the readiness state of the program
    saveSignal = pyqtSignal(str)
    # a signal to call the save function

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

        self.windowSizeX = max(900, int(startApp.primaryScreen().size().width() / 3))
        self.windowSizeY = int(self.windowSizeX * (9 / 16))
        # base window sizes (uses the larger of the two, 900 or ~33% of the monitor's width, 16:9 aspect ratio for height)
        # for a 1080p/1440p monitor, it should work out to ~ 900 x 510
        # 4K = 1280 x 720 (literally a third in both dimensions)

        self.windowPosX = int((startApp.primaryScreen().size().width() - self.windowSizeX) / 2)
        self.windowPosY = int((startApp.primaryScreen().size().height() - self.windowSizeY) / 2)
        # base window location coordinates (0, 0 is top left corner, by default, aims to place the window in the direct center of the screen)
        # subtracts the window itself first, to only get the part of the monitor that's left over, then divides in two to get the offset 
        # (how far from the edge(s) the window should be)

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(self.windowSizeX, self.windowSizeY))
        # the window size minimums
        self.move(self.windowPosX, self.windowPosY)
        # moves the window to the defined points (center)

    ### UI Element Base ###

        self.container = QWidget()
        # a container to hold elements
        self.mainLayout = QGridLayout()
        # new grid layout to put elements into
        self.mainLayout.setSpacing(25)
        # sets spacing of 25px between elements

        self.mainLayout.setColumnMinimumWidth(0, 150)
        self.mainLayout.setColumnMinimumWidth(1, 400)
        self.mainLayout.setColumnMinimumWidth(2, 150)
        # sets the minimum width for columns

        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setRowStretch(2, 1)
        self.mainLayout.setRowStretch(3, 1)
        self.mainLayout.setRowStretch(4, 1)
        # allows rows 1-4 to stretch (all the rows with the console)

        self.container.setLayout(self.mainLayout)
        # sets the container to use layout

    ### Main Label ("Console") ###

        self.consoleScroll = QScrollArea()
        # a console-like scrollable area
        self.consoleScroll.setWidgetResizable(True)
        # allows the widget to be resized
        self.consoleScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # disables the scroll bar
        self.consoleScroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # allows the scroll area to resize to fit
        self.consoleScroll.setMinimumWidth(400)
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
        self.mainLayout.addWidget(self.consoleScroll, 1, 1, 4, 1)
        # adds the scroll area to the main layout (top middle, spans rows 1-4, 0 is buttons/track, 4 is functions (side), 5 is buttons)

        self.mainLabel = QLabel()
        # a label to hold the main information about current process
        self.mainLabel.setText("DSI starter window")
        # initial text
        self.mainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        # centers the label to the bottom
        self.mainLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # allows the label to expand
        self.mainLabel.setMinimumWidth(400)
        # sets a minimum size for the label
        self.mainLabel.setMaximumWidth(self.consoleScroll.width())
        # sets the max width to match to match the console's width
        self.mainLabel.setWordWrap(True)
        # ensures text too long still wraps
        self.consoleScroll.setWidget(self.mainLabel)
        # sets the console to use the mainLabel

    ### Bottom Elements ###

        self.exitLayout = QGridLayout()
        # a grid layout for the exit button(s)

        self.exitButton = QPushButton("Exit")
        # a button to exit the program
        self.exitButton.setToolTip("Close the program and save progress")
        # tooltip
        self.exitButton.setFixedSize(200, 50)
        # sets size
        self.exitButton.clicked.connect(lambda: self.stopper("Shut Down"))
        # connects the exit button to the program stopping function

        self.restartButton = QPushButton("Restart")
        # a button to restart the program
        self.restartButton.setToolTip("Restart the program 'in-place' (without shutting down)")
        # tooltip
        self.restartButton.setFixedSize(90, 50)
        # sets size
        self.restartButton.clicked.connect(lambda: self.restartHelper(True))
        # connects the restart button to the program restarting function
        self.restartButton.hide()
        # hides by default

        self.exitLayout.addWidget(self.exitButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds only the exit button to the layout

        self.versionTag = QLabel(f"DSI v{self.version}\n ")
        # label for the semantic version
        self.versionTag.setToolTip("Current DSI version")
        # tooltip
        self.versionTag.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        # aligns the text itself to the left
        self.versionTag.setOpenExternalLinks(True)
        # allows opening links (in case of new update)

        self.directoryButton = QPushButton("...")
        # a button to open the directory
        self.directoryButton.setFixedSize(50, 50)
        # sets size
        self.directoryButton.setToolTip("Open the configuration location\nThis is where your configurations and SHAA files are located")
        # tooltip
        self.directoryButton.clicked.connect(lambda: os.startfile(configFolderPath))
        # connects the button to just opening the installation directory

        self.mainLayout.addWidget(self.versionTag, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addLayout(self.exitLayout, 5, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.directoryButton, 5, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all the items
        
    ### Hideable/Showable Elements ###

        self.userInputField = QLineEdit()
        # creates a new QLineEdit for user to input into
        self.userInputField.setToolTip("Write here")
        # tooltip
        self.userInputField.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # alings to center
        self.userInputField.setFixedSize(300, 30)
        # sets size
        self.mainLayout.addWidget(self.userInputField, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the qline to layout (middle middle)
        self.userInputField.hide()
        # hides by default

        self.submitButton = QPushButton("Submit")
        # makes a new button to save the iput
        self.submitButton.setToolTip("Enter text")
        # tooltip
        self.submitButton.setFixedSize(60, 35)
        # sets size
        self.mainLayout.addWidget(self.submitButton, 3, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds the button to layout (middle right)
        self.submitButton.hide()
        # hides by default

    ### Song Detail Elements ###

        self.songDetailLayout = QGridLayout()
        # the layout all the song detail items sit in

        self.mainLayout.addLayout(self.songDetailLayout, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout to the 2nd to bottom row in the left column

        self.songCounter = QLabel()
        # details label
        self.songCounter.setMinimumSize(180, 60)
        # sets min size
        self.songCounter.setToolTip("Current DSI session stats")
        # tooltip
        self.songCounter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns text to the left
        self.songDetailLayout.addWidget(self.songCounter, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the counter

        self.globalSongCounter = QLabel()
        # global details label
        self.globalSongCounter.setMinimumSize(180, 60)
        # sets min size
        self.globalSongCounter.setToolTip("Global DSI stats")
        # tooltip
        self.globalSongCounter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns text to the left
        self.songDetailLayout.addWidget(self.globalSongCounter, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the global counter
        self.globalSongCounter.hide()
        # hides the stats by default

        self.historySongCounter = QLabel("")
        # spotify history details label
        self.historySongCounter.setMinimumSize(180, 60)
        # sets min size
        self.historySongCounter.setToolTip("Spotify account stats")
        # tooltip
        self.historySongCounter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # aligns text to the left
        self.songDetailLayout.addWidget(self.historySongCounter, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the historical counter
        self.historySongCounter.hide()
        # hides the stats by default

    ### Stat Load/Place ###

        self.globalStats = statsWriter("Init")
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
        
        self.globalSongCounter.setText(f"DSI Global Stats:\nSongs played: {globalSongsPlayed:,.0f}\nTime played: {globalTimeString} hours\nAverage duration: {globalAvgString}")
        # sets the counter text to match

        self.historicalStats = ""
        # empty string (loads at startup)

    ### Function Elements ###

        self.functionLayout = QGridLayout()
        # a layout that holds functional buttons
        self.mainLayout.addLayout(self.functionLayout, 3, 2, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout to the main in the mirrored spot bottom row, right column

        self.cycleStatsButton = QPushButton("Cycle Statistics")
        # a button to cycle between global and session statistics
        self.cycleStatsButton.setFixedSize(125, 50)
        # sets fixed size
        self.cycleStatsButton.setToolTip("Cycle between current/global DSI and Spotify account stats")
        # tooltip

        self.cycleStatsButton.clicked.connect(lambda: self.songDetails("Cycle"))
        # connects the button click to the details cycling
        self.cycleStatsButton.hide()
        # hides the button on start

        self.functionNestButton = QPushButton("Actions")
        # a button to display user-interactable action buttons in a nested window
        self.functionNestButton.setFixedSize(125, 50)
        # sets fixed size
        self.functionNestButton.setToolTip("Open the action button view")
        # tooltip

        self.functionNestButton.clicked.connect(lambda: self.openSubWindow("Action"))
        # connects the button click to the nested action window
        self.functionNestButton.hide()
        # hides the button on start

        self.buttonSpacer = QSpacerItem(80, 50)
        # a spacer item to gap the visual/functional buttons

        self.openFuncConfigButton = QPushButton("Configure")
        # a button to open the config launcher pad
        self.openFuncConfigButton.setFixedSize(125, 50)
        # sets fixed size
        self.openFuncConfigButton.setToolTip("Open the configuration launcher")
        # tooltip

        self.openFuncConfigButton.clicked.connect(lambda: self.openSubWindow("Config"))
        # connects the button click to the detail display
        self.openFuncConfigButton.hide()
        # hides the button on start

        self.openUriMapperButton = QPushButton("Run URIMapper")
        # a button to open the URI mapper
        self.openUriMapperButton.setFixedSize(125, 50)
        # sets fixed size
        self.openUriMapperButton.setToolTip("Run the URI mapping program")
        # tooltip

        self.openUriMapperButton.clicked.connect(self.openURImapper)
        # connects the button click to the program runner
        self.openUriMapperButton.hide()
        # hides the button on start

        self.functionLayout.addWidget(self.functionNestButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.functionLayout.addWidget(self.cycleStatsButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.functionLayout.addItem(self.buttonSpacer, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.functionLayout.addWidget(self.openFuncConfigButton, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)        
        self.functionLayout.addWidget(self.openUriMapperButton, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the buttons

    ### Action Elements ###

        self.currentSongInfoButton = QPushButton("Song Details")
        # a button to display API-level details about the song
        self.currentSongInfoButton.setFixedSize(125, 50)
        # sets fixed size
        self.currentSongInfoButton.setToolTip("Display details about the currently playing song")
        # tooltip

        self.currentSongInfoButton.clicked.connect(self.songDetailsWindow)
        # connects the button click to the detail display

        self.uriMapConfigureButton = QPushButton("Manipulate\nURI Map")
        # a button to manipulate the URI map
        self.uriMapConfigureButton.setFixedSize(125, 50)
        # sets fixed size
        self.uriMapConfigureButton.setToolTip("Open a window to modify the mapped URI entries")
        # tooltip

        self.uriMapConfigureButton.clicked.connect(lambda: self.openSubWindow("URI"))
        # connects the button click to the URI manipulation display

        self.pauseCPPbutton = QPushButton("Pause Discord Rich\nPresence Updates")
        # a button to (temporarily) pause the Discord Rich Presence updates until re-clicked
        self.pauseCPPbutton.setFixedSize(125, 50)
        # sets fixed size
        self.pauseCPPbutton.setToolTip("Places the Discord Rich Presence updates in a paused state\nThis program continues to work, but won't send data to the Discord API")
        # tooltip

        self.pauseCPPbutton.clicked.connect(self.pauseRPUpdates)
        # connects the button click to the C++ pausing function
        self.cppPauseStatus = False
        # boolean to store the C++ pause status in (True = updates paused, False = updating as per usual)

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

        self.spotifyStatusLabel = QPushButton("Spotify API")
        # the Spotify API status label (button)
        self.spotifyStatusLabel.setToolTip("Spotify API status indicator")
        # tooltip
        self.spotifyStatusLabel.setFixedSize(70, 30)
        # sets minimum size
        self.spotifyStatusLabel.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
        """)
        # makes the button itself invisible

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

        self.discordStatusLabel = QPushButton("Discord API")
        # the Discord API status label (button)
        self.discordStatusLabel.setToolTip("Discord API status indicator\nPress to restart the C++ process")
        # tooltip
        self.discordStatusLabel.setFixedSize(70, 30)
        # sets minimum size
        self.discordStatusLabel.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
        """)
        # makes the button itself invisible
        self.discordStatusLabel.clicked.connect(lambda: self.restarter("C++", True))
        # clicking calls the restarting function to restart C++ with True (restart, not just shut off)

        self.discordRPPauseLabel = QLabel("")
        # Discord Rich Presence pause status (warning, if the Discord API connection is paused manually)
        self.discordRPPauseLabel.setStyleSheet("""
            color: red;
            font-size: 9px;
        """)
        # makes it red, smaller than normal

        self.discordResetImageButton = QPushButton("Retry Images")
        # Discord image reset button
        self.discordResetImageButton.setToolTip("Try to resolve missing Discord activity images"
        "\nThis is visible because Discord may have had issues with one or more images"
        "\nPressing this simply resets the internal flag to allow the images to be sent again")
        # tooltip
        self.discordResetImageButton.clicked.connect(self.imageFailReset)
        # clicking calls the image reset function to tell C++ to reset the image bool(s)

        self.statusLayout.addWidget(self.spotifyStatusIcon, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.statusLayout.addWidget(self.spotifyStatusLabel, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.statusLayout.addWidget(self.discordStatusIcon, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.statusLayout.addWidget(self.discordStatusLabel, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.statusLayout.addWidget(self.discordRPPauseLabel, 2, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.statusLayout.addWidget(self.discordResetImageButton, 3, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all the buttons and their icons

        self.spotifyStatusIcon.hide()
        self.spotifyStatusLabel.hide()
        self.discordStatusIcon.hide()
        self.discordStatusLabel.hide()
        self.discordResetImageButton.hide()
        # hides the statuses until they become useful
    
    ### Blacklist Elements ###

        self.blacklistLayout = QGridLayout()
        # the layout all the blacklist items sit in

        self.blacklistButtonLayout = QGridLayout()
        # the layout the buttons sit in

        self.mainLayout.addLayout(self.blacklistLayout, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
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
        self.blacklistButtonLayout.addWidget(self.blacklistAddButton, 0, 2)
        # adds the add button to the right side
        self.blacklistAddButton.setToolTip("Blacklist current song")
        # tooltip
        self.blacklistAddButton.setMinimumSize(60, 40)
        # sets minimum size

        self.blacklistRemoveButton = QPushButton("Unblacklist")
        # the button that removes a song from the blacklist
        self.blacklistButtonLayout.addWidget(self.blacklistRemoveButton, 0, 2)
        # adds the remove button to the right side
        self.blacklistRemoveButton.setToolTip("Remove the current song from blacklist")
        # tooltip
        self.blacklistRemoveButton.setMinimumSize(60, 40)
        # sets minimum size

        self.blacklistManageButton = QPushButton("Manage")
        # the button to open the blacklist manager
        self.blacklistButtonLayout.addWidget(self.blacklistManageButton, 0, 1)
        # adds the manage button to the middle
        self.blacklistManageButton.setToolTip("Open the blacklist/favorite list manager")
        # tooltip
        self.blacklistManageButton.setMinimumSize(60, 40)
        # sets the minimum size

        self.blacklistStarButton = QPushButton("Favorite")
        # the button that favorites a song
        self.blacklistButtonLayout.addWidget(self.blacklistStarButton, 0, 0)
        # adds the star button to the left side
        self.blacklistStarButton.setToolTip("Favorite the current song")
        # tooltip
        self.blacklistStarButton.setMinimumSize(60, 40)
        # sets minimum size

        self.blacklistUnstarButton = QPushButton("Unfavorite")
        # the button that unfavorites a song
        self.blacklistButtonLayout.addWidget(self.blacklistUnstarButton, 0, 0)
        # adds the unstar button to the left side
        self.blacklistUnstarButton.setToolTip("Unfavorite the current song")
        # tooltip
        self.blacklistUnstarButton.setMinimumSize(60, 40)
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
        self.saveSignal.connect(self.stopper)
        # connects the save signal to the stopper function

    ### Blacklist Intermediary ###

        self.blacklistTag.connect(self.blacklistManager)
        # connects the blacklist tag to the blacklist manager
        self.blacklistTagFull.connect(self.blacklistManager)
        # connects the second blacklist tag to the blacklist manager
        self.blacklistAddButton.clicked.connect(lambda: self.blacklistIntermediary("Add"))
        # connects the add button to the intermediary function with command add
        self.blacklistRemoveButton.clicked.connect(lambda: self.blacklistIntermediary("Remove"))
        # connects the remove button to the intermediary function with command remove
        self.blacklistManageButton.clicked.connect(lambda: self.blacklistManager("Manage", "", ""))
        # connects the manage button to the intermediary function with command manage
        self.blacklistStarButton.clicked.connect(lambda: self.blacklistIntermediary("Star"))
        # connects the star button to the intermediary function with command star
        self.blacklistUnstarButton.clicked.connect(lambda: self.blacklistIntermediary("Unstar"))
        # connects the unstar button to the intermediary function with command unstar

    ### Line "Storage" ###

        self.multiLabel = False
        # sets the multi-string label to false to begin with
        self.lines = deque(maxlen = consoleLength)
        # creates a "deque" to hold lines (strings), to form a "pseudo-console"

    ### Window References ###

        self.configWindow = None
        self.uriWindow = None
        self.actionWindow = None
        # stores a referenceless placeholder for internal window classes

    ### Keybinds ###

        self.saveKeybind = QShortcut(QKeySequence("Ctrl+S"), self)
        # stores a keybind for Ctrl + S
        self.saveKeybind.activated.connect(lambda: self.stopper("Auto-Save"))
        # pressing Ctrl + S calls the auto-save function

    ### Run Arguments ###

        QTimer.singleShot(0, self.checkUpdate)
        # runs the GitHub update check
        QTimer.singleShot(0, self.requiredItemCheck)
        # runs the required items function to check IDs



### Update Checker ###

    def checkUpdate(self):
        """Function that checks if there's a new version of the program"""

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
                latestVersion = tuple(int(x) for x in latestTag.split("."))
                # splits the latest tag into a tuple of date elements (year num, month, day, hour/min)
                installedVersion = tuple(int(x) for x in self.version.split("."))
                # splits the current tag into a tuple of date elements

                if latestVersion > installedVersion:
                # latest is higher than current -> update
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
                elif latestVersion < installedVersion:
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

        self.blacklistButtons("init")
        # calls the blacklist button decider with init command (hides all buttons)

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

    def iconChanger(self, widget: str, status: str, style: str):
        """A function to change the status icons"""

        if style == "Icon":
        # called to change the icon

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
        
        else:
        # not an icon call -> show button
            self.discordResetImageButton.show()
            # unhides the reset image button

### Image Reset ###

    def imageFailReset(self):
        """A function to reset the C++ image fail states"""

        resetPacket = {
            "Playback State": True,
            "Reset Images": True
        }
        # simple packet with the critical info as True (progresses loop in C++ to get to the reset part)

        cppPackets(resetPacket)
        # calls the C++ packet sender function to do exactly that

        self.discordResetImageButton.hide()
        # hides the button again

### Pause Rich Presence ###

    def pauseRPUpdates(self):
        """A function to pause the C++ updates"""

        newState = not self.cppPauseStatus
        # grabs the opposite boolean as the state to set the pause state to (eg. if it's False (not paused) -> True (paused))

        pausePacket = {"Pause Updates": newState}
        # simple packet with the pause state boolean

        cppPackets(pausePacket)
        # calls the C++ packet sender function to do exactly that

        if newState:
        # True = paused
            self.pauseCPPbutton.setText("Resume Discord Rich\nPresence Updates")
            # changes text to indicate what the button will do next
            self.discordRPPauseLabel.setText("Discord RP Paused!")
            # shows the text
        else:
        # False = unpaused
            self.pauseCPPbutton.setText("Pause Discord Rich\nPresence Updates")
            # changes text to indicate what the button will do next
            self.discordRPPauseLabel.setText("")
            # hides the text

        self.cppPauseStatus = newState
        # updates the variable with the new state

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

        self.songCounter.setText(f"DSI Session Stats:\nSongs played: {trackCounter:,.0f}\nTime played: {formatTimePlayed}\nAverage duration: {avgString}")
        # sets the counter text to match

        if action == "Cycle":
        # if the action is to cycle between the counters
        # current DSI = 1, global DSI = 2, historical = 3
            if self.songCounter.isVisible():
            # if the song counter (session) is visible
                self.songCounter.hide()
                self.globalSongCounter.show()
                self.historySongCounter.hide()
                # hides the current DSI stats + historicals, displays global stats
            elif self.globalSongCounter.isVisible() and not disableShaa:
            # if the global song counter is visible and SHAA is configured (if not, there's no data to display in overall)
                self.songCounter.hide()
                self.globalSongCounter.hide()
                self.historySongCounter.show()
                # hides the global + current DSI stats, displays historical stats
            else:
            # neither = historical visible (or SHAA disabled -> skip historicals)
                self.songCounter.show()
                self.globalSongCounter.hide()
                self.historySongCounter.hide()
                # hides the historical stats + global DSI stats, displays current DSI stats

### Song Details Window ###

    def songDetailsWindow(self):
        """A function to display a small window containing song details"""

        info = QDialog(self)
        # makes a dialog window
        info.setWindowTitle(f"Details for {cppFull.get("Song Name", "N/A")}")
        # sets the window title based on currently variable-stored song
        info.resize(400, 120)
        # window size

        infoText = (f"Song: {cppFull.get("Song Name", "N/A")} by {cppFull.get("Artist Name", "N/A")}\n"
        f"Album: {cppFull.get("Album Name", "N/A")}\n"
        f"Spotify URI: {cppFull.get("URI", "N/A")}\n"
        f"Statistics: {cppFull.get("Playcount", "N/A")} plays, {cppFull.get("Playtime", "N/A")} minutes")
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

### Subservient Windows ###

    def openSubWindow(self, window: str):
        """Function to open an instantiated window"""

        if window == "Config":
        # requested window is the config window
            if self.configWindow:
            # if the window is defined
                self.configWindow.show()
                # shows the window to open configs
        elif window == "URI":
        # requested window is the URI manipulation window
            if self.uriWindow:
            # if the window is defined
                self.uriWindow.trackPlacer(250000)
                # calls the trackplacer to fill the table of tracks first
                self.actionWindow.hide()
                # hides the action window (to let the URI window go on top)
                self.uriWindow.show()
                # shows the window to modify URI mappings
        elif window == "Action":
        # requested window is the action window
            if self.actionWindow:
            # if the window is defined
                self.actionWindow.show()
                # shows the window to allow action calls

### URI Mapper Window ###

    def openURImapper(self):
        """Function to run the URI mapper in a thread"""

        def runURImapper():
            """Sub-function to actually run the executable"""
            uriMapper = subprocess.Popen([uriMapExePath], creationflags=subprocess.CREATE_NEW_CONSOLE)
            # opens as a subprocess, forces new console creation (since URImapper is a console-only program
            returnCode = uriMapper.wait()
            # waits for the mapper to finish (blocking), captures exit code

            self.labelSwap.emit(f"URI mapper finished, reloading map", 2)
            # user inform
            URIFileReader("Map")
            # calls the URI map reader to update the global variable
        
        threading.Thread(target=runURImapper, daemon=True).start()
        # a thread for the URI mapper to sit in, so that the UI doesn't freeze

### Auto-Scroll ###

    def autoScroll(self):
        """A function to scroll the 'console' to the bottom"""

        scroller = self.consoleScroll.verticalScrollBar()
        # definition
        scroller.setValue(scroller.maximum())
        # uses the max value (pushes to bottom)

### Blacklist Manager ###

    def blacklistManager(self, action:str, track:str, uri:str, favoriteDict:dict=None):
        """A function to manage the blacklist of songs"""
        global blacklist
        # global -> local

        if action == "New Song":
        # if the action is to check a new song (song changed)

            artist = csArtistName
            # grabs the artist name from the global variable
            if not csArtistName or csArtistName is None:
            # if the artist name is blank (None, thanks to Spotify)
                artist = "An Artist"
                # preset string
            
            device = f"Playing on {deviceName}"
            # grabs the device name from the global variable
            if not deviceName or deviceName is None:
            # if the device name is blank (None, thanks to Spotify)
                device = ""
                # empty string
            
            volume = f"at {volumeLevel}%"
            # grabs the volume level from the global variable
            if not volumeLevel or volumeLevel is None:
            # if the volume level is blank (None, thanks to Spotify)
                volume = ""
                # empty string

            if uri in blacklist:
            # if the passed URI exists in the blacklist
                status = blacklist[uri]["status"]
                # grabs the stored "status" of the uri (starred, blacklisted)
                if status == "blacklisted":
                # song blacklisted
                    newSong = favoriteDict.get("Song")
                    # gets the new display song's name
                    newArtist = favoriteDict.get("Artist Name")
                    # gets the new display artist's name
                    self.blacklistSongName.setText(f"\nPlaying Blacklisted:\n{track} by {artist}\nDisplaying:\n{newSong} by {newArtist}")
                    # displays blacklisted view
                elif status == "starred":
                # song favorited
                    self.blacklistSongName.setText(f"\nPlaying Favorited:\n{track} by {artist}\n\n{device} {volume}")
                    # displays favorited view
                else:
                # song status none
                    self.blacklistSongName.setText(f"\nCurrently Playing:\n{track} by {artist}\n\n{device} {volume}")
                    # displays default view
            else:
            # if the URI doesn't exist in the blacklist
                status = "none"
                # sets the status to none
                self.blacklistSongName.setText(f"\nCurrently Playing:\n{track} by {artist}\n\n{device} {volume}")
                # displays default view

        elif action == "Remove" or action == "Unstar":
        # if the action is to remove the song from the blacklist or unfavorite it
            blacklist.pop(uri)
            # removes the URI from the blacklist
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
            if len(blacklist) >= 60:
            # if there's already over 60 items in the blacklist 
            # generally speaking, intended to be 50 blacklist + 10 whitelist, but if filling blacklist first, then whitelist, allows for 70
                self.labelSwap.emit(f"Can't blacklist {track}, list is too long!", 3)
                # user inform
            else:
            # not more than 60 items yet
                blacklist[uri] = {"status": "blacklisted", "info": blacklistInfo}
                # sets the blacklist entry for the URI to blacklisted (status + info dictionary)
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

        elif action == "Manage":
        # if the action is to manage the blacklist/favorite list
            self.blacklistManagerWindow()
            # runs the window
            return
            # doesn't run the button function

        elif action == "Init":
        # if the action is to start (first call)
            self.blacklistManageButton.show()
            self.blacklistSongName.show()
            # enables the song name field + manage button
            return
            # doesn't run the button function yet (it'll get ran a couple seconds later)

        self.blacklistButtons(status)
        # calls the blacklist button manager to hide/show the relevant buttons for the song

### Blacklist Manager Window ###

    def blacklistManagerWindow(self):
        """Function that displays a blacklist manager window"""
        manager = QDialog(self)
        # makes a dialog window
        manager.setWindowTitle(f"DSI Blacklist Manager")
        # sets the window title
        manager.setMinimumSize(600, 500)
        # sets a minimum size
        manager.resize(600, 500)
        # window size

        managerLayout = QVBoxLayout(manager)
        # layout for the blacklist manager

        favoriteLabel = QLabel("Favorite Tracks")
        favoriteLabel.setStyleSheet("font-weight: bold; font-size: 14px;")
        favoriteLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # title for the favorite tracks

        favoriteScrollWidget = QWidget()
        # a widget for the scroll area to sit in
        favoriteLayout = QVBoxLayout(favoriteScrollWidget)
        # layout for the favorite tracks

        favoriteScroll = QScrollArea()
        # adds a scroll area
        favoriteScroll.setWidget(favoriteScrollWidget)
        favoriteScroll.setWidgetResizable(True)
        # sets the scroll area to use the scroll widget

        managerLayout.addWidget(favoriteLabel)
        managerLayout.addWidget(favoriteScroll, 1)
        # adds the label and layout to main

        blacklistLabel = QLabel("Blacklisted Tracks")
        blacklistLabel.setStyleSheet("font-weight: bold; font-size: 14px;")
        blacklistLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # title for the blacklist tracks

        blacklistScrollWidget = QWidget()
        # a widget for the scroll area to sit in
        blacklistLayout = QVBoxLayout(blacklistScrollWidget)
        # layout for the blacklisted tracks

        blacklistScroll = QScrollArea()
        # adds a scroll area
        blacklistScroll.setWidget(blacklistScrollWidget)
        blacklistScroll.setWidgetResizable(True)
        # sets the scroll area to use the scroll widget

        managerLayout.addWidget(blacklistLabel)
        managerLayout.addWidget(blacklistScroll, 1)
        # adds the label and layout to main

        for uri, trackDict in blacklist.items():
        # goes through the blacklist, gets the URIs
            status = trackDict["status"]
            # gets the status (starred, blacklisted, none)
            name = trackDict["info"]["Song Name"]
            # gets the name of the song
            artist = trackDict["info"]["Artist Name"]
            # gets the artist of the song
            track = f"{name} by {artist}"
            # forms a string of the name and artist

            if status == "starred":
            # if the status is starred (favorited)

                rowWidget = QWidget()
                # a widget that can be deleted
                row = QHBoxLayout(rowWidget)
                # makes a new row layout for the track
                trackLabel = QLabel(track)
                trackLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                # adds a label, enforces the sizing rules

                trackButton = QPushButton("Unstar")
                # adds a button to unstar the item
                trackButton.clicked.connect(lambda _, n=name, u=uri, widget=rowWidget: (self.blacklistManager("Unstar", n, u), widget.deleteLater()))
                # connects the button to removing the URI from the blacklist + deleting the row from the window
                # captures the button state pass (doesn't store, not needed), name of the track, URI and the widget holding the row, so that they can be deleted

                row.addWidget(trackLabel)
                row.addWidget(trackButton)
                # adds the label and button to the layout
                favoriteLayout.addWidget(rowWidget)
                # adds the layout to the favorite layout

            elif status == "blacklisted":
            # if the status is blacklisted

                rowWidget = QWidget()
                # a widget that can be deleted
                row = QHBoxLayout(rowWidget)
                # makes a new row layout for the track
                trackLabel = QLabel(track)
                trackLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                # adds a label, enforces the sizing rules

                trackButton = QPushButton("Unblacklist")
                # adds a button to unblacklist the item
                trackButton.clicked.connect(lambda _, n=name, u=uri, widget=rowWidget: (self.blacklistManager("Remove", n, u), widget.deleteLater()))
                # connects the button to removing the URI from the blacklist + deleting the row from the window

                row.addWidget(trackLabel)
                row.addWidget(trackButton)
                # adds the label and button to the layout
                blacklistLayout.addWidget(rowWidget)
                # adds the layout to the favorite layout

        closeButton = QPushButton("Close")
        # button to close the window
        closeButton.clicked.connect(manager.accept)
        # connects the button to closing the manager window

        managerLayout.addWidget(closeButton)
        # adds the close button

        manager.exec()
        # executes (shows)

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
            self.blacklistManageButton.hide()
            self.blacklistSongName.hide()
            # hides the song name field and the manage button, too

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

### Program Restart Helper ###

    def restartHelper(self, status: bool):
        """A function to transition the UI from running to restart-able or from a restart call back to running"""

        if status:
        # status = True means restart -> running
            if hasattr(self, "restartTimer"):
            # checks if there's an auto-restart timer
                self.restartTimer.stop()
                # calls to stop it (prevent double-restart call)
                self.restartTimer.deleteLater()
                # calls to delete it 
            self.exitLayout.removeWidget(self.restartButton)
            # removes the restart button from the exit layout
            self.exitButton.setFixedSize(200, 50)
            # modifies the exit button size to fit alone
            self.restartButton.hide()
            # hides the restart button
            restartStart()
            # calls the function that resets all global thread references
            startStart()
            # calls the very starting function
        else:
        # status = False means running -> restart
            self.exitLayout.addWidget(self.restartButton, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the restart button to the exit layout
            self.exitButton.setFixedSize(90, 50)
            # modifies the exit button size to accomodate both buttons
            self.restartButton.show()
            # displays the restart button
            self.labelSwap.emit(f"All subprocesses closed, restart ready!", 3)
            # user inform on new status
            if autoRestart:
            # if the automatic restarting is enabled
                self.restartTimestamp = datetime.fromtimestamp(time.time() + 1800)
                # forms a timestamp for when the automatic restart should happen
                self.restartTimer = QTimer()
                # makes a QT timer
                self.restartTimer.setSingleShot(True)
                # sets the timer to only go off once
                self.restartTimer.timeout.connect(lambda: self.restartHelper(True))
                # connects the timer "timeout" (stop) to the restart helper (this function) with True call
                restartTimestampHuman = self.restartTimestamp.strftime("%H:%M:%S")
                # "translates" the timestamp from UNIX float to 'human-readable' time
                self.labelSwap.emit(f"Automatic restart scheduled for {restartTimestampHuman}!", 3)
                # user inform on pending auto-restart
                self.restartTimer.start(1800000)
                # starts the timer with 1,800,000 milliseconds (1800 seconds)

### Program Closer ###

    def stopper(self, severity: str):
        """A function to close the program gracefully, saving progress"""
        global blacklist, maplessURIs, stopLooper, lastDSIsave
        # global -> local

        self.labelSwap.emit("Saving DSI statistics...", 3)
        # user update

        self.blacklistWriter()
        # calls the blacklist writer to save the blacklist
        if enableMapping:
        # if mapping is enabled
            uriWriter(maplessURIs)
            # calls the URI writer with the current list of URIs to save it
        statsWriter("Save")
        # calls the statistics writer with Save

        lastDSIsave = time.time()
        # saves the last time DSI was saved (prevents really fast updates)

        if severity != "Auto-Save":
        # if the severity isn't to use as a save function
            if severity == "Shut Down":
            # call to shut down
                self.labelSwap.emit("Shutting down...", 3)
                # user update
            elif severity == "Restart":
            # call to restart prep
                self.labelSwap.emit("Preparing program for restart-ready state...", 3)
                # user update

            self.restarter("Song", False)
            # calls the restart function to shut down the song thread
            self.restarter("C++", False)
            # calls the restart function (with False for restart arg) to shut down the Discord subprocess
            self.restarter("Picture", False)
            # calls the restart function to shut down the picture thread

            if severity == "Shut Down":
            # called to shut down
                self.mainConfigWrite()
                # ensures the config is up-to-date with position and location data
                self.close()
                # closes the window
                startApp.quit()
                # quits the application
                raise SystemExit
                # stops everything

            elif severity == "Restart":
            # called to prepare for a restart
                stopLooper = True
                # sets the bool to True, killing looper in approx. 1 refresh cycle or less
                self.restarter("Main", False)
                # calls the restart function to shut down the main thread
                self.restartHelper(False)
                # calls the helper with False (not restarting, just preparing)

### Program Component Restarter ###

    def restarter(self, function: str, status: bool):
        """A function to restart specific functions in case they fail"""
        global cppThread, songThread, picThread, mainThread
        # global -> local

        if function == "C++":
        # if the passed function is the C++ thread 
            cppThreadEvent.set()
            # tells the cppThread to stop
            if cppThread.is_alive():
            # checks if the thread is alive
                try:
                # in try (prone to crashing)
                    self.labelSwap.emit("Waiting for the Discord component to shut down...", 3)
                    # user update
                    while cppThread.is_alive():
                    # while the C++ thread is still active
                        for attempt in range(25):
                        # tries 25 times (5 seconds)
                            cppThread.join(timeout=0.2)
                            # waits 0.2 seconds per attempt to check if the thread is dead already 
                            startApp.processEvents()
                            # lets the window UI keep updating (prevents freezing)
                        break
                        # after attempts, breaks
                except RuntimeError:
                # if it fails
                    pass
                    # moves on
            if status:
            # if the bool is True, and it's asking to restart (not just turn off)
                cppThread = None
                # resets the thread reference
                cppThreadEvent.clear()
                # clears the flag that was set
                cppThread = threading.Thread(target = runCpp, daemon=True, args=(cppThreadEvent,))
                # creates a thread for the C++ program to run in - this way it won't stop the main process
                cppThread.start()
                # starts the thread
        
        elif function == "Song":
        # if the passed function is the Song thread
            songThreadEvent.set()
            # stops it by setting the flag
            if songThread.is_alive():
            # checks if the thread is still alive
                try:
                # in try (prone to crashing)
                    while songThread.is_alive():
                    # while the song thread is still active
                        for attempt in range(25):
                        # tries 25 times (5 seconds)
                            songThread.join(timeout=0.2)
                            # waits 0.2 seconds per attempt to check if the thread is dead already
                            startApp.processEvents()
                            # lets the window UI keep updating (prevents freezing)
                        break
                        # after attempts, breaks
                except RuntimeError:
                # if it fails
                    pass
                    # moves on
            if status:
            # if the bool is True, and it's asking to restart (not just turn off)
                songThread = None
                # resets the thread reference
                songThreadEvent.clear()
                # clears the flag that was set
                songThread = threading.Thread(target = song, daemon=True, args=(pictureQueue, songThreadEvent,))
                # creates the song thread
                songThread.start()
                # starts the thread

        elif function == "Picture":
        # if the passed function is the pic thread
            if picThread.is_alive():
            # checks if the thread is still alive
                try:
                    while picThread.is_alive():
                    # while the picture thread is still active
                        for attempt in range(25):
                        # tries 25 times (5 seconds)
                            picThread.join(timeout=0.2)
                            # waits 0.2 seconds per attempt to check if the thread is dead already
                            startApp.processEvents()
                            # lets the window UI keep updating (prevents freezing)
                        break
                        # after attempts, breaks
                except RuntimeError:
                # if it fails
                    pass
                    # moves on

        elif function == "Main":
        # if the passed function is the main thread
            if mainThread.is_alive():
            # checks if the thread is still alive
                try:
                    while mainThread.is_alive():
                    # while the main thread is still active
                        for attempt in range(25):
                        # tries 25 times (5 seconds)
                            mainThread.join(timeout=0.2)
                            # waits 0.2 seconds per attempt to check if the thread is dead already
                            startApp.processEvents()
                            # lets the window UI keep updating (prevents freezing)
                        break
                        # after attempts, breaks
                except RuntimeError:
                # if it fails
                    pass
                    # moves on

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
        global spotifyClientID, spotifyClientSecret, spotifyRedirect, discordAppID
        # global -> local

        try:
        # tries to grab the IDs and such
            spotifyClientID = secretConfig["Spotify_Client_ID"]
            spotifyClientSecret = secretConfig["Spotify_Client_Secret"]
            spotifyRedirect = secretConfig["Spotify_Redirect_URI"]
            discordAppID = secretConfig["Discord_Application_ID"]
            # updates all the global variables
            self.labelSwap.emit("All required items loaded successfully, proceeding...", 0)
            # user update
            self.configsLoadCheck()
            # moves to next stage
        except:
        # if it fails (something's wrong with the file/input)
            self.requiredItemsFail(2)
            # calls the fail function to reconstruct

    def requiredItemsFail(self, state):
        """A function to handle missing required items (re-input)"""
        global secretConfig, spotifyClientID, spotifyClientSecret, spotifyRedirect, discordAppID
        # global -> local

        if state == 1:
        # state 1 is no file exists (first time or deleted file)
            self.labelSwap.emit("No required config found, please enter required information:", 0)
            # user inform

            spotifyClientID = self.requiredItemInput("Spotify_Client_ID")
            secretConfig["Spotify_Client_ID"] = spotifyClientID
            # stores the client ID 

            spotifyClientSecret = self.requiredItemInput("Spotify_Client_Secret")
            secretConfig["Spotify_Client_Secret"] = spotifyClientSecret
            # stores the client secret

            spotifyRedirect = self.requiredItemInput("Spotify_Redirect_URI")
            secretConfig["Spotify_Redirect_URI"] = spotifyRedirect
            # stores the redirect URL

            discordAppID = self.requiredItemInput("Discord_Application_ID")
            secretConfig["Discord_Application_ID"] = discordAppID
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
                spotifyClientID = secretConfig["Spotify_Client_ID"]
            except:
            # if it can't
                spotifyClientID = self.requiredItemInput("Spotify_Client_ID")
                # calls the input field to grab a new one instead
                secretConfig["Spotify_Client_ID"] = spotifyClientID
                # stores the client ID 
            try:
            # tries to grab the item from stored config
                spotifyClientSecret = secretConfig["Spotify_Client_Secret"]
            except:
                spotifyClientSecret = self.requiredItemInput("Spotify_Client_Secret")
                # calls the input field to grab a new one instead
                secretConfig["Spotify_Client_Secret"] = spotifyClientSecret
                # stores the client secret
            try:
            # tries to grab the item from stored config
                spotifyRedirect = secretConfig["Spotify_Redirect_URI"]
            except:
                spotifyRedirect = self.requiredItemInput("Spotify_Redirect_URI")
                # calls the input field to grab a new one instead
                secretConfig["Spotify_Redirect_URI"] = spotifyRedirect
                # stores the redirect URL

            try:
            # tries to grab the item from stored config
                discordAppID = secretConfig["Discord_Application_ID"]
            except:
                discordAppID = self.requiredItemInput("Discord_Application_ID")
                # calls the input field to grab a new one instead
                secretConfig["Discord_Application_ID"] = discordAppID
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

        self.configsLoadCheck()
        # moves to next stage

    def requiredItemInput(self, field):
        """Function to prompt user for a required item"""

        self.userInputField.setText("")
        # clears the text

        if field == "Spotify_Client_ID":
        # if the requested field is spotify client id
            fieldString = "Spotify Client ID"
            # forms a user-readable string

        elif field == "Spotify_Client_Secret":
        # if the requested field is
            fieldString = "Spotify Client Secret"
            # forms a user-readable string

        elif field == "Spotify_Redirect_URI":
        # if the requested field is
            fieldString = "Spotify Redirect URI"
            # forms a user-readable string

        elif field == "Discord_Application_ID":
        # if the requested field is discord app id
            fieldString = "Discord Application ID"
            # forms a user-readable string

        self.labelSwap.emit(f"Please enter your {fieldString}", 0)
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

    def configRun(self, config: str) -> dict | None: 
        """Function to read the configuration files"""

        if config == "Function":
        # function config load call

            if os.path.exists(funcConfigPath):
            # if the functionality-related config exists
                self.labelSwap.emit("Found functionality configuration, reading...", 0)
                # user update
                try:
                # tries to open the json file
                    with open(funcConfigPath, "r", encoding="utf-8") as fncCfg:
                    # opens the config file in read mode
                        functionConfig = json.load(fncCfg)
                        # stores the loaded json file as functionConfig
                        return functionConfig
                        # returns the config
                except Exception as err:
                # if there's an error
                    self.labelSwap.emit(f"Error reading the functional configuration file: {err}", 2)
                    # user inform
                    return None
                    # None return
            else:
            # config doesn't exist
                return None
                # None return

        elif config == "DSI":
        # DSI visual config load call

            if os.path.exists(dsiConfigPath):
            # checks if the config already exists (not first time) and the skipping is enabled
                self.labelSwap.emit("Found customisation configuration, reading...", 0)
                # user update
                try:
                # tries to open the json file
                    with open(dsiConfigPath, "r", encoding="utf-8") as jsCfg:
                    # opens the config file in read mode
                        dsiVisualConfig = json.load(jsCfg)
                        # stores the loaded json file as jsonConfig
                        return dsiVisualConfig
                        # returns the config
                except Exception as err:
                # if there's an error
                    self.labelSwap.emit(f"Error reading the DSI visual configuration file: {err}", 2)
                    # user inform
                    return None
                    # None return
            else:
            # if the dsi configuration doesn't exist
                return None
                # None return

        elif config == "SHAA":
        # SHAA config load call

            if os.path.exists(shaaConfigPath):
            # if the shaa configuration file does exist
                try:
                # tries to read the SHAA config file (try because it's not necessary, can be skipped)
                    with open(shaaConfigPath, "r", encoding="utf-8") as shaaCfg:
                    # opens the SHAA config
                        shaaConfig = json.load(shaaCfg)
                        # stores the loaded config
                        return shaaConfig
                        # returns the config
                except:
                # if the file can't be opened
                    self.labelSwap.emit(f"Error reading the SHA addon configuration file: {err}", 0)
                    # user update
                    return None
                    # None return
            else:
            # if the file doesn't exist
                return None
                # None return

### Config Load Sequence ###

    def configsLoadCheck(self):
        """Function that loads the configs in sequence and checks their validity"""
        global functionConfig, dsiVisualConfig, shaaConfig, skipConfigWindow
        # global -> local

    ### Functional ###

        functionConfig = self.configRun("Function")
        # runs the config runner and grabs the returned config

        if functionConfig is not None:
        # if the reader returned a config, not just None
            skipConfigWindow = functionConfig.get("disableCfgWin", False)
            # whether to prompt user with config window or not, boolean
            if skipConfigWindow:
            # if the boolean is True
                self.labelSwap.emit("Configuration found and skipping is enabled, proceeding...", 0)
                # user update

            if functionConfig.get("autoSaveTimer") is None or functionConfig.get("autoRestart") is None or functionConfig.get("savePosData") is None:
            # if any of the latest config option additions don't exist in the file
                skipConfigWindow = False
                # forces the variable off, to force a config check from user

        if functionConfig is None or not skipConfigWindow:
        # if the file doesn't exist, needs to be re-configured or the boolean to skip the config is off
            self.hide()
            # hides the mainWindow (otherwise appears frozen)
            mainConfig = subprocess.run([funcConfigExePath], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            # runs the functionality configurator (as blocking), continues task once it's done writing config
            if not mainConfig.returncode == 1:
            # checks if the return code isn't 1
                self.show()
                # re-shows itself
                self.labelSwap.emit(f"Configuration complete, proceeding...", 0)
                # sends the return code
                functionConfig = self.configRun("Function")
                # re-runs the config read for the functional config

    ### DSI Visual ###

        dsiVisualConfig = self.configRun("DSI")
        # runs the config runner and grabs the returned config

        if dsiVisualConfig is None or not skipConfigWindow:
        # if the file doesn't exist, needs to be re-configured or the boolean to skip the config is off
            self.hide()
            # hides the mainWindow (otherwise appears frozen)
            dsiConfig = subprocess.run([dsiConfigExePath], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            # runs the DSI configurator (as blocking), continues task once it's done writing config
            if not dsiConfig.returncode == 1:
            # checks if the return code isn't 1
                self.show()
                # re-shows itself
                self.labelSwap.emit(f"Customisation configuration complete, proceeding...", 0)
                # sends the return code
                dsiVisualConfig = self.configRun("DSI")
                # re-runs the config read for the DSI visual config

    ### SHAA Config ###

        nextTimer = 50
        # timer starts at 50 (ms)

        shaaConfig = self.configRun("SHAA")
        # runs the config runner and grabs the returned config

        if shaaConfig is None or not skipConfigWindow:
        # if the file doesn't exist, needs to be re-configured or the boolean to skip the config is off
            self.hide()
            # hides the mainWindow (otherwise appears frozen)
            shaCfg = subprocess.run([shaaConfigExePath], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            # runs the SHAA configurator (as blocking), continues task once it's done writing config
            if not shaCfg.returncode == 1:
            # checks if the return code isn't 1
                self.show()
                # re-shows itself
                self.labelSwap.emit(f"SHAA configuration complete, proceeding...", 0)
                # sends the return code
                shaaConfig = self.configRun("SHAA")
                # re-runs the config read for the SHA addon config

        QTimer.singleShot(nextTimer, self.mainConfigLoad)
        # runs the next stage

### Config Write ###

    def mainConfigWrite(self):
        """Function that writes the config with changes"""
        global functionConfig
        # global -> local

        if savePosData:
        # if saving window position/size data is enabled

            dsiWidth = self.window().size().width()
            dsiHeight = self.window().size().height()
            # grabs the current window size
            dsiPosX = self.window().pos().x()
            dsiPosY = self.window().pos().y()
            # grabs the current window position

            widthOffsetBool = (abs(dsiWidth - self.windowSizeX) < self.windowSizeX * 0.05)
            heightOffsetBool = (abs(dsiHeight - self.windowSizeY) < self.windowSizeY * 0.05)
            # checks if the current window size and the stored size are within 5%
            xPosOffsetBool = (abs(dsiPosX - self.windowPosX) < 10)
            yPosOffsetBool = (abs(dsiPosY - self.windowPosY) < 10)
            # checks if the current window position and the stored position are within 10px

            if not (widthOffsetBool and heightOffsetBool and xPosOffsetBool and yPosOffsetBool):
            # checks whether the window has remained in largely the same position/hasn't been resized
                try:
                # tries (opening, modifying and closing file could fail, better safe than sorry)
                    with open(funcConfigPath, "r", encoding="utf-8") as fncCfg:
                    # opens the config file in read mode
                        functionConfig = json.load(fncCfg)
                        # stores the loaded json file as functionConfig

                    functionConfig["DSIwidth"] = dsiWidth
                    functionConfig["DSIheight"] = dsiHeight
                    # grabs the current window sizes (X and Y)
                    functionConfig["DSIxPos"] = dsiPosX
                    functionConfig["DSIyPos"] = dsiPosY
                    # grabs the current window positions (X and Y)

                    with open(funcConfigPath, "w", encoding="utf-8") as fncCfg:
                    # opens the config file location
                        json.dump(functionConfig, fncCfg, indent=3)
                        # writes to file
                except:
                # if it does fail
                    None
                    # does nothing (saving the positions/sizes is a QoL thing that can be discarded)

### Config Load ###
    
    def mainConfigLoad(self):
        """Function that loads and captures the config options"""
        global refreshTime, enablePause, pauseStateText, enableUpdates, enableErrors
        global enableMapping, timestampStyle, startTime, consoleLength, hostData, addressType
        global autoSaveTimer, autoRestart, savePosData
        # global -> local

        refreshTime = functionConfig.get("refreshTime", 10.0)
        # grabs the refresh time from config
        try:
        # tries to
            refreshTime = float(refreshTime)
            # turns the time into a float
        except:
        # if it fails
            refreshTime = 10.0
            # fallback value of 10.0

        enablePause = bool(dsiVisualConfig.get("enablePause", True))
        pauseStateText = str(dsiVisualConfig.get("pauseText", "Paused on:"))
        enableUpdates = bool(functionConfig.get("printUpdates", True))
        enableErrors = bool(functionConfig.get("printErrors", True))
        enableMapping = bool(functionConfig.get("enableURI", True))
        timestampStyle = str(functionConfig.get("clockStyle", "Uptime"))
        consoleLength = int(functionConfig.get("consoleLength", 25))
        hostData = bool(functionConfig.get("hostData", True))
        addressType = str(functionConfig.get("addressType", "Device"))
        autoSaveTimer = int(functionConfig.get("autoSaveTimer", 2))
        autoRestart = bool(functionConfig.get("autoRestart", True))
        savePosData = bool(functionConfig.get("savePosData", True))
        self.windowSizeX = int(functionConfig.get("DSIwidth", self.windowSizeX))
        self.windowSizeY = int(functionConfig.get("DSIheight", self.windowSizeY))
        self.windowPosX = int(functionConfig.get("DSIxPos", self.windowPosX))
        self.windowPosY = int(functionConfig.get("DSIyPos", self.windowPosY))
        # loads all options from configs

        self.labelSwap.emit("Main configuration loaded, proceeding...", 0)
        # user update
        QTimer.singleShot(500, self.customConfigLoad)
        # runs the next stage

    def customConfigLoad(self):
        """Function that loads and stores the customisation config options"""
        global smallURL, spotifyURL, songNameSpacerL, songNameSpacerR, preText, postText, enableSong, enableArtist, enableAlbum, albumFallback, picCycleList
        # global -> local

        smallURL = dsiVisualConfig.get("smallPicURL", None)
        if smallURL is None:
        # if the smallURL is empty
            smallURL = "https://github.com/EllEff-Git/Discord-Spotify-Integration"
            # shameless plug <3 (only applies if there's no defined URL)
        spotifyURL = str(dsiVisualConfig.get("spotifyURLType", "Track"))
        songNameSpacerL = str(dsiVisualConfig.get("spacerL", "\u227a"))
        songNameSpacerR = str(dsiVisualConfig.get("spacerR", "\u227b"))
        preText = str(dsiVisualConfig.get("preText", ""))
        postText = str(dsiVisualConfig.get("postText", ""))
        enableSong = bool(dsiVisualConfig.get("enableSong", True))
        enableArtist = bool(dsiVisualConfig.get("enableArtist", True))
        enableAlbum = bool(dsiVisualConfig.get("enableAlbum", True))
        albumFallback = str(dsiVisualConfig.get("albumFallback", "A playlist"))
        picCycleList = str(dsiVisualConfig.get("pictureCycleType", "Spotify"))
        # grabs each option from config, loads into global var

        self.labelSwap.emit("Customisation configurations loaded, proceeding...", 0)
        # user update
        QTimer.singleShot(500, self.finalConfigLoad)
        # runs the next stage

    def finalConfigLoad(self):
        """Function that loads the last part of the config"""
        global picCycleList, picCycleTime, picCycleType, smallPic, hoverText
        # global -> local

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

        picCycleTime = int(dsiVisualConfig.get("pictureCycleTime", 10))
        # grabs the cycle time
        try:
        # tries to turn the time into minutes (ensures integer type, multiplies by 60)
            picCycleTime = (int(picCycleTime) * 60)
        except:
        # if it can't
            picCycleTime = 600
            # sets to default of 10 minutes

        picCycleType = str(dsiVisualConfig.get("pictureCycleBehavior", "Random"))
        smallPic = str(dsiVisualConfig.get("smallPic", ""))
        hoverText = str(dsiVisualConfig.get("smallPicHover", "Spotify"))
        # loads last settings

        QTimer.singleShot(500, self.shaaConfigLoad)
        # calls the shaa config loader

### SHAA Config Load ###

    def shaaConfigLoad(self):
        """Function to load and store the SHAA config options"""
        global songInfoField1, songInfoField2, shaaFallbackTotal, shaaFallback, shaaInfoDetails, songInfoFallback
        global songInfoFormatPlays, songInfoSpacer, songInfoFormatMins, songInfoFormatTextFirst, songInfoFormatDetails
        global songInfoFormatDetailsSpacer, songInfoDetailsDoubleSpace, dsiShoutout
        global enableFirstTime, firstTimeFormat, enableTopHour, topHourFormat, enableTopItems
        # a lot of global -> local

        if not disableShaa:
        # if the SHAA-related stuff isn't disabled

            songInfoField1 = str(shaaConfig.get("songInfoField1", "Track"))
            songInfoField2 = int(shaaConfig.get("songInfoField2", 0))
            shaaFallbackTotal = bool(shaaConfig.get("songInfoFallbackTotal", True))
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
            # if the field isn't custom
                songInfoFallback = "total"
                # uses "total" as an additional string

            songInfoFormatDetails = str(shaaConfig.get("songInfoDetailsText", "Total Hours"))
            songInfoFormatPlays = str(shaaConfig.get("songInfoFormatPlays", "plays"))
            songInfoSpacer = str(shaaConfig.get("songInfoFormatSpacer", "\u203b"))
            songInfoFormatMins = str(shaaConfig.get("songInfoFormatMins", "minutes"))
            songInfoFormatTextFirst = bool(shaaConfig.get("songInfoDetailsTextFirst", True))
            songInfoFormatDetailsSpacer = str(shaaConfig.get("songInfoDetailsSpacer", ":"))
            songInfoDetailsDoubleSpace = bool(shaaConfig.get("songInfoDetailsDoubleSpace", False))
            enableFirstTime = bool(shaaConfig.get("enableFirstTime", True))
            firstTimeFormat = str(shaaConfig.get("firstTimeFormat", "Listening for the first time!"))
            enableTopHour = bool(shaaConfig.get("enableTopHour", False))
            topHourFormat = str(shaaConfig.get("topHourFormat", "Listening at peak hours"))
            enableTopItems = bool(shaaConfig.get("enableTopTracks", True))
            dsiShoutout = bool(shaaConfig.get("dsiShoutout", True))
            # grabs everything from config

        else:
        # if the disableShaa is set to True
            None
            # does nothing, because those settings are already set above

        QTimer.singleShot(150, self.updateWarning)
        # calls the next stage (warnings regarding missing error logging)

### Update Prints ###

    def updateWarning(self):
        if not enableUpdates:
        # if console printing is disabled in config
            self.labelSwap.emit("Info logging disabled in config", 0)
            # user update
            QTimer.singleShot(1000, self.errorWarning)
            # calls the error warning function
        else:
            QTimer.singleShot(50, self.errorWarning)
            # calls the error warning function

### Error Prints ###

    def errorWarning(self):
        if not enableErrors:
        # if error printing is disabled in config
            self.labelSwap.emit("Error logging disabled in config", 0)
            # user update
            QTimer.singleShot(1000, self.idWriter)
            # calls the next stage (id writer)
        else:
            QTimer.singleShot(50, self.idWriter)
            # calls the next stage (id writer)

### Time String ###

    def Time(self):
        """Function that returns the time formatted"""
        if timestampStyle == "Uptime":
        # if the config option is set to uptime
            currentTime = int(datetime.now().timestamp())
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
            return (datetime.now().strftime("%H:%M:%S") + " ")
            # shortens the call to current system timestamp, adds empty space

        else:
        # if the config option is set to something else, reads as off (thus doesn't add anything)
            return ""
        
### ID Writer ###

    def idWriter(self):
        """Function for writing the discordIDs.json file"""
        # these are things the C++ program uses "statically" (they can't change during operation)

        content = {
            "Discord Application ID": discordAppID,
            "Small Image Filename": smallPic,
            "Album Fallback": albumFallback,
            "Version": f"v{DSIver}"
        }
        # makes a dictionary from the relevant config options

        with open(idDir, "w", encoding="utf-8") as idJsn:
        # opens the discordIDs.json file
            json.dump(content, idJsn, indent=2)
            # writes the config to file

            if enableUpdates:
            # if updates are enabled
                self.labelSwap.emit("Updated ID file for Discord...", 0)
            # writes the string to discordIDs.json at program launch

        if not disableShaa:
        # if SHAA compat isn't disabled
            QTimer.singleShot(150, self.timeGrabber)
            # calls the next stage (timeGrabber)
        else:
        # if SHAA compat is disabled
            QTimer.singleShot(1000, self.readyStateReadier)
            # skips timeGrabber

### Total Time Grabber ###

    def timeGrabber(self, forceRefresh: bool = False):
        """Function that grabs the total time counts from totalTimes file"""
        global totalHours, totalMinutes, totalSeconds, totalPlays, totalAverage, topHour, disableShaa
        global topTracks, topArtists, topAlbums
        # global -> local

        nextTimer = 1000
        # a 1-second timer to move to next stage (2.5 if no file found)
        totalDict = None
        # starts off as None

        if (totalDict is None) or (forceRefresh):
        # if the times haven't been loaded yet or it's a force refresh request (prevents re-assigning mid-run)
            self.labelSwap.emit("Grabbing SHA details from file...", 0)
            # user update

            if os.path.isfile(timeDir):
            # checks if the totalTimes.json file exists
                with open(timeDir, "r", encoding="utf-8") as times:
                # if yes, opens the file
                    totalDict: dict[str] = json.load(times)
                    # loads the file as a dictionary

                    totalHours = f"{float(totalDict.get("totalHours", 0)):,.2f}"
                    totalMinutes = f"{float(totalDict.get("totalMinutes", 0)):,.0f}"
                    totalSeconds = f"{float(totalDict.get("totalSeconds", 0)):,.0f}"
                    totalPlays = f"{int(totalDict.get("totalPlays", 0)):,.0f}"
                    # grabs the numbers, formats as beautified number strings (eg. 25,593.24 hours / 2,520,149 minutes...)
                    totalAverage = f"{totalDict.get("totalAverage", "0:00")}"
                    # grabs the average song duration across all history

                    uniqueTracks = int(totalDict.get("uniqueTracks", 0))
                    uniqueArtists = int(totalDict.get("uniqueArtists", 0))
                    uniqueAlbums = int(totalDict.get("uniqueAlbums", 0))
                    # grabs the number of unique items (unused)

                    topTracks = dict(totalDict.get("topTracks", {}))
                    topArtists = dict(totalDict.get("topArtists", {}))
                    topAlbums = dict(totalDict.get("topAlbums", {}))
                    # grabs the dictionaries of top items {"URI": {"Time": (ms), "Count": (x), "Rank": #}}

                    hourlyPlays: dict[str, int] = dict(totalDict.get("hourlyPlays", {"25": 0}))
                    # grabs the {"hournum": playnum} dictionary
                    hour, plays = max(hourlyPlays.items(), key=lambda item: item[1])
                    # grabs the highest playcount + hour, stores both
                    topHour = {hour: plays}
                    # stores in global var

                    timestamp = int(totalDict.get("timestamp", 0))
                    # grabs the saved timestamp as an integer

                    self.historySongCounter.setText(f"Account Stats:\nSongs played: {totalPlays}\nTime played: {totalHours} hours\nAverage duration: {totalAverage}")
                    # sets the text for the historical stats label

                    if timestamp != 0:
                    # if the timestamp is anything but 0 (got loaded correctly)
                        timestamp = datetime.fromtimestamp(timestamp)
                        # converts to a datetime object
                        timestampString = timestamp.strftime("%d %B %Y").lstrip("0")
                        # formats the timestamp to eg. "03 August 2025", then strips the left 0 if one exists
                    else:
                    # is 0 somehow
                        timestampString = "N/A"
                        # unavailable string

                if enableUpdates:
                # if updates are enabled
                    self.labelSwap.emit(f"Times saved ({timestampString}):\n{totalHours} hours\n{totalMinutes} minutes\n{totalSeconds} seconds\n{totalPlays} plays", 0)
                    # prints the total times at start

            else:
            # if the file for SHA doesn't exist
                if not disableShaa:
                # if SHAA isn't disabled
                    self.labelSwap.emit("Could not find totalTimes.json file, please ensure proper SHAA installation...", 2)
                    # there's already a print informing about non-SHAA installation later
                    disableShaa = True
                    # disables SHAA functionality (can't access files)
                    nextTimer += 1500
                    # adds 1.5 seconds to let user read text

            QTimer.singleShot(nextTimer, self.readyStateReadier)
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

        self.mainLayout.setColumnMinimumWidth(0, 200)
        self.mainLayout.setColumnMinimumWidth(1, 450)
        self.mainLayout.setColumnMinimumWidth(2, 200)
        # sets the minimum width for columns

        self.mainLayout.setColumnStretch(0, 0)
        self.mainLayout.setColumnStretch(1, 0)
        self.mainLayout.setColumnStretch(2, 0)
        # stops each column from expanding on their own

        self.resize(self.windowSizeX, self.windowSizeX)
        # resizes the window automatically
        self.move(self.windowPosX, self.windowPosY)
        # moves the window to pre-determined coordinates

        self.readyTag.emit()
        # sends a signal to the ready tag to allow progress (starts the threads)

### Program Ready State ###

    def programReadyState(self):
        """Function that activates things after the rest of the program is caught up"""

        if self.configWindow is None:
        # only re-assigns the variable if this is the first time (this can get called after startup)
            self.configWindow = ConfigWindow(self)
            # instantiates the configuration window class 
            self.configWindow.hide()
            # hides by default
        if self.uriWindow is None:
        # only re-assigns the variable if this is the first time (this can get called after startup)
            self.uriWindow = URIWindow(self)
            # instantiates the URI manipulation window class
            self.uriWindow.hide()
            # hides by default
        if self.actionWindow is None:
        # only re-assigns the variable if this is the first time (this can get called after startup)
            self.actionWindow = ActionWindow(self)
            # instantiates the action selection window class
            self.actionWindow.hide()
            # hides by default

        self.cycleStatsButton.show()
        self.functionNestButton.show()
        self.openFuncConfigButton.show()
        self.openUriMapperButton.show()
        # enables the function buttons button

        self.spotifyStatusIcon.show()
        self.spotifyStatusLabel.show()
        self.discordStatusIcon.show()
        self.discordStatusLabel.show()
        # enables all the status icons



### URI Manipulation Window ###


class URIFilter(QSortFilterProxyModel):
    """Class to use to filter through tracks/artists/URIs based on search"""
    def __init__(self, parent=None):
    # init 
        super().__init__(parent)
        # init 2

    ### Variables ###

        self.currentSearch = ""
        # current search value
        self.hideDupes = False
        # boolean that stores the clone/dupe state

    def textNormaliser(self, text: str) -> str:
        """Function to normalise text"""
        return unicodedata.normalize("NFKC", str(text)).casefold()
        # returns the passed text in normalised form (ensures the text follows unicode characters, then lowers it, if possible)

    def search(self, text:str):
        """Function to search the URI table for the passed text"""
        self.currentSearch = self.textNormaliser(text).strip()
        # ensures the current search stored is normalised and doesn't have any empty characters (whitespace)
        self.invalidateFilter()
        # invalidates the currently active filter (resets the search conditions so that only relevant info shows up)

    def filterAcceptsRow(self, rowNum: int, QParent):
        """Function to filter the rows of data"""

        model = self.sourceModel()
        # grabs the inherited model (from URIWindow)

        uri = model.index(rowNum, 2, QParent).data()
        # returns the URI stored in the given row
        mappedURI = model.index(rowNum, 3, QParent).data()
        # returns the mapped URI(s) stored in the given row

        if self.hideDupes and mappedURI == uri:
        # if the option to hide dupes is set and the URI matches the mapped URI
            return False
            # can't be shown

        for column in range(model.columnCount()):
        # goes through every column of data in the model's columns (Track, Artist, URI, URIs)
            index = model.index(rowNum, column, QParent)
            # grabs the actual index (address) of the item (eg. row 359, column Track)

            value = model.data(index, Qt.ItemDataRole.DisplayRole)
            # grabs the data in the matching cell (index)

            if self.currentSearch in self.textNormaliser(value or ""):
            # if the current search matches (part of) the text in the cell
                return True
                # the passed row can be displayed (valid)

        return False
        # if nothing matches, then it doesn't fit the data -> shouldn't be displayed



class URIWindow(QDialog):
    """Window class to show the URI manipulation window"""
    def __init__(self, parentWindow: DSI_MainWindow):
    # init
        super().__init__(parent = parentWindow)
        # init 2
        
        self.mainIcon = iconPath
        # the directory containing the program icon png (built-in)

        self.setMinimumSize(900, 500)
        # sets the window size 
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setWindowTitle("DSI URI Manipulator")
        # sets title name

    ### Base Elements ###

        self.mainLayout = QVBoxLayout()
        # base layout
        self.mainLayout.setContentsMargins(25, 25, 25, 25)
        # 25px margin each side
        self.mainLayout.setSpacing(25)
        # 25px spacing between each element
        self.setLayout(self.mainLayout)
        # sets the layout

        self.searchLayout = QGridLayout()
        # nested layout to host the search elements
        self.mainLayout.addLayout(self.searchLayout)
        # adds the search element layout to the main layout

    ### Search Elements ###

        self.trackSelector = QLineEdit()
        # the place to enter a track in question
        self.trackSelector.setPlaceholderText("Search by track, artist or album name or by URI...")
        # temp text
        self.trackSelector.setToolTip("Type a song or any of its identifiers to display its mapped URI details")
        # tooltip
        self.trackSelector.setFixedSize(300, 60)
        # fixed size

        self.searchSpacer = QSpacerItem(50, 60)
        # a spacer item to sit between the search and the other buttons

        self.copyURIbutton = QPushButton("Copy URI")
        # button to copy the currently active URI
        self.copyURIbutton.setToolTip("Press to copy the currently active track's URI to the search bar")
        # tooltip
        self.copyURIbutton.setFixedSize(125, 60)
        # fixed size
        self.copyURIbutton.clicked.connect(self.copyURItoSearch)
        # connects the click to the function

        self.removeMappedButton = QPushButton("Unmap URI")
        # button to remove the mapped URIs from the selected URI
        self.removeMappedButton.setToolTip("Press to remove the URI mapping from the active track's URI\nThis is useful if you think Spotify has mapped it wrong")
        # tooltip
        self.removeMappedButton.setFixedSize(125, 60)
        # fixed size
        self.removeMappedButton.clicked.connect(self.promptErase)
        # connects clicking the remove the mapping to the function to prompt -> erase

        self.hideDuplicatesButton = QCheckBox("Hide Clones")
        # button to hide the "clone" URIs
        self.hideDuplicatesButton.setToolTip("Only display URIs that have a different alternate URI\nMost URIs tend to map to the same URI (very licensing-dependant)")
        # tooltip
        self.hideDuplicatesButton.setFixedSize(125, 60)
        # fixed size
        self.hideDuplicatesButton.clicked.connect(self.hideDuplicateFunc)
        # connects the click to the function

    ### Table (Internals) ###

        self.searchModel = QStandardItemModel()
        # a 'model' to use to search the data with
        self.searchModel.setHorizontalHeaderLabels(["Track", "Artist", "URI", "Mapped URI(s)"])
        # sets up the header labels

        self.filterProxy = URIFilter()
        # a filtering proxy
        self.filterProxy.setSourceModel(self.searchModel)
        # makes the filter use the created search model
        self.filterProxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        # the filter doesn't care about cAse sEnSitiVitY
        self.filterProxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        # the sorting doesn't care about cAse sEnSitiVitY

        self.uriTable = QTableView()
        # a sheet-like view on the tracks
        self.uriTable.setModel(self.filterProxy)
        # makes the UI table use the created proxy
        self.uriTable.setSortingEnabled(True)
        # allows clicking the columns to sort them
        self.uriTable.setMinimumSize(500, 225)
        # sets the minimum size for the table
        self.uriTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # disables all methods of editing the cells (there's no function related to actually modifying them)

        self.uriTable.setColumnWidth(0, 200)
        self.uriTable.setColumnWidth(1, 150)
        self.uriTable.setColumnWidth(2, 200)
        self.uriTable.setColumnWidth(3, 200)
        # ensures all the columns have at least some space

        self.trackSelector.textChanged.connect(self.filterProxy.search)
        # connects typing in the search bar

        self.searchLayout.addWidget(self.trackSelector, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.searchLayout.addItem(self.searchSpacer, 0, 1)
        self.searchLayout.addWidget(self.copyURIbutton, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.searchLayout.addWidget(self.removeMappedButton, 0, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.searchLayout.addWidget(self.hideDuplicatesButton, 0, 4, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.uriTable)
        # adds all UI elements to layout

        self.trackPlacer(25)
        # starts up with the first 25 tracks

    def trackPlacer(self, count: int = 250000):
        """Function that adds all the relevant tracks to the table of tracks"""

        self.searchModel.removeRows(0, self.searchModel.rowCount())
        # removes every row contained within (calling .Clear() removes the headers, too)

        num = 0
        # starts counter at 0

        for uri in uriMap.keys():
        # goes through every stored URI in the mapped URI dict
            if isinstance(uriMap[uri], dict):
            # if the entry is a dictionary (str:str means old system, str:dict means new)
                modelItems = [
                    QStandardItem(uriMap[uri]["Song Name"]),
                    QStandardItem(uriMap[uri]["Artist"]),
                    QStandardItem(uri),
                    QStandardItem("\n".join(uriMap[uri]["URIs"]))
                ]
                # forms a list of items to place into the table
                self.searchModel.appendRow(modelItems)
                # adds the items to the rows of data (Song | Artist | URI | Mapped | Remove)

                num += 1
                # adds 1 to the running tally
                if num >= count:
                # if the counter exceeds the requested number (startup, otherwise basically ignored, unless your Spotify somehow has >250K tracks)
                    break
                    # stops (caps at passed number)

    def copyURItoSearch(self):
        """Function that copies the active URI to the filter search bar (and ensures the search is refreshed)"""

        activeURI: str = cppFull.get("URI", None)
        # grabs the last saved URI from the global variable (if fails, grabs None)
        if activeURI:
        # if it found one (not set to None)
            self.trackSelector.setText(activeURI)
            # sets the text to match the URI

    def promptErase(self):
        """Function that prompts before removing a URI mapping/row"""

        selectedRow = self.uriTable.selectionModel().currentIndex()
        # grabs the QIndex of the selected cell/row
        if not selectedRow.isValid():
        # if the index isn't considered "valid" (column, nothing selected, etc.)
            return
            # stops

        selectionIndex = self.filterProxy.mapToSource(selectedRow)
        # turns the selection into the filter's index (translates what the table sees -> what the filter sees)
        uri = self.searchModel.item(selectionIndex.row(), 2).text()
        # grabs the URI by getting the text of the 3rd column (0-start) and the selected row
        track = self.searchModel.item(selectionIndex.row(), 0).text()
        # does the same for the 1st column to get the track name (QoL)

        confirmErase = QMessageBox.question(self, "Confirm Unmap", f"Unmap {track}'s URIs?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        # prompts with a QMessageBox
        if confirmErase == QMessageBox.StandardButton.Yes:
        # pressing Yes -> confirm -> erase
            self.eraseRow(uri)
            # calls the row eraser to delete the given row and wipe the URI's map

    def eraseRow(self, uri: str):
        """Function that removes the selected row from the table and its mapped URIs"""
        global uriMap
        # global -> local

        for row in range(self.searchModel.rowCount()):
        # goes through the search model's rows
            if self.searchModel.item(row, 2).text() == uri:
            # checks the 3rd (0-start) column for the URI, looking for a match
                self.searchModel.removeRow(row)
                # matching URI -> removes the row from the 
                break
                # stops looking

        uriMap[uri]["URIs"] = []
        # resets the mapped URIs of the passed URI entry

    def hideDuplicateFunc(self):
        """Function that hides all the URIs that map to themselves"""
        visibilityBool = self.hideDuplicatesButton.isChecked()
        # grabs the state of the checkbox, stores as bool

        self.filterProxy.hideDupes = visibilityBool
        # sets the dupe hiding state to match the checkbox
        self.filterProxy.invalidateFilter()
        # calls the invalidation filter to refresh the table



### Action Dialog ###

class ActionWindow(QDialog):
    """Window class to show the action buttons"""
    def __init__(self, parentWindow: DSI_MainWindow):
    # init
        super().__init__(parent = parentWindow)
        # init 2

        self.mainIcon = iconPath
        # the directory containing the program icon png (built-in)

        self.setMinimumSize(450, 150)
        # sets the window size 
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setWindowTitle("DSI Actions")
        # sets title name

        self.actionWindowLayout = QHBoxLayout()
        # base layout
        self.setLayout(self.actionWindowLayout)
        # sets the layout

        self.actionWindowLayout.addWidget(parentWindow.currentSongInfoButton)
        self.actionWindowLayout.addWidget(parentWindow.uriMapConfigureButton)
        self.actionWindowLayout.addWidget(parentWindow.pauseCPPbutton)
        # adds all the relevant buttons to the layout



### Config Dialog ###

class ConfigWindow(QDialog):
    """Window class to show the configuration selection"""
    def __init__(self, parentWindow: DSI_MainWindow):
    # init
        super().__init__(parent = parentWindow)
        # init 2

        self.mainIcon = iconPath
        # the directory containing the program icon png (built-in)

        self.setMinimumSize(450, 150)
        # sets the window size 
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setWindowTitle("DSI Configuration")
        # sets title name

        self.activeConfig = None
        # stores the currently active configuration window
    
    ### Buttons ###

        self.mainLayout = QGridLayout()
        # base layout
        self.setLayout(self.mainLayout)
        # sets the layout

        self.taskLabel = QLabel("Select a configuration to open")
        # label

        self.configLayout = QHBoxLayout()
        # horizontal layout
        self.mainLayout.addLayout(self.configLayout, 1, 0)
        # adds the config layout to the main

        self.funcConfigButton = QPushButton("Functional\nConfiguration")
        self.funcConfigButton.setFixedSize(120, 60)
        self.funcConfigButton.clicked.connect(lambda: self.configWindowStart("Functional"))
        # func config
        self.dsiConfigButton = QPushButton("DSI Visual\nConfiguration")
        self.dsiConfigButton.setFixedSize(120, 60)
        self.dsiConfigButton.clicked.connect(lambda: self.configWindowStart("DSI"))
        # DSI config
        self.shaaConfigButton = QPushButton("SHAA Visual\nConfiguration")
        self.shaaConfigButton.setFixedSize(120, 60)
        self.shaaConfigButton.clicked.connect(lambda: self.configWindowStart("SHAA"))
        # SHAA config 

        self.configLayout.addWidget(self.funcConfigButton)
        self.configLayout.addWidget(self.dsiConfigButton)
        self.configLayout.addWidget(self.shaaConfigButton)
        # adds all the config buttons
        self.mainLayout.addWidget(self.taskLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the button to "close"

### Threads ###

    def funcThread(self):
        """Function to run the functional config"""

        funcConfigProc = subprocess.Popen([funcConfigExePath], creationflags=subprocess.CREATE_NO_WINDOW)
        # runs the functionality configurator asynchronously
        funcConfigProc.wait()
        # waits for the process to end (blocking)
        self.activeConfig = None
        # resets to none
    
    def dsiThread(self):
        """Function to run the DSI visual config"""

        dsiConfigProc = subprocess.Popen([dsiConfigExePath], creationflags=subprocess.CREATE_NO_WINDOW)
        # runs the DSI visual configurator asynchronously
        dsiConfigProc.wait()
        # waits for the process to end (blocking)
        self.activeConfig = None
        # resets to none

    def shaaThread(self):
        """Function to run the SHAA config"""

        shaaConfigProc = subprocess.Popen([shaaConfigExePath], creationflags=subprocess.CREATE_NO_WINDOW)
        # runs the SHAA configurator asynchronously
        shaaConfigProc.wait()
        # waits for the process to end (blocking)
        self.activeConfig = None
        # resets to none
        
### Config Run ###
    
    def configWindowStart(self, config: str):
        """Function to start a configuration window"""
        if self.activeConfig is not None:
        # if there's an actively open config
            self.taskLabel.setText(f"{self.activeConfig} window is open, cannot open another configuration!")
            # sets a warning
            return
            # stops
        else:
        # no window open yet
            self.activeConfig = config
            # sets the config state variable to match
            self.taskLabel.setText(f"{config} configuration window open...")
            # sets text

        if config == "Functional":
        # called config = functional
            threading.Thread(target=self.funcThread, daemon=True).start()
            # starts a thread for the configuration window (so it doesn't block everything with .wait())
        elif config == "DSI":
        # called config = DSI
            threading.Thread(target=self.dsiThread, daemon=True).start()
            # starts a thread for the configuration window (so it doesn't block everything with .wait())
        elif config == "SHAA":
        # called config = SHAA
            threading.Thread(target=self.shaaThread, daemon=True).start()
            # starts a thread for the configuration window (so it doesn't block everything with .wait())



### Global Objects ###

pictureQueue = queue.Queue()
"""An empty queue for pictures from picCycler to get sent to"""
songEvent = threading.Event()
"""An empty threading event list for song"""
picEvent = threading.Event()
"""An empty threading event list for picturecycler """
spotifyLock = threading.Lock()
"""A locking method to prevent redundant API calls (or 2 calls at once)"""

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
        client_id = spotifyClientID, 
        client_secret = spotifyClientSecret, 
        redirect_uri = spotifyRedirect,
        cache_path = spCache
        )
    # this assignment can only be made *after* the client UI window runs (because that handles the config -> global var)

    main = spotipy.Spotify(auth_manager = authorisation)
    # same deal with this



### Spotify Data Grabber Function ###

def authPlayback() -> dict | None:
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
                    mainWin.iconChanger("Spotify", "Green", "Icon")
                    # ensures the icon is green

                elif enableErrors and tokenRefresh:
                # if the tokenrefresh flag is set to true, that means a connectionError occurred at least once
                    mainWin.labelSwap.emit("Token refreshed successfully!", 0)
                    # prints user update with more specific info
                    mainWin.iconChanger("Spotify", "Green", "Icon")
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
                    if "failed to resolve" in str(error).lower():
                    # failed to resolve points to a you -> Spotify error, not a token refresh
                        if enableErrors:
                        # if error-printing is enabled
                            mainWin.labelSwap.emit(f"Lost connection to Spotify\nRetrying in 5 seconds ({attempt+1}/3)", 2)
                            # user inform
                    else:
                    # not present, likely token 
                        if enableErrors:
                        # if error-printing is enabled
                            mainWin.labelSwap.emit(f"Refreshing Spotify token...", 2)
                            # doesn't sleep because this is a token error and should get "fixed" nearly instantly
                            # expected to print just about every 3600 seconds (1h)
                        tokenRefresh = True
                        # sets the tokenRefresh flag to true so the next print is more relevant (purely QoL)

                elif isinstance(error, requests.exceptions.ReadTimeout):
                # if the error is a read timeout (sort of random)
                    if enableErrors:
                    # if error-printing is enabled
                        mainWin.labelSwap.emit(f"Spotify API timeout\nRetrying in 5 seconds ({attempt+1}/3)", 2)
                        # user inform
                    time.sleep(2)
                    # sleeps for 2 seconds (because there's a function-wide 3-second cooldown added on top)

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

                elif isinstance(error, SpotifyException) and (error.http_status == 500 or error.http_status == 503):
                # if the error is 500/503 (internal error fail)
                    if enableErrors:
                    # if error-printing is enabled
                        mainWin.labelSwap.emit(f"Spotify internal error\nAttempting to reconnect ({attempt+1}/3)", 2)
                        # "should never happen" (according to Spotify docs), but does occasionally (typically Spotify-side maintenance or servers down)

                elif isinstance(error, SpotifyException) and (error.http_status == 401 or error.http_status == 403):
                # if the error is 401/403 (access token error, forbidden action, etc)
                    if enableErrors:
                    # if error-printing is enabled
                        mainWin.labelSwap.emit(f"Spotify access error\nAttempting to reconnect ({attempt+1}/3)", 2)
                        # user inform on token error
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
                            mainWin.labelSwap.emit(f"Spotify error: {error}\nAttempting to reconnect ({attempt+1}/3)", 2)
                            # generic user update

                else:
                # if the error is anything else
                    if enableErrors:
                    # if error-printing is enabled
                        mainWin.labelSwap.emit(f"Spotify error: {error}\nAttempting to reconnect ({attempt+1}/3)", 2)
                        # generic user update

                mainWin.iconChanger("Spotify", "Yellow", "Icon")
                # ensures the icon is yellow for any error (may indicate a problem)

                if attempt == 2:
                # if it's the last attempt (range(3) = 0,1,2) and it fails
                    mainWin.labelSwap.emit(f"All attempts to reconnect failed due to: {error}\nStopping Spotify API calls...", 4)
                    # user update
                    mainWin.iconChanger("Spotify", "Red", "Icon")
                    # calls the icon changer with red icon
                    mainWin.saveSignal.emit("Restart")
                    # prompts user, then gets the restart slate ready

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

def URIFileReader(file: str):
    """Function that reads and stores variables related to SHAA / URI functionality"""
    global maplessURIs, csvReader, uriMap
    # global -> local

    if file == "SHAA":
    # SHAA file (csv) load
        if os.path.exists(SHAAdir):
        # if the grouped .csv file exists
            mainWin.labelSwap.emit("Spotify Analyser (Addon) functionality enabled", 0)
            # informs user SHAA is enabled
            csvReader = pd.read_csv(SHAAdir, encoding="utf-8")
            # opens the CSV file and uses utf-8 encoding to ensure compatibility
            csvReader = csvReader.set_index("URI")
            # sets the track URL as the index

    elif file == "URI":
    # unmapped URI file load
        if os.path.exists(noURIpath):
        # checks if the uri file (uriList.json) exists
            with open(noURIpath, "r", encoding="utf-8") as URIs:
                # loads the JSON file of URIs
                newURIs = json.load(URIs)
                # stores the loaded file as newURIs

                if isinstance(newURIs, list):
                # if the file still contains a list format (old system)
                    mainWin.labelSwap.emit(f"Converting URI list to new format...", 1)
                    # user inform
                    tempMaplessList = newURIs.copy()
                    # reassigns to a temp variable
                    for uri in tempMaplessList:
                    # goes through every URI in the list
                        maplessURIs[uri] = {}
                        # creates an empty dictionary entry for each URI
                else:
                # not old system
                    maplessURIs = newURIs
                    # reassigns the temp variable to the real dict

                if enableUpdates and enableMapping:
                # if the user prints and mapping options are enabled
                    uriLength = len(maplessURIs.keys())
                    # stores the length of the unmapped URI list
                    mainWin.labelSwap.emit(f"{uriLength} URIs stored", 1)
                    # helper print (if using the URI mapper)
        else:
        # if file doesn't exist
            maplessURIs = {}
            # creates a new, empty dict

    elif file == "Map":
    # URI map file load
        if os.path.exists(uriPath):
        # checks if the URI map file (uriMap.json) exists
            with open(uriPath, "r", encoding="utf-8") as maps:
            # loads the URI map file
                uriMap = json.load(maps)
                # stores the loaded file as uriMap
                if enableUpdates and enableMapping:
                # if the user prints and mapping options are enabled
                    uriMLength = len(uriMap.keys())
                    # stores the length of the mapped URIs
                    mainWin.labelSwap.emit(f"{uriMLength} URIs mapped", 1)
                    # user inform
        else:
        # if the file doesn't exist
            uriMap = {}
            # creates a new, empty list



def uriWriter(URIs: dict):
    """Function that writes the current unmapped URI dictionary to file"""

    with open(noURIpath, "w", encoding="utf-8") as nURI:
    # opens the unfound URI file in write mode
        json.dump(URIs, nURI, indent=3)
        # "dumps" the dict of URIs into the file (with indent)



def statsWriter(action: str):
    """Function that adds the current stats to file"""
    global globalStats
    # global -> local

    if action == "Init":
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

        return globalStats
        # returns the stats
    
    elif action == "Load":
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
    # action is to add a new item to whitelist
        if len(favoriteList) >= 10:
        # if there's 10 items already in the list
            mainWin.labelSwap.emit("The favorited song list is full!\nPlease remove one before favoriting this song!", 2)
            # user update
        else:
        # if there's not 10
            blacklist[currentURI] = {"status": "starred", "info": blacklistInfo}
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

            if self.picCycleList == "Spotify":
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

                if self.picCycleType == "Random":
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

                        time.sleep(self.picCycleTime)
                        # sleeps until it's time to change pictures
                        picEvent.clear()
                        # empties the picture event queue
                        self.run()
                        # runs the starter
                    else:
                        time.sleep(10)
                        # if the queue isn't empty, waits 10 seconds then re-runs the picture selection

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
                                mainWin.labelSwap.emit("Sequential picture set", 1)
                                # informs user a new picture is set
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

                if self.picCycleType == "Once":
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

                if self.picCycleType == "None":
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
    global cppProgram
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

    def cppQueueManager(output, cppQueue):
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

    songEvent.set()
    # sets a song event to force a new data packet to be sent after the C++ program starts (prevents empty data loads)

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
                    mainWin.iconChanger("Discord", "Green", "Icon")
                    # ensures the icon is green
                    
                elif "CPPFAIL" in line:
                # if the line contains "CPPFAIL" (critical C++ side failure)
                    mainWin.iconChanger("Discord", "Red", "Icon")
                    # ensures the icon is red
                    mainWin.labelSwap.emit(f"Discord RPC program failure, please press the 'Discord API' button to restart the C++ subprocess!", 3)
                    # sends a user log to inform user

                elif "api asset" in line.lower():
                # if the line contains "API asset" (means RPC failed because of Discord's API refusing to set the assets)
                    mainWin.iconChanger("Discord", "Red", "Icon")
                    # ensures the API icon is now red
                    mainWin.labelSwap.emit(f"Can't update Discord RPC due to Discord API errors, please manually exit and restart DSI\nYou'll likely be prompted to re-authorise Discord", 3)
                    # sends a user log to inform user

                elif "failed" in line.lower():
                # if the line contains "failed"/"Failed" (means the RPC update didn't go through)
                    mainWin.iconChanger("Discord", "Yellow", "Icon")
                    # ensures the icon is yellow
                    if "image" in line.lower():
                    # if the line also contains "image"/"Image" (means either of the pictures was broken)
                        mainWin.iconChanger("Discord", "Blue", "Images")
                        # calls the UI option to enable the bool override -> reset fail bools -> hopefully send non-broken images

    cppProgram.wait()
    # waits for the program to close

def cppPackets(packet: dict):
    """Function to send packets to the C++ program"""
    dataPacket = json.dumps(packet, indent=2).encode("utf-8")
    # converts the passed argument into json
    if cppProgram is not None:
    # ensures the C++ program is, in fact, defined
        if cppProgram.poll() is None:
        # None is good, means there's no return code -> should still be up
            cppProgram.stdin.write(struct.pack("!I", len(dataPacket)))
            # sends the byte length of the packet
            cppProgram.stdin.write(dataPacket)
            # writes the packet to the C++ program (sends)
            cppProgram.stdin.flush()
            # ensures all messages are sent



### Song Data File Field Selection/Creation ###

def song(pictureQueue: queue.Queue, event):
    """The function that handles all song data gathering and parsing"""
    global maplessURIs, cppLargeImage, uriMap, pauseStart, deviceName, volumeLevel
    global trackCounter, oldCount, cycleCount, blacklistInfo, hoverText, smallURL, timePlayed, csName, csArtistName, cppFull
    global csSongName, csArtistURL, csAlbumName, csAlbumURL, csPlaylistURL
    # global -> local

    mainWin.blacklistTag.emit("Init", "", "")
    # sends an empty signal to initialise (shows the manage button and song name)

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

        csFull: dict = currentInfo
        # gets a huge dictionary containing all the information about current song
        # "cs" in the variables just stands for CurrentSong, which, while descriptive, made the later variables insanely long

        if not csFull or not csFull.get("item"):
        # if the dictionary doesn't exist or can't be called
            cppFull = {
                "Playback State": False,
                "Reset Images": False,
                "Song": cppFull.get("Song", "A song"),
                "Song Name": cppFull.get("Song Name", "A song"),
                "Artist Name": cppFull.get("Artist Name", "An artist"),
                "Artist URL": cppFull.get("Artist URL", "An artist"),
                "Album": cppFull.get("Album", "An artist"),
                "Album Name": cppFull.get("Album Name", "An album"),
                "Album URL": cppFull.get("Album URL", "An album"),
                "Playlist URL": cppFull.get("Playlist URL", "No playlist"),
                "Spotify Image": cppFull.get("Spotify Image", "https://i.imgur.com/FeUsGIz.png"),
                "State": cppFull.get("State", "Discord Spotify Integration"),
                "Large Image": cppFull.get("Large Image", ""),
                "Large Text": cppFull.get("Large Text", "DSI"),
                "Small Text": cppFull.get("Small Text", "DSI"),
                "Spotify URL": cppFull.get("Spotify URL", ""),
                "Small URL": cppFull.get("Small URL", "An artist"),
                "UNIX Start": cppFull.get("UNIX Start", "An artist"),
                "UNIX End": cppFull.get("UNIX End", "An artist"),
                "Song Progress": cppFull.get("Song Progress", 0),
                "Pause": cppFull.get("Pause", False),
                "Song Raw": cppFull.get("Song Raw", "N/A"),
                "Track ID": cppFull.get("Track ID", trackCounter),
                "URI": cppFull.get("URI", "N/A"),
                "Mapped URI": cppFull.get("Mapped URI", "N/A"),
                "Playcount": cppFull.get("Playcount", "N/A"),
                "Playtime": cppFull.get("Playtime", "N/A"),
                "SHAA": cppFull.get("SHAA", not(disableShaa)),
            }
            # forms a dictionary to pass with Playback State as False this time

        else:
        # dictionary is valid and can be called
            csItem: dict = csFull.get("item")
            # takes the first part of the song's info (leaving out device info and various user states)
            csAlbum: dict = csItem.get("album")
            # takes a smaller part of the song's info (still contains a ton of extra)

            csDevice: dict = csFull.get("device")
            # gets a list of device information
            deviceName = csDevice.get("name")
            # gets the name of the playing device
            volumeLevel = csDevice.get("volume_percent")
            # gets the volume level of the spotify instance

            csName = str(csItem.get("name"))
            # stores the name of the song
            csSongName = csName
            # stores a duplicate for the final packet

            isLocalSong = csItem.get("is_local")
            # checks if the song is a local song (can't use standard API info requests if so)

            shaaPlaytimeMin = None
            shaaPlaycountSong = None
            shaaPlaytime = None
            # starts up variables as None

            topItem = False
            # boolean for whether the current track is in one of the top item dictionaries
            singlePlay = False
            # local boolean to check if the song has been played once
            firstPlay = False
            # local boolean to check if the song has ever been played

            if not isLocalSong:
            # these fields are only valid when it's not a local song

                csURI = csItem.get("uri")
                # grabs the URI of the song - which is what determines the song matching

                csImages: list[dict] = csAlbum.get("images")
                # gets the information about the album's images
                csCover = csImages[0].get("url")
                # gets the album cover url (used to pass to Discord if pictureCycle = Spotify)

                csArtists = csItem.get("artists")
                # stores all the artists listed on the song

                csArtistList = []
                # creates an empty list of artists
                for musician in csArtists:
                # for every artist in the list of artists (from Spotify)
                    artist = musician.get("name")
                    # gets the name of the artist from a dictionary
                    csArtistList.append(artist)
                    # appends it to the list of artists 

                if len(csArtistList) > 1:
                # if there's more than 1 artist
                    csArtistFirstHalf = csArtistList[0:-1]
                    # grabs all the artists except the last one
                    csArtistLast = csArtistList[-1]
                    # grabs the last artist

                    if len(csArtistFirstHalf) > 1:
                    # checks if there's more than 1 artist in the first half
                        csArtistString = ", ".join(csArtistFirstHalf)
                        # joins together with commas
                    else:
                    # if there's not more than 1 artist in the first half
                        csArtistString = "".join(csArtistFirstHalf)
                        # just joins with nothing (turns into a string basically)

                    csArtistString = (csArtistString + " and ")
                    # adds the "and" in between the first half and the last artist
                    csArtistString = (csArtistString + csArtistLast)
                    # adds the last artist to the string
                    csArtistName = csArtistString
                    # constructs a string from the artist names
                else:
                # if there's not more (just 1)
                    csArtistName = csArtistList[0]
                    # gets the name of the only artist
                try:
                    csArtistURL = csArtists[0].get("name")
                    # gets the "name" of the 0th artist (link)
                except:
                    csArtistURL = "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"
                    # uses Taylor Swift as fallback

                csAlbumName = csAlbum.get("name")
                # stores the album name
                csAlbumURLs: dict = csAlbum.get("external_urls")
                # stores all the album urls 
                csAlbumURL = csAlbumURLs.get("spotify")
                # gets the spotify url 

            csLength = int(csItem.get("duration_ms", 180000) / 1000)
            # stores the length of the song in seconds (fallback of 180 seconds)
            csProgress = int(csFull.get("progress_ms", 1000) / 1000)
            # saves the current song progress in seconds (fallback of 1 second)

            csUnixStart = int(time.time() - csProgress + 4)
            # stores the start time of the song by taking current time and subtracting progress
            # adds 4 seconds to shift the Discord timestamps to be slightly behind Spotify (they were a bit ahead before, actually)
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

            if enablePause and not csPlayState:
            # if the pause behavior is enabled and song paused
                songNameList.append(pauseStateText)
                # adds the pause text as the first string in the list (since it goes first)

            if not isLocalSong:
            # can't access these if the playing song is local
                cstrackURL: dict = csItem.get("external_urls")
                # stores the list that contains track's url
                csAlbumLinks: dict = csAlbum.get("external_urls") 
                # stores the list that contains album url
                csArtistLinks: dict = csArtists[0].get("external_urls")
                # stores the list that contains artist's url
                csArtistURL = csArtistLinks.get("spotify")
                # stores the artist URL
                csPlaylist: dict = csFull.get("context")
                # stores the list that contains the playlist url

            if csPlaylist == None:
            # checks if user is playing a playlist
                onPlaylist = False
                # if not, sets onPlaylist to false
            else:
            # if there is a playlist playing
                csPlaylistURLs: dict = csPlaylist.get("external_urls")
                # gets the list of external urls attached to that playlist
                csPlaylistURL = csPlaylistURLs.get("spotify")
                # grabs the Spotify playlist URL
                onPlaylist = True
                # sets onPlaylist to true

            if spotifyURL in spotifyURLlist:
            # if the selected type of URL is in the valid set

                if spotifyURL == "Track":
                # if the config option for url type is set to track
                    csURL = cstrackURL.get("spotify")
                    # takes the track's URL

                elif spotifyURL == "Album":
                # if the config option for url type is set to album
                    csURL = csAlbumLinks.get("spotify")
                    # takes the album's URL

                elif spotifyURL == "Artist":
                # if the config option for url type is set to artist
                    csURL = csArtistLinks.get("spotify")
                    # takes the artist's URL

                elif spotifyURL == "Playlist":
                # if the config option for url type is set to playlist
                    if onPlaylist:
                    # takes the playlist's URL
                        csURL = csPlaylistURLs.get("spotify")
                    else:
                    # the user isn't playing a playlist, but has selected the playlist url config option
                        csURL = smallURL
                        # sets it to smallURL as a fallback                    
            else:
            # if the config option for url type is invalid, defaults to DSI's github :)
                csURL = "https://github.com/EllEff-Git/Discord-Spotify-Integration/"
                # sets url to fallback


        ### SHAAless Behavior ###


            if not os.path.exists(SHAAdir) or disableShaa:
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

                    if shaaInfoDetails == "Volume":
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
                    
                    elif shaaInfoDetails == "Repeat":
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

                    elif shaaInfoDetails == "Shuffle":
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
                    # config calls for some options that doesn't exist without SHAA
                        shaaDetailField = "may be jamming out"
                        # uses fallback string instead
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

            if os.path.exists(SHAAdir) and not disableShaa:
            # this is the addon part to Spotify (History) Analyser (SHA + addon = SHAA)
            # this data is only entered to rich presence if used with SHA (and installed correctly)
            # checks if the CSV file exists to pull data from (requires one full run of SHA prior)
                
            ### URI Checkpoint ###

                if enableMapping:
                # if URI mapping is enabled

                    if finalURI not in maplessURIs or maplessURIs.get(finalURI, {}).get("Song Name") is None:
                    # if the URI is not in the URI list yet, or it doesn't have nested data
                        maplessURIs[finalURI] = {"Song Name": csSongName, "Artist": csArtistList[0]}
                        # adds it to the dictionary of URIs (adds name and artist)
                        if enableUpdates:
                        # if the user updates are enabled
                            mainWin.labelSwap.emit(f"URI added to list", 0)
                            # user update
                        if enableFirstTime and finalURI not in maplessURIs:
                        # if first time behavior is enabled and this branch is set off by it not being stored ()
                            firstPlay = True
                            # track hasn't been played before (since it's not in the URI list)

                    altURImap: dict | str = uriMap.get(csURI)
                    # gets the matching URI's dictionary (which contains the alternate URI(s), name and artist or just a string)

                    if altURImap:
                    # if the URI has stored data
                        if isinstance(altURImap, str):
                        # if the alternative URI map is still in string form (URI:URI2)
                            altURI = altURImap
                            # reassigns variable
                            if altURI in csvReader.index and finalURI not in csvReader.index:
                            # if the URI is not found in the CSV index, but the alternate URI is
                                finalURI = altURI
                                # sets the URI to use the alternate instead
                                if enableUpdates:
                                # if the user updates are enabled
                                    mainWin.labelSwap.emit("Using stats from mapped URI", 0)
                                    # user update
                        else:
                        # the map uses the new format (URI: URIs, Song Name, Artist)
                            for value in altURImap.get("URIs", []):
                            # goes through that map's URI values
                                if value in csvReader.index and finalURI not in csvReader.index:
                                # if the URI is not found in the CSV index, but the alternate URI is
                                    finalURI = altURI = value
                                    # sets the URI to use the alternate instead (also stores the alternate to push to webapp)
                                    if enableUpdates:
                                    # if the user updates are enabled
                                        mainWin.labelSwap.emit("Using stats from mapped URI", 0)
                                        # user update
                                    break
                                    # stops the for loop (found a match, don't need to look for a second)

                if finalURI in csvReader.index:
                # checks if the URI is in the CSV
                    if enableUpdates:
                    # if the user updates are enabled
                        mainWin.labelSwap.emit(f"Song stats found", 0)
                        # user update

                ### Top Hour ###

                    if enableTopHour:
                    # if the top hour is enabled
                        currentHour = f"{pd.Timestamp.now().hour:02d}"
                        # gets the current hour number as a string with leading 0s (how the dictionary is constructed)
                        if currentHour in topHour:
                        # if the current hour matches the stored top hour
                            songStuffList.append(topHourFormat)
                            # adds the top hour format
                            songStuffList.append(songInfoSpacer)
                            # adds the spacer item, too

                ### Plays / Field 1 ###

                    playcount = csvReader.loc[finalURI, "Playcount"]
                    playtime = csvReader.loc[finalURI, "Total Time"]
                    # sets temp variables that lookup the cells based on the track and columns

                ### Top Track/Album/Artist ###

                    if enableTopItems:
                    # if the top items config option is enabled (special prefix)
                        if finalURI in topTracks.keys():
                        # if that URI is in the top tracks dictionary
                            songStuffList.append(f"#{topTracks[finalURI]["Rank"]} track {songInfoSpacer}")
                            # adds the track identifier and string prefix

                        elif finalURI in topAlbums.keys():
                        # if that URI is in the top albums dictionary
                            songStuffList.append(f"#{topAlbums[finalURI]["Rank"]} album {songInfoSpacer}")
                            # adds the album identifier and string prefix
                            playtime = topAlbums[finalURI]["Time"]
                            playcount = topAlbums[finalURI]["Count"]
                            # overrides the CSV values with the album values from JSON
                            topItem = True
                            # sets the boolean to True (uses the values here)

                        elif finalURI in topArtists.keys():
                        # if that URI is in the top artists dictionary
                            songStuffList.append(f"#{topArtists[finalURI]["Rank"]} artist {songInfoSpacer}")
                            # adds the artist identifier and string prefix
                            playtime = topArtists[finalURI]["Time"]
                            playcount = topArtists[finalURI]["Count"]
                            # overrides the CSV values with the artist values from JSON
                            topItem = True
                            # sets the boolean to True (uses the values here)

                    if songInfoField1 == "Track" or topItem:
                    # if the selected type for first field is Track

                        if isinstance(playcount, pd.Series):
                        # if there's more than one instance of the current song
                            playcountTotal = playcount.sum()
                            # saves the playcount total based on calculated playcounts
                        else:
                        # if there's only one instance of the current song
                            playcountTotal = playcount
                            # saves the total as the playcount of the song

                        if playcountTotal == 1:
                        # if the playcount equals 1
                            singlePlay = True
                            # sets single play to True (affects formatting)

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

                    if singlePlay and songInfoFormatPlays.lower().endswith("s"):
                    # if the track has been played only once and the string contains a plural ("plays", "listens", "repeats"...)
                        songStuffList.append(songInfoFormatPlays[:-1])
                        # adds just the single form instead (removes the last character)
                    else:
                    # not matching style / not single playcount
                        songStuffList.append(songInfoFormatPlays)
                        # adds the first field's custom end styling

                ### Spacer ###

                    songStuffList.append(songInfoSpacer)
                    # adds the spacer to the list

                ### Minutes / Field 2 ###

                    if songInfoField2 in [0, 2, 4] or topItem:
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

                        if songInfoField2 in [0, 1]:
                        # track minutes
                            playtimeTotal = (playtimeTotal / 60)
                            # divides the seconds into minutes
                        
                        elif songInfoField2 in [2, 3]:
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
                
                elif firstPlay:
                # not in the CSV and it's the first time that song is played
                    songStuffList.append(firstTimeFormat)
                    # adds the first time listening format string
                    if enableUpdates:
                    # user informs enabled
                        mainWin.labelSwap.emit(f"Using first time special text!", 0)
                        # user inform on first time track
                        
            ### Details / Field 3 / Total Hours ###

                if shaaInfoDetails in detailOptions:
                # if the config option matches one of the set defaults

                    if shaaInfoDetails == "Hours":
                    # if the config calls for total hours
                        shaaDetailField = totalHours
                        # gets total hours
                        cppLargeHoverList.append(songInfoFormatDetails)
                        # uses the user-formatted one

                    elif shaaInfoDetails == "Minutes":
                    # if the config calls for total minutes
                        shaaDetailField = totalMinutes
                        # gets total minutes
                        cppLargeHoverList.append(songInfoFormatDetails)
                        # uses the user-formatted one

                    elif shaaInfoDetails == "Seconds":
                    # if the config calls for total seconds
                        shaaDetailField = totalSeconds
                        # gets total seconds
                        cppLargeHoverList.append(songInfoFormatDetails)
                        # uses the user-formatted one

                    elif shaaInfoDetails == "Plays":
                    # if the config calls for total plays
                        shaaDetailField = totalPlays
                        # gets total plays
                        cppLargeHoverList.append(songInfoFormatDetails)

                    elif shaaInfoDetails == "Cycle":
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
                        # on the third cycle, uses seconds
                            shaaDetailField = totalSeconds
                            # sets the field to be total seconds
                            cycleCount += 1
                            # adds 1 to the counter
                            cppLargeHoverList.append("Total Seconds")
                            # adds the string
                        elif cycleCount == 3:
                        # on the fourth (last) cycle, uses plays
                            shaaDetailField = totalPlays
                            # sets the field to be total plays
                            cycleCount = 0
                            # resets the counter
                            cppLargeHoverList.append("Total Plays")
                            # adds the string

                    elif shaaInfoDetails == "Volume":
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
                    
                    elif shaaInfoDetails == "Repeat":
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

                    elif shaaInfoDetails == "Shuffle":
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

                if (finalURI not in csvReader.index) and not firstPlay:
                # if the track wasn't found in CSV and it's not the first time for the track
                    if enableUpdates:
                    # if the updates are enabled
                        mainWin.labelSwap.emit(f"{csName} not found in CSV, using fallback values", 0)
                        # lets user know the song wasn't found in CSV
                    
                ### Top Hour ###

                    if enableTopHour:
                    # if the top hour is enabled
                        currentHour = pd.Timestamp.now().hour
                        # gets the current hour number
                        if currentHour in topHour:
                        # if the current hour matches the stored
                            songStuffList.append(topHourFormat)
                            # adds the top hour format
                            songStuffList.append(songInfoSpacer)
                            # adds the spacer item, too

                ### Field 1 / Field 2 ###

                    if shaaFallback == "Total":
                    # if the selected fallback is Total/total
                        shaaPlaycount = totalPlays if totalPlays else "Several"
                        # uses the total playcount for all songs
                        shaaPlaytime = totalMinutes if totalMinutes else "Numerous"
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
                # forms the 'state' string 
            elif not firstPlay:
            # if the list is empty, and it's not the first play of the track
                cppState = "An amount of time spent listening"
                # puts a fallback string instead
            else:
            # list is empty *because* first play is enabled
                cppState = ""
                # empty string

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
                songNameList.append(csArtistName)
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

        ### C++ Packet Former ###

            if picCycleList == "Spotify":
            # checks if the picture list is set to send pictures from Spotify covers
                cppLargeImage = csCover
                # replaces the image link with the spotify album cover if so

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
                        cppReplace = pickedSong["info"]
                        # gets the song's full dictionary
                        cppSongName = cppReplace["Song"]
                        cppAlbumName = cppReplace["Album"]
                        csArtistName = cppReplace["Artist Name"]
                        cppState = cppReplace["State"]
                        cppLargeImage = cppReplace["Large Image"]
                        cppLargeHover = cppReplace["Large Text"]
                        hoverText = cppReplace["Small Text"]
                        csURL = cppReplace["Spotify URL"]
                        smallURL = cppReplace["Small URL"]
                        # grabs all the relevant details that will replace the current song's information
                        mainWin.blacklistTagFull.emit("New Song", csName, finalURI, cppReplace)
                        # sends a signal to the blacklist manager with the full details
                    else:
                        mainWin.labelSwap.emit("This song is blacklisted, but no favorited songs found!\nPlease favorite at least one song to utilize blacklisting!", 2)
                        # user update
                else:
                # URI is in the blacklist, but not blacklisted (favorite)
                    mainWin.blacklistTag.emit("New Song", csName, finalURI)
                    # sends a signal to the blacklist manager to change the name and information
            else:
            # if the URI isn't in the blacklist
                mainWin.blacklistTag.emit("New Song", csName, finalURI)
                # sends a signal to the blacklist manager to change the name and information

            cppFull = {
                "Playback State": True,
                "Reset Images": False,
                "Song": cppSongName,
                "Song Name": csSongName,
                "Artist Name": (csArtistName if not isLocalSong else "A local artist"),
                "Artist URL": (csArtistURL if not isLocalSong else "A local artist"),
                "Album": cppAlbumName,
                "Album Name": (csAlbumName if not isLocalSong else "A local album"),
                "Album URL": (csAlbumURL if not isLocalSong else "A local album"),
                "Playlist URL": (csPlaylistURL if onPlaylist else "No playlist"),
                "Spotify Image": (csCover if not isLocalSong else "https://i.imgur.com/FeUsGIz.png"),
                "State": cppState,
                "Large Image": cppLargeImage,
                "Large Text": cppLargeHover,
                "Small Text": hoverText,
                "Spotify URL": (csURL if not isLocalSong else "A local song"),
                "Small URL": smallURL,
                "UNIX Start": csUnixStart,
                "UNIX End": csUnixEnd,
                "Song Progress": csProgress,
                "Pause": (not csPlayState),
                "Song Raw": csName,
                "Track ID": trackCounter,
                "URI": csURI,
                "Mapped URI": (altURI if altURI else "N/A"),
                "Playcount": (shaaPlaycountSong if shaaPlaycountSong is not None else "N/A"),
                "Playtime": (shaaPlaytimeMin if shaaPlaytimeMin is not None else "N/A"),
                "SHAA": (not disableShaa)
            }
            # forms a dictionary of the current song's full info (sent to C++ and Flask app, if enabled)

        blacklistInfo = {
            "Song Name": cppFull["Song Name"],
            "Artist Name": cppFull["Artist Name"],
            "Song": cppFull["Song"],
            "Album": cppFull["Album"],
            "State": cppFull["State"],
            "Large Image": cppFull["Large Image"],
            "Large Text": cppFull["Large Text"],
            "Small Text": cppFull["Small Text"],
            "Spotify URL": cppFull["Spotify URL"],
            "Small URL": cppFull["Small URL"]
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
    global currentURI, currentInfo, pauseUpdated, trackCounter, noPlayCounter, lastPlayStamp, lastDSIsave, storedStart, stopLooper
    # global -> local

    playbackRestored = False
    # bool to check if the playback was stopped or not

    while True:
    # this loop checks if the song playing is the same as the previous update, waits if yes, updates the song to match if not

        if stopLooper:
        # if the global bool is True, something wants to stop the looping function
            stopLooper = False
            # sets the bool to False, prevents double-stop
            break
            # breaks the loop

        now = time.time()
        # gets the current time, saves as local variable (used by a few checks)

        if autoSaveTimer != 0:
        # if the auto-saver isn't set to 0 (0 = no saving)
            if (lastDSIsave + (autoSaveTimer * 3600)) < now:
            # if it's been over the defined number of hours since the last auto-save
                mainWin.saveSignal.emit("Auto-Save")
                # sends a save signal to the stopping function of main window (but with not "Shut Down", so it saves, doesn't quit)

        info = authPlayback()
        # picks up all the info Spotify sends in an update
        currentInfo = info
        # sets the global variable to match

        if not info or not info.get("item"):
        # checks if the info "package" has something and if it contains valid information

            if noPlayCounter >= 2:
            # if the counter has reached 2, meaning it's been 3 attempts in a row (0, 1, 2)
                if noPlayCounter == 2:
                # only on the 3rd check
                    mainWin.labelSwap.emit(f"No playback detected for 15 seconds, lowering API rate to 1x/{int(refreshTime + 10)}s and disabling logging until playback continues", 2)
                    # user inform on change of process
                noPlayCounter += 1
                # adds 1 to the counter
                time.sleep(refreshTime + 10)
                # waits for rf+10 seconds (slower API rate)
                continue
                # resets back to looper start
        
            elif noPlayCounter < 3:
            # if the counter is less than 3
                mainWin.labelSwap.emit("No playback detected, re-checking in 5 seconds", 2)
                # user inform
                if noPlayCounter == 0:
                # on the first iteration
                    songEvent.set()
                    # sets a song event -> feed C++ "no playback" status
                time.sleep(5)
                # waits for a few seconds
                noPlayCounter += 1
                # adds 1 to the counter
                continue
                # resets back to looper start

        if noPlayCounter > 0:
        # if the playback has stopped at least once
            playbackRestored = True
            # if the loop progresses this far (doesn't get caught by the continue(s)), sets the bool to True -> different RP print
            noPlayCounter = 0
            # resets the "no playing state" counter to 0

        songURI = (info.get("item")).get("uri")
        # grabs the URI of the song, stores it
        songName = (info.get("item").get("name"))
        # stores name for display purposes
        songProg = ((info.get("progress_ms")) / 1000)
        # grabs the progress of the song at the pull time (ms/1000 = seconds)
        playing = bool(info.get("is_playing"))
        # checks the pause state (True if playing, False if not)

        if playing:
        # if the song is playing
            songStart = int(now - songProg)
            # stores the start time of the song by taking current time and subtracting progress
        else:
        # if the song is paused
            songStart = storedStart
            # uses the last stored value (shouldn't be very far off)

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

        songDur = ((info.get("item")).get("duration_ms") / 1000)
        # grabs both the current time and length of the song (in seconds)
        songLeft = (songDur - songProg)
        # calculates the time left on the song

        songScroll = False
        # defaults the bool to False (no track scrolling)
        if (abs(songStart - storedStart) > 10):
        # if the song's start differs more than 10 seconds from stored start (either direction)
            songScroll = True
            # sets the bool to True

        if (currentURI != songURI) or (songScroll) or (pauseUpdated and playing) or (playbackRestored):
        # if there's a song change - if the URI has changed / the start timestamp differs from the stored timestamp
        # if a pause has been triggered
        # if the playback was cut and is now restored

            if playbackRestored and (currentURI == songURI):
            # if the song "change" is because playback was restored and it's the same song
                mainWin.labelSwap.emit(f"Playback resumed, API rate back to 1/{refreshTime}s", 3)
                # user inform
            elif playbackRestored and (currentURI != songURI):
            # playback was restored AND it's a new song
                mainWin.labelSwap.emit(f"Playback resumed: {songName}, duration: {songDur:,.0f} seconds", 3)
                # user inform
            elif enableUpdates and not pauseUpdated:
            # if console updates are enabled and this change wasn't triggered by a pause
                mainWin.labelSwap.emit(f"{songName}, duration: {songDur:,.0f} seconds", 3)
                # user update on new song
            elif enableUpdates and pauseUpdated and playing:
            # if console updates are enabled and this change *was* triggered by a pause
                mainWin.labelSwap.emit(f"Unpaused: {songName}", 3)
                # user update on unpause

            playbackRestored = False
            # resets the boolean

            if pauseUpdated and playing:
            # if it's playing and the pauseUpdate has been set to true
                pauseUpdated = False
                # sets the pauseUpdated to false, so it doesn't run twice
            elif not pauseUpdated and playing:
            # if it's playing but pauseUpdate is false
                if not (currentURI == songURI and songScroll):
                # ensures the track counter doesn't go up from just scrolling a track
                    trackCounter += 1
                    # adds 1 to counter (means track has changed)

            currentURI = songURI
            # changes the internal variable to match new song
            storedStart = songStart
            # changes timestamp variable to match
            songEvent.set()
            # sets an event to make song() update the presence info

            time.sleep(2)
            # waits 2 seconds
            continue
            # sends back to the start of looper to check for a new song

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
                sleepfor = (songLeft + 0.5)
                # sleeps for the rest of the song (+.5s to ensure the song has ended)

        time.sleep(sleepfor)
        # sleeps for the determined time



### Load Commands ###

bg = None
picThread = None
songThread = None
cppThread = None
mainThread = None
songThreadEvent = None
cppThreadEvent = None
# all start as None so they can be reassigned later (to None and something)

spDataThread = threading.Thread(target = runSPData, daemon=True)
# creates a thread for the localhost Spotify data to update with



### Start Functions ###

def startStart():
    """The function that starts the starter"""
    global bg, picThread, songThread, cppThread, mainThread, songThreadEvent, cppThreadEvent
    # global -> local

    bg = pictureClass(picCycleList, picCycleType, picCycleTime, pictureQueue)
    # defines the background thread as the class containing all the picture function
    # passes the list, type, time and queue

    cppThreadEvent = threading.Event()
    # a threading event used to close the cppThread
    songThreadEvent = threading.Event()
    # a threading event used to close the songThread

    picThread = threading.Thread(target = bg.picCycler, daemon=True)
    # creates a thread for the picture changer
    cppThread = threading.Thread(target = runCpp, daemon=True, args=(cppThreadEvent,))
    # creates a thread for the C++ program to run in - this way it won't stop the main process
    songThread = threading.Thread(target = song, daemon=True, args=(pictureQueue, songThreadEvent,))
    # creates the song thread
    mainThread = threading.Thread(target = mainStart, daemon=True)
    # runs the main program function in a thread

    mainWin.iconChanger("Spotify", "Green", "Icon")
    mainWin.iconChanger("Discord", "Green", "Icon")
    # sets both API icons to green at start, otherwise they may get stuck at some other color

    mainThread.start()
    # starts the main thread

def restartStart():
    """The function that restarts the program"""
    global bg, picThread, songThread, cppThread, mainThread, songThreadEvent, cppThreadEvent
    # global -> local

    bg = None
    picThread = None
    songThread = None
    cppThread = None
    mainThread = None
    songThreadEvent = None
    cppThreadEvent = None
    # all start as None so they can be reassigned later (to None and something)

def mainStart():
    """The function that starts the actual program logic"""
    global bg, picThread, songThread, cppThread, mainThread, songThreadEvent, cppThreadEvent
    # global -> local

    URIFileReader("SHAA")
    URIFileReader("URI")
    URIFileReader("Map")
    # calls the URI loading function to grab all global variables
    blacklistReader()
    # runs the blacklist reader to get the blacklist
    eventer()
    # runs the event reassigner (the Spotify authorisation stuff)

    bg.start()
    # runs the "background" class, which handles the picture updates
    picThread.start()
    # starts the picture thread
    songThread.start()
    # starts the song thread to get updated info

    if hostData:
    # if the boolean for sharing data is enabled
        if not spDataThread.is_alive():
        # if the data thread is not already active
            spDataThread.start()
            # starts the spotify data thread

    if discordAppID and spotifyClientID:
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
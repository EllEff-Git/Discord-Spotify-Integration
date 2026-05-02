import pandas as pd
# Required for all the CSV parsing and data grabbing
import random, subprocess
# Required to choose random pictures and to start the C++ file
import os, sys, time, threading, queue, datetime
# Required for system information, background tasking and queueing
import spotipy, requests, json
# Required for basic function of Spotify data requests and storing
from spotipy.oauth2 import SpotifyOAuth
# Required for authorizing with Spotify
from spotipy.exceptions import SpotifyException
# Required to check for exceptions (errors)
from collections import deque
# Required for "console-like" UI logging
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required for the main window



### Version ###



DSIver = "0.5.2.0537"
"""The program version (Y.M.DD.HHMM)"""



### Directory Grab ###



directory = None
"""The base directory of the program, where DSI.exe resides"""
iconPath = None
"""The path of the app icon png"""


if getattr(sys, "frozen", False):
# since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    iconPath = os.path.join(sys._MEIPASS, "dsiIcon.png")
    # reassigns the path variables accordingly
else:
# if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    iconPath = os.path.join(directory, "icons", "dsiIcon.png")
    # reassigns the path variables accordingly

### Config ###

secretConfigPath = os.path.join(directory, "Data", "secretConfig.json")
"""The main configuration file, contains client secret info"""
dsiConfigPath = os.path.join(directory, "Data", "config.json")
"""The DSI configuration json file"""
dsiConfigWindow = os.path.join(directory, "Qt", "DSI_Qt", "dsiWindow.exe")
"""The DSI configurator program/window"""
shaaConfigPath = os.path.join(directory, "Data", "shaaConfig.json")
"""The SHAA x DSI configuration json file"""

### Token/ID ###

spCache = os.path.join(directory, "Data", "spotifycache.json")
"""The directory where the spotify cache (token) sits in"""
idDir = os.path.join(directory, "Discord", "ids.txt")
"""The directory where ids.txt should/will live (inside DSI/Discord/ids.txt)"""

### Song Details ###

songDataDir = os.path.join(directory, "Discord", "songData.txt")
"""The directory where songData.txt should/will live (inside DSI/Discord/songData.txt)"""
noURIdir = os.path.join(directory, "Data", "URIlist.json")
"""The directory where URIlist (unfound URIs) should/will live"""
uriDir = os.path.join(directory, "Data", "URImap.json")
"""The directory where URImap.json should/will live (inside DSI/Data/URImap.json)"""

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
"""The directory the C++ Exe lives in"""



### Global Variables ###


secretConfig = {}
"""The config file with client IDs and such"""
jsonConfig = None
"""The config file for the main function"""
shaaConfig = None
"""The config file specifically for SHA(A) features"""

sp_client_ID = None
"""Spotify Client ID, string"""
sp_client_secret = None
"""Spotify Client Secret, string"""
sp_redirect = None
"""Spotify redirect URL, string"""
dc_app_ID = None
"""Discord Application ID, string"""

skipConfigWindow = False
"""Whether to skip the configuration window or not"""

refreshTime = 0.0
"""Program update cycle interval time, float"""

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
"""Makes a list of all the possible options for spotify URL types"""

# Picture Cycling Methods #
pictureBehaviorList = ["random", "sequence", "once", "none"]
"""Makes a list of all the possible options for picture cycling types"""

pauseStart = None
"""Makes a starter variable that stores a timestamp when a pause occurs"""

currentInfo = None
"""Song info dictionary"""

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

cycleCount = 0
"""Variable to check the cycle count of hours, minutes and seconds (if enabled)"""

dsiShoutoutStr = "// Data by DSI"
"""A shoutout string to DSI, disabled by default in config"""





### Main Window ###



class DSI_MainWindow(QMainWindow):
    """The main window class"""
    labelSwap = pyqtSignal(str, int)
    # a pyQt signal to swap the label
    readyTag = pyqtSignal()
    # a signal to signal the readiness state of the window

    def __init__(self):
        super().__init__()

    ### Init / Basic ###

        self.show()
        # shows the program window (Windows hides by default)

        self.version = DSIver
        # stores the version in self
        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"DSI Starter v{self.version}"
        # stores the program name

        self.windowSizeX = max(1000, int(startApp.primaryScreen().size().width() / 3))
        self.windowSizeY = max(600, int(startApp.primaryScreen().size().height() / 3))
        # base window sizes (min of 1000 pixels ~33% of the main monitor's width and height)

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(self.windowSizeX, self.windowSizeY))
        # the window size

    ### UI Elements ###

        self.container = QWidget()
        # a container to hold elements
        self.mainLayout = QGridLayout()
        # new grid layout to put elements into
        self.mainLayout.setSpacing(20)
        # sets spacing of 20px to each

        self.mainLayout.setRowMinimumHeight(0, 50)
        self.mainLayout.setRowMinimumHeight(1, 50)
        self.mainLayout.setRowMinimumHeight(2, 100)
        self.mainLayout.setRowMinimumHeight(3, 50)
        self.mainLayout.setRowMinimumHeight(4, 50)
        # sets the minimum height for rows

        self.mainLayout.setColumnMinimumWidth(0, 100)
        self.mainLayout.setColumnMinimumWidth(1, 200)
        self.mainLayout.setColumnMinimumWidth(2, 300)
        self.mainLayout.setColumnMinimumWidth(3, 200)
        self.mainLayout.setColumnMinimumWidth(4, 100)
        # sets the minimum width for columns

        self.mainLayout.setColumnStretch(0, 0)
        self.mainLayout.setColumnStretch(1, 1)
        self.mainLayout.setColumnStretch(3, 1)
        self.mainLayout.setColumnStretch(4, 0)
        self.mainLayout.setColumnStretch(2, 1)
        # allows columns 1, 2 and 3 (center) to stretch
        self.mainLayout.setRowStretch(2, 1)
        # allows row 2 (center) to stretch

        self.container.setLayout(self.mainLayout)
        # sets the container to use layout

        self.mainLabel = QLabel()
        # a label to hold the main information about current process
        self.mainLabel.setText("DSI starter window")
        # initial text
        self.mainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the label
        self.mainLabel.setWordWrap(True)
        # makes the text wrap if it's too big
        self.mainLabel.setFixedSize(300, 50)
        # tells the label to prefer the main layout's size
        self.mainLayout.addWidget(self.mainLabel, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the label to the main layout (should be top, always)

    ### Hideable/Showable Elements ###

        self.userInputField = QLineEdit()
        # creates a new QLineEdit for user to input into
        self.userInputField.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # alings to center
        self.userInputField.setFixedSize(300, 30)
        # sets size
        self.mainLayout.addWidget(self.userInputField, 2, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the qline to layout (row 1, col 0)
        self.userInputField.hide()
        # hides by default

        self.submitButton = QPushButton("Submit")
        # makes a new button to save the iput
        self.submitButton.setFixedSize(60, 35)
        # sets size
        self.mainLayout.addWidget(self.submitButton, 2, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        # adds the button to layout (row 2, col 3)
        self.submitButton.hide()
        # hides by default

    ### Intermediary ###

        self.setCentralWidget(self.container)
        # sets the container to fill the window
        self.labelSwap.connect(self.changeLabel)
        # connects the label swap signal to the change label function
        self.readyTag.connect(startStart)
        # connects the ready tag to the program logic starter

    ### Line "Storage" ###

        self.multiLabel = False
        # sets the multi-string label to false to begin with
        self.lines = deque(maxlen = 15)
        # creates a "deque" to hold a max of 15 items (strings)

    ### Run Arguments ###

        self.requiredItemCheck()
        # runs the required items function to check IDs

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
            text = f"\n\nCRITICAL ERROR\n{time}{text}\n\n"
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

### Window Closer ###

    def stopper(self):
        """A function to close the window"""
        self.close()
        # just closes the window (stops blocking the main program flow)

### Required Stuff Grab ###

    def requiredItemCheck(self):
        """A function to check required items (IDs, etc)"""
        global secretConfig
        # global -> local

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
        global jsonConfig, shaaConfig, disableShaa, skipConfigWindow
        # global -> local

        if os.path.exists(dsiConfigPath):
        # checks if the config already exists (not first time) and the skipping is enabled
            self.labelSwap.emit("Found configuration, reading...", 0)
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

            try:
            # tries to read the config
                skipCfgWin = jsonConfig["disableCfgWin"]
                # whether to prompt user with config window or not, boolean
                self.labelSwap.emit("Configuration found and skipping is enabled, proceeding...", 0)
                # user update
            except:
            # if it can't be read
                skipCfgWin = False
                # sets to true if it can't be grabbed
                self.labelSwap.emit("Could not skip config...", 0)
                # user update
        else:
        # if the config file doesn't exist
            skipCfgWin = False
            # sets the config to false
            
        if not skipCfgWin:
        # if the file doesn't exist or config needs to be rechecked
            dsiConfig = subprocess.run([dsiConfigWindow], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            # runs the dsi configurator (as blocking), continues task once it's done writing config
            if not dsiConfig.returncode == 1:
            # checks if the return code isn't 1 (0 is bad, 1 is good)
                self.labelSwap.emit(f"Configuration complete, proceeding...", 0)
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
            # if the file can't be found/opened
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
        global refreshTime, enablePause, pauseStateText, enableUpdates, enableErrors, enableMapping, timestampStyle, startTime
        # global -> local

        refreshTime = jsonConfig["refreshTime"]
        # grabs the refresh time from config

        if refreshTime < 2:
        # if the refresh time is set too low
            refreshTime = 2
            # overrides to safe minimum of 2s  

        enablePause = jsonConfig["enablePause"]
        pauseStateText = jsonConfig["pauseText"]
        enableUpdates = jsonConfig["printUpdates"]
        enableErrors = jsonConfig["printErrors"]
        enableMapping = jsonConfig["enableURI"]
        timestampStyle = jsonConfig["clockStyle"]
        # loads all options from config

        self.labelSwap.emit("Main configuration loaded, proceeding...", 0)
        # user update
        QTimer.singleShot(1500, self.customConfigLoad)
        # runs the next stage

    def customConfigLoad(self):
        """Function that loads and stores the customisation config options"""
        global smallURL, spotifyURL, songNameSpacerL, songNameSpacerR, preText, postText, enableSong, enableArtist, enableAlbum, albumFallback, picCycleList
        # global -> local

        smallURL = jsonConfig["smallPicURL"]
        if not smallURL:
        # if the smallURL is empty
            smallURL = "https://github.com/EllEff-Git/Discord-Spotify-Integration"
            # shameless plug <3 (only applies if there's no defined URL)
        spotifyURL = jsonConfig["spotifyURLType"]
        songNameSpacerL = jsonConfig["spacerL"]
        songNameSpacerR = jsonConfig["spacerR"]
        preText = jsonConfig["preText"]
        postText = jsonConfig["postText"]
        enableSong = jsonConfig["enableSong"]
        enableArtist = jsonConfig["enableArtist"]
        enableAlbum = jsonConfig["enableAlbum"]
        albumFallback = jsonConfig["albumFallback"]
        picCycleList = jsonConfig["pictureCycleType"]
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

        picCycleTime = jsonConfig["pictureCycleTime"]
        try:
        # tries to turn the time into minutes (ensures integer type, multiplies by 60)
            picCycleTime = (int(picCycleTime) * 60)
        except:
        # if it can't, leaves it alone (should be the case when it's set to "Song")
            None

        picCycleType = jsonConfig["pictureCycleBehavior"]
        smallPic = jsonConfig["smallPic"]
        hoverText = jsonConfig["smallPicHover"]
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

            songInfoField1 = shaaConfig["songInfoField1"]
            songInfoField2 = shaaConfig["songInfoField2"]
            shaaFallbackTotal = shaaConfig["songInfoFallbackTotal"]
            if shaaFallbackTotal:
            # if the fallback total usage is enabled
                shaaFallback = "Total"
                # sets the string to "Total"
            else:
                shaaFallback = shaaConfig["songInfoFallbackText"]
                # gets the custom string from the shaa config

            shaaInfoDetails = shaaConfig["songInfoDetails"]
            if shaaInfoDetails == "Custom":
            # if the details field is set to custom
                shaaInfoDetails = shaaConfig["songInfoDetailsText"]
                # uses the custom string from the config
                songInfoFallback = ""
                # uses empty string (custom string defined above)
            else:
            # if the field isn't custom, uses "total" as an additional string
                songInfoFallback = "total"
                
            songInfoFormatPlays = shaaConfig["songInfoFormatPlays"]
            songInfoSpacer = shaaConfig["songInfoFormatSpacer"]
            songInfoFormatMins = shaaConfig["songInfoFormatMins"]
            songInfoFormatTextFirst = shaaConfig["songInfoDetailsTextFirst"]
            songInfoFormatDetails = shaaConfig["songInfoDetailsText"]
            songInfoFormatDetailsSpacer = shaaConfig["songInfoDetailsSpacer"]
            songInfoDetailsDoubleSpace = shaaConfig["songInfoDetailsDoubleSpace"]
            dsiShoutout = shaaConfig["dsiShoutout"]

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
        # if SHAA is installed
            QTimer.singleShot(2000, self.timeGrabber)
            # calls the next stage (timeGrabber)
        else:
            QTimer.singleShot(1000, self.readyStateReadier)
            # skips timeGrabber

### Total Time Grabber ###

    def timeGrabber(self):
        """Function that grabs the total time counts from totalTimes.txt file"""
        global totalHours, totalMinutes, totalSeconds
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
            times.close()
            # closes the file
        else:
        # if the file for SHA doesn't exist
            if not disableShaa:
            # if SHAA isn't disabled
                self.labelSwap.emit("Could not find totalTimes.txt file, please ensure proper SHAA installation...", 2)
                # there's already a print informing about non-SHAA installation later

        QTimer.singleShot(2500, self.readyStateReadier)
        # calls the next stage 

### Ready State Setter ###

    def readyStateReadier(self):
        """Function that finalizes the window class' progress"""
        self.multiLabel = True
        # sets the boolean to true, allowing further "prints" to utilise more than 1 line of output
        self.setWindowTitle(f"Discord Spotify Integration v{self.version}")
        # sets a new title (starter -> real)

        self.userInputField.deleteLater()
        self.submitButton.deleteLater()
        # deletes the now useless buttons

        self.mainLayout.removeWidget(self.mainLabel)
        # removes the main label widget

        self.mainLabel.setMinimumSize(500, 600)
        # sets minimum sizes for the label (overrides the previous fixed size)

        self.mainLayout.addWidget(self.mainLabel, 0, 2, 5, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the label back, but in the middle of the screen (spans all 5 rows)

        self.mainLayout.setColumnMinimumWidth(0, 20)
        self.mainLayout.setColumnMinimumWidth(1, 20)
        self.mainLayout.setColumnMinimumWidth(2, 500)
        self.mainLayout.setColumnMinimumWidth(3, 20)
        self.mainLayout.setColumnMinimumWidth(4, 20)
        # sets the minimum width for columns

        self.setMinimumSize(620, 650)
        # sets new minimum sizes for window

        self.readyTag.emit()
        # sends a signal to the ready tag to allow progress





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

    main = spotipy.Spotify(auth_manager = authorisation, requests_session = sessionID)
    # same deal with this



### Spotify Data Grabber Function ###



def authPlayback():
    """Function to more "safely" handle Spotify API requests and errors"""
    
    global main
    # takes the global variable for the OAuth

    with spotifyLock:
        # uses a threading lock, to prevent multiple requests at once (shouldn't really happen, but prevents double-access bugs)

        tokenRefresh = False
        # a boolean to determine whether to print the token refresh or reconnect text

        for attempt in range(3):
            # tries a max of 3 times to get Spotify data (typically succeeds 1st try, so if it doesn't work in 3, there's a bigger issue)

            try:
                # first tries to send an API request to Spotify
                
                success = main.current_playback()
                # if it works, returns the Spotify playback package (dictionary)

                if attempt != 0 and enableErrors and not tokenRefresh:
                    # if it's not the first attempt, meaning the reconnect attempt print has already been pushed once
                    mainWin.labelSwap.emit("Reconnect successful!", 0)
                    # prints user update

                elif enableErrors and tokenRefresh:
                    # if the tokenrefresh variable is set to true, that means a connectionerror occurred at least once
                    mainWin.labelSwap.emit("Token refreshed successfully!", 0)
                    # prints user update

                return success
                # sends back the successfully found dictionary to the calling function (should only be looper)
                

            except (SpotifyException, requests.exceptions.RequestException, ConnectionResetError) as error:
                # if it fails to acquire a Spotify playback package

                if enableErrors:
                    # if error printing is enabled

                    # this section individually checks for 4 separate errors, because they were the most common that I had 
                    # (token refreshing isn't *really* an error but is classed as such internally)
                    # while printing 2-3 lines of error code is "helpful", it doesn't really help when the error is a simple, self-fixing one
                    # this is why these (token expiry, read timeout and 429) are checked for first, so it doesn't print a massive chunk

                    if isinstance(error, requests.exceptions.ConnectionError):
                        # if the error is a connection error (token expired)
                        mainWin.labelSwap.emit("Refreshing Spotify token", 1)
                        # doesn't sleep because this is a token error and should get "fixed" nearly instantly
                        # expected to print just about every 3600 seconds (1h)
                        tokenRefresh = True
                        # sets the tokenRefresh flag to true so the next print is more relevant (purely QoL)

                    elif isinstance(error, requests.exceptions.ReadTimeout):
                        # if the error is a read timeout (sort of random)
                        mainWin.labelSwap.emit("Spotify API timeout, retrying in 5 seconds ({attempt+1}/3)", 2)
                        time.sleep(2)
                        # sleeps for 2 seconds (because there's a function-wide 3-second cooldown added on top)

                    elif isinstance(error, SpotifyException) and error.http_status == 429:
                        # if the error is due to a rate limit (429 error code from Spotify)
                        retryTimer = error.headers.get("Retry-After", 5)
                        # gets the retry cooldown timer (or 5, if none is found)
                        mainWin.labelSwap.emit(f"This application is being rate limited by Spotify, retrying in {retryTimer} ({attempt+1}/3)", 2)
                        time.sleep(int(retryTimer) - 3)
                        # sleeps for the duration of retryTimer-3 seconds (because there's a function-wide 3-second cooldown added on top)

                    elif isinstance(error, SpotifyException) and error.http_status == 500:
                        # if the error is 500 (internal error fail)
                        mainWin.labelSwap.emit(f"Spotify internal error (Code 500). Attempting to reconnect ({attempt+1}/3)]", 2)
                        # should never happen, but very very rarely does

                    else:
                        # if the error is anything else
                        mainWin.labelSwap.emit(f"Spotify errored due to {error}.\nAttempting to reconnect ({attempt+1}/3)", 2)

                if attempt == 2:
                    # if it's the last attempt (range(3) = 0,1,2) and it fails
                    mainWin.labelSwap.emit(f"All attempts to reconnect failed due to {error}\nPlease manually restart DSI. Exiting...", 4)
                    time.sleep(60)
                    raise SystemExit
                    # prompts user, then exits

                time.sleep(3)
                # waits 3 seconds to give it some time



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

        if os.path.exists(noURIdir):
            # checks if the uri file (uriList.json) exists
            with open(noURIdir, "r", encoding="utf-8") as URIs:
                # loads the JSON file of URIs
                uriList = json.load(URIs)
                # stores the loaded file as uriList
                if enableUpdates and enableMapping:
                # if the user prints and mapping options are enabled
                    uriLength = len(uriList)
                    # stores the length of the unmapped URI list
                    mainWin.labelSwap.emit(f"{uriLength} URIs stored", 1)
                    # debug-ish list (if using the URI mapper)
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
    with open(noURIdir, "w", encoding="utf-8") as nURI:
    # opens the unfound URI file in write mode
        json.dump(URIs, nURI, indent=3)
        # "dumps" the list of URIs into the file (with indent)



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
                            time.sleep(10)
                            # if the queue isn't empty, waits 10 seconds then re-runs the picture selection

                if self.picCycleType == "once":
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
                    mainWin.labelSwap.emit("Invalid picture cycle behavior or no picture set - proceeding without a picture", 1)
                self.running = False
                False
                # doesn't set a picture, doesn't need to - so it stops the background thread



### C++ ###



def runCpp():
    """Function to run the C++ / Discord RPC program"""
    with subprocess.Popen([cppPath], cwd=cppDir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, creationflags=subprocess.CREATE_NO_WINDOW) as cppPrint:
    # opens the C++ exe, passes the current working directory and takes its output
        if enableUpdates:
        # if user prints are enabled
            for lineRaw in cppPrint.stdout:
            # gets every output line
                line = lineRaw.strip()
                # ensures there's no empty prints
                if line:
                    # every time the C++ file prints something, this program takes it
                    mainWin.labelSwap.emit(f"{line.rstrip()}", 0)
                    # prints it after a line ends



### Song Data File Field Selection/Creation ###



def song(pictureQueue):
    """The function that handles all song data gathering and parsing, as well as pushing to C++ via text"""
    global uriList, cppLargeImage, uriMap, totalHours, totalMinutes, totalSeconds, detailOptions, pauseStart, currentInfo, trackCounter, oldCount
    global cycleCount
    # pulls some global variables to local

    while True:
    # while the loop is active, keeps repeating

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

        csUnixStart = int(time.time() - csProgress + 4)
        # stores the start time of the song by taking current time and subtracting progress
        # adds 5 seconds to shift the Discord timestamps to be slightly behind Spotify (they were a bit ahead before, actually)
        # this way, there shouldn't be a situation where Discord claims the song has ended when it's still playing on Spotify
        csUnixEnd = (csUnixStart + csLength)
        # stores the end time of the song (by adding up the start + duration)

        csPlayState = bool(csFull.get("is_playing"))
        # grabs the playback state (true/false)

        pauseState = False
        # defaults the pauseState to false

        if not csPlayState:
            # if the song is paused

            if pauseStart is None:
                # if there's no set pause time
                pauseStart = int(time.time() + 4)
                # sets the pause time to current time

            pauseState = True
            # sets the pauseState to True

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

                if shaaInfoDetails == "Volume":
                    # if the config calls for volume
                    try:
                        shaaDetailField = f"{csDevice.get("volume_percent")}%"
                        # takes the volume and makes it a percentage
                    except:
                        shaaDetailField = "some volume"
                        # if it fails, puts a fallback string
                    
                if shaaInfoDetails == "Repeat":
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

                if shaaInfoDetails == "Shuffle":
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


        if os.path.isfile(SHAAdir) and not disableShaa:
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

                if finalURI in csvReader.index:
                # checks if the URI is on the CSV (this check is just to prevent double prints)
                    if enableUpdates:
                    # if the user updates are enabled
                        mainWin.labelSwap.emit("Current song found in CSV", 0)

                if finalURI not in uriList:
                # if the URI is not in the URI list yet
                    if enableUpdates:
                        mainWin.labelSwap.emit("URI not found in list, added to URI list", 1)
                    uriList.append(finalURI)
                    # adds it to the list of URIs
                    uriWriter(uriList)
                    # calls the URI writer with the list

                if finalURI not in csvReader.index and altURI in csvReader.index:
                # if the URI is not found in the CSV index, but the alt URI is
                    finalURI = altURI
                    # sets the URI to use the alternate instead
                    if enableUpdates:
                    # if the user updates are enabled
                        mainWin.labelSwap.emit("URI not found in CSV, but mapped URI was", 0)

            if finalURI in csvReader.index:
            # checks if the URI is on the CSV  

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
                    # adds the total playcount to the list

                elif songInfoField1 == "Total":
                # if the selected type for the first field is Total

                    shaaPlaycount = f"{csvReader["Playcount"].agg("sum"):,.0f}"
                    # adds up *all* the playcounts for all tracks
                    songStuffList.append(shaaPlaycount)

                ### Field 1 Format ###

                songStuffList.append(songInfoFormatPlays)
                # adds the first field's custom end styling

                ### Spacer ###

                songStuffList.append(songInfoSpacer)
                # adds the spacer to the list

                ### Minutes / Field 2 ###

                if songInfoField2 == 0 or songInfoField2 == 2 or songInfoField2 == 4:
                # if the selected type for the second field is 0 (track minutes), 2 (track hours) or 4 (track seconds)

                    if isinstance(playtime, pd.Series):
                    # if there's more than one instance of the current song
                        playtimeTotal = int((playtime.sum()) / 1000)
                        # calculates the total playtime (seconds)
                    else:
                    # if there's only one instance of the current song
                        playtimeTotal = int(playtime / 1000)
                        # saves the total as the playtime of the song

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

                elif songInfoField2 == 1 or songInfoField2 == 3 or songInfoField2 == 5:
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
                        shaaDetailField = totalHours
                        # sets the field to be total hours
                        cycleCount += 1
                        # adds 1 to counter
                        cppLargeHoverList.append("Total Hours")
                    elif cycleCount == 1:
                        shaaDetailField = totalMinutes
                        # sets the field to be total minutes
                        cycleCount += 1
                        # adds 1 to counter
                        cppLargeHoverList.append("Total Minutes")
                    elif cycleCount == 2: 
                        shaaDetailField = totalSeconds
                        # sets the field to be total seconds
                        cycleCount = 0
                        # resets to 0 for next time 
                        cppLargeHoverList.append("Total Seconds")
                    # checks which case matches

                elif shaaInfoDetails.lower() == "volume":
                    # if the config calls for volume
                    try:
                        shaaDetailField = f"{csDevice.get("volume_percent")}%"
                        # takes the volume and makes it a percentage
                    except:
                        shaaDetailField = "some volume"
                        # if it fails, puts a fallback string
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # uses the user-formatted one
                
                elif shaaInfoDetails.lower() == "repeat":
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
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # uses the user-formatted one

                elif shaaInfoDetails.lower() == "shuffle":
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
                    cppLargeHoverList.append(songInfoFormatDetails)
                    # uses the user-formatted one

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
            # adds the field and a space

            if dsiShoutout:
            # if the dsi shoutout option is enabled
                cppLargeHoverList.append(dsiShoutoutStr)

            cppLargeHover = "".join(cppLargeHoverList)
            # joins together the list

            ### No Track Match ###

            if finalURI not in csvReader.index:
            # if the track wasn't found in CSV
                if enableUpdates:
                # if the updates are enabled, lets user know the song wasn't found in CSV
                    mainWin.labelSwap.emit(f"{csName} not found in CSV, using fallback values", 1)
                
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

        cppFull = (
                    f"songName = {cppSongName}\n"
                    f"albumName = {cppAlbumName}\n"
                    f"songStuff = {cppState}\n"
                    f"LargeImage = {cppLargeImage}\n"
                    f"LargeText = {cppLargeHover}\n"
                    f"SmallText = {hoverText}\n"
                    f"SpotifyURL = {csURL}\n"
                    f"SmallURL = {smallURL}\n"
                    f"UNIXstart = {str(csUnixStart)}\n"
                    f"UNIXend = {str(csUnixEnd)}\n"
                    f"PauseState = {str(pauseState)}\n"
                    f"Track ID = {str(trackCounter)}" 
                    )
        # merges all the song information together, split by newlines

        with open(songDataDir, "w", encoding="utf-8") as txt:
            # opens the songData text file
            txt.write(cppFull)
            # writes the full song information to the text file, which is read by the C++ program and then sent to Discord RPC
            if enableUpdates:
                mainWin.labelSwap.emit("Song data file updated", 0)
                # if updates are enabled, prints an update

        songEvent.clear()
        # clears the event queue, ready to get new requests



### Information Checking Loop ###



def looper():
    """Function that checks song info on a loop"""
    global currentURI, currentInfo, pauseUpdated, trackCounter
    # grabs the "global" variable (outside the function) as a local variables
    while True:
        # this loop checks if the song playing is the same as the previous update, waits if yes, updates the song to match if not

        info = authPlayback()
        # picks up all the info Spotify sends in an update

        if not info or not info.get("item"):
            # checks if the info has something and if it can be called
            if enableErrors:
                mainWin.labelSwap.emit("No playing state detected, re-checking in 5 seconds", 2)
            time.sleep(5)
            # waits for a few seconds
            continue
        
        currentInfo = info
        # sets the global variable to match

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
            picEvent.set()
            # since this only runs when the program first starts, sets an event immediately to picCycler, to grab a new picture
            songEvent.set()
            # since this only runs when the program first starts, sets an event immediately to song, to refresh data
            if enableUpdates:
                mainWin.labelSwap.emit(f"First song: {songName}, has been successfully processed", 3)
                # if user wants feedback, sends this

        songDur = ((info.get("item")).get("duration_ms")/1000)
        # grabs both the current time and length of the song (in seconds)
        songLeft = (songDur-songProg)
        # calculates the time left on the song

        if (currentURI != songURI) or ((songStart-5) > storedStart) or (pauseUpdated and playing):
        # if there's a song change (if the URI has changed or the start timestamp is higher than the stored timestamp) or if the pause has been triggered

            if enableUpdates and not pauseUpdated:
                # if console updates are enabled and this change wasn't triggered by a pause
                mainWin.labelSwap.emit(f"New song: {songName}, duration: {songDur:,.0f} seconds", 3)
                # user update on new song (makes a new line before itself so it separates tracks)
            elif enableUpdates and pauseUpdated:
                # if console updates are enabled and this change *was* triggered by a pause
                mainWin.labelSwap.emit(f"\nUnpaused: {songName}", 1)

            currentURI = songURI
            # changes the internal variable to match new song
            storedStart = songStart
            # changes timestamp variable to match
            songEvent.set()
            # sets an event to make song() update the text file

            if pauseUpdated:
                # if it's playing and the pauseUpdate has been set to true
                pauseUpdated = False
                # sets the pauseUpdated to false, so it doesn't run twice
            else:
                # if it's playing but pauseUpdate is false
                trackCounter += 1
                # adds 1 to counter (means track has changed)

            time.sleep(2.5)
            # waits 2.5 seconds
            continue
            # sends back to the start of looper to check for a new song (5 second checks after a song change to check for a song skip)

        if not playing and not pauseUpdated:
        # if the song is paused and hasn't yet updated the pause state
            if enablePause:
                # if the pause hasn't been registered yet and the pause behavior is enabled
                songEvent.set()
                # sets an event to make song() update the text file (this way it doesn't spam)
                pauseUpdated = True
                # sets the pause check to True, meaning it has been checked and acted on
                if enableUpdates:
                    # if user updates are on
                    mainWin.labelSwap.emit(f"Paused on: {songName}", 1)
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
                # if there's less song time left than refresh time (if refreshTime = 15, song will have to be <15)
                sleepfor = (songLeft + 1)
                # sleeps for the rest of the song (+1.5s to ensure the song has ended)
                # balance between accuracy and avoiding crazy rates
                
                if enableUpdates:
                    # only prints update if user config set so *and* the song is about to end
                    mainWin.labelSwap.emit(f"New song in {sleepfor:,.0f} seconds", 0)
                    # user inform on new song coming soon

        time.sleep(sleepfor)
        # sleeps for the determined time


### Load Commands ###

def startStart():
    """The function that starts the starter"""
    threading.Thread(target=mainStart, daemon=True).start()
    # runs the runner in a thread

def mainStart():
    """The function that starts the actual program logic"""

    shaaCheck()
    # runs the SHA(A) checker function first, to load global variables

    eventer()
    # runs the event reassigner (the spotify authorisation stuff)

    bg = pictureClass(picCycleList, picCycleType, picCycleTime, pictureQueue)
    # defines the background thread as the class containing all the picture function
    # passes the list, type, time and queue

    bg.start()
    # runs the "background" class, which handles the picture updates

    picThread = threading.Thread(target = bg.picCycler)
    # creates a thread for the picture changer
    picThread.start()
    # starts the picture thread

    songThread = threading.Thread(target = song, args=(pictureQueue,))
    # creates the song thread
    songThread.start()
    # starts the song thread to get updated info

    cppThread = threading.Thread(target = runCpp)
    # creates a thread for the C++ program to run in - this way it won't stop the main process

    if dc_app_ID and sp_client_ID:
        # if both the Application ID and Spotify Client ID are found
        mainWin.labelSwap.emit(f"Found Discord Application ID and Spotify Client ID, starting Discord RPC process", 1)
        # user inform
        time.sleep(3)
        # waits a couple seconds to make sure all details are set before calling
        cppThread.start()
        # starts the C++ thread
    else:
        # if both aren't found
        mainWin.labelSwap.emit("Configuration error! Delete the config file if this error persists! Exiting...", 2)
        # user inform
        time.sleep(60)
        # wait 10 seconds
        raise SystemExit
        # end the program, can't really do much without AppID/Spotify Client ID

    looper()
    # runs the looper, which manages the song refresh cycles





### Window Start ###





startApp = QApplication(sys.argv)
# base app instance (passes command line arguments)
mainWin = DSI_MainWindow()
# creates a window
startApp.exec()
# exceutes the app task (runs the QApplication)
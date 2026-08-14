from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required imports to manage the PyQt window
import json, os, sys, asyncio
# Required for config management



class Ui_DSIWindow(object):
    """The window class"""
    def setupUi(self, DSIWindow):
    # setup (sorry if the docs are a bit weird, this was made with the Qt Creator, I wrote docs after <3)
        if not DSIWindow.objectName():
        # checks for a name 
            DSIWindow.setObjectName(u"DSIWindow")
            # sets the name
        DSIWindow.setMinimumSize(850, 750)
        # sets the window size
        self.window = DSIWindow
        # stores a reference in self to the actual window (so that it can be closed later)

        self.centralWidget = QWidget(DSIWindow)
        # makes a QWidget out of the main window
        self.centralWidget.setObjectName(u"main")
        # sets the object name

        self.thisExeDir = os.path.dirname(sys.executable)
        # the directory this exe is located in
        self.mainIcon = os.path.join(sys._MEIPASS, "dsiIcon.png")
        # the directory containing the program icon png (built-in)
        self.configFolderPath = os.path.join(os.environ["LOCALAPPDATA"], "DSI")
        # the folder path that should contain all the configuration files

        self.mainFolder = os.path.abspath(os.path.join(self.thisExeDir, "..", "..", ".."))
        # stores the "main" folder (DSI, which is 3 folders up)
        self.configPath = os.path.join(self.configFolderPath, "config.json")
        # stores the config file path
        self.shaaPath = os.path.join(self.mainFolder, "runtime", "Qt", "shaaWindow", "shaaWindow.exe")
        # stores the SHAA configuration window path

        self.window.setWindowIcon(QIcon(self.mainIcon))
        # the window icon

        self.window.setWindowTitle("DSI Customisation Configurator")
        # sets title name

        def readConfig() -> dict:
            """Function to read the config file, returns the json dictionary"""
            try:
            # tries to read the config.json
                with open(self.configPath, "r", encoding="utf-8") as cfg:
                # opens the config file in read mode
                    newConfig = json.load(cfg)
                    # stores the contents in self.configuration
                    return newConfig
                    # returns the new config 
            except:
            # if it can't (file doesn't exist)
                defaultConfig = {
                    "enablePause": True,
                    "pauseText": "Paused on:",
                    "smallPicURL": "",
                    "smallPic": "",
                    "smallPicHover": "",
                    "spotifyURLType": "Track",
                    "preText": "",
                    "postText": "",
                    "spacerL": "≺",
                    "spacerR": "≻",
                    "enableSong": True,
                    "enableArtist": True,
                    "enableAlbum": True,
                    "albumFallback": "An album",
                    "pictureCycleType": "Spotify",
                    "pictureCycleTime": 10,
                    "pictureCycleBehavior": "Random"
                }
                # forms a new configuration file from preset defaults

                with open(self.configPath, "w", encoding="utf-8") as cfg:
                # "opens" the config (doesn't exist, so just makes a new one)
                    json.dump(defaultConfig, cfg, indent=3)
                    # writes the default config
                return defaultConfig
                # returns the default config

        self.loadedConfig = readConfig()
        # runs the config reader to get new config info, stores it

### Window Layout ###

        self.fullWindowLayout = QGridLayout(self.centralWidget)
        self.fullWindowLayout.setSpacing(15)
        self.fullWindowLayout.setContentsMargins(15, 0, 20, 15)
        # the main layout, contains all other widgets and layouts

        self.fullWindowLayout.setColumnMinimumWidth(0, 225)
        self.fullWindowLayout.setColumnMinimumWidth(1, 400)
        self.fullWindowLayout.setColumnMinimumWidth(2, 225)
        # sets minimum widths for all columns



### Basic Booleans (0 / 0) ###

        self.basicBooleanGrid = QGridLayout()
        self.basicBooleanGrid.setHorizontalSpacing(5)
        self.basicBooleanGrid.setVerticalSpacing(10)
        self.basicBooleanGrid.setContentsMargins(10, 10, 10, 10)
        # the basic boolean layout 

        self.fullWindowLayout.addLayout(self.basicBooleanGrid, 0, 0)
        # adds to main layout

    ### Pause ###

        self.pauseBoolean = QCheckBox("Enable Pause Text")
        # the checkbox for the pause enabling
        self.pauseBoolean.setChecked(self.loadedConfig["enablePause"])
        # ticks the box automatically
        self.pauseBoolean.setToolTip("Whether to enable the pause text on paused songs")
        # tooltip

        self.pauseText = QLineEdit()
        # the pause text entry
        self.pauseText.setText(self.loadedConfig["pauseText"])
        # sets the text from the config
        self.pauseText.setToolTip("The text to add before the first element, when playback is paused")
        # tooltip

        self.pauseLine = QFrame()
        # the line under the pause text
        self.pauseLine.setFrameShape(QFrame.Shape.HLine)
        self.pauseLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.basicBooleanGrid.addWidget(self.pauseBoolean, 0, 0)
        self.basicBooleanGrid.addWidget(self.pauseText, 1, 0)
        self.basicBooleanGrid.addWidget(self.pauseLine, 2, 0)
        # adds to the layout

    ### Song ###

        self.enableSong = QCheckBox("Enable Song Name")
        # the song boolean
        
        self.enableSong.setChecked(self.loadedConfig["enableSong"])
        # ticks the box automatically
        self.enableSong.setToolTip("Whether to add the song name to the presence string")
        # tooltip

        self.songLine = QFrame()
        # the line under song boolean
        self.songLine.setFrameShape(QFrame.Shape.HLine)
        self.songLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.basicBooleanGrid.addWidget(self.enableSong, 3, 0)
        self.basicBooleanGrid.addWidget(self.songLine, 4, 0)
        # adds to layout
           
    ### Artist ###

        self.enableArtist = QCheckBox("Enable Artist Name")
        # the artist boolean
        self.enableArtist.setChecked(self.loadedConfig["enableArtist"])
        # ticks the box automatically
        self.enableArtist.setToolTip("Whether to add the artist name(s) to the presence string")
        # tooltip

        self.artistLine = QFrame()
        # the line under song boolean
        self.artistLine.setFrameShape(QFrame.Shape.HLine)
        self.artistLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.basicBooleanGrid.addWidget(self.enableArtist, 5, 0)
        self.basicBooleanGrid.addWidget(self.artistLine, 6, 0)
        # adds to layout


    ### Album ###

        self.enableAlbum = QCheckBox("Enable Album Name")
        # the album boolean
        self.enableAlbum.setChecked(self.loadedConfig["enableAlbum"])
        # ticks the box automatically
        self.enableAlbum.setToolTip("Whether to add the album name to the presence string")
        # tooltip

        self.albumLine = QFrame()
        # the line under song boolean
        self.albumLine.setFrameShape(QFrame.Shape.HLine)
        self.albumLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.basicBooleanGrid.addWidget(self.enableAlbum, 7, 0)
        self.basicBooleanGrid.addWidget(self.albumLine, 8, 0)
        # adds to layout



### URL Grid (0 / 1) ###

        self.urlGrid = QGridLayout()
        self.urlGrid.setHorizontalSpacing(5)
        self.urlGrid.setVerticalSpacing(10)
        self.urlGrid.setContentsMargins(10, 10, 10, 10)
        # the grid that holds the URL stuff

        self.fullWindowLayout.addLayout(self.urlGrid, 0, 1)
        # adds to main layout

    ### Round Picture URL ###

        self.roundURLHeader = QLabel()
        # the header for the round picture URL
        self.roundURLHeader.setText("Round Picture Redirect")
        # sets the text

        self.roundURLText = QLineEdit()
        # the round picture URL text entry
        self.roundURLText.setText(self.loadedConfig["smallPicURL"])
        # sets the URL from the config automatically
        self.roundURLText.setToolTip("The link to redirect to when someone clicks on the small, round picture")
        # tooltip

        self.roundURLLine = QFrame()
        # the round url text line
        self.roundURLLine.setFrameShape(QFrame.Shape.HLine)
        self.roundURLLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.urlGrid.addWidget(self.roundURLHeader, 0, 0)
        self.urlGrid.addWidget(self.roundURLText, 1, 0)
        self.urlGrid.addWidget(self.roundURLLine, 2, 0)
        # adds to layout

    ### Round Pic (Discord) ###

        self.roundPicHeader = QLabel()
        # the round picture header text
        self.roundPicHeader.setText("Round Picture")
        # sets the text

        self.roundPicText = QLineEdit()
        # the round picture text entry
        self.roundPicText.setText(self.loadedConfig["smallPic"])
        # sets the picture name from the config file
        self.roundPicText.setToolTip("The name/link of the picture to load in the round frame\nYou can find it from your Developer Dashboard or link a picture")
        # tooltip

        self.roundPicLine = QFrame()
        # the round url text line
        self.roundPicLine.setFrameShape(QFrame.Shape.HLine)
        self.roundPicLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.urlGrid.addWidget(self.roundPicHeader, 3, 0)
        self.urlGrid.addWidget(self.roundPicText, 4, 0)
        self.urlGrid.addWidget(self.roundPicLine, 5, 0)
        # adds to layout

    ### Round Pic Hover ###

        self.roundPicHoverHeader = QLabel()
        # round picture hover text header
        self.roundPicHoverHeader.setText("Round Picture Hover")
        # sets the text

        self.roundPicHoverText = QLineEdit()
        # the round picture hover text entry
        self.roundPicHoverText.setText(self.loadedConfig["smallPicHover"])
        # sets the text from the config file
        self.roundPicHoverText.setToolTip("The text to display when hovering over the round picture")
        # tooltip

        self.roundPicHoverLine = QFrame()
        # the line under the hover text
        self.roundPicHoverLine.setFrameShape(QFrame.Shape.HLine)
        self.roundPicHoverLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.urlGrid.addWidget(self.roundPicHoverHeader, 6, 0)
        self.urlGrid.addWidget(self.roundPicHoverText, 7, 0)
        self.urlGrid.addWidget(self.roundPicHoverLine, 8, 0)
        # adds to layout

    ### Spotify URL ###

        self.spotifyURLoptions = ["Track", "Album", "Artist", "Playlist"]
        # stores all the URL options in a list
        self.loadedURLoption = self.loadedConfig["spotifyURLType"]
        # gets the loaded URL option from config
        self.spotifyURLoptions.remove(self.loadedURLoption)
        # removes the loaded URL option from the list

        self.spotifyURLHeader = QLabel()
        # the header for the Spotify URL
        self.spotifyURLHeader.setText("Spotify Link Type")
        # sets the text

        self.spotifyURLSelection = QComboBox()
        # the dropdown menu of URL options
        self.spotifyURLSelection.addItem(f"{self.loadedURLoption}")
        self.spotifyURLSelection.addItem(f"{self.spotifyURLoptions[0]}")
        self.spotifyURLSelection.addItem(f"{self.spotifyURLoptions[1]}")
        self.spotifyURLSelection.addItem(f"{self.spotifyURLoptions[2]}")
        # adds all the options
        self.spotifyURLSelection.setToolTip("The type of link that gets set into the large picture and song detail fields\n"
            "Note that Playlist requires an active playlist, otherwise defaults to Round Picture URL until an active playlist is found")
        # tooltip

        self.spotifyURLLine = QFrame()
        # the line under the hover text
        self.spotifyURLLine.setFrameShape(QFrame.Shape.HLine)
        self.spotifyURLLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.urlGrid.addWidget(self.spotifyURLHeader, 9, 0)
        self.urlGrid.addWidget(self.spotifyURLSelection, 10, 0)
        self.urlGrid.addWidget(self.spotifyURLLine, 11, 0)
        # adds to layout

    ### Album Fallback ###

        self.albumFallbackHeader = QLabel()
        # the album fallback header text
        self.albumFallbackHeader.setText("Album Fallback Text")
        # sets the text

        self.albumFallbackText = QLineEdit()
        # the album fallback text entry
        self.albumFallbackText.setText(self.loadedConfig["albumFallback"])
        # sets the text from the config file
        self.albumFallbackText.setToolTip("The text to use in the album's place, if the string is too long\n"
                                          "This happens when the presence string exceeds 128 characters")
        # tooltip

        self.urlGrid.addWidget(self.albumFallbackHeader, 12, 0)
        self.urlGrid.addWidget(self.albumFallbackText, 13, 0)
        # adds to layout

### Styling Grid (0 / 2) ###

        self.stylingGrid = QGridLayout()
        self.stylingGrid.setHorizontalSpacing(5)
        self.stylingGrid.setVerticalSpacing(10)
        self.stylingGrid.setContentsMargins(10, 10, 10, 10)
        # the grid that holds the right side entries
        
        self.fullWindowLayout.addLayout(self.stylingGrid, 0, 2)
        # adds the styling grid to the layout

   ### Pre-Text ###

        self.preTextHeader = QLabel()
        # the pre text header
        self.preTextHeader.setText("Pre-Text")
        # sets the text

        self.preText = QLineEdit()
        # the pre text
        self.preText.setText(self.loadedConfig["preText"])
        # sets the text from loaded config automatically
        self.preText.setToolTip("Text placed before the first element (may be omitted)")
        # tooltip

        self.preTextLine = QFrame()
        # the line under preText
        self.preTextLine.setFrameShape(QFrame.Shape.HLine)
        self.preTextLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.stylingGrid.addWidget(self.preTextHeader, 0, 0)
        self.stylingGrid.addWidget(self.preText, 1, 0)
        self.stylingGrid.addWidget(self.preTextLine, 2, 0)
        # adds to layout

    ### Post-Text ###

        self.postTextHeader = QLabel()
        # the post text header
        self.postTextHeader.setText("Post-Text")
        # sets the text

        self.postText = QLineEdit()
        # the post text entry
        self.postText.setText(self.loadedConfig["postText"])
        # sets the text from loaded config automatically
        self.postText.setToolTip("Text placed before the last element (may be omitted)")
        # tooltip

        self.postTextLine = QFrame()
        # the line under postText
        self.postTextLine.setFrameShape(QFrame.Shape.HLine)
        self.postTextLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.stylingGrid.addWidget(self.postTextHeader, 3, 0)
        self.stylingGrid.addWidget(self.postText, 4, 0)
        self.stylingGrid.addWidget(self.postTextLine, 5, 0)
        # adds to layout

    ### Left Spacer ###
  
        self.songSpacerLHeader = QLabel()
        # the left spacer header
        self.songSpacerLHeader.setText("Left Spacer")
        # sets the text

        self.songSpacerL = QLineEdit()
        # the left spacer entry
        self.songSpacerL.setText(self.loadedConfig["spacerL"])
        # loads the text from the config
        self.songSpacerL.setToolTip("The string/spacer placed after the first element\nDefault: \u227a")
        # the left spacer tooltip

        self.spacerLLine = QFrame()
        # the line after left spacer
        self.spacerLLine.setFrameShape(QFrame.Shape.HLine)
        self.spacerLLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.stylingGrid.addWidget(self.songSpacerLHeader, 6, 0)
        self.stylingGrid.addWidget(self.songSpacerL, 7, 0)
        self.stylingGrid.addWidget(self.spacerLLine, 8, 0)
        # adds to layout

    ### Right Spacer ###

        self.songSpacerRHeader = QLabel()
        # the right spacer header
        self.songSpacerRHeader.setText("Right Spacer")
        # sets the text

        self.songSpacerR = QLineEdit()
        # the right spacer entry
        self.songSpacerR.setText(self.loadedConfig["spacerR"])
        # loads the text from the config
        self.songSpacerR.setToolTip("The string/spacer placed after the second element\nDefault: \u227b")
        # tooltip

        self.spacerRLine = QFrame()
        # the line under right spacer
        self.spacerRLine.setFrameShape(QFrame.Shape.HLine)
        self.spacerRLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.stylingGrid.addWidget(self.songSpacerRHeader, 9, 0)
        self.stylingGrid.addWidget(self.songSpacerR, 10, 0)
        self.stylingGrid.addWidget(self.spacerRLine, 11, 0)
        # adds to layout



### Buttons (2 / 0) ###

        self.buttonLayout = QGridLayout()
        # this layout just contains 2 buttons, the shaa button and the starter button

        self.fullWindowLayout.addLayout(self.buttonLayout, 2, 0)
        # adds the vertical (button) layout to the full layout

        self.shaaConfigureButton = QPushButton()
        # the button that opens the SHAA configuration window
        self.shaaConfigureButton.setText("Configure SHAA Details")
        # sets the text
        self.shaaConfigureButton.setToolTip("Opens a new window to configure SHAA details")
        # tooltip
        self.shaaConfigureButton.setMinimumSize(250, 60)
        # sets a minimum size

        self.dsiStarterButton = QPushButton()
        # the button that closes this window and continues previous function (DSI or func config)
        self.dsiStarterButton.setText("Save and close")
        # sets the text
        self.dsiStarterButton.setToolTip("Closes this window and continues DSI process")
        # tooltip
        self.dsiStarterButton.setMinimumSize(250, 60)
        # sets a minimum size

        self.buttonLayout.addWidget(self.shaaConfigureButton, 0, 0)
        # adds the button to the layout
        self.buttonLayout.addWidget(self.dsiStarterButton, 1, 0)
        # adds the start button to the layout

        self.shaaConfigureButton.clicked.connect(self.runShaaWindow)
        # runs the SHAA configuration window when pressed
        self.dsiStarterButton.clicked.connect(self.writeConfig)
        # "connects" the starter button to the config writer (also closes the window)



### Song Preview Text (2 / 1) ###

        self.previewBox = QGridLayout()
        self.previewBox.setSpacing(5)
        self.previewBox.setContentsMargins(20, 10, 20, 10)
        # vertical layout

        self.fullWindowLayout.addLayout(self.previewBox, 2, 1)
        # adds the preview box layout to the main layout

    ### Preview Text ###

        if self.loadedConfig["enablePause"]:
        # if the config option is true
            self.songPreviewText = f"{self.loadedConfig["pauseText"]} a song {self.loadedConfig["spacerL"]} an artist {self.loadedConfig["spacerR"]} {self.loadedConfig["albumFallback"]}"
            # creates a songPreviewText string to be used as a preview for the full styling in "real-time"
        else:
        # if it's not
            self.songPreviewText = f"A song {self.loadedConfig["spacerL"]} an artist {self.loadedConfig["spacerR"]} {self.loadedConfig["albumFallback"]}"
            # uses no pause text 

        self.previewHeader = QLabel()
        # the tooltip for the preview string
        self.previewHeader.setText("Discord Presence String Preview:")
        # sets text

        self.previewText = QLabel()
        # the preview string for how the song should look in Discord (gets constructed below)
        self.previewText.setText(self.songPreviewText)
        # sets the text to the premade string
        self.previewText.setToolTip("This is roughly what the Discord song field will look like")
        # tooltip

        self.previewSpacerTop = QSpacerItem(20, 120, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.previewSpacerBottom = QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        # adds a new layout for the string preview

        self.previewBox.addItem(self.previewSpacerTop, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.previewBox.addWidget(self.previewHeader, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.previewBox.addWidget(self.previewText, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.previewBox.addItem(self.previewSpacerBottom, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout



### Picture Cycle Main (2 / 2) ###

        self.pictureGrid = QGridLayout()
        self.pictureGrid.setHorizontalSpacing(5)
        self.pictureGrid.setVerticalSpacing(10)
        self.pictureGrid.setContentsMargins(10, 10, 10, 10)
        # the layout that hosts the picture-related options

        self.fullWindowLayout.addLayout(self.pictureGrid, 2, 2)
        # adds the picture grid (bottom right) to the main layout

    ### Picture Cycle Types ###

        self.picCycleTypes = ["Spotify", "File", "None"]
        # stores the options for the picture cycling in a list
        self.loadedPicCycleType = self.loadedConfig["pictureCycleType"]
        # gets the loaded option for the type
        self.picCycleTypes.remove(self.loadedPicCycleType)
        # removes the loaded type from the list

        self.pictureCycleHeader = QLabel()
        # the header for the picCyclerType
        self.pictureCycleHeader.setText("Large Picture Type")
        # sets the text

        self.pictureCycleType = QComboBox()
        self.pictureCycleType.addItem(self.loadedPicCycleType)
        self.pictureCycleType.addItem(self.picCycleTypes[0])
        self.pictureCycleType.addItem(self.picCycleTypes[1])
        # dropdown for the type of cycling

        self.pictureCycleType.setToolTip("What to display in the big picture\n"
                                        "'Spotify' uses Spotify's album covers\n"
                                        "'File' reads from pictureList.txt\n"
                                        "'None' doesn't load a picture")
        # tooltip

        self.pictureCycleTypeLine = QFrame()
        self.pictureCycleTypeLine.setFrameShape(QFrame.Shape.HLine)
        self.pictureCycleTypeLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.pictureGrid.addWidget(self.pictureCycleHeader, 0, 0)
        self.pictureGrid.addWidget(self.pictureCycleType, 1, 0)
        self.pictureGrid.addWidget(self.pictureCycleTypeLine, 2, 0)
        # adds to grid

    ### Picture Cycle Time ###

        self.pictureCycleTimeHeader = QLabel()
        # the header for the picture cycle time
        self.pictureCycleTimeHeader.setText("Large Picture Timer")
        # sets the text

        self.pictureCycleTime = QLineEdit()
        # a text field that accepts the picture cycling time (int)
        self.pictureCycleTime.setText(str(self.loadedConfig["pictureCycleTime"]))
        # sets the text from the config
        self.pictureCycleTime.setToolTip("How long to wait between picture changes\nOnly applies if using 'File' in Large Picture Type")
        # tooltip

        self.pictureCycleTimeLine = QFrame()
        # the line under picture cycling time
        self.pictureCycleTimeLine.setFrameShape(QFrame.Shape.HLine)
        self.pictureCycleTimeLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.pictureGrid.addWidget(self.pictureCycleTimeHeader, 3, 0)
        self.pictureGrid.addWidget(self.pictureCycleTime, 4, 0)
        self.pictureGrid.addWidget(self.pictureCycleTimeLine, 5, 0)
        # adds to grid

    ### Picture Cycle Behavior ###

        self.picCycleBehaviors = ["Random", "Sequence", "Once", "None"]
        # stores the options for the picture cycling behavior in a list
        self.loadedPicCycleBehavior = self.loadedConfig["pictureCycleBehavior"]
        # gets the loaded option for the behavior
        self.picCycleBehaviors.remove(self.loadedPicCycleBehavior)
        # removes the loaded type

        self.pictureCycleBehaviorHeader = QLabel()
        # label (text field) for the cycle behavior, above the selection
        self.pictureCycleBehaviorHeader.setText("Large Picture Behavior")
        # sets the text

        self.pictureCycleBehavior = QComboBox()
        self.pictureCycleBehavior.addItem(self.loadedPicCycleBehavior)
        self.pictureCycleBehavior.addItem(self.picCycleBehaviors[0])
        self.pictureCycleBehavior.addItem(self.picCycleBehaviors[1])
        self.pictureCycleBehavior.addItem(self.picCycleBehaviors[2])
        # a dropdown for the cycling behavior
        self.pictureCycleBehavior.setToolTip("How to change the pictures\n"
                                                "Only applies if using 'File' in Large Picture Type"
                                                "'Random' picks a random picture every time\n"
                                                "'Sequence' picks the pictures in order\n"
                                                "'Once' picks a random picture once\n"
                                                "'None' leaves the picture empty")
        # tooltip

        self.pictureGrid.addWidget(self.pictureCycleBehaviorHeader, 6, 0)
        self.pictureGrid.addWidget(self.pictureCycleBehavior, 7, 0)
        # adds to the layout

    ### Central Widget ###

        DSIWindow.setCentralWidget(self.centralWidget)
        # sets central widget

### Connects ###

        self.pauseBoolean.stateChanged.connect(self.previewStringWriter)
        # if the state changes, calls the previewStringWriter
        self.enableSong.stateChanged.connect(self.previewStringWriter)
        # if the state changes, calls the previewStringWriter
        self.enableArtist.stateChanged.connect(self.previewStringWriter)
        # if the state changes, calls the previewStringWriter
        self.enableAlbum.stateChanged.connect(self.previewStringWriter)
        # if the state changes, calls the previewStringWriter

        self.pauseText.textChanged.connect(self.previewStringWriter)
        # if the text changes, calls the previewStringWriter
        self.albumFallbackText.textChanged.connect(self.previewStringWriter)
        # if the text changes, calls the previewStringWriter
        self.preText.textChanged.connect(self.previewStringWriter)
        # if the text changes, calls the previewStringWriter
        self.postText.textChanged.connect(self.previewStringWriter)
        # if the text changes, calls the previewStringWriter
        self.songSpacerL.textChanged.connect(self.previewStringWriter)
        # if the text changes, calls the previewStringWriter
        self.songSpacerR.textChanged.connect(self.previewStringWriter)
        # if the text changes, calls the previewStringWriter

### SHAA Window ###

    def runShaaWindow(self):
        """Function to run the SHAA configuration window"""
        async def asyncRunner():
            # has an integrated async function so it can run asynchronously from the main process
            shaaConfig = await asyncio.create_subprocess_exec(self.shaaPath)
            # runs the SHAA configurator as a subprocess of this subprocess
        asyncio.run(asyncRunner())
        # runs the async runner

### Config Write ###

    def writeConfig(self):
        """Function to write the config json file (and exit)"""
        configuration = {
            "enablePause": self.pauseBoolean.isChecked(),
            "pauseText": self.pauseText.text(),
            "smallPicURL": self.roundURLText.text(),
            "smallPic": self.roundPicText.text(),
            "smallPicHover": self.roundPicHoverText.text(),
            "spotifyURLType": self.spotifyURLSelection.currentText(),
            "preText": self.preText.text(),
            "postText": self.postText.text(),
            "spacerL": self.songSpacerL.text(),
            "spacerR": self.songSpacerR.text(),
            "enableSong": self.enableSong.isChecked(),
            "enableArtist": self.enableArtist.isChecked(),
            "enableAlbum": self.enableAlbum.isChecked(),
            "albumFallback": self.albumFallbackText.text(),
            "pictureCycleType": self.pictureCycleType.currentText(),
            "pictureCycleTime": int(self.pictureCycleTime.text()),
            "pictureCycleBehavior": self.pictureCycleBehavior.currentText()
        }
        # forms a configuration based on the states of each of the fields

        with open(self.configPath, "w", encoding="utf-8") as cfg:
        # opens the config file
            json.dump(configuration, cfg, indent=3)
            # dumps everything in

        self.window.close()
        # closes the whole window

### Preview String ###

    def previewStringWriter(self):
        """Function to modify/write the preview string"""
        previewTextList = []
        # creates an empty list
        boolCounter = 0
        # a counter of booleans to check how many elements should be included

        if self.preText.text():
        # if the pretext is defined
            boolCounter += 1

        if self.enableSong.isChecked():
        # if the song is enabled
            boolCounter += 1
        
        if self.enableArtist.isChecked():
        # if the artist is enabled
            boolCounter += 1

        if self.enableAlbum.isChecked():
        # if the album is enabled
            boolCounter += 1

        if self.postText.text():
        # if the posttext is defined
            boolCounter += 1

        if self.pauseBoolean.isChecked():
        # if the pause is defined
            previewTextList.append(self.pauseText.text())
            # adds the pause text
        if self.preText.text():
        # if the preText is enabled
            previewTextList.append(self.preText.text())
            # adds the pretext
        if self.enableSong.isChecked():
        # if the song is enabled
            previewTextList.append("A song")
            # adds a string
        if self.songSpacerL.text() and (boolCounter >= 2) and self.enableSong.isChecked():
        # if the left spacer is defined (and there's something to chase + the song is enabled, meaning it should go here)
            previewTextList.append(self.songSpacerL.text())
            # adds the left spacer
        if self.enableArtist.isChecked():
        # if the artist is enabled
            previewTextList.append("An artist")
            # adds a string
        if self.songSpacerL.text() and (boolCounter >= 2) and not self.enableSong.isChecked():
            # if every other condition is met, and the song is disabled, moves it here instead
            previewTextList.append(self.songSpacerL.text())
            # adds the left spacer here instead
        if self.songSpacerR and (boolCounter >= 3):
        # if the right spacer is defined (and there's something to chase)
            previewTextList.append(self.songSpacerR.text())
            # adds the right spacer
        if self.enableAlbum.isChecked():
        # if the album is enabled
            previewTextList.append(self.albumFallbackText.text())
            # adds the album fallback string
        if self.postText.text():
        # if the postText is defined
            previewTextList.append(self.postText.text())
            # adds the post text

        self.songPreviewText = " ".join(previewTextList)
        # forms a string from the subparts (which is then entered into the preview string display)
        self.previewText.setText(f"{self.songPreviewText}")
        # sets the preview string from the formed one


### Starter ###


if __name__ == "__main__":
# runs at start

    app = QApplication(sys.argv)
    # creates a Qt Application

    DSIcfgWindow = QMainWindow()
    # creates a window
    ui = Ui_DSIWindow()
    # takes the UI class
    ui.setupUi(DSIcfgWindow)
    # "populates" the UI class

    DSIcfgWindow.show()
    # displays the window

    sys.exit(app.exec())
    # waits for the app to be done, then exits
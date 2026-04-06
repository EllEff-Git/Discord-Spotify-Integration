from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
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
        DSIWindow.setFixedSize(1520, 1070)
        # sets the window size (1520 pixels wide, 1070 tall)
        self.window = DSIWindow
        # stores a reference in self to the actual window (so that it can be closed later)

        self.main = QWidget(DSIWindow)
        # makes a QWidget out of the main window
        self.main.setObjectName(u"main")
        # sets the object name

        if getattr(sys, 'frozen', False):
            self.cwd = os.path.dirname(sys.executable)
        else:
            self.cwd = os.path.dirname(os.path.abspath(__file__))
        # stores the "current working directory" (should be the Qt/DSI_Qt/ folder)
        self.mainFolder = os.path.join(self.cwd, "..", "..")
        # stores the "main" folder (DSI, which is 2 folders up)
        self.configPath = os.path.join(self.mainFolder, "Data", "config.json")
        # stores the config file path
        self.shaaPath = os.path.join(self.mainFolder, "Qt", "SHAA_Qt", "shaaWindow.exe")
        # stores the shaa configuration window path

        self.firstTime = False
        # stores a boolean for the first time launch (False by default)

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
                    "refreshTime": 10,
                    "enablePause": True,
                    "pauseText": "Paused on:",
                    "clockStyle": "System Time",
                    "enableURI": True,
                    "marketCode": "",
                    "printUpdates": True,
                    "printErrors": True,
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
                self.firstTime = True
                # sets the first time boolean to True (this will give a prompt)
                with open(self.configPath, "w", encoding="utf-8") as cfg:
                # "opens" the config (doesn't exist, so just makes a new one)
                    json.dump(defaultConfig, cfg, indent=3)
                    # writes the default config
                return defaultConfig
                # returns the default config

        self.loadedConfig = readConfig()
        # runs the config reader to get new config info, stores it

        self.clockStyleOptions = ["System Time", "Uptime", "Off"]
        # stores all the clock style options in a list
        self.loadedClockStyle = self.loadedConfig["clockStyle"]
        # gets the loaded clock style from config
        self.clockStyleOptions.remove(self.loadedClockStyle)
        # removes the loaded clock style from the list

        self.spotifyURLoptions = ["Track", "Album", "Artist", "Playlist"]
        # stores all the URL options in a list
        self.loadedURLoption = self.loadedConfig["spotifyURLType"]
        # gets the loaded URL option from config
        self.spotifyURLoptions.remove(self.loadedURLoption)
        # removes the loaded URL option from the list

        self.picCycleTypes = ["Spotify", "File", "None"]
        # stores the options for the picture cycling in a list
        self.loadedPicCycleType = self.loadedConfig["pictureCycleType"]
        # gets the loaded option for the type
        self.picCycleTypes.remove(self.loadedPicCycleType)
        # removes the loaded type from the list

        self.picCycleBehaviors = ["Random", "Sequence", "Once", "None"]
        # stores the options for the picture cycling behavior in a list
        self.loadedPicCycleBehavior = self.loadedConfig["pictureCycleBehavior"]
        # gets the loaded option for the behavior
        self.picCycleBehaviors.remove(self.loadedPicCycleBehavior)
        # removes the loaded type

        self.songPreviewText = "A Song - an artist - an album"
        # creates a songPreviewText string to be used as a preview for the full styling in "real-time"

        self.gridLayoutWidget_2 = QWidget(self.main)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(0, 0, 1515, 1060))
        # the "main" ('background') layout in the background, sets size and name

        self.fullWindowLayout = QGridLayout(self.gridLayoutWidget_2)
        self.fullWindowLayout.setSpacing(20)
        self.fullWindowLayout.setObjectName(u"fullWindowLayout")
        self.fullWindowLayout.setContentsMargins(15, 0, 20, 15)
        # the *actual* main layout, contains all other widgets and layouts

        self.pictureGrid = QGridLayout()
        self.pictureGrid.setObjectName(u"pictureGrid")
        self.pictureGrid.setHorizontalSpacing(5)
        self.pictureGrid.setVerticalSpacing(10)
        self.pictureGrid.setContentsMargins(10, 10, 10, 10)
        # the layout that hosts the picture-related options

        self.line_12 = QFrame(self.gridLayoutWidget_2)
        self.line_12.setObjectName(u"line_12")
        self.line_12.setFrameShape(QFrame.Shape.HLine)
        self.line_12.setFrameShadow(QFrame.Shadow.Sunken)
        # a horizontal line
        self.pictureGrid.addWidget(self.line_12, 3, 0, 1, 1)
        # adds the line

        self.pictureCycleTime = QLineEdit(self.gridLayoutWidget_2)
        self.pictureCycleTime.setObjectName(u"pictureCycleTime")
        # a text field that accepts the picture cycling time (int)
        self.pictureGrid.addWidget(self.pictureCycleTime, 5, 0, 1, 1)
        # adds the time input field

        self.line_13 = QFrame(self.gridLayoutWidget_2)
        self.line_13.setObjectName(u"line_13")
        self.line_13.setFrameShape(QFrame.Shape.HLine)
        self.line_13.setFrameShadow(QFrame.Shadow.Sunken)
        # a horizontal line
        self.pictureGrid.addWidget(self.line_13, 7, 0, 1, 1)
        # adds the line

        self.pictureCycleBehaviorHeader = QLabel(self.gridLayoutWidget_2)
        self.pictureCycleBehaviorHeader.setObjectName(u"pictureCycleBehaviorHeader")
        # label (text field) for the cycle behavior, above the selection
        self.pictureGrid.addWidget(self.pictureCycleBehaviorHeader, 8, 0, 1, 1)
        # adds the label

        self.pictureCycleTooltip = QLabel(self.gridLayoutWidget_2)
        self.pictureCycleTooltip.setObjectName(u"pictureCycleTooltip")
        # the tooltip label for the picCycler
        self.pictureGrid.addWidget(self.pictureCycleTooltip, 2, 0, 1, 1)
        # adds the tooltip to the grid

        self.pictureCycleBehavior = QComboBox(self.gridLayoutWidget_2)
        self.pictureCycleBehavior.addItem("")
        self.pictureCycleBehavior.addItem("")
        self.pictureCycleBehavior.addItem("")
        self.pictureCycleBehavior.addItem("")
        self.pictureCycleBehavior.setObjectName(u"pictureCycleBehavior")
        # a combobox (dropdown) for the cycling behavior (gets the strings from the translate I guess)
        self.pictureGrid.addWidget(self.pictureCycleBehavior, 9, 0, 1, 1)
        # adds the combobox to the picture grid

        self.pictureCycleTimeHeader = QLabel(self.gridLayoutWidget_2)
        self.pictureCycleTimeHeader.setObjectName(u"pictureCycleTimeHeader")
        # the header for the picture cycle time
        self.pictureGrid.addWidget(self.pictureCycleTimeHeader, 4, 0, 1, 1)
        # adds the header to the grid

        self.pictureCycleHeader = QLabel(self.gridLayoutWidget_2)
        self.pictureCycleHeader.setObjectName(u"pictureCycleHeader")
        # the header for the cycle type?
        self.pictureGrid.addWidget(self.pictureCycleHeader, 0, 0, 1, 1)
        # adds to grid

        self.pictureCycleType = QComboBox(self.gridLayoutWidget_2)
        self.pictureCycleType.addItem("")
        self.pictureCycleType.addItem("")
        self.pictureCycleType.addItem("")
        self.pictureCycleType.setObjectName(u"pictureCycleType")
        # dropdown for the type of cycling
        self.pictureGrid.addWidget(self.pictureCycleType, 1, 0, 1, 1)
        # adds to grid

        self.pictureCycleTimeTooltip = QLabel(self.gridLayoutWidget_2)
        self.pictureCycleTimeTooltip.setObjectName(u"pictureCycleTimeTooltip")
        # tooltip for the time
        self.pictureGrid.addWidget(self.pictureCycleTimeTooltip, 6, 0, 1, 1)
        # adds to grid

        self.fullWindowLayout.addLayout(self.pictureGrid, 2, 2, 1, 1)
        # adds the picture grid (bottom right) to the main layout

        self.previewBox = QVBoxLayout()
        self.previewBox.setSpacing(5)
        self.previewBox.setObjectName(u"previewBox")
        self.previewBox.setContentsMargins(20, 10, 20, 10)
        self.verticalSpacer_2 = QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        # adds a new layout for the string preview
        self.previewBox.addItem(self.verticalSpacer_2)
        # a vertical spacer, to keep the strings roughly in the middle of the box

        self.previewTooltip = QLabel(self.gridLayoutWidget_2)
        self.previewTooltip.setObjectName(u"previewTooltip")
        # the tooltip for the preview string
        self.previewBox.addWidget(self.previewTooltip)
        # adds to layout

        self.previewText = QLabel(self.gridLayoutWidget_2)
        self.previewText.setObjectName(u"previewText")
        # the preview string for how the song should look in Discord (gets constructed below)
        self.previewBox.addWidget(self.previewText)
        # adds to layout

        self.verticalSpacer = QSpacerItem(20, 120, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        # a second vertical spacer to keep the strings in the middle (one pushes down, other pushes up)
        self.previewBox.addItem(self.verticalSpacer)
        # adds the spacer to the layout

        self.fullWindowLayout.addLayout(self.previewBox, 2, 1, 1, 1)
        # adds the preview box layout to the main layout

        self.basicBooleanGrid = QGridLayout()
        self.basicBooleanGrid.setObjectName(u"basicBooleanGrid")
        self.basicBooleanGrid.setHorizontalSpacing(5)
        self.basicBooleanGrid.setVerticalSpacing(10)
        self.basicBooleanGrid.setContentsMargins(10, 10, 10, 10)
        self.printUpdatesTooltip = QLabel(self.gridLayoutWidget_2)
        self.printUpdatesTooltip.setObjectName(u"printUpdatesTooltip")

        self.basicBooleanGrid.addWidget(self.printUpdatesTooltip, 17, 0, 1, 1)

        self.enableURIMapBoolean = QCheckBox(self.gridLayoutWidget_2)
        self.enableURIMapBoolean.setObjectName(u"enableURIMapBoolean")
        if self.loadedConfig["enableURI"]:
        # if the config option is set to True
            self.enableURIMapBoolean.setChecked(True)
            # ticks the box automatically

        self.basicBooleanGrid.addWidget(self.enableURIMapBoolean, 9, 0, 1, 1)

        self.marketCodeHeader = QLabel(self.gridLayoutWidget_2)
        self.marketCodeHeader.setObjectName(u"marketCodeHeader")

        self.basicBooleanGrid.addWidget(self.marketCodeHeader, 12, 0, 1, 1)

        self.printErrorsBoolean = QCheckBox(self.gridLayoutWidget_2)
        self.printErrorsBoolean.setObjectName(u"printErrorsBoolean")
        if self.loadedConfig["printErrors"]:
        # if the config option is set to True
            self.printErrorsBoolean.setChecked(True)
            # ticks the box automatically

        self.basicBooleanGrid.addWidget(self.printErrorsBoolean, 19, 0, 1, 1)

        self.clockStyleTooltip = QLabel(self.gridLayoutWidget_2)
        self.clockStyleTooltip.setObjectName(u"clockStyleTooltip")

        self.basicBooleanGrid.addWidget(self.clockStyleTooltip, 24, 0, 1, 1)

        self.apiTimerNum = QLineEdit(self.gridLayoutWidget_2)
        self.apiTimerNum.setObjectName(u"apiTimerNum")

        self.basicBooleanGrid.addWidget(self.apiTimerNum, 1, 0, 1, 1)

        self.line_17 = QFrame(self.gridLayoutWidget_2)
        self.line_17.setObjectName(u"line_17")
        self.line_17.setFrameShape(QFrame.Shape.HLine)
        self.line_17.setFrameShadow(QFrame.Shadow.Sunken)

        self.basicBooleanGrid.addWidget(self.line_17, 21, 0, 1, 1)

        self.line_16 = QFrame(self.gridLayoutWidget_2)
        self.line_16.setObjectName(u"line_16")
        self.line_16.setFrameShape(QFrame.Shape.HLine)
        self.line_16.setFrameShadow(QFrame.Shadow.Sunken)

        self.basicBooleanGrid.addWidget(self.line_16, 15, 0, 1, 1)

        self.apiTimerHeader = QLabel(self.gridLayoutWidget_2)
        self.apiTimerHeader.setObjectName(u"apiTimerHeader")

        self.basicBooleanGrid.addWidget(self.apiTimerHeader, 0, 0, 1, 1)

        self.pauseBoolean = QCheckBox(self.gridLayoutWidget_2)
        self.pauseBoolean.setObjectName(u"pauseBoolean")
        if self.loadedConfig["enablePause"]:
        # if the config option is set to True
            self.pauseBoolean.setChecked(True)
            # ticks the box automatically
        self.pauseBoolean.stateChanged.connect(self.previewStringWriter)
        # if the state changes, calls the previewWriter

        self.basicBooleanGrid.addWidget(self.pauseBoolean, 4, 0, 1, 1)

        self.line_4 = QFrame(self.gridLayoutWidget_2)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.basicBooleanGrid.addWidget(self.line_4, 18, 0, 1, 1)

        self.clockStyleHeader = QLabel(self.gridLayoutWidget_2)
        self.clockStyleHeader.setObjectName(u"clockStyleHeader")

        self.basicBooleanGrid.addWidget(self.clockStyleHeader, 22, 0, 1, 1)

        self.clockStyleSelection = QComboBox(self.gridLayoutWidget_2)
        self.clockStyleSelection.addItem("")
        self.clockStyleSelection.addItem("")
        self.clockStyleSelection.addItem("")
        self.clockStyleSelection.setObjectName(u"clockStyleSelection")

        self.basicBooleanGrid.addWidget(self.clockStyleSelection, 23, 0, 1, 1)

        self.printUpdatesBoolean = QCheckBox(self.gridLayoutWidget_2)
        self.printUpdatesBoolean.setObjectName(u"printUpdatesBoolean")
        if self.loadedConfig["printUpdates"]:
        # if the config option is set to True
            self.printUpdatesBoolean.setChecked(True)
            # ticks the box automatically

        self.basicBooleanGrid.addWidget(self.printUpdatesBoolean, 16, 0, 1, 1)

        self.marketCode = QLineEdit(self.gridLayoutWidget_2)
        self.marketCode.setObjectName(u"marketCode")

        self.basicBooleanGrid.addWidget(self.marketCode, 13, 0, 1, 1)

        self.pauseTooltip = QLabel(self.gridLayoutWidget_2)
        self.pauseTooltip.setObjectName(u"pauseTooltip")

        self.basicBooleanGrid.addWidget(self.pauseTooltip, 7, 0, 1, 1)

        self.line = QFrame(self.gridLayoutWidget_2)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.basicBooleanGrid.addWidget(self.line, 3, 0, 1, 1)

        self.pauseText = QLineEdit(self.gridLayoutWidget_2)
        self.pauseText.setObjectName(u"pauseText")
        self.pauseText.textChanged.connect(self.previewStringWriter)
        # if the text changes, calls the previewStringWriter

        self.basicBooleanGrid.addWidget(self.pauseText, 6, 0, 1, 1)

        self.line_2 = QFrame(self.gridLayoutWidget_2)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.basicBooleanGrid.addWidget(self.line_2, 8, 0, 1, 1)

        self.printErrorsTooltip = QLabel(self.gridLayoutWidget_2)
        self.printErrorsTooltip.setObjectName(u"printErrorsTooltip")

        self.basicBooleanGrid.addWidget(self.printErrorsTooltip, 20, 0, 1, 1)

        self.marketCodeTooltip = QLabel(self.gridLayoutWidget_2)
        self.marketCodeTooltip.setObjectName(u"marketCodeTooltip")

        self.basicBooleanGrid.addWidget(self.marketCodeTooltip, 14, 0, 1, 1)

        self.enableURIMapTooltip = QLabel(self.gridLayoutWidget_2)
        self.enableURIMapTooltip.setObjectName(u"enableURIMapTooltip")

        self.basicBooleanGrid.addWidget(self.enableURIMapTooltip, 10, 0, 1, 1)

        self.line_3 = QFrame(self.gridLayoutWidget_2)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.basicBooleanGrid.addWidget(self.line_3, 11, 0, 1, 1)

        self.apiTimerTooltip = QLabel(self.gridLayoutWidget_2)
        self.apiTimerTooltip.setObjectName(u"apiTimerTooltip")

        self.basicBooleanGrid.addWidget(self.apiTimerTooltip, 2, 0, 1, 1)


        self.fullWindowLayout.addLayout(self.basicBooleanGrid, 0, 0, 2, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        # this layout just contains 2 buttons, the shaa button and the starter button

        self.shaaConfigureButton = QPushButton(self.gridLayoutWidget_2)
        self.shaaConfigureButton.setObjectName(u"shaaConfigureButton")
        self.shaaConfigureButton.clicked.connect(self.runShaaWindow)
        # runs the SHAA configuration window when pressed
        self.verticalLayout.addWidget(self.shaaConfigureButton)

        self.dsiStarterButton = QPushButton(self.gridLayoutWidget_2)
        self.dsiStarterButton.setObjectName(u"dsiStarterButton")
        self.dsiStarterButton.clicked.connect(self.writeConfig)
        # "connects" the starter button to the config writer (also closes the window)

        self.verticalLayout.addWidget(self.dsiStarterButton)
        # adds the start button to the layout


        self.fullWindowLayout.addLayout(self.verticalLayout, 2, 0, 1, 1)

        self.urlGrid = QGridLayout()
        self.urlGrid.setObjectName(u"urlGrid")
        self.urlGrid.setHorizontalSpacing(5)
        self.urlGrid.setVerticalSpacing(10)
        self.urlGrid.setContentsMargins(10, 10, 10, 10)
        self.roundURLTooltip = QLabel(self.gridLayoutWidget_2)
        self.roundURLTooltip.setObjectName(u"roundURLTooltip")

        self.urlGrid.addWidget(self.roundURLTooltip, 2, 1, 1, 1)

        self.line_6 = QFrame(self.gridLayoutWidget_2)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.Shape.HLine)
        self.line_6.setFrameShadow(QFrame.Shadow.Sunken)

        self.urlGrid.addWidget(self.line_6, 3, 1, 1, 1)

        self.line_15 = QFrame(self.gridLayoutWidget_2)
        self.line_15.setObjectName(u"line_15")
        self.line_15.setFrameShape(QFrame.Shape.HLine)
        self.line_15.setFrameShadow(QFrame.Shadow.Sunken)

        self.urlGrid.addWidget(self.line_15, 11, 1, 1, 1)

        self.spotifyURLHeader = QLabel(self.gridLayoutWidget_2)
        self.spotifyURLHeader.setObjectName(u"spotifyURLHeader")

        self.urlGrid.addWidget(self.spotifyURLHeader, 12, 1, 1, 1)

        self.roundURLText = QLineEdit(self.gridLayoutWidget_2)
        self.roundURLText.setObjectName(u"roundURLText")
        self.roundURLText.setText(self.loadedConfig["smallPicURL"])
        # sets the URL from the config automatically

        self.urlGrid.addWidget(self.roundURLText, 1, 1, 1, 1)

        self.roundPicHeader = QLabel(self.gridLayoutWidget_2)
        self.roundPicHeader.setObjectName(u"roundPicHeader")

        self.urlGrid.addWidget(self.roundPicHeader, 4, 1, 1, 1)

        self.spotifyURLTooltip = QLabel(self.gridLayoutWidget_2)
        self.spotifyURLTooltip.setObjectName(u"spotifyURLTooltip")

        self.urlGrid.addWidget(self.spotifyURLTooltip, 14, 1, 1, 1)

        self.line_8 = QFrame(self.gridLayoutWidget_2)
        self.line_8.setObjectName(u"line_8")
        self.line_8.setFrameShape(QFrame.Shape.HLine)
        self.line_8.setFrameShadow(QFrame.Shadow.Sunken)

        self.urlGrid.addWidget(self.line_8, 15, 1, 1, 1)

        self.albumFallbackTooltip = QLabel(self.gridLayoutWidget_2)
        self.albumFallbackTooltip.setObjectName(u"albumFallbackTooltip")

        self.urlGrid.addWidget(self.albumFallbackTooltip, 18, 1, 1, 1)

        self.albumFallbackHeader = QLabel(self.gridLayoutWidget_2)
        self.albumFallbackHeader.setObjectName(u"albumFallbackHeader")

        self.urlGrid.addWidget(self.albumFallbackHeader, 16, 1, 1, 1)

        self.albumFallbackText = QLineEdit(self.gridLayoutWidget_2)
        self.albumFallbackText.setObjectName(u"albumFallbackText")

        self.urlGrid.addWidget(self.albumFallbackText, 17, 1, 1, 1)

        self.roundPicHoverText = QLineEdit(self.gridLayoutWidget_2)
        self.roundPicHoverText.setObjectName(u"roundPicHoverText")
        self.roundPicHoverText.setText(self.loadedConfig["smallPicHover"])
        # sets the text from the config file

        self.urlGrid.addWidget(self.roundPicHoverText, 9, 1, 1, 1)

        self.roundPicTooltip = QLabel(self.gridLayoutWidget_2)
        self.roundPicTooltip.setObjectName(u"roundPicTooltip")

        self.urlGrid.addWidget(self.roundPicTooltip, 6, 1, 1, 1)

        self.roundURLHeader = QLabel(self.gridLayoutWidget_2)
        self.roundURLHeader.setObjectName(u"roundURLHeader")

        self.urlGrid.addWidget(self.roundURLHeader, 0, 1, 1, 1)

        self.roundPicHoverTooltip = QLabel(self.gridLayoutWidget_2)
        self.roundPicHoverTooltip.setObjectName(u"roundPicHoverTooltip")

        self.urlGrid.addWidget(self.roundPicHoverTooltip, 10, 1, 1, 1)

        self.roundPicText = QLineEdit(self.gridLayoutWidget_2)
        self.roundPicText.setObjectName(u"roundPicText")
        self.roundPicText.setText(self.loadedConfig["smallPic"])
        # sets the picture name from the config file

        self.urlGrid.addWidget(self.roundPicText, 5, 1, 1, 1)

        self.spotifyURLSelection = QComboBox(self.gridLayoutWidget_2)
        self.spotifyURLSelection.addItem("")
        self.spotifyURLSelection.addItem("")
        self.spotifyURLSelection.addItem("")
        self.spotifyURLSelection.addItem("")
        self.spotifyURLSelection.setObjectName(u"spotifyURLSelection")

        self.urlGrid.addWidget(self.spotifyURLSelection, 13, 1, 1, 1)

        self.line_14 = QFrame(self.gridLayoutWidget_2)
        self.line_14.setObjectName(u"line_14")
        self.line_14.setFrameShape(QFrame.Shape.HLine)
        self.line_14.setFrameShadow(QFrame.Shadow.Sunken)

        self.urlGrid.addWidget(self.line_14, 7, 1, 1, 1)

        self.roundPicHoverHeader = QLabel(self.gridLayoutWidget_2)
        self.roundPicHoverHeader.setObjectName(u"roundPicHoverHeader")

        self.urlGrid.addWidget(self.roundPicHoverHeader, 8, 1, 1, 1)


        self.fullWindowLayout.addLayout(self.urlGrid, 0, 1, 2, 1)

        self.stylingGrid = QGridLayout()
        self.stylingGrid.setObjectName(u"stylingGrid")
        self.stylingGrid.setHorizontalSpacing(5)
        self.stylingGrid.setVerticalSpacing(10)
        self.stylingGrid.setContentsMargins(10, 10, 10, 10)
        
        self.enableAlbumTooltip = QLabel(self.gridLayoutWidget_2)
        self.enableAlbumTooltip.setObjectName(u"enableAlbumTooltip")

        self.stylingGrid.addWidget(self.enableAlbumTooltip, 23, 0, 1, 1)

        self.line_10 = QFrame(self.gridLayoutWidget_2)
        self.line_10.setObjectName(u"line_10")
        self.line_10.setFrameShape(QFrame.Shape.HLine)
        self.line_10.setFrameShadow(QFrame.Shadow.Sunken)

        self.stylingGrid.addWidget(self.line_10, 15, 0, 1, 1)

        self.songSpacerR = QLineEdit(self.gridLayoutWidget_2)
        self.songSpacerR.setObjectName(u"songSpacerR")
        self.songSpacerR.textChanged.connect(self.previewStringWriter)
        # if the text changes, calls the previewWriter

        self.stylingGrid.addWidget(self.songSpacerR, 13, 0, 1, 1)

        self.preTextHeader = QLabel(self.gridLayoutWidget_2)
        self.preTextHeader.setObjectName(u"preTextHeader")

        self.stylingGrid.addWidget(self.preTextHeader, 0, 0, 1, 1)

        self.preTextTooltip = QLabel(self.gridLayoutWidget_2)
        self.preTextTooltip.setObjectName(u"preTextTooltip")

        self.stylingGrid.addWidget(self.preTextTooltip, 2, 0, 1, 1)

        self.line_18 = QFrame(self.gridLayoutWidget_2)
        self.line_18.setObjectName(u"line_18")
        self.line_18.setFrameShape(QFrame.Shape.HLine)
        self.line_18.setFrameShadow(QFrame.Shadow.Sunken)

        self.stylingGrid.addWidget(self.line_18, 3, 0, 1, 1)

        self.postTextHeader = QLabel(self.gridLayoutWidget_2)
        self.postTextHeader.setObjectName(u"postTextHeader")

        self.stylingGrid.addWidget(self.postTextHeader, 4, 0, 1, 1)

        self.postTextTooltip = QLabel(self.gridLayoutWidget_2)
        self.postTextTooltip.setObjectName(u"postTextTooltip")

        self.stylingGrid.addWidget(self.postTextTooltip, 6, 0, 1, 1)

        self.line_5 = QFrame(self.gridLayoutWidget_2)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.stylingGrid.addWidget(self.line_5, 7, 0, 1, 1)

        self.enableAlbum = QCheckBox(self.gridLayoutWidget_2)
        self.enableAlbum.setObjectName(u"enableAlbum")
        if self.loadedConfig["enableAlbum"]:
        # if the config option is set to True
            self.enableAlbum.setChecked(True)
            # ticks the box automatically
        self.enableAlbum.stateChanged.connect(self.previewStringWriter)
        # if the state changes, calls the previewWriter

        self.stylingGrid.addWidget(self.enableAlbum, 22, 0, 1, 1)

        self.line_11 = QFrame(self.gridLayoutWidget_2)
        self.line_11.setObjectName(u"line_11")
        self.line_11.setFrameShape(QFrame.Shape.HLine)
        self.line_11.setFrameShadow(QFrame.Shadow.Sunken)

        self.stylingGrid.addWidget(self.line_11, 11, 0, 1, 1)

        self.enableSong = QCheckBox(self.gridLayoutWidget_2)
        self.enableSong.setObjectName(u"enableSong")
        if self.loadedConfig["enableSong"]:
        # if the config option is set to True
            self.enableSong.setChecked(True)
            # ticks the box automatically
        self.enableSong.stateChanged.connect(self.previewStringWriter)
        # if the state changes, calls the previewWriter

        self.stylingGrid.addWidget(self.enableSong, 16, 0, 1, 1)

        self.songSpacerRHeader = QLabel(self.gridLayoutWidget_2)
        self.songSpacerRHeader.setObjectName(u"songSpacerRHeader")

        self.stylingGrid.addWidget(self.songSpacerRHeader, 12, 0, 1, 1)

        self.songSpacerL = QLineEdit(self.gridLayoutWidget_2)
        self.songSpacerL.setObjectName(u"songSpacerL")
        self.songSpacerL.textChanged.connect(self.previewStringWriter)
        # if the text changes, calls the previewWriter

        self.stylingGrid.addWidget(self.songSpacerL, 9, 0, 1, 1)

        self.songSpacerLHeader = QLabel(self.gridLayoutWidget_2)
        self.songSpacerLHeader.setObjectName(u"songSpacerLHeader")

        self.stylingGrid.addWidget(self.songSpacerLHeader, 8, 0, 1, 1)

        self.songSpacerLTooltip = QLabel(self.gridLayoutWidget_2)
        self.songSpacerLTooltip.setObjectName(u"songSpacerLTooltip")

        self.stylingGrid.addWidget(self.songSpacerLTooltip, 10, 0, 1, 1)

        self.enableArtist = QCheckBox(self.gridLayoutWidget_2)
        self.enableArtist.setObjectName(u"enableArtist")
        if self.loadedConfig["enableArtist"]:
        # if the config option is set to True
            self.enableArtist.setChecked(True)
            # ticks the box automatically
        self.enableArtist.stateChanged.connect(self.previewStringWriter)
        # if the state changes, calls the previewWriter

        self.stylingGrid.addWidget(self.enableArtist, 19, 0, 1, 1)

        self.preText = QLineEdit(self.gridLayoutWidget_2)
        self.preText.setObjectName(u"preText")
        self.preText.setText(self.loadedConfig["preText"])
        # sets the text from loaded config automatically
        self.preText.textChanged.connect(self.previewStringWriter)
        # if the text changes, calls the stringWriter

        self.stylingGrid.addWidget(self.preText, 1, 0, 1, 1)

        self.postText = QLineEdit(self.gridLayoutWidget_2)
        self.postText.setObjectName(u"postText")
        self.postText.setText(self.loadedConfig["postText"])
        # sets the text from loaded config automatically
        self.postText.textChanged.connect(self.previewStringWriter)
        # if the text changes, calls the stringWriter

        self.stylingGrid.addWidget(self.postText, 5, 0, 1, 1)

        self.enableSongTooltip = QLabel(self.gridLayoutWidget_2)
        self.enableSongTooltip.setObjectName(u"enableSongTooltip")

        self.stylingGrid.addWidget(self.enableSongTooltip, 17, 0, 1, 1)

        self.line_9 = QFrame(self.gridLayoutWidget_2)
        self.line_9.setObjectName(u"line_9")
        self.line_9.setFrameShape(QFrame.Shape.HLine)
        self.line_9.setFrameShadow(QFrame.Shadow.Sunken)

        self.stylingGrid.addWidget(self.line_9, 18, 0, 1, 1)

        self.line_7 = QFrame(self.gridLayoutWidget_2)
        self.line_7.setObjectName(u"line_7")
        self.line_7.setFrameShape(QFrame.Shape.HLine)
        self.line_7.setFrameShadow(QFrame.Shadow.Sunken)

        self.stylingGrid.addWidget(self.line_7, 21, 0, 1, 1)

        self.songSpacerRTooltip = QLabel(self.gridLayoutWidget_2)
        self.songSpacerRTooltip.setObjectName(u"songSpacerRTooltip")

        self.stylingGrid.addWidget(self.songSpacerRTooltip, 14, 0, 1, 1)

        self.enableArtistTooltip = QLabel(self.gridLayoutWidget_2)
        self.enableArtistTooltip.setObjectName(u"enableArtistTooltip")

        self.stylingGrid.addWidget(self.enableArtistTooltip, 20, 0, 1, 1)

        self.fullWindowLayout.addLayout(self.stylingGrid, 0, 2, 2, 1)

        DSIWindow.setCentralWidget(self.main)
        self.menubar = QMenuBar(DSIWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1523, 21))
        DSIWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(DSIWindow)
        self.statusbar.setObjectName(u"statusbar")
        DSIWindow.setStatusBar(self.statusbar)

        self.retranslateUi(DSIWindow)
        # applies the translation function to the DSIWindow (basically everything)

        QMetaObject.connectSlotsByName(DSIWindow)
        # connects the DSIWindow

    def retranslateUi(self, DSIWindow):
        """Function to 'translate' the strings, I suppose (auto-generated by Qt Creator)"""

        DSIWindow.setWindowTitle(QCoreApplication.translate("DSI Configuration", u"DSI Configuration", None))
        # the title of the whole window

        self.pictureCycleTimeHeader.setText(QCoreApplication.translate("DSIWindow", u"Picture Cycle Time", None))
        self.pictureCycleTime.setText(QCoreApplication.translate("DSIWindow", f"{self.loadedConfig["pictureCycleTime"]}", None))
        # gets the config option for the time
        self.pictureCycleTimeTooltip.setText(QCoreApplication.translate("DSIWindow", u"How many minutes are awaited between picture swaps ('Song' swaps every track swap)", None))

        self.pictureCycleBehaviorHeader.setText(QCoreApplication.translate("DSIWindow", u"Picture Cycle Behavior", None))
        self.pictureCycleTooltip.setText(QCoreApplication.translate("DSIWindow", u"<html><head/><body><p>How to cycle the big picture<br>Setting to Spotify uses the active album cover (disables cycler)<br>Setting to File reads the picture links from pictureList.txt<br>Setting to None loads no picture (disables cycler)</p></body></html>", None))
        self.pictureCycleBehavior.setItemText(0, QCoreApplication.translate("DSIWindow", f"{self.loadedPicCycleBehavior}", None))
        # takes the loaded config option to display as first
        self.pictureCycleBehavior.setItemText(1, QCoreApplication.translate("DSIWindow", f"{self.picCycleBehaviors[0]}", None))
        self.pictureCycleBehavior.setItemText(2, QCoreApplication.translate("DSIWindow", f"{self.picCycleBehaviors[1]}", None))
        self.pictureCycleBehavior.setItemText(3, QCoreApplication.translate("DSIWindow", f"{self.picCycleBehaviors[2]}", None))
        # the other three get loaded in order

        self.pictureCycleHeader.setText(QCoreApplication.translate("DSIWindow", u"Picture Cycle Type", None))
        self.pictureCycleType.setItemText(0, QCoreApplication.translate("DSIWindow", f"{self.loadedPicCycleType}", None))
        # gets the loaded type from cofnig to display as first
        self.pictureCycleType.setItemText(1, QCoreApplication.translate("DSIWindow", f"{self.picCycleTypes[0]}", None))
        self.pictureCycleType.setItemText(2, QCoreApplication.translate("DSIWindow", f"{self.picCycleTypes[1]}", None))
        # the other two get loaded in order

        self.previewTooltip.setText(QCoreApplication.translate("DSIWindow", u"<html><head/><body><p align=\"center\">Discord Presence String Preview:</p></body></html>", None))
        self.previewText.setText(QCoreApplication.translate("DSIWindow", f"<html><head/><body><p align=\"center\">{self.songPreviewText}</p></body></html>", None))
        # the song preview text field, uses the formed string

        self.enableURIMapBoolean.setText(QCoreApplication.translate("DSIWindow", u"Enable URI Mapping", None))
        self.printErrorsBoolean.setText(QCoreApplication.translate("DSIWindow", u"Show Program Errors", None))

        self.clockStyleTooltip.setText(QCoreApplication.translate("DSIWindow", u"What type of clock (if any) to use in the console", None))
        self.apiTimerNum.setText(QCoreApplication.translate("DSIWindow", f"{self.loadedConfig["refreshTime"]}", None))
        self.apiTimerHeader.setText(QCoreApplication.translate("DSIWindow", u"Spotify API Check Timer:", None))

        self.pauseBoolean.setText(QCoreApplication.translate("DSIWindow", u"Enable Pause Text", None))

        self.clockStyleHeader.setText(QCoreApplication.translate("DSIWindow", u"Console Clock Style", None))
        self.clockStyleSelection.setItemText(0, QCoreApplication.translate("DSIWindow", f"{self.loadedClockStyle}", None))
        # the clock style option - loads the stored style from config to use as the first one
        self.clockStyleSelection.setItemText(1, QCoreApplication.translate("DSIWindow", f"{self.clockStyleOptions[0]}", None))
        self.clockStyleSelection.setItemText(2, QCoreApplication.translate("DSIWindow", f"{self.clockStyleOptions[1]}", None))
        # the other two styles are the only ones left in the list of options (after the config one is removed), this way the first one always matches the config

        self.printUpdatesBoolean.setText(QCoreApplication.translate("DSIWindow", u"Show Program Status", None))
        self.printUpdatesTooltip.setText(QCoreApplication.translate("DSIWindow", u"Whether to display the current status of the program in the console", None))

        self.marketCodeHeader.setText(QCoreApplication.translate("DSIWindow", u"Market Area Code:", None))
        self.marketCode.setText(self.loadedConfig["marketCode"])
        # loads the market code from config (can be empty, is empty by default)
        self.marketCodeTooltip.setText(QCoreApplication.translate("DSIWindow", u"<html><head/><body><p>Your &quot;market area&quot; (the country your Spotify accounts belongs to)<br/>Only used if running the URIMap function<br/>Uses a 2-letter country code (ex. US, JP, DE, SN, CH...)</p></body></html>", None))

        self.pauseTooltip.setText(QCoreApplication.translate("DSIWindow", u"The text to add before the first element, when playback is paused", None))
        self.pauseText.setText(QCoreApplication.translate("DSIWindow", f"{self.loadedConfig["pauseText"]}", None))
        # takes the pause text from the loaded config 

        self.printErrorsTooltip.setText(QCoreApplication.translate("DSIWindow", u"Whether to display potential program and API errors in the console", None))
        self.enableURIMapTooltip.setText(QCoreApplication.translate("DSIWindow", u"Whether to enable the URI mapping function", None))
        self.apiTimerTooltip.setText(QCoreApplication.translate("DSIWindow", u"<html><head/><body><p>How many seconds are waited before sending a new API call<br/>Minimum of 2, recommended range 5 - 15</p></body></html>", None))
        self.shaaConfigureButton.setText(QCoreApplication.translate("DSIWindow", u"Configure SHAA Details\n"
            "(Opens a new window)", None))
        
        self.dsiStarterButton.setText(QCoreApplication.translate("DSIWindow", u"Start DSI\n"
            "(Closes this window, runs DSI)\n"
            "Ensure you press this to save the config!", None))
        # the "start" button (really a save + exit, but it lets the DSI function continue)
        self.roundURLTooltip.setText(QCoreApplication.translate("DSIWindow", u"What static URL to set in the round, smaller picture", None))
        self.spotifyURLHeader.setText(QCoreApplication.translate("DSIWindow", u"Spotify URL Type:", None))
        self.roundPicHeader.setText(QCoreApplication.translate("DSIWindow", u"Round Picture:", None))
        self.spotifyURLTooltip.setText(QCoreApplication.translate("DSIWindow", u"<html><head/><body><p>The link type for the URL that gets set into the link fields (large picture and song detail click)<br/>Note that Playlist requires an active playlist, otherwise defaults to Round Picture URL until an active playlist is found</p></body></html>", None))
        self.roundPicTooltip.setText(QCoreApplication.translate("DSIWindow", u"The name of the picture to load in the round frame (name from Developer Dashboard or link to a picture)", None))
        self.roundURLHeader.setText(QCoreApplication.translate("DSIWindow", u"Round Picture URL:", None))

        self.roundPicHoverHeader.setText(QCoreApplication.translate("DSIWindow", u"Round Picture Hover Text:", None))
        self.roundPicHoverTooltip.setText(QCoreApplication.translate("DSIWindow", u"The text to display when hovering over the round picture", None))

        self.spotifyURLSelection.setItemText(0, QCoreApplication.translate("DSIWindow", f"{self.loadedURLoption}", None))
        # uses the loaded URL option as the first one
        self.spotifyURLSelection.setItemText(1, QCoreApplication.translate("DSIWindow", f"{self.spotifyURLoptions[0]}", None))
        self.spotifyURLSelection.setItemText(2, QCoreApplication.translate("DSIWindow", f"{self.spotifyURLoptions[1]}", None))
        self.spotifyURLSelection.setItemText(3, QCoreApplication.translate("DSIWindow", f"{self.spotifyURLoptions[2]}", None))
        # uses the remaining ones from the list, in order
        
        self.preTextHeader.setText(QCoreApplication.translate("DSIWindow", u"Pre-text:", None))
        self.preTextTooltip.setText(QCoreApplication.translate("DSIWindow", u"Text placed before the first element (may be omitted)", None))
        self.postTextHeader.setText(QCoreApplication.translate("DSIWindow", u"Post-text:", None))
        self.postTextTooltip.setText(QCoreApplication.translate("DSIWindow", u"Text placed before the last element (may be omitted)", None))

        self.albumFallbackHeader.setText(QCoreApplication.translate("DSIWindow", u"Album Fallback Text:", None))
        self.albumFallbackText.setText(QCoreApplication.translate("DSIWindow", f"{self.loadedConfig["albumFallback"]}", None))
        self.albumFallbackTooltip.setText(QCoreApplication.translate("DSIWindow", u"<html><head/><body><p>The text to use in the album's place, if the string is too long<br>This happens when the presence string exceeds 128 characters</p></body></html>", None))

        self.songSpacerLHeader.setText(QCoreApplication.translate("DSIWindow", u"Left Spacer", None))
        self.songSpacerL.setText(QCoreApplication.translate("DSIWindow", f"{self.loadedConfig["spacerL"]}", None))
        self.songSpacerLTooltip.setText(QCoreApplication.translate("DSIWindow", u"<html><head/><body><p>The string/spacer placed after the first element<br>Default: \u227a</p></body></html>", None))

        self.songSpacerRHeader.setText(QCoreApplication.translate("DSIWindow", u"Right Spacer", None))
        self.songSpacerR.setText(QCoreApplication.translate("DSIWindow", f"{self.loadedConfig["spacerR"]}", None))
        self.songSpacerRTooltip.setText(QCoreApplication.translate("DSIWindow", u"<html><head/><body><p>The string/spacer placed after the second element<br>Default: \u227b</p></body></html>", None))

        self.enableSong.setText(QCoreApplication.translate("DSIWindow", u"Enable Song", None))
        self.enableSongTooltip.setText(QCoreApplication.translate("DSIWindow", u"Whether to add the song name to the presence string", None))

        self.enableArtist.setText(QCoreApplication.translate("DSIWindow", u"Enable Artist", None))
        self.enableArtistTooltip.setText(QCoreApplication.translate("DSIWindow", u"Whether to add the artist's name(s) to the presence string", None))

        self.enableAlbum.setText(QCoreApplication.translate("DSIWindow", u"Enable Album", None))
        self.enableAlbumTooltip.setText(QCoreApplication.translate("DSIWindow", u"Whether to add the album name to the presence string", None))


    def runShaaWindow(self):
        """Function to run the SHAA configuration window"""
        async def asyncRunner():
            # has an integrated async function so it can run asynchronously from the main process
            shaaConfig = await asyncio.create_subprocess_exec(self.shaaPath)
            # runs the SHAA configurator as a subprocess of this subprocess
        asyncio.run(asyncRunner())
        # runs the async runner

    def writeConfig(self):
        """Function to write the config json file (and exit)"""
        configuration = {
            "refreshTime": float(self.apiTimerNum.text()),
            "enablePause": self.pauseBoolean.isChecked(),
            "pauseText": self.pauseText.text(),
            "clockStyle": self.clockStyleSelection.currentText(),
            "enableURI": self.enableURIMapBoolean.isChecked(),
            "marketCode": self.marketCode.text(),
            "printUpdates": self.printUpdatesBoolean.isChecked(),
            "printErrors": self.printErrorsBoolean.isChecked(),
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
        # closes the whole process

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
            previewTextList.append("An album")
            # adds a string
        if self.postText.text():
        # if the postText is defined
            previewTextList.append(self.postText.text())
            # adds the post text

        self.songPreviewText = " ".join(previewTextList)
        # forms a string from the subparts (which is then entered into the preview string display)
        self.previewText.setText(QCoreApplication.translate("DSIWindow", f"<html><head/><body><p align=\"center\">{self.songPreviewText}</p></body></html>", None))
        # uses the set "translate" method to apply the new text (this way it's centered, may swap to a different form of centering later)

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
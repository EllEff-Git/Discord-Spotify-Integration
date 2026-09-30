from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required imports to manage the PyQt window
import json, os, sys
# Required for config management



class Ui_SHAAWindow(object):
    """The window class"""
    def setupUi(self, SHAAWindow):
    # setup (sorry if the docs are a bit weird, this was made with the Qt Creator, I wrote docs after <3)
        if not SHAAWindow.objectName():
        # checks for a name 
            SHAAWindow.setObjectName(u"SHAAWindow")
            # sets the name
        SHAAWindow.setMinimumSize(1600, 900)
        # sets the window size 
        self.window = SHAAWindow
        # stores a reference in self to the actual window (so that it can be closed later)

        self.thisExeDir = os.path.dirname(sys.executable)
        # the directory this exe is located in
        self.mainIcon = os.path.join(sys._MEIPASS, "dsiIcon.png")
        # the directory containing the program icon png (built-in)
        self.configFolderPath = os.path.join(os.environ["LOCALAPPDATA"], "DSI")
        # the folder path that should contain all the configuration files

        self.mainFolder = os.path.abspath(os.path.join(self.thisExeDir, "..", "..", ".."))
        # stores the "main" folder (DSI, which is 3 folders up)
        self.configPath = os.path.join(self.configFolderPath, "shaaConfig.json")
        # stores the config file's path

        self.window.setWindowIcon(QIcon(self.mainIcon))
        # the window icon

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
                    "songInfoField1": "Track",
                    "songInfoField2": 0,
                    "songInfoFallbackTotal": True,
                    "songInfoFallbackText": "",
                    "songInfoDetails": "Cycle",
                    "songInfoDetailsCustomText": "",
                    "songInfoFormatPlays": "plays",
                    "songInfoFormatSpacer": "※",
                    "songInfoFormatMins": "minutes",
                    "songInfoDetailsTextFirst": True,
                    "songInfoDetailsText": "Total Hours",
                    "songInfoDetailsSpacer": ":",
                    "songInfoDetailsDoubleSpace": False,
                    "enableFirstTime": True,
                    "firstTimeFormat": "Listening for the first time!",
                    "enableTopHour": False,
                    "topHourFormat": "Listening at peak hours",
                    "enableTopTracks": True,
                    "dsiShoutout": False
                }
                # sets the first time boolean to True (this will give a prompt)
                with open(self.configPath, "w", encoding="utf-8") as cfg:
                # "opens" the config (doesn't exist, so just makes a new one)
                    json.dump(defaultConfig, cfg, indent=3)
                    # writes the default config
                return defaultConfig
                # returns the default config

        self.loadedConfig = readConfig()
        # runs the config reader to get new config info, stores it

        self.songInfoField1Options = ["Track", "Total"]
        # stores the different options the field 1 can have (playcount)
        self.loadedField1Option = self.loadedConfig.get("songInfoField1", "Track")
        # gets the loaded option from file
        self.songInfoField1Options.remove(self.loadedField1Option)
        # removes the current option

        self.songInfoField2Options = ["Track (Minutes)", "Total (Minutes)", "Track (Hours)", "Total (Hours)", "Track (Seconds)", "Total (Seconds)"]
        # stores all the options possible for field 2
        self.loadedField2Option = self.loadedConfig.get("songInfoField2", 0)
        # gets the loaded option from file
        self.poppedField2 = self.songInfoField2Options.pop(self.loadedField2Option)
        # pops the index (0-5) and stores it

        self.songInfoDetailOptions = ["Hours", "Minutes", "Seconds", "Plays", "Cycle", "Volume", "Repeat", "Shuffle", "Custom"]
        # stores all the options possible for details field
        self.loadedDetailOption = self.loadedConfig.get("songInfoDetails", "Cycle")
        # gets the loaded option from file
        self.songInfoDetailOptions.remove(self.loadedDetailOption)
        # removes the current option

        self.mainWidget = QWidget(SHAAWindow)
        # window's central widget

        self.gridLayoutWidget = QWidget(self.mainWidget)
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 1600, 900))
        # the widget that holds all the other elements
    
        self.mainLayout = QGridLayout(self.gridLayoutWidget)
        self.mainLayout.setSpacing(10)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(20, 10, 20, 10)
        # makes and configures the main layout

### Bottom Left ###

        self.bottomLeftGrid = QVBoxLayout()

        self.closeAndSaveButton = QPushButton(self.gridLayoutWidget)
        self.closeAndSaveButton.setText("\nClose SHAA Configurator\n""(Please press this to save the configuration)\n")
        self.closeAndSaveButton.clicked.connect(self.writeConfig)
        self.bottomLeftGrid.addWidget(self.closeAndSaveButton)
        # adds the save button

        self.mainLayout.addLayout(self.bottomLeftGrid, 1, 1, 1, 1)

### Bottom Right ###

        self.bottomRightGrid = QGridLayout()
        self.bottomRightGrid.setObjectName(u"bottomRightGrid")
        self.bottomRightGrid.setHorizontalSpacing(5)
        self.bottomRightGrid.setVerticalSpacing(10)
        self.bottomRightGrid.setContentsMargins(10, 10, 10, 10)
        # bottom right config layout

    ### Opt 1 ###

        self.dsiShoutoutHeader = QLabel(self.gridLayoutWidget)
        self.dsiShoutoutHeader.setText("Whether to enable a DSI shoutout tag :)")
        self.bottomRightGrid.addWidget(self.dsiShoutoutHeader, 0, 0, 1, 1)
        # adds to row 0 

        self.dsiShoutoutCheck = QCheckBox(self.gridLayoutWidget)
        self.dsiShoutoutCheck.setChecked(self.loadedConfig.get("dsiShoutout", False))
        self.dsiShoutoutCheck.setText("Enable Tag")
        self.bottomRightGrid.addWidget(self.dsiShoutoutCheck, 1, 0, 1, 1)
        # adds to row 1 

        self.dsiShoutoutTooltip = QLabel(self.gridLayoutWidget)
        self.dsiShoutoutTooltip.setText('Looks like "// Data by DSI", is added to the end of the detail field\n'
                                        'Ex. "Total Hours: 11,123 // Data by DSI"')
        self.bottomRightGrid.addWidget(self.dsiShoutoutTooltip, 2, 0, 1, 1)
        # adds to row 2

        self.mainLayout.addLayout(self.bottomRightGrid, 1, 3, 1, 1)
        # adds the layout to the bottom right of the main layout

### Top Middle ###

        self.topMidGrid = QGridLayout()
        self.topMidGrid.setHorizontalSpacing(5)
        self.topMidGrid.setVerticalSpacing(10)
        self.topMidGrid.setContentsMargins(10, 10, 10, 10)
        # top middle config layout

    ### Opt 1 ###

        self.songInfoFormatPlaysHeader = QLabel(self.gridLayoutWidget)
        self.songInfoFormatPlaysHeader.setText("The text to display after the number in the first field")
        self.topMidGrid.addWidget(self.songInfoFormatPlaysHeader, 0, 0, 1, 1)
        # adds to row 0

        self.songInfoFormatPlaysText = QLineEdit(self.gridLayoutWidget)
        self.songInfoFormatPlaysText.setText(f"{self.loadedConfig.get("songInfoFormatPlays", "plays")}")
        self.topMidGrid.addWidget(self.songInfoFormatPlaysText, 1, 0, 1, 1)
        # adds to row 1

        self.songInfoFormatPlaysTooltip = QLabel(self.gridLayoutWidget)
        self.songInfoFormatPlaysTooltip.setText("Ex. '2,345 plays' or '2,345 listens' or '2,345 repetitions' or '234,567 total plays'...")
        self.topMidGrid.addWidget(self.songInfoFormatPlaysTooltip, 2, 0, 1, 1)
        # adds to row 2

        self.songInfoFormatPlaysLine = QFrame(self.gridLayoutWidget)
        self.songInfoFormatPlaysLine.setFrameShape(QFrame.Shape.HLine)
        self.songInfoFormatPlaysLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.topMidGrid.addWidget(self.songInfoFormatPlaysLine, 3, 0, 1, 1)
        # adds to row 3

    ### Opt 2 ###

        self.songInfoSpacerHeader = QLabel(self.gridLayoutWidget)
        self.songInfoSpacerHeader.setText("The spacer to place between the first and second field")
        self.topMidGrid.addWidget(self.songInfoSpacerHeader, 4, 0, 1, 1)
        # adds to row 4

        self.songInfoSpacerText = QLineEdit(self.gridLayoutWidget)
        self.songInfoSpacerText.setText(f"{self.loadedConfig.get("songInfoFormatSpacer", "※")}")
        self.topMidGrid.addWidget(self.songInfoSpacerText, 5, 0, 1, 1)
        # adds to row 5

        self.songInfoSpacerTooltip = QLabel(self.gridLayoutWidget)
        self.songInfoSpacerTooltip.setText("Ex. '2,345 plays \u203b 6,789 minutes' or '2,345 plays x 6,789 minutes'...")
        self.topMidGrid.addWidget(self.songInfoSpacerTooltip, 6, 0, 1, 1)
        # adds to row 6

        self.songInfoSpacerLine = QFrame(self.gridLayoutWidget)
        self.songInfoSpacerLine.setFrameShape(QFrame.Shape.HLine)
        self.songInfoSpacerLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.topMidGrid.addWidget(self.songInfoSpacerLine, 7, 0, 1, 1)
        # adds to row 7

    ### Opt 3 ###

        self.songInfoFormatMinsHeader = QLabel(self.gridLayoutWidget)
        self.songInfoFormatMinsHeader.setText("The text to display after the number in the first field")
        self.topMidGrid.addWidget(self.songInfoFormatMinsHeader, 8, 0, 1, 1)
        # adds to row 8

        self.songInfoFormatMinsText = QLineEdit(self.gridLayoutWidget)
        self.songInfoFormatMinsText.setText(f"{self.loadedConfig.get("songInfoFormatMins", "minutes")}")
        self.topMidGrid.addWidget(self.songInfoFormatMinsText, 9, 0, 1, 1)
        # adds to row 9

        self.songInfoFormatMinsTooltip = QLabel(self.gridLayoutWidget)
        self.songInfoFormatMinsTooltip.setText("Ex. '6,789 minutes' or '678,910 total minutes'...")
        self.topMidGrid.addWidget(self.songInfoFormatMinsTooltip, 10, 0, 1, 1)
        # adds to row 10

        self.songInfoFormatMinsLine = QFrame(self.gridLayoutWidget)
        self.songInfoFormatMinsLine.setFrameShape(QFrame.Shape.HLine)
        self.songInfoFormatMinsLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.topMidGrid.addWidget(self.songInfoFormatMinsLine, 11, 0, 1, 1)
        # adds to row 11

    ### Opt 4 ###

        self.firstTimeLabel = QLabel(self.gridLayoutWidget)
        self.firstTimeLabel.setText("Whether to enable special text for first-time tracks")
        self.topMidGrid.addWidget(self.firstTimeLabel, 12, 0, 1, 1)
        # adds to row 12

        self.firstTimeCheck = QCheckBox(self.gridLayoutWidget)
        self.firstTimeCheck.setText("First Time Text")
        self.firstTimeCheck.setChecked(self.loadedConfig.get("enableFirstTime", True))
        self.topMidGrid.addWidget(self.firstTimeCheck, 13, 0, 1, 1)
        # adds to row 13

        self.firstTimeTooltip = QLabel(self.gridLayoutWidget)
        self.firstTimeTooltip.setText("If the song has 0 plays, enables custom text to use (set below)\n"
                                    "Requires SHAA installed and requires URI mapping to be enabled")
        self.topMidGrid.addWidget(self.firstTimeTooltip, 14, 0, 1, 1)
        # adds to row 14

        self.firstTimeSpacerLine = QFrame(self.gridLayoutWidget)
        self.firstTimeSpacerLine.setFrameShape(QFrame.Shape.HLine)
        self.firstTimeSpacerLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.topMidGrid.addWidget(self.firstTimeSpacerLine, 15, 0, 1, 1)
        # adds to row 15

    ### Opt 5 ###

        self.firstTimeTextLabel = QLabel(self.gridLayoutWidget)
        self.firstTimeTextLabel.setText("The text to use for first time tracks")
        self.topMidGrid.addWidget(self.firstTimeTextLabel, 16, 0, 1, 1)
        # adds to row 16

        self.firstTimeTextLine = QLineEdit(self.gridLayoutWidget)
        self.firstTimeTextLine.setText(self.loadedConfig.get("firstTimeFormat", "Listening for the first time!"))
        self.topMidGrid.addWidget(self.firstTimeTextLine, 17, 0, 1, 1)
        # adds to row 17

        self.firstTimeTextSpacerLine = QFrame(self.gridLayoutWidget)
        self.firstTimeTextSpacerLine.setFrameShape(QFrame.Shape.HLine)
        self.firstTimeTextSpacerLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.topMidGrid.addWidget(self.firstTimeTextSpacerLine, 18, 0, 1, 1)
        # adds to row 18

    ### Opt 6 ###

        self.hourlyDataLabel = QLabel(self.gridLayoutWidget)
        self.hourlyDataLabel.setText("Whether to to enable special text for the top listening hour")
        self.topMidGrid.addWidget(self.hourlyDataLabel, 19, 0, 1, 1)
        # adds to row 19

        self.hourlyDataCheck = QCheckBox(self.gridLayoutWidget)
        self.hourlyDataCheck.setText("Top Hour Text")
        self.hourlyDataCheck.setChecked(self.loadedConfig.get("enableTopHour", False))
        self.topMidGrid.addWidget(self.hourlyDataCheck, 20, 0, 1, 1)
        # adds to row 20

        self.hourlyDataTooltip = QLabel(self.gridLayoutWidget)
        self.hourlyDataTooltip.setText("If the current time aligns with the SHAA data's 'top hour', enables custom text to use (set below)\n" \
                                        "Adds the same spacer used between first and second fields")
        self.topMidGrid.addWidget(self.hourlyDataTooltip, 21, 0, 1, 1)
        # adds to row 21

        self.hourlyDataLine = QFrame(self.gridLayoutWidget)
        self.hourlyDataLine.setFrameShape(QFrame.Shape.HLine)
        self.hourlyDataLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.topMidGrid.addWidget(self.hourlyDataLine, 22, 0, 1, 1)
        # adds to row 22

    ### Opt 7 ###

        self.hourlyDataTextLabel = QLabel(self.gridLayoutWidget)
        self.hourlyDataTextLabel.setText("The text to use for the top hour")
        self.topMidGrid.addWidget(self.hourlyDataTextLabel, 23, 0, 1, 1)
        # adds to row 23

        self.hourlyDataTextLine = QLineEdit(self.gridLayoutWidget)
        self.hourlyDataTextLine.setText(self.loadedConfig.get("topHourFormat", "Listening at peak hours"))
        self.topMidGrid.addWidget(self.hourlyDataTextLine, 24, 0, 1, 1)
        # adds to row 24

    ### Bottom ###

        self.topMiddleSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.topMidGrid.addItem(self.topMiddleSpacer, 25, 0, 1, 1)
        # adds to row 25

        self.mainLayout.addLayout(self.topMidGrid, 0, 1, 1, 1)
        # adds the layout to the top middle of the main layout

### Top Left ###

        self.topLeftGrid = QGridLayout()
        self.topLeftGrid.setHorizontalSpacing(5)
        self.topLeftGrid.setVerticalSpacing(10)
        self.topLeftGrid.setContentsMargins(10, 10, 10, 10)
        # top left side layout

    ### Row 0 ###

        self.songInfoField1Header = QLabel(self.gridLayoutWidget)
        self.songInfoField1Header.setText("The type of data to display in the first field (playcount)")
        self.topLeftGrid.addWidget(self.songInfoField1Header, 0, 0, 1, 1)
        # adds to row 0

    ### Row 1 ###

        self.songInfoField1Dropdown = QComboBox(self.gridLayoutWidget)
        self.songInfoField1Dropdown.addItem(f"{self.loadedField1Option}")
        self.songInfoField1Dropdown.addItem(f"{self.songInfoField1Options[0]}")
        self.topLeftGrid.addWidget(self.songInfoField1Dropdown, 1, 0, 1, 1)
        # adds to row 1

    ### Row 2 ###

        self.songInfoField1Tooltip = QLabel(self.gridLayoutWidget)
        self.songInfoField1Tooltip.setText("Track displays per-track data (ex. 2,345 plays)\nTotal displays total account data (ex. 234,567 plays)")
        self.topLeftGrid.addWidget(self.songInfoField1Tooltip, 2, 0, 1, 1)
        # adds to row 2

    ### Row 3 ###

        self.songInfoField1Line = QFrame(self.gridLayoutWidget)
        self.songInfoField1Line.setFrameShape(QFrame.Shape.HLine)
        self.songInfoField1Line.setFrameShadow(QFrame.Shadow.Sunken)
        self.topLeftGrid.addWidget(self.songInfoField1Line, 3, 0, 1, 1)
        # adds to row 3

    ### Row 4 ###

        self.songInfoField2Header = QLabel(self.gridLayoutWidget)
        self.songInfoField2Header.setText("The type of data to display in the second field (playtime)")
        self.topLeftGrid.addWidget(self.songInfoField2Header, 4, 0, 1, 1)
        # adds to row 4

    ### Row 5 ###

        self.songInfoField2Dropdown = QComboBox(self.gridLayoutWidget)
        self.songInfoField2Dropdown.addItem(f"{self.poppedField2}")
        self.songInfoField2Dropdown.addItem(f"{self.songInfoField2Options[0]}")
        self.songInfoField2Dropdown.addItem(f"{self.songInfoField2Options[1]}")
        self.songInfoField2Dropdown.addItem(f"{self.songInfoField2Options[2]}")
        self.songInfoField2Dropdown.addItem(f"{self.songInfoField2Options[3]}")
        self.songInfoField2Dropdown.addItem(f"{self.songInfoField2Options[4]}")
        self.topLeftGrid.addWidget(self.songInfoField2Dropdown, 5, 0, 1, 1)
        # adds to row 5

    ### Row 6 ###

        self.songInfoField2Tooltip = QLabel(self.gridLayoutWidget)
        self.songInfoField2Tooltip.setText("Track displays per-track data (ex. 6,789 minutes)\nTotal displays total account data (ex. 678,910 minutes)")
        self.topLeftGrid.addWidget(self.songInfoField2Tooltip, 6, 0, 1, 1)
        # adds to row 6

    ### Row 7 ###

        self.songInfoField2Line = QFrame(self.gridLayoutWidget)
        self.songInfoField2Line.setFrameShape(QFrame.Shape.HLine)
        self.songInfoField2Line.setFrameShadow(QFrame.Shadow.Sunken)
        self.topLeftGrid.addWidget(self.songInfoField2Line, 7, 0, 1, 1)
        # adds to row 7

    ### Row 8 ###

        self.shaaFallbackHeader = QLabel(self.gridLayoutWidget)
        self.shaaFallbackHeader.setText("The type of data to fallback on, if the current song isn't found in the CSV")
        self.topLeftGrid.addWidget(self.shaaFallbackHeader, 8, 0, 1, 1)
        # adds to row 8

    ### Row 9 ###

        self.shaaFallbackTotalCheck = QCheckBox(self.gridLayoutWidget)
        self.shaaFallbackTotalCheck.setChecked(self.loadedConfig.get("songInfoFallbackTotal", True))
        self.shaaFallbackTotalCheck.setText("Total")
        self.topLeftGrid.addWidget(self.shaaFallbackTotalCheck, 9, 0, 1, 1)
        # adds to row 9

    ### Row 10 ###

        self.shaaFallbackText = QLineEdit(self.gridLayoutWidget)
        self.shaaFallbackText.setText(self.loadedConfig.get("songInfoFallbackText", ""))
        self.topLeftGrid.addWidget(self.shaaFallbackText, 10, 0, 1, 1)
        # adds to row 10

    ### Row 11 ###

        self.shaaFallbackTooltip = QLabel(self.gridLayoutWidget)
        self.shaaFallbackTooltip.setText("If the Total checkbox is checked, uses total counts/times\n"
                                        "A custom string can be entered instead, if preferred, in the text field")
        self.topLeftGrid.addWidget(self.shaaFallbackTooltip, 11, 0, 1, 1)
        # adds to row 11

    ### Row 12 ###

        self.shaaFallbackLine = QFrame(self.gridLayoutWidget)
        self.shaaFallbackLine.setFrameShape(QFrame.Shape.HLine)
        self.shaaFallbackLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.topLeftGrid.addWidget(self.shaaFallbackLine, 12, 0, 1, 1)
        # adds to row 12

    ### Row 13 ###

        self.shaaInfoDetailsHeader = QLabel(self.gridLayoutWidget)
        self.shaaInfoDetailsHeader.setText("The type of data to display in the details field")
        self.topLeftGrid.addWidget(self.shaaInfoDetailsHeader, 13, 0, 1, 1)
        # adds to row 13

    ### Row 14 ###

        self.shaaInfoDetailsDropdown = QComboBox(self.gridLayoutWidget)
        self.shaaInfoDetailsDropdown.addItem(f"{self.loadedDetailOption}")
        self.shaaInfoDetailsDropdown.addItem(f"{self.songInfoDetailOptions[0]}")
        self.shaaInfoDetailsDropdown.addItem(f"{self.songInfoDetailOptions[1]}")
        self.shaaInfoDetailsDropdown.addItem(f"{self.songInfoDetailOptions[2]}")
        self.shaaInfoDetailsDropdown.addItem(f"{self.songInfoDetailOptions[3]}")
        self.shaaInfoDetailsDropdown.addItem(f"{self.songInfoDetailOptions[4]}")
        self.shaaInfoDetailsDropdown.addItem(f"{self.songInfoDetailOptions[5]}")
        self.shaaInfoDetailsDropdown.addItem(f"{self.songInfoDetailOptions[6]}")
        self.shaaInfoDetailsDropdown.addItem(f"{self.songInfoDetailOptions[7]}")
        self.topLeftGrid.addWidget(self.shaaInfoDetailsDropdown, 14, 0, 1, 1)
        # adds to row 14

    ### Row 15 ###

        self.shaaInfoDetailsTooltip = QLabel(self.gridLayoutWidget)
        self.shaaInfoDetailsTooltip.setText("Hours takes the total account hours\n"
                                            "Minutes takes the total account minutes\n"
                                            "Seconds takes the total account seconds\n"
                                            "Plays takes the total account playcount\n"
                                            "Cycle goes between the hours, minutes, seconds and plays every song\n"
                                            "Volume tries to take the current playing Spotify volume\n"
                                            "Repeat takes the current repeat state\n"
                                            "Shuffle takes the current shuffle state\n"
                                            "Custom enables the custom text below")
        self.topLeftGrid.addWidget(self.shaaInfoDetailsTooltip, 15, 0, 1, 1)
        # adds to row 15

    ### Row 16 ###

        self.shaaInfoDetailsCustomText = QLineEdit(self.gridLayoutWidget)
        self.shaaInfoDetailsCustomText.setText(f"{self.loadedConfig.get("songInfoDetailsCustomText", "")}")
        self.topLeftGrid.addWidget(self.shaaInfoDetailsCustomText, 16, 0, 1, 1)
        # adds to row 16

        self.topLeftSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.topLeftGrid.addItem(self.topLeftSpacer, 18, 0, 1, 1)

        self.mainLayout.addLayout(self.topLeftGrid, 0, 0, 2, 1)
        # adds the layout to the top left of the main layout

### Top Right ###

        self.topRightGrid = QGridLayout()
        self.topRightGrid.setHorizontalSpacing(5)
        self.topRightGrid.setVerticalSpacing(10)
        self.topRightGrid.setContentsMargins(10, 10, 10, 10)
        # top right side layout

    ### Opt 1 ###

        self.songInfoFormatDetailsOrderHeader = QLabel(self.gridLayoutWidget)
        self.songInfoFormatDetailsOrderHeader.setText("Whether to place the text before the number in the details field")
        self.topRightGrid.addWidget(self.songInfoFormatDetailsOrderHeader, 0, 0, 1, 1)
        # adds to row 0

        self.songInfoFormatDetailsOrderCheck = QCheckBox(self.gridLayoutWidget)
        self.songInfoFormatDetailsOrderCheck.setText("Text First")
        self.songInfoFormatDetailsOrderCheck.setChecked(self.loadedConfig.get("songInfoDetailsTextFirst", True))
        self.topRightGrid.addWidget(self.songInfoFormatDetailsOrderCheck, 1, 0, 1, 1)
        # adds to row 1

        self.songInfoFormatDetailsOrderLine = QFrame(self.gridLayoutWidget)
        self.songInfoFormatDetailsOrderLine.setFrameShape(QFrame.Shape.HLine)
        self.songInfoFormatDetailsOrderLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.topRightGrid.addWidget(self.songInfoFormatDetailsOrderLine, 2, 0, 1, 1)
        # adds to row 2

    ### Opt 2 ###

        self.songInfoFormatDetailsHeader = QLabel(self.gridLayoutWidget)
        self.songInfoFormatDetailsHeader.setText("The text to display before or after the number in the details field")
        self.topRightGrid.addWidget(self.songInfoFormatDetailsHeader, 3, 0, 1, 1)
        # adds to row 3

        self.songInfoFormatDetailsText = QLineEdit(self.gridLayoutWidget)
        self.songInfoFormatDetailsText.setText(f"{self.loadedConfig.get("songInfoDetailsText", "Total Hours")}")
        self.topRightGrid.addWidget(self.songInfoFormatDetailsText, 4, 0, 1, 1)
        # adds to row 4

        self.songInfoFormatDetailsTooltip = QLabel(self.gridLayoutWidget)
        self.songInfoFormatDetailsTooltip.setText("Ex. 'Total Hours: 11,123 ' or 'Hours: 11,123' or 'Hours listened; 11,123'... (Text First on)\n"
                                                "Ex. '11,123 Total Hours' or '11,123 hours' or '11,123 hours listened'... (Text First off)")
        self.topRightGrid.addWidget(self.songInfoFormatDetailsTooltip, 5, 0, 1, 1)
        # adds to row 5

        self.songInfoFormatDetailsLine = QFrame(self.gridLayoutWidget)
        self.songInfoFormatDetailsLine.setFrameShape(QFrame.Shape.HLine)
        self.songInfoFormatDetailsLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.topRightGrid.addWidget(self.songInfoFormatDetailsLine, 6, 0, 1, 1)
        # adds to row 6

    ### Opt 3 ###

        self.songInfoFormatSpacerHeader = QLabel(self.gridLayoutWidget)
        self.songInfoFormatSpacerHeader.setText("The spacer to use between the number and text in the details field")
        self.topRightGrid.addWidget(self.songInfoFormatSpacerHeader, 7, 0, 1, 1)
        # adds to row 7

        self.songInfoFormatSpacerText = QLineEdit(self.gridLayoutWidget)
        self.songInfoFormatSpacerText.setText(f"{self.loadedConfig.get("songInfoDetailsSpacer", ":")}")
        self.topRightGrid.addWidget(self.songInfoFormatSpacerText, 8, 0, 1, 1)
        # adds to row 8

        self.songInfoFormatSpacerTooltip = QLabel(self.gridLayoutWidget)
        self.songInfoFormatSpacerTooltip.setObjectName(u"songInfoFormatSpacerTooltip")
        self.songInfoFormatSpacerTooltip.setText("Ex. 'Total Hours: 11,123' or 'Total Hours - 11,123' or 'Total Hours = 11,123'...")
        self.topRightGrid.addWidget(self.songInfoFormatSpacerTooltip, 9, 0, 1, 1)
        # adds to row 9

        self.songInfoFormatSpacerLine = QFrame(self.gridLayoutWidget)
        self.songInfoFormatSpacerLine.setFrameShape(QFrame.Shape.HLine)
        self.songInfoFormatSpacerLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.topRightGrid.addWidget(self.songInfoFormatSpacerLine, 10, 0, 1, 1)
        # adds to row 10

    ### Opt 4 ###

        self.doubleSpaceLabel = QLabel(self.gridLayoutWidget)
        self.doubleSpaceLabel.setText("Whether to add a space on either side of the spacer in the details field")
        self.topRightGrid.addWidget(self.doubleSpaceLabel, 11, 0, 1, 1)
        # adds to row 11

        self.doubleSpaceCheck = QCheckBox(self.gridLayoutWidget)
        self.doubleSpaceCheck.setText("Add both spaces")
        self.doubleSpaceCheck.setChecked(self.loadedConfig.get("songInfoDetailsDoubleSpace", True))
        self.topRightGrid.addWidget(self.doubleSpaceCheck, 12, 0, 1, 1)
        # adds to row 12

        self.doubleSpaceTooltip = QLabel(self.gridLayoutWidget)
        self.doubleSpaceTooltip.setText("Ex. 'Total Hours: 11,123' or 'Total Hours : 11,123'...")
        self.topRightGrid.addWidget(self.doubleSpaceTooltip, 13, 0, 1, 1)
        # adds to row 13

        self.doubleSpaceSpacerLine = QFrame(self.gridLayoutWidget)
        self.doubleSpaceSpacerLine.setFrameShape(QFrame.Shape.HLine)
        self.doubleSpaceSpacerLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.topRightGrid.addWidget(self.doubleSpaceSpacerLine, 14, 0, 1, 1)
        # adds to row 14

    ### Opt 5 ###

        self.topTrackLabel = QLabel(self.gridLayoutWidget)
        self.topTrackLabel.setText("Whether to enable top track prefixes before the first/second fields\nEx. '#2 track with 2,345 plays \u203b 6,789 minutes'")
        self.topRightGrid.addWidget(self.topTrackLabel, 15, 0, 1, 1)
        # adds to row 15

        self.topTrackCheck = QCheckBox(self.gridLayoutWidget)
        self.topTrackCheck.setText("Top Track Prefixes")
        self.topTrackCheck.setChecked(self.loadedConfig.get("enableTopTracks", True))
        self.topRightGrid.addWidget(self.topTrackCheck, 16, 0, 1, 1)
        # adds to row 16

    ### Spacer ###

        self.topRightGridSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.topRightGrid.addItem(self.topRightGridSpacer, 21, 0, 1, 1)
        # adds to row 21

        self.mainLayout.addLayout(self.topRightGrid, 0, 3, 1, 1)

    ### Main ###

        SHAAWindow.setCentralWidget(self.mainWidget)
        QMetaObject.connectSlotsByName(SHAAWindow)


    def writeConfig(self):
        """Function to write the config json file (and exit)"""
        configuration = {
            "songInfoField1": self.songInfoField1Dropdown.currentText(),
            "songInfoField2": self.songInfoField2Dropdown.currentIndex(),
            "songInfoFallbackTotal": self.shaaFallbackTotalCheck.isChecked(),
            "songInfoFallbackText": self.shaaFallbackText.text(),
            "songInfoDetails": self.shaaInfoDetailsDropdown.currentText(),
            "songInfoDetailsCustomText": self.shaaInfoDetailsCustomText.text(),
            "songInfoFormatPlays": self.songInfoFormatPlaysText.text(),
            "songInfoFormatSpacer": self.songInfoSpacerText.text(),
            "songInfoFormatMins": self.songInfoFormatMinsText.text(),
            "songInfoDetailsTextFirst": self.songInfoFormatDetailsOrderCheck.isChecked(),
            "songInfoDetailsText": self.songInfoFormatDetailsText.text(),
            "songInfoDetailsSpacer": self.songInfoFormatSpacerText.text(),
            "songInfoDetailsDoubleSpace": self.doubleSpaceCheck.isChecked(),
            "enableFirstTime": self.firstTimeCheck.isChecked(),
            "firstTimeFormat": self.firstTimeTextLine.text(),
            "dsiShoutout": self.dsiShoutoutCheck.isChecked()
        }
        # forms a configuration based on the states of each of the fields

        with open(self.configPath, "w", encoding="utf-8") as cfg:
        # opens the config file
            json.dump(configuration, cfg, indent=3)
            # dumps everything in

        self.window.close()
        # closes the whole process

if __name__ == "__main__":

    app = QApplication(sys.argv)
    # creates a Qt Application

    SHAAcfgWindow = QMainWindow()
    # creates a window
    ui = Ui_SHAAWindow()
    # takes the UI class
    ui.setupUi(SHAAcfgWindow)
    # "populates" the UI class

    SHAAcfgWindow.show()
    # displays the window

    sys.exit(app.exec())
    # waits for the app to be done, then exits
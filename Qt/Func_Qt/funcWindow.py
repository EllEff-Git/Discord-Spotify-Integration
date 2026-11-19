from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required imports to manage the PyQt window
import json, os, sys
# Required for config management



class functionConfigWindow(QMainWindow):
    """The window class"""
    def __init__(self):
        super().__init__()
        # init

        self.monitorSizeX = app.primaryScreen().size().width()
        self.monitorSizeY = app.primaryScreen().size().height()
        # grabs the main window sizes to use as default sizes

        self.mainWinX = max(400, int(self.monitorSizeX / 6))
        self.mainWinY = int(self.mainWinX * 2)
        # forms default window sizes 
        self.mainWinPosX = ((self.monitorSizeX - self.mainWinX) / 2)
        self.mainWinPosY = ((self.monitorSizeY - self.mainWinY) / 2)
        # forms default window positions

        self.setMinimumSize(self.mainWinX, self.mainWinY)
        # sets the window size 
        self.mainWidget = QWidget()
        # makes a QWidget for the main window

        self.thisExeDir = os.path.dirname(sys.executable)
        # the directory this exe is located in
        self.mainIcon = os.path.join(sys._MEIPASS, "dsiIcon.png")
        # the directory containing the program icon png (built-in)
        self.configFolderPath = os.path.join(os.environ["LOCALAPPDATA"], "DSI")
        # the folder path that should contain all the configuration files

        self.mainFolder = os.path.abspath(os.path.join(self.thisExeDir, "..", "..", ".."))
        # stores the "main" folder (DSI, which is 3 folders up)
        self.configPath = os.path.join(self.configFolderPath, "functionConfig.json")
        # stores the config file's path

        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setWindowTitle("DSI Functionality Configuration")
        # sets title name
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

                self.firstTime = True
                # sets the first time boolean to True (this will give a prompt)

                defaultConfig = {
                    "disableCfgWin": False,
                    "refreshTime": 10.0,
                    "clockStyle": "System Time",
                    "enableURI": True,
                    "printUpdates": True,
                    "printErrors": True,
                    "consoleLength": 25,
                    "marketCode": "",
                    "hostData": True,
                    "addressType": "Device",
                    "autoSaveTimer": 2,
                    "autoRestart": True,
                    "savePosData": True,
                    "DSIwidth": self.mainWinX,
                    "DSIheight": self.mainWinY,
                    "DSIxPos": self.mainWinPosX,
                    "DSIyPos": self.mainWinPosY,
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

    ### Int Validator ###

        self.hourValidator = QIntValidator(0, 24)
        # int validator for 0-24 hours (auto-save)



    ### Main Layout ###

        self.mainLayout = QGridLayout(self.mainWidget)
        # sets the main layout to use a grid of the central
        self.mainLayout.setContentsMargins(25, 25, 25, 25)
        # sets margins of 25px 
        self.mainLayout.setVerticalSpacing(25)
        # sets vertical spacing

    ### Option Layout ###

        self.optionLayout = QGridLayout()
        # adds a grid layout for the options
        self.optionLayout.setContentsMargins(25, 25, 25, 25)
        # sets margins of 25px
        self.optionLayout.setVerticalSpacing(15)
        # sets vertical spacing
        self.optionLayout.setHorizontalSpacing(10)
        # sets horizontal spacing between elements

        self.optionLayout.setColumnStretch(0, 0)
        self.optionLayout.setColumnStretch(1, 0)
        # disables columns stretching automatically

        self.mainLayout.addLayout(self.optionLayout, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # sets the option layout into the main

    ### Title ###

        self.configTitle = QLabel("DSI Configuration\nHover any text for details")
        # title
        self.configTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.mainLayout.addWidget(self.configTitle, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the title to the main layout

    ### Enable URI ###

        self.enableURILabel = QLabel("Enable URI Mapping")
        # label for the URI enable option
        self.enableURILabel.setToolTip("Whether the URI mapping/storing should be enabled")
        # tooltip

        self.enableURICheck = QCheckBox()
        # checkbox for the URI check
        self.enableURICheck.setChecked(self.loadedConfig.get("enableURI", True))
        # sets the check state based on the config

        self.optionLayout.addWidget(self.enableURILabel, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.enableURICheck, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout

    ### Refresh Time ###

        self.refreshTimeLabel = QLabel("Refresh Time")
        # label for the refresh timer
        self.refreshTimeLabel.setToolTip("How often new data is requested from Spotify API\nRecommended: 5 - 10, minimum: 3")
        # tooltip
        
        self.refreshTimeLine = QLineEdit()
        # the line edit for the refresh time
        self.refreshTimeLine.setMaximumWidth(40)
        # sets max width to avoid it pushing everything insanely far
        self.refreshTimeLine.setText(f"{self.loadedConfig.get("refreshTime", 10.0)}")
        # sets the text to match the config text

        self.optionLayout.addWidget(self.refreshTimeLabel, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.refreshTimeLine, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Update Print ###

        self.printUpdatesLabel = QLabel("Print Updates")
        # label for the update printing
        self.printUpdatesLabel.setToolTip("Display program progress updates")
        # tooltip

        self.printUpdatesCheck = QCheckBox()
        self.printUpdatesCheck.setChecked(self.loadedConfig.get("printUpdates", True))
        # sets the check state based on the config

        self.optionLayout.addWidget(self.printUpdatesLabel, 3, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.printUpdatesCheck, 3, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout

    ### Error Print ###

        self.printErrorsLabel = QLabel("Print Errors")
        # label for the error printing
        self.printErrorsLabel.setToolTip("Display program errors")
        # tooltip

        self.printErrorsCheck = QCheckBox()
        self.printErrorsCheck.setChecked(self.loadedConfig.get("printErrors", True))
        # sets the check state based on the config

        self.optionLayout.addWidget(self.printErrorsLabel, 4, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.printErrorsCheck, 4, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout

    ### Disable Config ###

        self.disableCfgWinLabel = QLabel("Disable Auto-Config")
        # label for config window disabling
        self.disableCfgWinLabel.setToolTip("Skip opening the configuration windows at startup\nThey can be accessed at any time via the Configure button, this just manages the auto-run functionality")
        # tooltip

        self.disableCfgWinCheck = QCheckBox()
        self.disableCfgWinCheck.setChecked(self.loadedConfig.get("disableCfgWin", False))
        # sets the check state based on the config

        self.optionLayout.addWidget(self.disableCfgWinLabel, 5, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.disableCfgWinCheck, 5, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout

    ### Console Length ###

        self.consoleLengthLabel = QLabel("Console Length")
        # label for console length
        self.consoleLengthLabel.setToolTip("How many lines of the program status are stored\nDefault: 25, minimum: 5, maximum: 250")
        # tooltip

        self.consoleLengthLine = QLineEdit()
        # the console length entry line
        self.consoleLengthLine.setMaximumWidth(40)
        # sets max width to avoid it pushing everything insanely far
        self.consoleLengthLine.setText(f"{self.loadedConfig.get("consoleLength", 25)}")
        # sets the text to match the config

        self.optionLayout.addWidget(self.consoleLengthLabel, 6, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.consoleLengthLine, 6, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Market Code ###

        self.marketCodeLabel = QLabel("Market Code")
        # the market code label
        self.marketCodeLabel.setToolTip("The market code of your current region\n"
                                        "This is used for URI mapping\n"
                                        "Enter in the 2-letter country code format\n"
                                        "Ex. US, JP, DE, SN, CH...")
        # tooltip

        self.marketCodeLine = QLineEdit()
        # the market code entry
        self.marketCodeLine.setMaximumWidth(40)
        # sets max width to avoid it pushing everything insanely far
        self.marketCodeLine.setText(f"{self.loadedConfig.get("marketCode", "")}")
        # sets the text to match the config

        self.optionLayout.addWidget(self.marketCodeLabel, 7, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.marketCodeLine, 7, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Console Clock Style ###

        self.clockStyleOptions = ["System Time", "Uptime", "Off"]
        # stores all the clock style options in a list
        self.loadedClockStyle = self.loadedConfig.get("clockStyle", "System Time")
        # gets the loaded clock style from config
        self.clockStyleOptions.remove(self.loadedClockStyle)
        # removes the loaded clock style from the list

        self.clockStyleLabel = QLabel("Clock Style")
        # the clock style label
        self.clockStyleLabel.setToolTip("The clock style to use in the program output")
        # tooltip

        self.clockStyleDropdown = QComboBox()
        # the clock style selection menu
        self.clockStyleDropdown.addItem(f"{self.loadedClockStyle}")
        self.clockStyleDropdown.addItem(f"{self.clockStyleOptions[0]}")
        self.clockStyleDropdown.addItem(f"{self.clockStyleOptions[1]}")
        # adds the selections
        self.clockStyleDropdown.setMinimumWidth(100)
        # sets width
        
        self.optionLayout.addWidget(self.clockStyleLabel, 8, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.clockStyleDropdown, 8, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Server Hosting ###

        self.enableFlaskLabel = QLabel("Enable Data Hosting")
        # label for data hosting
        self.enableFlaskLabel.setToolTip("Enable sharing DSI data to local network or device\nUseful if running both DSI and SBO on the same network/device")
        # tooltip

        self.enableFlaskCheck = QCheckBox()
        self.enableFlaskCheck.setChecked(self.loadedConfig.get("hostData", True))
        # sets the check state based on the config

        self.optionLayout.addWidget(self.enableFlaskLabel, 9, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.enableFlaskCheck, 9, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout

    ### Address Type ###

        self.addressTypeLabel = QLabel("Address Type")
        # label for the refresh timer
        self.addressTypeLabel.setToolTip("What network address type to use\nDevice = 127.0.0.1 (only accessible on-device)\nLocal = 0.0.0.0 (accessible to any device across the same network)\nIf you want to display the overlay on the same device as SBO, keep this on 'Device'\nIf you want to display the overlay on a different device on the same network, use 'Local'")
        # tooltip

        self.addressTypeOptions = ["Device", "Local"]
        # the options available for address type
        self.selectedAddressType = self.loadedConfig.get("addressType", "Device")
        # loads the selected one from config (defaults to Device)
        self.addressTypeOptions.remove(self.selectedAddressType)
        # removes the selected one from the list (leaves only one option)
        
        self.addressTypeDropdown = QComboBox()
        # the dropdown menu for address type
        self.addressTypeDropdown.addItem(self.selectedAddressType)
        self.addressTypeDropdown.addItem(self.addressTypeOptions[0])
        # adds the available options (selected first to make it default)

        self.optionLayout.addWidget(self.addressTypeLabel, 10, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.addressTypeDropdown, 10, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Auto-Save Timer ###

        self.autoSaveTimerLabel = QLabel("Auto-Save Time")
        # label for the auto-save
        self.autoSaveTimerLabel.setToolTip("How often to save the DSI stats, unmapped URIs, blacklist and favorites to disk\n0-24 (hours) accepted, in integers\n0 disables auto-saving (only saves when manually exiting via Exit button)")
        # tooltip

        self.autoSaveTimerLine = QLineEdit()
        # the
        self.autoSaveTimerLine.setMaximumWidth(40)
        # sets max width to avoid it pushing everything insanely far
        self.autoSaveTimerLine.setText(f"{self.loadedConfig.get("autoSaveTimer", 2)}")
        # sets the text to match the config
        self.autoSaveTimerLine.setValidator(self.hourValidator)
        # sets the hour validator (only accepts 0-99 (gets trimmed to 24 at save))

        self.optionLayout.addWidget(self.autoSaveTimerLabel, 11, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.autoSaveTimerLine, 11, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Auto-Restart ###

        self.autoRestartLabel = QLabel("Restart Automatically")
        # label for the automatic restarting
        self.autoRestartLabel.setToolTip("Whether to enable automatic internal restarting\nThis only acts when Spotify API is the reason for the shut down in the first place\nWaits 30 minutes before automatically restarting to allow potential Spotify outage to pass")
        # tooltip

        self.autoRestartCheck = QCheckBox()
        # checkbox for the automatic restart
        self.autoRestartCheck.setChecked(self.loadedConfig.get("autoRestart", True))
        # sets the check state based on the config

        self.optionLayout.addWidget(self.autoRestartLabel, 12, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.autoRestartCheck, 12, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Save Positional Data ###

        self.savePosDataLabel = QLabel("Save Window Coordinates")
        # label for the positional saving
        self.savePosDataLabel.setToolTip("Whether to enable automatic position and window size saving at exit every time\nThe window is moved and sized at launch to these numbers, this just manages the storing aspect")
        # tooltip
        
        self.savePosDataCheck = QCheckBox()
        # checkbox for the positional saving
        self.savePosDataCheck.setChecked(self.loadedConfig.get("savePosData", True))
        # sets the check state based on the config

        self.optionLayout.addWidget(self.savePosDataLabel, 13, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.savePosDataCheck, 13, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Buttons ###

        self.buttonLayout = QGridLayout()
        # makes a button layout
        self.buttonLayout.setVerticalSpacing(15)
        # sets spacing

        self.mainLayout.addLayout(self.buttonLayout, 2, 0)
        # adds the layout to main (row 2, under the options)

        self.saveAndCloseButton = QPushButton()
        # a button to close and start DSI
        self.saveAndCloseButton.setText("Save and close")
        # sets text
        self.saveAndCloseButton.setToolTip("Closes this configuration window and continues DSI function")
        # tooltip
        self.saveAndCloseButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.firstTimeButton = QPushButton()
        # a button to open the first time prompt window
        self.firstTimeButton.setText("Help")
        # sets text
        self.firstTimeButton.setToolTip("Opens the help window")
        # tooltip
        self.firstTimeButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.buttonLayout.addWidget(self.saveAndCloseButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.addWidget(self.firstTimeButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all to the layout, vertically aligned

        self.saveAndCloseButton.clicked.connect(self.writeConfig)
        # connects the DSI start button to the config write + exit
        self.firstTimeButton.clicked.connect(self.firstTimePrompt)
        # connects the first time button to the prompt

    ### Central Widget ###

        self.setCentralWidget(self.mainWidget)
        # sets central widget

### First Time Prompt ###

        if self.firstTime:
            # if the first time flag is enabled
            QTimer.singleShot(0, self.firstTimePrompt)
            # runs the first time prompt window (after the UI is done loading)

    def firstTimePrompt(self):
        """Function that runs the first time prompt message box"""

        self.ftPrompt = QMessageBox()
        # creates a prompt for first time users
        self.ftPrompt.setWindowTitle("DSI Helper")
        # window title
        self.ftPrompt.setWindowIcon(QIcon(self.mainIcon))
        # icon
        self.ftPrompt.setText(
            "Hello and welcome to the DSI Configurator!\n\n"
            "This is the first step, and this handles all the DSI functions\n"
            "Options selected here change how the program runs\n"
            "If you need any more information about an option, try hovering over it :)\n\n"
            "To configure the look of your Discord Activity, press the 'Configure DSI Details' button\n\n"
            "If you've installed DSI as an addon to SHA, there is a button inside the DSI Customisation Configuration window to tweak the look of SHA details, too\n\n"
            "Any questions, concerns, bugs, improvements, ideas, etc. can be sent via GitHub or on Discord (LilPiffer)\n\n"
            "I hope you enjoy DSI and thank you for installing it <3"
            )
        # the window text

        self.closeft = self.ftPrompt.exec()
        # close first time prompt button

        if self.closeft == QMessageBox.StandardButton.Ok:
        # if everything is ok
            None
            # closes

### Config Write ###

    def writeConfig(self):
        """Function to write the config json file (and exit)"""

        refreshTime = self.refreshTimeLine.text()
        # grabs the text from the refresh time edit line

        try:
        # tries to
            refreshTime = float(refreshTime)
            # turn the time into a float
        except:
        # if it can't (not an int/float)
            refreshTime = 10.0
            # sets to default

        if refreshTime < 3:
        # if the time is set to less than 3 seconds (will result in API rate limits)
            refreshTime = 3.0
            # caps at the lowest allowed time (1x/3s)

        consoleLength = self.consoleLengthLine.text()
        # grabs the text from the console length edit line

        try:
        # tries to
            consoleLength = int(consoleLength)
            # turns it into integer
        except:
        # if it can't
            consoleLength = 25
            # sets to default
        
        if consoleLength < 5:
        # if the console length is lower than 5
            consoleLength = 5
            # sets to minimum of 5
        elif consoleLength > 250:
        # if the console length is higher than 250 (performance concern)
            consoleLength = 250
            # caps at 250

        autoSaveTime = self.autoSaveTimerLine.text()
        # grabs the text from the auto-save interval edit line

        try:
        # tries to
            autoSaveTime = int(autoSaveTime)
            # turns it into integer
        except:
        # if it can't
            autoSaveTime = 2
            # sets to default

        if autoSaveTime < 0:
        # if the timer is somehow negative
            autoSaveTime = 0
            # sets to 0 (disabled)
        elif autoSaveTime > 24:
        # if the timer is more than 24 hours
            autoSaveTime = 24
            # caps at 24

        configuration = {
            "disableCfgWin": self.disableCfgWinCheck.isChecked(),
            "refreshTime": refreshTime,
            "enableURI": self.enableURICheck.isChecked(),
            "printUpdates": self.printUpdatesCheck.isChecked(),
            "printErrors": self.printErrorsCheck.isChecked(),
            "consoleLength": consoleLength,
            "clockStyle": self.clockStyleDropdown.currentText(),
            "marketCode": self.marketCodeLine.text(),
            "hostData": self.enableFlaskCheck.isChecked(),
            "addressType": self.addressTypeDropdown.currentText(),
            "autoSaveTimer": autoSaveTime,
            "autoRestart": self.autoRestartCheck.isChecked(),
            "savePosData": self.savePosDataCheck.isChecked(),
            "DSIwidth": self.loadedConfig.get("DSIwidth", self.mainWinX),
            "DSIheight": self.loadedConfig.get("DSIheight", self.mainWinY),
            "DSIxPos": self.loadedConfig.get("DSIxPos", self.mainWinPosX),
            "DSIyPos": self.loadedConfig.get("DSIyPos", self.mainWinPosY)
        }
        # forms a configuration based on the states of each of the fields

        with open(self.configPath, "w", encoding="utf-8") as cfg:
        # opens the config file
            json.dump(configuration, cfg, indent=3)
            # dumps everything in

        self.close()
        # closes the whole process


### Starter ###


if __name__ == "__main__":
# runs at start

    app = QApplication(sys.argv)
    # creates a Qt Application

    FuncCfgWindow = functionConfigWindow()
    # instantiates the window class
    FuncCfgWindow.show()
    # displays the window

    sys.exit(app.exec())
    # waits for the app to be done, then exits
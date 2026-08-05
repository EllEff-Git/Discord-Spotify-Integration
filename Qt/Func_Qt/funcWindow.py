from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required imports to manage the PyQt window
import json, os, sys, asyncio
# Required for config management



class Ui_FuncWindow(object):
    """The window class"""
    def setupUi(self, FuncWindow):
    # setup (sorry if the docs are a bit weird, this was made with the Qt Creator, I wrote docs after <3)
        if not FuncWindow.objectName():
        # checks for a name 
            FuncWindow.setObjectName(u"FuncWindow")
            # sets the name
        FuncWindow.setMinimumSize(925, 350)
        # sets the window size 
        self.window = FuncWindow
        # stores a reference in self to the actual window (so that it can be closed later)

        self.main = QWidget(FuncWindow)
        # makes a QWidget out of the main window
        self.main.setObjectName(u"main")
        # sets the object name

        if getattr(sys, "frozen", False):
        # since the program bundled with pyInstaller, it's "frozen"
            self.cwd = os.path.dirname(sys.executable)
            self.mainIcon = os.path.join(sys._MEIPASS, "dsiIcon.png")
            # reassigns the path variables accordingly
        else:
        # if somehow not in a bundled (frozen) state
            self.cwd = os.path.dirname(__file__)
            self.mainIcon = os.path.join(self.cwd, "icons", "dist", "dsiIcon.png")
            # reassigns the path variables accordingly

        self.mainFolder = os.path.join(self.cwd, "..", "..")
        # stores the "main" folder (DSI, which is 2 folders up)
        self.configPath = os.path.join(self.mainFolder, "Data", "functionConfig.json")
        # stores the config file's path
        self.dsiPath = os.path.join(self.mainFolder, "Qt", "DSI_Qt", "dsiWindow.exe")
        # stores the DSI configuration window path

        self.window.setWindowIcon(QIcon(self.mainIcon))
        # the window icon

        self.window.setWindowTitle("DSI Functionality Configuration")
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
                    "clockStyle": "Uptime",
                    "enableURI": True,
                    "printUpdates": True,
                    "printErrors": True,
                    "consoleLength": 25,
                    "marketCode": "",
                    "hostData": True
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

        self.centralWidget = QWidget(FuncWindow)
        # the main, central widget
        self.centralWidget.setObjectName("centralWidget")
        # sets name



    ### Main Layout ###

        self.mainLayout = QGridLayout(self.centralWidget)
        # sets the main layout to use a grid of the central
        self.mainLayout.setObjectName("mainLayout")
        # sets name
        self.mainLayout.setContentsMargins(25, 25, 25, 25)
        # sets margins of 25px 
        self.mainLayout.setVerticalSpacing(25)
        # sets vertical spacing

    ### Option Layout ###

        self.optionLayout = QGridLayout()
        # adds a grid layout for the options
        self.optionLayout.setObjectName("optionLayout")
        # sets name
        self.optionLayout.setContentsMargins(25, 25, 25, 25)
        # sets margins of 25px
        self.optionLayout.setVerticalSpacing(15)
        # sets vertical spacing
        self.optionLayout.setHorizontalSpacing(10)
        # sets horizontal spacing between elements

        self.optionLayout.setColumnStretch(0, 0)
        self.optionLayout.setColumnStretch(1, 0)
        # disables columns stretching automatically

        self.mainLayout.addLayout(self.optionLayout, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # sets the option layout into the main



    ### Enable URI ###

        self.enableURILabel = QLabel("Enable URI")
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

        self.refreshTimeLabel = QLabel("Refresh time")
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

        self.printUpdatesLabel = QLabel("Print updates")
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

        self.printErrorsLabel = QLabel("Print errors")
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

        self.disableCfgWinLabel = QLabel("Disable config window")
        # label for config window disabling
        self.disableCfgWinLabel.setToolTip("Skip opening the configuration window(s)")
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
        self.consoleLengthLabel.setToolTip("How many lines of the program status are stored\nDefault: 25, minimum: 5")
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
        self.loadedClockStyle = self.loadedConfig.get("clockStyle", "Uptime")
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

        self.enableFlaskHost = QLabel("Enable data hosting")
        # label for data hosting
        self.enableFlaskHost.setToolTip("Enable a localhost server that hosts parsed data\n(Useful if running both DSI and SBO)")
        # tooltip

        self.enableFlaskCheck = QCheckBox()
        self.enableFlaskCheck.setChecked(self.loadedConfig.get("hostData", True))
        # sets the check state based on the config

        self.optionLayout.addWidget(self.enableFlaskHost, 9, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.enableFlaskCheck, 9, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout



    ### Buttons ###

        self.buttonLayout = QGridLayout()
        # makes a button layout
        self.buttonLayout.setVerticalSpacing(15)
        # sets spacing

        self.mainLayout.addLayout(self.buttonLayout, 2, 0)
        # adds the layout to main (row 2, under the options)

        self.dsiConfigButton = QPushButton()
        # a button to run the DSI config
        self.dsiConfigButton.setText("Configure DSI Details")
        # sets text
        self.dsiConfigButton.setToolTip("Opens a configuration window to change DSI details")
        # tooltip
        self.dsiConfigButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.startDsiButton = QPushButton()
        # a button to close and start DSI
        self.startDsiButton.setText("Start DSI\n"
            "Ensure you press this to save the config!")
        # sets text
        self.startDsiButton.setToolTip("Closes this configuration window and continues DSI function")
        # tooltip
        self.startDsiButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.firstTimeButton = QPushButton()
        # a button to open the first time prompt window
        self.firstTimeButton.setText("Help Window")
        # sets text
        self.firstTimeButton.setToolTip("Opens the help window")
        # tooltip
        self.firstTimeButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.buttonLayout.addWidget(self.dsiConfigButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.addWidget(self.startDsiButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.addWidget(self.firstTimeButton, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all to the layout, vertically aligned

        self.dsiConfigButton.clicked.connect(self.runDSIwindow)
        # connects the DSI config button to the async runner
        self.startDsiButton.clicked.connect(self.writeConfig)
        # connects the DSI start button to the config write + exit
        self.firstTimeButton.clicked.connect(self.firstTimePrompt)
        # connects the first time button to the prompt

    ### Central Widget ###

        FuncWindow.setCentralWidget(self.centralWidget)
        # sets central widget

### First Time Prompt ###

        if self.firstTime:
            # if the first time flag is enabled
            self.firstTimePrompt()
            # runs the first time prompt window

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

### DSI Window Run ###

    def runDSIwindow(self):
        """Function to run the DSI configuration window"""
        async def asyncRunner():
            # has an integrated async function so it can run asynchronously from the main process
            dsiConfig = await asyncio.create_subprocess_exec(self.dsiPath)
            # runs the DSI configurator as a subprocess of this subprocess
        asyncio.run(asyncRunner())
        # runs the async runner

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
            # sets to safe 10 second float

        consoleLength = self.consoleLengthLine.text()
        # grabs the text from the console length edit line

        if not type(consoleLength) == int:
        # if the consoleLength isn't an integer
            try:
            # tries to convert
                consoleLength = int(consoleLength)
                # turns it into integer (if it's float)
            except:
            # if it can't
                consoleLength = 25
                # sets safe number
        
        if consoleLength < 5:
        # if the console length is set to lower than 5
            consoleLength = 5
            # sets to minimum of 5

        configuration = {
            "disableCfgWin": self.disableCfgWinCheck.isChecked(),
            "refreshTime": refreshTime,
            "enableURI": self.enableURICheck.isChecked(),
            "printUpdates": self.printUpdatesCheck.isChecked(),
            "printErrors": self.printErrorsCheck.isChecked(),
            "consoleLength": consoleLength,
            "clockStyle": self.clockStyleDropdown.currentText(),
            "marketCode": self.marketCodeLine.text(),
        }
        # forms a configuration based on the states of each of the fields

        with open(self.configPath, "w", encoding="utf-8") as cfg:
        # opens the config file
            json.dump(configuration, cfg, indent=3)
            # dumps everything in

        self.window.close()
        # closes the whole process


### Starter ###


if __name__ == "__main__":
# runs at start

    app = QApplication(sys.argv)
    # creates a Qt Application

    FuncCfgWindow = QMainWindow()
    # creates a window
    ui = Ui_FuncWindow()
    # takes the UI class
    ui.setupUi(FuncCfgWindow)
    # "populates" the UI class

    FuncCfgWindow.show()
    # displays the window

    sys.exit(app.exec())
    # waits for the app to be done, then exits
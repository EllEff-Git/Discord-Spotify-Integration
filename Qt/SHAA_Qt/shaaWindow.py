from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
# Required imports to manage the PyQt window
import json, os, sys
# Required for config management

class Ui_SHAAWindow(object):
    def setupUi(self, SHAAWindow):
    # setup (sorry if the docs are a bit weird, this was made with the Qt Creator, I wrote docs after <3)
        if not SHAAWindow.objectName():
            SHAAWindow.setObjectName(u"SHAAWindow")
        SHAAWindow.setFixedSize(1455, 860)
        self.window = SHAAWindow
        # stores a reference in self to the actual window (so that it can be closed later)

        if getattr(sys, 'frozen', False):
            self.cwd = os.path.dirname(sys.executable)
        else:
            self.cwd = os.path.dirname(os.path.abspath(__file__))
        # stores the "current working directory" (should be the Qt/SHAA_Qt/ folder)
        self.mainFolder = os.path.join(self.cwd, "..", "..")
        # stores the "main" folder (DSI, which is 2 folders up)
        self.configPath = os.path.join(self.mainFolder, "Data", "shaaConfig.json")
        # stores the config file's path

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
                    "songInfoDetails": "Hours",
                    "songInfoDetailsText": "",
                    "songInfoFormatPlays": "plays",
                    "songInfoFormatSpacer": "※",
                    "songInfoFormatMins": "minutes",
                    "songInfoDetailsTextFirst": True,
                    "songInfoDetailsText": "Total Hours",
                    "songInfoDetailsSpacer": ":",
                    "songInfoDetailsDoubleSpace": False,
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
        self.loadedField1Option = self.loadedConfig["songInfoField1"]
        # gets the loaded option from file
        self.songInfoField1Options.remove(self.loadedField1Option)
        # removes the current option

        self.songInfoField2Options = ["Track (Minutes)", "Total (Minutes)", "Track (Hours)", "Total (Hours)", "Track (Seconds)", "Total (Seconds)"]
        # stores all the options possible for field 2
        self.loadedField2Option = self.loadedConfig["songInfoField2"]
        # gets the loaded option from file
        self.poppedField2 = self.songInfoField2Options.pop(self.loadedField2Option)
        # pops the index (0-5) and stores it

        self.songInfoDetailOptions = ["Hours", "Minutes", "Seconds", "Cycle", "Volume", "Repeat", "Shuffle", "Custom"]
        # stores all the options possible for details field
        self.loadedDetailOption = self.loadedConfig["songInfoDetails"]
        # gets the loaded option from file
        self.songInfoDetailOptions.remove(self.loadedDetailOption)
        # removes the current options

        self.centralwidget = QWidget(SHAAWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 1450, 810))
        self.mainLayout = QGridLayout(self.gridLayoutWidget)
        self.mainLayout.setSpacing(10)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(20, 10, 20, 10)
        self.bottomLeftGrid = QVBoxLayout()
        self.bottomLeftGrid.setObjectName(u"bottomLeftGrid")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.bottomLeftGrid.addItem(self.verticalSpacer)

        self.closeAndSaveButton = QPushButton(self.gridLayoutWidget)
        self.closeAndSaveButton.setObjectName(u"pushButton")
        self.closeAndSaveButton.clicked.connect(self.writeConfig)

        self.bottomLeftGrid.addWidget(self.closeAndSaveButton)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.bottomLeftGrid.addItem(self.verticalSpacer_2)

        self.mainLayout.addLayout(self.bottomLeftGrid, 1, 1, 1, 1)

        self.topMidGrid = QGridLayout()
        self.topMidGrid.setObjectName(u"topMidGrid")
        self.topMidGrid.setHorizontalSpacing(5)
        self.topMidGrid.setVerticalSpacing(10)
        self.topMidGrid.setContentsMargins(10, 10, 10, 10)
        self.songInfoFormatPlaysTooltip = QLabel(self.gridLayoutWidget)
        self.songInfoFormatPlaysTooltip.setObjectName(u"songInfoFormatPlaysTooltip")

        self.topMidGrid.addWidget(self.songInfoFormatPlaysTooltip, 2, 0, 1, 1)

        self.songInfoFormatMinsHeader = QLabel(self.gridLayoutWidget)
        self.songInfoFormatMinsHeader.setObjectName(u"songInfoFormatMinsHeader")

        self.topMidGrid.addWidget(self.songInfoFormatMinsHeader, 10, 0, 1, 1)

        self.songInfoSpacerText = QLineEdit(self.gridLayoutWidget)
        self.songInfoSpacerText.setObjectName(u"songInfoSpacerText")

        self.topMidGrid.addWidget(self.songInfoSpacerText, 5, 0, 1, 1)

        self.songInfoFormatMinsTooltip = QLabel(self.gridLayoutWidget)
        self.songInfoFormatMinsTooltip.setObjectName(u"songInfoFormatMinsTooltip")

        self.topMidGrid.addWidget(self.songInfoFormatMinsTooltip, 12, 0, 1, 1)

        self.songInfoFormatMinsText = QLineEdit(self.gridLayoutWidget)
        self.songInfoFormatMinsText.setObjectName(u"songInfoFormatMinsText")

        self.topMidGrid.addWidget(self.songInfoFormatMinsText, 11, 0, 1, 1)

        self.songInfoSpacerHeader = QLabel(self.gridLayoutWidget)
        self.songInfoSpacerHeader.setObjectName(u"songInfoSpacerHeader")

        self.topMidGrid.addWidget(self.songInfoSpacerHeader, 4, 0, 1, 1)

        self.songInfoFormatPlaysHeader = QLabel(self.gridLayoutWidget)
        self.songInfoFormatPlaysHeader.setObjectName(u"songInfoFormatPlaysHeader")

        self.topMidGrid.addWidget(self.songInfoFormatPlaysHeader, 0, 0, 1, 1)

        self.songInfoSpacerLine = QFrame(self.gridLayoutWidget)
        self.songInfoSpacerLine.setObjectName(u"songInfoSpacerLine")
        self.songInfoSpacerLine.setFrameShape(QFrame.Shape.HLine)
        self.songInfoSpacerLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.topMidGrid.addWidget(self.songInfoSpacerLine, 9, 0, 1, 1)

        self.songInfoSpacerTooltip = QLabel(self.gridLayoutWidget)
        self.songInfoSpacerTooltip.setObjectName(u"songInfoSpacerTooltip")

        self.topMidGrid.addWidget(self.songInfoSpacerTooltip, 6, 0, 1, 1)

        self.songInfoFormatPlaysLine = QFrame(self.gridLayoutWidget)
        self.songInfoFormatPlaysLine.setObjectName(u"songInfoFormatPlaysLine")
        self.songInfoFormatPlaysLine.setFrameShape(QFrame.Shape.HLine)
        self.songInfoFormatPlaysLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.topMidGrid.addWidget(self.songInfoFormatPlaysLine, 3, 0, 1, 1)

        self.songInfoFormatPlaysText = QLineEdit(self.gridLayoutWidget)
        self.songInfoFormatPlaysText.setObjectName(u"songInfoFormatPlaysText")

        self.topMidGrid.addWidget(self.songInfoFormatPlaysText, 1, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.topMidGrid.addItem(self.verticalSpacer_3, 13, 0, 1, 1)


        self.mainLayout.addLayout(self.topMidGrid, 0, 1, 1, 1)

        self.topLeftGrid = QGridLayout()
        self.topLeftGrid.setObjectName(u"topLeftGrid")
        self.topLeftGrid.setHorizontalSpacing(5)
        self.topLeftGrid.setVerticalSpacing(10)
        self.topLeftGrid.setContentsMargins(10, 10, 10, 10)
        self.shaaInfoDetailsHeader = QLabel(self.gridLayoutWidget)
        self.shaaInfoDetailsHeader.setObjectName(u"shaaInfoDetailsHeader")

        self.topLeftGrid.addWidget(self.shaaInfoDetailsHeader, 13, 0, 1, 1)

        self.shaaFallbackTooltip = QLabel(self.gridLayoutWidget)
        self.shaaFallbackTooltip.setObjectName(u"shaaFallbackTooltip")

        self.topLeftGrid.addWidget(self.shaaFallbackTooltip, 11, 0, 1, 1)

        self.songInfoField1Header = QLabel(self.gridLayoutWidget)
        self.songInfoField1Header.setObjectName(u"songInfoField1Header")

        self.topLeftGrid.addWidget(self.songInfoField1Header, 0, 0, 1, 1)

        self.shaaFallbackText = QLineEdit(self.gridLayoutWidget)
        self.shaaFallbackText.setObjectName(u"shaaFallbackText")
        self.shaaFallbackText.setText(self.loadedConfig["songInfoFallbackText"])
        # uses the config set text

        self.topLeftGrid.addWidget(self.shaaFallbackText, 10, 0, 1, 1)

        self.songInfoField1Tooltip = QLabel(self.gridLayoutWidget)
        self.songInfoField1Tooltip.setObjectName(u"songInfoField1Tooltip")

        self.topLeftGrid.addWidget(self.songInfoField1Tooltip, 2, 0, 1, 1)

        self.songInfoField1Line = QFrame(self.gridLayoutWidget)
        self.songInfoField1Line.setObjectName(u"songInfoField1Line")
        self.songInfoField1Line.setFrameShape(QFrame.Shape.HLine)
        self.songInfoField1Line.setFrameShadow(QFrame.Shadow.Sunken)

        self.topLeftGrid.addWidget(self.songInfoField1Line, 3, 0, 1, 1)

        self.shaaFallbackHeader = QLabel(self.gridLayoutWidget)
        self.shaaFallbackHeader.setObjectName(u"shaaFallbackHeader")

        self.topLeftGrid.addWidget(self.shaaFallbackHeader, 8, 0, 1, 1)

        self.shaaInfoDetailsCustomText = QLineEdit(self.gridLayoutWidget)
        self.shaaInfoDetailsCustomText.setObjectName(u"shaaInfoDetailsCustomText")

        self.topLeftGrid.addWidget(self.shaaInfoDetailsCustomText, 17, 0, 1, 1)

        self.songInfoField2Line = QFrame(self.gridLayoutWidget)
        self.songInfoField2Line.setObjectName(u"songInfoField2Line")
        self.songInfoField2Line.setFrameShape(QFrame.Shape.HLine)
        self.songInfoField2Line.setFrameShadow(QFrame.Shadow.Sunken)

        self.topLeftGrid.addWidget(self.songInfoField2Line, 7, 0, 1, 1)

        self.shaaInfoDetailsDropdown = QComboBox(self.gridLayoutWidget)
        self.shaaInfoDetailsDropdown.addItem("")
        self.shaaInfoDetailsDropdown.addItem("")
        self.shaaInfoDetailsDropdown.addItem("")
        self.shaaInfoDetailsDropdown.addItem("")
        self.shaaInfoDetailsDropdown.addItem("")
        self.shaaInfoDetailsDropdown.addItem("")
        self.shaaInfoDetailsDropdown.addItem("")
        self.shaaInfoDetailsDropdown.addItem("")
        self.shaaInfoDetailsDropdown.setObjectName(u"shaaInfoDetailsDropdown")

        self.topLeftGrid.addWidget(self.shaaInfoDetailsDropdown, 14, 0, 1, 1)

        self.shaaFallbackTotalCheck = QCheckBox(self.gridLayoutWidget)
        self.shaaFallbackTotalCheck.setObjectName(u"shaaFallbackTotalCheck")
        if self.loadedConfig["songInfoFallbackTotal"]:
        # if the loaded config has the fallback total set to True
            self.shaaFallbackTotalCheck.setChecked(True)
            # ticks the box automatically

        self.topLeftGrid.addWidget(self.shaaFallbackTotalCheck, 9, 0, 1, 1)

        self.songInfoField1Dropdown = QComboBox(self.gridLayoutWidget)
        self.songInfoField1Dropdown.addItem("")
        self.songInfoField1Dropdown.addItem("")
        self.songInfoField1Dropdown.setObjectName(u"songInfoField1Dropdown")

        self.topLeftGrid.addWidget(self.songInfoField1Dropdown, 1, 0, 1, 1)

        self.songInfoField2Header = QLabel(self.gridLayoutWidget)
        self.songInfoField2Header.setObjectName(u"songInfoField2Header")

        self.topLeftGrid.addWidget(self.songInfoField2Header, 4, 0, 1, 1)

        self.shaaInfoDetailsTooltip = QLabel(self.gridLayoutWidget)
        self.shaaInfoDetailsTooltip.setObjectName(u"shaaInfoDetailsTooltip")

        self.topLeftGrid.addWidget(self.shaaInfoDetailsTooltip, 15, 0, 1, 1)

        self.songInfoField2Tooltip = QLabel(self.gridLayoutWidget)
        self.songInfoField2Tooltip.setObjectName(u"songInfoField2Tooltip")

        self.topLeftGrid.addWidget(self.songInfoField2Tooltip, 6, 0, 1, 1)

        self.shaaFallbackLine = QFrame(self.gridLayoutWidget)
        self.shaaFallbackLine.setObjectName(u"shaaFallbackLine")
        self.shaaFallbackLine.setFrameShape(QFrame.Shape.HLine)
        self.shaaFallbackLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.topLeftGrid.addWidget(self.shaaFallbackLine, 12, 0, 1, 1)

        self.songInfoField2Dropdown = QComboBox(self.gridLayoutWidget)
        self.songInfoField2Dropdown.addItem("")
        self.songInfoField2Dropdown.addItem("")
        self.songInfoField2Dropdown.addItem("")
        self.songInfoField2Dropdown.addItem("")
        self.songInfoField2Dropdown.addItem("")
        self.songInfoField2Dropdown.addItem("")
        self.songInfoField2Dropdown.setObjectName(u"songInfoField2Dropdown")

        self.topLeftGrid.addWidget(self.songInfoField2Dropdown, 5, 0, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.topLeftGrid.addItem(self.verticalSpacer_4, 18, 0, 1, 1)


        self.mainLayout.addLayout(self.topLeftGrid, 0, 0, 1, 1)

        self.topRightGrid = QGridLayout()
        self.topRightGrid.setObjectName(u"topRightGrid")
        self.topRightGrid.setHorizontalSpacing(5)
        self.topRightGrid.setVerticalSpacing(10)
        self.topRightGrid.setContentsMargins(10, 10, 10, 10)
        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")

        self.topRightGrid.addWidget(self.label, 11, 0, 1, 1)

        self.songInfoFormatSpacerText = QLineEdit(self.gridLayoutWidget)
        self.songInfoFormatSpacerText.setObjectName(u"songInfoFormatSpacerText")

        self.topRightGrid.addWidget(self.songInfoFormatSpacerText, 8, 0, 1, 1)

        self.songInfoFormatDetailsOrderCheck = QCheckBox(self.gridLayoutWidget)
        self.songInfoFormatDetailsOrderCheck.setObjectName(u"songInfoFormatDetailsOrderCheck")
        if self.loadedConfig["songInfoDetailsTextFirst"]:
        # if the config option is enabled
            self.songInfoFormatDetailsOrderCheck.setChecked(True)
            # ticks the box automatically

        self.topRightGrid.addWidget(self.songInfoFormatDetailsOrderCheck, 1, 0, 1, 1)

        self.songInfoFormatSpacerHeader = QLabel(self.gridLayoutWidget)
        self.songInfoFormatSpacerHeader.setObjectName(u"songInfoFormatSpacerHeader")

        self.topRightGrid.addWidget(self.songInfoFormatSpacerHeader, 7, 0, 1, 1)

        self.doubleSpaceCheck = QCheckBox(self.gridLayoutWidget)
        self.doubleSpaceCheck.setObjectName(u"checkBox")
        if self.loadedConfig["songInfoDetailsDoubleSpace"]:
        # if the config option is enabled
            self.doubleSpaceCheck.setChecked(True)
            # ticks the box automatically

        self.topRightGrid.addWidget(self.doubleSpaceCheck, 12, 0, 1, 1)

        self.songInfoFormatSpacerTooltip = QLabel(self.gridLayoutWidget)
        self.songInfoFormatSpacerTooltip.setObjectName(u"songInfoFormatSpacerTooltip")

        self.topRightGrid.addWidget(self.songInfoFormatSpacerTooltip, 9, 0, 1, 1)

        self.songInfoFormatDetailsLine = QFrame(self.gridLayoutWidget)
        self.songInfoFormatDetailsLine.setObjectName(u"songInfoFormatDetailsLine")
        self.songInfoFormatDetailsLine.setFrameShape(QFrame.Shape.HLine)
        self.songInfoFormatDetailsLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.topRightGrid.addWidget(self.songInfoFormatDetailsLine, 6, 0, 1, 1)

        self.songInfoFormatDetailsHeader = QLabel(self.gridLayoutWidget)
        self.songInfoFormatDetailsHeader.setObjectName(u"songInfoFormatDetailsHeader")

        self.topRightGrid.addWidget(self.songInfoFormatDetailsHeader, 3, 0, 1, 1)

        self.songInfoFormatDetailsOrderLine = QFrame(self.gridLayoutWidget)
        self.songInfoFormatDetailsOrderLine.setObjectName(u"songInfoFormatDetailsOrderLine")
        self.songInfoFormatDetailsOrderLine.setFrameShape(QFrame.Shape.HLine)
        self.songInfoFormatDetailsOrderLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.topRightGrid.addWidget(self.songInfoFormatDetailsOrderLine, 2, 0, 1, 1)

        self.songInfoFormatDetailsOrderHeader = QLabel(self.gridLayoutWidget)
        self.songInfoFormatDetailsOrderHeader.setObjectName(u"songInfoFormatDetailsOrderHeader")

        self.topRightGrid.addWidget(self.songInfoFormatDetailsOrderHeader, 0, 0, 1, 1)

        self.songInfoFormatDetailsText = QLineEdit(self.gridLayoutWidget)
        self.songInfoFormatDetailsText.setObjectName(u"songInfoFormatDetailsText")

        self.topRightGrid.addWidget(self.songInfoFormatDetailsText, 4, 0, 1, 1)

        self.songInfoFormatDetailsTooltip = QLabel(self.gridLayoutWidget)
        self.songInfoFormatDetailsTooltip.setObjectName(u"songInfoFormatDetailsTooltip")

        self.topRightGrid.addWidget(self.songInfoFormatDetailsTooltip, 5, 0, 1, 1)

        self.songInfoFormatSpacerLine = QFrame(self.gridLayoutWidget)
        self.songInfoFormatSpacerLine.setObjectName(u"songInfoFormatSpacerLine")
        self.songInfoFormatSpacerLine.setFrameShape(QFrame.Shape.HLine)
        self.songInfoFormatSpacerLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.topRightGrid.addWidget(self.songInfoFormatSpacerLine, 10, 0, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.topRightGrid.addWidget(self.label_2, 13, 0, 1, 1)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.topRightGrid.addItem(self.verticalSpacer_5, 14, 0, 1, 1)


        self.mainLayout.addLayout(self.topRightGrid, 0, 3, 1, 1)

        self.bottomRightGrid = QGridLayout()
        self.bottomRightGrid.setObjectName(u"bottomRightGrid")
        self.bottomRightGrid.setHorizontalSpacing(5)
        self.bottomRightGrid.setVerticalSpacing(10)
        self.bottomRightGrid.setContentsMargins(10, 10, 10, 10)
        self.dsiShoutoutCheck = QCheckBox(self.gridLayoutWidget)
        self.dsiShoutoutCheck.setObjectName(u"dsiShoutoutCheck")
        if self.loadedConfig["dsiShoutout"]:
        # if the config option is enabled
            self.dsiShoutoutCheck.setChecked(True)
            # ticks the box automatically

        self.bottomRightGrid.addWidget(self.dsiShoutoutCheck, 1, 0, 1, 1)

        self.dsiShoutoutHeader = QLabel(self.gridLayoutWidget)
        self.dsiShoutoutHeader.setObjectName(u"dsiShoutoutHeader")

        self.bottomRightGrid.addWidget(self.dsiShoutoutHeader, 0, 0, 1, 1)

        self.dsiShoutoutTooltip = QLabel(self.gridLayoutWidget)
        self.dsiShoutoutTooltip.setObjectName(u"dsiShoutoutTooltip")

        self.bottomRightGrid.addWidget(self.dsiShoutoutTooltip, 2, 0, 1, 1)


        self.mainLayout.addLayout(self.bottomRightGrid, 1, 3, 1, 1)

        SHAAWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(SHAAWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1453, 21))
        SHAAWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(SHAAWindow)
        self.statusbar.setObjectName(u"statusbar")
        SHAAWindow.setStatusBar(self.statusbar)

        self.retranslateUi(SHAAWindow)

        QMetaObject.connectSlotsByName(SHAAWindow)
    # setupUi

    def retranslateUi(self, SHAAWindow):
        """Function to 'translate' the strings, I suppose (auto-generated by Qt Creator)"""
        SHAAWindow.setWindowTitle(QCoreApplication.translate("SHAA Configuration", u"SHAA Configuration", None))
        # the title of the whole window

        self.closeAndSaveButton.setText(QCoreApplication.translate("SHAAWindow", u"\n""Close SHAA Configurator\n"
            "(Please press this to save the configuration)\n", None))
        self.songInfoFormatPlaysTooltip.setText(QCoreApplication.translate("SHAAWindow", u"Ex. '2,345 plays' or '2,345 listens' or '2,345 repetitions' or '234,567 total plays'...", None))
        self.songInfoFormatMinsHeader.setText(QCoreApplication.translate("SHAAWindow", u"The text to display after the number in the first field", None))
        self.songInfoSpacerText.setText(QCoreApplication.translate("SHAAWindow", f"{self.loadedConfig["songInfoFormatSpacer"]}", None))
        self.songInfoFormatMinsTooltip.setText(QCoreApplication.translate("SHAAWindow", u"Ex. '6,789 minutes' or '678,910 total minutes'...", None))
        self.songInfoFormatMinsText.setText(QCoreApplication.translate("SHAAWindow", f"{self.loadedConfig["songInfoFormatMins"]}", None))
        self.songInfoSpacerHeader.setText(QCoreApplication.translate("SHAAWindow", u"The spacer to place between the first and second field", None))
        self.songInfoFormatPlaysHeader.setText(QCoreApplication.translate("SHAAWindow", u"The text to display after the number in the first field", None))
        self.songInfoSpacerTooltip.setText(QCoreApplication.translate("SHAAWindow", u"Ex. '2,345 plays \u203b 6,789 minutes' or '2,345 plays x 6,789 minutes'...", None))
        self.songInfoFormatPlaysText.setText(QCoreApplication.translate("SHAAWindow", f"{self.loadedConfig["songInfoFormatPlays"]}", None))
        self.shaaInfoDetailsHeader.setText(QCoreApplication.translate("SHAAWindow", u"The type of data to display in the details field", None))
        self.shaaFallbackTooltip.setText(QCoreApplication.translate("SHAAWindow", u"If the Total checkbox is checked, uses total counts/times\n"
            "A custom string can be entered instead, if preferred, in the text field", None))
        self.songInfoField1Header.setText(QCoreApplication.translate("SHAAWindow", u"The type of data to display in the first field (playcount)", None))
        self.songInfoField1Tooltip.setText(QCoreApplication.translate("SHAAWindow", u"<html><head/><body><p>Track displays per-track data (ex. 2,345 plays)<br>Total displays total account data (ex. 234,567 plays)</p></body></html>", None))
        self.shaaFallbackHeader.setText(QCoreApplication.translate("SHAAWindow", u"The type of data to fallback on, if the current song isn't found in the CSV", None))
        self.shaaInfoDetailsDropdown.setItemText(0, QCoreApplication.translate("SHAAWindow", f"{self.loadedDetailOption}", None))
        # uses the loaded config option
        self.shaaInfoDetailsDropdown.setItemText(1, QCoreApplication.translate("SHAAWindow", f"{self.songInfoDetailOptions[0]}", None))
        self.shaaInfoDetailsDropdown.setItemText(2, QCoreApplication.translate("SHAAWindow", f"{self.songInfoDetailOptions[1]}", None))
        self.shaaInfoDetailsDropdown.setItemText(3, QCoreApplication.translate("SHAAWindow", f"{self.songInfoDetailOptions[2]}", None))
        self.shaaInfoDetailsDropdown.setItemText(4, QCoreApplication.translate("SHAAWindow", f"{self.songInfoDetailOptions[3]}", None))
        self.shaaInfoDetailsDropdown.setItemText(5, QCoreApplication.translate("SHAAWindow", f"{self.songInfoDetailOptions[4]}", None))
        self.shaaInfoDetailsDropdown.setItemText(6, QCoreApplication.translate("SHAAWindow", f"{self.songInfoDetailOptions[5]}", None))
        self.shaaInfoDetailsDropdown.setItemText(7, QCoreApplication.translate("SHAAWindow", f"{self.songInfoDetailOptions[6]}", None))
        # uses the list remainders

        self.shaaFallbackTotalCheck.setText(QCoreApplication.translate("SHAAWindow", u"Total", None))

        self.songInfoField1Dropdown.setItemText(0, QCoreApplication.translate("SHAAWindow", f"{self.loadedField1Option}", None))
        # uses the loaded config option for the field1
        self.songInfoField1Dropdown.setItemText(1, QCoreApplication.translate("SHAAWindow", f"{self.songInfoField1Options[0]}", None))
        # uses the only other option left

        self.songInfoField2Header.setText(QCoreApplication.translate("SHAAWindow", u"The type of data to display in the second field (playtime)", None))
        self.shaaInfoDetailsTooltip.setText(QCoreApplication.translate("SHAAWindow", u"Hours takes the total account hours\n"
            "Minutes takes the total account minutes\n"
            "Seconds takes the total account seconds\n"
            "Cycle goes between the hours, minutes and seconds every song\n"
            "Volume tries to take the current playing Spotify volume\n"
            "Repeat takes the current repeat state\n"
            "Shuffle takes the current shuffle state\n"
            "Custom enables the custom text below", None))
        self.songInfoField2Tooltip.setText(QCoreApplication.translate("SHAAWindow", u"Track displays per-track data (ex. 6,789 minutes)\n"
            "Total displays total account data (ex. 678,910 minutes)", None))
        
        self.songInfoField2Dropdown.setItemText(0, QCoreApplication.translate("SHAAWindow", f"{self.poppedField2}", None))
        # uses the popped field as the first one
        self.songInfoField2Dropdown.setItemText(1, QCoreApplication.translate("SHAAWindow", f"{self.songInfoField2Options[0]}", None))
        self.songInfoField2Dropdown.setItemText(2, QCoreApplication.translate("SHAAWindow", f"{self.songInfoField2Options[1]}", None))
        self.songInfoField2Dropdown.setItemText(3, QCoreApplication.translate("SHAAWindow", f"{self.songInfoField2Options[2]}", None))
        self.songInfoField2Dropdown.setItemText(4, QCoreApplication.translate("SHAAWindow", f"{self.songInfoField2Options[3]}", None))
        self.songInfoField2Dropdown.setItemText(5, QCoreApplication.translate("SHAAWindow", f"{self.songInfoField2Options[4]}", None))
        # uses the option list indices

        self.label.setText(QCoreApplication.translate("SHAAWindow", u"Whether to add a space on either side of the spacer in the details field", None))
        self.songInfoFormatSpacerText.setText(QCoreApplication.translate("SHAAWindow", f"{self.loadedConfig["songInfoDetailsSpacer"]}", None))
        self.songInfoFormatDetailsOrderCheck.setText(QCoreApplication.translate("SHAAWindow", u"Text First", None))
        self.songInfoFormatSpacerHeader.setText(QCoreApplication.translate("SHAAWindow", u"The spacer to use between the number and text in the details field", None))
        self.doubleSpaceCheck.setText(QCoreApplication.translate("SHAAWindow", u"Add both spaces", None))
        self.songInfoFormatSpacerTooltip.setText(QCoreApplication.translate("SHAAWindow", u"Ex. 'Total Hours: 11,123' or 'Total Hours - 11,123' or 'Total Hours = 11,123'...", None))
        self.songInfoFormatDetailsHeader.setText(QCoreApplication.translate("SHAAWindow", u"The text to display before or after the number in the details field", None))
        self.songInfoFormatDetailsOrderHeader.setText(QCoreApplication.translate("SHAAWindow", u"Whether to place the text before the number in the details field", None))
        self.songInfoFormatDetailsText.setText(QCoreApplication.translate("SHAAWindow", f"{self.loadedConfig["songInfoDetailsText"]}", None))
        self.songInfoFormatDetailsTooltip.setText(QCoreApplication.translate("SHAAWindow", u"Ex. 'Total Hours: 11,123 ' or 'Hours: 11,123' or 'Hours listened; 11,123'... (text first)\n"
            "Ex. '11,123 Total Hours' or '11,123 hours' or '11,123 hours listened'... (number first)", None))
        self.label_2.setText(QCoreApplication.translate("SHAAWindow", u"Ex. 'Total Hours: 11,123' or 'Total Hours : 11,123'...", None))
        self.dsiShoutoutCheck.setText(QCoreApplication.translate("SHAAWindow", u"Enable Tag", None))
        self.dsiShoutoutHeader.setText(QCoreApplication.translate("SHAAWindow", u"Whether to enable a DSI shoutout tag :)", None))
        self.dsiShoutoutTooltip.setText(QCoreApplication.translate("SHAAWindow", u"Looks like \"// Data by DSI\", is added to the end of the detail field\n"
            "Ex. \"Total Hours: 11,123 // Data by DSI\"", None))
    # retranslateUi

    def writeConfig(self):
        """Function to write the config json file (and exit)"""
        configuration = {
            "songInfoField1": self.songInfoField1Dropdown.currentText(),
            "songInfoField2": self.songInfoField2Dropdown.currentIndex(),
            "songInfoFallbackTotal": self.shaaFallbackTotalCheck.isChecked(),
            "songInfoFallbackText": self.shaaFallbackText.text(),
            "songInfoDetails": self.shaaInfoDetailsDropdown.currentText(),
            "songInfoDetailsText": self.shaaInfoDetailsCustomText.text(),
            "songInfoFormatPlays": self.songInfoFormatPlaysText.text(),
            "songInfoFormatSpacer": self.songInfoSpacerText.text(),
            "songInfoFormatMins": self.songInfoFormatMinsText.text(),
            "songInfoDetailsTextFirst": self.songInfoFormatDetailsOrderCheck.isChecked(),
            "songInfoDetailsText": self.songInfoFormatDetailsText.text(),
            "songInfoDetailsSpacer": self.songInfoFormatSpacerText.text(),
            "songInfoDetailsDoubleSpace": self.doubleSpaceCheck.isChecked(),
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
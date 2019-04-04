#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import os
import logging
import traceback
import uuid
import requests
import queue
import time

sys.path.append('./lib')
sys.path.append('./res')
sys.path.append('./ui')

import res.resources
from ui.mainUI import Ui_stackedUI
from logging import handlers
from PyQt5 import QtCore, QtGui, QtWidgets
from lib.outlook_assistant import poll_availability, make_a_reservation, clear_reservations
from lib.access_tokens import uaid

class QtWidgetLogger(logging.Handler):
    """Custom Logging handler that is able to output stdout to a given QWidget for ex. QTextView"""
    def __init__(self):
        logging.Handler.__init__(self)
        self.outputWidget = None

    def emit(self, record):
        record = self.format(record)
        if record and self.outputWidget is not None:
            if len(record) == 1 and ord(str(record)) == 10:
                return
            else:
                cursor = self.outputWidget.textCursor()
                cursor.movePosition(QtGui.QTextCursor.End)
                cursor.insertText(record + "\r\n")
                self.outputWidget.setTextCursor(cursor)
                self.outputWidget.ensureCursorVisible()

# change workdir to scripts location
os.chdir(os.path.dirname(r'{0}'.format(sys.path[0])))

if not os.path.exists(sys.path[0] + "/logs/"):
    os.makedirs(sys.path[0] + "/logs/")

# setup logging
logger = logging.getLogger('Naurunappula')
logger.setLevel(logging.DEBUG)

fh = handlers.TimedRotatingFileHandler(sys.path[0] + '/logs/debug.log', when="d", interval=1, backupCount=7)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

qh = QtWidgetLogger()
qh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)
logger.addHandler(qh)

data_container = queue.Queue() # used by GAThread

# Subclass QThread to send analytics data to Google Analytics
class GAThread(QtCore.QThread):
    def __init__(self, uaid, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.uaid = uaid
        self.endpoint = 'https://www.google-analytics.com/collect'

    def run(self):
        """Send events to Google Analytics platform"""
        while True:
            try:
                data = data_container.get_nowait()
                if data is not None:
                    payload = {'v':'1',
                               'tid': self.uaid,         # tracking ID
                               'cid': data["uuid"],      # device uuid
                               't': 'event',             # hit type
                               'ec': data["category"],   # event category
                               'ea': data["action"],     # event action
                               'el': data["label"],      # event label
                               'ev': data["value"]       # event value
                        }
                    try:
                        logger.debug("Sending data to Google Analytics: {0}".format(data))
                        requests.post(url = self.endpoint, data = payload, headers = {'User-Agent': 'My User Agent 1.0'})
                    except:
                        logger.error("Failed to send data to Google Analytics. Trying again later.")
                data_container.task_done()
            except queue.Empty:
                pass
            finally:
                time.sleep(1)

# Subclass QThread to poll calendar availability
class CalendarPollerThread(QtCore.QThread):
    statusupdate = QtCore.pyqtSignal(dict)

    def __init__(self, preferences, interval, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.preferences = preferences
        self.interval = interval
        self.working = False
        self.paused = False

    def run(self):
        while True:
            if not self.paused:
                logger.info("Polling meetingroom status")
                self.check_status()
            else:
                logger.info("Calendar polling currently paused")
            time.sleep(self.interval)

    def refresh_status(self):
        self.check_status()

    def check_status(self):
        """Polling method that checks what is the current status of the meetingroom. Reoccurs every 30 seconds"""
        if self.working:
            return

        self.working = True

        result = json.loads(poll_availability(self.preferences))
        self.statusupdate.emit(result)

        self.working = False

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def ispaused(self):
        return self.paused

def sendToGoogleAnalytics(uuid, category, action, label, value = 0):
    payload = {}
    payload["uuid"] = uuid
    payload["category"] = category
    payload["action"] = action
    payload["label"] = label
    payload["value"] = value
    data_container.put(payload)

class Naurunappula(QtWidgets.QMainWindow, Ui_stackedUI):
    """Main class definition that implements Ui_stackedUI and all related events related to widgets defined in it"""
    def __init__(self, workdir="", parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.uuid = ""

        self.setupUi(self)
        self.setup_uuid()

        self.working = False

        qh.outputWidget = self.txtLogOutput # assign a widget to receive log output. Can be accessed from settings

        # connect QT signals to handler methods
        self.green_btnPage1.clicked.connect(self.start_page2)
        self.red_btnPage1.clicked.connect(self.start_page2)
        self.red_btnPage2.clicked.connect(self.start_page1)
        self.red_btnCancel.clicked.connect(self.clear_reservation)
        self.green_btnDecline.clicked.connect(self.decline_reservation)
        self.green_btnAccept.clicked.connect(self.make_reservation)
        self.green_dialPage2.valueChanged.connect(self.dial_value_changed)

        # connect signals for settings1controls
        self.btnSettings1_Next.clicked.connect(self.start_page2)
        self.btnSettings2_Previous.clicked.connect(self.start_page1)
        self.btnExit.clicked.connect(self.close)
        self.buttonBox.accepted.connect(self.settings_acccepted)
        self.buttonBox.rejected.connect(self.settings_rejected)

        # create an invisible settings button that is always present in the top left corner of the screen
        self.btnSettings = QtWidgets.QPushButton('', self)
        self.btnSettings.setMinimumSize(QtCore.QSize(240, 80))
        self.btnSettings.setMaximumSize(QtCore.QSize(240, 80))
        self.btnSettings.setObjectName("btnSettings")
        self.btnSettings.clicked.connect(self.start_settings_page)

        style = "QPushButton#btnSettings { \
            border-image: url(:/images/blank.png); \
        }"

        self.btnSettings.setStyleSheet(style)
        self.btnSettings.move(40,0) # set absolute position for the button so it stays visible always for the user

        self.settingsPageClicked = 1
        self.settingsPageThreshold = 5 # how many times to push the hidden button to access settings
        self.settingsOpened = False # variable that indicates if user is manipulating settings at the moment

        # preferences dictionary
        self.preferences = {}
        self.preferences["name"] = ""
        self.preferences["email"] = ""
        self.preferences["server"] = ""
        self.preferences["username"] = ""
        self.preferences["password"] = ""

        self.settingsLoaded = False
        self.settingsLoaded = self.load_settings() # load settings from file. If this fails, just assume its a new installation and use default values.

        self.amountofErrors = 0 # amount of network errors happened thusfar in a row
        self.errorThreshold = 2 # how many errors in a row can happen before we show an error screen to the user

        # enable dropshadows
        self.enable_drop_shadow()

        self.initialCheckOk = False

        # thread that updates Google Analytics
        self.AnalyticsThread = GAThread(uaid)
        self.AnalyticsThread.start()

        # thread that updates calendar status
        self.green_lblState_Page2.setText("Varaa Tila<br>" + str(self.green_dialPage2.value() * 5) + " min")
        self.red_lblState_Page2.setText("{0}\nVaraustiedot".format(self.preferences["name"]))
        self.CalendarPollerThread = CalendarPollerThread(self.preferences, 30)
        self.CalendarPollerThread.statusupdate.connect(self.update_ui)
        self.CalendarPollerThread.start()

        # timer that controls how long we spend time in various of places.
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.start_page1)

    def __del__(self):
        """When exiting, reroute stdout back to sys.__stdout__"""
        sys.stdout = sys.__stdout__

    def setup_uuid(self):
        """Setup UUID for the device. If uuid is already defined, read it from a file"""
        logger.info("Attempting to read device ID")
        file = sys.path[0] + "/uuid"
        if os.path.isfile(file):
            try:
                with open(file) as fileInput:
                    self.uuid = str(fileInput.readline())
                assert uuid.UUID(self.uuid).version == 4
                logger.info("Device ID found {0}".format(self.uuid))
            except Exception as e:
                logger.error("Failed to read device ID! Check file permissions {0}".format(e))
                sys.exit()
        else:
            logger.info("No device ID detected. Creating a new one")
            try:
                self.uuid = uuid.uuid4()
                with open(file, "w") as fileOutput:
                    fileOutput.write(str(self.uuid))
                logger.info("Device ID {0} assigned to this device.".format(self.uuid))
            except Exception as e:
                logger.error("Failed to save device ID! Check file permissions: {0}".format(e))
                sys.exit()

    """
     QT signal handlers
    """
    def close(self):
        self.close()

    def dial_value_changed(self, value):
        value = value * 5
        self.green_lblState_Page2.setText("Varaa Tila<br>" + str(value) + " min")
        # reset timer that controls idle timeout
        logger.info("Idle timeout restarted")
        self.timer.start(30000)

    def settings_acccepted(self):
        self.preferences["name"] = self.txtMeetingroom.text()
        self.preferences["email"] = self.txtMeetingroomEmail.text()
        self.preferences["server"] = self.txtServer.text()
        self.preferences["username"] = self.lineUsername.text()
        self.preferences["password"] = self.linePassword.text()
        self.settingsOpened = False
        self.save_settings()
        logger.info("Settings saved!")
        sendToGoogleAnalytics(self.uuid, "Interaction", "Settings", "Settings Accepted", 0)
        self.CalendarPollerThread.refresh_status()
        self.CalendarPollerThread.unpause()

    def settings_rejected(self):
        logger.info("Settings discarded!")
        self.settingsOpened = False
        sendToGoogleAnalytics(self.uuid, "Interaction", "Settings", "Settings Rejected", 0)
        self.CalendarPollerThread.refresh_status()
        self.CalendarPollerThread.unpause()
    """
     Load and save methods for device preferences
    """
    def load_settings(self):
        """Load settings from a predefined file called settings.dat"""
        content = []
        temp_pw = ""
        file = sys.path[0] + "/settings.dat"
        logger.info("Loading settings from file: {0}".format(file))
        try:
            with open(file) as fileInput:
                for line in fileInput:
                    content.append(line)

            content[4] = content[4].strip()

            # decode password
            for c in content[4]:
                temp_pw += chr(ord(c) - 5)

            self.preferences["name"] = content[0].rstrip('\r\n')
            self.preferences["email"] = content[1].rstrip('\r\n')
            self.preferences["server"] = content[2].rstrip('\r\n')
            self.preferences["username"] = content[3].rstrip('\r\n')
            self.preferences["password"] = temp_pw
            return True
        except Exception as e:
            logger.error("Failed to load configuration file: {0}".format(traceback.print_exc()))
            return False

    def save_settings(self):
        """Save settings to file for ex. server address and credentials to access a given resource calendar"""
        content = []
        temp_pw = ""

        # encode password
        for c in self.preferences["password"]:
            temp_pw += chr(ord(c) + 5)

        content.append(self.preferences["name"].strip())
        content.append(self.preferences["email"].strip())
        content.append(self.preferences["server"].strip())
        content.append(self.preferences["username"].strip())
        content.append(temp_pw)

        file = sys.path[0] + "/settings.dat"
        logger.info("Saving settings to file: {0}".format(file))
        with open(file, "w") as fileOutput:
            for row in content:
                fileOutput.write(row + "\n")

    """
     Methods used for creating, cancelling and checking reservations
    """
    def clear_reservation(self):
        """Attempt to clear the current reservation"""
        logger.info("Cancel requested!")
        if clear_reservations(self.preferences):
            sendToGoogleAnalytics(self.uuid, "Interaction", "Cancellation", "OK", 1)
        else:
            sendToGoogleAnalytics(self.uuid, "Interaction", "Cancellation", "NOK", 0)

        self.CalendarPollerThread.refresh_status()

    def make_reservation(self):
        """Attempt to make a reservation"""
        logger.info("Reservation requested!")
        duration = int(self.green_dialPage2.value() * 5)

        if make_a_reservation(self.preferences, duration):
            logger.info("Reservation successful!")
            sendToGoogleAnalytics(self.uuid, "Interaction", "Reservation", "{0} min".format(duration), duration)
        else:
            logger.info("Reservation unsuccessful!")
            sendToGoogleAnalytics(self.uuid, "Interaction", "Reservation", "Failed Reservation", 0)

        self.CalendarPollerThread.refresh_status()

    def decline_reservation(self):
        """User clicked back button to cancel the reservation"""
        logger.info("Reservation cancelled!")
        sendToGoogleAnalytics(self.uuid, "Interaction", "Reservation", "Cancelled Reservation", 0)
        self.start_page1()

    def update_ui(self, result):
        """Handler method that receives input from CalendarPoller thread"""
        if not self.settingsLoaded: # if the device is not configured -> return
            self.green_lblState_Page1.setText("Laite\nKonfiguroimatta")
            self.red_lblState_Page1.setText("Laite\nKonfiguroimatta")
            return

        if result["available"] == "True":
            if result["subject"] == "":
                self.green_lblState_Page1.setText("{0}\nVapaa".format(self.preferences["name"]))
                self.green_lblSubject_Page1.setText("Tila")
            else:
                self.green_lblState_Page1.setText("{0}\nVapaa {1} min".format(self.preferences["name"], int(result["duration"])))
                self.green_lblSubject_Page1.setText(result["subject"])

            self.green_lblNext_Page1.setText("Seuraava varaus")

            if result["start"] == "":
                self.green_lblDuration_Page1.setText("Vapaana")
            else:
                self.green_lblDuration_Page1.setText("{0} - {1}".format(result["start"], result["end"]))

            if int(result["duration"]) == 0 or int(result["duration"]) > 120:
                self.green_dialPage2.setRange(1, 24)
                self.green_dialPage2.setValue(6)
            else:
                numofTicks = self.round_down((int(result["duration"])), 5) / 5
                self.green_dialPage2.setRange(1, numofTicks)
                if numofTicks == 1: # special case: 5 minutes until next meeting
                    self.green_dialPage2.setValue(1)
                elif numofTicks == 2: # special case: 10 minutes until next meeting
                    self.green_dialPage2.setValue(2)
                else:
                    self.green_dialPage2.setValue(3)

            if self.centralstack.currentIndex() != 0:
                self.remove_graphics_effects() # remove fadein effects
                self.centralstack.setCurrentIndex(0) # green background
                self.centralstack.currentWidget().setCurrentIndex(0)
                self.enable_drop_shadow() # and enable dropshadows
                self.CalendarPollerThread.unpause()

            self.initialCheckOk = True
        else:
            if result["subject"] == "Error":
                sendToGoogleAnalytics(self.uuid, "Network", "Status", "Communication Failure", 0)
                self.amountofErrors += 1
                if self.amountofErrors >= self.errorThreshold or self.initialCheckOk is False: # two failures has happened with a communication error.
                    self.red_lblState_Page1.setText("Virhetilanne")
                    self.red_lblSubject_Page1.setText("Virhe")
                    self.red_lblDuration_Page1.setText("Tiedonsiirrossa")
            else:
                self.amountofErrors = 0 # reset error count
                self.red_lblState_Page1.setText("{0}\nVarattu {1} min".format(self.preferences["name"], int(result["duration"])))
                self.red_lblSubject_Page1.setText(result["subject"])
                self.red_lblDuration_Page1.setText("{0} - {1}".format(result["start"], result["end"]))

            if self.centralstack.currentIndex() != 1:
                self.remove_graphics_effects() # remove fadein effects
                self.centralstack.setCurrentIndex(1) # red background
                self.centralstack.currentWidget().setCurrentIndex(0)
                self.enable_drop_shadow() # and enable dropshadows
                self.CalendarPollerThread.unpause()
    """
     Methods used for changing layouts and transitioning from one page to another
    """
    def start_page1(self):
        """UI is based on QStackedWidget. This method changes the "page" to Page 1 of the stack"""
        self.remove_graphics_effects()
        currentLayout = self.centralstack.currentWidget().currentWidget()
        currentStack = self.centralstack.currentWidget()
        self.fade_out(currentLayout).finished.connect(lambda: self.change_layout_anim(currentStack, currentLayout, layout=0))
        self.CalendarPollerThread.unpause()
        logger.info("Idle timeout stopped")
        self.timer.stop()

    def start_page2(self):
        """UI is based on QStackedWidget. This method changes the "page" to Page 2 of the stack"""
        self.remove_graphics_effects()
        currentLayout = self.centralstack.currentWidget().currentWidget()
        currentStack = self.centralstack.currentWidget()
        self.fade_out(currentLayout).finished.connect(lambda: self.change_layout_anim(currentStack, currentLayout, layout=1))
        self.CalendarPollerThread.pause()
        logger.info("Idle timeout started")
        self.timer.start(30000)

    def start_settings_page(self):
        """Change the UI to Settings page"""
        if self.centralstack.currentIndex() == 2: # if settings page is already open, return
            return
        if self.settingsPageClicked <= self.settingsPageThreshold:
            logger.info("Settings page requested! {0}/{1}".format(self.settingsPageClicked, self.settingsPageThreshold))
            self.settingsPageClicked += 1
            return
        else:
            logger.info("Settings page accessible!")
            sendToGoogleAnalytics(self.uuid, "Interaction", "Settings", "Settings Entered", 1)
            self.txtMeetingroom.setText(self.preferences["name"])
            self.txtMeetingroomEmail.setText(self.preferences["email"])
            self.txtServer.setText(self.preferences["server"])
            self.lineUsername.setText(self.preferences["username"])
            self.linePassword.setText(self.preferences["password"])
            self.remove_graphics_effects() # remove fadein effects
            self.centralstack.setCurrentIndex(2) # change to settings page
            self.centralstack.currentWidget().setCurrentIndex(0)
            self.settingsPageClicked = 0
            self.settingsOpened = True
            self.CalendarPollerThread.pause()

    """
     Utility methods used when changing layouts
    """
    def change_layout_anim(self, stack = None, prevlayout = None, layout = 0):
        """When changing the laytout, or page, utilize nice GraphicsEffects to make the transition smoother"""
        if stack == None:
            stack = self.centralstack.currentWidget()
        if prevlayout == None:
            prevLayout = self.centralstack.currentWidget().currentWidget()

        stack.setCurrentIndex(layout)

        self.fade_in(stack.currentWidget()).finished.connect(lambda: self.fade_in(prevlayout).finished.connect(lambda: self.finalize_layout_change(prevlayout)))

    def finalize_layout_change(self, layout):
        self.remove_graphics_effects() # remove fadein effects
        if not self.settingsOpened: # we don't need graphics effect in settings.
            self.enable_drop_shadow() # and enable dropshadows

    """
     Graphics effect utility functions used for fading in / out widgets
     and adding dropshadows to widgets.
    """
    def fade_in(self, widget):
        """Adds a Fade In effect to a given widget"""
        eff = QtWidgets.QGraphicsOpacityEffect()
        widget.setGraphicsEffect(eff)
        self.anim = QtCore.QPropertyAnimation(eff, b"opacity")
        self.anim.setDuration(150)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QtCore.QEasingCurve.InOutSine)
        self.anim.start()
        return self.anim

    def fade_out(self, widget):
        """Adds a Fade Out effect to a given widget"""
        eff = QtWidgets.QGraphicsOpacityEffect()
        widget.setGraphicsEffect(eff)
        self.anim = QtCore.QPropertyAnimation(eff, b"opacity")
        self.anim.setDuration(150)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.setEasingCurve(QtCore.QEasingCurve.InOutSine)
        self.anim.start()
        return self.anim

    def enable_drop_shadow(self):
        """Enables dropshadows to every suitable QWidget"""
        for widget in self.centralwidget.findChildren(QtWidgets.QWidget):
            effect = QtWidgets.QGraphicsDropShadowEffect();
            effect.setBlurRadius(0);
            effect.setColor(QtGui.QColor(0, 0, 0, 64))
            effect.setOffset(1.5,1.5);
            widget.setGraphicsEffect(effect);

    def remove_graphics_effects(self):
        """Before changing layouts it is necessary to remove any GraphicsEffect that maybe in effect"""
        for widget in self.centralwidget.findChildren(QtWidgets.QWidget):
            widget.setGraphicsEffect(None)

    """
     Other utility methods
    """
    def round_down(self, num, divisor):
        """Utility method used when making reservations. Rounds down a given number to the nearest divisor"""
        return num - (num % divisor)

    def round_up(self, num, divisor):
        """Utility method used when making reservations. Rounds up a given number to the nearest divisor"""
        return num + (divisor % (num % divisor))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont(":fonts/BebasNeue Bold.ttf")
    QtGui.QFontDatabase.addApplicationFont(":fonts/BebasNeue Regular.ttf")
    myWindow = Naurunappula(None, None)

    try:
        if os.uname()[4][:3] == 'arm':
            myWindow.showFullScreen() #if we are running on rpi, run the program fullscreen
    except AttributeError: #attribute error is raised if we try to do this in windows
        pass

    myWindow.show()
    app.exec_()

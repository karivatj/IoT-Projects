#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import libraries
from gpiozero import PWMLED, LED, Button
import time
import sys
import threading
import logging
import certifi
import requests
import datetime
import collections
import codecs
import traceback

from dateutil.parser import parse
from requests_ntlm import HttpNtlmAuth
from xml.etree import ElementTree
from message_templates import *

# setup logging
# create logger with 'ipost_converter'
logger = logging.getLogger('naurunappula')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('debug.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

#content-type header must be this or server responds with 451
headers = {'Content-Type': 'text/xml; charset=utf-8'} # set what your server accepts

# date format: 2006-11-02T15:00:00
time_format = "%Y-%m-%d"
time_format_full = "%Y-%m-%dT%H:%M:%S"

# components
blue_led = None
red_led = None
green_led = None

working = False

# callback functions
def handle_button_press():
    global working
    if working:
        return
    else:
        working = True

    logger.debug("Button pressed")
    if check_availability():
        if make_a_reservation():
            # if the reservation was a success lets turn on the red led
            red_led.on()
            green_led.off()
    else:
        notification_blink(2)
        red_led.on()
        green_led.off()

    working = False

def handle_button_hold():
    global working
    if working:
        return
    else:
        working = True

    clear_reservations()

    working = False

def notification_blink(num_of_times):
    for i in range(0, num_of_times):
        red_led.on()
        green_led.on()
        time.sleep(0.50)
        red_led.off()
        green_led.off()
        time.sleep(0.50)

    red_led.pulse()
    green_led.pulse()

def error_blink(num_of_times):
    for i in range(0, num_of_times):
        red_led.off()
        green_led.on()
        time.sleep(0.20)
        red_led.on()
        green_led.off()
        time.sleep(0.20)

    red_led.pulse()
    green_led.pulse()

def get_appointments():
    start_time = datetime.datetime.today().strftime(time_format) + "T00:00:00.000Z"
    end_time = datetime.datetime.today().strftime(time_format) + "T23:59:59.999Z"

    #Send a GetFolder request. Use Sample request as a template and replace necessary parts from it
    message = sample_getcalendar_request.replace("!Replace_Email_Of_Calendar!", target_calendar)
    message = message.replace("!Start_Date!", start_time)
    message = message.replace("!End_Date!", end_time)

    try:
        logger.debug("Fetching data from " + server)
        response = requests.post(server, data=message, headers=headers, auth=HttpNtlmAuth(username, password), verify=certifi.where())
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error ({0})".format(e))
        error_blink(8)
        return None

    return response

def parse_appointments(response):
    tree = ElementTree.fromstring(response.content)
    today = datetime.datetime.now()
    data = {}
    data[target_calendar] = []
    timedelta = 2

    logger.info(response.content)

    if today > datetime.datetime(datetime.date.today().year, 3, 26, 3, 0, 0) and today < datetime.datetime(datetime.date.today().year, 10, 29, 4, 0, 0):
        timedelta = 3

    for elem in tree.iter(tag='{http://schemas.microsoft.com/exchange/services/2006/types}CalendarItem'):
        for child in elem:
            if("ItemId" in child.tag):
                data[target_calendar].append(child.attrib["Id"])
                data[target_calendar].append(child.attrib["ChangeKey"])
            if("Subject" in child.tag):
                data[target_calendar].append(child.text)
            elif("Start" in child.tag):
                date = parse(child.text)
                date = date + datetime.timedelta(hours=timedelta) #add timedifference
                data[target_calendar].append(date.strftime("%H:%M"))
            elif("End" in child.tag):
                date = parse(child.text)
                date = date + datetime.timedelta(hours=timedelta) #add timedifference
                data[target_calendar].append(date.strftime("%H:%M"))
    return data

def delete_appointment(itemid):
    pass
    '''
    message = sample_delete_request.replace("!Replace_ItemId!", itemid)

    try:
        logger.debug("Sending an Appointment Delete request to " + server)
        response = requests.post(server, data=message, headers=headers, auth=HttpNtlmAuth(username, password), verify=certifi.where())
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error ({0})".format(e))
        error_blink(8)
        return False

    if(response.status_code != 200):
        logger.error("Connection error. Status Code: {0}. Error: {1}".format(response.status_code, response.content))
        error_blink(8)
        return False
    else:
        logger.debug("Response OK. Apppointment deleted! {0}".format(response.content))
        return True
    '''

def make_a_reservation():
    logger.info("Trying to make a reservation for 15 minutes")
    now = datetime.datetime.now().replace(second=0, microsecond=0)
    nowplus15 = now + datetime.timedelta(minutes=15)

    start_time = now.strftime(time_format_full)
    end_time = nowplus15.strftime(time_format_full)

    #Send a Appointment request. Use Sample request as a template and replace necessary parts from it
    message = sample_appointment_request.replace("!Replace_Email_Of_Calendar!", target_calendar)
    message = message.replace("!Start_Date!", start_time)
    message = message.replace("!End_Date!", end_time)

    try:
        logger.debug("Sending an Appointment request to " + server)
        response = requests.post(server, data=message, headers=headers, auth=HttpNtlmAuth(username, password), verify=certifi.where())
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error ({0})".format(e))
        error_blink(8)
        return False

    if(response.status_code != 200):
        logger.error("Connection error. Status Code: {0}. Error: {1}".format(response.status_code, response.content))
        error_blink(8)
        return False
    else:
        logger.debug("Response OK. Apppointment set! {0}".format(response.content))
        return True

def clear_reservations():
    logger.info("Clearing appointments made by the device")

    red_led.pulse()
    green_led.pulse()

    response = get_appointments()

    if(response.status_code != 200):
        logger.error("Connection error. Status Code: {0}".format(response.status_code))
        error_blink(8)
        return
    else:
        logger.debug("Response OK. Parsing data...")
        calendar_data = parse_appointments(response)

        for calendar in calendar_data:
            for item in range(0, len(calendar_data[calendar]), 5):
                if(calendar_data[calendar][item+2] in "Ad-hoc varaus"):
                    itemid = calendar_data[calendar][item]
                    changekey = calendar_data[calendar][item+1]
                    logger.info("Deleting itemid {0}".format(itemid))
                    delete_appointment(itemid)

def check_availability():
    logger.debug("Checking reservation status for {0}".format(target_calendar))

    red_led.pulse()
    green_led.pulse()

    reserved = False
    response = get_appointments()

    if(response.status_code != 200):
        logger.error("Connection error. Status Code: {0}".format(response.status_code))
        error_blink(8)
        return
    else:
        logger.debug("Response OK. Parsing data...")
        calendar_data = parse_appointments(response)

        now = datetime.datetime.now().replace(second=0, microsecond=0)
        nowplus15 = now + datetime.timedelta(minutes=15)

        calendar_data = collections.OrderedDict(sorted(calendar_data.items(), key=lambda t: t[0]))

        for calendar in calendar_data:
            for item in range(0, len(calendar_data[calendar]), 5):
                start_date = parse(calendar_data[calendar][item+3])
                end_date = parse(calendar_data[calendar][item+4])

                # the 15 minute timeslot has to pass a few rules before it can be reserved
                if now >= start_date and nowplus15 <= end_date:
                    logger.debug("Meeting room is marked as reserved by rule #1")
                    reserved = True
                    break
                if now <= start_date and (nowplus15 >= (start_date -  datetime.timedelta(minutes=5)) and nowplus15 <= end_date):
                    logger.debug("Meeting room is marked as reserved by rule #2")
                    reserved = True
                    break
                if (now > start_date and now < end_date) and nowplus15 >= end_date:
                    logger.debug("Meeting room is marked as reserved by rule #3")
                    reserved = True
                    break

        # sleep a couple of seconds just so the progress is not too fast and the user manages to notice something is happening
        time.sleep(2)

        if reserved:
            logger.info("Meeting room reserved at the moment!")
            return False
        else:
            logger.info("Meeting room free at the moment!")
            return True

def poll_availability():
    polling_worker()
    # call again in 60 seconds
    threading.Timer(60, poll_availability).start()

def polling_worker():
    logger.debug("Polling reservation status for {0}".format(target_calendar))

    calendar_data = {} #dictionary containing the data
    calendar_data[target_calendar] = []

    reserved = False

    response = get_appointments()

    if(response.status_code != 200):
        logger.error("Connection error. Status Code: {0}".format(response.status_code))
        error_blink(8)
        return
    else:
        calendar_data = parse_appointments(response)

        now = datetime.datetime.now().replace(second=0, microsecond=0)
        nowplus15 = now + datetime.timedelta(minutes=15)

        calendar_data = collections.OrderedDict(sorted(calendar_data.items(), key=lambda t: t[0]))

        for calendar in calendar_data:
            for item in range(0, len(calendar_data[calendar]), 5):
                start_date = parse(calendar_data[calendar][item+3])
                end_date = parse(calendar_data[calendar][item+4])

                # the 15 minute timeslot has to pass a few rules before it can be reserved
                if now >= start_date and nowplus15 <= end_date:
                    logger.debug("Meeting room is marked as reserved by rule #1")
                    reserved = True
                    break
                if now <= start_date and (nowplus15 > start_date and nowplus15 <= end_date):
                    logger.debug("Meeting room is marked as reserved by rule #2")
                    reserved = True
                    break
                if (now > start_date and now < end_date) and nowplus15 >= end_date:
                    logger.debug("Meeting room is marked as reserved by rule #3")
                    reserved = True
                    break

        if reserved:
            logger.info("Meeting room reserved at the moment!")
            red_led.on()
            green_led.off()
        else:
            logger.info("Meeting room free at the moment!")
            red_led.off()
            green_led.on()

if __name__=="__main__":
    try:
        logger.debug("Starting up the experiment...")

        # setup pins
        blue_led = PWMLED(22)   # used as a status indicator
        red_led = PWMLED(17)    # used as "reserved" indicator
        green_led = PWMLED(4)   # used as "free" indicator

        blue_led.on()

        red_led.pulse()
        green_led.pulse()

        button = Button(27)
        button.when_released = handle_button_press
        button.hold_time = 5
        button.when_held = handle_button_hold

        poll_availability()

        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
    finally:
        logger.debug("Exiting...")
        blue_led.off()
        red_led.off()
        green_led.off()
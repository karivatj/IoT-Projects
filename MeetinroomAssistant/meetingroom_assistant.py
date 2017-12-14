#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import libraries
from gpiozero import PWMLED, LED, Button
import time
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

#date format
time_format = "%Y-%m-%d"
time_format_full = "%Y-%m-%dT%H:%M:%S"

# components
blue_led = None
red_led = None
green_led = None

#Sample message used to query calendar data. Remember to replace relevant parts of this message
sample_getcalendar_request = '''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:m="http://schemas.microsoft.com/exchange/services/2006/messages" 
    xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
   <soap:Header>
      <t:RequestServerVersion Version="Exchange2010_SP2" />
   </soap:Header>
   <soap:Body>
      <m:FindItem Traversal="Shallow">
         <m:ItemShape>
            <t:BaseShape>IdOnly</t:BaseShape>
            <t:AdditionalProperties>
               <t:FieldURI FieldURI="item:Subject" />
               <t:FieldURI FieldURI="calendar:Start" />
               <t:FieldURI FieldURI="calendar:End" />
            </t:AdditionalProperties>
         </m:ItemShape>
         <m:CalendarView MaxEntriesReturned="10" StartDate="!Start_Date!" EndDate="!End_Date!" />
         <m:ParentFolderIds>
            <t:DistinguishedFolderId Id="calendar">
               <t:Mailbox>
                  <t:EmailAddress>!Replace_Email_Of_Calendar!</t:EmailAddress>
               </t:Mailbox>
            </t:DistinguishedFolderId>
         </m:ParentFolderIds>
      </m:FindItem>
   </soap:Body>
</soap:Envelope>'''

#Sample message used to make an appointment to the designated calendar. Remember to replace relevant parts of this message
sample_appointment_request = '''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types" 
    xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
   <soap:Body>
      <CreateItem xmlns="http://schemas.microsoft.com/exchange/services/2006/messages" SendMeetingInvitations="SendToAllAndSaveCopy">
         <SavedItemFolderId>
            <t:DistinguishedFolderId Id="calendar" />
         </SavedItemFolderId>
         <Items>
            <t:CalendarItem xmlns="http://schemas.microsoft.com/exchange/services/2006/types">
               <Subject>Pikapalaveri</Subject>
               <Body BodyType="Text">Pikavaraus tehty Karin laitteen avustuksella.</Body>
               <ReminderIsSet>false</ReminderIsSet>
               <ReminderMinutesBeforeStart>60</ReminderMinutesBeforeStart>
               <Start>!Start_Date!</Start>
               <End>!End_Date!</End>
               <IsAllDayEvent>false</IsAllDayEvent>
               <LegacyFreeBusyStatus>Busy</LegacyFreeBusyStatus>
               <Location>OYS TestLab</Location>
               <RequiredAttendees>
                  <Attendee>
                     <Mailbox>
                        <EmailAddress>!Replace_Email_Of_Calendar!</EmailAddress>
                     </Mailbox>
                  </Attendee>
               </RequiredAttendees>
            </t:CalendarItem>
         </Items>
      </CreateItem>
   </soap:Body>
</soap:Envelope>'''

# date format: 2006-11-02T15:00:00

target_calendar = ''
username = ''
password = ''
server   = ''

# callback functions
def button_pressed():
    logger.debug("Button pressed")
    if check_availability():
        if make_a_reservation():
            # if the reservation was a success lets turn on the red led
            red_led.on()
            green_led.off()

def button_release():
    logger.debug("Button released")

def poll_availability():
    check_availability()
    # call the method again in 1 minute to check for availability
    threading.Timer(60, poll_availability).start()
       
def make_a_reservation():
    logger.info("Trying to make a reservation for 15 minutes")
    now = datetime.datetime.now()
    now_rounded_down = now - datetime.timedelta(minutes = now.minute % 15, seconds = now.second, microseconds = now.microsecond) # round to nearest quarter
    now_rounded_up = now_rounded_down + datetime.timedelta(minutes = 15)
    start_time = now_rounded_down.strftime(time_format_full)
    end_time = now_rounded_up.strftime(time_format_full)

    #Send a Appointment request. Use Sample request as a template and replace necessary parts from it
    message = sample_appointment_request.replace("!Replace_Email_Of_Calendar!", target_calendar)
    message = message.replace("!Start_Date!", start_time)
    message = message.replace("!End_Date!", end_time)

    try:
        logger.debug("Sending an Appointment request to " + server)
        response = requests.post(server, data=message, headers=headers, auth=HttpNtlmAuth(username, password), verify=certifi.where())
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error ({0})".format(e))
        return False

    if(response.status_code != 200):
        logger.error("Connection error. Status Code: {0}".format(response.status_code))
        return False
    else:
        logger.debug("Response OK. Apppointment set!")
        return True

def check_availability():
    logger.debug("Checking reservation status for {0}".format(target_calendar))

    red_led.pulse()
    green_led.pulse()

    calendar_data = {} #dictionary containing the data
    calendar_data[target_calendar] = []

    try:
        logger.debug("Connecting to server {0}".format(server))
        response = requests.get(server, auth=HttpNtlmAuth(username, password), verify=certifi.where())
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error ({0})".format(e))
        return

    if(response.status_code != 200):
        logger.error("Connection error. Status Code: {0}".format(response_status_code))
        return
    else:
        logger.debug("Connection OK - Continuing with the task")

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
        return

    if(response.status_code != 200):
        logger.error("Connection error. Status Code: {0}".format(response.status_code))
        return
    else:
        logger.debug("Response OK. Parsing data...")        
        tree = ElementTree.fromstring(response.content)
        today = datetime.datetime.now() 
        timedelta = 2

        if today > datetime.datetime(datetime.date.today().year, 3, 26, 3, 0, 0) and today < datetime.datetime(datetime.date.today().year, 10, 29, 4, 0, 0):
            timedelta = 3    

        for elem in tree.iter(tag='{http://schemas.microsoft.com/exchange/services/2006/types}CalendarItem'):
            for child in elem:
                if("Subject" in child.tag):
                    logger.info(child.text)                    
                    calendar_data[target_calendar].append(child.text)
                elif("Start" in child.tag):
                    date = parse(child.text)
                    date = date + datetime.timedelta(hours=timedelta) #add timedifference
                    logger.info(date)                    
                    calendar_data[target_calendar].append(date.strftime("%H:%M"))
                elif("End" in child.tag):
                    date = parse(child.text)                   
                    date = date + datetime.timedelta(hours=timedelta) #add timedifference
                    logger.info(date)                                        
                    calendar_data[target_calendar].append(date.strftime("%H:%M"))

    now = datetime.datetime.now()
    now_rounded_down = now - datetime.timedelta(minutes = now.minute % 15, seconds = now.second, microseconds = now.microsecond) # round to nearest quarter
    now_rounded_up = now_rounded_down + datetime.timedelta(minutes = 15) 

    calendar_data = collections.OrderedDict(sorted(calendar_data.items(), key=lambda t: t[0]))

    reserved = False

    for calendar in calendar_data:
        for item in range(0, len(calendar_data[calendar]), 3): 
            start_date = parse(calendar_data[calendar][item+1]) 
            end_date = parse(calendar_data[calendar][item+2])

            # the 15 minute timeslot has to pass a few rules before it can be reserved
            if now_rounded_down >= start_date and now_rounded_up <= end_date:
                logger.debug("Meeting room is marked as reserved by rule #1")
                reserved = True
                break
            if now_rounded_down <= start_date and (now_rounded_up >= start_date and now_rounded_up <= end_date):
                logger.debug("Meeting room is marked as reserved by rule #2")
                reserved = True
                break
            if (now_rounded_down >= start_date and now_rounded_down < end_date) and now_rounded_up >= end_date:
                logger.debug("Meeting room is marked as reserved by rule #3")
                reserved = True
                break
    
    # sleep a couple of seconds just so the progress is not too fast and the user manages to notice something is happening
    time.sleep(4)
    
    if reserved:
        logger.info("Meeting room reserved at the moment!")        
        red_led.on()
        green_led.off()
        return False
    else:
        logger.info("Meeting room free at the moment!")
        red_led.off()
        green_led.on()
        return True

if __name__=="__main__":
    try:
        logger.debug("Starting up the experiment...")

        # setup pins
        blue_led = PWMLED(22)   # used as a status indicator
        red_led = PWMLED(17)    # used as "reserved" indicator
        green_led = PWMLED(4)   # used as "free" indicator

        blue_led.on()

        button = Button(27)
        button.when_pressed = button_pressed

        poll_availability()

        while True:
            try:                                                                                                               
                time.sleep(1)
            except KeyboardInterrupt:
                break
    finally:
        logger.debug("Exiting...")
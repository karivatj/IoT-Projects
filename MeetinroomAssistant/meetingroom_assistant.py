#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import libraries
from gpiozero import PWMLED, Button
import time
import threading
import logging
import schedule

from datetime import timedelta
from exchangelib import EWSDateTime, EWSTimeZone, CalendarItem
from access_tokens import account

# define the timezone
tz = EWSTimeZone.timezone('Europe/Helsinki')

# setup logging
logger = logging.getLogger('naurunappula')
logger.setLevel(logging.DEBUG)
# create file handler which logs debug messages
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

# hw components
blue_led = None
red_led = None
green_led = None

working = False

def handle_button_release():
    global working
    if working:
        return
    else:
        working = True

        now = time.time()
        count = 1
        minutes = 15
        while time.time() < now + 1: # 1 second period
            if button.is_pressed:
                count +=1
        if count == 1:
            minutes = 15
        else:
            minutes = 30

        if check_availability(minutes):
            if make_a_reservation(minutes): # if the reservation was a success lets turn on the red light
                red_led.on()
                green_led.off()
        else:
            notification_blink(2)
            if minutes == 30:
                if check_availability(15):
                    red_led.off()
                    green_led.on()
                else:
                    red_led.on()
                    green_led.off()
            else:
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
        if check_availability(15):
            red_led.off()
            green_led.on()
        else:
            red_led.on()
            green_led.off()

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
    now = tz.localize(EWSDateTime.now())
    items = {}

    try:
        items = account.calendar.view(
            start=tz.localize(EWSDateTime(now.year, now.month, now.day, 6, 0)),
            end=tz.localize(EWSDateTime(now.year, now.month, now.day, 18, 0)),
        ).order_by('start')
    except Exception as e:
        logger.error("Failed to get appointments. Trying again later. Error: {0}".format(e))

    return items

def make_a_reservation(timeslot):
    logger.info("Trying to make a reservation for {0} minutes.".format(timeslot))
    now = tz.localize(EWSDateTime.now())

    start_time = tz.localize(EWSDateTime(now.year, now.month, now.day, now.hour, now.minute, 0, 0))
    end_time = tz.localize(EWSDateTime(now.year, now.month, now.day, now.hour, now.minute, 0, 0) + timedelta(minutes=timeslot))
    item = CalendarItem(folder=account.calendar, subject='Ad-hoc varaus', body='Made with Naurunappula at '+ str(now), start=start_time, end=end_time)

    try:
        item.save()
        logger.info("Reservation successful.")
        return True
    except Exception as e:
        logger.info("Reservation failed: {0}".format(e))
        return False

def clear_reservations():
    logger.info("Cancelling appointments made by the device")

    red_led.pulse()
    green_led.pulse()

    appointments = get_appointments()

    if(len(appointments) > 0):
        for app in appointments:
            if "Ad-hoc" in app.subject and "Naurunappula" in app.body:
                logger.info("Cancelling an appointment named {0} at {1} - {2}".format(app.subject, app.start, app.end))
                try:
                    app.delete()
                except Exception as e:
                    logger.error("Couldn't delete the appointment: {0}".format(e))
                    error_blink(4)
                    pass
    else:
        logger.info("No appointments to cancel.")

    time.sleep(2) # sleep for a while to give the user the sense of progress

def check_availability(timeslot):
    logger.info("Checking reservation status for {0}".format(account.primary_smtp_address))

    red_led.pulse()
    green_led.pulse()

    # sleep a couple of seconds just so the progress is not too fast and the user manages to notice something is happening
    time.sleep(2)
    appointments = get_appointments()
    return verify_availability(appointments, timeslot)

def verify_availability(appointments, timeslot):
    available = True
    now = tz.localize(EWSDateTime.now())
    nowplusdelta = now + timedelta(minutes=timeslot)

    try:
        for app in appointments:
            # the timeslot has to pass a few rules before it can be reserved
            if now >= app.start and now < app.end:
                logger.debug("Meeting room is marked as reserved by rule #1")
                available = False
                break
            if now >= app.start and nowplusdelta <= app.start:
                logger.debug("Meeting room is marked as reserved by rule #2")
                available = False
                break
            if now <= app.start and (nowplusdelta >= (app.start - timedelta(minutes=5)) and nowplusdelta <= app.end):
                logger.debug("Meeting room is marked as reserved by rule #3")
                available = False
                break
    except Exception as e:
        logger.error("Failed to parse appointments. Error: {0}".format(e))
        notification_blink(2)

    return available

def poll_availability():
    logger.info("Polling reservation status for {0}".format(account.primary_smtp_address))

    available = True

    logger.info("Getting appointments for today and checking availability.")
    appointments = get_appointments()
    available = verify_availability(appointments, 15)

    if not available:
        logger.info("Meeting room reserved at the moment!")
        red_led.on()
        green_led.off()
    else:
        logger.info("Meeting room free at the moment!")
        red_led.off()
        green_led.on()

if __name__=="__main__":
    try:
        logger.info("Starting up the experiment...")

        # setup pins
        blue_led = PWMLED(22)   # used as a status indicator
        red_led = PWMLED(17)    # used as "reserved" indicator
        green_led = PWMLED(4)   # used as "free" indicator

        blue_led.on()

        red_led.pulse()
        green_led.pulse()

        button = Button(27)
        button.when_released = handle_button_release
        button.when_pressed = None
        button.hold_time = 5
        button.when_held = handle_button_hold

        # check initial reservation status
        poll_availability()

        # schedule the status check to be run every minute
        schedule.every(1).minutes.do(poll_availability)

        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                break
    finally:
        logger.debug("Exiting...")
        schedule.clear()
        blue_led.off()
        red_led.off()
        green_led.off()
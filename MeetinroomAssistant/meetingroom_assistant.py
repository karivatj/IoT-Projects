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

# callback functions
def handle_button_press():
    global working
    if working:
        return
    else:
        logging.info("Reservation requested.")
        working = True
        if check_availability():
            if make_a_reservation(): # if the reservation was a success lets turn on the red light
                red_led.on()
                green_led.off()
            else:
                red_led.off()
                green_led.on()
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
        if check_availability():
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

    items = account.calendar.filter(
        start__gt=tz.localize(EWSDateTime(now.year, now.month, now.day, 0, 0)),
        end__lt=tz.localize(EWSDateTime(now.year, now.month, now.day, 23, 59)),
    )

    return items

def make_a_reservation():
    logger.info("Trying to make a reservation for 15 minutes.")
    now = tz.localize(EWSDateTime.now())

    start_time = tz.localize(EWSDateTime(now.year, now.month, now.day, now.hour, now.minute, 0, 0))
    end_time = tz.localize(EWSDateTime(now.year, now.month, now.day, now.hour, now.minute, 0, 0) + timedelta(minutes=15))
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

def check_availability():
    logger.debug("Checking reservation status for {0}".format(account.primary_smtp_address))

    red_led.pulse()
    green_led.pulse()

    # sleep a couple of seconds just so the progress is not too fast and the user manages to notice something is happening
    time.sleep(2)

    return verify_availability(get_appointments())

def verify_availability(appointments):
    available = True
    now = tz.localize(EWSDateTime.now())
    nowplus15 = now + timedelta(minutes=15)

    for app in appointments:
        # the 15 minute timeslot has to pass a few rules before it can be reserved
        if now >= app.start and nowplus15 <= app.start:
            logger.debug("Meeting room is marked as reserved by rule #1")
            available = False
            break
        if now <= app.start and (nowplus15 >= (app.start - timedelta(minutes=5)) and nowplus15 <= app.end):
            logger.debug("Meeting room is marked as reserved by rule #2")
            available = False
            break
        if (now > app.start and now < app.end) and nowplus15 >= app.end:
            logger.debug("Meeting room is marked as reserved by rule #3")
            available = False
            break

    return available    

def poll_availability():

    logger.debug("Polling reservation status for {0}".format(account.primary_smtp_address))

    available = True

    logger.debug("Getting appointments for today and checking availability.")
    available = verify_availability(get_appointments())

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
#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import libraries
import logging
import requests

from datetime import timedelta
from exchangelib import EWSDateTime, EWSTimeZone, CalendarItem, DELEGATE, Account, Credentials, NTLM, Configuration

# define the timezone
tz = EWSTimeZone.timezone('Europe/Helsinki')

# setup logging
logger = logging.getLogger('Naurunappula')

def get_appointments(preferences):
    now = tz.localize(EWSDateTime.utcnow())
    items = {}

    try:
        credentials = Credentials(username=preferences["username"], password=preferences["password"])
        config = Configuration(service_endpoint=preferences["server"], credentials=credentials, auth_type=NTLM)
        account = Account(primary_smtp_address=preferences["email"], config=config, autodiscover=False, access_type=DELEGATE)
        logger.info("Getting reservations for {0}".format(account.primary_smtp_address))
        items = account.calendar.view(
            start=tz.localize(EWSDateTime(now.year, now.month, now.day, 0, 0)),
            end=tz.localize(EWSDateTime(now.year, now.month, now.day, 23, 59)),
        ).order_by('start')
    except requests.exceptions.RequestException as e: # failure in data communication
        logger.exception("Failure while contacting the server.")
        return None
    except Exception as e:
        logger.exception("Failed to get appointments. Try again later.")
        return None

    return items

def make_a_reservation(preferences, timeslot):
    logger.info("Trying to make a reservation for {0} minutes.".format(timeslot))
    now = tz.localize(EWSDateTime.now())
    now = now.replace(minute=(now.minute - (now.minute % 5))) # round down to nearest 5

    start_time = now.replace(second=0, microsecond=0)
    end_time = now.replace(second=0, microsecond=0) + timedelta(minutes=timeslot)

    logger.debug("Reserving for " + str(start_time) + " - " + str(end_time))

    try:
        credentials = Credentials(username=preferences["username"], password=preferences["password"])
        config = Configuration(service_endpoint=preferences["server"], credentials=credentials, auth_type=NTLM)
        account = Account(primary_smtp_address=preferences["email"], config=config, autodiscover=False, access_type=DELEGATE)
        item = CalendarItem(folder=account.calendar, subject='Pikavaraus', body='Made with Naurunappula at ' + str(now), start=start_time, end=end_time)
    except requests.exceptions.RequestException as e: # failure in data communication
        logger.exception("Exception while contacting the server.")
        return False

    if not check_availability(preferences, timeslot):
        return False

    try:
        item.save()
        return True
    except Exception as e:
        return False

def purge_reservations(preferences):
    logger.info("Trying to purge reservations for the day. Debug purposes only!")

    appointments = get_appointments(preferences)

    if appointments is None:
        logger.error("Failed to cancel requested appointment. Perhaps there is an issue with network connectivity.")
        return

    if(len(appointments) > 0):
        for app in appointments:
            app.start = tz.localize(app.start.replace(tzinfo=None))
            app.end = tz.localize(app.end.replace(tzinfo=None))
            if "Pikavaraus" in app.subject and "Naurunappula" in app.body:
                logger.info("Cancelling an appointment named {0} at {1} - {2}".format(app.subject, app.start, app.end))
                try:
                    app.delete()
                except Exception as e:
                    logger.exception("Couldn't cancel appointment.")
                    return False
    else:
        logger.info("No appointments to cancel.")
        return False

    return True

def clear_reservations(preferences):
    logger.info("Cancelling appointments made by the device")

    appointments = get_appointments(preferences)

    if appointments is None:
        logger.error("Failed to cancel requested appointment. Perhaps there is an issue with network connectivity.")
        return

    now = tz.localize(EWSDateTime.utcnow())

    if(len(appointments) > 0):
        for app in appointments:
            start_time = tz.localize(app.start.replace(tzinfo=None))
            end_time    = tz.localize(app.end.replace(tzinfo=None))
            if "Pikavaraus" in app.subject and "Naurunappula" in app.body and now < end_time:
                logger.info("Cancelling an appointment named {0} at {1} - {2}".format(app.subject, start_time, end_time))
                try:
                    app.start = app.start.astimezone(tz)
                    app.end = tz.localize(EWSDateTime.now())
                    app.save()
                    return True
                except Exception as e:
                    logger.exception("Couldn't cancel appointment.")
                    return False
    else:
        logger.info("No appointments to cancel.")
        return False

def check_availability(preferences, timeslot):
    available = False

    try:
        appointments = get_appointments(preferences)
        if appointments is None:
            logger.error("Failed to cancel requested appointment. Perhaps there is an issue with network connectivity.")
        else:
            available = verify_availability(appointments, timeslot)
    except Exception as e:
        logger.exception("Failed to parse appointments.")

    return available

def verify_availability(appointments, timeslot):
    now = tz.localize(EWSDateTime.utcnow())
    nowplusdelta = now + timedelta(minutes=timeslot)

    for app in appointments:
        # the timeslot has to pass a few rules before it can be reserved
        start_time = tz.localize(app.start.replace(tzinfo=None))
        end_time = tz.localize(app.end.replace(tzinfo=None))
        if now >= start_time and now < end_time:
            logger.info("Meeting room is marked as reserved by rule #1")
            return app, False
        if now >= start_time and nowplusdelta <= start_time:
            logger.info("Meeting room is marked as reserved by rule #2")
            return app, False
        if now <= start_time and (nowplusdelta >= (start_time - timedelta(minutes=1)) and nowplusdelta <= end_time):
            logger.info("Meeting room is marked as reserved by rule #3")
            return app, False

    logger.info("Meeting room is free at the moment.")
    return None, True

def poll_availability(preferences):
    available = True
    now = tz.localize(EWSDateTime.utcnow())

    logger.info("Getting appointments for today and checking availability.")

    try:
        appointments = get_appointments(preferences)
        if appointments is None:
            return "{\"subject\": \"Error\", \"start\": \"\", \"end\": \"\", \"duration\": \"0\", \"available\": \"False\"}"
        blocking_appointment, available = verify_availability(appointments, 5)
    except Exception as e:
        logger.exception("Failed to parse appointments.")
        return "{\"subject\": \"Error\", \"start\": \"\", \"end\": \"\", \"duration\": \"0\", \"available\": \"False\"}"

    event_subject = ""
    event_start_time = ""
    event_end_time = ""
    event_found = False
    duration = 0

    if not available:
        logger.info("Meeting room reserved at the moment!")

        event_subject = blocking_appointment.subject

        duration = (tz.localize(blocking_appointment.end.replace(tzinfo=None)) - now).total_seconds() / 60

        if event_subject is None or event_subject is "":
            event_subject = "Nimetön varaus"

        event_subject = event_subject.replace("\"", "'")

        event_start_time = blocking_appointment.start.astimezone(tz) #adjust timezone to local timezone
        event_end_time   = blocking_appointment.end.astimezone(tz)   #adjust timezone to local timezone

        return "{\"subject\": \"" + event_subject + "\", \"start\": \"" + event_start_time.strftime('%H:%M') + "\", \"end\": \"" + event_end_time.strftime('%H:%M') + "\", \"duration\": " + str(duration) + ", \"available\": \"False\"}"

    else: # find if there are upcoming events
        try:
            for app in appointments:
                event_subject = app.subject

                if event_subject is None or event_subject is "":
                    event_subject = "Nimetön varaus"

                event_subject = event_subject.replace("\"", "'")
                event_start_time = app.start.astimezone(tz) #adjust timezone to local timezone for rendering
                event_end_time   = app.end.astimezone(tz)   #adjust timezone to local timezone for rendering

                if(now < tz.localize(app.start.replace(tzinfo=None)) and event_found == False):
                    event_found = True
                    duration = (tz.localize(app.start.replace(tzinfo=None)) - now).total_seconds() / 60
                    break

        except requests.exceptions.RequestException as e: # failure in data communication
            logger.exception("Failed to parse data.")
            return "{\"subject\": \"Error\", \"start\": \"\", \"end\": \"\", \"duration\": \"0\", \"available\": \"False\"}"

        if event_found:
            return "{\"subject\": \"" + event_subject + "\", \"start\": \"" + event_start_time.strftime('%H:%M') + "\", \"end\": \"" + event_end_time.strftime('%H:%M') + "\", \"duration\": " + str(duration) + ", \"available\": \"True\"}"
        else:
            return "{\"subject\": \"\", \"start\": \"\", \"end\": \"\", \"duration\": \"0\", \"available\": \"True\"}"
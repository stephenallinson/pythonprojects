#!/home/stephen/pyproj/calcurseimport/.env/bin/python

from datetime import datetime

import arrow
import icalendar
import os
import pytz
import recurring_ical_events
import requests
from dateutil import parser

### GLOBAL VARIABLES ###
CALENDARS = [os.getenv("OUTLOOK_URL"), os.getenv("GMAIL_URL")]
TIMEZONE = "Canada/Central"

# TODO:
# Get +/- 3 months of events
# Correct timezones
# Combine calendars
# Print/Write in order following apts standard


def get_event(ics_url):
    # Get today's dates
    # today = arrow.now(TIMEZONE).date()
    neg3mo = arrow.now(TIMEZONE).shift(months=-3).date()
    add3mo = arrow.now(TIMEZONE).shift(months=3).date()

    # Fetch the ICS file
    ics_file = requests.get(ics_url).text

    # Process recurring events
    r_calendar = icalendar.Calendar.from_ical(ics_file)
    r_events = recurring_ical_events.of(r_calendar).between(neg3mo, add3mo)

    # Process JSON
    json_events = create_json_calendar_events(ics_url, r_events)

    return json_events


def create_json_calendar_events(calendar_url, events):
    event_data = []

    # Rename Calendar
    if calendar_url.startswith("https://outlook.office365.com"):
        calendar_name = "Office 365"
    elif calendar_url.startswith("https://calendar.google.com"):
        calendar_name = "Gmail"
    else:
        calendar_name = calendar_url

    for event in events:
        start_dt = event["DTSTART"].dt
        end_dt = event["DTEND"].dt

        # Adjust for all-day events
        if type(start_dt) is datetime:
            start = start_dt.strftime("%Y-%m-%d %H:%M:%S%z")
        else:
            start = start_dt.strftime("%Y-%m-%d") + " 00:00:01-06:00"
        if type(end_dt) is datetime:
            end = end_dt.strftime("%Y-%m-%d %H:%M:%S%z")
        else:
            end = start  # Assuming end is the same as start for all-day events

        try:
            event_data.append(
                {
                    "Calendar": calendar_name,
                    "Event": str(event["SUMMARY"]),
                    "Start": start,
                    "End": end,
                }
            )
        except KeyError:
            event_data.append(
                {
                    "Calendar": calendar_name,
                    "Event": "No Title",
                    "Start": start,
                    "End": end,
                }
            )

    return event_data


def todays_events():
    data = []
    for i in CALENDARS:
        data.extend(get_event(i))

    for event in data:
        event["Start"] = (
            parser.parse(event["Start"])
            .astimezone(pytz.timezone(TIMEZONE))
            .strftime("%Y-%m-%d %H:%M:%S%z")
        )
        event["End"] = (
            parser.parse(event["End"])
            .astimezone(pytz.timezone(TIMEZONE))
            .strftime("%Y-%m-%d %H:%M:%S%z")
        )

    sorted_events = sorted(data, key=lambda x: arrow.get(x["Start"]))

    return sorted_events


def main():
    e = todays_events()
    with open("apts", "w") as f:
        for event in e:
            # Parse the start and end times
            start_datetime = datetime.strptime(event["Start"], "%Y-%m-%d %H:%M:%S%z")
            end_datetime = datetime.strptime(event["End"], "%Y-%m-%d %H:%M:%S%z")

            # Format the dates into the desired string format
            formatted_start = start_datetime.strftime("%m/%d/%Y @ %H:%M")
            formatted_end = end_datetime.strftime("%m/%d/%Y @ %H:%M")

            # Combine everything into the final string
            formatted_event = f"{formatted_start} -> {formatted_end}|{event['Event']}"

            print(formatted_event)
            f.write(formatted_event + "\n")
    f.close()


if __name__ == "__main__":
    main()

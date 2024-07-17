#!/home/stephen/pyproj/calimport/.env/bin/python

import arrow
from datetime import datetime
import os
import pytz
import requests
import recurring_ical_events
import icalendar
from dateutil import parser

### GLOBAL VARIABLES ###
CALENDARS = [os.getenv("OUTLOOK_URL"), os.getenv("GMAIL_URL")]
TIMEZONE = "Canada/Central"


def get_event(ics_url):
    # Start and End Ranges
    start_range = arrow.now(TIMEZONE).floor("day")
    end_range = start_range.shift(days=1)

    # Fetch the ICS file
    ics_file = requests.get(ics_url).text

    # Process recurring events
    r_calendar = icalendar.Calendar.from_ical(ics_file)
    r_events = recurring_ical_events.of(r_calendar).between(
        start_range.datetime, end_range.datetime
    )

    # Process JSON
    json_events = create_json_calendar_events(ics_url, r_events)

    return json_events


def next_event(events):
    current_time = arrow.now(TIMEZONE)
    no_events = {
        "Calendar": "",
        "Event": "None",
        "Start": datetime.now(pytz.timezone(TIMEZONE)),
        "End": datetime.now(pytz.timezone(TIMEZONE)),
    }
    future_events = []
    for e in events:
        event_end = parser.parse(e["End"]).astimezone(pytz.utc)
        if event_end > current_time:
            future_events.append(e)
    if future_events:
        future_events.sort(key=lambda x: parser.parse(x["Start"]).astimezone(pytz.utc))
        return future_events[0]
    else:
        return no_events


def create_json_calendar_events(calendar_url, events):
    event_data = []

    # Rename Calendar
    if calendar_url.startswith("https://outlook.office365.com"):
        calendar_name = "Office 365"
    elif calendar_url.startswith("https://calendar.google.com"):
        calendar_name = "Gmail"
    else:
        calendar_name = calendar_url

    try:
        for event in events:
            event_data.append(
                {
                    "Calendar": calendar_name,
                    "Event": str(event["SUMMARY"]),
                    "Start": str(
                        event["DTSTART"].dt.astimezone(pytz.timezone(TIMEZONE))
                    ),
                    "End": str(event["DTEND"].dt.astimezone(pytz.timezone(TIMEZONE))),
                }
            )
    except AttributeError:
        pass
        # print("Event had an error")

    return event_data


def todays_events():
    data = []
    for i in CALENDARS:
        data += get_event(i)

    for event in data:
        try:
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
        except ValueError:
            continue

    sorted_events = sorted(
        data, key=lambda x: parser.parse(x["Start"]).astimezone(pytz.utc)
    )

    return sorted_events


def main():
    upcoming_event = next_event(todays_events())
    if upcoming_event["Event"] == "None":
        print("None")
    else:
        print(
            f"{arrow.get(upcoming_event['Start']).format('HH:mm')}: {upcoming_event['Event']}"
        )


if __name__ == "__main__":
    main()

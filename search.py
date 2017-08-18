#!/usr/bin/env python3

"""Search for available FP+ times for a given ride."""

import os
import re
import io
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

RIDE = os.environ['RIDE']
PARK = os.environ['PARK']
DATE = os.environ['DATE']


def fetch_avail():
    """Fetch and return available time list for RIDE from touringplans.com"""
    req = requests.get(
        "https://touringplans.com/%s/fastpass-availability/date/%s" %
        (PARK, DATE))

    html_doc = req.text

    soup = BeautifulSoup(html_doc, 'html.parser')

    for elem in soup(text=re.compile(RIDE)):
        ride_el = elem

    for parent in ride_el.parents:
        if parent.name == "tr":
            fp_row = parent
            break

    return fp_row.find_all("td")[1].text.strip()


def did_change(avail):
    """Check cache and return if available times changed."""
    try:
        file = io.open("prev/%s.txt" % (RIDE), "r", encoding='utf8')
    except FileNotFoundError:
        prev = ""
    else:
        prev = file.read()
        file.close()

    return prev != avail


def cache(avail):
    """Cache available times."""
    io.open("prev/%s.txt" % (RIDE), "w", encoding='utf8').write(avail).close()


def send_message(avail):
    """Send a SMS message with available times."""
    client = Client()

    message_body = """FP+ found!
    %s, %s

    %s
    https://disneyworld.disney.go.com/fastpass-plus/""" % (RIDE, DATE, avail)

    client.messages.create(to=os.environ['TO_PHONE'],
                           from_=os.environ['FROM_PHONE'],
                           body=message_body)

    print("message sent!")


def main():
    """Find available FP times and notify user if they changed."""
    print("""STARTING SEARCH
    Park: %s
    Ride: %s
    Date: %s
    Current time: %s""" % (PARK, RIDE, DATE, str(datetime.now())))

    avail = fetch_avail()

    print(avail)

    if not did_change(avail):
        print("same as it ever was")
        exit(0)

    print("new!!!")

    cache(avail)


if __name__ == "__main__":
    main()

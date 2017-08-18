#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv
import os
import re
import io
from datetime import datetime

load_dotenv(find_dotenv())

RIDE = os.environ['RIDE']
PARK = os.environ['PARK']
DATE = os.environ['DATE']

print("""STARTING SEARCH
Park: %s
Ride: %s
Date: %s
Current time: %s""" % (PARK, RIDE, DATE, str(datetime.now())))

r = requests.get("https://touringplans.com/%s/fastpass-availability/date/%s" % (PARK, DATE))

html_doc = r.text

soup = BeautifulSoup(html_doc, 'html.parser')

for elem in soup(text=re.compile(RIDE)):
    el = elem

for parent in el.parents:
    if parent.name == "tr":
        p = parent
        break

fp = p.find_all("td")[1].text.strip()

print(fp)

try:
    f = io.open("prev/%s.txt" % (RIDE), "r", encoding='utf8')
except FileNotFoundError:
    prev = ""
else:
    prev = f.read()
    f.close()

print(prev)

if prev == fp:
    print("same as it ever was")
    exit(0)

print("new!!!")

f = io.open("prev/%s.txt" % (RIDE), "w", encoding='utf8')
f.write(fp)
f.close()

client = Client()

message_body = """FP+ found!
%s, %s

%s
https://disneyworld.disney.go.com/fastpass-plus/""" % (RIDE, DATE, fp)

client.messages.create(to=os.environ['TO_PHONE'], \
                       from_=os.environ['FROM_PHONE'], \
                       body=message_body)

print("message sent!")





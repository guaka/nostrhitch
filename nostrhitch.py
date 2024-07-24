#!/usr/bin/env
import os
import sys
import time
import uuid
import requests
import sqlite3

from datetime import datetime
from pprint import pprint

from pynostr.key import PrivateKey
from pynostr.relay_manager import RelayManager
from pynostr.event import Event, EventKind

from openlocationcode import openlocationcode
import geohash2

from settings import nsec


def download_file(url, filename):
    print ("Downloading", url)
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print('File saved as ', filename)
    else:
        print("Failed to fetch the page, status code:", response.status_code)

def fetch_data_from_db(filename, query):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    print (query)
    cursor.execute(query)

    results = cursor.fetchall()
    np = NostrPost()

    for row in results:
        np.post(row)
    np.close()
    
    conn.close()
    

def main():
    today = datetime.today().strftime('%Y-%m-%d')
    filename = f'hitchmap_{today}.sqlite'
    url = 'https://hitchmap.com/dump.sqlite'
    print ("nostr hitch: putting hitchmap data into nostr, and thus on notes.trustroots.org")

    if not os.path.exists(filename):
        download_file(url, filename)
    else:
        print(f"File '{filename}' already exists.")

    query = f"SELECT * FROM points WHERE datetime > '{today}'"
    fetch_data_from_db(filename, query)

class NostrPost:
    def __init__(self):
        private_key_obj = PrivateKey.from_nsec(nsec)
        self.private_key_hex = private_key_obj.hex()
        npub = private_key_obj.public_key.bech32()
        print(f"Posting as npub {npub}")

        self.relay_url = "wss://nos.lol"

        # Initialize the relay manager
        self.relay_manager = RelayManager(timeout=5)
        self.relay_manager.add_relay(self.relay_url)

    def post(self, hitchnote):
        print(hitchnote)
        # (8820951577709421825, 22.616731011815194, 121.00915170046848, 5.0, 'TW', 3.0, None, 'Easy spot to get pickup to taitung city directions.', '2023-07-23 01:09:07.200078', 0, 0, '', 22.616731011815194, 121.00915170046848, None)
        # (8565933277527005132, 43.891100365756145, 10.824542641639711, 5.0, 'IT', 10.0, 'hiker', 'perfect spot, got a ride to Massa very fast', '2023-07-23 10:05:52.361882', 0, 0, '', 43.92799682112012, 10.224226713180544, None)
        col1, start_lat, start_lng, rating, country, col6, hitchhiker_name, desc, datetime, col10, col11, end_lat, end_lng, col13, col14 = hitchnote

        if not hitchhiker_name:
            hitchhiker_name = ''
        event_content = f"hitchmap.com {hitchhiker_name}: {desc}"
        event_kind = 397 # notes.trustroots.org      # EventKind.TEXT_NOTE

        pluscode = openlocationcode.encode(start_lat, start_lng)
        geohash = geohash2.encode(start_lat, start_lng)
        # geohash = ...
        event = Event(kind=event_kind, content=event_content, tags=
                      [ 
                       ['L', "open-location-code"],
                       ['l', pluscode, "open-location-code"],
                       ['g', geohash],
                       ['t', 'hitchmap' ],
                       ['t', 'map-notes' ],
                        ]);
        # todo: ['created_at', timestamp] with datetime from hitchmap date
        
        event.sign(self.private_key_hex)
        pprint(vars(event))

        if False:
            self.relay_manager.publish_event(event)
            self.relay_manager.run_sync()  # Synchronize with the relay to send the event

        # Wait a bit to ensure the message has been sent
        time.sleep(5)

    def close():
        self.relay_manager.close_all_relay_connections()

if __name__ == "__main__":
    main()


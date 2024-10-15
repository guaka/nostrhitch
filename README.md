# nostrhitch

Some python code to fetch hitchmap.com's sqlite dump and post data as nostr notes.
These notes should show up in https://notes.trustroots.org/


## Setup

    cp settings.py.example settings.py

Add your `nsec` to `settings.py`.


On Debian/Ubuntu you might need this:

    apt install python3.XX-venv


Set up the virtual environment:

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements

Run it:

    python nostrhitch.py
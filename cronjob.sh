#!/bin/bash

cd $(dirname $0)

source venv/bin/activate

python nostrhitch.py >> nostrhitch.log 2>&1

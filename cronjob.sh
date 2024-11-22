#!/bin/bash

cd $(dirname $0)

source venv/bin/activate

date >> nostrhitch.log
echo "RUNNING cronjob.sh" >> nostrhitch.log
python nostrhitch.py >> nostrhitch.log 2>&1

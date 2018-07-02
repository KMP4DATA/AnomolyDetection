#!/bin/bash

batch_freq=10000
stream_freq = 1000


echo BASH run.sh script
echo Starting main program using frequency $freq



python ./src/main.py ./log_input/batch_log.json ./log_input/stream_log.json ./log_output/flagged_purchases.json $freq


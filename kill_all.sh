#!/bin/bash


echo "Stopping HTTP server..."
pkill -f "http.server 8000"

echo "Stopping Discord bot..."
pkill -f "/home/server/studio/main.py"

echo "Stopping BLE scanner..."
pkill -f "/home/server/studio/ble_scan.py"

# echo "Stopping sound script..." >> $LOG_FILE
# pkill -f "/home/server/studio/microphone/sound.py"

echo "Stopping noip2..."
pkill -f "/usr/local/bin/noip2"

echo "Stop script execution completed."

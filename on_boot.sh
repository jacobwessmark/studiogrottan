#!/bin/bash

# Wait for the network to be up
until ping -c1 www.google.com &>/dev/null; do
    echo "Waiting for network..."
    sleep 1
done

echo "Network is up, continuing with startup processes."

sleep 120

export PATH=/usr/bin:/bin:/sbin:/usr/sbin:/usr/local/bin
cd /home/server/studio

sudo /bin/python -m http.server 8000 &

sudo /bin/python /home/server/studio/main.py &

sudo /bin/python /home/server/studio/ble_scan.py &

# Uncomment if needed
# sudo /bin/python /home/server/studio/microphone/sound.py &

sudo /usr/local/bin/noip2 &
 
sudo /bin/python /home/server/studio/monitor.py &

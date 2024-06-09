# main.py
from led import LEDControl
from mqtt import MQTTClientSetup
import time
from wifi import WiFiManager
from config import LED_PIN, NUM_LEDS
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("logg")

# Initialize WiFi Manager
wifi = WiFiManager(logger=logger)

# Attempt to connect to WiFi
try:
    wifi.connect()
    logger.info("Connected to WiFi")
except Exception as e:
    logger.error("Failed to connect to WiFi: %s", str(e))

# Initialize LED control
led_control = LEDControl(pin=LED_PIN, num_leds=NUM_LEDS, logger=logger)

# Initialize MQTT client with a reference to the LED control and WiFi
mqtt_client = MQTTClientSetup(led_control=led_control, logger=logger, wifi=wifi)

heartbeat_interval = 10  # seconds
last_heartbeat_time = time.time()

# Main loop
while True:
    try:
        mqtt_client.check_messages()
    except Exception as e:
        logger.error("Error checking messages: %s", str(e))
    
    # Check if it's time to send a heartbeat
    current_time = time.time()
    if current_time - last_heartbeat_time >= heartbeat_interval:
        try:
            mqtt_client.send_heartbeat()
            last_heartbeat_time = current_time
        except Exception as e:
            logger.error("Error sending heartbeat: %s", str(e))
    
    try:
        mqtt_client.manage_heartbeat()  # This will check if it's time to send another heartbeat
    except Exception as e:
        logger.error("Error managing heartbeat: %s", str(e))
    
    time.sleep(0.1)

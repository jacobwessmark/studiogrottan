# mqtt.py
from umqtt.simple import MQTTClient
import machine
import time
from config import MQTT_BROKER, CLIENT_ID, TOPICS, SERVER_URL, FILES
from updater import OTAUpdater
import logging

# 


class MQTTClientSetup:
    def __init__(self, led_control, logger=None, wifi=None):
        self.wifi = wifi
        self.logger = logger or logging.getLogger(__name__)
        self.client = MQTTClient(CLIENT_ID, MQTT_BROKER)
        self.led_control = led_control
        self.client.set_callback(self.internal_callback)
        self.connect_and_subscribe()
        self.last_heartbeat_time = time.time()
        self.ota_updater = OTAUpdater(self.client, SERVER_URL, FILES)
        self.heartbeat_interval = 15  # seconds

    def reconnect(self):
        """Disconnects current MQTT client and establishes a new connection."""
        try:
            self.client.disconnect()
        except Exception as e:
            self.logger.error("Error disconnecting MQTT client: %s", str(e))
        
        # Create a new MQTT client instance
        self.client = MQTTClient(CLIENT_ID, MQTT_BROKER)
        self.client.set_callback(self.internal_callback)
        self.last_heartbeat_time = time.time()
        
        # Reconnect and subscribe to topics
        self.connect_and_subscribe()

    def connect_and_subscribe(self):
        """ Attempts to connect to the MQTT broker and subscribe to topics. """
        if self.wifi and not self.wifi.check_status():
            self.logger.warning("Cannot connect to MQTT because WiFi is down.")
            return
        try:
            self.client.connect(clean_session=True)
            for topic in TOPICS:
                self.client.subscribe(topic)
            self.logger.info("MQTT broker connected and subscribed.")
        except Exception as e:
            self.logger.error("Failed to connect and subscribe to MQTT: %s", str(e))
            time.sleep(5)
            self.reconnect() 

    def check_messages(self):
        """ Checks for new MQTT messages. """
        try:
            self.client.check_msg()
        except Exception as e:
            self.logger.error("Error checking messages: %s", str(e))
            self.last_heartbeat_time = 0  # Reset timer to force a heartbeat check

    def manage_heartbeat(self):
        """Manages the MQTT connection."""
        current_time = time.time()
        time_since_last_heartbeat = current_time - self.last_heartbeat_time
        
        if time_since_last_heartbeat > self.heartbeat_interval:
            self.logger.info("Time to check MQTT connection and subscribe...")
            self.reconnect()  # Reconnect if necessary


    def send_heartbeat(self):
        """ Sends a heartbeat message to ensure the MQTT connection is alive. """
        try:
            self.publish("ledfloor", "heartbeat")
            self.logger.info("Heartbeat sent")
        except Exception as e:
            self.logger.error("Failed to send heartbeat: %s", str(e))
            self.reconnect() 

    def publish(self, topic, msg):
        """ Publishes a message to a specific MQTT topic. """
        try:
            self.client.publish(topic, msg)
        except Exception as e:
            self.logger.error("Publish failed, error: %s", str(e))
            self.reconnect() 

    def internal_callback(self, topic, msg):
        """ Handles incoming MQTT messages with error handling. """
        self.last_heartbeat_time = time.time()  # Reset timer upon any valid message
        try:
            msg = msg.decode()
            self.logger.debug("Received message on %s: %s", topic, msg)
            if topic == b'ledfloor':
                commands = msg.split(',')
                if len(commands) == 4:
                    mode, r, g, b = commands
                    self.led_control.set_color(int(r), int(g), int(b))
                    self.led_control.set_mode(mode)
                elif len(commands) == 1:
                    if commands[0] == "reboot":
                        self.reboot()
                    elif commands[0] == "update":
                        self.update()
        except Exception as e:
            self.logger.error("Failed to process message: %s", str(e))

    def is_connected(self):
        """ Checks if the last message or heartbeat was within the allowable interval. """
        return time.time() - self.last_heartbeat_time <= self.heartbeat_interval

    def reboot(self):
        """ Reboots the microcontroller. """
        self.logger.info("Rebooting the microcontroller")
        self.publish("ledfloor", "Rebooting LED driver")
        time.sleep(1)
        machine.reset()

    def update(self):
        """ Updates firmware based on commands received over MQTT. """
        self.logger.info("Updating firmware")
        self.publish("ledfloor", "Updating firmware")
        self.ota_updater.update_firmware()

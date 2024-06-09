# wifi.py
import network
from config import WIFI_SSID, WIFI_PASSWORD
import time
import logging

class WiFiManager:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.connected = False
        self.connect()

    def connect(self):
        """Attempts to connect to the WiFi synchronously."""
        try:
            self.wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            attempt = 0
            while not self.wlan.isconnected() and attempt < 10:
                time.sleep(1)
                attempt += 1
                self.logger.info(f'Attempt {attempt}: Connecting to WiFi...')
            if self.wlan.isconnected():
                self.logger.info('WiFi connected successfully')
                self.connected = True
            else:
                self.logger.error('Failed to connect to WiFi after multiple attempts')
                self.connected = False
        except Exception as e:
            self.logger.error(f'WiFi connection error: {str(e)}')
            self.connected = False

    def check_status(self):
        """Checks the current WiFi connection status and tries reconnecting if necessary."""
        if self.wlan.isconnected():
            if not self.connected:  # Was previously disconnected
                self.logger.info('WiFi reconnected successfully')
            self.connected = True
        else:
            self.connected = False
            self.logger.warning('WiFi is currently disconnected. Attempting to reconnect...')
            self.connect()  # Try to reconnect
        return self.connected



import subprocess
import re
import time
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import User
import paho.mqtt.publish as publish
import logging

class ArpPresenceScanner:
    def __init__(self, host=None, topic=None, interface=None, interval=5, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.broker_address = host
        self.topic = topic
        self.interface = interface
        self.interval = interval
        self.last_seen = {}
        self.timeout = 600  # 10 minutes

        DATABASE_URI = "postgresql://postgres:secret@localhost:5432/studiodb"
        engine = create_engine(DATABASE_URI)
        self.session_factory = sessionmaker(bind=engine)
        self.session = scoped_session(self.session_factory)

        self.reset_all_users_presence()

    def reset_all_users_presence(self):
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                with self.session.begin():
                    all_users = self.session.query(User).all()
                    for user in all_users:
                        user.presence = False
                self.logger.info("All user presences have been reset to False.")
                return  # Exit after success
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1}: Error resetting user presence: {e}", exc_info=True)
                time.sleep(2)
        self.logger.error("Failed to reset user presence after several attempts.")

    def is_interface_ready(self):
        while True:
            self.logger.debug(f"Checking if interface {self.interface} is ready.")
            try:
                ip_output = subprocess.check_output(['ip', 'addr', 'show', self.interface], encoding='utf-8')
                if 'state UP' in ip_output and 'inet ' in ip_output:
                    self.logger.debug(f"Interface {self.interface} is ready with IP.")
                    return True
                else:
                    self.logger.debug(f"Interface {self.interface} is not ready or has no IP.")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to get IP address for {self.interface}: {e.output}")
            except Exception as e:
                self.logger.error(f"Unexpected error when checking interface {self.interface}: {e}", exc_info=True)
            time.sleep(10)  # wait before retrying to avoid spamming and give time for recovery

    def scan_network(self):
        while True:  # Keep trying indefinitely
            self.logger.debug("Starting network scan.")
            if self.is_interface_ready():
                try:
                    output = subprocess.check_output(
                        ['arp-scan', '--interface', self.interface, '--localnet'], encoding='utf-8')
                    mac_addresses = set(re.findall(r"\b(?:[a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}\b", output))
                    print(mac_addresses)
                    self.logger.debug(f"ARP scan successful, found addresses: {mac_addresses}")
                    return mac_addresses
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"ARP scan failed: {e.output}")
                except Exception as e:
                    self.logger.error(f"General error during network scan: {e}", exc_info=True)
            else:
                self.logger.debug("Network interface not ready for scanning.")
            time.sleep(10)  # Wait before next check

    def update_presence(self):
        current_macs = self.scan_network()
        print(current_macs)
        current_time = time.time()
        if not current_macs:
            return  # Early return if scan fails

        try:
            with self.session.begin():
                all_users = self.session.query(User).all()
                for user in all_users:
                    user_present = any(mac in current_macs for mac in user.mac_addresses)
                    if user_present:
                        if not user.presence:
                            user.presence = True
                            self.send_mqtt_message(user)
                    elif all(current_time - self.last_seen.get(mac, 0) > self.timeout for mac in user.mac_addresses):
                        if user.presence:
                            user.presence = False
                            self.send_mqtt_message(user)
                    self.last_seen.update((mac, current_time) for mac in current_macs)
        except Exception as e:
            self.logger.error("Error updating user presence", exc_info=True)

    def send_mqtt_message(self, user):
        try:
            message = f"{user.name} {'logged in' if user.presence else 'logged out'}"
            publish.single(self.topic, message, hostname=self.broker_address)
        except Exception as e:
            self.logger.error(f"Error sending MQTT message: {e}", exc_info=True)

    def send_periodic_message(self):
        while True:
            try:
                message = "arpbeat"
                publish.single(self.topic, message, hostname=self.broker_address)
                self.logger.info("Sent periodic MQTT message.")
            except Exception as e:
                self.logger.error(f"Error sending periodic MQTT message: {e}", exc_info=True)
            time.sleep(120)

    def start_loop(self):
        def loop():
            while True:
                self.update_presence()
                time.sleep(self.interval)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
        self.logger.info("Background presence update loop started.")

        periodic_thread = threading.Thread(target=self.send_periodic_message, daemon=True)
        periodic_thread.start()
        self.logger.info("Background periodic message loop started.")

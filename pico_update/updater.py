# updater.py
import urequests
from config import TOPICS
import machine

class OTAUpdater:
    def __init__(self, mqtt_client, SERVER_URL, FILES):
        self.mqtt_client = mqtt_client
        self.server_url = SERVER_URL
        self.files = FILES

    def update_firmware(self):
        # Publishing initial update message
        self.mqtt_client.publish(TOPICS[1], "Updating firmware")

        for file in self.files:
            try:
                response = urequests.get(f"{self.server_url}{file}")
                if response.status_code == 200:
                    with open(file, 'w') as f:
                        f.write(response.text)
                    self.mqtt_client.publish(TOPICS[1], f"Updated {file} successfully")
                else:
                    self.mqtt_client.publish(TOPICS[1], f"Failed to download {file}. Status code: {response.status_code}")
                response.close()
            except Exception as e:
                self.mqtt_client.publish(TOPICS[1], f"Exception updating {file}: {str(e)}")

        self.mqtt_client.publish(TOPICS[1], "Rebooting LED driver")
        machine.reset()

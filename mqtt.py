#mqtt.py
import paho.mqtt.client as mqtt
import logging
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from models import User

# Setup logging for MQTT client
logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self, broker, port=1883, message_callback=None):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected successfully to MQTT Broker")
        else:
            logger.error("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, message):

        if self.message_callback:
            self.message_callback(message.topic, message.payload.decode())

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.warning("Unexpected disconnection. Trying to reconnect...")
            self.connect()  # Attempt to reconnect

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error("Failed to connect to MQTT Broker: %s", str(e), exc_info=True)

    def subscribe(self, topic):
        try:
            self.client.subscribe(topic)
            logger.info(f"Subscribed to topic '{topic}'")
        except Exception as e:
            logger.error("Failed to subscribe to topic '{topic}': {e}")

    def publish(self, topic, message):
        try:
            self.client.publish(topic, message)
            logger.info(f"Published message to topic '{topic}'")
        except Exception as e:
            logger.error(f"Failed to publish message to topic '{topic}': {e}")


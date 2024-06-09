import paho.mqtt.client as mqtt
import random
import time
import math

# Define callback functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_publish(client, userdata, mid):
    print("Message published")

# Create MQTT client instance
client = mqtt.Client()

# Assign callback functions
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to localhost MQTT broker
client.connect("localhost", 1883, 60)

# client.publish("test", "temperature,host=server01,region=us-west value=82.0")
# create a loop where it once every second sends a different example value of the temperature. 

# Construct the message with the example temperature valu
#message = f"temperature,host=server01,region=us-west value={temperature}"
# temperature,host=server01,region=us-west value=82.0

# Publish the message to the MQTT topic
client.publish("logged_in", "test")


# Keep the client running to ensure message publishing
client.loop_forever()
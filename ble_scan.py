import asyncio
import time
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import BLEScanData  # Adjust the import as necessary to match your project structure
from bleak import BleakScanner
import paho.mqtt.publish as publish
import logging

# Assuming you have your database URI set up
DATABASE_URI = "postgresql://postgres:secret@localhost:5432/studiodb"
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

# Define maximum retries and delay between retries
MAX_RETRIES = 10
RETRY_DELAY = 10  # in seconds

async def scan_and_publish():
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            # Perform BLE scanning
            devices_found = await BleakScanner.discover()
            num_devices_found = len(devices_found)
            print(f"Devices found: {num_devices_found}")
            
            # Publish results to MQTT broker
            message = f"ble_devices,host=server01,region=us-west value={num_devices_found}"
            publish.single("ble_devices", message, hostname="localhost")
            return  # Return on success, which resets retry_count for the next call
        except Exception as e:
            logging.error(f"Failed to scan and publish: {e}")
            retry_count += 1
            print(f"Retry {retry_count}/{MAX_RETRIES}...")
            time.sleep(RETRY_DELAY)
    raise Exception("Max retries reached, unable to scan and publish")

async def scan_ble_devices():
    while True:
        total_devices_found = 0  # Initialize total count of devices found
        for _ in range(5):  # Perform 5 scanning cycles
            try:
                await scan_and_publish()
                time.sleep(30)
            except Exception as e:
                logging.error("Failed operation after max retries: {}".format(str(e)))
                # Handle failure after maximum retries here if necessary

# Run the scan_ble_devices function in an event loop
asyncio.run(scan_ble_devices())

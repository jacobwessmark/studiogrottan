import os
import discord
from discord_bot import MyBot
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from arp_scan import ArpPresenceScanner
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import subprocess

# Setup logging
log_file = "error_log.log"
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        RotatingFileHandler(log_file, maxBytes=100000, backupCount=5),
                        logging.StreamHandler()
                    ])

logger = logging.getLogger(__name__)

# Set up database
DATABASE_URI = "postgresql://postgres:secret@localhost:5432/studiodb"
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Load environment variables
try:
    load_dotenv()  # Load environment variables from .env file
    presence_tracker = ArpPresenceScanner(host="localhost", topic="logged_in", interface="wlan0")
    presence_tracker.start_loop()
except Exception as e:
    logger.error("Failed to load environment variables: %s", str(e))


def setup_mqtt_callback(bot):
    try:
        # Ensure the lambda function passes both topic and payload to handle_mqtt_message
        bot.mqtt_client.client.on_message = lambda client, userdata, message: bot.handle_mqtt_message(message.topic, message.payload.decode())
    except Exception as e:
        logger.error("Failed to set up MQTT callback: %s", str(e))



def start_discord_bot():
    discord_channels = [
        os.getenv('PEOPLE_IN_STUDIO'),
        os.getenv('STUDIO_CONTROLLER')
    ]

    if None in discord_channels:
        logger.error("One or more Discord channel IDs are not set in environment variables.")

    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    mqtt_port = int(os.getenv('MQTT_PORT', '1883'))

    bot = MyBot(
        mqtt_broker=os.getenv('MQTT_BROKER_ADDRESS'),
        mqtt_port=mqtt_port,
        discord_channels=discord_channels,
        session=session,
        intents=intents
    )




    retry_interval = 10  # seconds to wait before retrying
    max_retries = 5  # maximum number of retries
    attempt = 0

    while attempt < max_retries:
        try:
            setup_mqtt_callback(bot)
            bot.run(os.getenv('DISCORD_TOKEN'))
            break  # Exit loop if connection is successful
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}: An error occurred during bot setup or execution: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
                attempt += 1
            else:
                logger.error("Max retries reached, failed to start the Discord bot.")
                subprocess.run(["sudo", "reboot"], check=True)
                raise

# Start the bot with retry logic
try:
    start_discord_bot()
except Exception as final_exception:
    logger.critical("Unable to start the Discord bot after multiple retries.", exc_info=True)

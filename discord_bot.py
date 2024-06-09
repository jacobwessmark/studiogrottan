#discord_bot.py
import discord
from mqtt import MQTTClient
import os
import asyncio
import logging
from sqlalchemy.orm import scoped_session
from models import User
from topics import TOPICS

# Setup logging
logger = logging.getLogger(__name__)

class MyBot(discord.Client):
    def __init__(self, mqtt_broker, mqtt_port, discord_channels, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mqtt_client = MQTTClient(mqtt_broker, mqtt_port, self.handle_mqtt_message)
        self.discord_channels = {channel: None for channel in discord_channels}
        self.session = session
        self.topics = TOPICS
        self.debug = False

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        try:
            self.mqtt_client.connect()

            for topic in self.topics:
                self.mqtt_client.subscribe(topic)

            #self.mqtt_client.subscribe('discord_channel')
            #self.mqtt_client.subscribe('logged_in')
        
            for channel_id in self.discord_channels:
                try:
                    channel = await self.fetch_channel(int(channel_id))
                    self.discord_channels[channel_id] = channel
                    logger.info(f"Channel {channel_id} fetched successfully.")
                except TypeError as e:
                    logger.error(f"Error: Invalid channel ID '{channel_id}': {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error fetching channel {channel_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error during MQTT setup: {str(e)}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content == "mqttON":
            self.debug = True
            await message.channel.send("Debug mode enabled.")
            return
        elif message.content == "mqttOFF":
            self.debug = False
            await message.channel.send("Debug mode disabled.")
            return
        

        if self.debug == True:

            # Handling messages from the `studio_controller` to publish to MQTT
            if message.channel.id == int(os.getenv('STUDIO_CONTROLLER')):
                try:
                    # Check if the message is intended for a specific MQTT topic
                    if '/' in message.content:
                        topic, mqtt_message = message.content.split('/', 1)
                        self.mqtt_client.publish(topic, mqtt_message)
                        logger.info(f"Published to MQTT topic {topic}: {mqtt_message}")
                except Exception as e:
                    logger.error(f"Failed to publish message to MQTT: {str(e)}")
        
        else:
            await message.channel.send("Debug mode is disabled. Please enable debug mode to send MQTT messages.")   


    async def purge_and_send_message(self, channel, message, names):
        """Purges the channel and then sends a message."""
        try:
            await channel.purge(limit=100)  # Purge messages
            logger.info(f"Purged messages in {channel.name}.")

            people_in_studio = None
            
            if names:
                people_in_studio = "```People in the studio:\n" + "\n".join(names) + "```"
            else:
                people_in_studio = "```The studio is free atm.```"

            await channel.send(people_in_studio)  # Send message after purge
            logger.info(f"Message sent to {channel.name} after purge.")
        except Exception as e:
            logger.error(f"Failed to purge or send message in {channel.name}: {str(e)}")

    def handle_mqtt_message(self, topic, payload):
        people_in_studio_channel = self.discord_channels[os.getenv('PEOPLE_IN_STUDIO')]
        studio_controller_channel = self.discord_channels[os.getenv('STUDIO_CONTROLLER')]
        
        if self.debug:

            if studio_controller_channel:   
                message_content = f"**Topic:** {topic}\n**Message:** {payload}"
                asyncio.run_coroutine_threadsafe(studio_controller_channel.send(message_content), self.loop)


        if topic == "logged_in":
            all_users = self.session.query(User).all()
            names = [user.name for user in all_users if user.presence]
            if people_in_studio_channel:
                # Schedule the purge and send operation as a single coroutine
                asyncio.run_coroutine_threadsafe(
                    self.purge_and_send_message(people_in_studio_channel, payload, names), self.loop)
        

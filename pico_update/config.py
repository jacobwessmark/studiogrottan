
# config.py
WIFI_SSID = 'studio'
WIFI_PASSWORD = 'pongolapava'
MQTT_BROKER = '192.168.0.12'
CLIENT_ID = 'pico_wh'
NUM_LEDS = 600
FLOOR_LEDS = 250
LED_PIN = 5
FLOOR_PIN = 6
SERVER_URL = "http://192.168.0.12:8000/pico_update/"
FILES = ["main.py", "config.py", "wifi.py", "mqtt.py", "led.py", "updater.py"]



TOPICS = ["leddriver/control", "leddriver/debug", "floorled"] 

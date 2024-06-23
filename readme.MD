# StudioGrottan

## Introduction
StudioGrottan is an innovative project aimed at creating a functional and automated working environment for music and electronics/programming. It integrates various sensors and actuators using IoT principles to monitor, document, and control different aspects of a music studio.

## Project Overview
The core of the system is a Raspberry Pi 4, which acts as the central unit, handling communication with multiple devices and sensors. The system includes Zigbee devices, BLE scanning, and various sensors to optimize the studio environment.

## Features
- **MQTT Communication**: Utilizes MQTT protocol for efficient communication between devices.
- **Discord Integration**: Custom Discord bot for user interaction and monitoring.
- **BLE Scanning**: Monitors the presence of BLE devices to estimate the number of people.
- **ARP-Scan**: Identifies connected devices on the network to log presence.
- **Home Assistant**: Integrates and automates various smart devices in the studio.

## Hardware
- **Raspberry Pi 4**: Central unit handling overall system management.
- **Sonoff Zigbee Antenna**: Manages communication with Zigbee devices.
- **WS2812B LED Strips**: Controlled by Raspberry Pi Pico for visual feedback.
- **Xiaomi Temperature and Humidity Sensor**: Monitors environmental conditions.
- **4G-WiFi Router**: Provides internet access and network connectivity.

## Software
- **Python**: Core programming language for scripts and bot.
- **MQTT Broker (Mosquitto)**: Handles message passing between devices.
- **Discord Bot**: Facilitates interaction and monitoring via Discord.
- **Home Assistant**: Manages smart devices and automation.

## Installation
1. **Clone the repository**:
    ```bash
    git clone https://github.com/jacobwessmark/studiogrottan.git
    cd studiogrottan
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up MQTT Broker**:
    Follow the [Mosquitto installation guide](https://mosquitto.org/man/mosquitto-8.html) to set up your MQTT broker.

4. **Configure Home Assistant**:
    Install Home Assistant on your Raspberry Pi and set up the required integrations. Refer to the [Home Assistant installation guide](https://www.home-assistant.io/getting-started/).

5. **Run the application**:
    ```bash
    python main.py
    ```

## Usage

### Discord Bot
The Discord bot provides various commands to interact with the system:
- **!status**: Check the current status of the studio.
- **!whois**: See who is currently in the studio.

### MQTT
The system uses MQTT for inter-device communication. Ensure your devices are configured to connect to the MQTT broker and subscribe to the necessary topics.

### BLE Scanning
The BLE scanner runs on the Raspberry Pi 4 and sends data to the MQTT broker. This data is then visualized using Grafana.

## Contributions
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact
For any questions or suggestions, please contact jacobwessmark at github.

---

You are currently on the free plan, which is significantly limited by the number of requests. To increase your quota, you can check available plans following this [link](https://c7d59216ee8ec59bda5e51ffc17a994d.auth.portal-pluginlab.ai/pricing).

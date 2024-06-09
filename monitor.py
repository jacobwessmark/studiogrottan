import psutil
import subprocess
import time
import requests
import socket
import logging

# Configure logging
logging.basicConfig(filename='system_monitor.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

def clear_system_cache():
    try:
        subprocess.run(['sync'])
        subprocess.run('echo 3 > /proc/sys/vm/drop_caches', shell=True, check=True)
        logging.info("System cache cleared.")
    except Exception as e:
        logging.error(f"Failed to clear system cache: {e}")

def check_interface(interface='wlan0'):
    """ Check if network interface is up """
    try:
        status_output = subprocess.check_output(['ip', 'link', 'show', interface])
        if 'state UP' in status_output.decode():
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to check network interface {interface}: {e}")
        return False

def restart_network_interface(interface='wlan0'):
    """Restart the network interface using nmcli."""
    try:
        # Disconnect and then reconnect the interface
        subprocess.run(['nmcli', 'device', 'disconnect', interface], check=True)
        subprocess.run(['nmcli', 'device', 'connect', interface], check=True)
        logging.info(f"Network interface {interface} restarted successfully using nmcli.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to restart network interface {interface} using nmcli: {e}")


def log_process_memory():
    """ Logs memory usage for each process and returns a list of high memory processes """
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            proc_info = proc.as_dict(attrs=['pid', 'name', 'memory_percent'])
            if proc_info['memory_percent'] > 20:
                clear_system_cache()

                logging.info(f"High memory usage: PID={proc_info['pid']}, Name={proc_info['name']}, Usage={proc_info['memory_percent']}%")
            processes.append(proc_info)  # Append process info regardless of condition
    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
        logging.error(f"Error accessing process information: {e}")
    return processes  # Always return a list, even if it's empty

def get_memory_usage():
    """ Get memory stats """
    memory = psutil.virtual_memory()
    return {
        'total': memory.total,
        'available': memory.available,
        'percent': memory.percent,
        'used': memory.used,
        'free': memory.free
    }

def reboot_system():
    """ Reboot the system safely """
    try:
        logging.info("Initiating system reboot.")
        subprocess.run(['sudo', 'reboot'], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to reboot the system: {e}")


def check_internet():
    """ Check internet connectivity by pinging Google's DNS """
    try:
        subprocess.check_output(["ping", "-c", "1", "8.8.8.8"], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        restart_network_interface()  # Try to reset network interface if ping fails
        return False

def get_ip():
    """ Get local IP address """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
        s.close()
        return IP
    except Exception as e:
        logging.error(f"Failed to get IP address: {e}")
        return 'N/A'

def get_wifi_details():
    """ Get WiFi connection details """
    try:
        response = requests.get('http://ip-api.com/json')
        data = response.json()
        return {
            'ip': data.get('query'),
            'isp': data.get('isp'),
            'country': data.get('country'),
            'region': data.get('regionName'),
            'city': data.get('city')
        }
    except requests.RequestException as e:
        logging.error(f"Failed to get WiFi details: {e}")
        return None

def main():
    while True:
        print("Checking memory and internet status...")
        mem_usage = get_memory_usage()
        print(f"Memory Usage: {mem_usage}")

        top_processes = log_process_memory()
        print("Top consuming processes:")
        for proc in top_processes:
            print(f"PID: {proc['pid']}, Name: {proc['name']}, Memory Usage: {proc['memory_percent']}%")

        if check_internet():
            print("Internet connection is UP.")
            print(f"Local IP: {get_ip()}")
            wifi_details = get_wifi_details()
            if wifi_details:
                print(f"WiFi Details: {wifi_details}")
        else:
            print("Internet connection is DOWN.")

        time.sleep(1000)  # Sleep for 1000 seconds = 16 minutes

if __name__ == "__main__":
    main()

import time
import os
import json
import logging

# Variables
INTERVAL = 60
IP_DEVICES = {}
AT_HOME = {}
MESSAGES = {}


def load_config():
    """
        Load config.json from root and
        return decoded JSON
    """
    try:
        with open("config.json") as config:
            config_file = json.load(config)
            return config_file
    except FileNotFoundError:
        logging.fatal("Failed to find config.jon file! Make sure to rename config.example.json to config.jon")
    except ValueError:
        logging.fatal("Malformed json schema in config.json")


def ping(interval):
    """
        Start pinging IP_DEVICES. This function pings
        all IP Devices specified in config.json after
        set interval. By default interval is set to 60 seconds
        which equals to 1 minute
    """
    while True:
        # Loop over all IP Devices
        for u in IP_DEVICES:
            # Check if IP Device is at home
            if u in AT_HOME:
                response = os.popen(f"ping {u}").read()
                if "Received = 4" in response and 'Destination host unreachable' not in response:
                    # IP Device is still reachable (Must be home?)
                    logging.info(MESSAGES['reachable'].format(IP_DEVICES[u]))
                else:
                    # IP Device has left home
                    # Delete IP Device from AT_HOME dictionary
                    del AT_HOME[u]
                    logging.info(MESSAGES['lost_connection'].format(IP_DEVICES[u]))
            else:
                # Check if IP Device got finally home?
                response = os.popen(f"ping {u}").read()
                if "Received = 4" in response and 'Destination host unreachable' not in response:
                    # Add IP Device to AT_HOME dictionary
                    AT_HOME[u] = IP_DEVICES[u]
                    logging.info(MESSAGES['reachable'].format(IP_DEVICES[u]))
                else:
                    logging.info(MESSAGES['unreachable'].format(IP_DEVICES[u]))

        # Let's not flood
        time.sleep(interval)


if __name__ == '__main__':
    try:
        # Configure logger
        logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)

        # Load config.json file
        config_json = load_config()

        # Get all IP Devices
        IP_DEVICES = config_json['ip_devices']

        # Get interval for ping
        INTERVAL = config_json['interval']

        # Get messages (logs)
        MESSAGES = config_json['messages']

        # Start application
        ping(INTERVAL)

    except Exception as e:
        logging.fatal("Failed to start app")


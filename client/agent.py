import time
import json

CONFIG_FILE = "form_data.json"

def load_config():
    """
    Načíta konfiguráciu.
    """
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def maintain_connection(config):
    """
    Simuluje udržiavanie spojenia so serverom.
    """
    print(f"Maintaining connection for device '{config['device_name']}' with MAC: {config['mac_address']}")
    while True:
        print("Connection alive...")
        time.sleep(10)

def main():
    """
    Spustí agenta.
    """
    config = load_config()
    maintain_connection(config)

if __name__ == "__main__":
    main()

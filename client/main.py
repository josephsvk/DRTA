import os
import subprocess
import json
import sys
import argparse

CONFIG_FILE = "form_data.json"

def run_form():
    """
    Spustí formulár pre nastavenie.
    """
    print("Running setup form...")
    subprocess.run([sys.executable, "form.py"], check=True)

def run_agent():
    """
    Spustí agenta na udržiavanie spojenia.
    """
    print("Starting agent...")
    subprocess.run([sys.executable, "agent.py"], check=True)

def run_register():
    """
    Spustí registračný skript.
    """
    print("Running registration script...")
    subprocess.run([sys.executable, "register.py"], check=True)

def load_config():
    """
    Načíta konfiguráciu z form_data.json.
    """
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file '{CONFIG_FILE}' not found.")
        return None

def validate_totp():
    """
    Validates the TOTP provided by the user.
    """
    totp = input("Enter the TOTP code: ")
    # Simulate TOTP validation
    if len(totp) == 6 and totp.isdigit():
        print("TOTP validated successfully.")
        return True
    else:
        print("Invalid TOTP. Please try again.")
        return False

def exchange_keys_with_server(config):
    """
    Pošle identitu agenta a prijíma ďalšie informácie zo serveru.
    """
    print("Exchanging keys and information with the server...")
    # Simulate server communication
    server_response = {
        "port": "12345",
        "ipv6": "fd:fc:fb:fa:0001::2"
    }
    config.update(server_response)

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    print("Registration complete. Server returned:")
    print(f"Port: {server_response['port']}")
    print(f"IPv6: {server_response['ipv6']}")

def main():
    """
    Hlavná logika pre rozhodovanie.
    """
    parser = argparse.ArgumentParser(description="Program for managing setup, agents, and registration.")
    parser.add_argument("--setup", action="store_true", help="Run the setup form.")
    parser.add_argument("--run", action="store_true", help="Run the agent.")
    parser.add_argument("--register", action="store_true", help="Run the registration script.")
    parser.add_argument("--idle", action="store_true", help="Run in idle mode (do nothing).")

    args = parser.parse_args()

    if args.setup:
        run_form()
        sys.exit()
    elif args.run:
        run_agent()
        sys.exit()
    elif args.register:
        run_register()
        sys.exit()
    elif args.idle:
        print("Idle mode activated. Container is running but not performing any tasks.")
        while True:
            pass  # Keeps the container running in idle mode

    print("No valid argument provided. Use --setup, --run, --register, or --idle.")
    sys.exit()

if __name__ == "__main__":
    main()

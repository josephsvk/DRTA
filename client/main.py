import os
import subprocess
import json

CONFIG_FILE = "form_data.json"

def run_form():
    """
    Spustí formulár pre nastavenie.
    """
    print("Running setup form...")
    subprocess.run(["python", "form.py"], check=True)

def run_agent():
    """
    Spustí agenta na udržiavanie spojenia.
    """
    print("Starting agent...")
    subprocess.run(["python", "agent.py"], check=True)

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

def main():
    """
    Hlavná logika pre rozhodovanie.
    """
    print("Starting main program...")
    config = load_config()
    
    if config:
        print("Configuration found. Starting agent...")
        run_agent()
    else:
        print("No configuration found. Starting setup...")
        run_form()

if __name__ == "__main__":
    main()

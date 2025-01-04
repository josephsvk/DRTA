import os
import subprocess
import json
import shutil

# Define the directory for SSH keys
SSH_DIR = os.path.join(os.getcwd(), ".ssh")

# Ensure the directory exists
def ensure_ssh_dir():
    """
    Create the SSH directory if it does not exist.
    Handles permissions and other exceptions during directory creation.
    """
    try:
        os.makedirs(SSH_DIR, exist_ok=True)
        print(f"[INFO] SSH directory ensured at: {SSH_DIR}")
    except PermissionError:
        print(f"[ERROR] Permission denied: Unable to create SSH directory at {SSH_DIR}")
    except Exception as e:
        print(f"[ERROR] Error creating SSH directory: {e}")

# Function to generate SSH key
def generate_ssh_key(filename, comment):
    """
    Generate an SSH key using ssh-keygen.

    :param filename: Name of the key file to be created.
    :param comment: Comment associated with the key for identification.
    """
    try:
        key_path = os.path.join(SSH_DIR, filename)
        print(f"[DEBUG] Generating SSH key at {key_path} with comment '{comment}'")
        key_cmd = ["ssh-keygen", "-t", "ed25519", "-C", comment, "-f", key_path, "-N", ""]
        subprocess.run(key_cmd, check=True)
        print(f"[INFO] SSH key generated and saved to {key_path}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error generating SSH key: {e}")

# Function to save data to a JSON file with backup
def save_to_json(data, filename="form_data.json"):
    """
    Save the given data to a JSON file.
    Creates a backup of the existing file if it exists.

    :param data: Data to save in JSON format.
    :param filename: Name of the JSON file to save to.
    """
    try:
        if os.path.exists(filename):
            backup_filename = filename + ".bak"
            shutil.copy(filename, backup_filename)
            print(f"[INFO] Backup of existing file created: {backup_filename}")
        
        print(f"[DEBUG] Saving data to {filename}")
        with open(filename, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"[INFO] Data saved to {filename}")
    except Exception as e:
        print(f"[ERROR] Error saving data: {e}")

# Function to load existing JSON configuration
def load_existing_json(filename="form_data.json"):
    """
    Load existing configuration data from a JSON file.

    :param filename: Name of the JSON file to load.
    :return: Loaded data or None if the file does not exist or an error occurs.
    """
    try:
        print(f"[DEBUG] Attempting to load existing configuration from {filename}")
        with open(filename, "r") as json_file:
            data = json.load(json_file)
            print(f"[INFO] Loaded existing configuration from {filename}")
            return data
    except FileNotFoundError:
        print(f"[INFO] No existing configuration found at {filename}.")
        return None
    except Exception as e:
        print(f"[ERROR] Error loading configuration: {e}")
        return None

# Step-by-step interactive form
def main():
    """
    Main function to guide the user through the agent setup process.
    Allows users to load existing configurations or create new ones.
    """
    print("[INFO] Welcome to the Agent Identity Setup!")
    print("Please follow the steps to configure the agent.")

    # Check for existing configuration
    existing_data = load_existing_json()
    if existing_data:
        use_existing = input("Found an existing configuration. Do you want to use it? (yes/no): ").strip().lower()
        if use_existing == "yes":
            print("[INFO] Using existing configuration.")
            print(json.dumps(existing_data, indent=4))
            return

    # Ensure SSH directory exists
    ensure_ssh_dir()

    device_name = input("Enter the device name: ")

    print("Select IPv6 prefix:")
    prefixes = ["fd:fc:fb:fa::/48", "fd:ab:cd:ef::/48", "Custom"]
    for i, prefix in enumerate(prefixes, start=1):
        print(f"{i}. {prefix}")
    prefix_choice = input("Enter your choice (1-3): ")
    if prefix_choice == "3":
        ipv6_prefix = input("Enter your custom IPv6 prefix: ")
    else:
        ipv6_prefix = prefixes[int(prefix_choice) - 1]

    port = input("Enter the port (default: 22): ") or "22"
    location = input("Enter the location: ")
    function = input("Enter the function: ")

    # Generate SSH key
    key_filename = f"{device_name}_id_ed25519"
    generate_ssh_key(key_filename, device_name)

    # Save data
    data = {
        "device_name": device_name,
        "ipv6_prefix": ipv6_prefix,
        "port": port,
        "location": location,
        "function": function
    }
    save_to_json(data)

    print("[INFO] Configuration completed!")
    print(f"Device Name: {device_name}")
    print(f"IPv6 Prefix: {ipv6_prefix}")
    print(f"Port: {port}")
    print(f"Location: {location}")
    print(f"Function: {function}")

if __name__ == "__main__":
    main()

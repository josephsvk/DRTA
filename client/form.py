import os
import subprocess
import json

# Function to get the MAC address
def get_mac_address():
    try:
        result = subprocess.run(
            "ip link | awk '/state UP/ {getline; print $2}'",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError:
        return None

# Function to generate SSH key
def generate_ssh_key(filename, comment):
    try:
        key_cmd = f'ssh-keygen -t ed25519 -C "{comment}" -f {filename} -N ""'
        subprocess.run(key_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error generating SSH key: {e}")

# Function to save data to a JSON file
def save_to_json(data, filename="form_data.json"):
    try:
        with open(filename, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving data: {e}")

# Step-by-step interactive form
def main():
    print("Welcome to the Agent Identity Setup!")
    print("Please follow the steps to configure the agent.")
    
    mac_address = get_mac_address()
    if not mac_address:
        print("Unable to retrieve MAC address.")
        mac_address = input("Please enter the MAC address manually: ")

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
    generate_ssh_key(key_filename, mac_address)

    # Save data
    data = {
        "mac_address": mac_address,
        "device_name": device_name,
        "ipv6_prefix": ipv6_prefix,
        "port": port,
        "location": location,
        "function": function
    }
    save_to_json(data)

    print("\nConfiguration completed!")
    print(f"MAC Address: {mac_address}")
    print(f"Device Name: {device_name}")
    print(f"IPv6 Prefix: {ipv6_prefix}")
    print(f"Port: {port}")
    print(f"Location: {location}")
    print(f"Function: {function}")
    print(f"SSH Key saved as: {key_filename}")

if __name__ == "__main__":
    main()

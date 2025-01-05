import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

def verify_totp():
    # Retrieve the TOTP URL from environment variables or use the default
    url = os.getenv("TOTP_URL", "https://localhost:8443/verify-totp")
    headers = {"Content-Type": "application/json"}  # Set the request headers

    while True:
        try:
            print(f"[DEBUG] Using TOTP URL: {url}")
            totp_code = input("Please enter your TOTP code: ")
            print(f"[DEBUG] Entered TOTP code: {totp_code}")

            # Prepare the payload to send in the request
            payload = {"code": totp_code}
            print(f"[DEBUG] Payload prepared: {payload}")

            # Send a POST request to the TOTP verification endpoint
            response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)  # Added verify=False for testing
            print(f"[DEBUG] Response status: {response.status_code}, Response text: {response.text}")

            # Handle the server's response
            if response.status_code == 200:
                print("TOTP verification successful!")

                # Proceed to upload form data if verification succeeds
                send_form_data()
                break
            else:
                print(f"Error: {response.status_code} - {response.text}")
                print("Please try again.")
        except requests.exceptions.RequestException as e:
            # Catch and report any network-related errors
            print(f"[ERROR] An exception occurred: {e}")
            print("Retrying...")

def send_form_data():
    file_path = "form_data.json"  # Path to the JSON file containing form data
    upload_url = os.getenv("UPLOAD_URL", "http://0.0.0.0:8000/upload")  # Retrieve the upload URL from environment variables
    
    try:
        print(f"[DEBUG] Upload URL: {upload_url}")
        print(f"[DEBUG] File path: {file_path}")

        # Open the JSON file in binary mode for upload
        with open(file_path, "rb") as file:
            files = {"file": file}  # Prepare the file payload
            print(f"[DEBUG] Files payload prepared for upload.")
            response = requests.post(upload_url, files=files, verify=False)  # Added verify=False for testing

        # Handle the server's response
        print(f"[DEBUG] Upload response status: {response.status_code}, Response text: {response.text}")
        if response.status_code == 200:
            print("File uploaded successfully!")
        else:
            print(f"Failed to upload file. Server responded with: {response.status_code} - {response.text}")
    except FileNotFoundError:
        # Handle the case where the specified file does not exist
        print(f"[ERROR] File {file_path} not found.")
    except requests.exceptions.RequestException as e:
        # Catch and report any network-related errors during file upload
        print(f"[ERROR] An exception occurred while uploading the file: {e}")

if __name__ == "__main__":
    print("[DEBUG] Starting TOTP verification process.")
    verify_totp()

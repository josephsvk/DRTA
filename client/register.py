import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def verify_totp():
    url = os.getenv("TOTP_URL", "http://127.0.0.1:8000/verify-totp")
    headers = {"Content-Type": "application/json"}

    while True:
        try:
            totp_code = input("Please enter your TOTP code: ")

            # Prepare the payload
            payload = {"code": totp_code}

            # Send the request
            response = requests.post(url, headers=headers, data=json.dumps(payload))

            # Check the response
            if response.status_code == 200:
                print("TOTP verification successful!")

                # Send form_data.json to the server
                send_form_data()
                break
            else:
                print(f"Error: {response.status_code} - {response.text}")
                print("Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            print("Retrying...")

def send_form_data():
    file_path = "form_data.json"
    upload_url = os.getenv("UPLOAD_URL", "http://127.0.0.1:8000/upload")
    
    try:
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(upload_url, files=files)

        if response.status_code == 200:
            print("File uploaded successfully!")
        else:
            print(f"Failed to upload file. Server responded with: {response.status_code} - {response.text}")
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while uploading the file: {e}")

if __name__ == "__main__":
    verify_totp()

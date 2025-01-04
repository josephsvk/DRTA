import requests
import json

def verify_totp():
    url = "http://127.0.0.1:8000/verify-totp"
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
                break
            else:
                print(f"Error: {response.status_code} - {response.text}")
                print("Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            print("Retrying...")

if __name__ == "__main__":
    verify_totp()

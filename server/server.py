import os
import urllib3
import json
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import pyotp
from dotenv import load_dotenv
from flask import Flask, request

# Flask instance for handling file uploads. Flask is used here for simplicity in handling multipart/form-data.
flask_app = Flask(__name__)

# FastAPI instance for handling API requests. FastAPI provides a modern and high-performance API framework.
app = FastAPI()

# Load environment variables from a .env file, if available. This ensures sensitive data can be stored outside the codebase.
load_dotenv()

# Determine the environment (local or production).
env = os.getenv("ENV", "production")
verify_ssl = False if env == "local" else True

# Disable SSL warnings to avoid warnings when making requests to servers with self-signed certificates.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Retrieve the TOTP shared secret key from the environment variables.
SHARED_SECRET = os.getenv("TOTP_SECRET")
if not SHARED_SECRET:
    raise ValueError("TOTP_SECRET environment variable not set")  # Raise an error if the secret key is not defined.

# Define a model for validating incoming TOTP verification requests. Pydantic is used for data validation.
class TOTPRequest(BaseModel):
    code: str  # The TOTP code submitted by the user.

@app.post("/verify-totp")
async def verify_totp(request: TOTPRequest, raw_request: Request):
    """Endpoint to verify a submitted TOTP code.
    Uses pyotp to validate the provided code against the shared secret.
    """
    print("Received TOTP verification request.")  # Debug log for incoming requests.
    print(f"Headers: {raw_request.headers}")  # Log request headers for debugging.
    print(f"Body: {await raw_request.body()}")  # Log request body for debugging.
    totp = pyotp.TOTP(SHARED_SECRET)  # Initialize the TOTP instance with the shared secret.
    if totp.verify(request.code):  # Check if the submitted code is valid.
        print("TOTP verification succeeded.")  # Debug log for successful validation.
        return {"status": "valid"}  # Return a success response if the code is valid.
    else:
        print("TOTP verification failed.")  # Debug log for failed validation.
        raise HTTPException(status_code=400, detail="Invalid TOTP code")  # Raise an error for invalid codes.

@flask_app.route('/upload', methods=['POST'])
def upload():
    """Endpoint to upload a file through Flask.
    Checks if a file is included in the request and saves it locally.
    """
    print("Upload endpoint called.")  # Debug log for endpoint invocation.
    if 'file' not in request.files:  # Verify that a file is included in the request.
        print("No file found in the request.")  # Debug log for missing file.
        return {"error": "No file uploaded"}, 400  # Return an error if no file is uploaded.
    file = request.files['file']  # Retrieve the file from the request.
    print(f"File received: {file.filename}")  # Debug log for received file name.
    file.save(file.filename)  # Save the uploaded file to the local filesystem.
    print(f"File saved: {file.filename}")  # Debug log for file save success.
    return {"message": "File uploaded successfully"}, 200  # Return a success message.

if __name__ == "__main__":
    print("Starting Flask server with SSL.")  # Debug log for server start.
    # Example request for debugging SSL behavior.
    url = "https://example.com/test"
    headers = {"Content-Type": "application/json"}
    payload = {"key": "value"}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=verify_ssl)
        print(f"Request response: {response.status_code}, {response.text}")  # Debug log for request response.
    except Exception as e:
        print(f"Error making request: {e}")  # Debug log for errors.
    # Run the Flask application with SSL context for secure communication.
    flask_app.run(host="127.0.0.1", ssl_context=('cert.pem', 'key.pem'))

import os
import urllib3
import json
import requests
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import pyotp
from dotenv import load_dotenv

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
async def verify_totp(request: TOTPRequest):
    """Endpoint to verify a submitted TOTP code.
    Uses pyotp to validate the provided code against the shared secret.
    """
    print("Received TOTP verification request.")  # Debug log for incoming requests.
    totp = pyotp.TOTP(SHARED_SECRET)  # Initialize the TOTP instance with the shared secret.
    if totp.verify(request.code):  # Check if the submitted code is valid.
        print("TOTP verification succeeded.")  # Debug log for successful validation.
        return {"status": "valid"}  # Return a success response if the code is valid.
    else:
        print("TOTP verification failed.")  # Debug log for failed validation.
        raise HTTPException(status_code=400, detail="Invalid TOTP code")  # Raise an error for invalid codes.

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Endpoint to upload a file through FastAPI.
    Saves the uploaded file locally.
    """
    print("Upload endpoint called.")  # Debug log for endpoint invocation.
    file_location = f"./{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    print(f"File saved: {file.filename}")  # Debug log for file save success.
    return {"message": "File uploaded successfully"}  # Return a success message.

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server with SSL.")  # Debug log for server start.
    # Example request for debugging SSL behavior.
    url = "https://example.com/test"
    headers = {"Content-Type": "application/json"}
    payload = {"key": "value"}

    # Use local certificates directly from the root directory.
    cert_file = "./local-cert.pem"
    key_file = "./local-key.pem"

    # Verify the existence of certificates
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        raise FileNotFoundError(f"Missing SSL certificate files: {cert_file}, {key_file}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=verify_ssl)
        print(f"Request response: {response.status_code}, {response.text}")  # Debug log for request response.
    except Exception as e:
        print(f"Error making request: {e}")  # Debug log for errors.
    # Run the FastAPI application with SSL context for secure communication.
    uvicorn.run(app, host="0.0.0.0", port=443, ssl_certfile=cert_file, ssl_keyfile=key_file)

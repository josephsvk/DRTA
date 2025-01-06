import os
import urllib3
import json
import requests
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import pyotp
from dotenv import load_dotenv
import sys
import uvicorn
import ssl
import socket

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

def list_files_in_container():
    """List all files in the container for debugging purposes.
    Walk through the root directory and print each file found.
    """
    for root, dirs, files in os.walk("/"):
        for file in files:
            print(os.path.join(root, file))

def run_ssl_server():
    """Run the application using OpenSSL sockets for encryption."""
    cert_file = "./local-cert.pem"
    key_file = "./local-key.pem"

    # Verify the existence of certificates
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        raise FileNotFoundError(f"Missing SSL certificate files: {cert_file}, {key_file}")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind(("0.0.0.0", 8443))
        sock.listen(5)
        print("SSL server running on https://0.0.0.0:8443")

        with context.wrap_socket(sock, server_side=True) as ssock:
            while True:
                conn, addr = ssock.accept()
                print(f"Connection established with {addr}")

if __name__ == "__main__":
    # Determine if HTTP, HTTPS, or OpenSSL socket should be used based on command-line arguments
    use_https = "--https" in sys.argv
    use_openssl = "--openssl" in sys.argv

    if use_https:
        print("Starting FastAPI server with HTTPS.")
        # Run the FastAPI application with SSL context for secure communication.
        uvicorn.run(app, host="0.0.0.0", port=443, ssl_certfile="./local-cert.pem", ssl_keyfile="./local-key.pem")
    elif use_openssl:
        print("Starting server with OpenSSL sockets.")
        run_ssl_server()
    else:
        print("Starting FastAPI server with HTTP.")
        uvicorn.run(app, host="0.0.0.0", port=8000)

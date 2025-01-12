import os
import json
import uuid
import pyotp
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from app.database import SessionLocal, ClientData  # Assuming these are pre-configured
from loguru import logger
import time

app = FastAPI()

# Retrieve the TOTP shared secret key from environment variables.
SHARED_SECRET = os.getenv("TOTP_SECRET")
if not SHARED_SECRET:
    logger.critical("TOTP_SECRET environment variable not set. Terminating program.")
    raise SystemExit("TOTP_SECRET environment variable is required but not set. Exiting application.")

class TOTPRequest(BaseModel):
    code: str

    @validator("code")
    def validate_code(cls, value):
        if not value.isdigit() or len(value) != 6:
            raise ValueError("TOTP code must be exactly 6 digits.")
        return value

@app.post("/verify-totp")
async def verify_totp(request: TOTPRequest):
    """Verify a submitted TOTP code against the shared secret."""
    logger.info("Received TOTP verification request.")
    totp = pyotp.TOTP(SHARED_SECRET)  # Initialize the TOTP instance.
    if totp.verify(request.code):
        logger.info("TOTP verification succeeded.")
        return {"status": "valid"}  # Return success response if the code is valid.
    else:
        logger.warning("TOTP verification failed.")
        raise HTTPException(status_code=400, detail="Invalid TOTP code")  # Return error for invalid code.

@app.post("/process-form-data")
async def process_form_data(file: UploadFile = File(...)):
    """Process form_data.json content and store it in the database."""
    logger.info("Processing form_data.json.")
    file_content = await file.read()
    logger.debug(f"Received file content: {file_content.decode('utf-8')}" )
    data = json.loads(file_content.decode('utf-8'))  # Parse the uploaded JSON data.

    # Retrieve necessary environment variables for processing
    env_prefix = os.getenv("IPV6_PREFIX", "default_prefix").lower()
    port_range_start = int(os.getenv("PORT_RANGE_START", "8000"))
    port_range_end = int(os.getenv("PORT_RANGE_END", "9000"))

    # Extract values from the uploaded file
    device_name = data.get("device_name")
    ipv6_prefix = data.get("ipv6_prefix").lower()
    location = data.get("location")
    function = data.get("function")

    # Validate that the IPv6 prefix matches the environment prefix
    if ipv6_prefix != env_prefix:
        logger.error(f"Invalid IPv6 prefix provided: {ipv6_prefix}. Expected: {env_prefix}.")
        return {"error": "Invalid IPv6 prefix. Process terminated."}

    session = SessionLocal()

    try:
        # Generate a new port within the defined range
        last_port_entry = session.query(ClientData).order_by(ClientData.port.desc()).first()
        if last_port_entry and last_port_entry.port >= port_range_end:
            logger.error("No available ports in the defined range.")
            return {"error": "No available ports in the defined range."}

        port = last_port_entry.port + 1 if last_port_entry else port_range_start + 1

        logger.debug(f"Selected unique port: {port}")  

        # Generate unique ID and IPv6 address from timestamp
        timestamp = int(time.time() * 1000)  # Current timestamp in milliseconds
        hex_timestamp = hex(timestamp)[2:]  # Convert to hexadecimal and remove '0x'
        padded_hex_timestamp = hex_timestamp.zfill(20)  # Pad to 80 bits (20 hex characters)

        ipv6_generated = f"{ipv6_prefix}:{padded_hex_timestamp[:4]}:{padded_hex_timestamp[4:8]}:{padded_hex_timestamp[8:12]}:{padded_hex_timestamp[12:16]}:{padded_hex_timestamp[16:]}"

        logger.debug(f"Generated IPv6 address: {ipv6_generated}")

        # Generate a unique identifier for the client
        unique_id = padded_hex_timestamp  # Use the same padded timestamp as the unique ID
        logger.debug(f"Generated unique ID: {unique_id}")  

        # Save the client data to the database
        new_client = ClientData(
            device_name=device_name,
            ipv6_address=ipv6_generated,
            port=port,
            location=location,
            function=function,
            unique_id=unique_id
        )
        session.add(new_client)
        session.commit()
        logger.info(f"Client data saved successfully: {unique_id}")

        # Return processed data to the client
        return {
            "message": "Data processed successfully",
            "data": {
                "device_name": device_name,
                "ipv6_address": ipv6_generated,
                "port": port,
                "location": location,
                "function": function,
                "unique_id": unique_id
            }
        }
    except Exception as e:
        try:
            session.rollback()
            logger.error(f"Transaction rolled back due to error: {e}. Data attempted: {data}. Affected operation: Adding new client data.")
            if session.is_active:
                session.close()  # Ensure session is properly closed if rollback partially succeeded.
        except Exception as rollback_error:
            logger.critical(f"Rollback failed: {rollback_error}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if session.is_active:
            session.close()
        logger.debug("Database session closed.")  # Log session closure
        logger.debug(f"Selected unique port: {port}")  

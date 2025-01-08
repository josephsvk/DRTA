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
import uuid
import logging
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

# Configure structured logging for better log management
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI instance for handling API requests.
app = FastAPI()

# Load environment variables from a .env file to store sensitive data securely.
load_dotenv()

# Initialize database with SQLCipher for encrypted data storage
DB_PATH = "./secure_data.db"
DB_KEY = os.getenv("DB_KEY", "default_secure_key")  # Database encryption key
try:
    logger.info("Initializing database engine...")
    engine = create_engine(
        f"sqlite+pysqlcipher://:{DB_KEY}@/{DB_PATH}",
        connect_args={"check_same_thread": False},
        future=True
    )
    Base = declarative_base()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully.")
except Exception as e:
    logger.critical(f"Database initialization failed: {e}")
    raise

# Define the database model for storing client data.
class ClientData(Base):
    __tablename__ = "client_data"

    id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String, nullable=False)
    ipv6_address = Column(String, unique=True, nullable=False)
    port = Column(Integer, unique=True, nullable=False)
    location = Column(String, nullable=False)
    function = Column(String, nullable=False)
    unique_id = Column(String, unique=True, nullable=False)

# Disable SSL warnings to avoid unnecessary warnings during development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Retrieve the TOTP shared secret key from environment variables.
SHARED_SECRET = os.getenv("TOTP_SECRET")
if not SHARED_SECRET:
    logger.critical("TOTP_SECRET environment variable not set")  # Log critical error
    raise ValueError("TOTP_SECRET environment variable not set")  # Ensure the key is defined.

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
    logger.debug(f"Received file content: {file_content.decode('utf-8')}")  # Debug log of file content
    data = json.loads(file_content.decode('utf-8'))  # Parse the uploaded JSON data.

    # Retrieve necessary environment variables for processing
    env_prefix = os.getenv("IPV6_PREFIX", "default_prefix")
    port_range_start = int(os.getenv("PORT_RANGE_START", "8000"))
    port_range_end = int(os.getenv("PORT_RANGE_END", "9000"))

    # Extract values from the uploaded file
    device_name = data.get("device_name")
    ipv6_prefix = data.get("ipv6_prefix")
    location = data.get("location")
    function = data.get("function")

    # Validate that the IPv6 prefix matches the environment prefix
    if ipv6_prefix != env_prefix:
        logger.error(f"Invalid IPv6 prefix provided: {ipv6_prefix}. Expected: {env_prefix}.")
        return {"error": "Invalid IPv6 prefix. Process terminated."}

    session = SessionLocal()

    try:
        # Generate a new unique port within the defined range
        for port in range(port_range_start, port_range_end):
            if not session.query(ClientData).filter_by(port=port).first():
                logger.debug(f"Selected unique port: {port}")  # Log selected port
                break
        else:
            logger.error("No available ports in the defined range.")
            return {"error": "No available ports in the defined range."}

        # Generate a new unique IPv6 address
        for i in range(1, 65536):
            ipv6_address = f"{ipv6_prefix}:{i}"
            if not session.query(ClientData).filter_by(ipv6_address=ipv6_address).first():
                logger.debug(f"Generated unique IPv6 address: {ipv6_address}")  # Log selected IPv6 address
                break
        else:
            logger.error("No available IPv6 addresses in the defined range.")
            return {"error": "No available IPv6 addresses in the defined range."}

        # Generate a unique identifier for the client
        unique_id = str(uuid.uuid4())
        logger.debug(f"Generated unique ID: {unique_id}")  # Log unique ID

        # Save the client data to the database
        new_client = ClientData(
            device_name=device_name,
            ipv6_address=ipv6_address,
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
                "ipv6_address": ipv6_address,
                "port": port,
                "location": location,
                "function": function,
                "unique_id": unique_id
            }
        }
    except Exception as e:
        try:
            session.rollback()
            logger.error(f"Transaction rolled back due to error: {e}")
        except Exception as rollback_error:
            logger.critical(f"Rollback failed: {rollback_error}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        session.close()
        logger.debug("Database session closed.")  # Log session closure

if __name__ == "__main__":
    logger.info("Starting FastAPI server with HTTPS.")
    uvicorn.run(app, host="0.0.0.0", port=443, ssl_certfile="./local-cert.pem", ssl_keyfile="./local-key.pem")

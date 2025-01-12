import os
import urllib3
from fastapi import FastAPI
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
from OpenSSL import crypto

# My server modules
from app_routes import register_routes

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

# Load the environment type and handle accordingly
is_production = os.getenv("PRODUCTION", "false").lower() == "true"
if not is_production:
  
    # Disable SSL warnings to avoid unnecessary warnings during development
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    logger.info("Running in local environment. SSL warnings are disabled.")
else:
    logger.warning(f"Running in production environment." 
                   f"Ensure SSL certificates and configurations are secure.")

# Function to generate self-signed certificates
def generate_self_signed_cert(certfile, keyfile):
    logger.info("Generating self-signed SSL certificates for local use.")

    # Create a new private key and self-signed certificate
    key = crypto.PKey()
  
    # Configurable key size with default
    key_size = int(os.getenv("CERT_KEY_SIZE", "2048"))  
    key.generate_key(crypto.TYPE_RSA, key_size)

    cert = crypto.X509()
    cert.get_subject().C = os.getenv("CERT_C", "US")
    cert.get_subject().ST = os.getenv("CERT_ST", "California")
    cert.get_subject().L = os.getenv("CERT_L", "San Francisco")
    cert.get_subject().O = os.getenv("CERT_O", "My Company")
    cert.get_subject().CN = os.getenv("CERT_CN", "localhost")
    cert.set_serial_number(int(os.getenv("CERT_SERIAL", "1000")))
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, "sha256")

    # Write the private key and certificate to files
    with open(certfile, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(keyfile, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    logger.info(f"Self-signed SSL certificates generated successfully at" 
                f"certfile: {certfile} and keyfile: {keyfile}.")

# Register all routes from a separate module
register_routes(app)

if __name__ == "__main__":
    logger.info("Starting FastAPI server with HTTPS.")

    # Load SSL certificate paths or use defaults
    ssl_certfile = os.getenv("SSL_CERTFILE", "./local-cert.pem")
    ssl_keyfile = os.getenv("SSL_KEYFILE", "./local-key.pem")

    # Generate SSL certificates if missing
    if not os.path.exists(ssl_certfile) or not os.path.exists(ssl_keyfile):
        logger.warning(
            f"SSL certificate or key file missing. Attempting to generate new"
            f"certificates at certfile: {ssl_certfile} and keyfile: {ssl_keyfile}."
        )
        generate_self_signed_cert(ssl_certfile, ssl_keyfile)

    # Load host and port from environment variables or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "443"))

    try:
        # Run uvicorn server on host and port  
        uvicorn.run(app, 
                    host=host, 
                    port=port, 
                    ssl_certfile=ssl_certfile,
                    ssl_keyfile=ssl_keyfile)
    except Exception as e:
        logger.critical(f"Failed to start server: {e}")
        raise

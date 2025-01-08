import os
import logging
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.inspection import inspect

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseLogger")

# Configuration for database setup
DB_PATH = os.getenv("DB_PATH", "./secure_data.db")  # Path to the SQLite database file
DB_KEY = os.getenv("DB_KEY", "default_secure_key")  # Encryption key for the database

def generate_database_url(db_key, db_path):
    """
    Generates the database URL.
    Args:
        db_key (str): The encryption key for the database.
        db_path (str): The path to the SQLite database file.
    Returns:
        str: The formatted database URL.
    """
    return f"sqlite+pysqlcipher://:{db_key}@/{db_path}"

# Initialize database connection
try:
    logger.info("Initializing database engine...")
    engine = create_engine(
        generate_database_url(DB_KEY, DB_PATH),
        connect_args={"check_same_thread": False},
        future=True
    )
    Base = declarative_base()
    SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine)
    logger.info("Database engine initialized successfully.")
except Exception as e:
    logger.critical(f"Failed to initialize the database: {e}")
    raise

# Define database models
class ClientData(Base):
    """
    Represents the schema for client data stored in the database.
    Attributes:
        id (int): Primary key, unique identifier for each client.
        device_name (str): Name of the device.
        ipv6_address (str): Unique IPv6 address of the device.
        port (int): Communication port of the device.
        location (str): Physical or logical location of the device.
        function (str): Role or functionality of the device.
        unique_id (str): Unique identifier for the client.
    """
    __tablename__ = "client_data"

    id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String, nullable=False)
    ipv6_address = Column(String, unique=True, nullable=False)
    port = Column(Integer, unique=True, nullable=False)
    location = Column(String, nullable=False)
    function = Column(String, nullable=False)
    unique_id = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return (
            f"<ClientData(id={self.id}, device_name='{self.device_name}', ipv6_address='{self.ipv6_address}', "
            f"port={self.port}, location='{self.location}', function='{self.function}', unique_id='{self.unique_id}')>"
        )

# Create database tables
try:
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")
except Exception as e:
    logger.critical(f"Failed to create database tables: {e}")
    raise

# Utility function for obtaining a database session
def get_db_session():
    """
    Provides a new database session for performing operations.
    Returns:
        sqlalchemy.orm.Session: A new session bound to the database engine.
    """
    session = None
    try:
        logger.info("Creating a new database session...")
        session = SessionLocal()
        return session
    except Exception as e:
        logger.error(f"Failed to create database session: {e}")
        if session:
            session.close()
        raise
    finally:
        if session:
            session.close()
            logger.info("Database session closed.")

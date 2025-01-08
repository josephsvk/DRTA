import os
import logging
import sqlite3  # Import SQLite to define the custom connection
import re
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseLogger")

# Configuration for database setup
DB_PATH = os.getenv("DB_PATH", "./secure_data.db")  # Path to the SQLite database file
DB_KEY = os.getenv("DB_KEY", "default_secure_key")  # Encryption key for the database

def connect(db_path, db_key):
    """
    Custom connection function for SQLite.
    Args:
        db_path (str): Path to the database file.
        db_key (str): Encryption key for the database.
    Returns:
        sqlite3.Connection: The SQLite connection.
    """
    conn = sqlite3.connect(db_path)  # Pripojenie k SQLite databáze
    conn.execute(f"PRAGMA key='{db_key}'")  # Nastavenie šifrovacieho kľúča
    conn.create_function("regexp", 2, lambda x, y: bool(re.search(x, y)))  # Registrácia 'regexp' funkcie
    return conn

# Initialize database connection
try:
    logger.info("Initializing database engine...")
    engine = create_engine(
        "sqlite+pysqlcipher:///path/to/secure.db",
        creator=lambda: connect(DB_PATH, DB_KEY),
        connect_args={"check_same_thread": False},
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

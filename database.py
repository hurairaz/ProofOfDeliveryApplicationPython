from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# URL for the Postgres database connection.
# Format: SQLALCHEMY_DATABASE_URL = postgresql://username:password@host/database
load_dotenv()
database_url = os.getenv("SQLALCHEMY_DATABASE_URL")
SQLALCHEMY_DATABASE_URL = f"{database_url}"

# Creates an Engine instance that connects to the database.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session factory bound to the engine.
# This factory will create new Session objects which are used to interact with the database.
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)

# Provides a base class for creating ORM models.
Base = declarative_base()

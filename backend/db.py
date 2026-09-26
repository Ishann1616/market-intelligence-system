import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

DATABASE_URL= os.getenv("DATABASE_URL")

# The engine is what actually talks to Postgres
engine = create_engine(DATABASE_URL)

# SessionLocal is how we'll open individual conversations with the DB
SessionLocal = sessionmaker(bind=engine)


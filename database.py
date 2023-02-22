from dotenv import load_dotenv
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

if load_dotenv():
    URL_DATABASE_CREDENTIALS = getenv('URL_DATABASE')

    SQLITE_DATABASE_URL = URL_DATABASE_CREDENTIALS
    engine = create_engine(
        SQLITE_DATABASE_URL
    )

    SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

    Base = declarative_base()


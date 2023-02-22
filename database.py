from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLITE_DATABASE_URL = "postgresql://postgres:name123@localhost:5432/TodoApplicationDatabasev2"

engine = create_engine(
    SQLITE_DATABASE_URL
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()


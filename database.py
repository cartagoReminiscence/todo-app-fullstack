from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLITE_DATABASE_URL = "postgresql://fqxatais:BPKWgqgqaRfkqdF3uiEZ7iOfkAB7KLyv@suleiman.db.elephantsql.com/fqxatais"
engine = create_engine(
    SQLITE_DATABASE_URL
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()


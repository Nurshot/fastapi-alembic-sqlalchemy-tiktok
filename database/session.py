from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator            #new





SQLALCHEMY_DATABASE_URL = "postgresql://amasor:mem123@127.0.0.1:5432/android"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#if you don't want to install postgres or any database, use sqlite, a file system based database, 
# uncomment below lines if you would like to use sqlite and comment above 2 lines of SQLALCHEMY_DATABASE_URL AND engine

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

def get_db() -> Generator:   #new
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
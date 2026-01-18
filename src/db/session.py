import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

if not os.getenv("POSTGRES_PORT"):
    raise ValueError("POSTGRES_PORT is missing from environment variables, check .env file")



# create connection to db, constructing db url
# using only fstring to avoid hardcoding credentials, better for prod. 

db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

#creating engine - connection pool

engine = create_engine(db_url, pool_size=20, max_overflow=10) #20 concurrent threads #upto 10 bonus threads, in case of traffic spikes. 

#session settings
#no autocommit, this gives us control over data saves, enabling rollback during connection/request errors. 

SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)

#ORM manager

Base= declarative_base()

def get_db():
    db = SessionLocal()

    try: 
        yield db

    finally: 
        db.close()



"""
file for database related configurations
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# step 1 - define database url
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"

# step 2 - define the database engine
# an engine is that something that we can use to open up a conneciton to database
# url + connect arguments( arguments that can be passed into create engine which will allow us find the some connecitons of databse)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

"""
 check same thread = false ---> by default sql lite only uses one thread for connections,fastapi uses multiple threads
 """

# step 3  -- create a session local ,each instance of session local  has a independant session - we can create session with sessionmaker
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
"""
"""

# step4 -- > make sure we can create database objects  - for that we need to create a base - this base will contol database for createing or updating objects
Base = declarative_base()

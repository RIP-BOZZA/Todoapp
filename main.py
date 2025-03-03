"""
root file for  applicaiton
"""
from fastapi import FastAPI 
from database import engine ,Base
from routers import auth ,todos


app=FastAPI()
app.include_router(auth.router)
app.include_router(todos.router)

# this will all create all configuraitons & tables in database.py and models.py file
Base.metadata.create_all(bind=engine) # this will be only run if the db does not exist

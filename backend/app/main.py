from app.database.db import Base, engine
from app.models.municipality import Municipality
from app.models.municipality_official import MunicipalityOfficial
from fastapi import FastAPI


app = FastAPI()


Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message":"Scraper AI system running "} 

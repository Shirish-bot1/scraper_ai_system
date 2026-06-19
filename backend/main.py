# from fastapi import FastAPI, HTTPException, Query
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from fastapi.responses import FileResponse
# from app.database.db import Base, engine
# from app.services.data_fetcher import get_complete_municipality_data, get_full_database_dump,export_municipalities_to_csv
# from app.ai_agent import chat_with_agent
# from app.services.data_fetcher import get_multiple_municipalities
# from fastapi.staticfiles import StaticFiles
# from app.scrapper.official_scraper import scrape_municipality
# import os

# # Initialize database tables
# Base.metadata.create_all(bind=engine)

# app = FastAPI(title="Municipality AI API")
# if not os.path.exists("exports"):
#     os.makedirs("exports")

# app.mount("/exports", StaticFiles(directory="exports"), name="exports")

# # Enable CORS for React
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "http://127.0.0.1:5173"
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# @app.get("/")
# async def root():
#     return {"message": "Municipality AI API is running."}

# @app.get("/ask-ai/")
# async def query_municipality_info(name: str = Query(...)):
#     data = get_complete_municipality_data(name)
#     if not data:
#         raise HTTPException(status_code=404, detail="Municipality not found")
#     return data

# class ChatRequest(BaseModel):
#     municipality: str
#     question: str

# class ScraperRequest(BaseModel):
#     url: str

# @app.post("/chat/")
# async def chat_with_ai(request: ChatRequest):
#     try:
#         result = chat_with_agent(request.question, request.municipality)

#         # detect CSV request
#         query = request.question.lower()

#         csv_files = []

#         if "csv" in query:

#             file_path = export_municipalities_to_csv(20)

#             file_name = file_path.split("/")[-1]
#             csv_files.append({
#                  "name": file_name,
#                   "url": f"http://127.0.0.1:8000/exports/{file_name}"

#             })

#         return {
#             "municipality": request.municipality,
#             "answer": result,
#             "csv_files": csv_files
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/full-dump")
# async def get_all_data():
#     return get_full_database_dump()

# @app.get("/export-csv")
# async def export_csv(limit: int = 20):

#     file_path = export_municipalities_to_csv(limit)

#     return FileResponse(
#         path=file_path,
#         filename=file_path,
#         media_type="text/csv"
#     )

# @app.get("/municipalities")
# async def municipalities(limit: int = 20):

#     return get_multiple_municipalities(limit)


# @app.get("/download-csv")
# def download_csv(limit: int = 20):

#     file_path = export_municipalities_to_csv(limit)

#     return FileResponse(
#         path=file_path,
#         filename=f"municipalities_{limit}.csv",
#         media_type="text/csv"
#     )

# @app.post("/scrape")
# async def scrape_website(request: ScraperRequest):

#     try:
#         data = scrape_municipality(request.url)

#         return {
#             "success": True,
#             "url": request.url,
#             "data": data
#         }

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Scraping failed: {str(e)}"
#         )

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import os

from app.database.db import Base, engine, SessionLocal
from app.models.municipality import Municipality

from app.services.data_fetcher import (
    get_complete_municipality_data,
    get_full_database_dump,
    export_municipalities_to_csv
)

from app.ai_agent import chat_with_agent
from app.scrapper.official_scraper import scrape_municipality


# =========================
# INIT APP + DB
# =========================
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Municipality AI API")

if not os.path.exists("exports"):
    os.makedirs("exports")

app.mount("/exports", StaticFiles(directory="exports"), name="exports")


# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ROOT
# =========================
@app.get("/")
async def root():
    return {"message": "Municipality AI API is running."}


# =========================
# AI QUERY (SINGLE MUNICIPALITY)
# =========================
@app.get("/ask-ai/")
async def query_municipality_info(name: str = Query(...)):
    data = get_complete_municipality_data(name)

    if not data:
        raise HTTPException(status_code=404, detail="Municipality not found")

    return data


# =========================
# CHAT AI
# =========================
class ChatRequest(BaseModel):
    municipality: str
    question: str


@app.post("/chat/")
async def chat_with_ai(request: ChatRequest):
    try:
        result = chat_with_agent(request.question, request.municipality)

        query = request.question.lower()
        csv_files = []

        if "csv" in query:
            file_path = export_municipalities_to_csv(20)
            file_name = file_path.split("/")[-1]

            csv_files.append({
                "name": file_name,
                "url": f"http://127.0.0.1:8000/exports/{file_name}"
            })

        return {
            "municipality": request.municipality,
            "answer": result,
            "csv_files": csv_files
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# FULL DATA DUMP (DEBUG)
# =========================
@app.get("/api/full-dump")
async def get_all_data():
    return get_full_database_dump()


# =========================
# CSV EXPORT
# =========================
@app.get("/export-csv")
async def export_csv(limit: int = 20):
    file_path = export_municipalities_to_csv(limit)

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="text/csv"
    )


# =========================
# 🚀 FIXED: MUNICIPALITIES LIST (NO LIMIT ISSUE)
# =========================
@app.get("/municipalities")
async def get_municipality_list():
    db = SessionLocal()
    try:
        municipalities = db.query(Municipality.municipality_name).all()

        return [m.municipality_name for m in municipalities]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


# =========================
# CSV DOWNLOAD
# =========================
@app.get("/download-csv")
def download_csv(limit: int = 20):
    file_path = export_municipalities_to_csv(limit)

    return FileResponse(
        path=file_path,
        filename=f"municipalities_{limit}.csv",
        media_type="text/csv"
    )


# =========================
# SCRAPER API
# =========================
class ScraperRequest(BaseModel):
    url: str


@app.post("/scrape")
async def scrape_website(request: ScraperRequest):
    try:
        data = scrape_municipality(request.url)

        return {
            "success": True,
            "url": request.url,
            "data": data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )
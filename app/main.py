from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .database import AsyncSessionLocal, engine, Base
from . import processing
import shutil
import os

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.post("/upload_csv/{table_name}")
async def upload_csv(table_name: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    path = f"csv_files/{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if table_name not in processing.MODEL_MAP:
        return {"error": "Invalid table name"}

    await processing.upload_csv(db, path, table_name)
    return {"status": "success"}

@app.post("/batch_insert/{table_name}")
async def batch_insert(table_name: str, data: list[dict], db: AsyncSession = Depends(get_db)):
    if not (1 <= len(data) <= 1000):
        return {"error": "Batch must be 1 to 1000 records"}

    if table_name not in processing.MODEL_MAP:
        return {"error": "Invalid table name"}

    await processing.batch_insert(db, data, table_name)
    return {"status": "inserted"}
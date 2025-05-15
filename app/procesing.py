from pyspark.sql import SparkSession
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from . import models

MODEL_MAP = {
    "departments": models.Department,
    "jobs": models.Job,
    "employees": models.Employee
}

def get_spark_session():
    spark = SparkSession.builder \
        .appName("CSVUploader") \
        .master("local[*]") \
        .getOrCreate()
    return spark

def read_csv_with_spark(file_path: str):
    spark = get_spark_session()
    df = spark.read.option("header", True).csv(file_path)
    return df.toJSON().map(lambda row: eval(row)).collect()

async def upload_csv(db: AsyncSession, file_path: str, model_name: str):
    data = read_csv_with_spark(file_path)
    model = MODEL_MAP[model_name]
    await db.execute(insert(model), data)
    await db.commit()

async def batch_insert(db: AsyncSession, data: list[dict], model_name: str):
    model = MODEL_MAP[model_name]
    await db.execute(insert(model), data)
    await db.commit()

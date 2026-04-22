from fastapi import FastAPI
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.api.measurements import router as measurements_router

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(measurements_router)
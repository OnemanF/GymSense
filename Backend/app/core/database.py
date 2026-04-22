from app.core.config import settings
from app.models.sensor_reading import SensorReading
from sqlmodel import SQLModel, Session, create_engine

engine = create_engine(settings.database_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
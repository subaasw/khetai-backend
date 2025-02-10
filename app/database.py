from sqlmodel import SQLModel, create_engine, Session
from config import DB_CONFIG

engine = create_engine(DB_CONFIG, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

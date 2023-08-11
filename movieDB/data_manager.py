from sqlalchemy.orm import Session, sessionmaker
from movieDB.models_data_manager import ModelsDataManager
from movieDB.models import Base, engine

# Create your session here
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Create your data_manager object
data_manager = ModelsDataManager(session)

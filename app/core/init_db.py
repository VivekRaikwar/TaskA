from sqlalchemy import create_engine
from ..models.database import Base
from .config import settings

def init_db():
    """Initialize the database."""
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db() 
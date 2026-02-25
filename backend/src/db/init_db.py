from src.db.database import Base, engine
from src.db import models  # noqa: F401 — registers all models


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


if __name__ == "__main__":
    create_tables()

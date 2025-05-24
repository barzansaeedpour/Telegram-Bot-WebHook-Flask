# db.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///telegram.db"  # You can use PostgreSQL, MySQL, etc.

Base = declarative_base()

class TelegramUser(Base):
    __tablename__ = 'telegram_user_sazman'
    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(String, unique=True)
    sazman_id = Column(String, unique=True)  # or Integer, depending on your app

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

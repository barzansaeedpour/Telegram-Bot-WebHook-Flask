# db.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///telegram.db"

Base = declarative_base()

class TelegramUser(Base):
    __tablename__ = 'telegram_user_sazman'
    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(String, unique=True)
    sazman_id = Column(String, unique=True)  # or Integer, depending on your app

class DashboardPageConnection(Base):
    __tablename__ = 'dashboard_page_connection'
    id = Column(Integer, primary_key=True)
    query_title = Column(String, nullable=False)
    page_id = Column(String, nullable=False)
    connection_string = Column(String, nullable=False)
    query = Column(String, nullable=False)

# In db.py
class AdminUser(Base):
    __tablename__ = 'admin_user'
    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Store hashed passwords in production





engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Create all tables
# from db import Base, engine

# Base.metadata.drop_all(bind=engine)   # DANGER: deletes all tables and data
Base.metadata.create_all(bind=engine) # Recreate all tables with updated schema


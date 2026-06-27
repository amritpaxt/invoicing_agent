from sqlalchemy import create_engine, Column, String, Float, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

engine = create_engine("sqlite:///tia.db", connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(String, primary_key=True)
    employee_name = Column(String, nullable=True)
    client_name = Column(String, nullable=True)
    amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    status = Column(String, default="needs_review")
    issues = Column(String, nullable=True)
    dispatched = Column(Boolean, default=False)
    client_notified = Column(Boolean, default=False)
    finalized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    dispatched_at = Column(DateTime, nullable=True)

Base.metadata.create_all(engine)
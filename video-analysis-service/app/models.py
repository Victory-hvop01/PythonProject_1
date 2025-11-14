from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    has_movement = Column(Boolean, nullable=False)
    movement_percentage = Column(Float, nullable=False)
    analysis_time = Column(Float, nullable=False)  # Время анализа в секундах
    created_at = Column(DateTime, default=datetime.now)
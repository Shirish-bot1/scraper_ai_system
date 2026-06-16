from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.database.db import Base



class Municipality(Base):
    __tablename__ = "municipalities"

    id = Column(Integer, primary_key=True, index=True)

    province = Column(String(100))
    district = Column(String(100))
    municipality_name = Column(String(255))
    municipality_type = Column(String(100))

    website = Column(Text)
    email = Column(String(255))
    phone = Column(String(100))

    created_at = Column(TIMESTAMP, server_default=func.now())
   
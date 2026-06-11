from sqlalchemy import Column, Integer, String, ForeignKey,Text ,TIMESTAMP
from sqlalchemy.sql import func
from app.database.db import Base


class MunicipalityOfficial(Base):
    __tablename__ = "municipality_officials"

    id = Column(Integer, primary_key=True, index=True)

    municipality_id = Column(
        Integer,
        ForeignKey("municipalities.id", ondelete="CASCADE")
    )
    
    province = Column(String(100))
    district = Column(String(100))
    municipality_name = Column(String(255))
    municipality_type = Column(String(100))
    website = Column(Text)

    mayor_name = Column(String(255))
    mayor_email = Column(String(255))
    mayor_phone = Column(String(100))

    deputy_mayor_name = Column(String(255))
    deputy_mayor_email = Column(String(255))
    deputy_mayor_phone = Column(String(100))

    updated_at = Column(TIMESTAMP, server_default=func.now())
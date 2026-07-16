from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from models.enums import ItemType
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class Item(Base):
    __tablename__ = "items"

    id              = Column(Integer, primary_key=True, index=True)
    
    name            = Column(String, nullable=False)
    type            = Column(Enum(ItemType), nullable=False)
    category        = Column(String)
    count           = Column(Integer, nullable=False)
    unit            = Column(String, nullable=True)
    
    is_active       = Column(Boolean, default=True, nullable=False)
    
    
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


    #relations
    assignments     = relationship("Assignment", back_populates="item", cascade="all, delete-orphan")
    transactions    = relationship("Transaction", back_populates="item", cascade="all, delete-orphan")
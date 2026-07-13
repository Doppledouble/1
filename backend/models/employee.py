from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Employee(Base):
    __tablename__ = "employees"
    
    id              = Column(Integer, primary_key=True, index=True)
    
    first_name      = Column(String, nullable=False)
    last_name       = Column(String, nullable=False)
    contact         = Column(String, nullable=True)
    
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    #relationships
    assignments     = relationship("Assignment", back_populates="employee", cascade="all, delete-orphan")
    transactions    = relationship("Transaction",back_populates="employee")
    
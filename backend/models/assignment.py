from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from datetime import datetime, timezone
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id          = Column(Integer, primary_key=True, index=True)

    item_id     = Column(Integer, ForeignKey("items.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    location    = Column(String, nullable=True)
    
    quantity    = Column(Integer, nullable=False, default=1)
    notes       = Column(String, nullable=True)
    
    assigned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    returned_at = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(String, nullable=True)

    # relationships
    item        = relationship("Item", back_populates="assignments")
    employee    = relationship("Employee", back_populates="assignments")
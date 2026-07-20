from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AssignmentBase(BaseModel):
    item_id: int
    employee_id: int
    location: Optional[str] = None
    quantity: int
    notes: Optional[str] = None
    assigned_at: Optional[datetime] = None


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(BaseModel):
    notes: Optional[str] = None
    quantity: Optional[int] = None
    location: Optional[str] = None
    
    
class ItemBasic(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True
        
        
class EmployeeBasic(BaseModel):
    id: int
    first_name: str
    last_name: str
    
    class Config:
        from_attributes = True
        

class AssignmentResponse(BaseModel):
    id: int
    quantity: int
    assigned_at: datetime
    returned_at: Optional[datetime] = None

    item: ItemBasic
    employee: EmployeeBasic
    location: Optional[str] = None
    notes: Optional[str] = None  

    class Config:
        from_attributes = True
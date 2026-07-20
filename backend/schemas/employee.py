from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EmployeeBase(BaseModel):
    first_name  : str
    last_name   : str
    contact     : Optional[str] = None
    
class EmployeeCreate(EmployeeBase):
    pass
    
    
class EmployeeUpdate(BaseModel):
    first_name  : Optional[str] = None
    last_name   : Optional[str] = None
    contact     : Optional[str] = None


class EmployeeResponse(EmployeeBase):
    id          : int
    created_at  : datetime
    updated_at  : Optional[datetime] = None
    
    class Config:
        from_attributes = True
        
        
class EmployeeSummaryResponse(EmployeeBase):
    id                      : int
    tools_used_count        : int
    materials_used_count    : int
    last_activity           : Optional[datetime] = None

    class Config:
        from_attributes = True
        
        
class EmployeeCurrentTool(BaseModel):
    assignment_id   : int
    item_id         : int
    item_name       : str
    location        : Optional[str] = None
    quantity        : int
    assigned_at     : datetime
    
    class Config:
        from_attributes = True
    
    
class EmployeeTransactionItem(BaseModel):
    transaction_id  : int
    item_id         : int
    item_name       : str
    transaction_type: str
    location        : Optional[str] = None
    quantity        : int
    notes           : Optional[str] = None
    created_at      : datetime
    
    class Config:
        from_attributes = True
    

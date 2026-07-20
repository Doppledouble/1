from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db

from models.employee import Employee
from models.assignment import Assignment
from models.transaction import Transaction
from models.enums import TransactionType

from schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeSummaryResponse,
    EmployeeCurrentTool,
    EmployeeTransactionItem,
)
from schemas.pagination import Page

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("/")
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


@router.get("/{employee_id}/summary", response_model=EmployeeSummaryResponse)
def get_employee_summary(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tools_used_count = (
        db.query(Assignment)
        .filter(Assignment.employee_id == employee_id)
        .count()
    )

    materials_used_count = (
        db.query(Transaction)
        .filter(
            Transaction.employee_id == employee_id,
            Transaction.transaction_type == TransactionType.WITHDRAW,
        )
        .count()
    )

    last_transaction = (
        db.query(Transaction)
        .filter(Transaction.employee_id == employee_id)
        .order_by(Transaction.created_at.desc())
        .first()
    )

    return EmployeeSummaryResponse(
        id=employee.id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        contact=employee.contact,
        tools_used_count=tools_used_count,
        materials_used_count=materials_used_count,
        last_activity=last_transaction.created_at if last_transaction else None,
    )


@router.get("/{employee_id}/current-tools", response_model=list[EmployeeCurrentTool])
def get_employee_current_tools(employee_id: int, db: Session = Depends(get_db)):
    assignments = (
        db.query(Assignment)
        .options(joinedload(Assignment.item))
        .filter(Assignment.employee_id == employee_id, Assignment.returned_at.is_(None))
        .all()
    )

    return [
        EmployeeCurrentTool(
            assignment_id=a.id,
            item_id=a.item_id,
            item_name=a.item.name,
            location=a.location,
            quantity=a.quantity,
            assigned_at=a.assigned_at,
        )
        for a in assignments
    ]


@router.get("/{employee_id}/transactions", response_model=Page[EmployeeTransactionItem])
def get_employee_transactions(
    employee_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    base_query = (
        db.query(Transaction)
        .options(joinedload(Transaction.item))
        .filter(Transaction.employee_id == employee_id)
        .order_by(Transaction.created_at.desc())
    )

    total = base_query.count()

    transactions = base_query.offset((page - 1) * page_size).limit(page_size).all()

    items = [
        EmployeeTransactionItem(
            transaction_id=t.id,
            item_id=t.item_id,
            item_name=t.item.name,
            quantity=t.quantity,
            transaction_type=t.transaction_type.value,
            location=t.location,
            notes=t.notes,
            created_at=t.created_at,
        )
        for t in transactions
    ]

    return Page[EmployeeTransactionItem].create(
        items=items, total=total, page=page, page_size=page_size
    )


@router.get("/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@router.post("/")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    new_employee = Employee(
        first_name=employee.first_name,
        last_name=employee.last_name,
        contact=employee.contact,
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee


@router.patch("/{employee_id}")
def update_employee(
    employee_id: int, employee_data: EmployeeUpdate, db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = employee_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

    return employee


@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if employee:
        db.delete(employee)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {"message": f"Employee with id {employee_id} successfuly deleted"}

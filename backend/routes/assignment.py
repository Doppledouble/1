from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone

from database import get_db
from models.assignment import Assignment
from models.item import Item
from models.employee import Employee
from models.transaction import Transaction
from models.enums import TransactionType, ItemType
from schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentResponse

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.post("/", response_model=AssignmentResponse)
def create_assignment(data: AssignmentCreate, db: Session = Depends(get_db)):
    item = (
        db.query(Item).filter(Item.id == data.item_id, Item.is_active == True).first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.type != ItemType.TOOL:
        raise HTTPException(
            status_code=400, detail="Only tool-type items can be assigned"
        )

    if item.count < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock available")

    item.count -= data.quantity

    assignment = Assignment(
        item_id=data.item_id,
        employee_id=data.employee_id,
        location=data.location,
        quantity=data.quantity,
        notes=data.notes,
        assigned_at=data.assigned_at or datetime.now(timezone.utc)
    )
    db.add(assignment)

    transaction = Transaction(
        item_id=item.id,
        quantity=-data.quantity,
        transaction_type=TransactionType.ASSIGNMENT,
        employee_id=data.employee_id,
        location=data.location,
        notes=data.notes,
        assigned_at=data.assigned_at or datetime.now(timezone.utc)
    )
    db.add(transaction)

    db.commit()
    db.refresh(assignment)

    return assignment


@router.get("/", response_model=list[AssignmentResponse])
def get_assignments(
    active: bool | None = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
):
    query = db.query(Assignment).options(
        joinedload(Assignment.item), joinedload(Assignment.employee)
    )
    if active is not None:
        query = query.filter(
            Assignment.returned_at.is_(None)
            if active
            else Assignment.returned_at.isnot(None)
        )

    return query.all()


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = (
        db.query(Assignment)
        .options(joinedload(Assignment.item), joinedload(Assignment.employee))
        .filter(Assignment.id == assignment_id)
        .first()
    )

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    return assignment


@router.patch("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: int, data: AssignmentUpdate, db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment.returned_at is not None:
        raise HTTPException(status_code=400, detail="Cannot edit a returned assignment")

    update_data = data.model_dump(exclude_unset=True)

    if "quantity" in update_data:
        new_quantity = update_data["quantity"]

        if new_quantity < 1:
            raise HTTPException(status_code=400, detail="Quantity must be at least 1")

        item = db.query(Item).filter(Item.id == assignment.item_id).first()
        difference = new_quantity - assignment.quantity

        if difference > 0 and item.count < difference:
            raise HTTPException(
                status_code=400, detail="Insufficient stock for this adjustment"
            )

        item.count -= difference
        assignment.quantity = new_quantity

        transaction = Transaction(
            item_id=item.id,
            quantity=-difference,
            transaction_type=TransactionType.ADJUSTMENT,
            employee_id=assignment.employee_id,
            location=assignment.location,
            notes=f"Penyesuaian jumlah assignment #{assignment.id}",
        )
        db.add(transaction)

        del update_data["quantity"]

    for key, value in update_data.items():
        setattr(assignment, key, value)

    db.commit()
    db.refresh(assignment)

    return assignment


@router.delete("/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if assignment:
        db.delete(assignment)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Assignment not found")

    return {"message": f"Assignment with id {assignment_id} successfuly deleted"}


@router.patch("/{assignment_id}/return", response_model=AssignmentResponse)
def return_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment.returned_at is not None:
        raise HTTPException(status_code=400, detail="Assignment already returned")

    item = db.query(Item).filter(Item.id == assignment.item_id).first()
    item.count += assignment.quantity

    assignment.returned_at = datetime.now(timezone.utc)

    transaction = Transaction(
        item_id=item.id,
        quantity=assignment.quantity,
        transaction_type=TransactionType.RETURN,
        employee_id=assignment.employee_id,
        location=assignment.location,
        notes="Barang dikembalikan",
    )
    db.add(transaction)

    db.commit()
    db.refresh(assignment)

    return assignment

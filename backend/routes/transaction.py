from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from models.employee import Employee
from database import get_db
from models.item import Item
from models.enums import ItemType, TransactionType
from models.transaction import Transaction

from schemas.transaction import StockTransactionResponse, StockWithdrawRequest
from schemas.pagination import Page

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/items/{item_id}/withdraw", response_model=StockTransactionResponse)
def withdraw_material(
    item_id: int, data: StockWithdrawRequest, db: Session = Depends(get_db)
):
    item = db.query(Item).filter(Item.id == item_id, Item.is_active == True).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.type != ItemType.MATERIAL:
        raise HTTPException(
            status_code=400, detail="This route is only for material-type items"
        )

    if item.count < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    item.count -= data.quantity

    transaction = Transaction(
        item_id=item.id,
        quantity=-data.quantity,
        transaction_type=TransactionType.WITHDRAW,
        employee_id=data.employee_id,
        location=data.location,
        notes=data.notes,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


@router.get("/items/{item_id}/history", response_model=Page[StockTransactionResponse])
def get_item_history(
    item_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    type: Optional[TransactionType] = Query(None),
    quantity: Optional[int] = Query(None),
    employee: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    notes: Optional[str] = Query(None),
    created_at: Optional[str] = Query(None, description="dd/mm/yyyy"),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    base_query = (
        db.query(Transaction)
        .options(joinedload(Transaction.employee), joinedload(Transaction.item))
        .outerjoin(Employee, Transaction.employee_id == Employee.id)
        .filter(Transaction.item_id == item_id)
    )

    if type:
        base_query = base_query.filter(Transaction.transaction_type == type)

    if quantity is not None:
        base_query = base_query.filter(Transaction.quantity == quantity)

    if employee:
        full_name = func.concat(
            func.coalesce(Employee.first_name, ""), " ", func.coalesce(Employee.last_name, "")
        )
        base_query = base_query.filter(full_name.ilike(f"%{employee}%"))

    if location:
        base_query = base_query.filter(Transaction.location.ilike(f"%{location}%"))

    if notes:
        base_query = base_query.filter(Transaction.notes.ilike(f"%{notes}%"))

    if created_at:
        try:
            parsed_date = datetime.strptime(created_at, "%d/%m/%Y").date()
            base_query = base_query.filter(func.date(Transaction.created_at) == parsed_date)
        except ValueError:
            pass

    sort_map = {
        "type": Transaction.transaction_type,
        "quantity": Transaction.quantity,
        "employee": Employee.first_name,
        "location": Transaction.location,
        "notes": Transaction.notes,
        "created_at": Transaction.created_at,
    }
    sort_column = sort_map.get(sort_by, Transaction.created_at)
    base_query = base_query.order_by(
        sort_column.asc() if sort_order == "asc" else sort_column.desc(),
        Transaction.id.asc()
    )

    total = base_query.count()

    transactions = base_query.offset((page - 1) * page_size).limit(page_size).all()

    return Page[StockTransactionResponse].create(
        items=transactions, total=total, page=page, page_size=page_size
    )

@router.get("/", response_model=list[StockTransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    return (
        db.query(Transaction)
        .options(joinedload(Transaction.item), joinedload(Transaction.employee))
        .order_by(Transaction.created_at.desc())
        .all()
    )

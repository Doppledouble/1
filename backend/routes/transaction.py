from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models.item import Item
from models.enums import ItemType, TransactionType
from models.transaction import Transaction

from schemas.transaction import StockTransactionResponse, StockWithdrawRequest

router = APIRouter(prefix="/transactions",tags=["Transactions"])

@router.post("/items/{item_id}/withdraw", response_model=StockTransactionResponse)
def withdraw_material(item_id: int, data: StockWithdrawRequest, db: Session = Depends(get_db)):
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.is_active == True
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.type != ItemType.MATERIAL:
        raise HTTPException(status_code=400, detail="This route is only for material-type items")

    if item.count < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    item.count -= data.quantity

    transaction = Transaction(
        item_id=item.id,
        quantity=-data.quantity,
        transaction_type=TransactionType.WITHDRAW,
        employee_id=data.employee_id,
        location=data.location,
        notes=data.notes
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction

   
@router.get("/items/{item_id}/history", response_model=list[StockTransactionResponse])
def get_item_history(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return (
        db.query(Transaction)
        .options(
            joinedload(Transaction.employee),
            joinedload(Transaction.item))  # avoid N+1
        .filter(Transaction.item_id == item_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )


@router.get("/", response_model=list[StockTransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    return (
        db.query(Transaction)
        .options(
            joinedload(Transaction.item),
            joinedload(Transaction.employee)
        )
        .order_by(Transaction.created_at.desc())
        .all()
    )
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone

from models.assignment import Assignment
from database import get_db
from models.item import Item
from schemas.item import ItemCreate, ItemUpdate, ItemResponse
from models.transaction import Transaction
from models.enums import TransactionType, ItemType


router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    
    existing_item = db.query(Item).filter(
        Item.name == item.name,
        Item.is_active == False
    ).first()

    if existing_item:
        existing_item.is_active = True
        existing_item.category = item.category
        existing_item.type = item.type
        existing_item.count = item.count
        existing_item.unit = item.unit

        db.flush()

        transaction = Transaction(
            item_id=existing_item.id,
            quantity=item.count,
            transaction_type=TransactionType.ADD,
            created_at=item.inventory_date or datetime.now(timezone.utc)
        )

        db.add(transaction)
        db.commit()
        db.refresh(existing_item)

        return existing_item

    new_item = Item(
        name=item.name,
        category=item.category,
        type=item.type,
        count=item.count,
        unit=item.unit,
        is_active=True
    )

    db.add(new_item)
    db.flush()

    transaction = Transaction(
        item_id=new_item.id,
        quantity=item.count,
        transaction_type=TransactionType.ADD,
        created_at=item.inventory_date or datetime.now(timezone.utc)
    )

    db.add(transaction)
    db.commit()
    db.refresh(new_item)

    return new_item


@router.get("/", response_model=list[ItemResponse])
def get_items(db: Session = Depends(get_db)):
    return db.query(Item).filter(Item.is_active == True).all()


@router.get("/tool", response_model=list[ItemResponse])
def get_tool(db: Session = Depends(get_db)):
    return db.query(Item).filter(
        Item.is_active == True,
        Item.type == ItemType.TOOL).all()
    
    
@router.get("/material", response_model=list[ItemResponse])
def get_material(db: Session = Depends(get_db)):
    return db.query(Item).filter(
        Item.is_active == True,
        Item.type == ItemType.MATERIAL).all()    


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.is_active == True
        ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@router.patch("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: Session = Depends(get_db)
):
    item = db.query(Item).filter(Item.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_data.model_dump(exclude_unset=True)

    old_count = item.count
    new_count = update_data.get("count", old_count)
    difference = new_count - old_count
    
    for key, value in update_data.items():
        setattr(item, key, value)   
        
    if difference != 0:    
        transaction = Transaction(
            item_id= item.id,
            quantity= difference,
            transaction_type= TransactionType.ADJUSTMENT
        )
        db.add(transaction)

    db.commit()
    db.refresh(item)

    return item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.is_active == True
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    active_assignment = db.query(Assignment).filter(
        Assignment.item_id == item_id,
        Assignment.returned_at.is_(None) 
    ).first()

    if active_assignment:
        raise HTTPException(
            status_code=400,
            detail="Item cannot be deleted while it is currently assigned to an employee"
        )

    item.count = 0
    item.is_active = False
    
    transaction = Transaction(
        item_id = item.id,
        quantity =- item.count,
        transaction_type = TransactionType.REMOVE,
        notes="Item dihapus dari inventori" 
    )
   
    db.add(transaction)
    db.commit()

    return {"message": f"Item {item.name} successfully deleted"}
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud
from database import engine, get_db

# Створюємо таблиці в БД
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts API")

@app.post("/contacts/", response_model=schemas.ContactResponse)
def create(contact: schemas.ContactBase, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact)

@app.get("/contacts/", response_model=List[schemas.ContactResponse])
def read_all(name: str = None, last_name: str = None, email: str = None, db: Session = Depends(get_db)):
    return crud.get_contacts(db, name, last_name, email)

@app.get("/contacts/birthdays", response_model=List[schemas.ContactResponse])
def birthdays(db: Session = Depends(get_db)):
    return crud.get_upcoming_birthdays(db)

@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def read_one(contact_id: int, db: Session = Depends(get_db)):
    contact = crud.get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Not found")
    return contact

@app.delete("/contacts/{contact_id}")
def delete(contact_id: int, db: Session = Depends(get_db)):
    crud.delete_contact(db, contact_id)
    return {"status": "deleted"}
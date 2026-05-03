from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models, schemas

def create_contact(db: Session, contact: schemas.ContactBase):
    db_contact = models.Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, name: str = None, last_name: str = None, email: str = None):
    query = db.query(models.Contact)
    if name:
        query = query.filter(models.Contact.first_name.ilike(f"%{name}%"))
    if last_name:
        query = query.filter(models.Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(models.Contact.email.ilike(f"%{email}%"))
    return query.all()

def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()

def delete_contact(db: Session, contact_id: int):
    contact = get_contact(db, contact_id)
    if contact:
        db.delete(contact)
        db.commit()
    return contact

def get_upcoming_birthdays(db: Session):
    today = datetime.today().date()
    end_date = today + timedelta(days=7)
    all_contacts = db.query(models.Contact).all()
    upcoming = []
    for contact in all_contacts:
        bday_this_year = contact.birthday.replace(year=today.year)
        if today <= bday_this_year <= end_date:
            upcoming.append(contact)
    return upcoming
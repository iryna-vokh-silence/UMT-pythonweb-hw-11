from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models, schemas, auth


def create_contact(db: Session, contact: schemas.ContactBase, user: models.User):
    db_contact = models.Contact(**contact.model_dump(), owner_id=user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts(db: Session, user: models.User, name: str = None, last_name: str = None, email: str = None):
    query = db.query(models.Contact).filter(models.Contact.owner_id == user.id)
    if name:
        query = query.filter(models.Contact.first_name.ilike(f"%{name}%"))
    if last_name:
        query = query.filter(models.Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(models.Contact.email.ilike(f"%{email}%"))
    return query.all()


def get_contact(db: Session, contact_id: int, user: models.User):
    return db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.owner_id == user.id,
    ).first()


def delete_contact(db: Session, contact_id: int, user: models.User):
    contact = get_contact(db, contact_id, user)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


def get_upcoming_birthdays(db: Session, user: models.User):
    today = datetime.today().date()
    end_date = today + timedelta(days=7)
    all_contacts = db.query(models.Contact).filter(models.Contact.owner_id == user.id).all()
    upcoming = []
    for contact in all_contacts:
        bday_this_year = contact.birthday.replace(year=today.year)
        if today <= bday_this_year <= end_date:
            upcoming.append(contact)
    return upcoming


def update_contact(db: Session, contact_id: int, body: schemas.ContactBase, user: models.User):
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.owner_id == user.id,
    ).first()
    if db_contact:
        db_contact.first_name = body.first_name
        db_contact.last_name = body.last_name
        db_contact.email = body.email
        db_contact.phone = body.phone
        db_contact.birthday = body.birthday
        db_contact.additional_data = body.additional_data
        db.commit()
        db.refresh(db_contact)
    return db_contact


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    new_user = models.User(
        email=user.email,
        password=auth.get_password_hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def verify_user(db: Session, email: str):
    user = get_user_by_email(db, email)
    if user and not user.is_verified:
        user.is_verified = True
        db.commit()
        db.refresh(user)
    return user


def update_user_avatar(db: Session, user: models.User, url: str):
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user

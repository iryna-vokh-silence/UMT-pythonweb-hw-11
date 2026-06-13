from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import models, schemas, crud, auth
from database import engine, get_db
from email_service import send_verification_email
import cloudinary
import cloudinary.uploader
from config import settings

models.Base.metadata.create_all(bind=engine)

cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Contacts API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Auth ---

@app.post("/auth/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, body.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    user = crud.create_user(db, body)
    token = auth.create_email_token(user.email)
    try:
        await send_verification_email(user.email, token)
    except Exception as e:
        print(f"[EMAIL] Could not send verification email: {e}")
        print(f"[EMAIL] Verification URL: http://localhost:8000/auth/verify/{token}")
    return user


@app.post("/auth/login", response_model=schemas.TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, body.username)
    if not user or not auth.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/verify/{token}", response_model=schemas.UserResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    email = auth.decode_email_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")
    user = crud.verify_user(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --- User ---

@app.get("/users/me", response_model=schemas.UserResponse)
@limiter.limit("10/minute")
async def get_me(request: Request, current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@app.patch("/users/avatar", response_model=schemas.UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    result = cloudinary.uploader.upload(
        file.file,
        public_id=f"avatars/{current_user.email}",
        overwrite=True,
    )
    url = result["secure_url"]
    return crud.update_user_avatar(db, current_user, url)


# --- Contacts ---

@app.post("/contacts/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create(contact: schemas.ContactBase, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_contact(db, contact, current_user)


@app.get("/contacts/", response_model=List[schemas.ContactResponse])
def read_all(name: str = None, last_name: str = None, email: str = None, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.get_contacts(db, current_user, name, last_name, email)


@app.get("/contacts/birthdays", response_model=List[schemas.ContactResponse])
def birthdays(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.get_upcoming_birthdays(db, current_user)


@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def read_one(contact_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    contact = crud.get_contact(db, contact_id, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Not found")
    return contact


@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update(contact_id: int, body: schemas.ContactBase, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    contact = crud.update_contact(db, contact_id, body, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Not found")
    return contact


@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(contact_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    contact = crud.delete_contact(db, contact_id, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Not found")
    return None

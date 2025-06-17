from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta
import os
import secrets
from models import User, RefreshToken, RefreshTokenRequest, UserResponse, UserUpdateRequest
from db import get_db

SECRET_KEY = os.environ.get("SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 1


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    # Look for user in DB and verify password
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def cleanup_expired_tokens(db: Session):
    # Remove all expired refresh tokens from database
    current_time = datetime.utcnow()
    deleted_count = db.query(RefreshToken).filter(
        RefreshToken.expires_at < current_time
    ).delete()
    db.commit()
    return deleted_count


def create_refresh_token(db: Session, user_id: int):
    # Clean up expired tokens globally
    cleanup_expired_tokens(db)

    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    # Delete old refresh tokens for this user (complete removal)
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id
    ).delete()

    # Create new refresh token
    refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(refresh_token)
    db.commit()

    return token


def verify_refresh_token(db: Session, token: str):
    # Clean up expired tokens before verification
    cleanup_expired_tokens(db)

    # Look for token in DB
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == token,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()

    # Token not found in DB
    if not refresh_token:
        return None

    # Search for user and return it based on refresh token
    user = db.query(User).filter(User.id == refresh_token.user_id).first()
    return user


def revoke_refresh_token(db: Session, token: str):
    # Delete the refresh token completely
    db.query(RefreshToken).filter(RefreshToken.token == token).delete()
    db.commit()


def revoke_all_user_tokens(db: Session, user_id: int):
    # Delete all tokens of a specific user
    deleted_count = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id
    ).delete()
    db.commit()
    return deleted_count


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kon credentialen niet verifiëren",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Niet de benodigde toestemming")
    return current_user


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "access":
            raise HTTPException(status_code=403, detail="Token is invalide of verlopen.")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalide of verlopen.")


from main import app, get_db


@app.post("/token", tags=["Authentication"])
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """
    Login with username and password to get access token and refresh token
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrecte gebruikersnaam of wachtwoord")

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(db, user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@app.post("/token/refresh", tags=["Authentication"])
async def refresh_access_token(
        request: RefreshTokenRequest,
        db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    user = verify_refresh_token(db, request.refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalide of verlopen refresh token"
        )

    # Create new access token
    access_token = create_access_token(data={"sub": user.username})

    # Create a new refresh token for token rotation
    new_refresh_token = create_refresh_token(db, user.id)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@app.post("/token/revoke", tags=["Authentication"])
async def revoke_token(
        request: RefreshTokenRequest,
        db: Session = Depends(get_db)
):
    """
    Revoke refresh token
    """
    revoke_refresh_token(db, request.refresh_token)
    return {"message": "Token is succesvol ingetrokken"}


@app.post("/logout", tags=["Authentication"])
async def logout(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Logout and revoke all refresh tokens
    """
    deleted_count = revoke_all_user_tokens(db, current_user.id)
    return {"message": f"Succesvol uitgelogd. {deleted_count} aantal tokens weggehaald."}


@app.post("/users/", tags=["Authentication"])
def create_user(
        username: str,
        password: str,
        role: str = "user",
        db: Session = Depends(get_db),
        admin: User = Depends(get_current_admin_user)
):
    """
    Create a new user based on username and password
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        raise HTTPException(status_code=400, detail="Gebruikersnaam bestaat al!")
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"username": new_user.username, "role": new_user.role}


@app.get("/me", tags=["Authentication"])
def read_users_me(
        current_user: User = Depends(get_current_user)
):
    """
    Returns username and role
    """
    return {"username": current_user.username, "role": current_user.role}


@app.get("/verify-token/{token}", tags=["Authentication"])
async def verify_user_token(
        token: str
):
    """
    Verify access token
    """
    verify_token(token=token)
    return {"message": "Token is valide"}


@app.get("/users/", tags=["Authentication"], response_model=list[UserResponse])
def list_users(
        db: Session = Depends(get_db),
        admin: User = Depends(get_current_admin_user)
):
    """
    List all users
    """
    users = db.query(User).all()

    if not users:
        raise HTTPException(status_code=404, detail="Geen gebruikers gevonden")

    return users


@app.put("/users/{user_id}", tags=["Authentication"], response_model=UserResponse)
def update_user(
        user_id: int,
        user_update: UserUpdateRequest,
        db: Session = Depends(get_db),
        admin: User = Depends(get_current_admin_user)
):
    """
    Update user by ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Gebruiker niet gevonden")

    # Check if username is being changed and if it's already taken
    if user_update.username and user_update.username != user.username:
        existing_user = db.query(User).filter(User.username == user_update.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Gebruikersnaam is al in gebruik")
        user.username = user_update.username

    # Update password if provided
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)
        revoke_all_user_tokens(db, user.id)

    # Update role if provided
    if user_update.role:
        user.role = user_update.role

    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}", tags=["Authentication"])
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        admin: User = Depends(get_current_admin_user)
):
    """
    Delete user by ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Gebruiker niet gevonden")

    # Prevent admin from deleting themselves
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Het is niet mogelijk om je eigen account te verwijderen")

    # Revoke all refresh tokens before deletion
    revoke_all_user_tokens(db, user.id)

    # Delete the user
    db.delete(user)
    db.commit()

    return {"message": f"Gebruiker '{user.username}' succesvol verwijderd!"}
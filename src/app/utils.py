from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from services.auth_service import SECRET_KEY, ALGORITHM

async def get_token_from_cookie(request: Request):
    # Get token from cookie
    token = request.cookies.get("access_token")
    if not token:
        return None
    if token.startswith("Bearer "):
        return token.replace("Bearer ", "")
    return token

async def get_current_user_from_cookie(
    request: Request,
    db: Session
):
    # Define exception for authentication failures
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"}
    )
    token = await get_token_from_cookie(request)
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    from db.models.User import User
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user

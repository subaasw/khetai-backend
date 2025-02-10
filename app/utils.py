import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import httpx
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from config import SPARROW_API, SPARROW_TOKEN

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(uid: str, phone: str, expires_delta: timedelta = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(phone), "uid": uid}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        if "sub" not in payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload.get('sub')
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    payload = verify_access_token(token)
    return payload["sub"]

def get_current_farmer_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = verify_access_token(token)
    farmer_id: int = int(payload.get("uid"))
    if farmer_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return farmer_id


async def send_otp_to_sparrow(phone: int, otp: str):
    payload = {
        'token': SPARROW_TOKEN,
        'from':'MVIC Tech Titans',
        'to': phone,
        'text':f'Here is your otp: {otp}'
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SPARROW_API, json=payload)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return {"message": "Data sent successfully", "response": response.json()}

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

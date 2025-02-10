from typing import Optional, List
from pydantic import BaseModel

class FarmerLogin(BaseModel):
    phone: str

class FarmerRegister(BaseModel):
    phone: str
    name: str
    location: str

class UserRegister(BaseModel):
    phone: str
    name: str
    location: str

class UserLogin(BaseModel):
    phone: str

class OTPVerifySchema(BaseModel):
    phone: str
    otp_code: str

class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    image: str = None

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    images: Optional[list[str]] = None

    
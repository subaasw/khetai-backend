from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import Column, JSON

class Farmer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(unique=True, index=True)
    name: str
    location: str
    verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    products: List["Products"] = Relationship(back_populates="farmer")

class VerifyOtp(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(unique=True, index=True)
    otp_code: str
    otp_expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Products(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    price: float
    category: str = Field(default='Fruits')
    image: str = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    farmer_id: int = Field(foreign_key="farmer.id")

    farmer: Optional["Farmer"] = Relationship(back_populates="products")

# User Model
class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(unique=True, index=True)
    name: str
    location: str
    verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_type: str = Field(default="user")

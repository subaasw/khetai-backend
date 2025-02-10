import random
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, Request, status, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import Farmer, VerifyOtp, Products, Users
from schemas import FarmerLogin, FarmerRegister, OTPVerifySchema, ProductCreate, ProductUpdate, UserLogin, UserRegister
from utils import create_access_token, verify_access_token, get_current_farmer_id
from typing import List

from services import voice_to_text_converter
from services.diseases_detection import predict_image_class
from services.chatbot import chat_with_openai

from uploader import ImageUploader, AudioUploader
from config import PRODUCTS_DIR, USERS_DIR, VOICES_DIR

product_image_uploader = ImageUploader(PRODUCTS_DIR)
user_image_uploader = ImageUploader(USERS_DIR)
voice_uploader = AudioUploader(VOICES_DIR)

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/farmer/login")
def farmer_login(login_data: FarmerLogin, session: Session = Depends(get_session)):
    farmer = session.exec(select(Farmer).where(Farmer.phone == login_data.phone)).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    if not farmer.verified:
        raise HTTPException(status_code=403, detail="Phone number not verified")
    return {"message": "Login successful", "farmer_id": farmer.id, "name": farmer.name, "location": farmer.location, "phone": farmer.phone}

@app.post("/farmer/register")
def register_farmer(data: FarmerRegister, session: Session = Depends(get_session)):
    existing_farmer = session.exec(select(Farmer).where(Farmer.phone == data.phone)).first()
    if existing_farmer:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    new_farmer = Farmer(phone=data.phone, name=data.name, location=data.location)
    session.add(new_farmer)
    session.commit()
    session.refresh(new_farmer)
    return {"message": "Farmer registered successfully", "farmer_id": new_farmer.id}

@app.post("/farmer/request-otp")
async def request_otp(phone: str, session: Session = Depends(get_session)):
    otp = str(random.randint(100000, 999999))
    otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
    farmer = session.exec(select(Farmer).where(Farmer.phone == phone)).first()
    if not farmer:
        farmer = Farmer(phone=phone, verified=False)
        session.add(farmer)
        session.commit()
    otp_entry = session.exec(select(VerifyOtp).where(VerifyOtp.phone == phone)).first()
    if otp_entry:
        otp_entry.otp_code = otp
        otp_entry.otp_expires_at = otp_expiry
    else:
        otp_entry = VerifyOtp(phone=phone, otp_code=otp, otp_expires_at=otp_expiry)
        session.add(otp_entry)

    # await send_otp_to_sparrow(farmer.phone, otp)

    session.commit()
    return {"message": "OTP sent successfully", "otp": otp}

@app.post("/farmer/verify-otp")
def verify_otp(data: OTPVerifySchema, session: Session = Depends(get_session)):
    farmer = session.exec(select(Farmer).where(Farmer.phone == data.phone)).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    otp_entry = session.exec(select(VerifyOtp).where((VerifyOtp.otp_code == data.otp_code) & (VerifyOtp.phone == data.phone))).first()
    if not otp_entry:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if datetime.now(timezone.utc) > otp_entry.otp_expires_at.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")
    farmer.verified = True
    session.delete(otp_entry)
    session.commit()
    access_token = create_access_token(farmer.id, farmer.phone)

    response = JSONResponse({"message": "OTP verified successfully, farmer is now verified"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  
        secure=False,    
        samesite="none"
    )

    return response

@app.get("/farmer/me")
def get_current_farmer(request: Request, session: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")

    phone = verify_access_token(token)
    farmer = session.exec(select(Farmer).where(Farmer.phone == phone)).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    return {
        "id": farmer.id,
        "phone": farmer.phone,
        "name": farmer.name,
        "location": farmer.location,
        "verified": farmer.verified
    }

@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(
    request: Request,
    product: ProductCreate,
    session: Session = Depends(get_session)
):
    token = request.cookies.get("access_token")
    farmer = session.exec(select(Farmer).where(Farmer.phone == token)).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    new_product = Products(
        title=product.title,
        description=product.description,
        price=product.price,
        images=product.image,
        farmer_id=farmer.id
    )

    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return new_product

@app.get("/products/{product_id}", response_model=Products)
def read_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Products, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    session: Session = Depends(get_session),
    farmer_id: int = Depends(get_current_farmer_id)
):
    product = session.get(Products, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.farmer_id != farmer_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")

    session.delete(product)
    session.commit()

    return {"detail": "Product deleted successfully"}

@app.put("/products/{product_id}", response_model=Products)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    session: Session = Depends(get_session),
    farmer_id: int = Depends(get_current_farmer_id)
):
    product = session.get(Products, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.farmer_id != farmer_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this product")

    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    session.add(product)
    session.commit()
    session.refresh(product)

    return product

# File Uploads
@app.post("/upload/product-image/")
async def upload_product_image(file: UploadFile = File(...)):
    try:
        file_path = await product_image_uploader.save_file(file)
        return {"file_path": str(file_path)}
    except HTTPException as e:
        raise e

@app.post("/upload/user-images/")
async def upload_user_images(files: List[UploadFile] = File(...)):
    try:
        file_paths = await user_image_uploader.save_files(files)
        return {"file_paths": [str(path) for path in file_paths]}
    except HTTPException as e:
        raise e

@app.post("/upload/voice")
async def upload_voice(file: UploadFile = File(...)):
    try:
        await voice_uploader.save_file(file)
        text = await voice_to_text_converter('uploads/voices/' + file.filename)
        return {"text": text}
    except HTTPException as e:
        raise e
    
@app.post("/diseases-detect")
async def diseases_detection(file: UploadFile):
    try:
        image_path = await product_image_uploader.save_file(file)
        prediction = predict_image_class(image_path)
        return {"prediction": prediction}
    except HTTPException as e:
        raise e

@app.post("/chat")
async def ai_chat(message: str):
    res = await chat_with_openai(message)
    return {"res": res}

# User Routes
@app.post("/user/login")
def user_login(login_data: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(Users).where(Users.phone == login_data.phone)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Farmer not found")
    if not user.verified:
        raise HTTPException(status_code=403, detail="Phone number not verified")
    return {"message": "Login successful", "user_id": user.id, "name": user.name, "location": user.location, "phone": user.phone}

@app.post("/user/register")
def register_user(data: UserRegister, session: Session = Depends(get_session)):
    existing_user = session.exec(select(Users).where(Users.phone == data.phone)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    new_user = Users(phone=data.phone, name=data.name, location=data.location)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}

@app.get("/user/me")
def get_current_user(request: Request, session: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")

    phone = verify_access_token(token)
    user = session.exec(select(Users).where(user.phone == phone)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "phone": user.phone,
        "name": user.name,
        "location": user.location,
        "verified": user.verified
    }

@app.get("/")
async def home():
    return {"message": "Welcome to KethAI!"}


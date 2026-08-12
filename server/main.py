import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.member import router as member_router
from database.connection import engine, Base

# DB의 테이블 확인 및 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORSMiddleware 추가
origins = os.getenv(
    "FRONT_ORIGINS","http://localhost:3000,http://localhost:5173" 
    ).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

app.include_router(member_router, prefix="/api/member", tags=["member"])   
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#from routes.auth import router as auth_router
from routes.ai import router as ai_router
from routes.bike import router as bike_router
from routes.chat import router as chat_router
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

#app.include_router(auth_router, prefix="/auth", tags=["auth"])   
app.include_router(ai_router, prefix="/api/ai/bike", tags=["ai"])   
app.include_router(bike_router, prefix="/api/bike/seoul", tags=["bike"])   
app.include_router(chat_router, prefix="/api/chat", tags=["chatbot"])   
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
# 1. OpenAI 대신 AsyncOpenAI를 import 합니다.
from openai import AsyncOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# 2. AsyncOpenAI 클라이언트로 생성합니다.
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("")
async def chat_with_ai(request: ChatRequest):
    print("1. 프론트엔드 요청 도착:", request.message)
    
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY가 설정되지 않았습니다.")

    try:
        print("2. OpenAI API 호출 시작...")
        # 3. AsyncOpenAI + await 연동
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "당신은 서울시 따릉이 서비스 안내 친절한 AI 도우미입니다."},
                {"role": "user", "content": request.message},
            ],
            temperature=0.7,
        )
        
        ai_message = response.choices[0].message.content
        print("3. OpenAI 응답 완료:", ai_message)

        return {"status": "success", "answer": ai_message}

    except Exception as e:
        print("4. API 호출 에러 발생:", str(e))
        raise HTTPException(status_code=500, detail=f"OpenAI API 호출 오류: {str(e)}")
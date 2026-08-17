import os
import joblib
import pandas as pd
from fastapi import APIRouter, Path, Depends, Response, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from schemas.bikeforecast import BikeForecastRequest


router = APIRouter()

# 모델 경로 설정
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ai", "model", "bike_demand_model.pkl")

# 모델 파일 로드
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"⚠️ 모델 로드 실패: {e}")
    model = None

# bike 수요 예측
@router.post("/bike/forecast")
async def bike_forecast(payload : BikeForecastRequest) -> dict:
    if model is None:
        raise HTTPException(status_code=500, detail="모델이 로드되지 않았습니다.")

    try:
        # Pydantic 객체를 딕셔너리로 변환 후 DataFrame 생성
        raw_dict = payload.model_dump()
        df = pd.DataFrame([raw_dict])

        # 학습 때와 동일한 전처리 수행
        date_series = pd.to_datetime(df['date'])
        df['month'] = date_series.dt.month
        df['dayofweek'] = date_series.dt.dayofweek
        df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)

        # boolean -> int 변환 / 모델 feature 명과 동일하게 설정
        df['holiday'] = df['is_holiday'].astype(int)

        # 학습 시 사용했던 순서 그대로 피처 컬럼 정렬
        FEATURE_COLUMNS = [
            'hour', 
            'temperature', 
            'humidity', 
            'wind_speed', 
            'rainfall', 
            'holiday', 
            'month', 
            'dayofweek', 
            'is_weekend'
        ]

        X = df[FEATURE_COLUMNS]

        # 모델 예측
        prediction = model.predict(X)
        
        # 음수가 나올 수 있는 회귀 모델 특성 방지 (대여량 최소 0)
        predicted_value = max(0, int(round(prediction[0])))

        return {
            "status": "success",
            "predicted_rentals": predicted_value
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"예측 처리 실패: {str(e)}")
from pydantic import BaseModel
from datetime import date

# 프론트엔드 Payload 스키마 정의
class RentalPredictionPayload(BaseModel):
    station_id: int | str
    date: date  
    hour: int
    is_holiday: int  
    temperature: float
    humidity: float
    rainfall: float
    wind_speed: float

    # 모델 학습에는 미사용 (선택적 수신 처리)
    recent_1h_rental_count: float | None = None
    prev_day_same_hour_rental_count: float | None = None
    rolling_7d_same_hour_avg: float | None = None


# 응답 스키마 정의
class DemandPredictionResponse(BaseModel):
    predicted_demand: float
    demand_level: str
    shortage_risk: bool
    message: str
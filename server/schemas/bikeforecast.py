from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from datetime import date, time


# AI 활용 bike 수요 예측에 입력으로 받을 값
class BikeForecastRequest(BaseModel):
    station_id: int
    date: date              # "2026-08-17"
    hour: int               # 3
    is_holiday: bool
    temperature: float
    humidity: float
    rainfall: float
    wind_speed: float
    recent_hourly_rentals: int
    prev_day_same_hour_rentals: int
    rolling_7d_same_hour_avg: float = Field(validation_alias="rolling7dSameHourAvg")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # snake_case로도 데이터를 받을 수 있게 허용
        json_schema_extra={
            "examples": [
                {
                    "stationId": 1,
                    "date": "2026-08-17",
                    "hour": 9,
                    "isHoliday": False,  
                    "temperature": 29.0,
                    "humidity": 50.0,
                    "rainfall": 0.0,
                    "windSpeed": 2.0,
                    "recentHourlyRentals": 28,          
                    "prevDaySameHourRentals": 31,
                    "rolling7dSameHourAvg": 29.0
                }
            ]
        }
    )
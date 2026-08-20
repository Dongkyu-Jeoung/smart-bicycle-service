from pydantic import BaseModel, Field, ConfigDict
from datetime import date

class BikeForecastRequest(BaseModel):
    station_id: int = Field(..., alias="stationId")
    date: date
    hour: int
    is_holiday: bool = Field(..., alias="isHoliday")
    temperature: float
    humidity: float
    rainfall: float
    wind_speed: float = Field(..., alias="windSpeed")
    recent_hourly_rentals: int = Field(..., alias="recentHourlyRentals")
    prev_day_same_hour_rentals: int = Field(..., alias="prevDaySameHourRentals")
    rolling_7d_same_hour_avg: float = Field(..., alias="rolling7dSameHourAvg")

    model_config = ConfigDict(
        populate_by_name=True,  # 스네이크케이스나 알리아스 이름 모두 허용
    )
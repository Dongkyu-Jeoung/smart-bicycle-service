from pydantic import BaseModel, Field


# ------------------------------------------------------------------
# Pydantic 응답 스키마 (프론트엔드가 요구하는 카멜케이스 포맷 정의)
# ------------------------------------------------------------------
class StationSchema(BaseModel):
    name: str
    available: int
    total: int


class BikeCourseResponse(BaseModel):
    id: str
    name: str
    region: str
    difficulty: str
    bike_type: str = Field(..., alias="bikeType")
    distance: str
    duration: str
    rating: float
    free: bool
    image: str
    tags: list[str] | None = None
    departure: StationSchema | dict | str | None = None
    destination: StationSchema | dict | str | None = None

    class Config:
        from_attributes = True  # ORM 모델 객체를 Pydantic으로 자동 변환
        populate_by_name = True  # bike_type -> bikeType 변환 허용
        
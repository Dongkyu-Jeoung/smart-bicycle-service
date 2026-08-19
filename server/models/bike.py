from sqlalchemy import String, Float, Boolean, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from database.connection import Base


class BikeRoutesModel(Base):
    __tablename__ = "bike_routes"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    region_tag: Mapped[str | None] = mapped_column(String(50), nullable=True)  # regionTag
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    bike_type: Mapped[str] = mapped_column(String(50), nullable=False)  # bikeType
    distance: Mapped[str] = mapped_column(String(20), nullable=False)
    duration: Mapped[str] = mapped_column(String(20), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0) # reviewCount
    free: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    image: Mapped[str] = mapped_column(String(500), nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    
    # 출발/도착지 정보 (문자열 또는 Dict 구조 모두 저장 가능하도록 JSON 활용)
    departure: Mapped[dict | str | None] = mapped_column(JSON, nullable=True)
    destination: Mapped[dict | str | None] = mapped_column(JSON, nullable=True)

    # 목업 데이터의 추가 필드들
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    elevation_gain: Mapped[str | None] = mapped_column(String(50), nullable=True)     # elevationGain
    max_elevation: Mapped[str | None] = mapped_column(String(50), nullable=True)      # maxElevation
    completion_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)        # completionRate
    participants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    season: Mapped[str | None] = mapped_column(String(50), nullable=True)
    safety_tips: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)         # safetyTips
    elevation_profile: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)  # elevationProfile
import requests
import math
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.connection import get_db
from models.bike import BikeRoutesModel
from schemas.bike import BikeCourseResponse
from dotenv import load_dotenv

router = APIRouter()

# 따릉이 data API KEY 불러오기
load_dotenv()
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")

# 사용할 위도,경도 정보(강남역 사거리) -> 유저 위치 정보 대체 예정
USER_LAT = 37.497952  # 기준 위도 (Latitude)
USER_LNG = 127.027619  # 기준 경도 (Longitude)

# 두 위경도(GPS 좌표) 사이의 거리(m 또는 km)를 구하는 하버스인(Haversine) 함수
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    두 위도/경도 지점 간의 대권 거리(Direct Distance)를 km 단위로 계산
    """
    R = 6371.0  # 지구 반지름 (km)

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance  # km 단위 반환


# ------------------------------------------------------------------------------
# '따릉이 루트' 탭 :: DB의 전체 루트 중 '따릉이' 타입으로 저장된 routes들 불러옴
# ------------------------------------------------------------------------------
@router.get("/routes", response_model=list[BikeCourseResponse])
async def get_ttareungi_routes(db: Session = Depends(get_db)):
    # bike_type 컬럼이 '따릉이'인 데이터만 필터링 조회
    stmt = select(BikeRoutesModel).where(BikeRoutesModel.bike_type == "따릉이")
    result = db.scalars(stmt).all()

    return result


# ------------------------------------------------------------------------------
# 오늘 총 이용 / 운영 대여소 / 현재 이용 중 / 평균 이용시간
# 일단 data 그대로 보내는 걸로 만듬 -> 향후 : ?
# ------------------------------------------------------------------------------
@router.get("/summary")
async def get_hero_stats():
    BIKE_HERO_STATS = [
        { 'label': "오늘 총 이용", 'value': "142,800", 'unit': "건", 'trend': "+8.4%" },
        { 'label': "운영 대여소", 'value': "2,692", 'unit': "개소", 'trend': "+2.1%" },
        { 'label': "현재 이용 중", 'value': "4,318", 'unit': "대", 'trend': "+12.3%" },
        { 'label': "평균 이용 시간", 'value': "17.4", 'unit': "분", 'trend': "-1.8%" },
    ]

    return BIKE_HERO_STATS

# ------------------------------------------------------------------------------
# { stations : 대여소 정보, hourly_usage : 시간대별 이용량 }
# 실제 작동 기능 : 사용자 위치 기반 가까운 6개 대여소
#                   이름, 거리, 사용가능 자전거, 전체 거치수, 가능 자전거 수에 따른 상태(status) 표시
# 현재 기능 : 정해진 위치(상수 선언)에서 가까운 대여소 정보 DB 호출 -> 정보 표시
# ------------------------------------------------------------------------------

@router.get("/stations")
async def get_stations():
    # 전체 대여소 수집을 위해 1,000개 단위 3개 구간 호출
    # 따릉이 전체 대여소 2700여개 BUT 한번에 1000개씩만 호출 가능
    ranges = [(1, 1000), (1001, 2000), (2001, 3000)]
    stations_data = []

    try:
        # 서울시 공공데이터 API 순회 호출
        for start, end in ranges:
            url = f"http://openapi.seoul.go.kr:8088/{SEOUL_API_KEY}/json/bikeList/{start}/{end}/"
            response = requests.get(url, timeout=5)
            data = response.json()

            if "rentBikeStatus" in data and "row" in data["rentBikeStatus"]:
                stations_data.extend(data["rentBikeStatus"]["row"])

        # 시간대별 대여수 :: mockData 가져옴
        HOURLY_USAGE = [
            { "hour": "0시", "count": 1200 }, { "hour": "1시", "count": 800 }, { "hour": "2시", "count": 500 },
            { "hour": "3시", "count": 400 }, { "hour": "4시", "count": 600 }, { "hour": "5시", "count": 1500 },
            { "hour": "6시", "count": 4000 }, { "hour": "7시", "count": 12000 }, { "hour": "8시", "count": 24500 },
            { "hour": "9시", "count": 16000 }, { "hour": "10시", "count": 10000 }, { "hour": "11시", "count": 9500 },
            { "hour": "12시", "count": 13500 }, { "hour": "13시", "count": 10500 }, { "hour": "14시", "count": 9800 },
            { "hour": "15시", "count": 10200 }, { "hour": "16시", "count": 12500 }, { "hour": "17시", "count": 21000 },
            { "hour": "18시", "count": 29500 }, { "hour": "19시", "count": 24000 }, { "hour": "20시", "count": 16000 },
            { "hour": "21시", "count": 11000 }, { "hour": "22시", "count": 7000 }, { "hour": "23시", "count": 3000 },
        ]

        if not stations_data:
            return {
                "stations": [],
                "hourlyUsage": HOURLY_USAGE
            }

        # 1. 거리 계산
        processed_stations = []
        for station in stations_data:
            try:
                st_lat = float(station.get("stationLatitude", 0))
                st_lng = float(station.get("stationLongitude", 0))

                if st_lat != 0 and st_lng != 0:
                    dist_km = calculate_distance(USER_LAT, USER_LNG, st_lat, st_lng)
                    processed_stations.append({
                        "raw_station": station,
                        "dist_km": dist_km
                    })
            except (ValueError, TypeError):
                continue

        # 2. 거리순 정렬 후 상위 6개 추출
        sorted_stations = sorted(processed_stations, key=lambda x: x["dist_km"])[:6]

        # 3. 프론트엔드 포멧 중 stations에 해당하는 형태 가공
        stations = []
        for index, item in enumerate(sorted_stations, start=1):
            st = item["raw_station"]
            dist_km = item["dist_km"]

            # 거리 문자열 포맷팅 (1km 미만: m, 1km 이상: km)
            if dist_km < 1.0:
                distance_str = f"{int(dist_km * 1000)}m"
            else:
                distance_str = f"{round(dist_km, 1)}km"

            available = int(st.get("parkingBikeTotCnt", 0))  # 대여 가능 수량
            total = int(st.get("rackTotCnt", 0))             # 총 거치대 수량

            # 대여 가능 수량에 따른 상태(status) 값 결정
            if available == 0:
                status = "EMPTY"
            elif available <= 3:
                status = "LOW"
            else:
                status = "GOOD"

            stations.append({
                "id": index,
                "name": st.get("stationName", ""),
                "distance": distance_str,
                "available": available,
                "total": total,
                "status": status
            })

        return {
            "stations": stations,
            "hourlyUsage": HOURLY_USAGE
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"데이터 요청 오류: {str(e)}"
        )
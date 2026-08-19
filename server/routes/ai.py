import os
import joblib
import pandas as pd
from fastapi import APIRouter, Path, Depends, Response, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from schemas.bikeforecast import BikeForecastRequest


router = APIRouter()

# 현재 파일 폴더(/server/routes)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 모델 경로 설정 (forecast :: 수요예측)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ai", "model", "bike_demand_model.pkl")

# CSV 파일 경로 설정 :: 월별 이용추이 / 인기대여소 TOP6에 사용
FILE_PATH_1 = os.path.join(BASE_DIR, "data", "bike_monthly_25.1-6.csv")
FILE_PATH_2 = os.path.join(BASE_DIR, "data", "bike_monthly_25.7-12.csv")
FILE_PATH_3 = os.path.join(BASE_DIR, "data", "bike_daily_2606.csv")

# 탭 제일 하단 AI INSIGHTS에 해당하는 mockdata
# 향후 실제 데이터 기반 insight 변경 가능
AI_INSIGHTS = [
  {
    "tag": "패턴",
    "icon": "TrendingUp",
    "title": "퇴근 시간 수요가 출근보다 23% 높음",
    "description": "17~19시 이용량이 7~9시 대비 평균 23.4% 높습니다. 귀가 시 자전거 이용 선호도가 뚜렷하게 증가하는 추세입니다.",
    "metricLabel": "퇴근 vs 출근",
    "metricValue": "+23.4%",
    "tone": "up",
  },
  {
    "tag": "날씨",
    "icon": "CloudRain",
    "title": "강수 시 이용률 67% 급감",
    "description": "비 오는 날 이용량이 맑은 날 대비 67% 감소합니다. 날씨 예보 연동 실시간 재고 분산 전략이 필요합니다.",
    "metricLabel": "비 vs 맑음",
    "metricValue": "-67%",
    "tone": "down",
  },
  {
    "tag": "이용자",
    "icon": "Users",
    "title": "20~30대가 전체 이용의 62% 점유",
    "description": "핵심 이용층은 20대(34.1%)와 30대(28.4%)입니다. 40~50대 유입 확대를 위한 생활형 루트 콘텐츠 강화가 효과적입니다.",
    "metricLabel": "20~30대 비중",
    "metricValue": "62%",
    "tone": "neutral",
  },
  {
    "tag": "패턴",
    "icon": "Zap",
    "title": "평균 이동 거리 2.8km, 10분 미만 68%",
    "description": "전체 대여의 68%가 10분 미만 단거리 이용입니다. 지하철역 반경 500m 내 대여소 밀도 확충이 핵심 과제입니다.",
    "metricLabel": "평균 이동 거리",
    "metricValue": "2.8km",
    "tone": "neutral",
  },
  {
    "tag": "경로",
    "icon": "MapPin",
    "title": "여의나루-합정 구간 반복 이용률 1위",
    "description": "동일 구간 재이용률이 78%에 달하는 여의나루-합정 코스. 한강변 인기 코스 우선 정비 및 실시간 알림 강화를 권장합니다.",
    "metricLabel": "재이용률",
    "metricValue": "78%",
    "tone": "up",
  },
  {
    "tag": "예측",
    "icon": "Sparkles",
    "title": "봄 성수기 수요 조기 포화 예측",
    "description": "4~5월 한강변 대여소는 오후 4시부터 재고 소진율 92%에 도달. AI 모델은 2주 전부터 해당 구간 집중 보충을 권장합니다.",
    "metricLabel": "성수기 소진율",
    "metricValue": "92%",
    "tone": "up",
  },
]

# 모델 파일 로드
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"⚠️ 모델 로드 실패: {e}")
    model = None


# 25년 따릉이 월별 데이터(csv) 호출해서 월별 이용추이 / 인기대여소 TOP6 가공 함수
def load_and_process_bike_data():
    """
    두 개의 CSV 파일을 읽어서 월별 이용량(MONTHLY_USAGE) 및
    상위 대여소(TOP_STATIONS) 데이터를 가공하는 함수
    """
    # 25년 월별 따릉이 대여 데이터 로드
    try:
        df1 = pd.read_csv(FILE_PATH_1, encoding="cp949")
    except Exception:
        df1 = pd.read_csv(FILE_PATH_1, encoding="utf-8")

    try:
        df2 = pd.read_csv(FILE_PATH_2, encoding="utf-8")
    except Exception:
        df2 = pd.read_csv(FILE_PATH_2, encoding="cp949")

    full_df = pd.concat([df1, df2], ignore_index=True)

    # 문자열 타입 및 수치형 변환
    full_df["기준년월"] = full_df["기준년월"].astype(str)
    full_df["대여건수"] = pd.to_numeric(full_df["대여건수"], errors="coerce").fillna(0)

    # 월별 이용량 계산 (MONTHLY_USAGE 포맷)
    monthly_df = full_df.groupby("기준년월")["대여건수"].sum().reset_index()
    monthly_df = monthly_df.sort_values(by="기준년월")

    monthly_usage = []
    for _, row in monthly_df.iterrows():
        ym = row["기준년월"]
        month_str = f"{int(ym[-2:])}월"  # '202501' -> '1월'
        monthly_usage.append({"month": month_str, "count": int(row["대여건수"])})

    # 상위 6개 대여소 계산 (TOP_STATIONS 포맷)
    station_df = full_df.groupby("대여소명")["대여건수"].sum().reset_index()
    top_stations_df = station_df.sort_values(by="대여건수", ascending=False).head(6)

    top_stations = []
    for _, row in top_stations_df.iterrows():
        top_stations.append({
            "name": row["대여소명"],
            "count": int(row["대여건수"])
        })

    return monthly_usage, top_stations


# 26년 6월 일별 데이터 불러와서 연령대별로 대여건수 합치는 함수
def get_age_distribution():
    """
    따릉이 이용 현황 DataFrame을 입력받아 연령대별 이용 비율(%)을 반환하는 함수
    """
    df = pd.read_csv(FILE_PATH_3, encoding="cp949")

    # 컬럼명 공백 제거 (공공데이터의 ' 이용건수' 공백 대응)
    df.columns = df.columns.str.strip()

    # 이용건수 컬럼 수치형 변환
    df["이용건수"] = pd.to_numeric(df["이용건수"], errors="coerce").fillna(0)

    # 연령대 텍스트 매핑/정제 함수
    def map_age_group(age_str):
        if not isinstance(age_str, str) or not age_str.strip():
            return "기타"

        age = age_str.strip()

        if "10" in age:
            return "10대"
        elif "20" in age:
            return "20대"
        elif "30" in age:
            return "30대"
        elif "40" in age:
            return "40대"
        elif "50" in age:
            return "50대"
        elif any(k in age for k in ["60", "70", "80"]):
            return "60대+"
        else:
            return "기타"

    df["age_category"] = df["연령대"].apply(map_age_group)

    # 연령대별 이용건수 합계 계산
    age_counts = (
        df.groupby("age_category")["이용건수"].sum().reindex(
            ["10대", "20대", "30대", "40대", "50대", "60대+"], fill_value=0
        )
    )

    total_count = age_counts.sum()

    # 데이터가 없을 경우 기본 0% 처리
    if total_count == 0:
        return [
            {"age": age, "percent": 0.0}
            for age in ["10대", "20대", "30대", "40대", "50대", "60대+"]
        ]

    # 비율(%) 계산 및 반환 포맷 구성
    result = []
    for age, count in age_counts.items():
        percent = round((count / total_count) * 100, 1)
        result.append({"age": age, "percent": percent})

    return result


# 서버 구동 시 메모리에 가공 데이터를 캐싱
try:
    MONTHLY_USAGE_DATA, TOP_STATIONS_DATA = load_and_process_bike_data()
    AGE_DISTRIBUTION = get_age_distribution()
except Exception as e:
    print(f"통계 데이터 로드 실패: {e}")
    MONTHLY_USAGE_DATA, TOP_STATIONS_DATA, AGE_DISTRIBUTION = [], [], []



# bike 수요 예측
@router.post("/forecast")
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


# ---------------------------------------------------------------------------------
# AI 분석 탭 진입시 호출 되는 router
# ---------------------------------------------------------------------------------
@router.get("/analysis")
async def get_bike_analysis():

    # 서버 시작 후 캐싱한 데이터 있는지 확인
    if not MONTHLY_USAGE_DATA or not TOP_STATIONS_DATA or not AGE_DISTRIBUTION:
        raise HTTPException(
            status_code=500, detail="통계 데이터를 불러오는데 실패했습니다."
        )


    return {
        "monthlyUsage": MONTHLY_USAGE_DATA,
        "topStations": TOP_STATIONS_DATA,
        "ageDistribution": AGE_DISTRIBUTION,
        "insights" : AI_INSIGHTS
    }
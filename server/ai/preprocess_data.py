import glob
import os
import pandas as pd

# ========================================================================
# 26년 2월 ~ 6월 따릉이 시간대별 대여 정보 데이터
# 26년 2월 ~ 6월 기상청 시간대별 날씨 데이터 
# 따릉이 데이터 :: 날짜, 시간, 대여소 별 대여건수 합
# + 날씨 데이터 (날짜, 시간) 기준으로 병합
# ========================================================================


def process_and_merge_data():
    # 1. 스크립트 실행 위치 기준 상대 경로 설정 (../routes/data)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../routes/data"))

    # 데이터 저장 경로가 없는 경우 폴더 생성
    os.makedirs(DATA_DIR, exist_ok=True)

    # 2. 따릉이 대여 데이터 불러오기 (../routes/data/bike_hour_20260*.csv)
    bike_pattern = os.path.join(DATA_DIR, "bike_hour_20260[2-6]*.csv")
    bike_files = sorted(glob.glob(bike_pattern))
    print(f"데이터 탐색 경로: {DATA_DIR}")
    print(f"발견된 따릉이 데이터 파일 목록: {bike_files}")

    if not bike_files:
        raise FileNotFoundError(
            f"'{DATA_DIR}' 경로에서 따릉이 데이터(bike_hour_20260*.csv)를 찾을 수 없습니다."
        )

    bike_df_list = []
    for file in bike_files:
        try:
            df = pd.read_csv(file, encoding="utf-8-sig")
        except UnicodeDecodeError:
            df = pd.read_csv(file, encoding="cp949")
        bike_df_list.append(df)

    bike_df = pd.concat(bike_df_list, ignore_index=True)

    # 컬럼명 정리 및 타입 변환
    bike_df["대여시간"] = bike_df["대여시간"].astype(int)
    bike_df["대여소번호"] = (
        bike_df["대여소번호"].astype(str).str.zfill(5)
    )  # 대여소번호 5자리 유지

    # [대여일자, 대여시간, 대여소번호] 기준 이용건수 합산
    bike_grouped = (
        bike_df.groupby(["대여일자", "대여시간", "대여소번호"], as_index=False)[
            "이용건수"
        ]
        .sum()
        .rename(
            columns={
                "대여일자": "date",
                "대여시간": "hour",
                "대여소번호": "stationId",
                "이용건수": "target_rentals",
            }
        )
    )

    # 3. 날씨 데이터 불러오기 및 전처리 (../routes/data/weather_daily.csv)
    weather_path = os.path.join(DATA_DIR, "weather_daily_2026.csv")

    try:
        weather_df = pd.read_csv(weather_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        weather_df = pd.read_csv(weather_path, encoding="cp949")

    # (1) '일시' 컬럼을 datetime으로 변환 후 'date' (YYYY-MM-DD), 'hour' (0~23 정수) 생성
    weather_df["dt"] = pd.to_datetime(weather_df["일시"])
    weather_df["date"] = weather_df["dt"].dt.strftime("%Y-%m-%d")
    weather_df["hour"] = weather_df["dt"].dt.hour

    # (2) 컬럼명 단위 제거
    weather_df = weather_df.rename(
        columns={
            "기온(°C)": "기온",
            "강수량(mm)": "강수량",
            "풍속(m/s)": "풍속",
            "습도(%)": "습도",
        }
    )

    # (3) 강수량 결측값(NaN)을 0으로 처리
    if "강수량" in weather_df.columns:
        weather_df["강수량"] = weather_df["강수량"].fillna(0)

    # 병합에 필요한 날씨 컬럼 추출 및 중복 제거
    weather_cols = ["date", "hour"] + [
        col for col in ["기온", "강수량", "풍속", "습도"] if col in weather_df.columns
    ]
    weather_clean = weather_df[weather_cols].drop_duplicates(
        subset=["date", "hour"]
    )

    # 4. [date, hour] 기준 병합 (left join)
    merged_df = pd.merge(
        bike_grouped, weather_clean, on=["date", "hour"], how="left"
    )

    # 5. 완성된 CSV 파일을 ../routes/data/merged_bike_weather.csv에 저장
    output_path = os.path.join(DATA_DIR, "merged_bike_weather.csv")
    merged_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(
        f"병합 완료! 파일 저장 위치: {output_path} (전체 행 수: {len(merged_df)})"
    )


if __name__ == "__main__":
    process_and_merge_data()
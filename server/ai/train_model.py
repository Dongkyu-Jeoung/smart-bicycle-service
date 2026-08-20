import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def train_and_save_model():
    # 1. 파일 경로 설정 (현재 스크립트 위치 기준 ../routes/data)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../routes/data"))

    csv_path = os.path.join(DATA_DIR, "merged_bike_weather.csv")
    model_path = os.path.join(DATA_DIR, "bike_demand_rf_model.pkl")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {csv_path}")

    # 데이터 로드
    df = pd.read_csv(csv_path)

    # 2. 한글 컬럼명을 프론트엔드 Payload / 피처명에 맞춰 영문으로 변환
    df = df.rename(
        columns={
            "기온": "temperature",
            "강수량": "rainfall",
            "풍속": "windSpeed",
            "습도": "humidity",
        }
    )

    # 3. 파생 피처 생성 (date 기반)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["dayofweek"] = df["date"].dt.dayofweek
    df["is_weekend"] = df["dayofweek"].apply(lambda x: 1 if x >= 5 else 0)

    # 4. 학습 피처 세트 정의 (stationId, isHoliday 및 미사용 항목 모두 제외)
    features = [
        "month",
        "day",
        "dayofweek",
        "is_weekend",
        "hour",
        "temperature",
        "humidity",
        "rainfall",
        "windSpeed",
    ]

    X = df[features]
    y = df["target_rentals"]

    # 5. 모델 학습 (RandomForestRegressor)
    model = RandomForestRegressor(
        n_estimators=100, max_depth=15, random_state=42, n_jobs=-1
    )
    model.fit(X, y)

    # 6. 성능 측정 (MAE, RMSE, R² Score)
    preds = model.predict(X)
    mae = mean_absolute_error(y, preds)
    rmse = np.sqrt(mean_squared_error(y, preds))
    r2 = r2_score(y, preds)

    print("=== 모델 학습 평가 결과 ===")
    print(f"MAE  : {mae:.2f} 건")
    print(f"RMSE : {rmse:.2f} 건")
    print(f"R²   : {r2:.4f} ({r2 * 100:.2f}% 설명력)")

    # 7. 모델 및 피처 목록만 pkl 파일로 저장 (LabelEncoder 제거)
    model_bundle = {
        "model": model,
        "features": features,
    }

    joblib.dump(model_bundle, model_path)
    print(f"모델 저장 완료: {model_path}")


if __name__ == "__main__":
    train_and_save_model()
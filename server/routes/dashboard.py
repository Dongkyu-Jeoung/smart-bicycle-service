from fastapi import APIRouter


router = APIRouter()

RECOMMENDED_ROUTE = {
    "id": "bukhansan-loop",
    "name": "북한산 순환 코스",
    "region": "서울 · 은평구",
    "regionTag": "서울",
    "difficulty": "고급",
    "bikeType": "MTB",
    "distance": "42km",
    "duration": "3h 20m",
    "rating": 4.9,
    "reviewCount": 1284,
    "image":"https://images.unsplash.com/photo-1633707167699-cdd893b84441?w=1200&q=70",
    "tags": ["고급", "MTB"],
    "departure": "북한산 국립공원 입구",
    "destination": "북한산 국립공원 입구",
    "availableBike": 8,
    "returnSpace": 12,
    "elevationGain": "1,240m",
    "maxElevation": "1,240m",
    "completionRate": 78,
    "participants": 3082,
    "season": "봄 · 가을",
    "description":
      "북한산 국립공원을 순환하는 험준한 산악 코스. 가파른 오르막과 시원한 내리막이 반복되는 스릴 만점의 루트.",
    "safetyTips": [
      "헬멧과 보호대를 반드시 착용하세요",
      "출발 전 GPS와 배터리를 확인하세요",
      "날씨 변화에 대비한 레이어를 준비하세요",
      "초행길은 혼자보다 그룹 라이딩을 추천해요",
    ],
    "elevationProfile": [
      { "km": 0, "elevation": 80 },
      { "km": 8, "elevation": 420 },
      { "km": 16, "elevation": 980 },
      { "km": 21, "elevation": 1240 },
      { "km": 28, "elevation": 1100 },
      { "km": 35, "elevation": 650 },
      { "km": 42, "elevation": 90 },
    ],
  },

QUICK_MENU = [
    { "icon": "Map", "label": "루트 탐색", "path": "/riding/start" },
    { "icon": "Bike", "label": "따릉이", "path": "/bike/seoul" },
    { "icon": "Users", "label": "커뮤니티", "path": "/community" },
    { "icon": "Trophy", "label": "챌린지", "path": "/challenges" }
]

COMMUNITY_FEED = [
  { "name": "박서연", "initial": "박", "text": "님이 북한산 루트 완주 인증", "time": "5분 전", "likes": 24 },
  { "name": "이재혁", "initial": "이", "text": "님이 제주 환상길 D-7 모집 중", "time": "22분 전", "likes": 41 },
  { "name": "최지현", "initial": "최", "text": "님이 한강 종주 신기록 달성", "time": "1시간 전", "likes": 87 },
]

DASHBOARD_STATS = {
  "user": {
    "name": "김민준",
    "handle": "@minzun_rides",
    "level": "중급 라이더",
    "joinedDays": 142,
    "streak": 7,
  },
  "totals": [
    { "label": "총 라이딩", "value": "214", "unit": "회", "icon": "Map" },
    { "label": "누적 거리", "value": "3,842", "unit": "km", "icon": "TrendingUp" },
    { "label": "총 라이딩 시간", "value": "186", "unit": "h", "icon": "Clock" },
    { "label": "연속 라이딩", "value": "7", "unit": "일", "icon": "Flame" },
  ],
  "activity": {
    "badges": 12,
    "challenges": 8,
    "followers": 34,
    "savedRoutes": 27,
  }
}

@router.get("/")
async def get_dashboard():


    return {
      **DASHBOARD_STATS,
      "recommendedRoute": RECOMMENDED_ROUTE,
      "quickMenu": QUICK_MENU,
      "communityFeed": COMMUNITY_FEED,
    }








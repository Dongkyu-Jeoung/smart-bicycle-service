from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.connection import get_db 
from models.bike import BikeRoutesModel 

router = APIRouter()

@router.get("/{id}")
async def get_route_detail(id: str, db: Session = Depends(get_db)):
    stmt = select(BikeRoutesModel).where(BikeRoutesModel.id == id)
    route = db.execute(stmt).scalars().first()
    
    # 데이터가 없으면 404 에러 반환
    if not route:
        raise HTTPException(status_code=404, detail="해당 루트를 찾을 수 없습니다.")

    return route

@router.get("/")
async def get_routes(type: Optional[str] = None, db: Session = Depends(get_db)):
    # type이 정해지지 않은 경우 전체 루트 조회
    stmt = select(BikeRoutesModel)
    
    # 'personal' 타입 요청이 들어온 경우 필터링
    if type == "personal":
        stmt = stmt.where(BikeRoutesModel.bike_type != "따릉이")
        
    routes = db.execute(stmt).scalars().all()
    return routes
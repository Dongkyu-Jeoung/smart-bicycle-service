from fastapi import APIRouter, Path, Depends, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from schemas.member import MemberItem, MemberLogin
from models.member import MemberModel
from database.connection import get_db
from core.security import hash_password, verify_password,\
                            create_access_token, create_refresh_token

router = APIRouter()

# 토큰명, 유효기간 설정
REFRESH_COOKIE_NAME = "refreshToken"
REFRESH_COOKIE_MAX_AGE = 60 * 60 * 24 * 7           # 7days

# 회원가입
@router.post("/signup")
async def signup(memberItem : MemberItem, db : Session = Depends(get_db)) -> dict:
    # DB 연동 : 
    # 1. models.MemberModel에 memberItem 저장
    memberModel = MemberModel(
        nickname = memberItem.nickname,
        pwd = hash_password(memberItem.pwd),
        email = memberItem.email,
        ridingStyles = memberItem.ridingStyles,
        agreeMarketing = memberItem.agreeMarketing,
        agreeRequired = memberItem.agreeRequired
    )

    # 2. 연결된 db session의 add() 함수 호출
    db.add(memberModel)

    # 3. commit
    db.commit()

    return {
        "isSignup": True
    }

# 로그인
@router.post("/login")
async def login(memberLogin: MemberLogin, response : Response,db: Session = Depends(get_db)) -> dict:
    # 1. id를 통해 DB 데이터 가져오기
    stmt = select(MemberModel).where(MemberModel.email == memberLogin.email)
    member = db.scalars(stmt).first()

    # 2. 없으면 : 에러 메시지 리턴
    if member is None or not verify_password(memberLogin.pwd, member.pwd):
        return {
            "isLogin": False,
            "accessToken": None,
            "user": None
        }

    # token
    access_token = create_access_token(
        member_id=member.nickname, 
        role=member.role
    )

    refresh_token = create_refresh_token(
        member_id = member.nickname,
        role = member.role
    )

    response.set_cookie(
            key=REFRESH_COOKIE_NAME,
            value=refresh_token,
            httponly=True,
            samesite="lax",
            secure= False,
            max_age= REFRESH_COOKIE_MAX_AGE
        )

    return {
        "isLogin": True,
        "accessToken": access_token,
        "user": {
            "nickname": member.nickname,
            "email": member.email,
            "role": member.role
        }
    }



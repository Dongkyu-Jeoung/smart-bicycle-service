from pydantic import BaseModel, ConfigDict
from datetime import datetime


# Member class
class Member(BaseModel):
    nickname: str
    pwd: str
    email: str
    ridingStyles: list[str]
    agreeMarketing: bool
    agreeRequired: bool
    created_at: datetime


# Signup에 사용할 class
class MemberItem(BaseModel):
    nickname: str
    pwd: str
    email: str
    ridingStyles: list[str]
    agreeMarketing: bool
    agreeRequired: bool

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nickname": "dk1111",
                    "pwd": "asdf1234",
                    "email": "test@a.com" ,
                    "ridingStyles": ["로드", "그래벨"],
                    "agreeMarketing" : True,
                    "agreeRequired" : False
                }
            ]
        }
    )


# Login에 사용할 class
class MemberLogin(BaseModel):
    email: str
    pwd: str
    keepLoggedIn: bool

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "pwd": "asdf1234",
                    "email": "test@a.com" ,
                    "keepLoggedIn" : False
                }
            ]
        }
    )
# backend/app/schemas/token.py

from pydantic import BaseModel
from typing import Union # 导入 Union

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Union[str, None] = None

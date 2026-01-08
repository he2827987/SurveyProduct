from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    username: str
    password: str

class RegisterUser(BaseModel):
    username: str
    password: str
    company_name: str

class UserInDB(BaseModel):
    id: int
    username: str
    password: str
    company_id: int
    company_name: str

# 模拟数据库存储
users_db: Dict[str, UserInDB] = {}
company_id_counter = 1
user_id_counter = 1

@app.get("/")
def read_root():
    return {"message": "企业问卷调查系统API测试成功"}

# 同时支持两种路径
@app.post("/auth/login")
@app.post("/api/user/login")
def login(user: User):
    # 检查用户名和密码
    if user.username not in users_db:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    stored_user = users_db[user.username]
    if stored_user.password != user.password:
        raise HTTPException(status_code=401, detail="密码错误")
    
    return {
        "id": stored_user.id,
        "username": stored_user.username,
        "company_id": stored_user.company_id
    }

# 同时支持两种路径
@app.post("/auth/register")
@app.post("/api/user/register")
def register(user: RegisterUser):
    global company_id_counter, user_id_counter
    
    # 检查必填字段
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="用户名和密码为必填项")
    
    if not user.company_name:
        raise HTTPException(status_code=400, detail="企业名称为必填项")
    
    # 检查用户名是否已存在
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="该用户名已被注册")
    
    # 创建新用户
    new_user = UserInDB(
        id=user_id_counter,
        username=user.username,
        password=user.password,
        company_id=company_id_counter,
        company_name=user.company_name
    )
    
    # 存储用户
    users_db[user.username] = new_user
    
    # 更新ID计数器
    user_id_counter += 1
    company_id_counter += 1
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "company_id": new_user.company_id
    }

# 获取所有用户（仅用于测试）
@app.get("/api/users")
def get_all_users():
    return [
        {
            "id": user.id,
            "username": user.username,
            "company_id": user.company_id,
            "company_name": user.company_name
        }
        for user in users_db.values()
    ] 
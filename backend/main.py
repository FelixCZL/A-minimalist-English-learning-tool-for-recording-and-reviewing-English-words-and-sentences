from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import json
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import List, Optional

# 加载环境变量
load_dotenv()

from models import (
    EntryCreate,
    EntryResponse,
    SimilarEntry,
    SyncRequest,
    SyncResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    User as UserModel,
)
from database import (
    get_db,
    init_db,
    vector_db,
    create_entry,
    get_all_entries,
    get_entry_by_id,
    delete_entry_by_id,
    sync_entries,
    get_device_id,
)
from ai_service import analyze_content, generate_embedding

app = FastAPI(title="English Study Tool API")

# JWT 配置
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

security = HTTPBearer()

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized!")
    print("Server is running at http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")


@app.get("/")
def root():
    return {
        "message": "English Study Tool API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "create_entry": "POST /entries",
            "get_entries": "GET /entries",
            "get_entry": "GET /entries/{entry_id}",
            "find_similar": "GET /entries/{entry_id}/similar",
            "delete_entry": "DELETE /entries/{entry_id}",
        },
    }


@app.post("/entries", response_model=EntryResponse)
async def create_new_entry(entry: EntryCreate, db: Session = Depends(get_db)):
    """
    创建新条目
    1. 接收用户输入
    2. 调用 AI 分析
    3. 生成 embedding
    4. 保存到数据库和向量数据库
    """
    try:
        # AI 分析
        print(f"Analyzing content: {entry.content[:50]}...")
        ai_result = analyze_content(entry.content, entry.source, entry.note)

        # 生成 embedding
        print("Generating embedding...")
        embedding = generate_embedding(entry.content)

        # 保存到 SQLite
        print("Saving to database...")
        db_entry = create_entry(
            db=db,
            content=entry.content,
            entry_type=ai_result["entry_type"],
            source=entry.source or "",
            note=entry.note or "",
            ai_analysis=json.dumps(ai_result["analysis"], ensure_ascii=False),
            tags=",".join(ai_result["tags"]),
        )

        # 保存到向量数据库
        print(f"Saving to vector database (ID: {db_entry.id})...")
        vector_db.add_entry(
            entry_id=db_entry.id,
            content=entry.content,
            embedding=embedding,
            metadata={
                "entry_type": ai_result["entry_type"],
                "tags": ",".join(ai_result["tags"]),
            },
        )

        print(f"Entry created successfully! ID: {db_entry.id}")
        return db_entry

    except Exception as e:
        print(f"Error creating entry: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")


@app.get("/entries", response_model=List[EntryResponse])
async def get_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有条目"""
    try:
        entries = get_all_entries(db, skip=skip, limit=limit)
        return entries
    except Exception as e:
        print(f"Error getting entries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get entries: {str(e)}")


@app.get("/entries/{entry_id}", response_model=EntryResponse)
async def get_entry(entry_id: int, db: Session = Depends(get_db)):
    """获取单个条目"""
    entry = get_entry_by_id(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@app.get("/entries/{entry_id}/similar", response_model=List[SimilarEntry])
async def find_similar_entries(
    entry_id: int, limit: int = 5, db: Session = Depends(get_db)
):
    """查找相似条目"""
    try:
        # 获取原条目
        entry = get_entry_by_id(db, entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")

        # 生成查询的 embedding
        print(f"Finding similar entries for ID: {entry_id}")
        query_embedding = generate_embedding(entry.content)

        # 在向量数据库中搜索
        results = vector_db.search_similar(
            query_embedding, n_results=limit + 1
        )  # +1 因为会包含自己

        # 构建响应
        similar_entries = []
        if results and results["ids"] and len(results["ids"]) > 0:
            for i, entry_id_str in enumerate(results["ids"][0]):
                result_id = int(entry_id_str)

                # 跳过自己
                if result_id == entry_id:
                    continue

                # 获取条目详情
                result_entry = get_entry_by_id(db, result_id)
                if result_entry:
                    # 获取相似度分数
                    similarity = (
                        1.0 - results["distances"][0][i]
                        if "distances" in results
                        else 0.0
                    )

                    similar_entries.append(
                        SimilarEntry(
                            id=result_entry.id,
                            content=result_entry.content,
                            entry_type=result_entry.entry_type,
                            similarity=similarity,
                            ai_analysis=result_entry.ai_analysis,
                        )
                    )

                if len(similar_entries) >= limit:
                    break

        print(f"Found {len(similar_entries)} similar entries")
        return similar_entries

    except Exception as e:
        print(f"Error finding similar entries: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to find similar entries: {str(e)}"
        )


@app.delete("/entries/{entry_id}")
async def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    try:
        success = delete_entry_by_id(db, entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entry not found")

        vector_db.delete_entry(entry_id)

        return {"message": "Entry deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting entry: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete entry: {str(e)}")


@app.get("/device-id")
async def get_device_info():
    """获取设备ID"""
    return {"device_id": get_device_id()}


@app.post("/sync", response_model=SyncResponse)
async def sync_data(request: SyncRequest, db: Session = Depends(get_db)):
    """同步数据"""
    try:
        print(f"Syncing data from device: {request.device_id}")

        server_entries, conflicts = sync_entries(
            db, request.local_entries, request.device_id
        )

        last_sync_time = datetime.utcnow()

        print(
            f"Sync completed. Server entries: {len(server_entries)}, Conflicts: {len(conflicts)}"
        )

        return SyncResponse(
            server_entries=server_entries,
            conflicts=conflicts,
            last_sync_time=last_sync_time,
        )
    except Exception as e:
        print(f"Error syncing data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync data: {str(e)}")


# 认证相关函数
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[UserModel]:
    """获取当前用户"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except jwt.PyJWTError:
        return None

    user = db.query(UserModel).filter(UserModel.username == username).first()
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 认证端点
@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = (
        db.query(UserModel).filter(UserModel.username == user.username).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )

    # 密码验证（至少6位）
    if len(user.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="密码至少需要6位"
        )

    # 创建用户
    password_hash = bcrypt.hashpw(
        user.password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    db_user = UserModel(username=user.username, password_hash=password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # 生成 token
    access_token = create_access_token(data={"sub": user.username})

    return Token(access_token=access_token, username=user.username)


@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    # 验证密码
    if not bcrypt.checkpw(
        user.password.encode("utf-8"), db_user.password_hash.encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    # 生成 token
    access_token = create_access_token(data={"sub": user.username})

    return Token(access_token=access_token, username=user.username)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

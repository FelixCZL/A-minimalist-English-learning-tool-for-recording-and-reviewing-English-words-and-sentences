from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    create_engine,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

Base = declarative_base()


# SQLAlchemy ORM Model for User
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# SQLAlchemy ORM Model for Entry
class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    entry_type = Column(String(20))
    source = Column(String(200))
    note = Column(Text)
    ai_analysis = Column(Text)
    tags = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = Column(Integer, default=0)
    device_id = Column(String(100))
    sync_status = Column(String(20), default="synced")
    version = Column(Integer, default=1)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)


# Pydantic Models for API
class EntryCreate(BaseModel):
    content: str
    source: Optional[str] = None
    note: Optional[str] = None


class AIAnalysis(BaseModel):
    """AI 分析结果的数据结构"""

    entry_type: str  # "word" or "sentence"
    data: Dict[str, Any]  # 具体的分析数据


class WordAnalysis(BaseModel):
    """单词分析结果"""

    word: str
    part_of_speech: str
    definition: str
    collocations: List[str]
    example_sentence: str


class SentenceAnalysis(BaseModel):
    """句子分析结果"""

    sentence: str
    function: str  # 句子功能
    pattern: str  # 句式模式
    why_good: str  # 为什么是好句子
    rewrite_examples: List[str]  # 改写示例


class EntryResponse(BaseModel):
    id: int
    content: str
    entry_type: str
    source: Optional[str]
    note: Optional[str]
    ai_analysis: str
    tags: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SimilarEntry(BaseModel):
    """相似条目"""

    id: int
    content: str
    entry_type: str
    similarity: float
    ai_analysis: str


class SyncEntry(BaseModel):
    """同步条目"""

    id: int
    content: str
    entry_type: str
    source: Optional[str]
    note: Optional[str]
    ai_analysis: str
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted: int
    device_id: str
    sync_status: str
    version: int

    class Config:
        from_attributes = True


class SyncRequest(BaseModel):
    """同步请求"""

    last_sync_time: Optional[datetime] = None
    device_id: str
    local_entries: List[SyncEntry] = []


class SyncResponse(BaseModel):
    """同步响应"""

    server_entries: List[SyncEntry]
    conflicts: List[SyncEntry]
    last_sync_time: datetime


# User Authentication Models
class UserCreate(BaseModel):
    """用户注册"""

    username: str
    password: str


class UserLogin(BaseModel):
    """用户登录"""

    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应"""

    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token"""

    access_token: str
    token_type: str = "bearer"
    username: str

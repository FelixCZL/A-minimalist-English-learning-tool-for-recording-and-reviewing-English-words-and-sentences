from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

Base = declarative_base()

# SQLAlchemy ORM Model
class Entry(Base):
    __tablename__ = "entries"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)  # 原始输入内容
    entry_type = Column(String(20))  # "word" 或 "sentence"
    source = Column(String(200))  # 来源（X, YouTube, Report 等）
    note = Column(Text)  # 用户备注
    ai_analysis = Column(Text)  # AI 分析结果（JSON 字符串）
    tags = Column(Text)  # 标签（逗号分隔）
    created_at = Column(DateTime, default=datetime.utcnow)

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

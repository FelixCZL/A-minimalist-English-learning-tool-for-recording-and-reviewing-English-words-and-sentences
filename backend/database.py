from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Entry
import numpy as np
import json
import os

# SQLite 数据库
DATABASE_URL = "sqlite:///./english_study.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表
def init_db():
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 简化的向量数据库（内存存储 + JSON 持久化）
class VectorDB:
    def __init__(self):
        # 创建持久化目录
        self.persist_directory = "./vector_db"
        os.makedirs(self.persist_directory, exist_ok=True)
        self.data_file = os.path.join(self.persist_directory, "vectors.json")
        
        # 内存存储：{entry_id: {"embedding": [...], "content": "...", "metadata": {...}}}
        self.vectors = {}
        
        # 从文件加载
        self._load()
    
    def _load(self):
        """从文件加载向量数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 转换回整数键
                    self.vectors = {int(k): v for k, v in data.items()}
            except Exception as e:
                print(f"Error loading vector data: {e}")
                self.vectors = {}
    
    def _save(self):
        """保存向量数据到文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.vectors, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving vector data: {e}")
    
    def add_entry(self, entry_id: int, content: str, embedding: list, metadata: dict):
        """添加条目到向量数据库"""
        self.vectors[entry_id] = {
            "embedding": embedding,
            "content": content,
            "metadata": metadata
        }
        self._save()
    
    def search_similar(self, embedding: list, n_results: int = 5):
        """搜索相似条目（使用余弦相似度）"""
        if not self.vectors:
            return {"ids": [[]], "distances": [[]]}
        
        query_vec = np.array(embedding)
        similarities = []
        
        for entry_id, data in self.vectors.items():
            stored_vec = np.array(data["embedding"])
            # 计算余弦相似度
            similarity = np.dot(query_vec, stored_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(stored_vec) + 1e-10
            )
            similarities.append((entry_id, 1 - similarity))  # 转换为距离
        
        # 按距离排序（距离越小越相似）
        similarities.sort(key=lambda x: x[1])
        
        # 返回前 n_results 个
        top_results = similarities[:n_results]
        ids = [[str(entry_id) for entry_id, _ in top_results]]
        distances = [[dist for _, dist in top_results]]
        
        return {"ids": ids, "distances": distances}
    
    def delete_entry(self, entry_id: int):
        """删除条目"""
        if entry_id in self.vectors:
            del self.vectors[entry_id]
            self._save()

# 全局向量数据库实例
vector_db = VectorDB()

# 数据库操作函数
def create_entry(db: Session, content: str, entry_type: str, source: str, 
                 note: str, ai_analysis: str, tags: str):
    """创建新条目"""
    entry = Entry(
        content=content,
        entry_type=entry_type,
        source=source,
        note=note,
        ai_analysis=ai_analysis,
        tags=tags
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def get_all_entries(db: Session, skip: int = 0, limit: int = 100):
    """获取所有条目"""
    return db.query(Entry).order_by(Entry.created_at.desc()).offset(skip).limit(limit).all()

def get_entry_by_id(db: Session, entry_id: int):
    """根据 ID 获取条目"""
    return db.query(Entry).filter(Entry.id == entry_id).first()

def delete_entry_by_id(db: Session, entry_id: int):
    """删除条目"""
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if entry:
        db.delete(entry)
        db.commit()
        return True
    return False

def search_entries(db: Session, query: str):
    """搜索条目（简单文本搜索）"""
    return db.query(Entry).filter(
        Entry.content.contains(query) | Entry.tags.contains(query)
    ).all()

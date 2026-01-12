from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import json
from typing import List

# 加载环境变量
load_dotenv()

from models import EntryCreate, EntryResponse, SimilarEntry
from database import get_db, init_db, vector_db, create_entry, get_all_entries, get_entry_by_id, delete_entry_by_id
from ai_service import analyze_content, generate_embedding

app = FastAPI(title="English Study Tool API")

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
            "delete_entry": "DELETE /entries/{entry_id}"
        }
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
            tags=",".join(ai_result["tags"])
        )
        
        # 保存到向量数据库
        print(f"Saving to vector database (ID: {db_entry.id})...")
        vector_db.add_entry(
            entry_id=db_entry.id,
            content=entry.content,
            embedding=embedding,
            metadata={
                "entry_type": ai_result["entry_type"],
                "tags": ",".join(ai_result["tags"])
            }
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
async def find_similar_entries(entry_id: int, limit: int = 5, db: Session = Depends(get_db)):
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
        results = vector_db.search_similar(query_embedding, n_results=limit + 1)  # +1 因为会包含自己
        
        # 构建响应
        similar_entries = []
        if results and results['ids'] and len(results['ids']) > 0:
            for i, entry_id_str in enumerate(results['ids'][0]):
                result_id = int(entry_id_str)
                
                # 跳过自己
                if result_id == entry_id:
                    continue
                
                # 获取条目详情
                result_entry = get_entry_by_id(db, result_id)
                if result_entry:
                    # 获取相似度分数
                    similarity = 1.0 - results['distances'][0][i] if 'distances' in results else 0.0
                    
                    similar_entries.append(SimilarEntry(
                        id=result_entry.id,
                        content=result_entry.content,
                        entry_type=result_entry.entry_type,
                        similarity=similarity,
                        ai_analysis=result_entry.ai_analysis
                    ))
                
                if len(similar_entries) >= limit:
                    break
        
        print(f"Found {len(similar_entries)} similar entries")
        return similar_entries
        
    except Exception as e:
        print(f"Error finding similar entries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find similar entries: {str(e)}")

@app.delete("/entries/{entry_id}")
async def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    """删除条目"""
    try:
        # 从 SQLite 删除
        success = delete_entry_by_id(db, entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        # 从向量数据库删除
        vector_db.delete_entry(entry_id)
        
        return {"message": "Entry deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting entry: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete entry: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

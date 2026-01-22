# English Study Tool

一个极简的英语学习工具，用于记录和复习英文单词和句子。

## 功能特性

- 📝 快速记录单词和句子
- 🤖 AI 自动分析和分类
- 🔍 基于语义的相似句子查找
- 📚 历史记录浏览
- 🔄 **多设备同步** - 实时同步数据到所有设备
- 📱 **离线可用** - 无网络时继续使用，联网后自动同步
- ⚡ **增量同步** - 只传输变更数据，高效省流量

## 技术栈

### 后端
- Python 3.8+
- FastAPI
- SQLite
- Chroma (向量数据库)
- DeepSeek API

### 前端
- React
- Vite
- Axios

## 多设备同步配置

### 本地 SQLite 模式（默认）

无需配置，开箱即用。数据存储在本地 SQLite 数据库中。

### 云数据库模式（推荐用于多设备同步）

使用 Supabase 实现真正的多设备同步：

1. **创建 Supabase 项目**
   - 访问 https://supabase.com 并创建免费项目
   - 记下项目的 URL 和密码

2. **配置数据库连接**
   ```bash
   cd backend
   cp .env.example .env
   ```
   
   编辑 `.env` 文件：
   ```env
   DATABASE_URL=postgresql://postgres:[your-password]@db.[project-id].supabase.co:5432/postgres
   USE_CLOUD_DB=true
   DEEPSEEK_API_KEY=your_deepseek_api_key
   ```

3. **设置 Supabase 数据库表**
   
   访问 Supabase Dashboard > SQL Editor，执行以下 SQL：
   ```sql
   CREATE TABLE entries (
       id SERIAL PRIMARY KEY,
       content TEXT NOT NULL,
       entry_type VARCHAR(20),
       source VARCHAR(200),
       note TEXT,
       ai_analysis TEXT,
       tags TEXT,
       created_at TIMESTAMP DEFAULT NOW(),
       updated_at TIMESTAMP DEFAULT NOW(),
       deleted INTEGER DEFAULT 0,
       device_id VARCHAR(100),
       sync_status VARCHAR(20) DEFAULT 'synced',
       version INTEGER DEFAULT 1
   );
   
   CREATE INDEX idx_entries_updated_at ON entries(updated_at);
   CREATE INDEX idx_entries_device_id ON entries(device_id);
   ```

### 同步功能说明

- **自动同步**：每 30 秒自动同步一次数据
- **离线支持**：离线时数据保存在本地，联网后自动同步
- **冲突解决**：自动处理简单冲突，复杂冲突提示用户手动处理
- **增量同步**：只传输变更的数据，节省流量

## 快速开始

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，设置：
- `DEEPSEEK_API_KEY`（必需）
- `DATABASE_URL` 和 `USE_CLOUD_DB`（根据需要选择）

### 3. 启动后端服务

```bash
cd backend
python main.py
```

后端将运行在 http://localhost:8000

### 4. 安装前端依赖

```bash
cd frontend
npm install
```

### 5. 启动前端服务

```bash
cd frontend
npm run dev
```

前端将运行在 http://localhost:5173

## 使用说明

1. 在输入框中粘贴英文单词或句子
2. 可选填写来源和备注
3. 点击「保存」，AI 将自动分析
4. 在历史记录中点击任意条目查看详情
5. 点击「查看相似句子」发现相关内容

## 项目结构

```
English_Study_tool/
├── backend/           # Python 后端
│   ├── main.py       # FastAPI 主程序（包含同步 API）
│   ├── models.py     # 数据模型（包含同步相关模型）
│   ├── database.py   # 数据库操作（包含同步逻辑）
│   ├── ai_service.py # AI 服务
│   ├── .env.example  # 环境变量配置示例
│   └── requirements.txt
├── frontend/         # React 前端
│   ├── src/
│   │   └── App.jsx   # 主应用（包含同步逻辑）
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## API 端点

### 基础功能
- `POST /entries` - 创建新条目
- `GET /entries` - 获取所有条目
- `GET /entries/{id}` - 获取单个条目
- `GET /entries/{id}/similar` - 查找相似条目
- `DELETE /entries/{id}` - 删除条目

### 同步功能
- `GET /device-id` - 获取设备 ID
- `POST /sync` - 同步数据
  - 请求参数：
    ```json
    {
      "device_id": "device_123",
      "local_entries": [...]
    }
    ```
  - 响应：
    ```json
    {
      "server_entries": [...],
      "conflicts": [],
      "last_sync_time": "2024-01-13T12:00:00"
    }
    ```

## 技术细节

### 同步机制
- **版本控制**：每个条目都有版本号，用于冲突检测
- **软删除**：删除操作标记为 deleted=1，而不是物理删除
- **时间戳**：使用 updated_at 进行增量同步
- **设备标识**：每个设备有唯一 ID，用于识别数据来源

### 数据存储
- **SQLite 模式**：数据存储在 `english_study.db`
- **Supabase 模式**：数据存储在云端 PostgreSQL 数据库
- **向量数据**：存储在 `vector_db/vectors.json`（需要单独同步）

# 变更日志 (Changelog)

## [2.0.0] - 2025-01-13

### 新增功能 🎉
- ✨ **多设备同步功能**
  - 支持本地 SQLite 和云数据库（Supabase）切换
  - 实时同步数据到所有设备（30秒轮询）
  - 离线可用性：无网络时继续使用，联网后自动同步
  - 增量同步：只传输变更数据，节省流量
  - 设备管理：自动生成设备唯一标识
  - 冲突检测：自动处理简单冲突，复杂冲突提示用户

- ✨ **离线支持**
  - 数据本地持久化（localStorage）
  - 在线/离线状态实时检测
  - 离线时所有操作正常可用
  - 联网后自动同步所有变更

- ✨ **数据同步**
  - 新增同步 API 端点：`GET /device-id` 和 `POST /sync`
  - 软删除支持（deleted 字段）
  - 版本控制（version 字段）防止数据丢失
  - 更新时间戳（updated_at）实现增量同步

### 技术改进 🔧
- 📦 依赖更新
  - 添加 `supabase>=2.3.0` 用于云数据库支持
  - 添加 `websockets>=12.0` 用于实时通信
  - 添加 `aiosqlite>=0.19.0` 用于异步数据库操作

- 🗄️ 数据库模型更新
  - Entry 模型新增 5 个同步相关字段
  - 新增 3 个同步相关的 Pydantic 模型

- 🔌 API 更新
  - 新增设备 ID 获取端点
  - 新增数据同步端点
  - 更新现有端点以支持同步功能

- 🎨 前端改进
  - 新增同步状态指示器
  - 新增在线/离线状态显示
  - 新增最后同步时间显示
  - 新增离线操作支持

### 文档更新 📚
- 📝 更新 README.md
  - 添加多设备同步功能说明
  - 添加云数据库配置步骤
  - 添加同步机制说明
  - 添加技术细节说明

- 📖 新增文档
  - SYNC_GUIDE.md - 多设备同步使用指南
  - SYNC_IMPLEMENTATION.md - 功能实现总结

### 配置更新 ⚙️
- 🔑 更新 .env.example
  - 添加数据库配置选项
  - 添加云数据库连接说明

### 文件变更 📁

#### 修改的文件
- `backend/models.py` - 添加同步相关字段和模型
- `backend/database.py` - 添加同步逻辑和设备 ID 管理
- `backend/main.py` - 添加同步 API 端点
- `backend/requirements.txt` - 添加新依赖
- `backend/.env.example` - 添加数据库配置
- `frontend/src/App.jsx` - 添加同步逻辑和 UI
- `README.md` - 更新文档

#### 新增的文件
- `SYNC_GUIDE.md` - 使用指南
- `SYNC_IMPLEMENTATION.md` - 实现总结
- `CHANGELOG.md` - 变更日志（本文件）

### Breaking Changes ⚠️
- 无破坏性变更，向后兼容

### 已知问题 🐛
- LSP 类型检查警告（不影响运行）
- 向量数据（embedding）暂不自动同步，需要时重新生成

### 后续计划 🚀
- [ ] WebSocket 实时同步
- [ ] Service Worker 后台同步
- [ ] PWA 支持
- [ ] 数据压缩优化
- [ ] 批量操作优化

---

## [1.0.0] - 初始版本

### 核心功能
- 📝 快速记录单词和句子
- 🤖 AI 自动分析和分类
- 🔍 基于语义的相似句子查找
- 📚 历史记录浏览

### 技术栈
- 后端：Python 3.8+, FastAPI, SQLite, Chroma, DeepSeek API
- 前端：React, Vite, Axios

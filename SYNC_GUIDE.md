# 多设备同步使用指南

## 概述

本工具支持多设备间的实时数据同步，让您可以在不同设备上无缝学习英语。

## 配置步骤

### 1. 选择同步模式

#### 本地模式（单设备使用）
- 无需任何配置
- 数据存储在本地 SQLite 数据库
- 适合只在单台设备上使用

#### 云同步模式（多设备使用）
- 使用 Supabase 云数据库
- 支持多设备实时同步
- 数据安全可靠，有备份

### 2. 配置云同步

#### 第一步：创建 Supabase 项目
1. 访问 [Supabase](https://supabase.com)
2. 注册/登录账户
3. 点击 "New Project" 创建新项目
4. 选择免费套餐（足够个人使用）
5. 设置项目名称和密码

#### 第二步：获取数据库连接信息
1. 进入项目 Dashboard
2. 点击左侧菜单 "Settings" > "Database"
3. 找到 "Connection string"
4. 选择 "URI" 格式
5. 复制连接字符串，格式如：
   ```
   postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
   ```

#### 第三步：创建数据库表
1. 进入 Supabase Dashboard
2. 点击 "SQL Editor"
3. 点击 "New query"
4. 粘贴以下 SQL 并执行：

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

#### 第四步：配置后端环境变量
1. 复制 `.env.example` 为 `.env`
2. 编辑 `.env` 文件：

```env
# 使用云数据库
DATABASE_URL=postgresql://postgres:[your-password]@db.[project-id].supabase.co:5432/postgres
USE_CLOUD_DB=true

# DeepSeek API
DEEPSEEK_API_KEY=your_api_key_here
```

#### 第五步：在每台设备上配置
- 在每台需要同步的设备上，重复上述步骤
- 确保所有设备连接到同一个 Supabase 项目
- 确保每台设备都有相同的 DATABASE_URL 和 DEEPSEEK_API_KEY

## 使用说明

### 自动同步
- 系统每 30 秒自动同步一次数据
- 数据变更时会立即同步到服务器
- 其他设备的数据变更会在 30 秒内同步到当前设备

### 离线使用
- 无网络时，数据自动保存在本地
- 可以正常添加、查看、删除条目
- 联网后会自动同步所有变更

### 同步状态
页面顶部显示同步状态：
- 🟢 **在线** - 已连接服务器
- 🔴 **离线** - 无网络连接
- 🔄 **同步中** - 正在同步数据
- ✅ **已同步** - 同步完成
- ⚠️ **有冲突** - 发现数据冲突
- ❌ **同步失败** - 同步过程中出错

### 冲突处理
当多台设备同时修改同一条数据时，会发生冲突：

- **自动处理**：如果修改时间相差较大，自动使用最新的版本
- **手动处理**：如果修改时间接近，系统会提示冲突，需要手动选择保留哪个版本

### 向量数据同步
目前向量数据（embedding）暂不自动同步：
- 在新设备上首次使用相似度搜索时，会自动重新生成 embedding
- 不影响核心功能的正常使用

## 常见问题

### Q: 为什么数据没有立即同步？
A: 自动同步间隔为 30 秒，或者手动刷新页面触发同步。

### Q: 如何强制立即同步？
A: 刷新页面即可触发立即同步。

### Q: 离线时的数据会丢失吗？
A: 不会。数据保存在本地浏览器中，联网后会自动同步。

### Q: 如何查看设备 ID？
A: 页面顶部会显示当前设备的 ID。

### Q: 删除的条目会同步到其他设备吗？
A: 会的。删除操作会同步到所有设备。

### Q: 可以回退到之前的版本吗？
A: 目前不支持版本回退功能。如有需要，可以在 Supabase Dashboard 中手动恢复数据库。

## 性能优化建议

1. **定期清理**：定期清理不再需要的条目，减少同步数据量
2. **网络优化**：在网络良好的环境下使用，确保同步顺畅
3. **分批同步**：如果数据量很大，建议分批导入，避免单次同步过多数据

## 安全建议

1. **保护密钥**：妥善保管 DEEPSEEK_API_KEY 和数据库密码
2. **定期备份**：定期导出 Supabase 数据库作为备份
3. **权限控制**：如需多人使用，建议在 Supabase 中设置 Row Level Security (RLS)

## 故障排除

### 同步失败
1. 检查网络连接
2. 检查 DATABASE_URL 是否正确
3. 查看 Supabase 服务是否正常
4. 检查 `.env` 文件配置是否正确

### 数据不一致
1. 检查所有设备是否使用相同的 DATABASE_URL
2. 在 Supabase Dashboard 中查看数据库状态
3. 考虑清空本地缓存（刷新页面）

### 连接超时
1. 检查 Supabase 服务的可用性
2. 检查网络连接质量
3. 考虑更换 Supabase 项目地区

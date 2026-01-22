# 🚀 快速开始 - English Study Tool v2.0

恭喜！代码已成功推送到 GitHub。现在按照以下步骤完成云部署。

---

## 📋 当前状态

✅ 代码已推送到 GitHub
✅ 后端依赖已安装
✅ 前端依赖已安装
✅ 本地构建测试通过
⏳ 等待配置 DeepSeek API Key
⏳ 等待云端部署

---

## 🔑 第一步：获取 DeepSeek API Key

1. 访问 [https://platform.deepseek.com](https://platform.deepseek.com)
2. 注册或登录账户
3. 创建 API Key
4. **保存这个 Key**，后面部署时需要用到

---

## 🎯 第二步：部署后端到 Render

### 1. 登录 Render
访问 [https://dashboard.render.com](https://dashboard.render.com) 并使用 GitHub 账户登录

### 2. 创建 Web Service
1. 点击右上角的 **"New +"**
2. 选择 **"Web Service"**
3. 连接你的 GitHub 仓库：`FelixCZL/A-minimalist-English-learning-tool-for-recording-and-reviewing-English-words-and-sentences`
4. 选择分支：`main`

### 3. 配置服务
- **Name**: `english-study-tool-api`（或任意名称）
- **Environment**: `Python`
- **Build Command**: `cd backend && pip install -r requirements.txt`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### 4. 配置环境变量
在 **Environment Variables** 部分添加以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PYTHON_VERSION` | `3.9` | Python 版本 |
| `SECRET_KEY` | 任意随机字符串（或点击"Generate"）| JWT 密钥 |
| `DEEPSEEK_API_KEY` | 你的 DeepSeek API Key | **必需** |
| `DATABASE_URL` | `sqlite:///./english_study.db` | 数据库连接 |
| `USE_CLOUD_DB` | `false` | 不使用云数据库 |

### 5. 部署
- 点击 **"Create Web Service"**
- 等待部署完成（约 2-5 分钟）
- 部署成功后，记下服务 URL，例如：`https://english-study-tool-api.onrender.com`

### 6. 测试 API
访问 `https://your-app-name.onrender.com/docs` 查看 API 文档

---

## 🌐 第三步：部署前端到 Netlify

### 1. 登录 Netlify
访问 [https://app.netlify.com](https://app.netlify.com) 并使用 GitHub 账户登录

### 2. 创建新站点
1. 点击 **"Add new site"**
2. 选择 **"Import an existing project"**
3. 连接你的 GitHub 仓库

### 3. 配置构建设置
Netlify 会自动检测配置：
- **Build command**: `npm run build`
- **Publish directory**: `dist`
- 点击 **"Deploy site"**

### 4. 配置环境变量
1. 进入 **Site settings** > **Environment variables**
2. 添加以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `VITE_API_BASE` | `https://your-render-app-name.onrender.com` | 后端 API 地址 |

**重要**：将 `your-render-app-name.onrender.com` 替换为你在 Render 上部署的实际 URL

### 5. 部署
- 点击 **"Deploy site"**
- 等待部署完成（约 1-2 分钟）
- 部署成功后，记下站点 URL，例如：`https://your-app-name.netlify.app`

---

## ✅ 第四步：测试应用

### 访问你的应用
打开浏览器访问 Netlify 提供的 URL，例如：
`https://your-app-name.netlify.app`

### 测试功能
1. **注册用户**
   - 点击"注册"
   - 输入用户名和密码（至少 6 位）
   - 点击"注册"按钮

2. **添加单词或句子**
   - 输入一个英文单词或句子
   - 点击"保存"
   - 查看 AI 分析结果

3. **测试图表页面**
   - 点击顶部导航的"图表"
   - 确认 TradingView Lightweight Charts 正常渲染

---

## 🏠 本地运行（可选）

如果你想本地运行，请使用启动脚本：

### Windows
双击 `start.bat` 文件

### 手动启动
```bash
# 后端
cd backend
python main.py

# 前端（新终端）
cd frontend
npm run dev
```

访问 `http://localhost:5173` 使用应用。

---

## 🔧 常见问题

### 1. 后端部署失败
- 检查 `requirements.txt` 是否正确
- 确保 Python 版本设置正确
- 查看 Render 日志获取详细错误信息

### 2. 前端无法连接后端
- 确保 `VITE_API_BASE` 环境变量设置正确
- 检查后端是否正常运行
- 确认后端 CORS 配置允许所有来源

### 3. AI 分析失败
- 确认 `DEEPSEEK_API_KEY` 已正确设置
- 检查 API Key 是否有效
- 查看 Render 日志获取错误信息

### 4. 图表不显示
- 清除浏览器缓存
- 检查浏览器控制台是否有错误
- 确保 `lightweight-charts` 包已正确安装

---

## 📊 费用说明

### Netlify（前端）
- **免费额度**：
  - 100GB 带宽/月
  - 300 分钟构建时间/月
  - 无限站点
  - 自动 HTTPS
  - 全球 CDN

### Render（后端）
- **免费额度**：
  - 1 个 Web Service
  - 512MB RAM
  - 0.1 CPU
  - 24/7 运行（免费版会休眠）
  - 自动 HTTPS

**注意**：Render 免费版会在 15 分钟无活动后休眠，首次访问需要 30-60 秒启动时间。

---

## 🎉 完成！

恭喜！你的 English Study Tool 已成功部署到云端！

如需帮助，请查看：
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 详细部署指南
- [Netlify 文档](https://docs.netlify.com)
- [Render 文档](https://render.com/docs)

---

**版本**: 2.0.0
**更新日期**: 2026-01-22

# 部署指南 - Netlify + Render (零成本方案)

本指南将帮助你将 English Study Tool 部署到 Netlify (前端) 和 Render (后端)，实现零成本的完整部署。

## 📋 前置要求

- GitHub 账户
- Netlify 账户 ([https://www.netlify.com](https://www.netlify.com))
- Render 账户 ([https://render.com](https://render.com))
- DeepSeek API Key ([https://platform.deepseek.com](https://platform.deepseek.com))

---

## 🚀 部署步骤

### 第一步：准备代码

1. **将代码推送到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/your-username/your-repo.git
   git push -u origin main
   ```

2. **确保项目结构正确**
   ```
   your-repo/
   ├── backend/
   │   ├── main.py
   │   ├── models.py
   │   ├── database.py
   │   ├── ai_service.py
   │   ├── requirements.txt
   │   └── .env.example
   ├── frontend/
   │   ├── src/
   │   ├── package.json
   │   ├── tailwind.config.js
   │   └── vite.config.js
   ├── netlify.toml
   └── render.yaml
   ```

---

### 第二步：部署后端到 Render

1. **登录 Render**
   - 访问 [https://dashboard.render.com](https://dashboard.render.com)
   - 使用 GitHub 账户登录

2. **创建新的 Web Service**
   - 点击 "New +"
   - 选择 "Web Service"
   - 连接你的 GitHub 仓库
   - 选择分支：`main`

3. **配置 Build 和 Start 命令**
   - **Environment**: `Python`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **配置环境变量**
   在 Environment Variables 部分添加以下变量：
   
   | 变量名 | 值 | 说明 |
   |--------|-----|------|
   | `PYTHON_VERSION` | `3.9` | Python 版本 |
   | `SECRET_KEY` | 自动生成或自定义 | JWT 密钥 |
   | `DEEPSEEK_API_KEY` | 你的 DeepSeek API Key | 必需 |
   | `DATABASE_URL` | `sqlite:///./english_study.db` | 本地数据库 |
   | `USE_CLOUD_DB` | `false` | 不使用云数据库 |

5. **部署**
   - 点击 "Create Web Service"
   - 等待部署完成（约 2-5 分钟）
   - 部署成功后，记下服务 URL，例如：`https://english-study-tool-api.onrender.com`

6. **获取 API 文档**
   - 访问 `https://your-app-name.onrender.com/docs`
   - 测试 API 端点是否正常工作

---

### 第三步：部署前端到 Netlify

1. **登录 Netlify**
   - 访问 [https://app.netlify.com](https://app.netlify.com)
   - 使用 GitHub 账户登录

2. **创建新站点**
   - 点击 "Add new site"
   - 选择 "Import an existing project"
   - 连接你的 GitHub 仓库

3. **配置构建设置**
   - **Build command**: `npm run build`（Netlify 会自动检测）
   - **Publish directory**: `dist`（Netlify 会自动检测）
   - 点击 "Deploy site"

4. **配置环境变量**
   - 进入 Site settings > Environment variables
   - 添加以下变量：
   
   | 变量名 | 值 | 说明 |
   |--------|-----|------|
   | `VITE_API_BASE` | `https://your-render-app-name.onrender.com` | 后端 API 地址 |

5. **部署**
   - 点击 "Deploy site"
   - 等待部署完成（约 1-2 分钟）
   - 部署成功后，记下站点 URL，例如：`https://your-app-name.netlify.app`

---

### 第四步：测试应用

1. **访问前端**
   - 打开浏览器访问 Netlify 提供的 URL
   - 例如：`https://your-app-name.netlify.app`

2. **测试注册和登录**
   - 点击"注册"
   - 输入用户名和密码（至少 6 位）
   - 注册成功后自动登录

3. **测试主要功能**
   - 添加单词或句子
   - 查看 AI 分析结果
   - 测试查找相似内容
   - 测试同步功能

4. **测试图表页面**
   - 点击顶部导航的"图表"
   - 确认 TradingView Lightweight Charts 正常渲染

---

## 🔧 高级配置

### 使用 PostgreSQL（可选）

如果你需要使用 PostgreSQL 而不是 SQLite：

1. **在 Render 上创建 PostgreSQL 数据库**
   - 点击 "New +"
   - 选择 "PostgreSQL"
   - 创建数据库

2. **更新后端环境变量**
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   USE_CLOUD_DB=true
   ```

3. **重新部署后端**

---

### 自定义域名（可选）

1. **Netlify 自定义域名**
   - 进入 Site settings > Domain management
   - 点击 "Add custom domain"
   - 按照提示配置 DNS

2. **Render 自定义域名**
   - 进入 Web Service 设置
   - 点击 "Custom Domains"
   - 按照提示配置 DNS

---

## 📊 费用说明

### Netlify（前端）
- **免费额度**：
  - 100GB 带宽/月
  - 300 分钟构建时间/月
  - 无限站点
  - 自动 HTTPS
  - 全局 CDN

### Render（后端）
- **免费额度**：
  - 1 个 Web Service
  - 512MB RAM
  - 0.1 CPU
  - 24/7 运行（免费版会休眠）
  - 自动 HTTPS

**注意**：Render 免费版会在 15 分钟无活动后休眠，首次访问需要 30-60 秒启动时间。

---

## 🐛 常见问题

### 1. 后端部署失败

**问题**：Render 构建失败

**解决方案**：
- 检查 `requirements.txt` 是否正确
- 确保 Python 版本设置正确
- 查看 Render 日志获取详细错误信息

### 2. 前端无法连接后端

**问题**：CORS 错误或连接失败

**解决方案**：
- 确保 `VITE_API_BASE` 环境变量设置正确
- 检查后端是否正常运行
- 确认后端 CORS 配置允许所有来源（`allow_origins=["*"]`）

### 3. 登录失败

**问题**：注册或登录失败

**解决方案**：
- 确保密码至少 6 位
- 检查 `SECRET_KEY` 环境变量是否设置
- 查看 Render 日志获取错误信息

### 4. 图表不显示

**问题**：Lightweight Charts 页面空白

**解决方案**：
- 清除浏览器缓存
- 检查浏览器控制台是否有错误
- 确保 `lightweight-charts` 包已正确安装

---

## 🔄 持续部署

### 自动部署

**Netlify 和 Render 都配置了自动部署**：

1. 当你推送代码到 GitHub 的 `main` 分支时：
   - Netlify 自动重新构建前端
   - Render 自动重新构建后端

2. 你也可以手动触发部署：
   - Netlify：在 Dashboard 点击 "Deploy site"
   - Render：在 Dashboard 点击 "Manual Deploy"

---

## 📝 更新日志

### 2026-01-22
- ✅ 添加用户认证系统（注册/登录）
- ✅ 集成 Tailwind CSS，升级 UI
- ✅ 集成 TradingView Lightweight Charts
- ✅ 配置 Netlify + Render 部署
- ✅ 添加部署文档

---

## 🎉 完成！

你的应用现在已经成功部署到 Netlify 和 Render，实现了零成本的完整部署方案！

如有任何问题，请查看：
- [Netlify 文档](https://docs.netlify.com)
- [Render 文档](https://render.com/docs)
- 项目 GitHub Issues

---

## 📞 支持

如果遇到部署问题，可以：
1. 查看部署日志
2. 检查环境变量配置
3. 在 GitHub Issues 中提问

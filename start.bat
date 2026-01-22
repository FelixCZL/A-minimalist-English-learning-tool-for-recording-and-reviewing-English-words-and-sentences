@echo off
echo ========================================
echo English Study Tool - 启动脚本
echo ========================================
echo.

echo [1/2] 启动后端服务器...
cd /d "%~dp0backend"
start "Backend Server" cmd /k "python main.py"
echo 后端服务器已启动在 http://localhost:8000
echo.

echo [2/2] 等待3秒后启动前端...
timeout /t 3 /nobreak >nul

cd /d "%~dp0frontend"
start "Frontend Dev Server" cmd /k "npm run dev"
echo 前端服务器已启动在 http://localhost:5173
echo.

echo ========================================
echo 应用已启动！
echo 后端: http://localhost:8000
echo 前端: http://localhost:5173
echo API文档: http://localhost:8000/docs
echo ========================================
echo.
echo 注意: 关闭此窗口不会停止服务器。
echo 请关闭打开的命令行窗口来停止服务器。
echo.
pause

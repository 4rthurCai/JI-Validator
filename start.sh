#!/bin/bash

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "pip3 未安装，请先安装pip3"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 启动服务器
echo "启动FastAPI服务器..."
echo "服务器将在 http://localhost:8000 运行"
echo "前端页面请直接打开 index.html 文件"
echo ""
echo "按 Ctrl+C 停止服务器"
python main.py

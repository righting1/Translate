# 基于官方 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /myapp

# 复制依赖文件
COPY requirements.txt ./
COPY .env.example ./

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令（生产环境建议关闭 reload）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

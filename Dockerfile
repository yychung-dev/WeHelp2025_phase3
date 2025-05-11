# 使用 amd64 架構的 python 3.11 映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製依賴檔
COPY requirements.txt .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案
COPY . .

# 對外expose container port 8000
EXPOSE 8000

# 執行 FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]


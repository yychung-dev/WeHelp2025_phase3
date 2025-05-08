# 使用輕量級 Python 映像檔
FROM python:3.10-slim

# 建立 app 工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案檔案到容器內部
COPY . .

# 自動建立 uploads 資料夾（雖然 app 內有設，但這裡確保容器內也有）
RUN mkdir -p uploads

# 指定啟動指令（uvicorn 啟動 FastAPI 應用）
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
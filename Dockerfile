FROM python:3.10-slim

# 安裝必要套件
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# 設置環境變數
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="$PATH:/usr/bin"

# 複製程式碼
WORKDIR /app
COPY . .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 啟動服務
CMD ["python", "app.py"]

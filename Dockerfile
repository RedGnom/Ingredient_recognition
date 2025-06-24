FROM python:3.11.9

WORKDIR /app

# Устанавливаем системные зависимости для OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python-пакеты
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --upgrade inference-sdk==0.48.1 && \
    pip cache purge

# Копируем исходный код
COPY *.py ./

CMD ["python", "Bot.py"]
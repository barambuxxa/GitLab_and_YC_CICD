FROM python:3.10-slim

# Устанавливаем переменные окружения (аналог Lambda)
ENV LANG=en_US.UTF-8 \
    TZ=UTC \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Устанавливаем рабочий каталог (как в Lambda)
WORKDIR /var/task

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем существующий Lambda код
COPY lambda_function.py .

# Копируем HTTP-обертку для Yandex Serverless Containers
COPY server.py .

# Указываем порт (Yandex Cloud передаст PORT через переменную окружения)
EXPOSE ${PORT:-8080}

# Запускаем HTTP-сервер
CMD ["python", "server.py"]
FROM python:3.10-slim

# Устанавливаем системные зависимости
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя приложения
RUN useradd --create-home --shell /bin/bash app
WORKDIR /home/app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Меняем владельца файлов
RUN chown -R app:app .
USER app

# Создаем статическую папку
RUN mkdir -p static media

# Порт приложения
EXPOSE 8000

# Команда запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
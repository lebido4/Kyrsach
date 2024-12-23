FROM python:3.9

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем код приложения
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт API
EXPOSE 8001

# Запуск Flask приложения
CMD ["python", "app.py"]

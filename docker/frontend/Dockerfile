# Frontend Dockerfile
# Используем Nginx для раздачи статического контента

FROM nginx:alpine

# Удаление стандартной конфигурации
RUN rm /etc/nginx/conf.d/default.conf

# Копирование конфигурации Nginx (путь относительно контекста сборки - корня проекта)
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/

# Копирование статических файлов
COPY frontend/ /usr/share/nginx/html/

# Открытие порта
EXPOSE 80

# Команда запуска
CMD ["nginx", "-g", "daemon off;"]

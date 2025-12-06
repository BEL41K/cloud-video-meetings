# CloudMeet Lite

**Облачная платформа для видеоконференций**

CloudMeet Lite — это веб-приложение для видеоконференций

> **Примечание:** Данный проект является учебным и демонстрирует архитектурные решения. Реальная видеосвязь (WebRTC) не реализована, вместо неё используется имитация с текстовым чатом.

---

## 📋 Содержание

1. [Описание проекта](#описание-проекта)
2. [Технологический стек](#технологический-стек)
3. [Архитектура](#архитектура)
4. [Структура проекта](#структура-проекта)
5. [Быстрый старт](#быстрый-старт)
6. [Запуск в Docker Swarm](#запуск-в-docker-swarm)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [API Документация](#api-документация)
9. [Конфигурация](#конфигурация)

---

## 📝 Описание проекта

CloudMeet Lite позволяет:

- **Регистрация и авторизация** — создание аккаунта, вход в систему с использованием JWT токенов
- **Управление комнатами** — создание, просмотр списка и удаление комнат видеоконференций
- **Присоединение к комнатам** — вход в комнату и отслеживание статуса участников
- **Текстовый чат** — обмен сообщениями внутри комнаты в реальном времени
- **Имитация видеоконференции** — демонстрационный интерфейс с элементами управления

### Функциональные возможности

| Функция | Описание |
|---------|----------|
| Регистрация | Email, имя пользователя, пароль |
| Авторизация | JWT токены с настраиваемым временем жизни |
| Комнаты | CRUD операции, отслеживание активности |
| Участники | Статусы online/in_call/offline |
| Чат | История сообщений с кэшированием |

---

## 🛠 Технологический стек

### Backend
- **Python 3.12** — основной язык программирования
- **FastAPI** — современный асинхронный веб-фреймворк
- **SQLAlchemy 2.0** — ORM для работы с базой данных
- **Pydantic** — валидация данных и сериализация
- **PostgreSQL 15** — реляционная база данных
- **Redis 7** — кэширование данных
- **JWT (python-jose)** — аутентификация на основе токенов

### Frontend
- **HTML5 / CSS3** — разметка и стили
- **Vanilla JavaScript** — логика без фреймворков
- **Fetch API** — взаимодействие с backend

### DevOps
- **Docker** — контейнеризация сервисов
- **Docker Compose** — оркестрация для разработки
- **Docker Swarm** — кластеризация для продакшена
- **GitHub Actions** — CI/CD пайплайн
- **Nginx** — веб-сервер и reverse proxy

---

## 🏗 Архитектура

Проект построен на **микросервисной архитектуре** с использованием API Gateway паттерна.

```
┌─────────────────────────────────────────────────────────────┐
│                         КЛИЕНТ                              │
│                    (Браузер / SPA)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Nginx)                         │
│              Статические файлы + Reverse Proxy              │
│                        :80                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API GATEWAY                             │
│             FastAPI + JWT валидация                         │
│                        :8000                                │
└─────────────────────────────────────────────────────────────┘
                    │                   │
                    ▼                   ▼
┌───────────────────────┐   ┌───────────────────────┐
│     AUTH SERVICE      │   │  CONFERENCE SERVICE   │
│   FastAPI + SQLAlchemy│   │  FastAPI + SQLAlchemy │
│         :8000         │   │         :8000         │
└───────────────────────┘   └───────────────────────┘
            │                         │       │
            ▼                         ▼       ▼
┌───────────────────────┐   ┌─────────┐ ┌─────────┐
│      PostgreSQL       │   │PostgreSQL│ │  Redis  │
│    cloudmeet_auth     │   │conference│ │  Cache  │
└───────────────────────┘   └─────────┘ └─────────┘
```

### Микросервисы

#### 1. Auth Service (Сервис аутентификации)
- Регистрация новых пользователей
- Аутентификация и выдача JWT токенов
- Валидация токенов
- Хранение данных пользователей

**Endpoints:**
- `POST /api/auth/register` — регистрация
- `POST /api/auth/login` — авторизация
- `GET /api/auth/me` — текущий пользователь
- `GET /api/auth/validate` — валидация токена

#### 2. Conference Service (Сервис конференций)
- Управление комнатами видеоконференций
- Отслеживание участников
- Обмен сообщениями в чате
- Кэширование с помощью Redis

**Endpoints:**
- `POST /api/rooms` — создать комнату
- `GET /api/rooms` — список комнат
- `GET /api/rooms/{id}` — детали комнаты
- `POST /api/rooms/{id}/join` — войти в комнату
- `POST /api/rooms/{id}/leave` — выйти из комнаты
- `POST /api/rooms/{id}/messages` — отправить сообщение
- `GET /api/rooms/{id}/messages` — история сообщений

#### 3. Gateway (API шлюз)
- Единая точка входа для frontend
- Проксирование запросов к сервисам
- Валидация JWT токенов

---

## 📁 Структура проекта

```
cloud-video-meetings/
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # GitHub Actions pipeline
├── backend/
│   ├── auth-service/              # Сервис аутентификации
│   │   ├── app/
│   │   │   ├── api/               # API endpoints
│   │   │   │   ├── auth.py        # Роуты аутентификации
│   │   │   │   └── deps.py        # Зависимости
│   │   │   ├── core/              # Конфигурация
│   │   │   │   ├── config.py      # Настройки
│   │   │   │   └── security.py    # JWT и пароли
│   │   │   ├── db/                # База данных
│   │   │   │   └── database.py    # SQLAlchemy
│   │   │   ├── models/            # ORM модели
│   │   │   │   └── user.py        # Модель User
│   │   │   ├── schemas/           # Pydantic схемы
│   │   │   │   └── user.py        # Схемы User
│   │   │   └── main.py            # Точка входа
│   │   └── requirements.txt
│   ├── conference-service/        # Сервис конференций
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── rooms.py       # Роуты комнат
│   │   │   │   ├── messages.py    # Роуты сообщений
│   │   │   │   └── deps.py        # Зависимости
│   │   │   ├── core/
│   │   │   │   ├── config.py
│   │   │   │   └── security.py
│   │   │   ├── db/
│   │   │   │   ├── database.py
│   │   │   │   └── redis.py       # Redis клиент
│   │   │   ├── models/
│   │   │   │   ├── room.py        # Модель Room
│   │   │   │   ├── participant.py # Модель Participant
│   │   │   │   └── message.py     # Модель Message
│   │   │   ├── schemas/
│   │   │   │   ├── room.py
│   │   │   │   └── message.py
│   │   │   └── main.py
│   │   └── requirements.txt
│   └── gateway/                   # API Gateway
│       ├── app/
│       │   ├── api/
│       │   │   ├── auth.py        # Проксирование auth
│       │   │   ├── rooms.py       # Проксирование rooms
│       │   │   └── deps.py
│       │   ├── core/
│       │   │   ├── config.py
│       │   │   └── security.py
│       │   ├── services/
│       │   │   └── proxy.py       # HTTP клиент
│       │   └── main.py
│       └── requirements.txt
├── docker/
│   ├── auth-service/
│   │   └── Dockerfile
│   ├── conference-service/
│   │   └── Dockerfile
│   ├── gateway/
│   │   └── Dockerfile
│   └── frontend/
│       ├── Dockerfile
│       └── nginx.conf
├── frontend/
│   ├── index.html                 # Страница входа
│   ├── rooms.html                 # Список комнат
│   ├── room.html                  # Комната конференции
│   └── static/
│       ├── css/
│       │   ├── style.css          # Общие стили
│       │   ├── auth.css           # Стили авторизации
│       │   ├── rooms.css          # Стили списка комнат
│       │   └── room.css           # Стили комнаты
│       └── js/
│           ├── api.js             # API клиент
│           ├── auth.js            # Логика авторизации
│           ├── rooms.js           # Логика списка комнат
│           └── room.js            # Логика комнаты
├── scripts/
│   └── init-multiple-databases.sh # Инициализация БД
├── docker-compose.yml             # Для разработки
├── stack-compose.yml              # Для Docker Swarm
├── .env.example                   # Пример переменных
└── README.md                      # Документация
```

---

## 🚀 Быстрый старт

### Предварительные требования

- Docker 20.10+
- Docker Compose 2.0+
- Git

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/BEL41K/cloud-video-meetings.git
cd cloud-video-meetings
```

### Шаг 2: Настройка переменных окружения

```bash
cp .env.example .env
# Отредактируйте .env при необходимости
```

### Шаг 3: Запуск проекта

```bash
# Сделать скрипт инициализации исполняемым
chmod +x scripts/init-multiple-databases.sh

# Сборка и запуск всех сервисов
docker compose up --build -d
```

### Шаг 4: Проверка работоспособности

```bash
# Проверка статуса контейнеров
docker compose ps

# Проверка health endpoints
curl http://localhost:80/health      # Frontend
curl http://localhost:8000/health    # Gateway
curl http://localhost:8001/health    # Auth Service
curl http://localhost:8002/health    # Conference Service
```

### Шаг 5: Использование приложения

Откройте в браузере: **http://localhost**

1. Зарегистрируйтесь (email, имя, пароль)
2. Войдите в систему
3. Создайте комнату
4. Пригласите других пользователей (откройте в другом браузере/инкогнито)
5. Общайтесь в чате

### Остановка проекта

```bash
docker compose down

# Полная очистка (включая данные)
docker compose down --volumes --remove-orphans
```

---

## 🐳 Запуск в Docker Swarm

Docker Swarm обеспечивает кластеризацию с репликацией сервисов и балансировкой нагрузки.

### Инициализация Swarm

```bash
# На manager-ноде
docker swarm init

# На worker-нодах (используйте токен из вывода предыдущей команды)
docker swarm join --token <TOKEN> <MANAGER_IP>:2377
```

### Подготовка образов

Образы должны быть опубликованы в Docker Registry (Docker Hub):

```bash
# Логин в Docker Hub
docker login

# Сборка и публикация образов
export DOCKER_USERNAME=your_username

docker build -t $DOCKER_USERNAME/cloudmeet-auth-service:latest \
  -f docker/auth-service/Dockerfile backend/auth-service

docker build -t $DOCKER_USERNAME/cloudmeet-conference-service:latest \
  -f docker/conference-service/Dockerfile backend/conference-service

docker build -t $DOCKER_USERNAME/cloudmeet-gateway:latest \
  -f docker/gateway/Dockerfile backend/gateway

docker build -t $DOCKER_USERNAME/cloudmeet-frontend:latest \
  -f docker/frontend/Dockerfile .

docker push $DOCKER_USERNAME/cloudmeet-auth-service:latest
docker push $DOCKER_USERNAME/cloudmeet-conference-service:latest
docker push $DOCKER_USERNAME/cloudmeet-gateway:latest
docker push $DOCKER_USERNAME/cloudmeet-frontend:latest
```

### Деплой стека

```bash
# Экспорт переменных
export DOCKER_USERNAME=your_username
export JWT_SECRET_KEY=your-production-secret-key
export POSTGRES_PASSWORD=your-secure-password

# Деплой
docker stack deploy -c stack-compose.yml cloudmeet
```

### Управление стеком

```bash
# Просмотр сервисов
docker stack services cloudmeet

# Просмотр задач (контейнеров)
docker stack ps cloudmeet

# Логи сервиса
docker service logs cloudmeet_auth-service

# Масштабирование
docker service scale cloudmeet_auth-service=3

# Обновление сервиса
docker service update --image $DOCKER_USERNAME/cloudmeet-auth-service:v2 \
  cloudmeet_auth-service

# Удаление стека
docker stack rm cloudmeet
```

### Конфигурация Swarm

Файл `stack-compose.yml` содержит:

- **replicas: 2** — по 2 реплики backend сервисов
- **update_config** — политика обновления с rollback
- **restart_policy** — автоматический перезапуск при сбоях
- **resources** — лимиты памяти
- **overlay network** — внутренняя сеть кластера

---

## 🔄 CI/CD Pipeline

GitHub Actions автоматизирует сборку, тестирование и деплой.

### Workflow: `.github/workflows/ci-cd.yml`

#### Триггеры
- Push в ветку `main`
- Pull Request в ветку `main`

#### Jobs

1. **build-and-test**
   - Сборка Docker образов
   - Запуск всех сервисов
   - Health checks
   - Smoke tests (регистрация, логин, создание комнаты)

2. **push-images** (только для push в main)
   - Публикация образов в Docker Hub
   - Теги: `latest` и `{commit-sha}`

3. **deploy** (опционально)
   - SSH деплой на production сервер
   - Обновление Docker Swarm стека

### Настройка Secrets

В настройках репозитория GitHub (Settings → Secrets) добавьте:

| Secret | Описание |
|--------|----------|
| `DOCKER_USERNAME` | Логин Docker Hub |
| `DOCKER_PASSWORD` | Пароль/токен Docker Hub |
| `DEPLOY_HOST` | SSH хост для деплоя (опционально) |
| `DEPLOY_USER` | SSH пользователь (опционально) |
| `DEPLOY_KEY` | SSH приватный ключ (опционально) |
| `JWT_SECRET_KEY` | Секретный ключ для production |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL для production |

### Локальное тестирование CI

```bash
# Имитация CI локально
cp .env.example .env
docker compose build --parallel
docker compose up -d
sleep 30

# Smoke tests
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "display_name": "Test", "password": "testpass"}'

docker compose down --volumes
```

---

## 📚 API Документация

После запуска доступна автоматическая документация:

- **Gateway Swagger UI:** http://localhost:8000/docs
- **Gateway ReDoc:** http://localhost:8000/redoc
- **Auth Service Swagger:** http://localhost:8001/docs
- **Conference Service Swagger:** http://localhost:8002/docs

### Примеры запросов

#### Регистрация
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "display_name": "John Doe",
    "password": "securepassword"
  }'
```

#### Авторизация
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

#### Создание комнаты
```bash
curl -X POST http://localhost:8000/api/rooms \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Team Meeting"}'
```

#### Отправка сообщения
```bash
curl -X POST http://localhost:8000/api/rooms/1/messages \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, everyone!"}'
```

---

## ⚙️ Конфигурация

### Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `POSTGRES_USER` | cloudmeet | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | cloudmeet_secret | Пароль PostgreSQL |
| `JWT_SECRET_KEY` | super-secret-... | Секретный ключ JWT |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 60 | Время жизни токена |
| `REDIS_HOST` | redis | Хост Redis |
| `CACHE_TTL_SECONDS` | 300 | TTL кэша (5 минут) |

### Порты

| Сервис | Порт (dev) | Описание |
|--------|-----------|----------|
| Frontend | 80 | Веб-интерфейс |
| Gateway | 8000 | API Gateway |
| Auth Service | 8001 | Сервис аутентификации |
| Conference Service | 8002 | Сервис конференций |
| PostgreSQL | 5432 | База данных |
| Redis | 6379 | Кэш |

---

## 📄 Лицензия

MIT License

---

## 👥 Авторы

Курсовой проект по дисциплине "Облачные технологии"

---

**CloudMeet Lite** — демонстрация микросервисной архитектуры и современных DevOps практик.

# Инструкция по деплою

## Автоматический деплой

Запустите скрипт деплоя:

```bash
./deploy/deploy.sh
```

Скрипт выполнит:
1. Подключение к серверу
2. Клонирование/обновление репозитория
3. Установку Docker и Docker Compose (если не установлены)
4. Сборку и запуск Docker контейнера
5. Настройку nginx

## Ручной деплой

### 1. Подключение к серверу

```bash
ssh zambas124@158.160.120.116
```

### 2. Клонирование/обновление репозитория

```bash
cd ~
if [ -d "air" ]; then
    cd air
    git pull origin master
else
    git clone https://github.com/zamb124/air.git
    cd air
fi
```

### 3. Установка Docker (если не установлен)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 4. Установка Docker Compose (если не установлен)

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 5. Настройка config.json

```bash
if [ ! -f config.json ]; then
    cp config.json.example config.json
    # Отредактируйте config.json и укажите реальные токены API
fi
```

### 6. Запуск Docker контейнера

```bash
docker compose build
docker compose up -d
```

### 7. Настройка nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/air
sudo ln -s /etc/nginx/sites-available/air /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Управление Docker контейнером

```bash
# Статус
docker compose ps

# Логи
docker compose logs -f

# Перезапуск
docker compose restart

# Остановка
docker compose down

# Запуск
docker compose up -d

# Пересборка и перезапуск
docker compose build --no-cache
docker compose up -d
```

## Проверка работы

После деплоя проверьте:

```bash
# Проверка что сервис запущен
curl http://localhost:8001/

# Проверка через nginx
curl http://158.160.120.116/
```

## Важные замечания

1. Docker и Docker Compose должны быть установлены на сервере
2. Файл `config.json` должен быть создан на сервере (скопируйте из `config.json.example`)
3. База данных будет создана автоматически в `data/db.db` (монтируется как volume)
4. Docker контейнер работает на порту 8001 локально, nginx проксирует на порт 80
5. После установки Docker может потребоваться перелогиниться для применения группы docker


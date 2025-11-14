#!/bin/bash

set -e

SERVER="zambas124@158.160.120.116"
PROJECT_DIR="/home/zambas124/air"
REPO_URL="https://github.com/zamb124/air.git"

echo "🚀 Начинаем деплой на сервер..."

echo "📦 Подключение к серверу и клонирование/обновление репозитория..."
ssh $SERVER bash << ENDSSH
    PROJECT_DIR="$PROJECT_DIR"
    REPO_URL="$REPO_URL"
    
    if [ -d "\$PROJECT_DIR" ]; then
        echo "📂 Репозиторий уже существует, обновляем..."
        cd \$PROJECT_DIR
        git pull origin master
    else
        echo "📂 Клонируем репозиторий..."
        git clone \$REPO_URL \$PROJECT_DIR
        cd \$PROJECT_DIR
    fi

    echo "🐳 Проверяем Docker..."
    if ! command -v docker &> /dev/null; then
        echo "📦 Устанавливаем Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker \$USER
        rm get-docker.sh
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo "📦 Устанавливаем Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi

    echo "📝 Проверяем config.json..."
    if [ ! -f config.json ]; then
        if [ -f config.json.example ]; then
            echo "⚠️  config.json не найден, копируем из примера..."
            cp config.json.example config.json
            echo "⚠️  ВАЖНО: Отредактируйте config.json и укажите реальные токены API!"
        else
            echo "⚠️  ВНИМАНИЕ: config.json.example не найден!"
        fi
    fi

    echo "📁 Создаем директорию для данных..."
    mkdir -p data

    echo "🐳 Собираем и запускаем Docker контейнер..."
    DOCKER_CMD="docker"
    if ! docker ps &> /dev/null; then
        echo "⚠️  Docker требует sudo, используем sudo для команд..."
        DOCKER_CMD="sudo docker"
    fi
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
        if [ "\$DOCKER_CMD" = "sudo docker" ]; then
            COMPOSE_CMD="sudo docker-compose"
        fi
    else
        COMPOSE_CMD="docker compose"
        if [ "\$DOCKER_CMD" = "sudo docker" ]; then
            COMPOSE_CMD="sudo docker compose"
        fi
    fi
    
    \$COMPOSE_CMD down || true
    \$COMPOSE_CMD build --no-cache
    \$COMPOSE_CMD up -d

    echo "✅ Docker контейнер запущен"
ENDSSH

echo "📋 Копируем конфигурацию nginx..."
scp deploy/nginx.conf $SERVER:/tmp/air-nginx.conf

echo "⚙️ Настраиваем nginx на сервере..."
ssh $SERVER bash << 'ENDSSH'
    echo "🔧 Настраиваем nginx..."
    sudo mv /tmp/air-nginx.conf /etc/nginx/sites-available/air
    if [ -f /etc/nginx/sites-enabled/air ]; then
        sudo rm /etc/nginx/sites-enabled/air
    fi
    sudo ln -s /etc/nginx/sites-available/air /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx

    echo "📊 Статус Docker контейнеров:"
    if docker ps &> /dev/null; then
        if command -v docker-compose &> /dev/null; then
            docker-compose ps
        else
            docker compose ps
        fi
    else
        if command -v docker-compose &> /dev/null; then
            sudo docker-compose ps
        else
            sudo docker compose ps
        fi
    fi
ENDSSH

echo "✅ Деплой завершен!"
echo "🌐 Сервис доступен по адресу: http://158.160.120.116"


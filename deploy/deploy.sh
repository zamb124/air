#!/bin/bash

set -e

SERVER="zambas124@158.160.120.116"
PROJECT_DIR="/home/zambas124/air"
REPO_URL="https://github.com/zamb124/air.git"

IS_REMOTE=false
if [ -d "$PROJECT_DIR" ] && [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
    IS_REMOTE=true
    echo "🔍 Скрипт запущен на удаленном сервере, выполняем локально..."
fi

if [ "$IS_REMOTE" = true ]; then
    DEPLOY_FUNC() {
        deploy_local
    }
else
    DEPLOY_FUNC() {
        deploy_remote
    }
fi

deploy_local() {
    echo "🚀 Начинаем локальный деплой..."
    cd "$PROJECT_DIR"
    
    echo "📂 Обновляем репозиторий..."
    git pull origin master || true
    
    echo "🐳 Проверяем Docker..."
    if ! command -v docker &> /dev/null; then
        echo "📦 Устанавливаем Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
    fi
    
    echo "🔧 Запускаем Docker daemon..."
    sudo systemctl start docker
    sudo systemctl enable docker
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        echo "📦 Устанавливаем Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    echo "📝 Проверяем config.json..."
    if [ ! -f config.json ]; then
        if [ -f config.json.example ]; then
            echo "⚠️  config.json не найден, копируем из примера..."
            cp config.json.example config.json
            echo "⚠️  ВАЖНО: Отредактируйте config.json и укажите реальные токены API!"
        fi
    fi
    
    echo "📁 Создаем директорию для базы данных..."
    mkdir -p app/db
    
    echo "🐳 Останавливаем и пересобираем Docker контейнер (полная пересборка)..."
    
    if sudo docker ps &> /dev/null; then
        DOCKER_CMD="sudo docker"
        if command -v docker-compose &> /dev/null; then
            COMPOSE_CMD="sudo docker-compose"
        else
            COMPOSE_CMD="sudo docker compose"
        fi
    elif docker ps &> /dev/null 2>&1; then
        DOCKER_CMD="docker"
        if command -v docker-compose &> /dev/null; then
            COMPOSE_CMD="docker-compose"
        else
            COMPOSE_CMD="docker compose"
        fi
    else
        echo "❌ Не удалось подключиться к Docker daemon"
        exit 1
    fi
    
    echo "Используем команду: $COMPOSE_CMD"
    $COMPOSE_CMD down || true
    
    $COMPOSE_CMD build --no-cache --pull
    $COMPOSE_CMD up -d
    
    echo "🧹 Удаляем старые неиспользуемые образы проекта..."
    USED_IMAGE_ID=$($DOCKER_CMD inspect air-api --format='{{.Image}}' 2>/dev/null || echo "")
    if [ -n "$USED_IMAGE_ID" ]; then
        $DOCKER_CMD images "air-air" --format "{{.ID}}" | while read IMAGE_ID; do
            if [ "$IMAGE_ID" != "$USED_IMAGE_ID" ]; then
                $DOCKER_CMD rmi -f "$IMAGE_ID" 2>/dev/null || true
            fi
        done
    fi
    
    echo "🧹 Очищаем dangling образы и неиспользуемый кэш..."
    $DOCKER_CMD image prune -f || true
    
    echo "✅ Docker контейнер пересобран и запущен"
    
    echo "📊 Статус Docker контейнеров:"
    $COMPOSE_CMD ps
}

deploy_remote() {
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
    
    echo "🔧 Запускаем Docker daemon..."
    sudo systemctl start docker
    sudo systemctl enable docker

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

    echo "📁 Создаем директорию для базы данных..."
    mkdir -p app/db

    echo "🐳 Останавливаем и пересобираем Docker контейнер (полная пересборка)..."
    
    if sudo docker ps &> /dev/null; then
        DOCKER_CMD="sudo docker"
        if command -v docker-compose &> /dev/null; then
            COMPOSE_CMD="sudo docker-compose"
        else
            COMPOSE_CMD="sudo docker compose"
        fi
    elif docker ps &> /dev/null 2>&1; then
        DOCKER_CMD="docker"
        if command -v docker-compose &> /dev/null; then
            COMPOSE_CMD="docker-compose"
        else
            COMPOSE_CMD="docker compose"
        fi
    else
        echo "❌ Не удалось подключиться к Docker daemon"
        exit 1
    fi
    
    echo "Используем команду: \$COMPOSE_CMD"
    \$COMPOSE_CMD down || true
    
    \$COMPOSE_CMD build --no-cache --pull
    \$COMPOSE_CMD up -d
    
    echo "🧹 Удаляем старые неиспользуемые образы проекта..."
    USED_IMAGE_ID=\$(\$DOCKER_CMD inspect air-api --format='{{.Image}}' 2>/dev/null || echo "")
    if [ -n "\$USED_IMAGE_ID" ]; then
        \$DOCKER_CMD images "air-air" --format "{{.ID}}" | while read IMAGE_ID; do
            if [ "\$IMAGE_ID" != "\$USED_IMAGE_ID" ]; then
                \$DOCKER_CMD rmi -f "\$IMAGE_ID" 2>/dev/null || true
            fi
        done
    fi
    
    echo "🧹 Очищаем dangling образы и неиспользуемый кэш..."
    \$DOCKER_CMD image prune -f || true

    echo "✅ Docker контейнер пересобран и запущен"
ENDSSH

echo "📋 Копируем конфигурацию nginx..."
scp deploy/nginx.conf $SERVER:/tmp/air-nginx.conf

echo "⚙️ Настраиваем nginx на сервере..."
ssh $SERVER bash << 'ENDSSH'
    echo "🔧 Проверяем nginx..."
    if ! command -v nginx &> /dev/null; then
        echo "📦 Устанавливаем nginx..."
        sudo apt-get update
        sudo apt-get install -y nginx
        sudo systemctl start nginx
        sudo systemctl enable nginx
    fi
    
    echo "🔧 Настраиваем nginx..."
    sudo mkdir -p /etc/nginx/sites-available
    sudo mkdir -p /etc/nginx/sites-enabled
    sudo mv /tmp/air-nginx.conf /etc/nginx/sites-available/air
    if [ -f /etc/nginx/sites-enabled/air ]; then
        sudo rm /etc/nginx/sites-enabled/air
    fi
    sudo ln -s /etc/nginx/sites-available/air /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx

    echo "📊 Статус Docker контейнеров:"
    cd \$PROJECT_DIR
    if sudo docker ps &> /dev/null; then
        if command -v docker-compose &> /dev/null; then
            sudo docker-compose ps || true
        else
            sudo docker compose ps || true
        fi
    elif docker ps &> /dev/null 2>&1; then
        if command -v docker-compose &> /dev/null; then
            docker-compose ps || true
        else
            docker compose ps || true
        fi
    else
        echo "⚠️  Не удалось проверить статус контейнеров"
    fi
ENDSSH

    echo "✅ Деплой завершен!"
    echo "🌐 Сервис доступен по адресу: http://158.160.120.116"
}

DEPLOY_FUNC


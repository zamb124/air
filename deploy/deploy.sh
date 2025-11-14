#!/bin/bash

set -e

# Настройки подключения к серверу (можно переопределить через переменные окружения)
USERNAME="${USERNAME:-zambas124}"
SERVER_IP="${SERVER_IP:-158.160.120.116}"
SERVER="$USERNAME@$SERVER_IP"
PROJECT_DIR="/home/$USERNAME/air"
REPO_URL="https://github.com/zamb124/air.git"
DOMAIN="${DOMAIN:-omnistore.su}"  # По умолчанию используем omnistore.su, можно переопределить через переменную окружения

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
    
    echo "🔒 Настраиваем SSL для nginx..."
    DOMAIN="${DOMAIN:-omnistore.su}"
    SSL_CONFIG=""
    HAS_SELFSIGNED=false
    
    if [ -f "/etc/nginx/ssl/selfsigned.crt" ]; then
        HAS_SELFSIGNED=true
        echo "🔍 Обнаружен самоподписанный сертификат"
    fi
    
    if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "$SERVER_IP" ]; then
        echo "📦 Устанавливаем certbot для Let's Encrypt..."
        if ! command -v certbot &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y certbot python3-certbot-nginx
        fi
        
        echo "🔐 Проверяем SSL сертификат для домена $DOMAIN..."
        if sudo test -e "/etc/letsencrypt/live/$DOMAIN/fullchain.pem"; then
            echo "✅ SSL сертификат Let's Encrypt уже существует для $DOMAIN"
            SSL_CONFIG="ssl"
            SERVER_NAME="$DOMAIN"
        else
            if [ "$HAS_SELFSIGNED" = "true" ]; then
                echo "⚠️  Обнаружен самоподписанный сертификат, пытаемся получить Let's Encrypt..."
            fi
            echo "🔐 Получаем SSL сертификат для домена $DOMAIN..."
            
            CERTBOT_OUTPUT=$(sudo certbot certonly --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect 2>&1)
            CERTBOT_EXIT=$?
            
            sleep 2
            
            if [ -e "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
                echo "✅ SSL сертификат Let's Encrypt найден для $DOMAIN"
                SSL_CONFIG="ssl"
                SERVER_NAME="$DOMAIN"
            elif echo "$CERTBOT_OUTPUT" | grep -q "Certificate not yet due for renewal\|already exists\|Successfully received certificate"; then
                echo "ℹ️  Certbot сообщает, что сертификат существует, проверяем файл..."
                sleep 2
                if sudo test -e "/etc/letsencrypt/live/$DOMAIN/fullchain.pem"; then
                    echo "✅ SSL сертификат Let's Encrypt найден для $DOMAIN"
                    SSL_CONFIG="ssl"
                    SERVER_NAME="$DOMAIN"
                else
                    echo "⚠️  Файл сертификата не найден, проверяем альтернативные пути..."
                    CERT_PATH=$(sudo find /etc/letsencrypt -path "*/live/$DOMAIN/fullchain.pem" 2>/dev/null | head -1)
                    if [ -n "$CERT_PATH" ] && sudo test -e "$CERT_PATH"; then
                        echo "✅ SSL сертификат Let's Encrypt найден по пути: $CERT_PATH"
                        SSL_CONFIG="ssl"
                        SERVER_NAME="$DOMAIN"
                    else
                        echo "⚠️  Сертификат не найден, используем самоподписанный"
                        DOMAIN=""
                    fi
                fi
            elif [ $CERTBOT_EXIT -eq 0 ]; then
                sleep 1
                if sudo test -e "/etc/letsencrypt/live/$DOMAIN/fullchain.pem"; then
                    echo "✅ SSL сертификат Let's Encrypt успешно получен для $DOMAIN"
                    SSL_CONFIG="ssl"
                    SERVER_NAME="$DOMAIN"
                else
                    echo "❌ Сертификат не найден после получения"
                    DOMAIN=""
                fi
            else
                echo "❌ Не удалось получить сертификат Let's Encrypt"
                if [ "$HAS_SELFSIGNED" = "true" ]; then
                    echo "⚠️  Оставляем самоподписанный сертификат"
                fi
                DOMAIN=""
            fi
        fi
    fi
    
    if [ -z "$DOMAIN" ] || [ -z "$SSL_CONFIG" ]; then
        echo "🔐 Используем самоподписанный SSL сертификат..."
        sudo mkdir -p /etc/nginx/ssl
        if [ ! -f "/etc/nginx/ssl/selfsigned.crt" ]; then
            sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout /etc/nginx/ssl/selfsigned.key \
                -out /etc/nginx/ssl/selfsigned.crt \
                -subj "/C=RU/ST=State/L=City/O=Organization/CN=$SERVER_IP"
            echo "✅ Самоподписанный сертификат создан"
        else
            echo "✅ Используем существующий самоподписанный сертификат"
        fi
        SSL_CONFIG="ssl-selfsigned"
        SERVER_NAME="$SERVER_IP"
    fi
    
    echo "🔧 Настраиваем nginx с SSL..."
    sudo mkdir -p /etc/nginx/sites-available
    sudo mkdir -p /etc/nginx/sites-enabled
    
    if [ "$SSL_CONFIG" = "ssl" ]; then
        sudo tee /etc/nginx/sites-available/air > /dev/null << NGINX_EOF
server {
    listen 80;
    server_name $SERVER_NAME;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name $SERVER_NAME;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://127.0.0.1:8001/;
        access_log off;
    }
}
NGINX_EOF
    else
        sudo tee /etc/nginx/sites-available/air > /dev/null << NGINX_EOF
server {
    listen 80;
    server_name $SERVER_NAME;

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name $SERVER_NAME;

    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://127.0.0.1:8001/;
        access_log off;
    }
}
NGINX_EOF
    fi
    
    if [ -f /etc/nginx/sites-enabled/air ]; then
        sudo rm /etc/nginx/sites-enabled/air
    fi
    sudo ln -s /etc/nginx/sites-available/air /etc/nginx/sites-enabled/
    
    echo "🔍 Проверяем конфигурацию nginx..."
    if sudo nginx -t; then
        echo "✅ Конфигурация nginx валидна, перезагружаем..."
        sudo systemctl reload nginx
    else
        echo "❌ Ошибка в конфигурации nginx!"
        exit 1
    fi
    
    if [ "$SSL_CONFIG" = "ssl" ]; then
        echo "🔄 Настраиваем автоматическое обновление сертификата Let's Encrypt..."
        (crontab -l 2>/dev/null | grep -v "certbot renew" ; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab - || true
        echo "✅ Автообновление сертификата настроено (каждую ночь в 3:00)"
    fi
    
    echo "📊 Статус Docker контейнеров:"
    $COMPOSE_CMD ps
    
    echo "✅ Деплой завершен!"
    if [ -n "$DOMAIN" ]; then
        echo "🌐 Сервис доступен по адресу: https://$DOMAIN"
    else
        echo "🌐 Сервис доступен по адресу:"
        echo "   HTTP: http://$SERVER_IP (редирект на HTTPS)"
        echo "   HTTPS: https://$SERVER_IP (самоподписанный сертификат)"
    fi
}

deploy_remote() {
    echo "🚀 Начинаем деплой на сервер..."

echo "📦 Подключение к серверу и клонирование/обновление репозитория..."
ssh -o ConnectTimeout=30 -o ServerAliveInterval=60 $SERVER bash << ENDSSH
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

echo "⚙️ Настраиваем nginx и SSL на сервере..."
ssh -o ConnectTimeout=60 -o ServerAliveInterval=30 -o ServerAliveCountMax=10 -o TCPKeepAlive=yes $SERVER bash << ENDSSH
    PROJECT_DIR="$PROJECT_DIR"
    DOMAIN="${DOMAIN:-omnistore.su}"
    SERVER_IP="$SERVER_IP"
    
    echo "🔧 Проверяем nginx..."
    if ! command -v nginx &> /dev/null; then
        echo "📦 Устанавливаем nginx..."
        sudo apt-get update
        sudo apt-get install -y nginx
        sudo systemctl start nginx
        sudo systemctl enable nginx
    fi
    
    echo "🔒 Настраиваем SSL для домена: \$DOMAIN"
    SSL_CONFIG=""
    HAS_SELFSIGNED=false
    
    if [ -f "/etc/nginx/ssl/selfsigned.crt" ]; then
        HAS_SELFSIGNED=true
        echo "🔍 Обнаружен самоподписанный сертификат"
    fi
    
    if [ -n "\$DOMAIN" ] && [ "\$DOMAIN" != "\$SERVER_IP" ]; then
        echo "📦 Устанавливаем certbot для Let's Encrypt..."
        if ! command -v certbot &> /dev/null; then
            sudo apt-get install -y certbot python3-certbot-nginx
        fi
        
        echo "🔐 Проверяем SSL сертификат для домена \$DOMAIN..."
        if sudo test -e "/etc/letsencrypt/live/\$DOMAIN/fullchain.pem"; then
            echo "✅ SSL сертификат Let's Encrypt уже существует для \$DOMAIN"
            SSL_CONFIG="ssl"
            SERVER_NAME="\$DOMAIN"
        else
            if [ "\$HAS_SELFSIGNED" = "true" ]; then
                echo "⚠️  Обнаружен самоподписанный сертификат, пытаемся получить Let's Encrypt..."
            fi
            echo "🔐 Получаем SSL сертификат для домена \$DOMAIN..."
            echo "⚠️  Убедитесь, что домен \$DOMAIN указывает на IP \$SERVER_IP"
            echo "⚠️  Убедитесь, что порты 80 и 443 открыты в firewall"
            
            CERTBOT_OUTPUT=\$(sudo certbot certonly --nginx -d \$DOMAIN --non-interactive --agree-tos --email admin@\$DOMAIN --redirect 2>&1)
            CERTBOT_EXIT=\$?
            
            sleep 2
            
            if sudo test -e "/etc/letsencrypt/live/\$DOMAIN/fullchain.pem"; then
                echo "✅ SSL сертификат Let's Encrypt найден для \$DOMAIN"
                SSL_CONFIG="ssl"
                SERVER_NAME="\$DOMAIN"
            elif echo "\$CERTBOT_OUTPUT" | grep -q "Certificate not yet due for renewal\|already exists\|Successfully received certificate"; then
                echo "ℹ️  Certbot сообщает, что сертификат существует, проверяем файл..."
                sleep 2
                if sudo test -e "/etc/letsencrypt/live/\$DOMAIN/fullchain.pem"; then
                    echo "✅ SSL сертификат Let's Encrypt найден для \$DOMAIN"
                    SSL_CONFIG="ssl"
                    SERVER_NAME="\$DOMAIN"
                else
                    echo "⚠️  Файл сертификата не найден, проверяем альтернативные пути..."
                    CERT_PATH=\$(sudo find /etc/letsencrypt -path "*/live/\$DOMAIN/fullchain.pem" 2>/dev/null | head -1)
                    if [ -n "\$CERT_PATH" ] && sudo test -e "\$CERT_PATH"; then
                        echo "✅ SSL сертификат Let's Encrypt найден по пути: \$CERT_PATH"
                        SSL_CONFIG="ssl"
                        SERVER_NAME="\$DOMAIN"
                    else
                        echo "⚠️  Сертификат не найден, используем самоподписанный"
                        DOMAIN=""
                    fi
                fi
            elif [ \$CERTBOT_EXIT -eq 0 ]; then
                sleep 1
                if sudo test -e "/etc/letsencrypt/live/\$DOMAIN/fullchain.pem"; then
                    echo "✅ SSL сертификат Let's Encrypt успешно получен для \$DOMAIN"
                    SSL_CONFIG="ssl"
                    SERVER_NAME="\$DOMAIN"
                else
                    echo "❌ Сертификат не найден после получения"
                    DOMAIN=""
                fi
            else
                echo "❌ Не удалось получить сертификат Let's Encrypt"
                if [ "\$HAS_SELFSIGNED" = "true" ]; then
                    echo "⚠️  Оставляем самоподписанный сертификат"
                fi
                DOMAIN=""
            fi
        fi
    fi
    
    if [ -z "\$DOMAIN" ] || [ -z "\$SSL_CONFIG" ]; then
        echo "🔐 Используем самоподписанный SSL сертификат..."
        sudo mkdir -p /etc/nginx/ssl
        if [ ! -f "/etc/nginx/ssl/selfsigned.crt" ]; then
            sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout /etc/nginx/ssl/selfsigned.key \
                -out /etc/nginx/ssl/selfsigned.crt \
                -subj "/C=RU/ST=State/L=City/O=Organization/CN=\$SERVER_IP"
            echo "✅ Самоподписанный сертификат создан"
        else
            echo "✅ Используем существующий самоподписанный сертификат"
        fi
        SSL_CONFIG="ssl-selfsigned"
        SERVER_NAME="\$SERVER_IP"
    fi
    
    echo "🔧 Настраиваем nginx с SSL..."
    sudo mkdir -p /etc/nginx/sites-available
    sudo mkdir -p /etc/nginx/sites-enabled
    
    if [ "\$SSL_CONFIG" = "ssl" ]; then
        cat > /tmp/air-nginx-ssl.conf << NGINX_EOF
server {
    listen 80;
    server_name \$SERVER_NAME;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\\\$host\\\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name \$SERVER_NAME;

    ssl_certificate /etc/letsencrypt/live/\$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/\$DOMAIN/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/\$DOMAIN/chain.pem;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \\\$host;
        proxy_set_header X-Real-IP \\\$remote_addr;
        proxy_set_header X-Forwarded-For \\\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\\$scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://127.0.0.1:8001/;
        access_log off;
    }
}
NGINX_EOF
        sudo mv /tmp/air-nginx-ssl.conf /etc/nginx/sites-available/air
    else
        cat > /tmp/air-nginx-ssl.conf << NGINX_EOF
server {
    listen 80;
    server_name \$SERVER_NAME;

    location / {
        return 301 https://\\\$host\\\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name \$SERVER_NAME;

    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \\\$host;
        proxy_set_header X-Real-IP \\\$remote_addr;
        proxy_set_header X-Forwarded-For \\\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\\$scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://127.0.0.1:8001/;
        access_log off;
    }
}
NGINX_EOF
        sudo mv /tmp/air-nginx-ssl.conf /etc/nginx/sites-available/air
    fi
    
    if [ -f /etc/nginx/sites-enabled/air ]; then
        sudo rm /etc/nginx/sites-enabled/air
    fi
    sudo ln -s /etc/nginx/sites-available/air /etc/nginx/sites-enabled/
    
    echo "🔍 Проверяем конфигурацию nginx..."
    if sudo nginx -t; then
        echo "✅ Конфигурация nginx валидна, перезагружаем..."
        sudo systemctl reload nginx
    else
        echo "❌ Ошибка в конфигурации nginx!"
        exit 1
    fi
    
    if [ "\$SSL_CONFIG" = "ssl" ]; then
        echo "🔄 Настраиваем автоматическое обновление сертификата Let's Encrypt..."
        (crontab -l 2>/dev/null | grep -v "certbot renew" ; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab - || true
        echo "✅ Автообновление сертификата настроено (каждую ночь в 3:00)"
    fi

    echo "📊 Статус Docker контейнеров:"
    cd "\$PROJECT_DIR"
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
    if [ -n "$DOMAIN" ]; then
        echo "🌐 Сервис доступен по адресу: https://$DOMAIN"
    else
        echo "🌐 Сервис доступен по адресу:"
        echo "   HTTP: http://$SERVER_IP (редирект на HTTPS)"
        echo "   HTTPS: https://$SERVER_IP (самоподписанный сертификат)"
    fi
}

DEPLOY_FUNC


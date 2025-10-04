#!/bin/bash

echo "🚀 Запуск системы управления энергосистемой Эстонии"
echo "=================================================="

if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден. Установите Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не найден. Установите Docker Compose"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "🔧 Создание .env файла..."
    cat > .env << EOF
HOST=0.0.0.0
PORT=9000
DEBUG=False
DATABASE_URL=energy_system.db
SECRET_KEY=est_energy_system_secret_key
EOF
fi

echo "📁 Создание необходимых директорий..."
mkdir -p data logs

echo "🛑 Остановка существующих контейнеров..."
docker-compose down

echo "🔨 Сборка Docker образа..."
docker-compose build

echo "🌐 Запуск веб-сервера в контейнере..."
echo "📍 Сервер: http://localhost:9000"
echo ""
echo "🛑 Для остановки нажмите Ctrl+C"
echo ""

docker-compose up

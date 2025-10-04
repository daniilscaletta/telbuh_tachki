#!/bin/bash
set -e

echo "🚀 Запуск Оперативного Центра Энергетики и Транспорта..."
echo "📋 Симулятор уязвимостей для обучения"
echo ""

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден. Пожалуйста, установите Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не найден. Пожалуйста, установите Docker Compose."
    exit 1
fi

if [ ! -f .env ]; then
    echo "📝 Создание файла конфигурации .env..."
    cp env.example .env
    echo "✅ Файл .env создан из шаблона"
fi

if [ ! -f .env ]; then
    echo "❌ Файл .env не найден. Создайте его на основе env.example"
    exit 1
fi

echo "🔧 Настройка переменных окружения..."
source .env

echo "📦 Сборка Docker образа..."
docker-compose build

echo "🚀 Запуск системы..."
docker-compose up -d

echo ""
echo "✅ Система запущена!"
echo ""
echo "🌐 Веб-интерфейс доступен по адресу: http://localhost:${APP_PORT:-5557}"
echo ""

# Проверяем статус контейнера
sleep 3
if docker-compose ps | grep -q "Up"; then
    echo "✅ Контейнер успешно запущен"
    echo "🌐 Откройте браузер и перейдите по адресу: http://localhost:${APP_PORT:-5557}"
else
    echo "❌ Ошибка запуска контейнера"
    exit 1
fi

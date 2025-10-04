#!/bin/bash

echo "🚀 Запуск системы управления энергосистемой Эстонии"
echo "=================================================="

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install -r requirements.txt

# Создание .env файла
if [ ! -f ".env" ]; then
    echo "🔧 Создание .env файла..."
    cp env.example .env
fi

# Запуск системы
echo "🌐 Запуск веб-сервера..."
echo "📍 Сервер: http://localhost:9000"
echo "🔓 SQL Injection: http://localhost:9000/search"
echo "🏁 Флаг: EST_ENERGY_SYSTEM_2024"
echo ""
echo "⚠️  ВНИМАНИЕ: Это демонстрационный проект с учебными уязвимостями!"
echo "📖 Инструкция по взлому: ЗАПУСК_И_ВЗЛОМ.md"
echo ""
echo "🛑 Для остановки нажмите Ctrl+C"
echo ""

python main.py

import sqlite3
import os
from typing import List, Tuple, Optional
from app.models.energy_models import PowerStation, EnergyConsumption, SystemAlert

def read_flag():
    """Читает флаг из файла"""
    # Попробуем найти флаг в разных местах
    possible_paths = [
        "/app/flag/flag",
        "app/flag/flag",
        "flag/flag"
    ]
    
    for flag_file_path in possible_paths:
        if os.path.exists(flag_file_path):
            with open(flag_file_path, 'r') as f:
                return f.read().strip()
    
    # Если флаг не найден, возвращаем тестовый
    return "FLAG_NOT_FOUND"

class DatabaseManager:
    """Менеджер базы данных для системы управления энергосистемой"""
    
    def __init__(self, db_path: str = "energy_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Получить соединение с базой данных"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Создание таблиц
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS power_stations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                capacity_mw REAL NOT NULL,
                status TEXT NOT NULL,
                operator TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS energy_consumption (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT NOT NULL,
                consumption_mwh REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_flags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flag_name TEXT UNIQUE NOT NULL,
                flag_value TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Добавление тестовых данных
        self._insert_test_data(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_test_data(self, cursor):
        """Добавление тестовых данных"""
        # Estonian Power Stations
        stations = [
            ("Eesti Energia Narva Power Plants", "Narva", 1800.0, "Active", "Eesti Energia"),
            ("Iru Power Plant", "Tallinn", 1200.0, "Active", "Eesti Energia"),
            ("Auvere Power Plant", "Narva", 300.0, "Active", "Eesti Energia"),
            ("Balti Power Plant", "Narva", 1500.0, "Active", "Eesti Energia"),
            ("Keila-Joa Hydroelectric Plant", "Keila-Joa", 1.2, "Active", "Eesti Energia"),
            ("Kunda Cement Plant", "Kunda", 50.0, "Active", "Kunda Nordic Tsement"),
            ("Tallinn Combined Heat and Power", "Tallinn", 200.0, "Active", "Tallinna Küte"),
            ("Tartu District Heating", "Tartu", 150.0, "Active", "Tartu Energia")
        ]
        
        for station in stations:
            cursor.execute('''
                INSERT OR IGNORE INTO power_stations (name, location, capacity_mw, status, operator)
                VALUES (?, ?, ?, ?, ?)
            ''', station)
        
        # Estonian Energy Consumption by Counties
        consumption_data = [
            ("Harju County", 2500.5),
            ("Tartu County", 1800.3),
            ("Ida-Viru County", 2200.7),
            ("Pärnu County", 1200.2),
            ("Lääne-Viru County", 900.1),
            ("Viljandi County", 800.8),
            ("Saare County", 600.4),
            ("Võru County", 500.9)
        ]
        
        for data in consumption_data:
            cursor.execute('''
                INSERT OR IGNORE INTO energy_consumption (region, consumption_mwh)
                VALUES (?, ?)
            ''', data)
        
        # Estonian System Alerts
        alerts = [
            ("Warning", "High network load in Harju County", "Medium"),
            ("Information", "Scheduled maintenance on 330kV line Tallinn-Narva", "Low"),
            ("Critical", "Emergency shutdown of substation #15 in Tartu", "High"),
            ("Information", "Completion of scheduled maintenance at Iru Power Plant", "Low"),
            ("Warning", "Increased consumption during peak hours in Tallinn", "Medium")
        ]
        
        for alert in alerts:
            cursor.execute('''
                INSERT OR IGNORE INTO system_alerts (alert_type, message, severity)
                VALUES (?, ?, ?)
            ''', alert)
        
        # System Flag
        system_flag = read_flag()
        cursor.execute('''
            INSERT OR IGNORE INTO system_flags (flag_name, flag_value, description)
            VALUES (?, ?, ?)
        ''', ("TASK_COMPLETED", system_flag, "Estonian Energy System Management Task Completion Flag"))
    
    def get_all_stations(self) -> List[Tuple]:
        """Получить все электростанции"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM power_stations ORDER BY name")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_all_consumption(self) -> List[Tuple]:
        """Получить все данные потребления"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM energy_consumption ORDER BY consumption_mwh DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_all_alerts(self) -> List[Tuple]:
        """Получить все уведомления"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM system_alerts ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_stations_vulnerable(self, query: str) -> List[Tuple]:
        """
        УЯЗВИМЫЙ МЕТОД: Поиск станций с SQL injection уязвимостью
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # УЯЗВИМОСТЬ: Прямая подстановка без экранирования
        sql_query = f"SELECT * FROM power_stations WHERE name LIKE '%{query}%' OR location LIKE '%{query}%'"
        
        try:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            conn.close()
            # Возвращаем информативную ошибку для SQL injection
            error_msg = str(e)
            if "UNION" in error_msg and "columns" in error_msg:
                # Информативная ошибка о количестве колонок
                raise Exception(f"SQL Error: {error_msg}. Hint: The query has 7 columns (id, name, location, capacity_mw, status, operator, created_at). Try: ' UNION SELECT 1,2,3,4,5,6,7 --")
            elif "no such table" in error_msg.lower():
                # Информативная ошибка о таблицах
                raise Exception(f"SQL Error: {error_msg}. Hint: Available tables: power_stations, energy_consumption, system_alerts, system_flags")
            elif "no such column" in error_msg.lower():
                # Информативная ошибка о колонках
                raise Exception(f"SQL Error: {error_msg}. Hint: Check column names in the database schema")
            else:
                raise Exception(f"SQL Error: {error_msg}")
    
    def search_with_sql_injection(self, query: str) -> List[Tuple]:
        """
        УЯЗВИМЫЙ МЕТОД: Поиск с SQL injection для получения флага
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # УЯЗВИМОСТЬ: Прямая подстановка без экранирования
        sql_query = f"SELECT * FROM power_stations WHERE name LIKE '%{query}%' OR location LIKE '%{query}%'"
        
        try:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            conn.close()
            raise e
    
    def get_system_flag(self, flag_name: str) -> Optional[str]:
        """Получить системный флаг"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT flag_value FROM system_flags WHERE flag_name = ?", (flag_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_database_schema(self) -> dict:
        """Получить схему базы данных для SQL injection"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Получаем информацию о таблицах
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            schema[table] = [col[1] for col in columns]
        
        conn.close()
        return schema
    
    def get_system_statistics(self) -> dict:
        """Получить статистику системы"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Статистика станций
        cursor.execute("SELECT COUNT(*) FROM power_stations")
        total_stations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM power_stations WHERE status = 'Active'")
        active_stations = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(capacity_mw) FROM power_stations")
        total_capacity = cursor.fetchone()[0] or 0
        
        # Статистика потребления
        cursor.execute("SELECT SUM(consumption_mwh) FROM energy_consumption")
        total_consumption = cursor.fetchone()[0] or 0
        
        # Статистика уведомлений
        cursor.execute("SELECT COUNT(*) FROM system_alerts")
        total_alerts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_stations": total_stations,
            "active_stations": active_stations,
            "total_capacity": total_capacity,
            "total_consumption": total_consumption,
            "total_alerts": total_alerts
        }

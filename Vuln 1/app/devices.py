import time
import threading
from typing import Dict, List
import random

class Device:
    def __init__(self, id: str, kind: str, name: str, location: str, role: str):
        self.id = id
        self.kind = kind
        self.name = name
        self.location = location
        self.role = role
        self.status = "OK"  # OK | WARNING | OFFLINE | DEGRADED | COMPROMISED
        self.load = 10.0
        self.last_seen = time.time()
        self.extra = {}
        self.power_level = 75  # Додано: рівень потужності
        self.voltage = 50      # Додано: рівень напруги
        self.temperature = 35  # Додано: температура

    def to_dict(self):
        return {
            "id": self.id,
            "kind": self.kind,
            "name": self.name,
            "location": self.location,
            "role": self.role,
            "status": self.status,
            "load": round(self.load, 2),
            "last_seen": int(self.last_seen),
            "power_level": self.power_level,
            "voltage": self.voltage,
            "temperature": self.temperature,
            "extra": self.extra
        }

class DeviceManager:
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.lock = threading.Lock()

    def seed_sample(self):
        # реалістичні об'єкти в доменах: енергетика, транспорт, оборона
        self.add(Device("pp-1", "power", "Електростанція «Альфа»", "Район Північ-1", "Генерація"))
        self.add(Device("ss-1", "substation", "Підстанція Північ", "Район Північ-2", "Розподіл"))
        self.add(Device("th-1", "transport", "Хаб поїздів Центр", "Станція Центр", "Транспортний вузол"))
        self.add(Device("rad-1", "defense", "РЛС Схід", "Гора Східна", "Спостереження"))
        t = threading.Thread(target=self._telemetry_pulse, daemon=True)
        t.start()

    def add(self, device: Device):
        with self.lock:
            self.devices[device.id] = device

    def list_devices(self) -> List[dict]:
        with self.lock:
            return [d.to_dict() for d in self.devices.values()]

    def get(self, device_id: str):
        return self.devices.get(device_id)

    def restart_device(self, device_id: str):
        d = self.get(device_id)
        if not d:
            return False
        with self.lock:
            d.status = "OK"
            d.load = max(5.0, d.load * 0.6)
            d.last_seen = time.time()
            d.extra["note"] = "Перезапущено оператором (симуляція)"
        return True

    def isolate_device(self, device_id: str):
        d = self.get(device_id)
        if not d:
            return False
        with self.lock:
            d.status = "DEGRADED"
            d.extra["note"] = "Ізольовано для розслідування (симуляція)"
        return True

    def mark_compromised(self, device_id: str, note: str = ""):
        d = self.get(device_id)
        if not d:
            return False
        with self.lock:
            d.status = "COMPROMISED"
            d.extra["compromise_note"] = note
            d.last_seen = time.time()
        return True

    # Новий метод: регулювання потужності
    def adjust_power(self, device_id: str, power_level: int):
        d = self.get(device_id)
        if not d:
            return False
        with self.lock:
            d.power_level = power_level
            d.extra["power_adjusted"] = f"Потужність змінена на {power_level}%"
            # Вплив на навантаження
            d.load = max(5, min(120, d.load + (power_level - 75) / 10))
        return True

    # Новий метод: регулювання напруги
    def adjust_voltage(self, device_id: str, voltage: int):
        d = self.get(device_id)
        if not d:
            return False
        with self.lock:
            d.voltage = voltage
            d.extra["voltage_adjusted"] = f"Напруга змінена на {voltage}%"
        return True

    # simulations
    def simulate_grid_cascade(self):
        with self.lock:
            for d in self.devices.values():
                if d.kind in ("power", "substation"):
                    d.load += random.uniform(15.0, 40.0)
                    d.status = "WARNING" if d.load < 90 else "OFFLINE"
                    d.last_seen = time.time()
            if "pp-1" in self.devices:
                self.devices["pp-1"].extra["cascade_note"] = "Перевантаження розпочато " + time.ctime()
        return True

    def simulate_spoof_telemetry(self):
        with self.lock:
            if "th-1" in self.devices:
                d = self.devices["th-1"]
                d.extra["spoofed_route"] = True
                d.status = "WARNING"
                d.last_seen = time.time()
        return True

    def simulate_transport_deadlock(self):
        with self.lock:
            if "th-1" in self.devices:
                d = self.devices["th-1"]
                d.status = "OFFLINE"
                d.extra["deadlock_note"] = "Конфлікт міжсистемних interlock-правил"
                d.last_seen = time.time()
        return True

    def _telemetry_pulse(self):
        while True:
            with self.lock:
                for d in self.devices.values():
                    # Змінюємо параметри з урахуванням встановлених значень
                    d.load += random.uniform(-3.0, 3.0)
                    d.load = max(0.0, min(120.0, d.load))
                    
                    # Температура залежить від навантаження
                    d.temperature = 20 + (d.load / 120 * 40) + random.uniform(-2, 2)
                    
                    if random.random() < 0.02:
                        d.status = random.choice(["OK", "WARNING", "DEGRADED"])
                    d.last_seen = time.time()
            time.sleep(2.0)
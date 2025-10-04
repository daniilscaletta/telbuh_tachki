from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class PowerStation:
    """Модель електростанції"""
    id: Optional[int] = None
    name: str = ""
    location: str = ""
    capacity_mw: float = 0.0
    status: str = "Активна"
    operator: str = ""
    created_at: Optional[datetime] = None

@dataclass
class EnergyConsumption:
    """Модель споживання енергії"""
    id: Optional[int] = None
    region: str = ""
    consumption_mwh: float = 0.0
    timestamp: Optional[datetime] = None

@dataclass
class SystemAlert:
    """Модель системного сповіщення"""
    id: Optional[int] = None
    alert_type: str = ""
    message: str = ""
    severity: str = "Низька"
    timestamp: Optional[datetime] = None

@dataclass
class SearchResult:
    """Модель результату пошуку"""
    query: str = ""
    results: list = None
    total_count: int = 0
    
    def __post_init__(self):
        if self.results is None:
            self.results = []

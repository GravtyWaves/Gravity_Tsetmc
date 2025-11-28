"""Configuration settings used by core clients"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class TSEClientConfig:
    BASE_URL_NEW: str = "https://cdn.tsetmc.com/api"
    BASE_URL_OLD: str = "https://old.tsetmc.com/tsev2/data"
    HEADERS: Optional[Dict[str, str]] = None
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3

    def __post_init__(self):
        if self.HEADERS is None:
            self.HEADERS = {
                'User-Agent': 'Mozilla/5.0 (compatible; GravityTSE/1.0; +https://github.com/GravtyWaves)'
            }

config = TSEClientConfig()

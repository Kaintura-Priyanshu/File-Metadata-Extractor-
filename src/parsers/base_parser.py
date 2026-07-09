from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple, Dict, Any


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> Tuple[Any, Dict[str, Any]]:
        pass
    
    def _safe_get(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        return data.get(key, default)
    
    def _convert_to_int(self, value: Any, default: Any = None) -> Any:
        try:
            if value is not None:
                return int(value)
            return default
        except (ValueError, TypeError):
            return default
    
    def _convert_to_float(self, value: Any, default: Any = None) -> Any:
        try:
            if value is not None:
                return float(value)
            return default
        except (ValueError, TypeError):
            return default

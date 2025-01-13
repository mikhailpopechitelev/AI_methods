from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, ValidationError, Field, field_serializer, field_validator, model_validator, AnyUrl
from enum import IntEnum
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG
from verboselogs import VERBOSE, SPAM
from typing import Literal, Any, Union, Optional
from .logging import Logging

from shared.types.context import Context
from shared.types.expandUserPath import ExpandUserPath
from pathlib import Path
import json



class Config(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(env_prefix="WooBook_", extra="ignore")
    tgToken: str = 'xxx'
    gptToken: str = 'xxx'
    dsn: AnyUrl = "sqlite:///sqlite.db"
    
    logging: Logging = Logging()
    _context: Optional[Context] = None
    
    def save(self, path: Path) -> None:
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=4))
    
    @classmethod
    def fromFile(cls, path: Path) -> Config:
        default  = cls()
        with open (path, "r") as f:
            data: dict[str, Any] = json.load(f)
            default.model_dump(mode="json").update(data)
            
            return cls(**data)
        
    
configExample: Config = Config()

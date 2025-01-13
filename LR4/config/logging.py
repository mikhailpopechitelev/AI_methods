from __future__ import annotations
from pydantic import BaseModel, ValidationError, Field, field_serializer, field_validator, model_validator, AnyUrl
from enum import IntEnum
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG
from verboselogs import VERBOSE, SPAM
from typing import Literal, Any, Union
from shared.types.expandUserPath import ExpandUserPath
from pathlib import Path



class LoggingLevel(IntEnum):
    CRITICAL = CRITICAL
    ERROR = ERROR  
    WARNING = WARNING
    INFO = INFO
    VERBOSE = VERBOSE
    DEBUG = DEBUG
    SPAM = SPAM


class Logging(BaseModel):
    name: str = "WooBook"
    level: Literal[LoggingLevel.SPAM, 
                    LoggingLevel.DEBUG,
                    LoggingLevel.VERBOSE,
                    LoggingLevel.INFO,
                    LoggingLevel.WARNING,
                    LoggingLevel.ERROR,
                    LoggingLevel.CRITICAL] = LoggingLevel.INFO

    path: ExpandUserPath = Path(".")
    
    @field_serializer("level") # type: ignore[misc]
    def loggingLevelSerializer(self, level: LoggingLevel, _info: Any) -> str:
        match level:
            case LoggingLevel.SPAM:
                return "spam"
            case LoggingLevel.DEBUG:
                return "debug"
            case LoggingLevel.VERBOSE:
                return "verbose"
            case LoggingLevel.INFO:
                return "info"
            case LoggingLevel.WARNING:
                return "warning"
            case LoggingLevel.ERROR:
                return "error"
            case LoggingLevel.CRITICAL:
                return "critical"
            
            case _:
                raise ValidationError("Unprocessed ConfigLoggingLevel you probably forgot to add a case for this one")
    
    @field_validator("level", mode="before") # type: ignore
    def loggingLevelValidator(cls, value: Union[int, str]) -> LoggingLevel:
        if isinstance(value, int):
            try:
                return LoggingLevel(value)
            except:
                raise ValidationError("Must be one of [spam, debug, verbose, info, warning, error, critical]")
        
        elif isinstance(value, str):
            val = value.lower()
            match val:
                case "spam":
                    return LoggingLevel.SPAM
                case "debug":
                    return LoggingLevel.DEBUG
                case "verbose":
                    return LoggingLevel.VERBOSE
                case "info":
                    return LoggingLevel.INFO
                case "warning":
                    return LoggingLevel.WARNING
                case "error":
                    return LoggingLevel.ERROR
                case "critical":
                    return LoggingLevel.CRITICAL
                case _:
                    raise ValidationError("Must be one of [spam, debug, verbose, info, warning, error, critical]")
        else:
            raise ValidationError("Must be int or str contained int value")


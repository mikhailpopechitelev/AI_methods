from verboselogs import VerboseLogger, SPAM, NOTICE, VERBOSE
from config.logging import Logging
from shared.singleton import SingletonMeta
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, LogRecord
from logging.handlers import MemoryHandler
from pathlib import Path
from datetime import datetime
import pytz

from typing import List

from time import gmtime

import logging
import coloredlogs
import os


class Logger(VerboseLogger, metaclass=SingletonMeta):
    def __init__(self, config: Logging):
        self.config = config
        self.path = config.path
        
        super().__init__(self.config.name, self.config.level)
        
        self.path.mkdir(parents=True, exist_ok=True)
        
        fileName = datetime.now(pytz.utc).strftime(f"{self.config.name}_%d-%m-%Y") + ".log"
        self.logFile = self.path / fileName
        
        self.file = logging.FileHandler(str(self.logFile))
        self.fileformat = logging.Formatter(
            "[~] %(asctime)s [%(levelname)s] - %(message)s")
        
        self.file.setLevel(self.level)
        self.file.setFormatter(self.fileformat)
        
        super().addHandler(self.file)
        coloredlogs.install(level=self.config.level, logger=super(),
                            fmt='%(asctime)s [%(levelname)s] - %(message)s')
        
        logging.Formatter.converter = gmtime

        super().info('Start Logger')

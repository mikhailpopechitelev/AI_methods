from dataclasses import dataclass
from sqlalchemy import Engine

from logger import Logger
from gpt.speakersManager import SpeakerManager


@dataclass
class Context:
    engine: Engine
    logger: Logger
    manager: SpeakerManager
from aiogram import BaseMiddleware
from aiogram import types
from aiogram.types import Message
from typing import Any, Callable, Awaitable, Dict
from config.general import Config


class ConfigMiddleware(BaseMiddleware):
    def __init__(self, config: Config):
        self.config = config

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        data["config"] = self.config
        return await handler(event, data)
    

from __future__ import annotations
from shared.singleton import SingletonMeta
from shared.types.context import Context
from config.general import Config
from logger import Logger
from db.db import initDB

from telegram.handlers.start import startRouter
from telegram.handlers.composition import compositionRouter
from telegram.handlers.pages import pagesRouter
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from telegram.middleware import ConfigMiddleware
from gpt.speakersManager import SpeakerManager

import pytz
import signal
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from threading import Thread



class Master(metaclass=SingletonMeta):
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

        self.dbEngine = initDB(str(self.config.dsn))
        self.config._context = Context(
            engine=self.dbEngine,
            logger=self.logger,
            manager=SpeakerManager(config.gptToken)
        )
        
        self.bot = Bot(token=self.config.tgToken, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher(storage=MemoryStorage())
        
        configMiddleware = ConfigMiddleware(self.config)
        
        self.dp.message.middleware(configMiddleware)
        self.dp.callback_query.middleware(configMiddleware)
        
        self._initRouters()
        
        self._loop = asyncio.new_event_loop()
        self._loop.set_debug(True)
        
        self._thread = Thread(name="background bot", target=self._background_task, daemon=True)
        self._pollingTask = None
        
        def stopMasterManualy(sig, frame) -> None:
            self.logger.warning("The master forcibly terminates its work")
            self.stop()
        
        if sys.platform == "win32":
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            
        else:
            signal.signal(signal.SIGINT, stopMasterManualy)
            signal.signal(signal.SIGTERM, stopMasterManualy)
    
    def _initRouters(self) -> None:
        self.dp.include_router(startRouter)
        self.dp.include_router(compositionRouter)
        self.dp.include_router(pagesRouter)


    
    def _background_task(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
        
    def start(self) -> None:
        
        if not self._thread.is_alive():
            self._thread.start()
        else:
            self.logger.warning(f"Attempting to restart bot polling")
            
        async def startPolling():
            self.logger.info("Starting bot polling")
            
            await self.bot.delete_webhook(drop_pending_updates=True)
            await self.dp.start_polling(self.bot)
        
        self._pollingTask = asyncio.run_coroutine_threadsafe(startPolling(), loop=self._loop)
    
    def stop(self) -> None:
        if self._thread.is_alive():
            if self._pollingTask:
                self._pollingTask.cancel()
                try:
                    self._pollingTask.result()
                except asyncio.CancelledError:
                    pass
            try:
                self._loop.call_soon_threadsafe(self._loop.stop)
            except asyncio.CancelledError:
                self.logger.info("Bot polling stopped")
                pass
            
        else:
            self.logger.warning(f"Attempting to stop polling before starting")
        
    def __enter__(self) -> Master:
        self.start()
        
        return self
    
    def join(self) -> None:
        self._thread.join()
    
    def __exit__(self, exceptionType: type, exceptionValue: str, exceptionVraceback: str) -> None:
        #Exception handling here
        self.stop()
    
    def __del__(self) -> None:
        # self.stop()
        ...

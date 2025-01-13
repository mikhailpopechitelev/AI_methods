from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
from gpt.speaker import Speaker
from gpt.speakersManager import SpeakerManager

from config.general import Config
from telegram.keyboards.root import mainKeyboard
from telegram.keyboards.back import goBackKeyboard
from telegram.handlers.pages import generate_catalog_page, generate_bookshelf_page

from config.rapid import RAPIDAPI_HOST, RAPIDAPI_KEY

from db.db import Composition , Compositionshelf
from sqlmodel import Session, select
import http.client
import json

startRouter = Router()

@startRouter.message(CommandStart())
async def cmdStart(message: Message, config: Config):
    with Session(config._context.engine) as session:
        session.commit()

    await message.answer(f'Привет, {message.from_user.first_name}', reply_markup=mainKeyboard())


@startRouter.message(F.text == "🔙 Назад")    
async def back(message: Message, config: Config):
    await message.answer("Вы в меню", reply_markup=mainKeyboard())


@startRouter.message(F.text == "📚 Каталог")
async def show_catalog(message: Message, config: Config):
    user = message.from_user
    with Session(config._context.engine) as session:
        return await message.answer(
            "📚 *Каталог музыки:*\nВыберите музыку для подробной информации.",
            reply_markup=generate_catalog_page(page=0, user=user, session=session),  
        )


@startRouter.message(F.text == "🎧 Мой плейлист")
async def open_my_bookshelf(message: Message, config: Config):
    user = message.from_user
    with Session(config._context.engine) as session:
        return await message.answer(
            "🎧 Мой плейлист\nВыберите музыку для подробной информации.",
            reply_markup=generate_bookshelf_page(page=0, user=user, session=session),
        )


@startRouter.message(F.text == "📝 Обсуждения")
async def start_discussion(message: Message, config: Config):
    user = message.from_user.first_name
    await message.answer(f"📝 Что обсудим, {user}?", reply_markup=goBackKeyboard())
    #user_id = message.from_user.id
    #speaker = Speaker(user_id, config)
    #user_sessions[message.from_user.id] = speaker
    
    
@startRouter.message(lambda message: message.text not in ["📝 Обсуждения", "🔙 Назад","🤩 рекомендации"])
async def handle_user_message(message: Message, config: Config):

    user_id = message.from_user.id
    
    speaker = config._context.manager.get_or_create_speaker(user_id)
    response = speaker.send_message(f'\"{message.text}\"')

    await message.answer(response, reply_markup=goBackKeyboard())
    
    
@startRouter.message(F.text == "🤩 рекомендации")
async def handle_user_message(message: Message, config: Config):

    user = message.from_user
    with Session(config._context.engine) as session:
        composition_for_user = session.exec(
            select(Composition)
            .join(Compositionshelf, Composition.id == Compositionshelf.compositionID)
            .where(Compositionshelf.userID == user.id)
        ).all()

    if not composition_for_user:
        return await message.answer(
            "Я пока не знаю, какая музыка вам нравится. Расскажите о ваших предпочтениях, чтобы я мог посоветовать что-то интересное!", reply_markup=goBackKeyboard()
        )
        
    composition_titles = ", ".join(composition.title for composition in composition_for_user)
    
    payload = {
        #"prompt": f"Посоветуй музыку на основе следующих произведений, которые мне понравились: {composition_titles}",
        
        "prompt": "Посоветуй, пожалуйста, музыку, если мне нравится Первый концерт Чайковского. По возможности предоставляя ссылки, и отвечая покороче",
        "system_prompt": "Отвечай только на русском языке. Ты — музыкальный критик, глубоко разбирающийся в музыке разных жанров, эпох и культур. К тебе обращаются пользователи, чтобы получить рецензию или твое личное мнение по поводу той или иной композиции, альбома или исполнителя. Отвечай на поставленные вопросы пользователей. Формат должен быть таким, чтобы он не был слишком длинным и не казался пользователю ответом от машины.Используй четкие и лаконичные формулировки, пиши уверенным, но дружелюбным тоном, добавляя при необходимости немного эмоций, чтобы оживить ответ."
    }

    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST,
        'Content-Type': "application/json"
    }

    json_payload = json.dumps(payload).encode('utf-8')

    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    conn.request("POST", "/llama3", body=json_payload, headers=headers)

    res = conn.getresponse()
    response = res.read().decode('utf-8')
    parsed_response = json.loads(response)
    message_for_user = parsed_response["msg"]
    await message.answer(message_for_user, reply_markup=goBackKeyboard())
 
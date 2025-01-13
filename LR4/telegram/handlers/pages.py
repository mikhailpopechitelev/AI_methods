from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, User, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery


from sqlmodel import Session, select
from sqlalchemy import func
from db.db import Composition, Compositionshelf
from config.general import Config
from telegram.keyboards.root import mainKeyboard

from sqlmodel import Session


ELEMENTS_ON_PAGE = 3


pagesRouter = Router()

@pagesRouter.callback_query(lambda c: c.data and c.data.startswith("catalog_page_"))
async def change_catalog_page(callback_query: CallbackQuery, config: Config):
    page = int(callback_query.data.split("_")[-1])
    user = callback_query.from_user
    
    with Session(config._context.engine) as session:
        await callback_query.message.edit_text(
            "📚 *Ваш плейлист:*\nВыберите музыку для подробной информации.",
            reply_markup=generate_catalog_page(page=page, user=user, session=session)
        )


@pagesRouter.callback_query(lambda c: c.data and c.data.startswith("bookshelf_page_"))
async def change_bookshelf_page(callback_query: CallbackQuery, config: Config):
    page = int(callback_query.data.split("_")[-1])
    user = callback_query.from_user
    
    with Session(config._context.engine) as session:
        await callback_query.message.edit_text(
            "📚 *Ваш плейлист:*\nВыберите музыку для подробной информации.",
            reply_markup=generate_bookshelf_page(page=page, user=user, session=session)
        )




def generate_catalog_page(page: int, user: User, session: Session):
    builder = InlineKeyboardBuilder()

    # Вычисляем границы текущей страницы
    start = page * ELEMENTS_ON_PAGE
    end = start + ELEMENTS_ON_PAGE

    # Получаем книги для текущей страницы
    count = session.exec(
        select(func.count(Composition.id))
    ).one()
    
    compositions_on_page = session.exec(select(Composition).offset(start).limit(ELEMENTS_ON_PAGE)).all()

    # Добавляем кнопки с названиями книг
    for composition in compositions_on_page:
        title = composition.title
        exists = session.exec(
            select(func.count(Compositionshelf.id)).where(
                Compositionshelf.userID == user.id
            ).where(
                Compositionshelf.compositionID == composition.id
            )
        ).one()
        if exists:
            title = "✅ " + composition.title
        
        builder.add(InlineKeyboardButton(text=title, callback_data=f"book_{composition.id}"))

    # Добавляем кнопки навигации (вперед/назад)
    if end < count:  # Если есть следующая страница
        builder.row(InlineKeyboardButton(text="➡ Вперед", callback_data=f"catalog_page_{page + 1}"))
    if start > 0:  # Если это не первая страница
        builder.row(InlineKeyboardButton(text="⬅ Назад", callback_data=f"catalog_page_{page - 1}"))

    return builder.as_markup()



def generate_bookshelf_page(page: int, user: User, session: Session):
    builder = InlineKeyboardBuilder()

    # Вычисляем границы текущей страницы
    start = page * ELEMENTS_ON_PAGE
    end = start + ELEMENTS_ON_PAGE

    # Получаем книги для текущей страницы
    count = session.exec(
        select(func.count(Compositionshelf.id)).where(
            Compositionshelf.userID == user.id
        )
    ).one()
    
    compositions_on_page = session.exec(
        select(Composition).join(
            Compositionshelf,
            Composition.id == Compositionshelf.compositionID
        ).where(
            Compositionshelf.userID == user.id
        ).offset(start).limit(ELEMENTS_ON_PAGE)
    ).all()
    
    for composition in compositions_on_page:
        title = "✅ " + composition.title
        
        builder.add(InlineKeyboardButton(text=title, callback_data=f"book_{composition.id}"))

    # Добавляем кнопки навигации (вперед/назад)
    if end < count:  # Если есть следующая страница
        builder.row(InlineKeyboardButton(text="➡ Вперед", callback_data=f"bookshelf_page_{page + 1}"))
    if start > 0:  # Если это не первая страница
        builder.row(InlineKeyboardButton(text="⬅ Назад", callback_data=f"bookshelf_page_{page - 1}"))

    return builder.as_markup()
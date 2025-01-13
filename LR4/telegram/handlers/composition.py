from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, User
from telegram.keyboards.back import goBackKeyboard, goBackOrShelfKeyboard
from config.general import Config

from sqlmodel import Session, select
from sqlalchemy import func
from db.db import Composition, Compositionshelf


compositionRouter = Router()



def generate_add_to_shelf_button(composition: Composition, user: User, config: Config):
    with Session(config._context.engine) as session:
        exists = session.exec(
            select(func.count(Compositionshelf.id)).where(
                Compositionshelf.userID == user.id
            ).where(
                Compositionshelf.compositionID == composition.id
            )
        ).one()
    
    rows = []
    if exists:
        rows = [
                InlineKeyboardButton(
                    text="Назад", 
                    callback_data=f"goback_from_shelf_{composition.id}"
                ),
                InlineKeyboardButton(
                    text="❌ Убрать из плейлиста", 
                    callback_data=f"remove_from_shelf_{composition.id}"
                )
            ]
    else:
        rows = [
                InlineKeyboardButton(
                    text="➕ Добавить в плейлист", 
                    callback_data=f"add_to_shelf_{composition.id}"
                )
            ]
    
    builder = InlineKeyboardMarkup(
        inline_keyboard=[
            rows
        ]
    )
    return builder

@compositionRouter.callback_query(lambda c: c.data and c.data.startswith("book_"))
async def show_book_details(callback_query: CallbackQuery, config: Config):
    # Извлечение названия книги из callback_data
    compositionId = callback_query.data.split("_", 1)[1]
    user = callback_query.from_user
    
    with Session(config._context.engine) as session:
        composition = session.exec(
            select(
                Composition
            ).where(Composition.id == compositionId)
        ).first()
    
    if composition:
        # Формирование текста с описанием
        composition_info = (
            f"📖 *{composition.title}*\n"
            f"✍ *Автор*: {composition.author}\n"
            f"📅 *Год выпуска*: {composition.year}\n"
            f"📝 *Описание*: {composition.details}\n"

        )


        await callback_query.message.answer(
            composition_info, 
            reply_markup=generate_add_to_shelf_button(composition, user, config),
            parse_mode="Markdown"
        )
    else:
        await callback_query.message.answer("Музыка не найдена.",reply_markup=goBackKeyboard(callback_query.message.from_user.id))

@compositionRouter.callback_query(lambda c: c.data and c.data.startswith("goback_from_shelf_"))
async def remove_from_shelf(callback_query: CallbackQuery, config: Config):
    compositionId = callback_query.data.split("_")[-1]
    user = callback_query.from_user
    
    await callback_query.message.answer(
    f" Вы вернулись назад ", 
    parse_mode="Markdown",
    reply_markup=goBackOrShelfKeyboard())
        
@compositionRouter.callback_query(lambda c: c.data and c.data.startswith("remove_from_shelf_"))
async def remove_from_shelf(callback_query: CallbackQuery, config: Config):
    compositionId = int(callback_query.data.split("_")[-1])  # Получаем ID композиции
    user = callback_query.from_user

    with Session(config._context.engine) as session:
        # Находим запись в Compositionshelf для указанного пользователя и композиции
        composition_on_shelf = session.exec(
            select(Compositionshelf)
            .where(Compositionshelf.compositionID == compositionId)
            .where(Compositionshelf.userID == user.id)
        ).first()

        if composition_on_shelf:
            # Удаляем запись о композиции с полки
            session.delete(composition_on_shelf)
            session.commit()

            # Получаем название композиции для уведомления
            composition = session.exec(
                select(Composition)
                .where(Composition.id == compositionId)
            ).first()
            title = composition.title if composition else "Неизвестная композиция"

            # Логирование и отправка сообщения пользователю
            config._context.logger.debug(
                f"Composition {compositionId} removed from user {user.id}'s Compositionshelf"
            )

            await callback_query.message.answer(
                f"Музыка *{title}* убрана из плейлиста!",
                parse_mode="Markdown",
                reply_markup=goBackOrShelfKeyboard()
            )
        else:
            # Если композиция на полке не найдена
            await callback_query.message.answer(
                "Музыка не найдена в вашем плейлисте.",
                reply_markup=goBackOrShelfKeyboard()
            )


@compositionRouter.callback_query(lambda c: c.data and c.data.startswith("add_to_shelf_"))
async def add_to_shelf(callback_query: CallbackQuery, config: Config):
    сompositionId = callback_query.data.split("_")[-1]
    user = callback_query.from_user
        
    with Session(config._context.engine) as session:
        сomposition = session.exec(
            select(
                Composition
            ).where(Composition.id == сompositionId)
        ).first()
        
        if сomposition is not None:
            print(сomposition)
            compositionOnShelf = session.exec(
                select(Compositionshelf)
                .where(Compositionshelf.userID == user.id)
                .where(Compositionshelf.compositionID == сomposition.id)
            ).first()
            print(compositionOnShelf)
            if compositionOnShelf is not None:
                await callback_query.message.answer(
                    f"📚 Музыка *{сomposition.title}* Уже добавлена в плейлист!",
                    parse_mode="Markdown",
                    reply_markup=goBackOrShelfKeyboard()
                )
                return
            
            session.add(
                Compositionshelf(
                    userID=user.id,
                    compositionID=сomposition.id,
                    score=0
                )
            )
            session.commit()
            await callback_query.message.answer(
                f"📚 Музыка *{сomposition.title}* добавлена на полку! ✅", 
                parse_mode="Markdown",
                reply_markup=goBackOrShelfKeyboard()
            )
            
        else:
            await callback_query.message.answer(
                "Книга не найдена.",
                reply_markup=goBackKeyboard()
            )

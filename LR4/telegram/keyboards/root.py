from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def mainKeyboard():

    buttons = [
        [KeyboardButton(text="🎧 Мой плейлист"), KeyboardButton(text="📝 Обсуждения")],
        [KeyboardButton(text="📚 Каталог"), KeyboardButton(text="🤩 рекомендации")]
    ]
        
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True, 
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню:"
    )
    return keyboard
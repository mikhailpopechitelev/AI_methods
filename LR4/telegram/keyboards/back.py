from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def goBackKeyboard():
    buttons = [
        [KeyboardButton(text="🔙 Назад")]
    ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True, 
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню:"
    
    )
    return keyboard


def goBackOrShelfKeyboard():
    buttons = [
        [KeyboardButton(text="🔙 Назад")],
        [KeyboardButton(text="🎧 Мой плейлист")]
    ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True, 
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню:"
    
    )
    return keyboard
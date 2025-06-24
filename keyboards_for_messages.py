from ast import Continue
from telebot import types

# Кнопки под сообщение Да/Нет
yes_no_keyboard = types.InlineKeyboardMarkup()
yes_no_keyboard.add(
    types.InlineKeyboardButton(text="Да", callback_data="yes"),
    types.InlineKeyboardButton(text="Нет", callback_data="no")
)
continue_keyboard = types.InlineKeyboardMarkup()
continue_keyboard.add(
    types.InlineKeyboardButton(text="Посмотреть послностью", callback_data="continue"),
)






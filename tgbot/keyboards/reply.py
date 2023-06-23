from aiogram import types

kbd = types.ReplyKeyboardMarkup(keyboard=[
    [types.KeyboardButton(text="🎲"), types.KeyboardButton(text="/анекдот")],
    [types.KeyboardButton(text="/нагадування"), types.KeyboardButton(text="/перекладач")],
    [types.KeyboardButton(text="/втрати"), types.KeyboardButton(text="/валюта")]
], resize_keyboard=True)
kbd2 = types.ReplyKeyboardMarkup(keyboard=[
    [types.KeyboardButton(text="/stop")]
], resize_keyboard=True)

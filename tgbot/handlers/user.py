import asyncio
import json
import random
import re
from datetime import datetime

import aiohttp
import requests as requests
from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from googletrans import Translator

from tgbot.keyboards.reply import kbd, kbd2
from tgbot.misc.parser import parse_jokes
from tgbot.misc.states import MyForm

scores_good = {}
scores_bad = {}
scores_neu = {}


async def start1233(message: types.Message):
    await message.reply(
        "Привіт! Я твій універсальний телеграм-бот Romn! Зараз я готов розважити тебе анекдотами, показати актуальний курс валют на сьогодні, допомогти встановити нагадування, перекладати слова англійською та навіть грати в кубик. Просто вибери те що тобі потрібно на клавіатурі або вибери команди нижче: \n/anek - рандомний анекдот \n/vtratu - дізнатися втрати росіян на сьогодні \n/setrem - встановити нагадування на день-місяць-рік години:хвилини \n🎲 - зіграти з ботом у кубик. Виграє той у кого число більше ніж у супротивника \n/trans - перевести слова",
        reply_markup=kbd)
    await message.answer(
        "Вибач якщо я підлагую або видаю тобі неправильні команди! Я стараюся на свій максимум на який мене запра")

    user_id = message.from_user.id
    scores_good[user_id] = 0
    scores_bad[user_id] = 0
    scores_neu[user_id] = 0


############################################################################################################################

############################################################################################################################

async def send_joke(message: types.Message):
    jokes = await (parse_jokes())
    jokes_max = len(jokes)
    if jokes:
        joke = random.randint(0, jokes_max)
        text_only = re.sub(r'<h4>(.*?)</h4>', '', jokes[joke])
        await message.answer(text_only)
    else:
        await message.answer("Не вдалося знайти анекдоти")


############################################################################################################################


############################################################################################################################

async def vtra(message: types.Message):
    url = "https://russianwarship.rip/api/v2/statistics/latest"  # підключення до сайта
    response = requests.get(url)
    data = response.json()
    await message.reply(
        f"На сьогоднішній день({data['data']['date']}) втрати ворога такі:\nГарних руськіх = {data['data']['stats']['personnel_units']}\nТанків = {data['data']['stats']['tanks']}\nАртилерія = {data['data']['stats']['artillery_systems']}\nМЛРС = {data['data']['stats']['mlrs']}\nЛітачків = {data['data']['stats']['planes']}")
    # Тут можна доробити щоб показувало прям все-все
    await asyncio.sleep(2)


############################################################################################################################

############################################################################################################################


async def start_rem(message: types.Message):
    await message.reply(
        "Встановлювання нагадування ввімкнено. Надішліть мені дату у вигляді ДД.ММ.РР ГГ:ХХ . Залишити можна коли відправиш /stop",
        reply_markup=kbd2)
    await MyForm.reminder_datetime.set()

async def stop_rem(message: types.Message, state:FSMContext):
    await message.reply("Встановлювання нагадувань вимкнено.", reply_markup=kbd)
    await state.finish()

async def process_reminder_datetime(message: types.Message, state: FSMContext):
    reminder_datetime = message.text
    try:
        reminder_date, reminder_time = reminder_datetime.split(' ')
        datetime.strptime(reminder_date, '%d.%m.%Y')
        datetime.strptime(reminder_time, '%H:%M')
    except ValueError:
        await message.reply('Невірний формат дати або часу. Будь ласка, введіть у форматі ДД.ММ.РРРР ГГ:ХХ')
        return
    await message.reply('Нагадування встановлено. Я нагадаю вам у вказаний час.')
    await asyncio.sleep(get_seconds_until_reminder(reminder_datetime))
    await message.answer(f'Нагадування! Зараз {reminder_datetime}.')


def get_seconds_until_reminder(reminder_datetime):
    reminder_date, reminder_time = reminder_datetime.split(' ')
    reminder_datetime = datetime.strptime(reminder_date + ' ' + reminder_time, '%d.%m.%Y %H:%M')
    current_datetime = datetime.now()
    seconds_until_reminder = (reminder_datetime - current_datetime).total_seconds()
    return seconds_until_reminder


# Да
############################################################################################################################

############################################################################################################################
# Гра кубик, все розбирали

async def roll_dice(message: types.Message):

    user_id = message.from_user.id
    if user_id not in scores_good:
        scores_good[user_id] = 0
        scores_bad[user_id] = 0
        scores_neu[user_id] = 0

    await asyncio.sleep(4)
    user_id = message.from_user.id
    answer = await message.answer_dice("🎲")
    await asyncio.sleep(4)
    pl_score = message.dice.value
    bot_score = answer.dice.value
    if pl_score < bot_score:
        dice_bad = 1
        await message.answer("Ти програв")
        scores_bad[user_id] += dice_bad
        await message.answer(
            f"Ти переміг бота вже {scores_good[user_id]} разів \nПрограв боту {scores_bad[user_id]} разів \nНічия була {scores_neu[user_id]} разів")
    elif pl_score > bot_score:
        dice_good = 1
        await message.answer("Ти виграв")
        scores_good[user_id] += dice_good
        await message.answer(
            f"Ти переміг бота вже {scores_good[user_id]} разів \nПрограв боту {scores_bad[user_id]} разів \nНічия була {scores_neu[user_id]} разів")
    else:
        dice_neu = 1
        await message.answer("Нічия")
        scores_neu[user_id] += dice_neu
        await message.answer(
            f"Ти переміг бота вже {scores_good[user_id]} разів \nПрограв боту {scores_bad[user_id]} разів \nНічия була {scores_neu[user_id]} разів")


############################################################################################################################

############################################################################################################################
# Валюта, можна ще добавити калькулятор
async def valuta(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5') as response:
            rates = await response.json()
    date = datetime.now().strftime('%d.%m.%Y %H:%M')
    for rate in rates:
        await message.answer(
            f"Сьогодні {date} курс {rate.get('ccy')} / {rate.get('base_ccy')} становить: \nПродати - {rate.get('buy')}\nКупити - {rate.get('sale')} ")


############################################################################################################################

############################################################################################################################
translator = Translator()



async def start_translation(message: types.Message):
    await message.reply("Переклад увімкнено. Надішліть мені слова для перекладу. Залишити можна коли напишеш /stop",
                        reply_markup=kbd2)
    await MyForm.translator.set()


async def stop_translation(message: types.Message, state:FSMContext):
    await message.reply("Переклад вимкнено.", reply_markup=kbd)
    await state.finish()

async def translate_words(message: types.Message):
    translation = translator.translate(message.text, dest="en")
    await message.reply(f"Переклад:\n{translation.text}")


############################################################################################################################

def register_user(dp: Dispatcher):
    dp.register_message_handler(start1233, commands=['start', "старт", "help"])
    dp.register_message_handler(send_joke, commands=['anek', "анекдот"])
    dp.register_message_handler(vtra, commands=["vtratu", "втрати"])
    dp.register_message_handler(start_rem, commands=['setrem', "нагадування"])
    dp.register_message_handler(stop_rem, commands=['stop'], state=MyForm.reminder_datetime)
    dp.register_message_handler(process_reminder_datetime, state=MyForm.reminder_datetime)
    dp.register_message_handler(roll_dice, content_types=types.ContentTypes.DICE)
    dp.register_message_handler(valuta, commands=['valuta', "валюта"])
    dp.register_message_handler(start_translation, commands=['trans', "перекладач"])
    dp.register_message_handler(stop_translation, commands=['stop'], state=MyForm.translator)
    dp.register_message_handler(translate_words, state=MyForm.translator)

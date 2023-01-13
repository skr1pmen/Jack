import asyncio
import os
import requests
import re
import aioschedule
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import tracemalloc

from database import Database
import group as groups

tracemalloc.start()
load_dotenv()

bot = Bot(token=os.getenv('token'))
# bot = Bot(token=os.getenv('testToken'))
dp = Dispatcher(bot)
db = Database('jack.db')


async def parsing(group):
    url = f"{os.getenv('url')}{group}"

    headers = {
        "Accept": os.getenv("accept"),
        "User-Agent": os.getenv("useragent")
    }

    try:
        req = requests.get(url, headers=headers)
        src = req.text

        with open("schedule.html", "w", encoding='utf-8') as file:
            file.write(src)
    except:
        print(f"Код: {group}. Не доступен!")

    with open("schedule.html", encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    scd = []
    i = 1
    for number in soup.find_all('td', class_="thead"):
        finish = re.sub(r'[\n\n|—\n]', '', number.get_text())
        if i == 1 or i == 9:
            scd.append([f"<b>{finish.strip()}</b>:•"])
            i += 1
        else:
            scd.append([f"<b>{finish.strip()}</b>:"])
            i += 1

    i = 1
    for item in soup.find_all('td', class_="td-bold"):
        finish = re.sub(r'[\n\n|—\n]', '', item.get_text())
        if i % 8 == 0:
            i += 1
        if finish.strip() == "":
            scd[i].append(f"нет пары•")
        else:
            scd[i].append(f"{finish.strip()}•")
        i += 1
    schedule = str(scd)
    db.new_schedule(schedule, group)


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    if not db.chat_exists(msg.chat.id):
        db.add_chat(msg.chat.id, msg.from_user.first_name, False)

    welcome_message = f'Привет, {msg.from_user.first_name}! Я Джек, помощник в отслеживании изменений в расписании.'\
                      f' Если ты хочешь чтобы я отправлял тебе расписание твоей группы, то укажи пожалуйста для начала'\
                      f' её название.\n <i>Пример: МК-22</i>'
    sticker_hi = 'CAACAgIAAxkBAAEFxFRjFnKx2k7rTEcWbXsJu0z5xlTMUwACiBEAArOMcUnCJQLlwkLsoikE'

    await msg.answer_sticker(sticker_hi)
    await msg.answer(welcome_message, parse_mode='html')


@dp.message_handler(commands=['message'])
async def message(msg: types.Message):
    if msg.from_user.id == 729497930:
        for user in db.all_chats():
            message = msg.text[9:]
            try:
                text = message.replace("{name}", f"{user[1]}").replace('{bot}', '@srmk_bot').replace('{i}', '@skr1pmen')
                await bot.send_message(user[0], text, parse_mode='html')
            except:
                pass


def keyboards():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    website = types.KeyboardButton('Сайт 🌐')
    reload = types.KeyboardButton('Расписание 📅')
    bell = types.KeyboardButton('Звонки 🔔')
    help = types.KeyboardButton('Помощь 📞')
    settings = types.KeyboardButton('Настройки ⚙')
    return markup.add(website, reload, bell, help, settings)


@dp.message_handler()
async def user_text(msg: types.Message):
    try:
        if db.group_exists(msg.chat.id) == 0:
            group = msg.text.lower()
            for name, code in groups.group.items():
                if name == group:
                    db.add_group(msg.chat.id, code)
                    await msg.answer("Хорошо, теперь ты будешь получать расписание этой группы.", parse_mode='html', reply_markup=keyboards())
        else:
            if msg.text.lower() == "сайт 🌐":
                markup = InlineKeyboardMarkup()
                url = f'{os.getenv("url")}{db.group_exists(msg.chat.id)}'
                markup.add(InlineKeyboardButton("Перейти", url=url))
                await msg.answer("Для перехода на страницу с рассписанием нажмите на кнопку ниже.", parse_mode='html',
                                 reply_markup=markup)
            elif msg.text.lower() == "расписание 📅":
                group = db.get_group(msg.chat.id)
                list = db.schedule_print(group)
                schedule = re.sub(r'[\[\'\],]', '', list).replace("•", "\n")

                await msg.answer("Рассписание занятий на данный момент:\n\n" + schedule, parse_mode='html')
            elif msg.text.lower() == "звонки 🔔":
                with open("schedule_bell.txt", encoding='utf-8') as file:
                    raw_list = file.read()
                    list = re.sub(r'[\[\'\],]', '', raw_list).replace("•", "\n")
                await msg.answer("Рассписание звонков:\n\n" + list, parse_mode='html')
            elif msg.text.lower() == "помощь 📞":
                await msg.answer("В случае возникновения каких либо вопросов/ошибок обращайтесь к @skr1pmen. "
                                 "В начале сообщения указал #JackBot")
            elif msg.text.lower() == "настройки ⚙":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                group = types.KeyboardButton('Изменить группу 📔')
                back = types.KeyboardButton('Назад ◀')
                if msg.from_user.id == 729497930:
                    if db.get_mailing() == 1:
                        mailing = types.KeyboardButton('Отключить рассылку 📮')
                        markup.add(group, mailing, back)
                    else:
                        mailing = types.KeyboardButton('Включить рассылку 📮')
                        markup.add(group, mailing, back)
                else:
                    markup.add(group, back)
                await msg.answer("<b>Доступные настройки:</b>\n•Изменить группу", parse_mode='html', reply_markup=markup)
            elif msg.text.lower() == "изменить группу 📔":
                await msg.answer("Введи, пожалуйста, название группы, чтобы её изменить.\n<i>Пример: МК-22</i>", parse_mode='html')
                db.edit_group(msg.chat.id)
            elif msg.text.lower() == "отключить рассылку 📮":
                await msg.answer("Рассылка отключена!", parse_mode='html', reply_markup=keyboards())
                db.deactivate_mailing()
            elif msg.text.lower() == "включить рассылку 📮":
                await msg.answer("Рассылка включена!", parse_mode='html', reply_markup=keyboards())
                db.activate_mailing()
            elif msg.text.lower() == "назад ◀":
                await msg.answer("Возвращаю в меню", parse_mode='html', reply_markup=keyboards())
            else:
                await msg.answer("Прости, но я тебя не понимаю 😞", parse_mode='html')
    except:
        pass


@dp.message_handler()
async def NewSchedule():
    if db.get_mailing() == 1:
        for group in groups.group.values():
            db.record_old_schedule(group)
            await asyncio.sleep(0.05)
            await parsing(group)

            try:
                if db.schedule(group):
                    chats = db.get_chats(group)
                    list = db.schedule_print(group)
                    schedule = re.sub(r'[\[\'\],]', '', list).replace("•", "\n")
                    try:
                        await bot.send_message(chats, "На сайте обновили расписание:\n\n" + schedule, parse_mode='html')
                    except:
                        pass
            except:
                pass


async def schedule():
    aioschedule.every(60).seconds.do(NewSchedule)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(schedule())
    print("Jack запущен!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

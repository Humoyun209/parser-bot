import asyncio
import logging
from environs import Env

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.filters import Command
from database import DataBase
from parsers import FunBay


env = Env()
env.read_env()


bot = Bot(token=env.str("TOKEN"), parse_mode="HTML")
dp = Dispatcher()
db = DataBase("db.sqlite3")
fb = FunBay("https://funpay.com/lots/545/", "data/index.html", "data/lots.json")


logging.basicConfig(
    level=logging.INFO, format="%(levelname)s - [%(asctime)s] - %(name)s - %(message)s"
)


@dp.message(Command(commands=["start"]))
async def process_start(message: Message):
    await fb.get_html_page()
    await fb.parse_data_to_json()
    new_lots = await db.insert_new_lots()
    len_new_lots = len(new_lots)
    if len_new_lots == 0:
        await message.answer("Новые лоты не найдены")
    else:
        for i, lot in enumerate(new_lots):
            if (i + 1) % 10 == 0:
                await asyncio.sleep(10)
            await bot.send_message(
                env.str("CHANNEL_URL"),
                f'\n✅ Новый лот!\n{lot.description}\n💰 <b>Цена:</b> {lot.price}\n<b>Посмотреть на сайте:</b> ‼️<a href="{lot.url}">Перейти</a>‼️',
            )


@dp.message(Command(commands=["admin"]))
async def process_admin(message: Message):
    delete_month_back = InlineKeyboardButton(
        text="❌ Удалить лоты", callback_data="delete:month"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[delete_month_back]])
    await message.answer(
        "Вы можете удалить все лоты, созданные месяц назад: ", reply_markup=kb
    )


@dp.callback_query(F.data == "delete:month")
async def delete_lots(cb: CallbackQuery):
    await db.delete_old_lots()
    await cb.message.answer("Все лоты, созданные неделья назад, удалены ✅")
    await cb.message.delete()


@dp.message()
async def get_echo(message: Message):
    await message.answer("Бот ничего не понимает")


if __name__ == "__main__":
    dp.run_polling(bot)

import logging 
from environs import Env

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from database import DataBase
from parsers import FunBay


env = Env()
env.read_env()


bot = Bot(token=env.str('TOKEN'))
dp = Dispatcher()
db = DataBase('db.sqlite3')
fb = FunBay('https://funpay.com/lots/545/', 'data/index.html', 'data/lots.json')


logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - [%(asctime)s] - %(name)s - %(message)s'
)


@dp.message(Command(commands=['start']))
async def process_start(message: Message):
    fb.get_html_page()
    fb.parse_data_to_json()
    new_lots = db.insert_lots()
    if len(new_lots) == 0:
        await message.answer('Новые лоты не найдено')
    else:
        for lot in new_lots:
            await message.answer(f'\n✅ Новый лот!\n{lot.get("description")}\n💰 Цена: {lot.get("price")}\n{lot.get("url")}')


@dp.message()
async def get_echo(message: Message):
    await message.answer('Бот ничего не понимает')
            

if __name__ == '__main__':
    dp.run_polling(bot)
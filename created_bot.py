from dotenv import load_dotenv, find_dotenv
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import os
from aiogram.contrib.fsm_storage.redis import RedisStorage2

storage = RedisStorage2()

load_dotenv(find_dotenv())
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)

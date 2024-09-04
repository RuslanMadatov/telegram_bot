from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from created_bot import bot
from data_baze import baze_bd, redis_db
from keyboards import admin_keyboard
from handlers import admin


class Price_FSMAdmin(StatesGroup):
    new_price = State()
    name = State()


# ф-ция, запускающая класс
async def names_prices(message: types.Message):
    if message.from_user.id == admin.ID:
        await Price_FSMAdmin.new_price.set()
        await message.answer('Введите новую цену продукта')


async def save_update_prices(message: types.Message,
                             state: FSMContext):  # ф-ция ловит ответ и дает имена продуктов для копирования
    if message.from_user.id == admin.ID:
        await redis_db.set_price(message.text)
        await Price_FSMAdmin.next()
        await message.answer('Скопируйте  название изменяемого продукта')
        read = [names_menu[0] for names_menu in await baze_bd.call_name_menu()]
        for i in read:
            await message.answer(i)


async def save_new_prices(message: types.Message,
                          state: FSMContext):  # ф-ция ловит ответ и завершает процесс изменения
    if message.from_user.id == admin.ID:
        await redis_db.set_name(message.text)
        await redis_db.load_new_prices()
        await bot.send_message(message.from_user.id, 'Изменение цены прошло успешно',
                               reply_markup=admin_keyboard.button_case_admin)
        await redis_db.delit()
        await state.finish()


def new_prices_register(dp: Dispatcher):
    dp.register_message_handler(names_prices, (lambda message: message.text == 'Цена'), state=None)
    dp.register_message_handler(save_update_prices, state=Price_FSMAdmin.new_price)
    dp.register_message_handler(save_new_prices, state=Price_FSMAdmin.name)

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from created_bot import bot
from aiogram import types, Dispatcher
from data_baze import baze_bd, redis_db
from keyboards import admin_keyboard
from handlers import admin

class Total_quantity_FSMAdmin(StatesGroup):
    new_total_quantity = State()
    name = State()


async def names_total_quantity(message: types.Message):
    if message.from_user.id == admin.ID:
        await Total_quantity_FSMAdmin.new_total_quantity.set()
        await message.answer('Введите новое количество  продукта')

async def save_update_total_quantity(message: types.Message, state: FSMContext):
    if message.from_user.id == admin.ID:
        await redis_db.set_total_quantity(message.text)
        await Total_quantity_FSMAdmin.next()
        await message.answer('Скопируйте название изменяемого продукта')
        read = [names_menu[0] for names_menu in await baze_bd.call_name_menu()]
        for i in read:
            await message.answer(i)

async def save_new_total_quantity(message: types.Message, state: FSMContext):
    if message.from_user.id == admin.ID:
        await redis_db.set_name(message.text)
        await redis_db.load_new_total_quantity()
        await bot.send_message(message.from_user.id, 'Изменение количества продукта прошло успешно',
                               reply_markup=admin_keyboard.button_case_admin)
        await redis_db.delit()
        await state.finish()

def new_total_quantity_register(dp: Dispatcher):
    dp.register_message_handler(names_total_quantity, (lambda message: message.text == 'Колличество продукта'), state=None)
    dp.register_message_handler(save_update_total_quantity, state=Total_quantity_FSMAdmin.new_total_quantity)
    dp.register_message_handler(save_new_total_quantity, state=Total_quantity_FSMAdmin.name)
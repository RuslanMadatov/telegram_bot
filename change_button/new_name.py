from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from created_bot import bot
from aiogram import types, Dispatcher
from data_baze import baze_bd, redis_db
from keyboards import admin_keyboard
from handlers import admin


class Name_FSMAdmin(StatesGroup):
    new_names = State()
    name = State()


# ф-ция, запускающая класс
async def names_names(message: types.Message):
    if message.from_user.id == admin.ID:
        await Name_FSMAdmin.new_names.set()
        await message.answer('Напишите новое название продукта')


# ф-ция для сохранения нового названия продукта
async def save_update_name(message: types.Message, state: FSMContext):
    if message.from_user.id == admin.ID:
        await redis_db.set_name_new(message.text)
        await Name_FSMAdmin.next()
        await message.answer('Скопируйте название изменяемого продукта')
        read = [names_menu[0] for names_menu in await baze_bd.call_name_menu()]
        for i in read:
            await message.answer(i)


# ф-ция ловит ответ и завершает процесс изменения
async def save_new_name(message: types.Message, state: FSMContext):
    if message.from_user.id == admin.ID:
        await redis_db.set_name(message.text)
        if await redis_db.load_new_names() == False:
            await bot.send_message(message.from_user.id,
                                   'Продукт с таким названием уже существует, нужно изменить название')
        else:
            await bot.send_message(message.from_user.id, 'Изменение названия прошло успешно',
                                   reply_markup=admin_keyboard.button_case_admin)
        await redis_db.delit()
        await state.finish()


def new_names_register(dp: Dispatcher):
    dp.register_message_handler(names_names, (lambda message: message.text == 'Название продукта'), state=None)
    dp.register_message_handler(save_update_name, state=Name_FSMAdmin.new_names)
    dp.register_message_handler(save_new_name, state=Name_FSMAdmin.name)

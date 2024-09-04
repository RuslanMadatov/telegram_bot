from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from created_bot import bot
from data_baze import baze_bd, redis_db
from keyboards import admin_keyboard
from handlers import admin


class Discription_FSMAdmin(StatesGroup):
    new_discription = State()
    name = State()


async def names_discriptions(message: types.Message):  # ф-ция, запускающая класс
    if message.from_user.id == admin.ID:
        await Discription_FSMAdmin.new_discription.set()
        await message.answer('Введите изменение в состав изменяемого продукта')


# ф-ция ловит ответ и дает имена продуктов для копирования
async def save_update_discriptions(message: types.Message,
                                   state: FSMContext):
    if message.from_user.id == admin.ID:
        await redis_db.set_discription(message.text)
        await Discription_FSMAdmin.next()
        await message.answer('Скопируйте  название изменяемого продукта')
        read = [names_menu[0] for names_menu in await baze_bd.call_name_menu()]
        for i in read:
            await message.answer(i)

# ф-ция ловит ответ и завершает процесс изменения
async def save_new_discription(message: types.Message,
                               state: FSMContext):
    if message.from_user.id == admin.ID:
        await redis_db.set_name(message.text)
        await redis_db.load_new_discriptions()
        await bot.send_message(message.from_user.id, 'Изменение состава прошло успешно',
                               reply_markup=admin_keyboard.button_case_admin)
        await redis_db.delit()
        await state.finish()


def new_discriptions_register(dp: Dispatcher):
    dp.register_message_handler(names_discriptions, (lambda message: message.text == 'Состав продукта'), state=None)
    dp.register_message_handler(save_update_discriptions, state=Discription_FSMAdmin.new_discription)
    dp.register_message_handler(save_new_discription, state=Discription_FSMAdmin.name)

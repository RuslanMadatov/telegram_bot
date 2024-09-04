from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from created_bot import bot
from data_baze import baze_bd, redis_db
from keyboards import admin_keyboard
from handlers import admin


class Photo_FSMAdmin(StatesGroup):
    new_photos = State()
    name = State()


# ф-ция, запускающая класс
async def names_photos(message: types.Message):
    if message.from_user.id == admin.ID:
        await Photo_FSMAdmin.new_photos.set()
        await message.answer('Загрузите новое фото')

# ф-ция для сохранения нового фото продукта
async def save_update_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == admin.ID:
        await redis_db.set_photo(message.photo[0].file_id)
        await Photo_FSMAdmin.next()
        await message.answer('Скопируйте название изменяемого продукта')
        read = [names_menu[0] for names_menu in await baze_bd.call_name_menu()]
        for i in read:
            await message.answer(i)

# ф-ция ловит ответ и завершает процесс изменения
async def save_new_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == admin.ID:
        await redis_db.set_name(message.text)
        await redis_db.load_new_photos()
        await bot.send_message(message.from_user.id, 'Изменение изображения прошло успешно',
                               reply_markup=admin_keyboard.button_case_admin)
        await redis_db.delit()
        await state.finish()


def new_photo_register(dp: Dispatcher):
    dp.register_message_handler(names_photos, (lambda message: message.text == 'Изображение продукта'), state=None)
    dp.register_message_handler(save_update_photo, content_types=['photo'], state=Photo_FSMAdmin.new_photos)
    dp.register_message_handler(save_new_photo, state=Photo_FSMAdmin.name)

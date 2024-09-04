from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from created_bot import bot
from aiogram.dispatcher.filters import Text
from data_baze import baze_bd, redis_db
from keyboards import admin_keyboard, client_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ID = None


class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    discription = State()
    price = State()
    total_quantity = State()


# Проверка на администратора, нужно писать в группу
# @dp.message_handler(commands=['moderator'], is_chat_admin=True)
async def make_chat_commands(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Здравствуйте, Администратор',
                           reply_markup=admin_keyboard.button_case_admin)
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    adminId = []
    for admins in chat_admins:
        adminId.append(str(admins.user.id))
    await baze_bd.insert_in_admin(adminId)


# Начало диалога загрузки нового пункта меню
# @dp.message_handler(commands='Загрузить', state=None)
async def cm_start(message: types.Message):
    if message.from_user.id == ID:
        await FSMAdmin.photo.set()
        await message.reply('Загрузите фото')


# @dp.message_handler(state='*', comands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await redis_db.delit()
        await state.finish()
        await message.reply('OK', reply_markup=admin_keyboard.button_case_admin)


# Получаем первый ответ и записываем его в redis
# @dp.message_handler(content_types=['photo'], state=FSMAdmin.photo)
async def load_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        await redis_db.set_photo(message.photo[0].file_id)
        await FSMAdmin.next()
        await message.reply('Введите название продукта')


# Получаем второй ответ
# @dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        await redis_db.set_name(message.text)
        await FSMAdmin.next()
        await message.reply('Введите состав продукта')


# Получаем третий ответ
# @dp.message_handler(state=FSMAdmin.discription)
async def load_discription(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        await redis_db.set_discription(message.text)
        await FSMAdmin.next()
        await message.reply('Укажите стоимость продукта')


# Получаем четвертый ответ
# @dp.message_handler(state=FSMAdmin.price)
async def load_price(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        await redis_db.set_price(message.text)
        await FSMAdmin.next()
        await message.reply('Укажите число имеющегося продукта')

# Получаем пятый ответ ответ и используем полученые данные
async def load_total_product_quantity(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        await redis_db.set_total_quantity(message.text)
        if await redis_db.load() == False:
            await message.answer('Продукт с таким названием уже существует, нужно изменить название')
        else:
            await message.answer('Загрузка нового продукта прошла успешно')
        await redis_db.delit()
        await state.finish()


# кэлбэк при удалении
async def del_callback_run(callbak_query: types.CallbackQuery):
    await baze_bd.sql_delete_command(callbak_query.data.replace('del ', ''))
    await redis_db.del_total_quantity(callbak_query.data.replace('del ', ''))
    #await callbak_query.answer(text=f'{callbak_query.data.replace("del ", "")} удалена.', show_alert=True)
    await bot.answer_callback_query(callbak_query.id, text=f'{callbak_query.data.replace("del ", "")} удалена.')
    await callbak_query.message.delete_reply_markup()


# @dp.message_handler(commands='Удалить')
async def delete_item(message: types.Message):
    if message.from_user.id == ID:
        read = await baze_bd.sql_read_admin()
        for ret in read:
            await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nСостав продукта: {ret[2]}\nЦена: {ret[3]}',
                                 reply_markup=InlineKeyboardMarkup().add(
                                     InlineKeyboardButton(f'Удалить {ret[1]}', callback_data=f'del {ret[1]}')))
            '''await bot.send_message(message.from_user.id, text='^^^^',
                                   reply_markup=InlineKeyboardMarkup().add(
                                       InlineKeyboardButton(f'Удалить {ret[1]}', callback_data=f'del {ret[1]}')))'''


# ф-ция для кнопки изменить
async def to_change(message: types.Message):
    if message.from_user.id == ID:
        await bot.send_message(message.from_user.id, text='Что хотите изменить?', reply_markup=admin_keyboard.kb_choice)


#  ф-ция для кнопки "назад"
async def button_back(message: types.Message):
    if message.from_user.id == ID:
        await bot.send_message(message.from_user.id, 'Вы вернулись в меню',
                               reply_markup=admin_keyboard.button_case_admin)
    else:
        await bot.send_message(message.from_user.id, 'Вы вернулись в меню',
                               reply_markup=client_keyboard.client_kbs)


def admin_hendler(dp: Dispatcher):
    dp.register_message_handler(make_chat_commands, commands=['moderator'], is_chat_admin=True)
    dp.register_message_handler(cm_start, (lambda message: message.text == 'Загрузить новый продукт'), state=None)
    dp.register_message_handler(cancel_handler, state='*', commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin.photo)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_message_handler(load_discription, state=FSMAdmin.discription)
    dp.register_message_handler(load_price, state=FSMAdmin.price)
    dp.register_message_handler(load_total_product_quantity, state=FSMAdmin.total_quantity)
    dp.register_message_handler(delete_item, (lambda message: message.text == 'Удалить'))
    dp.register_callback_query_handler(del_callback_run, lambda x: x.data and x.data.startswith('del '))
    dp.register_message_handler(to_change, (lambda message: message.text == 'Изменить продукт'))
    dp.register_message_handler(button_back, (lambda message: message.text == 'Назад 🔙'))

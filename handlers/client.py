from aiogram import types, Dispatcher
from created_bot import dp, bot
from keyboards import client_keyboard
from data_baze import baze_bd, redis_db
from aiogram.dispatcher.filters import Text


# @dp.message_handler(commands=['start', 'help'])  # клиентская часть
async def comands_start_help(message: types.Message):
    try:  # обработка ошибки, если не добавлен в группу
        await bot.send_message(message.from_user.id, 'Здравствуйте',
                               reply_markup=client_keyboard.client_kbs)  # ввод клавы
        await message.delete()
    except:
        await message.reply('Общение с ботом через ЛС, напишите ему: r\http//t.me/PraynikBot')


# @dp.message_handler(commands=['Режим_работы'])
async def operating_mode(message: types.Message):
    await bot.send_message(message.from_user.id, 'Пн - Пт с 08:00 до 17:00')


# @dp.message_handler(commands=['Расположение'])
async def location(message: types.Message):
    # await bot.send_message(message.from_user.id, 'ул. Есенина, 22')
    await message.answer(text='Нажмите, чтобы узнать расположение', reply_markup=client_keyboard.client_kbs_inline)


# выдаёт меню клиенту
async def praynik_menu(message: types.Message):
    await baze_bd.sql_read_client(message, message.from_user.id)
    # await baze_bd.user_exists(message.from_user.id)


# ф-ция получает ответ от инлайн-клавиатуры при нажатии +1, -1, Потвердить
# @dp.callback_query_handler(Text(startswith="num_"))
async def callbacks_num(call: types.CallbackQuery):
    # Распарсиваем callback инлайн клавиатуры
    action = call.data.split("_")
    id_name = str(action[2]) + '_' + str(action[3])
    user_values = int(await redis_db.get_redis_user_value(id_name))
    # Парсим строку и извлекаем действие, например `num_incr` -> `incr`
    if action[1] == "incr":
        user_value = user_values + 1
        await redis_db.redis_user_value(id_name, user_value)
        # Проверка сколько берет покупатель и сколько на складе товара в данный момент времени
        if int(await redis_db.get_redis_user_value(id_name)) > int(
                await redis_db.get_total_quantity(action[3])):
            await bot.answer_callback_query(call.id, text='К сожалению, такого количества продукта нет')
            user_value = int(await redis_db.get_total_quantity(action[3]))
            await redis_db.redis_user_value(id_name, user_value)
        else:
            await bot.answer_callback_query(call.id, text=str(await redis_db.get_redis_user_value(id_name)))
    elif action[1] == "decr":
        user_value = user_values - 1
        if int(user_value) == -1:
            user_value = 0
        await redis_db.redis_user_value(id_name, user_value)
        await bot.answer_callback_query(call.id, text=str(await redis_db.get_redis_user_value(id_name)))
    elif action[1] == "finish":
        quantity_of_goods = int(await redis_db.get_redis_user_value(id_name))
        if quantity_of_goods == 0:
            await bot.answer_callback_query(call.id, text='Ноль товар нельзя добавить в корзину')
        else:
            user_id = id_name.split('_')[0]
            name_product = id_name.split('_')[1]
            price = float(await baze_bd.price_product(name_product))
            total_product_price = price * quantity_of_goods
            # Проверка сущетсвует ли товар в корзине
            if await baze_bd.insert_in_basket(user_id, name_product, price, quantity_of_goods,
                                              total_product_price) == False:
                await bot.answer_callback_query(call.id, text="Этот товар уже в корзине")
            else:
                await bot.answer_callback_query(call.id, text='Товар добавлен в корзину')
            await call.message.delete_reply_markup()
        await call.answer()


#  ф-ция для кнопки корзина и выдает клавиатуру для корзины, что в ней находится и подитог
async def in_basket(message: types.Message):
    if await baze_bd.user_exists_basket(message.from_user.id) == False:
        await bot.send_message(message.from_user.id, 'У вас нет товаров в корзине')
    else:
        await bot.send_message(message.from_user.id, 'Ваша корзина', reply_markup=client_keyboard.basket_client)
        await baze_bd.user_basket_select(message, message.from_user.id)
        await bot.send_message(message.from_user.id,
                               text=f'Подытог:  {str(await baze_bd.the_amount_of_payment_for_goods_for_users(message.from_user.id))} рублей')



# Удаляет выбраный товар
async def callbacks_basket_del(call: types.CallbackQuery):
    call_del = call.data.split('_')
    user_id = str(call_del[1])
    name = str(call_del[2])
    await baze_bd.user_basket_del_product(user_id, name)
    await bot.answer_callback_query(call.id, text="Товар удалён из Вашей корзины")
    await bot.send_message(call.from_user.id,
        text=f'Подытог: {str(await baze_bd.the_amount_of_payment_for_goods_for_users(call.from_user.id))} рублей')
    await call.message.delete_reply_markup()
    await call.answer()


def client_handler(dp: Dispatcher):
    dp.register_message_handler(comands_start_help, commands=['start', 'help'])
    dp.register_message_handler(operating_mode, (
        lambda
            message: message.text == 'Режим работы ⌚'))  # ввел лямбду что бы запустить ф-цию и убрать косую черту
    dp.register_message_handler(location, (lambda message: message.text == 'Расположение 🧭'))
    dp.register_message_handler(praynik_menu, (lambda message: message.text == 'Меню 🍪'))
    dp.register_callback_query_handler(callbacks_num, (Text(startswith="num_")))
    dp.register_message_handler(in_basket, (lambda message: message.text == 'Корзина 🛒'))
    dp.register_callback_query_handler(callbacks_basket_del, (Text(startswith="del_")))

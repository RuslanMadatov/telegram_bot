from aiogram import types  # это и ниже ввел что бы не было косых черточек в меню
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

client_kbs = types.ReplyKeyboardMarkup(resize_keyboard=True)
b1 = types.KeyboardButton('Режим работы ⌚')
b2 = types.KeyboardButton('Расположение 🧭')
b3 = types.KeyboardButton('Меню 🍪')
b4 = types.KeyboardButton('Корзина 🛒')
client_kbs.add(b3).add(b4).add(b1).insert(b2)  # кнопки внизу экрана

# Меню корзины
basket_client = types.ReplyKeyboardMarkup(resize_keyboard=True)
basket_1 = types.KeyboardButton('Перейти к оплате 💰')
basket_3 = types.KeyboardButton('Назад 🔙')
basket_client.add(basket_1).add(basket_3)


# Добавил инлайн кнопку, чтобы расположение выводилось на карту
client_kbs_inline = InlineKeyboardMarkup(row_width=1)
url_button = InlineKeyboardButton(text='Расположение',
                                  url='https://yandex.ru/maps/11/ryazan/house/ulitsa_yesenina_22/Z0AYcQFmQEMFQFtufXpzeXtjYQ==/?ll=39.766962%2C54.628705&z=16')
client_kbs_inline.add(url_button)

def basket_inlain(id_name):
    inlain_basket = InlineKeyboardMarkup(row_width=1)
    inlain_basket_button = types.InlineKeyboardButton(text='Удалить товар из корзины', callback_data='del_' + id_name)
    inlain_basket.add(inlain_basket_button)
    return inlain_basket

def get_keyboard(id_name):  # инлайн клава для заказов
    # Генерация клавиатуры.
    buttons = [
        types.InlineKeyboardButton(text="-1", callback_data='num_decr_' + id_name),
        types.InlineKeyboardButton(text="+1", callback_data='num_incr_' + id_name),
        types.InlineKeyboardButton(text="В корзину", callback_data="num_finish_" + id_name)
    ]
    # Благодаря row_width=2, в первом ряду будет две кнопки, а оставшаяся одна
    # уйдёт на следующую строку
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard



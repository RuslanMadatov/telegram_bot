from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Кнопки клавы админа
button_load = KeyboardButton('Загрузить новый продукт')
button_update = KeyboardButton('Изменить продукт')
button_del = KeyboardButton('Удалить')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load).add(button_update).add(button_del)

# Кнопки клавы админа для изменения продукта
button_choice_0 = KeyboardButton('Название продукта')
button_choice_1 = KeyboardButton('Состав продукта')
button_choice_2 = KeyboardButton('Изображение продукта')
button_choice_3 = KeyboardButton('Цена')
button_choice_4 = KeyboardButton('Колличество продукта')
button_choice_5 = KeyboardButton('Назад 🔙')

kb_choice = ReplyKeyboardMarkup(resize_keyboard=True).add(button_choice_0).insert(button_choice_1).add(
    button_choice_2).insert(button_choice_3).add(button_choice_4).insert(button_choice_5)

from aiogram import types
from created_bot import dp, Dispatcher
import json, string
from data_baze.baze_bd import exists_in_admin


# добавил ответ для стикеров + для бота у которого нет тригеров
async def echo_document(message: types.Message):
    await message.reply_sticker(message.sticker.file_id)
    await message.answer('Для продолжения общения напишите команду "/start"')


# антимат и проверка на спам
async def echo_send_mat(message: types.Message):
    with open('антимат.json') as file:
        a = set(json.load(file))

    b = set(message.text.translate(str.maketrans('', '', string.punctuation)).lower().split())
    c = (message.text.translate(str.maketrans('', '', string.punctuation)).lower().split())
    lst = ['купить', 'хочу', 'приобрести', 'взять', 'преобрести', 'раздобыть', 'заполучить']
    url = message.text.split(':')

    if a & b != set():
        await message.reply('Мат запрещён')
        await message.delete()
    # почему-то питон считает одинаковые значения Ложью, поэтому все перевернул наоборот
    elif url[0] == 'http' or url[0] == 'https':
        if (exists_in_admin(message.from_user.id)) == True:
            pass
        else:
            await message.reply('Спам запрещён')
            await message.delete()
    else:
        for i in lst:
            if i in c:
                await message.answer('Чтобы купить продукт напишите команду "/start"')
    #     await message.answer(message.text) + для бота у которого нет тригеров
    #     await message.answer('Для продолжения общения напишите команду "/start"')


def others_handler(dp: Dispatcher):
    dp.register_message_handler(echo_document, content_types=[types.ContentType.STICKER])
    dp.register_message_handler(echo_send_mat)

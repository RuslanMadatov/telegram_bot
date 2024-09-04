from created_bot import dp, bot
from aiogram import types, Dispatcher
from aiogram.types.message import ContentType
from config import PAY_TOKEN_TEST
from data_baze import baze_bd


# передает счет покупателю
async def start_of_payment(message: types.Message):
    if PAY_TOKEN_TEST.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, 'Я запущен в тестовом режиме')
    price = types.LabeledPrice(label='Ваши товары',
                               amount=baze_bd.the_amount_of_payment_for_goods_for_cheque(message.from_user.id))
    await bot.send_invoice(message.chat.id, title='Оплата товаров', description='Итого:', provider_token=PAY_TOKEN_TEST,
                           currency='rub', is_flexible=False, prices=[price], start_parameter='products-example',
                           payload=str(message.from_user.id), need_phone_number=True, need_name=True)


# ф-ция отвечающая на запрос банка
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# ф-ция ловящая ответ при оплате
async def process_successful_payment(message: types.Message):
    # проверяем существует ли покупатель в корзине и отправляем админам номер транзакции имя и номер тел покупателя
    if await baze_bd.user_exists_basket(message.successful_payment.invoice_payload) == True:
        await bot.send_message(message.from_user.id, 'Спасибо за покупку!')
        a = message.successful_payment.order_info.phone_number
        b = message.successful_payment.provider_payment_charge_id
        c = message.successful_payment.order_info.name
        admins_id = baze_bd.select_in_admin()
        for id_admin in admins_id:
            for adminid in id_admin:
                if adminid == '5273991830':
                    continue
                else:
                    await bot.send_message(int(adminid),
                                           text=f'Транзакция {b}\nКлиент {c} с номером телефона {a}\n Совершил покупку товара:')
                    for ret in baze_bd.user_basket_select_end(message.successful_payment.invoice_payload):
                        await bot.send_message(int(adminid),
                                               text=f'{ret[0]}\nКолличество: {ret[1]}\nИтоговая цена товара: {ret[2]}')
                    # проверяем сработала ли ф-ция, а затем удаляем покупки юзера из корзины
                    if await baze_bd.the_rest_of_the_product_after_purchase(
                            message.successful_payment.invoice_payload) == True:
                        baze_bd.del_user_in_basket(message.successful_payment.invoice_payload)


def payment_handler(dp: Dispatcher):
    dp.register_message_handler(start_of_payment, (lambda message: message.text == 'Перейти к оплате 💰'))
    dp.register_pre_checkout_query_handler(process_pre_checkout_query, (lambda query: True))
    dp.register_message_handler(process_successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT)

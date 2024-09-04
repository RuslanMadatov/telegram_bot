import logging
from aiogram.utils import executor
from created_bot import dp, bot
from handlers import admin, client, others, payment
from change_button import new_product_composition, new_photo, new_product_price, new_name, new_total_quantity
from  data_baze.baze_bd import cur, conn

log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logging.basicConfig(filename='example.log', format=log_format, level=logging.INFO, filemode='a')


async def on_startup(_):
    print('Бот в работе')


async def stop(_):
    cur.close()
    conn.close()

client.client_handler(dp)
admin.admin_hendler(dp)
new_product_composition.new_discriptions_register(dp)
new_photo.new_photo_register(dp)
new_product_price.new_prices_register(dp)
new_name.new_names_register(dp)
new_total_quantity.new_total_quantity_register(dp)
payment.payment_handler(dp)
others.others_handler(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

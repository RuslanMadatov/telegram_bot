import aioredis
from config import HOST, DB_NAME
from data_baze import baze_bd

redis_cl = aioredis.from_url(url=HOST, db=DB_NAME, encoding="utf-8", decode_responses=True)


# сохраняет фото в redis в admin.py
async def set_photo(message_photo: str) -> None:
    await redis_cl.set('img', message_photo)


# сохраняет название продукта в redis  в admin.py
async def set_name(message_name: str) -> None:
    await redis_cl.set('name', message_name)


# сохраняет состав продукта в redis  в admin.py
async def set_discription(message_discription: str) -> None:
    await redis_cl.set('discription', message_discription)


# сохраняет цену продукта в redis  в admin.py
async def set_price(message_price: str) -> None:
    a = ' руб/шт'
    if ',' in message_price:
        message_price = message_price.replace(',', '.')
    c = message_price + a
    await redis_cl.set('price', c)


# сохраняерт общее колличество продукта в при загрузке нового продукта admin. py
async def set_total_quantity(message_total_quantity: str) -> None:
    await redis_cl.set('total_quantity', message_total_quantity)


# сохраняерт название и  общее колличество продукта остаётся в памяти redis
async def save_total_quantity(name_product: str, total_quantity: str) -> None:
    await redis_cl.set(name_product, total_quantity)


# удаляет из redis название и общее количество продукта, нужна при изменении названия продукта, чтобы не было мусора
async def del_total_quantity(name_product: str) -> None:
    await redis_cl.delete(name_product)


# вызывает из redis колличество продукта
async def get_total_quantity(name_product: str) -> str:
    return await redis_cl.get(name_product)


# загружает фото, название, состав, цену  и количество товара из redis в postgresql  из admin.py
async def load():
    a = str(await redis_cl.get('img')), str(await redis_cl.get('name')), str(
        await redis_cl.get('discription')), str(await redis_cl.get('price')), str(await redis_cl.get('total_quantity'))
    e = tuple(a)
    if await baze_bd.sql_add_command(e) == False:
        return False
    else:
        await save_total_quantity(e[1], e[4])


# загружает новое фото из redis в postgresql
async def load_new_photos():
    a = str(await redis_cl.get('img')), str(await redis_cl.get('name'))
    new_photo = tuple(a)
    await baze_bd.update_photos(new_photo)


# загружает новый состав из redis в postgresql
async def load_new_discriptions():
    a = str(await redis_cl.get('discription')), str(await redis_cl.get('name'))
    new_discriptions = tuple(a)
    await baze_bd.update_discription(new_discriptions)


# сохраняет новое название продукта в redis  в admin.py
async def set_name_new(message_name):
    await redis_cl.set('name_new', message_name)


# загружает новую цену из redis в postgresql
async def load_new_prices():
    a = str(await redis_cl.get('price')), str(await redis_cl.get('name'))
    new_prices = tuple(a)
    await baze_bd.update_price(new_prices)


# загружает новое название продукта из redis в postgresql
async def load_new_names():
    a = str(await redis_cl.get('name_new')), str(await redis_cl.get('name'))
    new_names = tuple(a)
    if await baze_bd.update_name(new_names) == False:
        return False
    else:
        # Добавил это условие, т. к. при изменение имени на идентичное имя redis удаляет значение из памяти
        if new_names[0] == new_names[1]:
            pass
        else:
            res = await get_total_quantity(new_names[1])
            await save_total_quantity(new_names[0], str(res))
            await del_total_quantity(new_names[1])


# загружает новое количество продукта из redis в postgresql
async def load_new_total_quantity():
    a = str(await redis_cl.get('total_quantity')), str(await redis_cl.get('name'))
    new_total_quantity = tuple(a)
    await baze_bd.update_total_quantity(new_total_quantity)
    await save_total_quantity(a[1], a[0])


# удаляет фото, название, состав, цену, количество товара из redis, если они существуют admin.py
async def delit():
    if await redis_cl.exists('img'):
        await redis_cl.delete('img')
    if await redis_cl.exists('name'):
        await redis_cl.delete('name')
    if await redis_cl.exists('name_new'):
        await redis_cl.delete('name_new')
    if await redis_cl.exists('discription'):
        await redis_cl.delete('discription')
    if await redis_cl.exists('price'):
        await redis_cl.delete('price')
    if await redis_cl.exists('total_quantity'):
        await redis_cl.delete('total_quantity')


# изменяет колличество товара, который пойдет в корзину client.py
async def redis_user_value(id_name, user_value):
    id_name = str(id_name)
    user_value = str(user_value)
    await redis_cl.set(id_name, user_value)
    # expire  удаляет значения через n-время
    await redis_cl.expire(name=id_name, time=180)


# вызывает колличество товара, который пойдет в корзину client.py
async def get_redis_user_value(id_name):
    id_name = str(id_name)
    a = await redis_cl.get(id_name)
    # если запрос вывел ничего, то принимаем его равным 0
    if a is None:
        a = 0
    return a

# закрывает redis
def redis_close():
    redis_cl.close()

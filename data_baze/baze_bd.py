import typing
import psycopg2
from created_bot import bot
from config import CONNECT_STR
from keyboards import client_keyboard
from data_baze.redis_db import save_total_quantity

conn = psycopg2.connect(CONNECT_STR)
cur = conn.cursor()

'''def sql_start():
    global base, cur
    base = sqlite3.connect('Praynik.db')
    cur = base.cursor()
    if base:
        print('Date base connect')
    base.execute('CREATE TABLE IF NOT EXISTS menu(img TEXT, name TEXT PRIMARY KEY, discription TEXT, price TEXT)')
    base.commit()'''


# загрзка данных о товаре от администратора в меню admin.py
async def sql_add_command(e: typing.Tuple[str, str, str, str, str]):
    try:
        cur.execute("""INSERT INTO menu (img, name, discription, price, total_quantity)
                                        VALUES(%s, %s, %s, %s, %s)
                                        """, e)
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False
    else:
        conn.commit()
    #conn.close()
    #cur.close()


# загрзка данных о товаре от покупателя при нажатии в корзину
async def insert_in_basket(user_id: str, name_product: str, price: float, quantity_of_goods: int,
                           total_product_price: float):
    try:
        cur.execute("""INSERT INTO basket (user_id, name, price, quantity, total_amount)
                                        VALUES(%s, %s, %s, %s, %s)
                                        """,
                    (str(user_id), str(name_product), str(price), str(quantity_of_goods), str(total_product_price)))
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False
    else:
        conn.commit()
    #conn.close()
    #cur.close()


# ф-ция для загрузки и обновления админов в БД
async def insert_in_admin(adminsId: typing.List[str]) -> None:
    cur.execute('TRUNCATE admin')
    conn.commit()
    for i in adminsId:
        cur.execute("""INSERT INTO admin (admin_id) VALUES(%s)""", (str(i),))
        conn.commit()


# ф-ция вызова id админов для payment
def select_in_admin():
    cur.execute('SELECT * FROM admin;')
    return cur.fetchall()

def exists_in_admin(user_id):
    cur.execute('SELECT EXISTS (SELECT * FROM admin WHERE admin_id=%s)', (str(user_id),))
    result = cur.fetchone()
    # т.к. False находится в списке и кортеже одновремнно пришлось её вытаскивать
    return result[0]


# Выводит меню для клиента в client py
async def sql_read_client(message, user_id: str) -> None:
    cur.execute('SELECT * FROM menu;')
    for ret in cur.fetchall():
        await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nСостав продукта: {ret[2]}\nЦена: {ret[3]}',
                             reply_markup=client_keyboard.get_keyboard(str(user_id) + '_' + str(ret[1])))
    conn.commit()
    #conn.close()
    #cur.close()


# Выводит меню для админа в admin.py для удаления товара
async def sql_read_admin():
    cur.execute('SELECT * FROM menu')
    return cur.fetchall()


# Удаляет выбранный объект в admin.py
async def sql_delete_command(data: str) -> None:
    cur.execute('DELETE FROM menu WHERE name=%s', (data,))
    conn.commit()
    #conn.close()
    #cur.close()


# показывает все имена из меню для изменений в продукте для файлов в change_button
async def call_name_menu():
    cur.execute('SELECT name FROM menu')
    return cur.fetchall()


# загружает новый состав продукта в new_product_composition
async def update_discription(new_discriptions: typing.Tuple[str, str]) -> None:
    cur.execute('UPDATE menu SET discription=%s WHERE name=%s', new_discriptions)
    conn.commit()
    #conn.close()
    #cur.close()


# загружает новое фото продукта в new_photo
async def update_photos(new_photo: typing.Tuple[str, str]) -> None:
    cur.execute('UPDATE menu SET img=%s WHERE name=%s', new_photo)
    conn.commit()
    #conn.close()
    #cur.close()


# загружает новую цену продукта в new_product_price
async def update_price(new_prices: typing.Tuple[str, str]) -> None:
    cur.execute('UPDATE menu SET price=%s WHERE name=%s', new_prices)
    conn.commit()
    #conn.close()
    #cur.close()


# загружает новое название продукта в new_name
async def update_name(new_names: typing.Tuple[str, str]):
    try:
        cur.execute('UPDATE menu SET name=%s WHERE name=%s', new_names)
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False
    else:
        conn.commit()
    #conn.close()
    #cur.close()


# загружает новую цену продукта в new_product_price
async def update_total_quantity(new_total_quantity: typing.Tuple[str, str]) -> None:
    cur.execute('UPDATE menu SET total_quantity=%s WHERE name=%s', new_total_quantity)
    conn.commit()
    #conn.close()
    #cur.close()


#  ф-ция, чтобы узнать есть ли товар в корзине клиента client.py
async def user_exists_basket(user_id: str) -> bool:
    cur.execute('SELECT EXISTS(SELECT * FROM basket WHERE user_id=%s)', (str(user_id),))
    result = cur.fetchone()
    return result[0]


#  ф-ция, чтобы узнать стоймость товара из menu и передать её затем в basket  client.py
async def price_product(name_product: str) -> str:
    cur.execute('SELECT price FROM menu WHERE name=%s', (name_product,))
    price_product = cur.fetchone()
    cost = price_product[0].split(' ')
    conn.commit()
    return cost[0]


# загружает товары выбранные пользователем с инлайн кнопкой "удалить"
async def user_basket_select(message, user_id: str):
    cur.execute('SELECT name, quantity, total_amount FROM basket WHERE user_id=%s', (str(user_id),))
    for ret in cur.fetchall():
        await bot.send_message(message.from_user.id, f'{ret[0]}\nКолличество: {ret[1]}\nИтоговая цена товара: {ret[2]}',
                               reply_markup=client_keyboard.basket_inlain(str(user_id) + '_' + str(ret[0])))
    conn.commit()


# Загружает товары выбранные покупателем
def user_basket_select_end(user_id: str):
    cur.execute('SELECT name, quantity, total_amount FROM basket WHERE user_id=%s', (str(user_id),))
    return cur.fetchall()


#  Удаляет выбраный товар из корзины
async def user_basket_del_product(user_id: str, name: str) -> None:
    cur.execute('DELETE FROM basket WHERE user_id=%s AND name=%s', (user_id, name))
    conn.commit()



#  Удаляет юзера из корзины и его покупки после оплаты
def del_user_in_basket(user_id: str) -> None:
    cur.execute('DELETE FROM basket WHERE user_id=%s', (str(user_id),))
    conn.commit()
    #conn.close()
    #cur.close()


# Считает подытог
async def the_amount_of_payment_for_goods_for_users(user_id: str) -> None:
    amount = 0.0
    cur.execute('SELECT total_amount FROM basket WHERE user_id=%s', (str(user_id),))
    for i in cur.fetchall():
        for j in i:
            if j is None:
                j = 0
        amount += float(j)
    conn.commit()
    return amount


#  Считает итог и передаёт в payment send_invoice
def the_amount_of_payment_for_goods_for_cheque(user_id: str) -> int:
    amount = 0.0
    cur.execute('SELECT total_amount FROM basket WHERE user_id=%s', (str(user_id),))
    for i in cur.fetchall():
        for j in i:
            amount += float(j)
    amount *= 100.0
    conn.commit()
    return int(amount)


# Считает количество оставшегося товара после покупки и сохряняет в БД
async def the_rest_of_the_product_after_purchase(user_id: str) -> bool:
    cur.execute('SELECT name, quantity FROM basket WHERE user_id=%s', (str(user_id),))
    for ret in cur.fetchall():
        cur.execute('SELECT total_quantity FROM menu WHERE name=%s', (str(ret[0]),))
        for i in cur.fetchall():
            res = int(i[0]) - int(ret[1])
            cur.execute('UPDATE menu SET total_quantity=%s WHERE name=%s', tuple([str(res), str(ret[0])]))
            conn.commit()
            await save_total_quantity(str(ret[0]), str(res))
    return True

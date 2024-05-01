import random
import telebot
import webbrowser
import sqlite3
from telebot import types
from datetime import datetime


# Считывание токена телеграм бота
file = open('./token.txt')
mytoken = file.read()
# Передача токена
bot = telebot.TeleBot(mytoken)
# Переменная действующей секции
current_section = None
# Переменная для хранения информации о последнем показанном товаре
last_displayed_products = {}
# Словарь для хранения корзин для каждого пользователя
carts = {}

#Загрузка всех товаров из базы данных
def load_all_products():
    conn = sqlite3.connect('./db/catalog.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, pic, price, brand, category, details FROM products")
    all_products_data = cursor.fetchall()
    conn.close()
    return all_products_data

# ----- Категории каталога ------
def display_category(message, product_list, category_name, section_title):
    max_buttons_per_row = 2
    buttons = add_buttons_to_markup({str(product[0]): product[1] for product in product_list}, max_buttons_per_row)
    buttons.append([back_btns['back_catalog']])
    buttons.append([back_btns['back_home']])
    markup = create_markup(buttons)
    bot.send_message(message.chat.id, f'Раздел {section_title}:', reply_markup=markup)

def set_current_section_and_display_category(message, section_name, product_list, category_name, section_title):
    global current_section
    current_section = section_name
    # Создаем кнопки
    display_category(message, product_list, category_name, section_title)
def display_category_by_name(message, category_name, section_title):
    category_products = [product for product in products_list if product[5] == category_name]
    if category_products:
        set_current_section_and_display_category(message, category_name, category_products, category_name, section_title)
    else:
        bot.send_message(message.chat.id, f"В категории '{section_title}' нет товаров.")

def drives_category(message):
    display_category_by_name(message, "drives", "AIRSOFT приводов (Модели страйкбольного «оружия»)")

def sights_category(message):
    display_category_by_name(message, "sights", "Оптические прицелы")

def gas_category(message):
    display_category_by_name(message, "gas", "Газа")

def girboxes_category(message):
    display_category_by_name(message, "girboxes", "Гирбоксов")

def launchers_category(message):
    display_category_by_name(message, "launchers", "Пусковых устройств")

def hopup_nodes_category(message):
    display_category_by_name(message, "hopup_nodes", "Хоп-апов")

def gears_category(message):
    display_category_by_name(message, "gears", "Шестерней")

# ----- Закрытие категории каталога ------

products_list = load_all_products()

#Создание таблицы пользователей
def create_account_table(user_id, telegram_username):
    connection = sqlite3.connect('./db/users.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS account (
                        user_id INTEGER PRIMARY KEY,
                        telegram_username TEXT,
                        start_time TEXT,
                        last_activity_time TEXT
                    )''')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Проверяем, существует ли запись с данным user_id
    cursor.execute('''SELECT user_id FROM account WHERE user_id = ?''', (user_id,))
    existing_user = cursor.fetchone()
    if not existing_user:  # Если пользователь еще не существует, то добавляем
        cursor.execute(
            '''INSERT INTO account (user_id, telegram_username, start_time, last_activity_time) VALUES (?, ?, ?, ?)''',
            (user_id, telegram_username, current_time, current_time))
    else:  # Если пользователь уже существует, обновляем время последнего захода
        cursor.execute('''UPDATE account SET last_activity_time = ? WHERE user_id = ?''', (current_time, user_id))
    connection.commit()
    connection.close()

# Ответы пользователю, если введено что-то непонятное для бота
answers = ['Я не понял, что ты хочешь сказать.',
           'Извини, я тебя не понимаю.',
           'Я не знаю такой команды.',
           'Увы, я не знаю, что отвечать в такой ситуации... >_<'
           ]


# ------- Кнопки -------
start_btns = {
    'catalog': '🛍 Каталог',
    'about': '🛈 О нас',
    'faqs': '📄 Частые вопросы'
}
about_btns = {
    'number': '📞 Номер телефона',
    'address': '🗺️ Адрес'
}
faq_btns = {
    'Являются ли оружием товары?':  'Cогласно Федеральному закону <i>"Об оружии" от 13.12.1996 N 150-ФЗ.</i>  товары в нашем магазине <b>НЕ ЯВЛЯЮТСЯ ОРУЖИЕМ!</b> '
                                    'Airsoft - пневматика, с дульной энергией менее 3Дж, использует только пластиковые шары - 6мм.',
    'Почему наши клиенты лучшие?': 'Потому что они крутые!'
}
back_btns = {
    'back': '↩️ Назад',
    'back_catalog': '↩️ В каталог',
    'back_home': '↩️ Вернуться в меню'
}
buy_btns = {
    'buy': 'Купить',
    'cart': '🛒 Корзина',
    'add_to_cart': '🛒 Добавить в корзину'
}
goods_btns = {
    'drives': 'Привода',
    'sights': 'Прицелы',
    'girboxes': 'Гирбоксы',
    'gas': 'Газ',
    'launchers': 'Пусковые устройства',
    'gears': 'Шестерни',
    'hopup_nodes':'Узлы хоп-ап'
}
# ------- Закрытие кнопки -------

# Функция для генерации случайного ответа
def random_answer(message):
    bot.send_message(message.chat.id, answers[random.randint(0, 3)])

# Функция для удобного создания кнопок
def create_markup(buttons):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in buttons:
        markup.row(*row)
    return markup

# Создание кнопок для товара
def create_buttons_for_product():
    return [
        [buy_btns['add_to_cart']],
        [buy_btns['cart']],
        [back_btns['back'], back_btns['back_catalog']],
        [back_btns['back_home']]
    ]

# Добавление кнопок в ряд
def add_buttons_to_markup(button_dict, max_buttons_per_row):
    buttons = []
    row = []
    for btn_key, btn_text in button_dict.items():
        row.append(btn_text)
        if len(row) == max_buttons_per_row:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return buttons

# Обработка фото и стикеров
@bot.message_handler(content_types=['photo', 'sticker', 'audio'])
def get_photo(message):
    bot.send_message(message.chat.id, 'Извини, я не могу обрабатывать фото, стикеры и голосовые :(')


# Функция обработки команды /start
@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.from_user.id
    user_username = message.from_user.username

    # Кнопки после /start
    buttons = [
        [start_btns['catalog']],
        [buy_btns['cart']],
        [start_btns['about'], start_btns['faqs']],
    ]
    markup = create_markup(buttons)

    if message.text == '/start':
        create_account_table(user_id, user_username )
        # Отправляем приветственное сообщение
        bot.send_message(message.chat.id,
                         f'Привет, {message.from_user.first_name}!\n В нашей мастерской "FRW - Fire Rabbit Workshop" ты можешь приобрести качественное снаряжение и экипировку для страйкбола!\n ВК моего владельца: https://vk.com/petrucho_t',
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Вернули тебя в главное меню!', reply_markup=markup)


#Добавление товара в корзину
@bot.message_handler(func=lambda message: message.text == buy_btns.get('add_to_cart'))
def inquire_about_product(message):
    user_id = message.chat.id
    if user_id in last_displayed_products:
        selected_product_info = last_displayed_products[user_id][0]  # Получаем информацию о товаре
        selected_product_name = selected_product_info["название"]  # Получаем название товара
        selected_product_price = selected_product_info["цена"]  # Получаем цену товара

        if user_id not in carts:
            carts[user_id] = []  # Если корзины пользователя еще нет, создаем пустую корзину

        cart_item = {"название": selected_product_name, "цена": selected_product_price}
        carts[user_id].append(cart_item)  # Добавляем товар в корзину
        bot.send_message(message.chat.id, f'Товар "{selected_product_name}" добавлен в корзину.')
        print(carts)
    else:
        bot.send_message(message.chat.id, "Не удалось добавить товар в корзину. Попробуйте заново.")


#Показ корзины + удаление товаров из неё
@bot.message_handler(func=lambda message: message.text == '🛒 Корзина' or message.text.lower() == 'все')
def show_cart(message):
    buttons = [
        [buy_btns['buy']],
        [back_btns['back_home']]
    ]
    markup = create_markup(buttons)
    user_id = message.chat.id
    if user_id in carts:
        if message.text.lower() == 'все':  # Проверяем, если отправлено слово "все"
            carts[user_id] = []  # Очищаем корзину для данного пользователя
            bot.send_message(message.chat.id, "Корзина очищена.", reply_markup=markup)
            return
        cart_items = carts[user_id]
        if cart_items:
            total_price = 0  # Переменная для хранения общей суммы
            requires_confirmation = False  # Флаг, указывающий на то, что есть товары с неполной ценой
            response = "Ваша корзина:\n"
            for i, item in enumerate(cart_items, start=1):
                # Проверяем, есть ли цифры в строке цены
                if any(char.isdigit() for char in item["цена"]):
                    price = int(''.join(filter(str.isdigit, item["цена"])))  # Извлекаем только цифры из цены
                else:
                    price = 0  # Если цифр вообще нет, считаем цену равной нулю
                    requires_confirmation = True
                total_price += price  # Добавляем цену товара к общей сумме
                response += f'{i}. Название: {item["название"]}, Цена: {item["цена"]}\n'
            total_price_str = str(total_price) + "₽"
            if requires_confirmation:
                total_price_str += " (требует уточнения)"
            response += f"\nОбщая сумма: {total_price_str}"  # Добавляем общую сумму в текст ответа
            response += "\n\nЧтобы удалить товар из корзины, отправьте его номер.\nЕсли хотите очистить корзину полностью, напишите 'все'."
            bot.send_message(message.chat.id, response, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Ваша корзина пуста.",  reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ваша корзина пуста.",  reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in [name_product[1] for name_product in products_list])
def handle_product_message(message):
    user_id = message.chat.id
    last_displayed_products[user_id] = []  # Инициализируем список товаров пользователя
    product_name = message.text
    for product in products_list:
        if product_name == product[1]:
            last_displayed_products[user_id].append({"название": product[1], "цена": product[3]})  # Добавляем товар в список пользователя
            print(last_displayed_products)

            response = f"Название: {product[1]}\n"
            response += f"Цена: {product[3]}\n"
            response += f"Бренд: {product[4]}\n"
            response += f"Описание: {product[6]}"
            caption = response

            photo_path = product[2]  # Путь к файлу изображения
            photo = open(photo_path, 'rb')  # Открываем файл изображения
            bot.send_photo(message.chat.id, photo, caption=caption)
            photo.close()  # Закрываем файл после отправки

            buttons = create_buttons_for_product()
            markup = create_markup(buttons)
            bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
            return


#Купить
@bot.message_handler(func=lambda message: message.text == buy_btns['buy'])
def buy_product(message):
    user_id = message.chat.id
    if user_id in carts:
        cart_items = carts[user_id]
        if cart_items:
            response = "Ваша корзина:\n"
            total_price = 0
            requires_confirmation = False
            cart_text = "<pre>"
            item_counts = {}  # Словарь для хранения количества каждого товара
            already_printed = []  # Список для отслеживания уже выведенных товаров
            for item in cart_items:
                item_name = item["название"]
                item_counts[item_name] = item_counts.get(item_name, 0) + 1
            i = 1  # Инициализируем индекс для вывода товаров
            for item in cart_items:
                item_name = item["название"]
                if item_name not in already_printed:
                    if any(char.isdigit() for char in item["цена"]):  # Проверяем, есть ли цифры в строке цены
                        price = int(''.join(filter(str.isdigit, item["цена"])))
                    else:
                        price = 0  # Если цифр вообще нет, считаем цену равной нулю
                        requires_confirmation = True
                    total_price += price * item_counts[item_name]  # Умножаем цену на количество штук товара
                    if item_counts[item_name] > 1:
                        # Если количество товаров больше 1, выводим количество штук и умноженную цену
                        cart_text += f'{i}. Товар: {item_name} ({item_counts[item_name]} штуки), Цена: {item["цена"]} * {item_counts[item_name]} = {price * item_counts[item_name]}₽\n'
                    else:
                        cart_text += f'{i}. Товар: {item_name}, Цена: {item["цена"]}\n'
                    # Добавляем текущий товар в список уже выведенных
                    already_printed.append(item_name)
                    i += 1  # Увеличиваем индекс для следующего товара
            if requires_confirmation:
                cart_text += f"\nОбщая сумма: {total_price}₽ (требует уточнения)\n"
            else:
                cart_text += f"\nОбщая сумма: {total_price}₽\n"
            cart_text += "</pre>"
            response += cart_text
            response += "\nДля покупки скопируйте содержимое корзины (нажмите на название товара и все содержимое скопируется) и свяжитесь с нами по ссылке: <a href='https://t.me/liipkka'>Написать в Telegram</a>"
            bot.send_message(message.chat.id, response, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Ваша корзина пуста.")
    else:
        bot.send_message(message.chat.id, "Ваша корзина пуста.")


# Обработка обычных текстовых команд, описанных в кнопках
@bot.message_handler(func=lambda message: True)
def info(message):
    if message.text == start_btns.get('catalog'):
        goodsChapter(message)

    elif message.text == start_btns.get('about'):
        aboutUs(message)

    elif message.text == start_btns.get('faqs'):
        faqAnswer(message)

    elif message.text == about_btns.get('number'):
        bot.send_message(message.chat.id,'<b>Номер телефона:</b> 7 (924) 834-88-86', parse_mode='html')

    elif message.text == about_btns.get('address'):
        bot.send_message(message.chat.id,'<b>Адрес:</b> Иркутск, Декабрьских событий, 102', parse_mode='html')

    elif message.text == goods_btns.get('drives'):
        drives_category(message)

    elif message.text == goods_btns.get('sights'):
        sights_category(message)

    elif message.text == goods_btns.get('gas'):
        gas_category(message)

    elif message.text == goods_btns.get('girboxes'):
        girboxes_category(message)

    elif message.text == goods_btns.get('launchers'):
        launchers_category(message)

    elif message.text == goods_btns.get('hopup_nodes'):
        hopup_nodes_category(message)

    elif message.text == goods_btns.get('gears'):
        gears_category(message)

    elif message.text == buy_btns.get('buy'):
        webbrowser.open('')

    elif message.text == back_btns.get('back'):
        if current_section:
            # Если пользователь находится в каком-то разделе каталога, возвращаем его к списку товаров этого раздела
            if current_section == "drives":
                drives_category(message)
            elif current_section == "sights":
                sights_category(message)
            elif current_section == "gas":
                gas_category(message)
            elif current_section == "girboxes":
                girboxes_category(message)
            elif current_section == "launchers":
                launchers_category(message)
            elif current_section == "hopup_nodes":
                hopup_nodes_category(message)
            elif current_section == "gears":
                gears_category(message)
        else:
            goodsChapter(message)

    elif message.text in faq_btns:
        text = f'{faq_btns[message.text]}'
        bot.send_message(message.chat.id, text, parse_mode='html')

    elif message.text == back_btns.get('back_catalog'):
        goodsChapter(message)

    elif message.text == back_btns.get('back_home'):
        welcome(message)

    else:
        random_answer(message)

# Функция, отвечающая за раздел товаров
def goodsChapter(message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    create_account_table(user_id, user_username)
    max_buttons_per_row = 3
    buttons = add_buttons_to_markup(goods_btns, max_buttons_per_row)
    buttons.append([back_btns['back_home']])
    markup = create_markup(buttons)
    bot.send_message(message.chat.id, "Каталог товаров:", reply_markup=markup)

# Функция, отвечающая за раздел о нас
def aboutUs(message):
    buttons = [
        [about_btns['number'], about_btns['address']],
        [back_btns['back_home']]
    ]
    markup = create_markup(buttons)
    bot.send_message(message.chat.id, 'Раздел "О нас".\nЗдесь ты можешь узнать информацию о нас.', reply_markup=markup)

# Функция, отвечающая за раздел вопрос частых
def faqAnswer(message):
    buttons = []
    row = []
    for btn_key in faq_btns:
        row.append(btn_key)
        if len(row) == 3:  # Когда в ряду уже три кнопки, добавляем этот ряд и начинаем новый
            buttons.append(row)
            row = []
    if row:  # Добавляем последний неполный ряд, если он есть
        buttons.append(row)
    buttons.append([back_btns['back_home']])  # Добавляем кнопку "Назад на главную"
    markup = create_markup(buttons)
    bot.send_message(message.chat.id, 'Раздел "Вопросы и ответы".\nЗдесь ты можешь найти ответы на часто задаваемые вопросы.', reply_markup=markup)

# Строчка, чтобы программа не останавливалась
bot.polling(none_stop=True)
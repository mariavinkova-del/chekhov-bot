"""
Телеграм-бот «Я навсегда москвич: Чеховская Москва»
Запуск: python3 chekhov_bot.py
Зависимости: pip install pyTelegramBotAPI requests
"""

import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ======================================================
# ТОКЕН БОТА — вставьте сюда ваш актуальный токен
# ======================================================
TOKEN = '8730914019:AAFlPfJbcyN5zy2lzo3yEAuntS7ujMyhtxY'

bot = telebot.TeleBot(TOKEN)

# ======================================================
# ФОТО — замените None на open("photos/имя.jpg", "rb")
# когда добавите фотографии в папку photos/
# ======================================================
PHOTOS = {
    "map": open("photos/map.jpg", "rb"),
    "university": open("photos/university.jpg", "rb"),
    "chekhov_house": open("photos/chekhov_house.jpg", "rb"),
    "church": open("photos/church.jpg", "rb"),
    "hermitage": open("photos/hermitage.jpg", "rb"),
    "mhat": open("photos/mhat.jpg", "rb"),
    "dmitrovka": open("photos/dmitrovka.jpg", "rb"),
    "novodevichy": open("photos/novodevichy.jpg", "rb"),
}
# ======================================================
# ХРАНИЛИЩЕ ОЧКОВ ВИКТОРИНЫ
# user_id -> количество правильных ответов
# ======================================================
quiz_scores = {}

# ======================================================
# ПРОГРЕСС МАРШРУТА
# ======================================================
TOTAL_STOPS = 7

def progress_bar(current, total=TOTAL_STOPS):
    filled = "▓" * current
    empty = "░" * (total - current)
    return f"{filled}{empty} {current}/{total}"

# ======================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ======================================================

def kb(*buttons):
    markup = InlineKeyboardMarkup()
    for text, data in buttons:
        markup.add(InlineKeyboardButton(text, callback_data=data))
    return markup

def send_photo_or_text(chat_id, photo_key, caption, markup):
    photo = PHOTOS.get(photo_key)
    if photo:
        bot.send_photo(chat_id, photo, caption=caption, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, f"🖼 <i>[Фото: {photo_key}]</i>\n\n{caption}", reply_markup=markup, parse_mode="HTML")

def edit_or_send(call, text, markup):
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              reply_markup=markup, parse_mode="HTML")
    except Exception:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

def get_moscow_weather():
    try:
        url = "https://wttr.in/Moscow?format=j1"
        r = requests.get(url, timeout=5)
        data = r.json()
        temp = data["current_condition"][0]["temp_C"]
        feels = data["current_condition"][0]["FeelsLikeC"]
        desc = data["current_condition"][0]["weatherDesc"][0]["value"]
        humidity = data["current_condition"][0]["humidity"]

        temp_int = int(temp)
        if temp_int >= 18:
            advice = "☀️ Отличная погода для пешей прогулки по маршруту!"
        elif temp_int >= 10:
            advice = "🧥 Возьмите лёгкую куртку — и вперёд на маршрут!"
        elif temp_int >= 0:
            advice = "🧤 Оденьтесь потеплее — на улице прохладно."
        else:
            advice = "🥶 Морозно! Возможно, лучше изучить маршрут виртуально."

        return (
            f"🌤 <b>Погода в Москве сейчас:</b>\n\n"
            f"🌡 Температура: <b>{temp}°C</b> (ощущается как {feels}°C)\n"
            f"💧 Влажность: {humidity}%\n"
            f"☁️ {desc}\n\n"
            f"{advice}"
        )
    except Exception:
        return "🌤 <b>Погода в Москве:</b>\n\nНе удалось загрузить данные.\nПроверьте соединение с интернетом."

# ======================================================
# ГЛАВНОЕ МЕНЮ
# ======================================================

def show_main_menu(chat_id, message_id=None):
    text = (
        "<b>«Я навсегда москвич: Чеховская Москва»</b>\n\n"
        "Интерактивный исторический бот-гид.\n"
        "Проект посвящён московским адресам Антона Павловича Чехова "
        "и культурной среде Москвы конца XIX века.\n\n"
        "Выберите раздел:"
    )
    markup = kb(
        ("🗺 Начать маршрут", "route_menu"),
        ("📍 Карта", "map"),
        ("📖 О Чехове", "about"),
        ("🎭 Викторина", "quiz_start"),
        ("💡 Интересные факты", "facts_menu"),
        ("🌤 Погода в Москве", "weather"),
        ("📚 Источники", "sources"),
    )
    if message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
        except Exception:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=["start"])
def start(message):
    show_main_menu(message.chat.id)


# ======================================================
# ПОГОДА
# ======================================================

def show_weather(call):
    weather_text = get_moscow_weather()
    text = weather_text + "\n\n<i>Данные обновляются в реальном времени.</i>"
    markup = kb(
        ("🗺 Начать маршрут", "route_menu"),
        ("🏠 Главное меню", "main_menu"),
    )
    edit_or_send(call, text, markup)


# ======================================================
# КАРТА
# ======================================================

def show_map(call):
    caption = (
        "📍 <b>Маршрут «Чеховская Москва»</b>\n\n"
        "Протяжённость маршрута: около 7 км пешком.\n"
        "Продолжительность: 5–6 часов.\n\n"
        "Маршрут включает 7 остановок, связанных с жизнью и творчеством А.П. Чехова."
    )
    markup = kb(
        ("🗺 Начать маршрут", "route_menu"),
        ("🏠 Вернуться в меню", "main_menu"),
    )
    photo = PHOTOS.get("map")
    if photo:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_photo(call.message.chat.id, photo, caption=caption, reply_markup=markup, parse_mode="HTML")
    else:
        edit_or_send(call, f"🖼 <i>[Здесь будет карта маршрута]</i>\n\n{caption}", markup)


# ======================================================
# О ЧЕХОВЕ
# ======================================================

def show_about(call):
    text = (
        "📖 <b>Антон Павлович Чехов (1860–1904)</b>\n\n"
        "Русский писатель, драматург и врач.\n\n"
        "<b>Основные темы творчества:</b>\n"
        "— повседневная жизнь\n"
        "— кризис интеллигенции\n"
        "— одиночество\n"
        "— социальные противоречия\n"
        "— изменение русской провинции\n\n"
        "Чехов получил медицинское образование в Москве и значительную часть жизни был связан с городом."
    )
    markup = kb(
        ("📅 Биография", "biography"),
        ("🩺 Чехов и медицина", "medicine"),
        ("🎭 Чехов и театр", "theatre"),
        ("🏠 Вернуться в меню", "main_menu"),
    )
    edit_or_send(call, text, markup)

def show_biography(call):
    text = (
        "📅 <b>Биография</b>\n\n"
        "Антон Чехов родился в Таганроге в 1860 году.\n\n"
        "В 1879 году переехал в Москву и поступил на медицинский факультет Московского университета.\n\n"
        "Во время учёбы начал публиковать рассказы в юмористических журналах под псевдонимом <i>«Антоша Чехонте»</i>.\n\n"
        "В 1890-е годы стал одним из крупнейших русских писателей и драматургов."
    )
    markup = kb(
        ("⬅️ Вернуться назад", "about"),
        ("🏠 Главное меню", "main_menu"),
    )
    edit_or_send(call, text, markup)

def show_medicine(call):
    text = (
        "🩺 <b>Чехов и медицина</b>\n\n"
        "Чехов работал врачом и совмещал медицину с литературной деятельностью.\n\n"
        "Медицинский опыт повлиял на его произведения:\n"
        "<i>«Палата №6»</i>, <i>«Скучная история»</i>, <i>«Ионыч»</i>.\n\n"
        "Чехов участвовал в борьбе с эпидемиями и бесплатно лечил крестьян."
    )
    markup = kb(
        ("⬅️ Вернуться назад", "about"),
        ("🏠 Главное меню", "main_menu"),
    )
    edit_or_send(call, text, markup)

def show_theatre_about(call):
    text = (
        "🎭 <b>Чехов и театр</b>\n\n"
        "Сотрудничество Чехова с Московским Художественным театром стало важным этапом развития русского театра.\n\n"
        "<b>Постановки МХТ:</b>\n"
        "— «Чайка»\n"
        "— «Дядя Ваня»\n"
        "— «Три сестры»\n"
        "— «Вишнёвый сад»\n\n"
        "Они сформировали новый подход к драматургии и актёрской игре."
    )
    markup = kb(
        ("⬅️ Вернуться назад", "about"),
        ("🏠 Главное меню", "main_menu"),
    )
    edit_or_send(call, text, markup)


# ======================================================
# МЕНЮ МАРШРУТА
# ======================================================

def show_route_menu(call):
    text = (
        "🗺 <b>Маршрут «Чеховская Москва»</b>\n\n"
        "Маршрут включает 7 остановок.\n"
        "Выберите остановку или идите по порядку:"
    )
    markup = kb(
        ("1️⃣ Московский университет", "stop_1"),
        ("2️⃣ Дом-музей Чехова", "stop_2"),
        ("3️⃣ Церковь (Венчание)", "stop_3"),
        ("4️⃣ Ресторан «Эрмитаж»", "stop_4"),
        ("5️⃣ МХТ", "stop_5"),
        ("6️⃣ Малая Дмитровка", "stop_6"),
        ("7️⃣ Новодевичье кладбище", "stop_7"),
        ("🏠 Главное меню", "main_menu"),
    )
    edit_or_send(call, text, markup)


# ======================================================
# ОСТАНОВКИ МАРШРУТА (с прогресс-баром)
# ======================================================

def show_stop_1(call):
    caption = (
        f"📍 <b>Остановка 1: Московский университет</b>\n"
        f"ул. Моховая, д. 11\n"
        f"<code>{progress_bar(1)}</code>\n\n"
        "В 1879 году Чехов поступил на медицинский факультет Московского университета.\n\n"
        "Во время учёбы он публиковал рассказы под псевдонимом <i>«Антоша Чехонте»</i> "
        "и сотрудничал с московскими журналами.\n\n"
        "Медицинское образование оказало значительное влияние на его творчество."
    )
    markup = kb(
        ("💡 Интересный факт", "fact_1"),
        ("💬 Цитата", "quote_1"),
        ("➡️ Следующая остановка", "stop_2"),
        ("🏠 Главное меню", "main_menu"),
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_photo_or_text(call.message.chat.id, "university", caption, markup)

def show_fact_1(call):
    text = (
        "💡 <b>Интересный факт</b>\n\n"
        "Чехов совмещал учёбу и литературную работу, чтобы поддерживать семью после банкротства отца."
    )
    markup = kb(("⬅️ Назад к остановке", "stop_1"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)

def show_quote_1(call):
    text = "💬 <b>Цитата</b>\n\n<i>«Медицина — моя законная жена, а литература — любовница».</i>"
    markup = kb(("⬅️ Назад к остановке", "stop_1"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)


def show_stop_2(call):
    caption = (
        f"📍 <b>Остановка 2: Дом-музей А.П. Чехова</b>\n"
        f"ул. Садовая-Кудринская, д. 6\n"
        f"<code>{progress_bar(2)}</code>\n\n"
        "С 1886 по 1890 год Чехов жил здесь и написал произведения:\n"
        "<i>«Степь»</i>, <i>«Скучная история»</i>, <i>«Огни»</i>.\n\n"
        "Дом стал центром литературной жизни Москвы конца XIX века."
    )
    markup = kb(
        ("👥 Кто бывал у Чехова", "guests"),
        ("💬 Цитата", "quote_2"),
        ("➡️ Следующая остановка", "stop_3"),
        ("🏠 Главное меню", "main_menu"),
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_photo_or_text(call.message.chat.id, "chekhov_house", caption, markup)

def show_guests(call):
    text = (
        "👥 <b>Кто бывал у Чехова</b>\n\n"
        "Дом Чехова посещали:\n"
        "— Исаак Левитан\n"
        "— Пётр Чайковский\n"
        "— Владимир Гиляровский\n"
        "— Дмитрий Григорович"
    )
    markup = kb(("⬅️ Назад", "stop_2"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)

def show_quote_2(call):
    text = "💬 <b>Цитата</b>\n\n<i>«Я навсегда москвич».</i>"
    markup = kb(("⬅️ Назад", "stop_2"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)


def show_stop_3(call):
    caption = (
        f"📍 <b>Остановка 3: Церковь Воздвижения Креста Господня</b>\n"
        f"1-й Тружеников пер., д. 8\n"
        f"<code>{progress_bar(3)}</code>\n\n"
        "В 1901 году здесь состоялось венчание Антона Чехова и Ольги Книппер.\n"
        "Церемония проходила в узком кругу.\n\n"
        "История брака Чехова и Книппер отражает тесную связь литературы и театра начала XX века."
    )
    markup = kb(
        ("💡 Интересный факт", "fact_3"),
        ("💬 Цитата", "quote_3"),
        ("➡️ Следующая остановка", "stop_4"),
        ("🏠 Главное меню", "main_menu"),
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_photo_or_text(call.message.chat.id, "church", caption, markup)

def show_fact_3(call):
    text = (
        "💡 <b>Интересный факт</b>\n\n"
        "После венчания Чехов и Книппер сразу отправились на вокзал и уехали в свадебное путешествие."
    )
    markup = kb(("⬅️ Назад", "stop_3"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)

def show_quote_3(call):
    text = "💬 <b>Цитата</b>\n\n<i>«Если боитесь одиночества, то не женитесь».</i>"
    markup = kb(("⬅️ Назад", "stop_3"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)


def show_stop_4(call):
    caption = (
        f"📍 <b>Остановка 4: Ресторан «Эрмитаж»</b>\n"
        f"Петровский бульвар, д. 14\n"
        f"<code>{progress_bar(4)}</code>\n\n"
        "Ресторан являлся одним из центров общественной жизни Москвы конца XIX века.\n"
        "Здесь проходили встречи писателей, издателей и актёров.\n\n"
        "В 1897 году именно здесь у Чехова произошёл тяжёлый приступ туберкулёза."
    )
    markup = kb(
        ("💡 Интересный факт", "fact_4"),
        ("💬 Цитата", "quote_4"),
        ("➡️ Следующая остановка", "stop_5"),
        ("🏠 Главное меню", "main_menu"),
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_photo_or_text(call.message.chat.id, "hermitage", caption, markup)

def show_fact_4(call):
    text = (
        "💡 <b>Интересный факт</b>\n\n"
        "С рестораном «Эрмитаж» связано имя Люсьена Оливье — создателя знаменитого салата оливье."
    )
    markup = kb(("⬅️ Назад", "stop_4"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)

def show_quote_4(call):
    text = "💬 <b>Цитата</b>\n\n<i>«В человеке должно быть всё прекрасно».</i>"
    markup = kb(("⬅️ Назад", "stop_4"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)


def show_stop_5(call):
    caption = (
        f"📍 <b>Остановка 5: Московский Художественный театр</b>\n"
        f"Камергерский переулок, д. 3\n"
        f"<code>{progress_bar(5)}</code>\n\n"
        "Сотрудничество Чехова с МХТ стало важным этапом развития русского театра.\n\n"
        "Здесь были поставлены:\n"
        "<i>«Чайка»</i>, <i>«Три сестры»</i>, <i>«Дядя Ваня»</i>, <i>«Вишнёвый сад»</i>."
    )
    markup = kb(
        ("🐦 История «Чайки»", "seagull"),
        ("💬 Цитата", "quote_5"),
        ("➡️ Следующая остановка", "stop_6"),
        ("🏠 Главное меню", "main_menu"),
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_photo_or_text(call.message.chat.id, "mhat", caption, markup)

def show_seagull(call):
    text = (
        "🐦 <b>История «Чайки»</b>\n\n"
        "Первая постановка «Чайки» в Петербурге провалилась.\n\n"
        "Спектакль МХТ в 1898 году изменил отношение публики к пьесе и принёс Чехову театральный успех."
    )
    markup = kb(("⬅️ Назад", "stop_5"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)

def show_quote_5(call):
    text = "💬 <b>Цитата</b>\n\n<i>«Краткость — сестра таланта».</i>"
    markup = kb(("⬅️ Назад", "stop_5"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)


def show_stop_6(call):
    caption = (
        f"📍 <b>Остановка 6: Дом на Малой Дмитровке</b>\n"
        f"ул. Малая Дмитровка, д. 29/15\n"
        f"<code>{progress_bar(6)}</code>\n\n"
        "После возвращения с Сахалина Чехов жил здесь и работал над книгой <i>«Остров Сахалин»</i>.\n\n"
        "Поездка значительно повлияла на взгляды писателя и усилила социальную проблематику его произведений."
    )
    markup = kb(
        ("🏝 О Сахалине", "sakhalin"),
        ("💬 Цитата", "quote_6"),
        ("➡️ Следующая остановка", "stop_7"),
        ("🏠 Главное меню", "main_menu"),
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_photo_or_text(call.message.chat.id, "dmitrovka", caption, markup)

def show_sakhalin(call):
    text = (
        "🏝 <b>О Сахалине</b>\n\n"
        "Во время поездки Чехов провёл перепись населения Сахалина и изучал условия жизни каторжан и ссыльных.\n\n"
        "Результатом исследования стала книга <i>«Остров Сахалин»</i>."
    )
    markup = kb(("⬅️ Назад", "stop_6"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)

def show_quote_6(call):
    text = "💬 <b>Цитата</b>\n\n<i>«Равнодушие — паралич души».</i>"
    markup = kb(("⬅️ Назад", "stop_6"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)


def show_stop_7(call):
    caption = (
        f"📍 <b>Остановка 7: Новодевичье кладбище</b>\n"
        f"Лужнецкий пр-д, вл. 2\n"
        f"<code>{progress_bar(7)}</code>\n\n"
        "Антон Чехов был похоронен в Москве в 1904 году.\n"
        "Проститься с писателем пришли тысячи людей.\n\n"
        "Могила Чехова остаётся одним из главных мемориальных мест русской культуры."
    )
    markup = kb(
        ("💡 Интересный факт", "fact_7"),
        ("✅ Завершить маршрут", "finish"),
        ("🏠 Главное меню", "main_menu"),
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_photo_or_text(call.message.chat.id, "novodevichy", caption, markup)

def show_fact_7(call):
    text = (
        "💡 <b>Интересный факт</b>\n\n"
        "Тело Чехова доставили в Москву в вагоне-рефрижераторе, который использовался для перевозки устриц.\n\n"
        "Эта деталь часто упоминалась современниками в воспоминаниях о похоронах писателя."
    )
    markup = kb(("⬅️ Назад", "stop_7"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)

def show_finish(call):
    text = (
        "✅ <b>Маршрут завершён!</b>\n\n"
        f"<code>{progress_bar(7)}</code>\n\n"
        "Вы прошли по всем ключевым московским адресам Антона Павловича Чехова "
        "и познакомились с культурной средой Москвы конца XIX века.\n\n"
        "Спасибо за использование проекта <b>«Я навсегда москвич»</b>."
    )
    markup = kb(
        ("🎭 Пройти викторину", "quiz_start"),
        ("🏠 Главное меню", "main_menu"),
    )
    edit_or_send(call, text, markup)


# ======================================================
# ВИКТОРИНА — 5 вопросов с очками
# ======================================================

QUIZ_QUESTIONS = [
    {
        "q": "Вопрос 1 из 5:\nНа каком факультете учился Чехов?",
        "options": [("📜 Исторический", False), ("🩺 Медицинский", True), ("⚖️ Юридический", False)],
        "explanation": "Чехов окончил медицинский факультет Московского университета в 1884 году."
    },
    {
        "q": "Вопрос 2 из 5:\nКак называлась пьеса, провал которой в Петербурге стал поводом для постановки в МХТ?",
        "options": [("🐦 Чайка", True), ("🌸 Вишнёвый сад", False), ("👨‍👩‍👧 Три сестры", False)],
        "explanation": "«Чайка» провалилась в Петербурге, но триумфально прошла в МХТ в 1898 году."
    },
    {
        "q": "Вопрос 3 из 5:\nВ каком году состоялось венчание Чехова и Ольги Книппер?",
        "options": [("1895", False), ("1901", True), ("1904", False)],
        "explanation": "Чехов и Книппер обвенчались в 1901 году в Церкви Воздвижения Креста Господня."
    },
    {
        "q": "Вопрос 4 из 5:\nПод каким псевдонимом Чехов публиковал ранние рассказы?",
        "options": [("Антоша Чехонте", True), ("Человек без селезёнки", False), ("Антон Павлов", False)],
        "explanation": "Псевдоним «Антоша Чехонте» Чехов использовал в начале литературной карьеры."
    },
    {
        "q": "Вопрос 5 из 5:\nКуда Чехов отправился в 1890 году, написав затем знаменитую книгу-репортаж?",
        "options": [("На Камчатку", False), ("На Сахалин", True), ("В Сибирь", False)],
        "explanation": "Чехов совершил поездку на Сахалин и написал книгу «Остров Сахалин»."
    },
]

def quiz_cb(q_index, is_correct):
    return f"quiz_ans_{q_index}_{'1' if is_correct else '0'}"

def show_quiz_question(call, q_index, score):
    q = QUIZ_QUESTIONS[q_index]
    text = (
        f"🎭 <b>Викторина «Чеховская Москва»</b>\n"
        f"Счёт: {'⭐' * score}{'·' * (q_index - score)} {score}/{q_index}\n\n"
        f"{q['q']}"
    )
    buttons = [(label, quiz_cb(q_index, correct)) for label, correct in q["options"]]
    buttons.append(("🏠 Выйти из викторины", "main_menu"))
    edit_or_send(call, text, kb(*buttons))

def show_quiz_start(call):
    user_id = call.from_user.id
    quiz_scores[user_id] = 0
    q = QUIZ_QUESTIONS[0]
    text = (
        "🎭 <b>Викторина «Чеховская Москва»</b>\n\n"
        "5 вопросов. За каждый верный ответ — ⭐\n\n"
        f"{q['q']}"
    )
    buttons = [(label, quiz_cb(0, correct)) for label, correct in q["options"]]
    buttons.append(("🏠 Выйти из викторины", "main_menu"))
    edit_or_send(call, text, kb(*buttons))

def handle_quiz_answer(call, q_index, is_correct):
    user_id = call.from_user.id
    if user_id not in quiz_scores:
        quiz_scores[user_id] = 0
    if is_correct:
        quiz_scores[user_id] += 1

    score = quiz_scores[user_id]
    q = QUIZ_QUESTIONS[q_index]
    result_emoji = "✅" if is_correct else "❌"
    result_word = "Верно!" if is_correct else "Неверно."
    next_index = q_index + 1

    if next_index < len(QUIZ_QUESTIONS):
        text = (
            f"{result_emoji} <b>{result_word}</b>\n"
            f"<i>{q['explanation']}</i>\n\n"
            f"Счёт: {'⭐' * score}{'·' * (next_index - score)} {score}/{next_index}"
        )
        markup = kb((f"➡️ Вопрос {next_index + 1}", f"quiz_next_{next_index}_{score}"))
        edit_or_send(call, text, markup)
    else:
        total = len(QUIZ_QUESTIONS)
        stars = "⭐" * score
        if score == total:
            verdict = "🏆 Блестяще! Вы настоящий знаток Чехова!"
        elif score >= 3:
            verdict = "👏 Хороший результат! Вы хорошо знаете Чехова."
        elif score >= 1:
            verdict = "📖 Неплохо! Пройдите маршрут, чтобы узнать больше."
        else:
            verdict = "🗺 Советуем пройти маршрут — там много интересного!"

        text = (
            f"{result_emoji} <b>{result_word}</b>\n"
            f"<i>{q['explanation']}</i>\n\n"
            f"🎭 <b>Викторина завершена!</b>\n\n"
            f"Ваш результат: {stars} <b>{score} из {total}</b>\n\n"
            f"{verdict}"
        )
        markup = kb(
            ("🔄 Пройти ещё раз", "quiz_start"),
            ("🏠 Главное меню", "main_menu"),
        )
        edit_or_send(call, text, markup)


# ======================================================
# ИНТЕРЕСНЫЕ ФАКТЫ
# ======================================================

def show_facts_menu(call):
    text = "💡 <b>Интересные факты</b>\n\nВыберите тему:"
    markup = kb(
        ("🏙 Москва XIX века", "fact_moscow"),
        ("🎭 Театры", "fact_theatres"),
        ("🍽 Рестораны", "fact_restaurants"),
        ("🎓 Студенты", "fact_students"),
        ("🚃 Транспорт", "fact_transport"),
        ("🏠 Главное меню", "main_menu"),
    )
    edit_or_send(call, text, markup)

def show_fact_moscow(call):
    text = (
        "🏙 <b>Москва XIX века</b>\n\n"
        "Во второй половине XIX века Москва быстро росла.\n\n"
        "Развивались университеты, театры, издательства и система общественного транспорта.\n\n"
        "Город становился одним из главных культурных центров Российской империи."
    )
    markup = kb(("⬅️ Назад", "facts_menu"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)

def show_fact_theatres(call):
    text = (
        "🎭 <b>Театры Москвы</b>\n\n"
        "В конце XIX века в Москве действовали Малый театр, Большой театр и МХТ.\n\n"
        "МХТ, основанный Станиславским и Немировичем-Данченко в 1898 году, "
        "стал революционной площадкой — именно здесь была впервые успешно поставлена «Чайка» Чехова."
    )
    markup = kb(("⬅️ Назад", "facts_menu"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)

def show_fact_restaurants(call):
    text = (
        "🍽 <b>Рестораны Москвы</b>\n\n"
        "Рестораны конца XIX века были важными центрами культурной и деловой жизни.\n\n"
        "Ресторан «Эрмитаж» на Петровском бульваре был особенно популярен среди литераторов и актёров. "
        "Именно здесь впервые появился знаменитый салат оливье."
    )
    markup = kb(("⬅️ Назад", "facts_menu"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)

def show_fact_students(call):
    text = (
        "🎓 <b>Студенты Москвы</b>\n\n"
        "Московский университет был одним из главных центров интеллектуальной жизни страны.\n\n"
        "Многие студенты, как и Чехов, совмещали учёбу с подработкой — "
        "писали для газет и журналов."
    )
    markup = kb(("⬅️ Назад", "facts_menu"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)

def show_fact_transport(call):
    text = (
        "🚃 <b>Транспорт Москвы</b>\n\n"
        "В 1880-е годы по московским улицам ходила конка — предшественник трамвая.\n\n"
        "В 1899 году в Москве появился первый электрический трамвай. "
        "Железная дорога связывала Москву с другими городами — "
        "именно по ней Чехов путешествовал на Сахалин."
    )
    markup = kb(("⬅️ Назад", "facts_menu"), ("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)


# ======================================================
# ИСТОЧНИКИ
# ======================================================

def show_sources(call):
    text = (
        "📚 <b>Источники проекта</b>\n\n"
        "- Письма А.П. Чехова\n"
        "— Воспоминания современников\n"
        "— Исследования по истории Москвы\n"
        "— Материалы МХТ\n"
        "— Биографии Чехова"
    )
    markup = kb(("🏠 Главное меню", "main_menu"))
    edit_or_send(call, text, markup)


# ======================================================
# ГЛАВНЫЙ ОБРАБОТЧИК CALLBACK
# ======================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    bot.answer_callback_query(call.id)
    d = call.data

    if d == "main_menu":
        show_main_menu(call.message.chat.id, call.message.message_id)
    elif d == "map":            show_map(call)
    elif d == "about":          show_about(call)
    elif d == "biography":      show_biography(call)
    elif d == "medicine":       show_medicine(call)
    elif d in ("theatre", "theatre_about"): show_theatre_about(call)
    elif d == "route_menu":     show_route_menu(call)
    elif d == "weather":        show_weather(call)
    elif d == "sources":        show_sources(call)

    elif d == "stop_1":  show_stop_1(call)
    elif d == "fact_1":  show_fact_1(call)
    elif d == "quote_1": show_quote_1(call)

    elif d == "stop_2":  show_stop_2(call)
    elif d == "guests":  show_guests(call)
    elif d == "quote_2": show_quote_2(call)

    elif d == "stop_3":  show_stop_3(call)
    elif d == "fact_3":  show_fact_3(call)
    elif d == "quote_3": show_quote_3(call)

    elif d == "stop_4":  show_stop_4(call)
    elif d == "fact_4":  show_fact_4(call)
    elif d == "quote_4": show_quote_4(call)

    elif d == "stop_5":   show_stop_5(call)
    elif d == "seagull":  show_seagull(call)
    elif d == "quote_5":  show_quote_5(call)

    elif d == "stop_6":   show_stop_6(call)
    elif d == "sakhalin": show_sakhalin(call)
    elif d == "quote_6":  show_quote_6(call)

    elif d == "stop_7": show_stop_7(call)
    elif d == "fact_7": show_fact_7(call)
    elif d == "finish": show_finish(call)

    elif d == "quiz_start":
        show_quiz_start(call)
    elif d.startswith("quiz_ans_"):
        # Формат: quiz_ans_НОМЕРВОПРОСА_0или1
        parts = d.split("_")
        q_index = int(parts[2])
        is_correct = parts[3] == "1"
        handle_quiz_answer(call, q_index, is_correct)
    elif d.startswith("quiz_next_"):
        # Формат: quiz_next_НОМЕРВОПРОСА_СЧЁТ
        parts = d.split("_")
        q_index = int(parts[2])
        score = int(parts[3])
        quiz_scores[call.from_user.id] = score
        show_quiz_question(call, q_index, score)

    elif d == "facts_menu":       show_facts_menu(call)
    elif d == "fact_moscow":      show_fact_moscow(call)
    elif d == "fact_theatres":    show_fact_theatres(call)
    elif d == "fact_restaurants": show_fact_restaurants(call)
    elif d == "fact_students":    show_fact_students(call)
    elif d == "fact_transport":   show_fact_transport(call)


# ======================================================
# ЗАПУСК
# ======================================================

if __name__ == "__main__":
    print("✅ Бот запущен. Нажмите Ctrl+C для остановки.")
    bot.infinity_polling()
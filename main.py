import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- KONFIGURATSIYA ---
TOKEN = "8185440589:AAH-QOBqKunLzLQvYmhGt8osUOKXeR4gd8E"
ADMIN_ID = 8239382195
CARD_NUMBER = "9860 1966 0027 8234"
ADMIN_USERNAME = "@kvonyeon"
CHANNEL_LINK = "@zar_isbot"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- BAZA BILAN ISHLASH (Xabar tarqatish uchun) ---
db = sqlite3.connect("users.db")
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
db.commit()

class Order(StatesGroup):
    lang = State()
    section = State()
    waiting_for_topic = State()
    waiting_for_pages = State()
    waiting_for_desc = State()
    waiting_for_payment = State()
    waiting_for_broadcast = State()

# --- MATNLAR ---
MESSAGES = {
    'uz': {
        'start': "Assalomu alaykum! Tilni tanlang / Выберите язык / Select language:",
        'menu': "Bo'limni tanlang:",
        'topic': "Mavzu nima haqida?",
        'pages': "Necha varaq bo'lishi kerak?",
        'it_ask': "Qanday maqsadda yaratmoqchisiz?",
        'it_resp': "Yaqin orada admin sizga shaxsiy xabarda javob beradi!",
        'tech_ask': "Qanday muammoingiz bor?",
        'tech_resp': "Admin tez orada javob beradi!",
        'pay_info': "💰 <b>Narxi: {price} so'm</b>\n\n💳 Karta: <code>{card}</code>\n\nTo'lovni qiling va skrinshotni yuboring.\n\n📚 Namunalar: {channel}\n👨‍💻 Admin: {admin}",
        'done': "Skrinshot qabul qilindi! ✅ Admin tasdiqlashi bilan loyihangiz boshlanadi.",
        'btns': ["📊 Prezentatsiya", "📚 Kurs ishi / Mustaqil ish", "🤖 Bot yaratish", "🌐 Sayt yaratish", "🛠 PK/Tel yordam", "👨‍💻 Admin bilan aloqa"]
    },
    'ru': {
        'start': "Здравствуйте! Выберите язык / Select language:",
        'menu': "Выберите раздел:",
        'topic': "На какую тему работа?",
        'pages': "Сколько листов нужно?",
        'it_ask': "Для каких целей вы хотите создать?",
        'it_resp': "В ближайшее время админ ответит вам в личные сообщения!",
        'tech_ask': "Какая у вас проблема?",
        'tech_resp': "Админ ответит вам скоро!",
        'pay_info': "💰 <b>Стоимость: {price} сум</b>\n\n💳 Карта: <code>{card}</code>\n\nПополните баланс и отправьте скриншот сюда.\n\n📚 Канал доверия: {channel}\n👨‍💻 Admin: {admin}",
        'done': "Скриншот принят! ✅ Когда админ подтвердит его, мы начнем ваш проект.",
        'btns': ["📊 Презентация", "📚 Курсовая / Самостоятельная", "🤖 Создать бота", "🌐 Создать сайт", "🛠 Помощь ПК/Тел", "👨‍💻 Связь с админом"]
    },
    'en': {
        'start': "Welcome! Select language:",
        'menu': "Select a section:",
        'topic': "What is the topic?",
        'pages': "How many pages?",
        'it_ask': "For what purposes do you want to create it?",
        'it_resp': "Admin will contact you shortly!",
        'tech_ask': "What is your problem?",
        'tech_resp': "Admin will answer you soon!",
        'pay_info': "💰 <b>Price: {price} UZS</b>\n\n💳 Card: <code>{card}</code>\n\nPlease pay and send the screenshot here.\n\n📚 Proofs: {channel}\n👨‍💻 Admin: {admin}",
        'done': "Screenshot received! ✅ Admin will start the project after confirmation.",
        'btns': ["📊 Presentation", "📚 Coursework / Independent work", "🤖 Create a Bot", "🌐 Create a Website", "🛠 PC/Phone Help", "👨‍💻 Contact Admin"]
    }
}

# --- KLAVIATURALAR ---
def get_lang_kb():
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="🇺🇿 O'zbekcha"), types.KeyboardButton(text="🇷🇺 Русский"), types.KeyboardButton(text="🇬🇧 English")]], resize_keyboard=True)

def get_menu_kb(lang):
    b = MESSAGES[lang]['btns']
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text=b[0]), types.KeyboardButton(text=b[1])],[types.KeyboardButton(text=b[2]), types.KeyboardButton(text=b[3])],[types.KeyboardButton(text=b[4]), types.KeyboardButton(text=b[5])]], resize_keyboard=True)

# --- BROADCAST (ADMIN UCHUN) ---
@dp.message(Command("send_all"), F.from_user.id == ADMIN_ID)
async def start_broadcast(m: types.Message, state: FSMContext):
    await m.answer("Barcha foydalanuvchilarga yuboriladigan xabarni yozing:")
    await state.set_state(Order.waiting_for_broadcast)

@dp.message(Order.waiting_for_broadcast, F.from_user.id == ADMIN_ID)
async def do_broadcast(m: types.Message, state: FSMContext):
    cur.execute("SELECT id FROM users")
    users = cur.fetchall()
    count = 0
    for user in users:
        try:
            await bot.send_message(user[0], m.text)
            count += 1
        except: continue
    await m.answer(f"Xabar {count} ta foydalanuvchiga yuborildi! ✅")
    await state.clear()

# --- ASOSIY LOGIKA ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message, state: FSMContext):
    cur.execute("INSERT OR IGNORE INTO users VALUES (?)", (m.from_user.id,))
    db.commit()
    await state.clear()
    await m.answer(MESSAGES['uz']['start'], reply_markup=get_lang_kb())

@dp.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English"]))
async def set_lang(m: types.Message, state: FSMContext):
    l = 'uz' if "O'z" in m.text else 'ru' if "Рус" in m.text else 'en'
    await state.update_data(lang=l)
    await m.answer(MESSAGES[l]['menu'], reply_markup=get_menu_kb(l))

@dp.message(lambda m: any(m.text in MESSAGES[l]['btns'] for l in MESSAGES))
async def handle_menu(m: types.Message, state: FSMContext):
    data = await state.get_data()
    l = data.get('lang', 'ru')
    btn = m.text
    
    # Har bir til uchun tugmalarni to'g'ri tekshirish
    if btn in [MESSAGES['uz']['btns'][0], MESSAGES['ru']['btns'][0], MESSAGES['en']['btns'][0]]: # Pres
        await state.update_data(section=btn, price=15000)
        await m.answer(MESSAGES[l]['topic'])
        await state.set_state(Order.waiting_for_topic)
    elif btn in [MESSAGES['uz']['btns'][1], MESSAGES['ru']['btns'][1], MESSAGES['en']['btns'][1]]: # Kurs
        await state.update_data(section=btn, price=20000)
        await m.answer(MESSAGES[l]['topic'])
        await state.set_state(Order.waiting_for_topic)
    elif btn in [MESSAGES['uz']['btns'][2], MESSAGES['ru']['btns'][2], MESSAGES['en']['btns'][2],
                MESSAGES['uz']['btns'][3], MESSAGES['ru']['btns'][3], MESSAGES['en']['btns'][3],
                MESSAGES['uz']['btns'][4], MESSAGES['ru']['btns'][4], MESSAGES['en']['btns'][4]]: # IT / Tech
        await state.update_data(section=btn)
        is_it = "Bot" in btn or "Sayt" in btn or "Web" in btn or "🤖" in btn or "🌐" in btn
        q = MESSAGES[l]['it_ask'] if is_it else MESSAGES[l]['tech_ask']
        await m.answer(q)
        await state.set_state(Order.waiting_for_desc)
    else: # Admin
        await m.answer(f"👨‍💻 Admin bilan bog'lanish: {ADMIN_USERNAME}")

@dp.message(Order.waiting_for_topic)
async def get_topic(m: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(topic=m.text)
    await m.answer(MESSAGES[data['lang']]['pages'])
    await state.set_state(Order.waiting_for_pages)

@dp.message(Order.waiting_for_pages)
async def get_pages(m: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(pages=m.text)
    txt = MESSAGES[data['lang']]['pay_info'].format(price=data['price'], card=CARD_NUMBER, channel=CHANNEL_LINK, admin=ADMIN_USERNAME)
    await m.answer(txt, parse_mode="HTML")
    await state.set_state(Order.waiting_for_payment)

@dp.message(Order.waiting_for_desc)
async def get_desc(m: types.Message, state: FSMContext):
    data = await state.get_data()
    l = data['lang']
    user = f"@{m.from_user.username}" if m.from_user.username else f"ID: {m.from_user.id}"
    await bot.send_message(ADMIN_ID, f"📩 <b>YANGI SO'ROV:</b>\nBo'lim: {data['section']}\nMijoz: {user}\nMa'lumot: {m.text}", parse_mode="HTML")
    is_it = "Bot" in data['section'] or "Sayt" in data['section'] or "Web" in data['section'] or "🤖" in data['section'] or "🌐" in data['section']
    await m.answer(MESSAGES[l]['it_resp'] if is_it else MESSAGES[l]['tech_resp'])
    await state.clear()

@dp.message(Order.waiting_for_payment, F.photo)
async def get_pay(m: types.Message, state: FSMContext):
    data = await state.get_data()
    user = f"@{m.from_user.username}" if m.from_user.username else f"ID: {m.from_user.id}"
    caption = f"🔥 <b>YANGI TO'LOV!</b>\n\nTur: {data['section']}\nMavzu: {data['topic']}\nVaraq: {data['pages']}\nNarx: {data['price']} so'm\nMijoz: {user}"
    await bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=caption, parse_mode="HTML")
    await m.answer(MESSAGES[data['lang']]['done'])
    await state.clear()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

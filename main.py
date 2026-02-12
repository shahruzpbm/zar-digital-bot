import asyncio
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

class Order(StatesGroup):
    lang = State()
    section = State()
    waiting_for_topic = State()
    waiting_for_pages = State()
    waiting_for_desc = State()
    waiting_for_payment = State()

# --- MATNLAR VA NARXLAR ---
MESSAGES = {
    'uz': {
        'start': "Assalomu alaykum! Tilni tanlang:",
        'menu': "Bo'limni tanlang:",
        'topic': "Mavzu nima haqida?",
        'pages': "Necha varaq bo'lishi kerak?",
        'it_desc': "Bot yoki Saytni qanday maqsadda yaratmoqchisiz?",
        'it_resp': "Yaqin orada admin sizga shaxsiy xabarda javob beradi!",
        'tech_desc': "Muammoingiz nimadan iborat?",
        'tech_resp': "Admin tez orada sizga javob beradi!",
        'payment': "💰 <b>To'lov: {price} so'm</b>\n\nKarta: <code>{card}</code>\n\nTo'lovni amalga oshiring va skrinshotni yuboring. Buyurtma tasdiqlangach, loyihangiz boshlanadi.\n\n📚 Namunalar: {channel}\n👨‍💻 Admin: {admin}",
        'screenshot_received': "Skrinshot qabul qilindi! ✅ Admin tasdiqlashi bilan loyihani boshlaymiz.",
        'sections': ["📊 Prezentatsiya", "📚 Kurs ishi / Mustaqil ish", "🤖 Bot yaratish", "🌐 Sayt yaratish", "🛠 PK/Tel yordam", "👨‍💻 Admin bilan bog'lanish"]
    },
    'ru': {
        'start': "Здравствуйте! Выберите язык:",
        'menu': "Выберите раздел:",
        'topic': "Какая тема работы?",
        'pages': "Сколько листов нужно?",
        'it_desc': "Для каких целей вы хотите создать Бота или Сайт?",
        'it_resp': "В ближайшее время админ ответит вам в личные сообщения!",
        'tech_desc': "Какая у вас проблема?",
        'tech_resp': "Админ ответит вам скоро!",
        'payment': "💰 <b>К оплате: {price} сум</b>\n\nКарта: <code>{card}</code>\n\nПополните баланс и отправьте скриншот сюда. После подтверждения мы начнем ваш проект.\n\n📚 Канал доверия: {channel}\n👨‍💻 Админ: {admin}",
        'screenshot_received': "Скриншот принят! ✅ Когда админ подтвердит его, мы начнем ваш проект.",
        'sections': ["📊 Презентация", "📚 Курсовая / Самостоятельная", "🤖 Создать бота", "🌐 Создать сайт", "🛠 Помощь ПК/Тел", "👨‍💻 Связь с админом"]
    },
    'en': {
        'start': "Welcome! Select language:",
        'menu': "Choose a section:",
        'topic': "What is the topic?",
        'pages': "How many pages?",
        'it_desc': "For what purposes do you want to create a Bot or Website?",
        'it_resp': "Admin will contact you shortly!",
        'tech_desc': "Describe your problem:",
        'tech_resp': "Admin will answer you soon!",
        'payment': "💰 <b>Price: {price} UZS</b>\n\nCard: <code>{card}</code>\n\nPlease pay and send a screenshot here. We will start your project after confirmation.\n\n📚 Proofs: {channel}\n👨‍💻 Admin: {admin}",
        'screenshot_received': "Screenshot received! ✅ Admin will notify you and we will start the project.",
        'sections': ["📊 Presentation", "📚 Coursework / Independent work", "🤖 Create a Bot", "🌐 Create a Website", "🛠 PC/Phone Help", "👨‍💻 Contact Admin"]
    }
}

def lang_kb():
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="🇺🇿 O'zbekcha"), types.KeyboardButton(text="🇷🇺 Русский"), types.KeyboardButton(text="🇬🇧 English")]], resize_keyboard=True)

def main_menu(lang):
    sections = MESSAGES[lang]['sections']
    return types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text=sections[0]), types.KeyboardButton(text=sections[1])],
        [types.KeyboardButton(text=sections[2]), types.KeyboardButton(text=sections[3])],
        [types.KeyboardButton(text=sections[4]), types.KeyboardButton(text=sections[5])]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer(MESSAGES['ru']['start'], reply_markup=lang_kb())

@dp.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English"]))
async def set_lang(m: types.Message, state: FSMContext):
    lang = 'uz' if "O'z" in m.text else 'ru' if "Рус" in m.text else 'en'
    await state.update_data(lang=lang)
    await m.answer(MESSAGES[lang]['menu'], reply_markup=main_menu(lang))

@dp.message(lambda m: any(m.text in MESSAGES[l]['sections'] for l in MESSAGES))
async def handle_sections(m: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    sec = m.text
    if sec in [MESSAGES[lang]['sections'][0], MESSAGES[lang]['sections'][1]]:
        price = 15000 if sec == MESSAGES[lang]['sections'][0] else 20000
        await state.update_data(section=sec, price=price)
        await m.answer(MESSAGES[lang]['topic'])
        await state.set_state(Order.waiting_for_topic)
    elif sec in [MESSAGES[lang]['sections'][2], MESSAGES[lang]['sections'][3]]:
        await state.update_data(section=sec)
        await m.answer(MESSAGES[lang]['it_desc'])
        await state.set_state(Order.waiting_for_desc)
    elif sec == MESSAGES[lang]['sections'][4]:
        await state.update_data(section=sec)
        await m.answer(MESSAGES[lang]['tech_desc'])
        await state.set_state(Order.waiting_for_desc)
    else:
        await m.answer(f"Admin: {ADMIN_USERNAME}")

@dp.message(Order.waiting_for_topic)
async def get_topic(m: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(topic=m.text)
    await m.answer(MESSAGES[data['lang']]['pages'])
    await state.set_state(Order.waiting_for_pages)

@dp.message(Order.waiting_for_pages)
async def get_pages(m: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    await state.update_data(pages=m.text)
    txt = MESSAGES[lang]['payment'].format(price=data['price'], card=CARD_NUMBER, channel=CHANNEL_LINK, admin=ADMIN_USERNAME)
    await m.answer(txt, parse_mode="HTML") # Заменили Markdown на HTML
    await state.set_state(Order.waiting_for_payment)

@dp.message(Order.waiting_for_desc)
async def get_desc(m: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    admin_info = f"📩 <b>SO'ROV: {data['section']}</b>\nMaqsad: {m.text}\nMijoz: @{m.from_user.username}"
    await bot.send_message(ADMIN_ID, admin_info, parse_mode="HTML")
    resp = MESSAGES[lang]['it_resp'] if "Bot" in data['section'] or "Sayt" in data['section'] else MESSAGES[lang]['tech_resp']
    await m.answer(resp)
    await state.clear()

@dp.message(Order.waiting_for_payment, F.photo)
async def get_screenshot(m: types.Message, state: FSMContext):
    data = await state.get_data()
    username = f"@{m.from_user.username}" if m.from_user.username else "No Username"
    info = (f"🔥 <b>YANGI BUYURTMA!</b>\n\n"
            f"Turi: {data['section']}\n"
            f"Mavzu: {data['topic']}\n"
            f"Varaqlar: {data['pages']}\n"
            f"Narxi: {data['price']} so'm\n"
            f"Mijoz: {username}")
    await bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=info, parse_mode="HTML")
    await m.answer(MESSAGES[data['lang']]['screenshot_received'])
    await state.clear()

async def main():
    await bot.delete_webhook(drop_pending_updates=True) # Очистка старых сообщений
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS").split(",")))
GROUP_ID = int(os.getenv("GROUP_ID"))

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

# === Xizmatlar tugmalari ===
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("🕋 Umra Paketlari", "🛂 Saudiya Vizasi")
main_menu.add("🎫 Rawdah/Tasreh", "🏨 Hotel/Hostel")
main_menu.add("🚌 Transport", "🚄 HHR Poyezdi")
main_menu.add("✈️ Aviabiletlar", "🍱 Guruh Ovqatlari")
main_menu.add("❤️ Xayriya qilish")

# === To‘lov paneli ===
payment_panel = InlineKeyboardMarkup(row_width=1)
payment_panel.add(
    InlineKeyboardButton("💳 Uzcard", callback_data="pay_uzcard"),
    InlineKeyboardButton("💳 Humo", callback_data="pay_humo"),
    InlineKeyboardButton("💳 Visa/MasterCard", callback_data="pay_visa"),
    InlineKeyboardButton("🪙 Crypto (USDT/BTC)", callback_data="pay_crypto")
)

# === Statega o‘tishlar ===
class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_people = State()
    waiting_for_details = State()
    waiting_for_payment = State()

# === /start komandasi ===
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user = message.from_user.full_name
    await message.answer(
        f"Assalomu alaykum, <b>{user}</b>! 👋\n\n"
        "Bu — <b>UmraJet</b> botiga xush kelibsiz!\n"
        "Premium Umra xizmatlari va qulay buyurtmalar uchun mo‘ljallangan.\n\n"
        "Quyidagi menyudan kerakli xizmatni tanlang. 👇",
        reply_markup=main_menu
    )

# === Umra Paketlari ===
@dp.message_handler(lambda msg: msg.text == "🕋 Umra Paketlari")
async def umra_packages(message: types.Message):
    await message.answer(
        "<b>🕋 Umra Paketlari</b>\n\n"
        "1. <b>Standart paket</b> — <i>$1200 dan boshlab</i>\n"
        "   ✅ Vizali/Vizasiz variantlar\n"
        "   ✅ Econom hotel, transport, ovqatlar\n\n"
        "2. <b>VIP paket</b> — <i>$1800 dan boshlab</i>\n"
        "   🌟 Markazdagi 5⭐ hotel\n"
        "   🧑‍✈️ Shaxsiy kuzatuvchilar\n"
        "   🍽 To‘liq ovqatlanish va qulayliklar\n\n"
        "📌 To‘liq ma’lumot va buyurtma uchun pastdagi tugmadan foydalaning.",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("📥 Buyurtma berish", callback_data="order_umra")
        )
    )

# === Saudiya Vizasi ===
@dp.message_handler(lambda msg: msg.text == "🛂 Saudiya Vizasi")
async def saudi_visa(message: types.Message):
    await message.answer(
        "<b>🛂 Saudiya vizalari</b>\n\n"
        "1. <b>Umra Vizasi</b> — <i>$160</i>\n"
        "2. <b>Turistik Vizasi</b> — <i>$120</i>\n\n"
        "🧑‍💻 Guruhlar uchun chegirmalar mavjud!\n\n"
        "Vizani rasmiylashtirish uchun pasport fotosurati va shaxsiy ma’lumotlar kerak bo‘ladi.\n\n"
        "Quyidagi tugma orqali buyurtma bering:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("📥 Vizaga buyurtma", callback_data="order_visa")
        )
    )

# === Rawdah/Tasreh ===
@dp.message_handler(lambda msg: msg.text == "🎫 Rawdah/Tasreh")
async def rawdah_tasreh(message: types.Message):
    await message.answer(
        "<b>🎫 Rawdah Tasreh (ziyolat uchun ruxsatnoma)</b>\n\n"
        "🔹 <b>Viza bilan:</b> 15 SAR / kishi\n"
        "🔹 <b>Vizasiz:</b> 20 SAR / kishi\n\n"
        "👥 Ko‘p kishilik yoki doimiy mijozlarga chegirma mumkin.\n\n"
        "📅 Sanani, ismni va kishilar sonini yuboring.\n\n"
        "Buyurtma uchun tugmani bosing:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("📥 Tasrehga buyurtma", callback_data="order_tasreh")
        )
    )

# === Hotel/Hostel ===
@dp.message_handler(lambda msg: msg.text == "🏨 Hotel/Hostel")
async def hotel_booking(message: types.Message):
    await message.answer(
        "<b>🏨 Hotel va Hostel bron qilish</b>\n\n"
        "📍 Makkah va Madinahdagi joylar\n"
        "⭐ 2-5 yulduzli variantlar\n"
        "🛏 Hostel, apartament va oilaviy xona variantlari mavjud\n\n"
        "Narxlar kun va joyga qarab farq qiladi.\n\n"
        "Buyurtma berish uchun quyidagi tugmani bosing:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("📥 Hotel bron qilish", callback_data="order_hotel")
        )
    )

# === Transport Xizmatlari ===
@dp.message_handler(lambda msg: msg.text == "🚗 Transport Xizmati")
async def transport_service(message: types.Message):
    await message.answer(
        "<b>🚗 Transport xizmatlari</b>\n\n"
        "• Makkah ↔ Madinah — har xil klassdagi avtolar\n"
        "• Jidda aeroportidan kutib olish\n"
        "• VIP va oddiy variantlar mavjud\n"
        "• Narx: marshrut va avto turiga qarab farq qiladi\n\n"
        "📞 Tezda buyurtma uchun tugmani bosing:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("📥 Transport buyurtma", callback_data="order_transport")
        )
    )

# === Poyezd Chiptalari (HHR) ===
@dp.message_handler(lambda msg: msg.text == "🚄 Poyezd Chiptalari (HHR)")
async def train_tickets(message: types.Message):
    await message.answer(
        "<b>🚄 HHR Poyezd chiptalari</b>\n\n"
        "🛤 Yo‘nalishlar:\n"
        "   • Madinah ↔ Makka\n"
        "   • Riyadh ↔ Dammam\n"
        "   • Jeddah ↔ Makkah\n\n"
        "🎟 Narxlar yo‘nalish va vaqtga qarab o‘zgaradi\n"
        "📅 Chiptalar oldindan bron qilinadi\n\n"
        "Buyurtma uchun quyidagi tugmani bosing:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("📥 Chipta olish", callback_data="order_train")
        )
    )

# === Avia Chiptalar ===
@dp.message_handler(lambda msg: msg.text == "✈️ Avia Chiptalar")
async def flight_booking(message: types.Message):
    await message.answer(
        "<b>✈️ Avia chipta bron qilish</b>\n\n"
        "🌐 Istalgan yo‘nalish uchun avia chiptalar:\n"
        "   • Saudiya → O‘zbekiston\n"
        "   • O‘zbekiston → Saudiya\n\n"
        "🛫 Uchish sanasi va yo‘nalishni yozib yuboring.\n\n"
        "Buyurtma uchun tugmani bosing:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("📥 Avia chipta olish", callback_data="order_flight")
        )
    )

# === Guruh Ovqatlar ===
@dp.message_handler(lambda msg: msg.text == "🍽 Guruh Ovqatlar")
async def group_meals(message: types.Message):
    await message.answer(
        "<b>🍽 Guruh ovqatlar (catering)</b>\n\n"
        "👨‍👩‍👧‍👦 Guruh, ziyoratchilar yoki tadbirlar uchun maxsus ovqat yetkazib berish\n"
        "🥘 Turk, O‘zbek, Arab taomlari\n"
        "📦 To‘liq paketlar (nonushta, tushlik, kechki ovqat)\n\n"
        "Narxlar shartga qarab kelishiladi.\n\n"
        "Buyurtma uchun tugmani bosing:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("📥 Ovqat buyurtma", callback_data="order_meals")
        )
    )

# === Xayriya/Donatsiya ===
@dp.message_handler(lambda msg: msg.text == "❤️ Xayriya qilish")
async def donate(message: types.Message):
    await message.answer(
        "<b>❤️ Xayriya qilish</b>\n\n"
        "Agar UmraJet orqali xayriya qilmoqchi bo‘lsangiz, biz orqali:\n"
        "• Ovqat ulashish\n"
        "• Masjidlar uchun yordam\n"
        "• Haj/Umra qilolmaydiganlarga yordam loyihalari\n\n"
        "📨 Hohlagan summani va maqsadni yozib yuboring\n"
        "yoki quyidagi tugma orqali bog‘laning:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("📥 Xayriya qilish", callback_data="order_donation")
        )
    )

# === FSM order state (universal) ===
class OrderFSM(StatesGroup):
    waiting_for_info = State()

# === Har bir xizmat uchun callback bosilganda FSM boshlanadi ===

@dp.callback_query_handler(lambda c: c.data.startswith("order_"))
async def handle_order_callback(call: types.CallbackQuery, state: FSMContext):
    service = call.data.replace("order_", "")
    await state.update_data(service=service)
    await call.message.edit_text(
        f"📋 <b>{service.replace('_', ' ').capitalize()}</b> xizmatiga buyurtma berish\n\n"
        "✍️ Iltimos, kerakli ma'lumotlarni to‘liq yozing:\n"
        "Ism, sana, odam soni, yo‘nalish, qo‘shimcha izoh...",
        parse_mode="HTML"
    )
    await OrderFSM.waiting_for_info.set()

@dp.message_handler(state=OrderFSM.waiting_for_info)
async def collect_order_info(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    service = user_data.get("service", "xizmat")
    order_text = message.text

    payment_kb = InlineKeyboardMarkup(row_width=2)
    payment_kb.add(
        InlineKeyboardButton("💳 Uzcard", callback_data="pay_uzcard"),
        InlineKeyboardButton("💳 Humo", callback_data="pay_humo"),
        InlineKeyboardButton("💳 Visa", callback_data="pay_visa"),
        InlineKeyboardButton("💸 Crypto", callback_data="pay_crypto")
    )

    await message.answer(
        f"✅ <b>Buyurtma qabul qilindi!</b>\n\n"
        f"🛎 <b>Xizmat:</b> {service.replace('_', ' ').capitalize()}\n"
        f"📝 <b>Buyurtma tafsilotlari:</b>\n{order_text}\n\n"
        f"💰 <b>To‘lov usulini tanlang:</b>",
        reply_markup=payment_kb,
        parse_mode="HTML"
    )

    # Send to managers
    managers = ["@vip_arabiy", "@V001VB"]
    for manager in managers:
        try:
            await bot.send_message(
                manager,
                f"📥 <b>Yangi buyurtma!</b>\n\n"
                f"👤 <b>Foydalanuvchi:</b> @{message.from_user.username or message.from_user.full_name}\n"
                f"🛎 <b>Xizmat:</b> {service.replace('_', ' ').capitalize()}\n"
                f"📝 <b>Ma'lumot:</b>\n{order_text}",
                parse_mode="HTML"
            )
        except:
            pass

    await state.finish()

# === To‘lov tugmalari ===

@dp.callback_query_handler(lambda c: c.data.startswith("pay_"))
async def handle_payment_options(call: types.CallbackQuery):
    method = call.data.replace("pay_", "")
    if method == "uzcard":
        text = "<b>💳 Uzcard orqali to‘lov</b>\n\nKarta: <code>8600 1234 5678 9012</code>\nIsm: ABROR\n\nTo‘lovdan so‘ng kvitansiyani yuboring ✅"
    elif method == "humo":
        text = "<b>💳 HUMO orqali to‘lov</b>\n\nKarta: <code>9860 1234 5678 9012</code>\nIsm: ABROR\n\nTo‘lovdan so‘ng screenshot yuboring 📸"
    elif method == "visa":
        text = "<b>💳 VISA orqali to‘lov</b>\n\nCard: <code>4000 1234 5678 9012</code>\nName: ABROR GLOBAL\n\nTo‘lov tasdiqlangach aloqa qilamiz."
    elif method == "crypto":
        text = "<b>💸 Crypto orqali to‘lov</b>\n\nUSDT (TRC20): <code>TVN...XYZ12</code>\n\nIzoh bilan to‘lov qiling, so‘ng screenshot yuboring ✅"
    else:
        text = "❗ To‘lov usuli topilmadi."

    await call.message.edit_text(text, parse_mode="HTML")


# === Admin panel ===
from datetime import datetime

admin_ids = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

@dp.message_handler(commands=["admin"])
async def admin_panel(message: types.Message):
    if message.from_user.id not in admin_ids:
        return await message.reply("❌ Sizga bu bo‘limga ruxsat yo‘q.")

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Statistika", callback_data="admin_stats"),
        InlineKeyboardButton("💵 Donatsiyalar", callback_data="admin_donations")
    )
    await message.answer("🔐 <b>Admin paneliga xush kelibsiz.</b>", reply_markup=kb, parse_mode="HTML")


# === Statistika tugmasi ===
@dp.callback_query_handler(lambda c: c.data == "admin_stats")
async def show_stats(call: types.CallbackQuery):
    # Faqat bugungi statistika (mock qilingan)
    now = datetime.now().strftime("%d-%m-%Y")
    await call.message.edit_text(
        f"📊 <b>Statistika — {now}</b>\n\n"
        f"🧾 Buyurtmalar: <b>15 ta</b>\n"
        f"💰 Umumiy tushum: <b>$2,400</b>\n"
        f"📈 Eng ko‘p xizmat: <b>Umra vizasi</b>",
        parse_mode="HTML"
    )


# === Donatsiyalar bo‘limi ===
@dp.callback_query_handler(lambda c: c.data == "admin_donations")
async def show_donations(call: types.CallbackQuery):
    await call.message.edit_text(
        "🙏 <b>Botni qo‘llab-quvvatlash uchun donatsiya qiling:</b>\n\n"
        "💳 Uzcard: <code>8600 1234 5678 9012</code>\n"
        "💸 Crypto USDT TRC20: <code>TVN...XYZ12</code>\n\n"
        "Rahmat sizga! 🤝",
        parse_mode="HTML"
    )


# === Asosiy menyuga Yordam tugmasi qo‘shish ===
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(
    KeyboardButton("🕋 Umra paketlari"),
    KeyboardButton("🛂 Vizalar"),
    KeyboardButton("🚍 Transport"),
    KeyboardButton("🚆 Poyezd"),
    KeyboardButton("🏨 Mehmonxonalar"),
    KeyboardButton("🥘 Guruh ovqatlari"),
    KeyboardButton("💝 Yordam")  # Bu yangi tugma
)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(
        "Assalomu alaykum! UmraJetBotga xush kelibsiz.\n"
        "Quyidagi bo‘limlardan birini tanlang:",
        reply_markup=main_kb
    )

# === Yordam tugmasi bosilganda ===
@dp.message_handler(lambda m: m.text == "💝 Yordam")
async def donate_handler(message: types.Message):
    text = (
        "🙏 <b>Botni qo‘llab-quvvatlash uchun donatsiya qiling:</b>\n\n"
        "💳 Uzcard: <code>8600 1234 5678 9012</code>\n"
        "💸 Crypto USDT TRC20: <code>TVN...XYZ12</code>\n\n"
        "Rahmat sizga! 🤝"
    )
    await message.answer(text, parse_mode="HTML")


from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

# Buyurtma uchun FSM yaratamiz
class OrderStates(StatesGroup):
    waiting_for_service = State()
    waiting_for_details = State()

@dp.message_handler(lambda m: m.text == "🕋 Umra paketlari")
async def umra_package_start(message: types.Message):
    await message.answer("Iltimos, Umra paketini tanlang yoki qo'shimcha ma'lumot yuboring.")
    await OrderStates.waiting_for_details.set()

@dp.message_handler(state=OrderStates.waiting_for_details)
async def process_order_details(message: types.Message, state: FSMContext):
    user = message.from_user
    order_text = message.text

    # Adminlarga yuborish
    admin_ids = [123456789, 987654321]  # O'zingizning admin IDlaringiz
    for admin_id in admin_ids:
        await dp.bot.send_message(admin_id,
            f"Yangi buyurtma:\nFoydalanuvchi: {user.full_name} (@{user.username})\nBuyurtma: {order_text}")

    await message.answer("Buyurtmangiz qabul qilindi! Tez orada siz bilan bog‘lanamiz.")
    await state.finish()


orders_count = 0  # Bu misol uchun oddiy o'zgaruvchi

@dp.message_handler(state=OrderStates.waiting_for_details)
async def process_order_and_count(message: types.Message, state: FSMContext):
    global orders_count
    orders_count += 1
    # Buyurtmani adminlarga yuborish kodi shu yerda bo'ladi
    # ...

@dp.message_handler(commands=['stats'])
async def send_stats(message: types.Message):
    admin_ids = [123456789]  # Admin ID
    if message.from_user.id in admin_ids:
        await message.answer(f"Botda jami buyurtmalar soni: {orders_count}")
    else:
        await message.answer("Sizda bu komandani ishlatish huquqi yo'q.")

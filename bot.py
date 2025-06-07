import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# FSM (agar kerak bo‘lsa keyinchalik kengaytiriladi)
class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_service = State()
    waiting_for_confirmation = State()

# --- Main menu klaviaturasi ---
def main_menu_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "🕋 Umra Paketlari",
        "🛂 Saudiya Vizalari",
        "🌟 Rawdah Tasrihi",
        "🚖 Transport Xizmatlari",
        "🚄 HHR Poyezd Chiptalari",
        "🍽️ Guruhlik Ovqatlanish",
        "🎁 Donat Qilish",
        "❌ Bekor Qilish"
    ]
    kb.add(*buttons)
    return kb

# --- Service Inline Keyboard ---
def service_inline_kb(service):
    kb = types.InlineKeyboardMarkup(row_width=1)
    if service == "Umra Paketlari":
        kb.add(
            types.InlineKeyboardButton("Standard Paket", callback_data="umra_standard"),
            types.InlineKeyboardButton("VIP Paket", callback_data="umra_vip"),
        )
    elif service == "Saudiya Vizalari":
        kb.add(
            types.InlineKeyboardButton("Umra Viza", callback_data="visa_umra"),
            types.InlineKeyboardButton("Turistik Viza", callback_data="visa_tourist"),
        )
    elif service == "Rawdah Tasrihi":
        kb.add(
            types.InlineKeyboardButton("Tasrih Olish", callback_data="tasreh_order"),
        )
    elif service == "Transport Xizmatlari":
        kb.add(
            types.InlineKeyboardButton("Makkaga Transport", callback_data="transport_makka"),
            types.InlineKeyboardButton("Madina Transport", callback_data="transport_madina"),
        )
    elif service == "HHR Poyezd Chiptalari":
        kb.add(
            types.InlineKeyboardButton("Madina – Makkah", callback_data="train_mm"),
            types.InlineKeyboardButton("Riyadh – Dammam", callback_data="train_rd"),
            types.InlineKeyboardButton("Makkah – Madina", callback_data="train_mk_md"),
            types.InlineKeyboardButton("Dammam – Riyadh", callback_data="train_dm_ry"),
        )
    elif service == "Guruhlik Ovqatlanish":
        kb.add(
            types.InlineKeyboardButton("Ovqat Buyurtma", callback_data="group_food"),
        )
    elif service == "Donat Qilish":
        kb.add(
            types.InlineKeyboardButton("Donat Qilish", callback_data="donate"),
        )
    kb.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu"))
    return kb

# --- Start handler ---
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_name = message.from_user.first_name or "Hurmatli mijoz"
    text = (
        f"👋 Assalomu alaykum, <b>{user_name}</b>!\n\n"
        "UmraJet botiga xush kelibsiz! Quyidagi xizmatlardan birini tanlang:"
    )
    await message.answer(text, reply_markup=main_menu_kb())

# --- Cancel handler ---
@dp.message_handler(lambda message: message.text == "❌ Bekor Qilish")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Buyurtma bekor qilindi. /start orqali boshidan boshlashingiz mumkin.", reply_markup=types.ReplyKeyboardRemove())

# --- Service selection handler ---
@dp.message_handler(lambda message: message.text in [
    "🕋 Umra Paketlari",
    "🛂 Saudiya Vizalari",
    "🌟 Rawdah Tasrihi",
    "🚖 Transport Xizmatlari",
    "🚄 HHR Poyezd Chiptalari",
    "🍽️ Guruhlik Ovqatlanish",
    "🎁 Donat Qilish"
])
async def service_select_handler(message: types.Message):
    service = message.text.replace("🕋 ", "").replace("🛂 ", "").replace("🌟 ", "").replace("🚖 ", "")\
        .replace("🚄 ", "").replace("🍽️ ", "").replace("🎁 ", "")
    kb = service_inline_kb(service)
    await message.answer(f"<b>{service}</b> bo‘limiga xush kelibsiz! Quyidagi xizmatlardan birini tanlang:", reply_markup=kb)

# --- Callback handler for inline buttons ---
@dp.callback_query_handler()
async def callback_handler(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id

    # Orqaga tugmasi
    if data == "back_to_menu":
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, "Bosh menyuga qaytdingiz.", reply_markup=main_menu_kb())
        return

    # Umra paketlari
    if data == "umra_standard":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🕋 <b>Umra Standard Paket</b>\n\n"
            "Bu paketda barcha asosiy xizmatlar mavjud:\n"
            "- Samolyot chiptasi\n"
            "- Mehmonxona joylashuvi\n"
            "- Transport xizmatlari\n\n"
            "Narxi: $1200 dan boshlab.\n"
            "Buyurtma berish uchun bosh menejerga murojaat qiling: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    if data == "umra_vip":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🕋 <b>Umra VIP Paket</b>\n\n"
            "Eksklyuziv xizmatlar, qulay mehmonxonalar, maxsus transport va boshqa qulayliklar.\n"
            "Narxi: $1800 dan boshlab.\n"
            "Buyurtma uchun: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    # Vizalar
    if data == "visa_umra":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🛂 <b>Umra Viza</b>\n\n"
            "Umra ziyorati uchun Saudiya vizasi xizmatlari.\n"
            "Narxi: $160.\n"
            "Bosh menejer: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    if data == "visa_tourist":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🛂 <b>Turistik Viza</b>\n\n"
            "Saudiya Arabistoni uchun turistik viza xizmatlari.\n"
            "Narxi: $120.\n"
            "Menejerlar: @vip_arabiy, @V001VB"
        )
        await bot.send_message(user_id, text)
        return

    # Rawdah Tasrihi
    if data == "tasreh_order":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🌟 <b>Rawdah Tasrihi</b>\n\n"
            "Tasrih olish uchun biz bilan bog‘laning.\n"
            "Narxlar:\n"
            "- Vizali mijozlar uchun: 15 SAR\n"
            "- Vizasis mijozlar uchun: 20 SAR\n\n"
            "Qo‘shimcha ma'lumot uchun @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    # Transport
    if data == "transport_makka":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🚖 <b>Makkaga Transport</b>\n\n"
            "Ishonchli va qulay transport xizmatlari.\n"
            "Narx va buyurtma uchun admin bilan bog‘laning."
        )
        await bot.send_message(user_id, text)
        return

    if data == "transport_madina":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🚖 <b>Madina Transport</b>\n\n"
            "Madina shahrida transport xizmatlari.\n"
            "Narxlar va buyurtma: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    # Poyezd
    if data == "train_mm":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🚄 <b>Madina – Makkah</b>\n"
            "Tezkor HHR poezd chiptalari.\n"
            "Narx va buyurtma uchun: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    if data == "train_rd":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🚄 <b>Riyadh – Dammam</b>\n"
            "Poyezd chiptalari va rezervatsiya.\n"
            "Menejer: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    if data == "train_mk_md":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🚄 <b>Makkah – Madina</b>\n"
            "HHR poyezd chiptalari mavjud.\n"
            "Buyurtma uchun: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    if data == "train_dm_ry":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🚄 <b>Dammam – Riyadh</b>\n"
            "Poyezd chiptalari haqida ma'lumot.\n"
            "Bog‘lanish: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    # Guruhlik ovqatlanish
    if data == "group_food":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🍽️ <b>Guruhlik Ovqatlanish</b>\n"
            "Katta guruhlar uchun maxsus ovqatlanish xizmatlari.\n"
            "Narxlar va buyurtma uchun: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    # Donat qilish
    if data == "donate":
        await bot.answer_callback_query(callback_query.id)
        text = (
            "🎁 <b>Donat Qilish</b>\n"
            "Bizga yordam bermoqchi bo‘lsangiz, quyidagi usullar orqali donat qilishingiz mumkin:\n\n"
            "Uzcard: 8600 1234 5678 9012\n"
            "Humo: 9860 1234 5678 9012\n"
            "Visa: 4111 1111 1111 1111\n"
            "Kripto: 0xAbcDef1234567890\n\n"
            "Rahmat! @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    # Default javob
    await bot.answer_callback_query(callback_query.id, text="Bu tugma uchun javob mavjud emas.")

# --- Fallback for unknown messages ---
@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer("Iltimos, menyudan xizmatni tanlang yoki /start yozing.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

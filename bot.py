import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_service = State()
    waiting_for_details = State()
    waiting_for_confirmation = State()

# -- Main keyboard with services --
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        "🕋 Umra Paketlari",
        "🛂 Saudiya Vizalari",
        "🌟 Rawdah Tasrihi",
        "🚖 Transport Xizmatlari",
        "🚄 HHR Poyezd Chiptalari",
        "🍽️ Guruhlik Ovqatlanish",
        "🎁 Donat Qilish",
        "❌ Bekor Qilish"
    )
    return kb

# -- Inline keyboards for services --
def get_service_inline(service):
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

# Start handler
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    name = message.from_user.first_name or "Hurmatli mijoz"
    text = f"👋 Assalomu alaykum, <b>{name}</b>!\nUmraJet botiga xush kelibsiz! Quidagi xizmatlardan birini tanlang:"
    await message.answer(text, reply_markup=main_menu())

# Cancel handler
@dp.message_handler(lambda message: message.text == "❌ Bekor Qilish")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Buyurtma bekor qilindi. /start yozib bosh menyuga qayting.", reply_markup=types.ReplyKeyboardRemove())

# Main menu service selection
@dp.message_handler(lambda message: message.text in [
    "🕋 Umra Paketlari",
    "🛂 Saudiya Vizalari",
    "🌟 Rawdah Tasrihi",
    "🚖 Transport Xizmatlari",
    "🚄 HHR Poyezd Chiptalari",
    "🍽️ Guruhlik Ovqatlanish",
    "🎁 Donat Qilish"
])
async def service_menu(message: types.Message):
    # To remove emoji from text key to get exact service name
    service = message.text
    for e in ["🕋 ", "🛂 ", "🌟 ", "🚖 ", "🚄 ", "🍽️ ", "🎁 "]:
        service = service.replace(e, "")
    kb = get_service_inline(service)
    await message.answer(f"<b>{service}</b> bo‘limiga xush kelibsiz! Quyidagi xizmatlardan birini tanlang:", reply_markup=kb)

# Callback handler for inline buttons
@dp.callback_query_handler()
async def inline_kb_handler(callback: types.CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id

    # Back button
    if data == "back_to_menu":
        await bot.answer_callback_query(callback.id)
        await bot.send_message(user_id, "Bosh menyuga qaytdingiz.", reply_markup=main_menu())
        return

    # Umra paketlari
    if data == "umra_standard":
        await bot.answer_callback_query(callback.id)
        text = (
            "🕋 <b>Umra Standard Paket</b>\n\n"
            "• Samolyot chiptasi\n"
            "• Mehmonxona joylashuvi\n"
            "• Transport xizmatlari\n"
            "Narxi: $1200 dan boshlab.\n"
            "Buyurtma uchun bosh menejer: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    if data == "umra_vip":
        await bot.answer_callback_query(callback.id)
        text = (
            "🕋 <b>Umra VIP Paket</b>\n\n"
            "Eksklyuziv xizmatlar va maxsus qulayliklar.\n"
            "Narxi: $1800 dan boshlab.\n"
            "Buyurtma uchun: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    # Saudiya vizalari
    if data == "visa_umra":
        await bot.answer_callback_query(callback.id)
        text = (
            "🛂 <b>Umra Viza</b>\n\n"
            "Narxi: $160.\n"
            "Bosh menejer: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    if data == "visa_tourist":
        await bot.answer_callback_query(callback.id)
        text = (
            "🛂 <b>Turistik Viza</b>\n\n"
            "Narxi: $120.\n"
            "Menejerlar: @vip_arabiy, @V001VB"
        )
        await bot.send_message(user_id, text)
        return

    # Rawdah tasrihi
    if data == "tasreh_order":
        await bot.answer_callback_query(callback.id)
        text = (
            "🌟 <b>Rawdah Tasrihi</b>\n\n"
            "Vizali mijozlar uchun: 15 SAR\n"
            "Vizasis mijozlar uchun: 20 SAR\n\n"
            "Qo‘shimcha ma’lumot uchun: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    # Transport
    if data == "transport_makka":
        await bot.answer_callback_query(callback.id)
        text = (
            "🚖 <b>Makkaga Transport</b>\n\n"
            "Ishonchli transport xizmatlari.\n"
            "Narx va buyurtma uchun: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    if data == "transport_madina":
        await bot.answer_callback_query(callback.id)
        text = (
            "🚖 <b>Madina Transport</b>\n\n"
            "Madina shahridagi transport xizmatlari.\n"
            "Bog‘lanish: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    # HHR poyezd chiptalari
    if data == "train_mm":
        await bot.answer_callback_query(callback.id)
        text = (
            "🚄 <b>Madina – Makkah</b>\n"
            "HHR poezd chiptalari.\n"
            "Buyurtma uchun: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    if data == "train_rd":
        await bot.answer_callback_query(callback.id)
        text = (
            "🚄 <b>Riyadh – Dammam</b>\n"
            "Poyezd chiptalari va rezervatsiya.\n"
            "Menejer: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    if data == "train_mk_md":
        await bot.answer_callback_query(callback.id)
        text = (
            "🚄 <b>Makkah – Madina</b>\n"
            "HHR poyezd chiptalari mavjud.\n"
            "Buyurtma uchun: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    if data == "train_dm_ry":
        await bot.answer_callback_query(callback.id)
        text = (
            "🚄 <b>Dammam – Riyadh</b>\n"
            "Poyezd chiptalari haqida ma'lumot.\n"
            "Bog‘lanish: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    # Guruhlik ovqatlanish
    if data == "group_food":
        await bot.answer_callback_query(callback.id)
        text = (
            "🍽️ <b>Guruhlik Ovqatlanish</b>\n"
            "Katta guruhlar uchun maxsus ovqatlanish xizmatlari.\n"
            "Narxlar va buyurtma uchun: @vip_arabiy"
        )
        await bot.send_message(user_id, text)
        return

    # Donat qilish
    if data == "donate":
        await bot.answer_callback_query(callback.id)
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
    await bot.answer_callback_query(callback.id, text="Bu tugma uchun javob mavjud emas.")

# Fallback handler
@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer("Iltimos, menyudan xizmatni tanlang yoki /start yozing.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

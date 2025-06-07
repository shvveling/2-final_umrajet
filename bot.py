import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split()))
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# -------- States --------

class OrderStates(StatesGroup):
    waiting_for_service = State()
    waiting_for_details = State()
    waiting_for_payment_method = State()
    waiting_for_confirmation = State()

# -------- Keyboards --------

# Start menu buttons (services overview)
start_text = (
    "🕋 *Assalomu alaykum, {name}!* \n\n"
    "🎉 UmraJet Telegram botiga xush kelibsiz! Sizga quyidagi xizmatlarni taqdim etamiz:\n\n"
    "🌟 *Bizning xizmatlar:* \n"
    "📜 Umra paketlari\n"
    "🛂 Saudiya vizalari\n"
    "🏨 Mehmonxonalar va yotoqxona\n"
    "🚗 Transport xizmatlari\n"
    "🚅 Poyezd chiptalari\n"
    "🍽 Guruh taomlari\n"
    "📿 Ravza tasreh\n"
    "💰 Donat bo‘limi\n\n"
    "📢 Bizning kanallar: @umrajet, @the_ravza\n"
    "📞 Managerlar: @vip_arabiy (Asosiy), @V001VB (Zaxira)\n\n"
    "*Quyidagi bo‘limlardan birini tanlang va batafsil ma'lumot oling!*"
)

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🕋 Umra paketlari", callback_data="service_umra_packages"),
        InlineKeyboardButton("🛂 Vizalar", callback_data="service_visas"),
        InlineKeyboardButton("🏨 Mehmonxonalar", callback_data="service_hotels"),
        InlineKeyboardButton("🚗 Transport", callback_data="service_transport"),
        InlineKeyboardButton("🚅 Poyezd chiptalari", callback_data="service_trains"),
        InlineKeyboardButton("🍽 Guruh taomlari", callback_data="service_group_meals"),
        InlineKeyboardButton("📿 Ravza tasreh", callback_data="service_ravza_tasreh"),
        InlineKeyboardButton("💰 Donat bo‘limi", callback_data="donate"),
    )
    return kb

def payment_methods_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💳 Uzcard", callback_data="pay_uzcard"),
        InlineKeyboardButton("🏦 Humo", callback_data="pay_humo"),
        InlineKeyboardButton("💳 Visa", callback_data="pay_visa"),
        InlineKeyboardButton("🪙 Crypto", callback_data="pay_crypto"),
        InlineKeyboardButton("🔙 Ortga", callback_data="back_to_services"),
    )
    return kb

# -------- Handlers --------

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(start_text.format(name=message.from_user.first_name), parse_mode="Markdown", reply_markup=main_menu())

# Service panels handlers

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('service_'))
async def service_handler(callback_query: types.CallbackQuery):
    service = callback_query.data.split('_')[1]

    if service == "umra":
        text = (
            "🕋 *Umra Paketlari*\n\n"
            "✅ Standart paket - $1200 dan boshlanadi\n"
            "✅ VIP paket - $1800 dan boshlanadi\n\n"
            "📞 Managerlar: @vip_arabiy (Asosiy), @V001VB (Zaxira)\n\n"
            "To‘lov usullarini tanlang."
        )
    elif service == "visas":
        text = (
            "🛂 *Saudiya Vizalari*\n\n"
            "✅ Umra viza - $160\n"
            "✅ Turistik viza - $120\n"
            "❗ Guruhlarga chegirmalar mavjud\n\n"
            "📞 Managerlar: @vip_arabiy (Asosiy), @V001VB (Zaxira)\n\n"
            "To‘lov usullarini tanlang."
        )
    elif service == "hotels":
        text = (
            "🏨 *Mehmonxonalar va Yotoqxona*\n\n"
            "Sizga qulay va arzon turar joylarni taklif qilamiz.\n\n"
            "📞 Managerlar: @vip_arabiy (Asosiy), @V001VB (Zaxira)\n\n"
            "To‘lov usullarini tanlang."
        )
    elif service == "transport":
        text = (
            "🚗 *Transport Xizmatlari*\n\n"
            "Avtomobil va avtobuslar bilan qulay transport xizmatlari.\n\n"
            "📞 Managerlar: @vip_arabiy (Asosiy), @V001VB (Zaxira)\n\n"
            "To‘lov usullarini tanlang."
        )
    elif service == "trains":
        text = (
            "🚅 *Poyezd Chiptalari*\n\n"
            "Mashhur yo‘nalishlar:\n"
            "– Madina – Makka\n"
            "– Riyad – Dammam\n"
            "– Riyad – Makka\n"
            "– Riyad – Qosim\n\n"
            "📞 Managerlar: @vip_arabiy (Asosiy), @V001VB (Zaxira)\n\n"
            "To‘lov usullarini tanlang."
        )
    elif service == "group":
        text = (
            "🍽 *Guruh Taomlari*\n\n"
            "Sifatli va mazali taomlar guruhlar uchun.\n\n"
            "📞 Managerlar: @vip_arabiy (Asosiy), @V001VB (Zaxira)\n\n"
            "To‘lov usullarini tanlang."
        )
    elif service == "ravza":
        text = (
            "📿 *Ravza Tasreh*\n\n"
            "🔹 Viza bilan: 15 SAR / dona\n"
            "🔹 Vizsiz: 20 SAR / dona\n"
            "🔹 10 tadan ortiq bo‘lsa, chegirmalar mavjud!\n\n"
            "📞 Managerlar: @vip_arabiy (Asosiy), @V001VB (Zaxira)\n\n"
            "To‘lov usullarini tanlang."
        )
    else:
        await callback_query.answer("Kechirasiz, bu xizmat hozircha mavjud emas.", show_alert=True)
        return

    await callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=payment_methods_keyboard())

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('pay_'))
async def payment_handler(callback_query: types.CallbackQuery):
    pay_method = callback_query.data.split('_')[1]

    if pay_method == "uzcard":
        text = (
            "💳 *Uzcard kartalar*:\n"
            "1️⃣ 8600 0304 9680 2624 (Khamidov Ibodulloh)\n"
            "2️⃣ 5614 6822 1222 3368 (Khamidov Ibodulloh)\n\n"
            "❗ Kartani tanlash va nusxalash uchun ustiga bosishingiz mumkin.\n"
        )
    elif pay_method == "humo":
        text = (
            "🏦 *Humo kartasi*:\n"
            "9860 1001 2621 9243 (Khamidov Ibodulloh)\n\n"
            "❗ Kartani tanlash va nusxalash uchun ustiga bosishingiz mumkin.\n"
        )
    elif pay_method == "visa":
        text = (
            "💳 *Visa kartalar*:\n"
            "1️⃣ 4140 8400 0184 8680 (Khamidov Ibodulloh)\n"
            "2️⃣ 4278 3100 2389 5840 (Khamidov Ibodulloh)\n\n"
            "❗ Kartani tanlash va nusxalash uchun ustiga bosishingiz mumkin.\n"
        )
    elif pay_method == "crypto":
        text = (
            "🪙 *Crypto hisoblar*:\n"
            "USDT (Tron TRC20): `TLGiUsNzQ8n31x3VwsYiWEU97jdftTDqT3`\n"
            "ETH (BEP20): `0xa11fb72cc1ee74cfdaadb25ab2530dd32bafa8f8`\n"
            "BTC (BEP20): `0xa11fb72cc1ee74cfdaadb25ab2530dd32bafa8f8`\n\n"
            "❗ Manzilni nusxalash uchun ustiga bosishingiz mumkin.\n"
        )
    else:
        await callback_query.answer("Kechirasiz, bu to‘lov usuli mavjud emas.", show_alert=True)
        return

    back_kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_services"))
    await callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=back_kb)

@dp.callback_query_handler(lambda c: c.data == "back_to_services")
async def back_to_services_handler(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(start_text.format(name=callback_query.from_user.first_name), parse_mode="Markdown", reply_markup=main_menu())

# Donat bo‘limi
@dp.callback_query_handler(lambda c: c.data == "donate")
async def donate_handler(callback_query: types.CallbackQuery):
    text = (
        "💰 *Donat bo‘limi*\n\n"
        "Bizga yordam berishni istaysizmi? Sizning xayringiz biz uchun juda muhim!\n\n"
        "Quyidagi usullar orqali donat qilishingiz mumkin:\n\n"
        "💳 Uzcard va Humo kartalar\n"
        "🪙 Crypto hisoblar\n\n"
        "Managerlar:\n"
        "📞 @vip_arabiy (Asosiy)\n"
        "📞 @V001VB (Zaxira)\n\n"
        "Rahmat sizga! 🤲"
    )
    await callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=payment_methods_keyboard())

# Foydalanuvchi buyurtmasi uchun soddalashtirilgan FSM (misol uchun)
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('service_'))
async def start_order(callback_query: types.CallbackQuery, state: FSMContext):
    # Boshlash uchun holatni saqlaymiz
    await OrderStates.waiting_for_details.set()
    await state.update_data(service=callback_query.data)
    await callback_query.message.answer("✅ Buyurtmangizni batafsil yozing yoki savol bering:")

@dp.message_handler(state=OrderStates.waiting_for_details)
async def process_order_details(message: types.Message, state: FSMContext):
    data = await state.get_data()
    service = data.get("service", "Noma'lum xizmat")

    # Bu yerda adminlarga buyurtmani jo'natamiz
    text = (
        f"🆕 *Yangi buyurtma*\n"
        f"👤 Foydalanuvchi: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"📱 ID: {message.from_user.id}\n"
        f"📌 Xizmat: {service}\n"
        f"📝 Tafsilotlar: {message.text}\n"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Adminga xabar yuborishda xatolik: {e}")

    await message.answer("✅ Buyurtmangiz qabul qilindi! Tez orada managerlar siz bilan bog‘lanishadi.")
    await state.finish()

# Qo‘shimcha handlerlar va sozlashlar kerak bo‘lsa, so‘rang.

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

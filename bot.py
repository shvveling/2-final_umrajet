import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

# Load env vars
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))
GROUP_ID = int(os.getenv("GROUP_ID"))

# Configure logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ===== FSM States =====
class OrderStates(StatesGroup):
    choosing_service = State()
    entering_quantity = State()
    entering_visa_status = State()
    confirming_order = State()
    waiting_payment = State()

# ===== Payment Info =====
PAYMENTS = {
    "Uzcard": "Uzcard: 8600 1234 5678 9012\nNom: UmraJet Bot",
    "Humo": "Humo: 9860 4321 8765 2109\nNom: UmraJet Bot",
    "Visa": "Visa: 4111 1111 1111 1111\nNom: UmraJet Bot",
    "Crypto": "Crypto (BTC): 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
}

# ===== Services & Prices =====
SERVICES = {
    "umrah_standard": {
        "name": "🕋 Umra Paket - Standart",
        "desc": "Umra safaringiz uchun eng qulay va arzon paket. Narxi: 1200$ dan boshlab.",
        "price": 1200
    },
    "umrah_vip": {
        "name": "💎 Umra Paket - VIP",
        "desc": "Lux darajadagi Umra tajribasi. Narxi: 1800$ dan boshlab.",
        "price": 1800
    },
    "visa_umrah": {
        "name": "🛂 Umra Vizasi",
        "desc": "Umra vizasi narxi: 160$. Tez va ishonchli xizmat.",
        "price": 160
    },
    "visa_tourist": {
        "name": "🛂 Turistik Viza",
        "desc": "Saudiya Arabistoni uchun turist viza. Narxi: 120$.",
        "price": 120
    },
    "rawdah_tasreh": {
        "name": "🌟 Rawdah Tasreh",
        "desc": ("Rawdah tasreh xizmati.\n"
                 "10 yoki undan ko'p bo'lsa:\n"
                 " - Visa bilan: 13 SAR / kishiga\n"
                 " - Visasiz: 17 SAR / kishiga\n"
                 "Guruh yoki katta buyurtmalarda narx kelishilgan."),
        "price": None  # Narx shartlarga ko'ra belgilanadi
    },
    "transport": {
        "name": "🚖 Transport xizmatlari",
        "desc": "Makkaga va Madinaga borish uchun qulay transport xizmatlari.",
        "price": None
    },
    "train_ticket": {
        "name": "🚆 HHR Poyezd chiptasi",
        "desc": ("HHR yo'nalishlari:\n"
                 "- Madina – Makka\n"
                 "- Riyadh – Dammam\n"
                 "- Riyadh – Jidda\n"
                 "- Riyadh – Madina\n"
                 "- Dammam – Jidda\n"
                 "- Dammam – Madina\n"
                 "- Makka – Madina"),
        "price": None
    },
    "group_meal": {
        "name": "🍽️ Guruh uchun ovqatlanish",
        "desc": "Guruh ovqatlanish paketlari va maxsus menyular.",
        "price": None
    }
}

MANAGERS = ["@vip_arabiy (Asosiy)", "@V001VB (Zaxira)"]

# ===== Keyboards =====
def main_menu_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    for key, service in SERVICES.items():
        kb.insert(InlineKeyboardButton(service["name"], callback_data=f"service_{key}"))
    kb.add(InlineKeyboardButton("📞 Biz bilan bog'lanish", callback_data="contact"))
    return kb

def payment_menu_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    for method in PAYMENTS.keys():
        kb.insert(InlineKeyboardButton(method, callback_data=f"pay_{method}"))
    kb.add(InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_services"))
    return kb

def confirm_order_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_order"))
    kb.add(InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_order"))
    return kb

# ===== Helper Functions =====
def format_service_desc(key):
    service = SERVICES[key]
    desc = f"{service['name']}\n\n{service['desc']}"
    if service["price"]:
        desc += f"\n\nNarx: {service['price']}$"
    desc += f"\n\nManagerlar: {', '.join(MANAGERS)}"
    desc += f"\n\nBizning kanallar: @umrajet, @the_ravza"
    return desc

def send_admins(message):
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, message, parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.error(f"Adminga habar yuborishda xatolik: {e}")

# ===== Bot Handlers =====

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "UmraJet Telegram botiga xush kelibsiz! Siz uchun quyidagi xizmatlarni taklif qilamiz. "
        "Iltimos, kerakli xizmatni tanlang:",
        reply_markup=main_menu_kb()
    )
    await OrderStates.choosing_service.set()

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("service_"), state=OrderStates.choosing_service)
async def process_service_choice(callback_query: types.CallbackQuery, state: FSMContext):
    service_key = callback_query.data[len("service_"):]
    if service_key not in SERVICES:
        await callback_query.answer("Noma'lum xizmat tanlandi.")
        return
    await state.update_data(service=service_key)

    service = SERVICES[service_key]

    # Maxsus holatlar (masalan, Rawdah Tasreh uchun vizani so'rash)
    if service_key == "rawdah_tasreh":
        await callback_query.message.answer(
            format_service_desc(service_key) + "\n\nNechta tasreh kerakligini kiriting (raqam bilan):"
        )
        await OrderStates.entering_quantity.set()
        return

    if service_key in ["umrah_standard", "umrah_vip", "visa_umrah", "visa_tourist"]:
        # Oddiy buyurtma - miqdorni sorash
        await callback_query.message.answer(
            format_service_desc(service_key) + "\n\nNechta buyurtma qilmoqchisiz? (raqam kiriting):"
        )
        await OrderStates.entering_quantity.set()
        return

    # Agar miqdor kerak bo'lmasa (masalan transport, guruh ovqatlari)
    await callback_query.message.answer(format_service_desc(service_key))
    await callback_query.answer()

@dp.message_handler(state=OrderStates.entering_quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    service_key = data.get("service")

    try:
        quantity = int(message.text)
        if quantity <= 0:
            await message.answer("Iltimos, 1 yoki undan katta raqam kiriting.")
            return
    except:
        await message.answer("Iltimos, faqat raqam kiriting.")
        return

    await state.update_data(quantity=quantity)

    # Rawdah tasreh maxsus logika
    if service_key == "rawdah_tasreh":
        await message.answer(
            "Tasreh uchun viza borligi haqida ma'lumot bering:\n"
            "✅ Bor bo'lsa, 'ha' deb yozing\n"
            "❌ Yo'q bo'lsa, 'yo‘q' deb yozing"
        )
        await OrderStates.entering_visa_status.set()
        return

    # Oddiy xizmatlar uchun to‘lov usulini tanlashga o'tish
    await message.answer("Iltimos, to‘lov usulini tanlang:", reply_markup=payment_menu_kb())
    await OrderStates.waiting_payment.set()

@dp.message_handler(state=OrderStates.entering_visa_status)
async def process_visa_status(message: types.Message, state: FSMContext):
    visa_answer = message.text.strip().lower()
    if visa_answer not in ["ha", "yo'q", "yo‘q"]:
        await message.answer("Iltimos, 'ha' yoki 'yo‘q' deb yozing.")
        return

    visa_provided = visa_answer == "ha"
    await state.update_data(visa=visa_provided)

    # Narx hisoblash
    data = await state.get_data()
    quantity = data.get("quantity")

    if visa_provided:
        price_per_person = 13
    else:
        price_per_person = 17

    total_price = price_per_person * quantity
    await state.update_data(total_price=total_price)

    msg = (
        f"Siz tanlagan xizmat: Rawdah Tasreh\n"
        f"Nechta tasreh: {quantity}\n"
        f"Viza mavjudligi: {'Ha' if visa_provided else 'Yo‘q'}\n"
        f"Narx: {price_per_person} SAR x {quantity} = {total_price} SAR\n\n"
        "To‘lov usulini tanlang:"
    )
    await message.answer(msg, reply_markup=payment_menu_kb())
    await OrderStates.waiting_payment.set()

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("pay_"), state=OrderStates.waiting_payment)
async def process_payment_method(callback_query: types.CallbackQuery, state: FSMContext):
    method = callback_query.data[len("pay_"):]
    if method not in PAYMENTS:
        await callback_query.answer("Noma'lum to‘lov usuli.")
        return

    data = await state.get_data()
    service_key = data.get("service")
    quantity = data.get("quantity")
    visa_provided = data.get("visa", None)
    total_price = data.get("total_price")

    # Narxni hisoblash kerak bo'lsa
    if total_price is None:
        service = SERVICES[service_key]
        price = service.get("price")
        if price is not None:
            total_price = price * quantity
        else:
            total_price = "Noma'lum"

    pay_info = PAYMENTS[method]

    text = (
        f"✅ Buyurtmangiz qabul qilindi!\n\n"
        f"Xizmat: {SERVICES[service_key]['name']}\n"
        f"Miqdor: {quantity}\n"
    )
    if visa_provided is not None:
        text += f"Viza: {'Ha' if visa_provided else 'Yo‘q'}\n"
    text += f"Umumiy narx: {total_price} $\n\n"
    text += f"To‘lov uchun quyidagi ma'lumotlardan foydalaning:\n\n<code>{pay_info}</code>\n\n"
    text += "To‘lov qilganingizdan so‘ng, iltimos, tasdiqlash uchun xabar yuboring."

    await callback_query.message.answer(text, parse_mode=ParseMode.HTML)

    # Adminlarga xabar yuborish
    order_summary = (
        f"🆕 Yangi buyurtma!\n"
        f"Foydalanuvchi: @{callback_query.from_user.username or callback_query.from_user.full_name} (ID: {callback_query.from_user.id})\n"
        f"Xizmat: {SERVICES[service_key]['name']}\n"
        f"Miqdor: {quantity}\n"
    )
    if visa_provided is not None:
        order_summary += f"Viza: {'Ha' if visa_provided else 'Yo‘q'}\n"
    order_summary += f"To‘lov usuli: {method}\n"
    order_summary += f"Umumiy narx: {total_price}\n"
    order_summary += f"Managerlar: {', '.join(MANAGERS)}"

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, order_summary)
        except Exception as e:
            logging.error(f"Adminga xabar yuborishda xato: {e}")

    await callback_query.answer()
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "contact", state="*")
async def contact_us(callback_query: types.CallbackQuery):
    contact_text = (
        "Biz bilan bog'lanish:\n"
        "Asosiy menejer: @vip_arabiy\n"
        "Zaxira menejer: @V001VB\n\n"
        "Kanallarimiz:\n"
        "@umrajet\n"
        "@the_ravza\n\n"
        "Savollar bo‘lsa, bemalol murojaat qiling."
    )
    await callback_query.message.answer(contact_text)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "back_to_services", state="*")
async def back_to_services(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Asosiy menyuga qaytdingiz:", reply_markup=main_menu_kb())
    await OrderStates.choosing_service.set()
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "confirm_order", state=OrderStates.confirming_order)
async def confirm_order_handler(callback_query: types.CallbackQuery, state: FSMContext):
    # Bu qism kerak bo'lsa keyin qo'shiladi
    await callback_query.answer("Buyurtma qabul qilindi!")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "cancel_order", state=OrderStates.confirming_order)
async def cancel_order_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Buyurtma bekor qilindi.")
    await state.finish()
    await callback_query.answer()

@dp.message_handler()
async def fallback_handler(message: types.Message):
    await message.answer(
        "Iltimos, quyidagi menyudan xizmatni tanlang yoki /start buyrug'ini bering.",
        reply_markup=main_menu_kb()
    )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

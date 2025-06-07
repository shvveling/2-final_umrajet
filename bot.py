import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))
GROUP_ID = int(os.getenv("GROUP_ID"))

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

# --- FSM holatlari ---
class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_service = State()
    waiting_for_quantity = State()
    waiting_for_extra_info = State()
    waiting_for_payment_method = State()
    confirmation = State()

# --- Xizmatlar ro'yxati ---
SERVICES = {
    "umra_package": {
        "title": "🕋 Umra Paketlari",
        "description": "Standart Umra paketi 1200$ dan boshlanadi.\nVIP Umra paketi 1800$ dan boshlanadi.\n\nBizning paketlarimiz yuqori sifat va qulaylikni ta'minlaydi.",
        "price_info": "1200$ (Standart), 1800$ (VIP)",
    },
    "saudi_visa": {
        "title": "🛂 Saudiya Vizalari",
        "description": "Umra viza: 160$\nTuristik viza: 120$\nGuruhlarga chegirmalar mavjud.",
        "price_info": "Umra: 160$, Turistik: 120$",
    },
    "rawda_tasreh": {
        "title": "🌺 Ravza Tasreh Xizmati",
        "description": ("Tasreh narxi dona uchun:\n"
                        "- Agar viza taqdim etilsa: 15 SAR\n"
                        "- Viza bo‘lmasa: 20 SAR\n\n"
                        "10 tadan ortiq buyurtmalarda yoki guruhlar uchun narxlar kelishiladi."),
        "price_info": "15 SAR (viza bilan), 20 SAR (vizasiz), chegirma mavjud",
    },
    "train_tickets": {
        "title": "🚄 Saudiya Temir Yo‘llari",
        "description": ("Temir yo‘l chiptalari:\n"
                        "- Madina–Makka\n"
                        "- Riyadh–Dammam\n"
                        "- Madina–Riyadh\n"
                        "Narxlar va yo‘nalishlar bo‘yicha batafsil ma’lumot uchun murojaat qiling."),
        "price_info": "Yo‘nalishga qarab farq qiladi",
    },
    "donate": {
        "title": "🎁 Donat (Xayriya)",
        "description": "Bizning xizmatlarimizni qo‘llab-quvvatlash uchun donat qiling. Har qanday summani mamnuniyat bilan qabul qilamiz!",
        "price_info": "Istalgan summada",
    },
    # Qo'shimcha xizmatlar qo'shish mumkin
}

# --- To'lov kartalari ---
PAYMENT_CARDS = {
    "uzcard": [
        "8600 0304 9680 2624 (Khamidov Ibodulloh)",
        "5614 6822 1222 3368 (Khamidov Ibodulloh)",
    ],
    "humo": [
        "9860 1001 2621 9243 (Khamidov Ibodulloh)",
    ],
    "visa": [
        "4140 8400 0184 8680 (Khamidov Ibodulloh)",
        "4278 3100 2389 5840 (Khamidov Ibodulloh)",
    ],
    "crypto": {
        "USDT (Tron TRC20)": "TLGiUsNzQ8n31x3VwsYiWEU97jdftTDqT3",
        "ETH (BEP20)": "0xa11fb72cc1ee74cfdaadb25ab2530dd32bafa8f8",
        "BTC (BEP20)": "0xa11fb72cc1ee74cfdaadb25ab2530dd32bafa8f8",
    },
}

# --- Managerlar ---
MANAGERS = ["@vip_arabiy", "@V001VB"]

# --- Start xabari ---
START_MESSAGE = (
    "Assalomu alaykum, <b>{name}</b>!\n\n"
    "Sizni UmraJet botiga xush kelibsiz! 👋\n\n"
    "Quyidagi xizmatlarimizni tanlab, kerakli ma'lumotlarni oling va buyurtma bering:\n\n"
)

# --- Xizmatlar paneli yaratamiz ---
def get_services_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    for key, service in SERVICES.items():
        kb.insert(InlineKeyboardButton(service['title'], callback_data=f"service_{key}"))
    kb.add(InlineKeyboardButton("🔙 Ortga", callback_data="back_to_start"))
    return kb

# --- To'lovlar paneli ---
def get_payment_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("💳 Uzcard", callback_data="pay_uzcard"))
    kb.add(InlineKeyboardButton("💰 Humo", callback_data="pay_humo"))
    kb.add(InlineKeyboardButton("💳 Visa", callback_data="pay_visa"))
    kb.add(InlineKeyboardButton("₿ Crypto", callback_data="pay_crypto"))
    kb.add(InlineKeyboardButton("🔙 Ortga", callback_data="back_to_services"))
    return kb

# --- Start handler ---
@dp.message_handler(commands=['start', 'menu'])
async def cmd_start(message: types.Message):
    name = message.from_user.full_name or message.from_user.first_name
    text = START_MESSAGE.format(name=name)
    # xizmatlar nomlari
    services_list = "\n".join([f"• {s['title']}" for s in SERVICES.values()])
    text += services_list + "\n\n"
    text += "Bizning Telegram kanallarimiz:\n" \
            "📢 @umrajet\n" \
            "🌹 @the_ravza\n\n" \
            "Managerlarimiz:\n" + ", ".join(MANAGERS)
    await message.answer(text, reply_markup=get_services_keyboard())

# --- Callback query handler ---
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("service_"))
async def service_detail_handler(callback_query: types.CallbackQuery):
    service_key = callback_query.data[8:]
    service = SERVICES.get(service_key)
    if not service:
        await callback_query.answer("Xizmat topilmadi.", show_alert=True)
        return

    desc = f"<b>{service['title']}</b>\n\n{service['description']}\n\n" \
           f"<b>Narxlar:</b> {service['price_info']}\n\n" \
           "Buyurtma berish uchun quyidagi tugmani bosing."
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Buyurtma berish", callback_data=f"order_{service_key}"))
    kb.add(InlineKeyboardButton("🔙 Ortga", callback_data="back_to_services"))
    await callback_query.message.edit_text(desc, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "back_to_services")
async def back_to_services_handler(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "Xizmatlar ro'yxati:", reply_markup=get_services_keyboard()
    )

# --- Buyurtma bosqichlari ---
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("order_"))
async def order_start_handler(callback_query: types.CallbackQuery, state: FSMContext):
    service_key = callback_query.data[6:]
    await state.update_data(service=service_key)
    await OrderStates.waiting_for_name.set()
    await callback_query.message.answer("Iltimos, ismingizni kiriting:")
    await callback_query.answer()

@dp.message_handler(state=OrderStates.waiting_for_name, content_types=types.ContentTypes.TEXT)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await OrderStates.waiting_for_phone.set()
    await message.answer("Telefon raqamingizni kiriting (masalan: +998901234567):")

@dp.message_handler(state=OrderStates.waiting_for_phone, content_types=types.ContentTypes.TEXT)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if not (phone.startswith('+') and phone[1:].isdigit()):
        await message.answer("Iltimos, telefon raqamini +998901234567 formatda kiriting.")
        return
    await state.update_data(phone=phone)
    data = await state.get_data()
    service_key = data.get("service")
    service = SERVICES.get(service_key)
    if service_key == "rawda_tasreh":
        await OrderStates.waiting_for_quantity.set()
        await message.answer("Necha dona tasreh kerakligini kiriting:")
    else:
        await OrderStates.waiting_for_extra_info.set()
        await message.answer("Qo‘shimcha ma’lumot bo‘lsa yozing yoki 'Yo‘q' deb yuboring:")

@dp.message_handler(state=OrderStates.waiting_for_quantity, content_types=types.ContentTypes.TEXT)
async def process_quantity(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Iltimos, musbat butun son kiriting.")
        return
    await state.update_data(quantity=int(message.text))
    await OrderStates.waiting_for_extra_info.set()
    await message.answer("Qo‘shimcha ma’lumot bo‘lsa yozing yoki 'Yo‘q' deb yuboring:")

@dp.message_handler(state=OrderStates.waiting_for_extra_info, content_types=types.ContentTypes.TEXT)
async def process_extra_info(message: types.Message, state: FSMContext):
    extra = message.text
    await state.update_data(extra_info=extra)
    await OrderStates.waiting_for_payment_method.set()

    kb = get_payment_keyboard()
    await message.answer("To‘lov usulini tanlang:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("pay_"), state=OrderStates.waiting_for_payment_method)
async def payment_method_handler(callback_query: types.CallbackQuery, state: FSMContext):
    pay_method = callback_query.data[4:]
    await state.update_data(payment_method=pay_method)
    data = await state.get_data()

    # To'lov kartalari ko'rsatish
    if pay_method in ["uzcard", "humo", "visa"]:
        cards = PAYMENT_CARDS.get(pay_method, [])
        cards_text = "\n".join(cards)
        text = f"<b>{pay_method.capitalize()} kartalari:</b>\n{cards_text}\n\n" \
               "To‘lovni amalga oshirib, keyin buyurtmani tasdiqlang."
    elif pay_method == "crypto":
        crypto_info = PAYMENT_CARDS["crypto"]
        text = "<b>Kripto hamyonlari:</b>\n"
        for coin, address in crypto_info.items():
            text += f"{coin}: <code>{address}</code>\n"
        text += "\nTo‘lovni amalga oshirib, keyin buyurtmani tasdiqlang."
    else:
        text = "Noma’lum to‘lov usuli."

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Buyurtmani tasdiqlash", callback_data="confirm_order"))
    kb.add(InlineKeyboardButton("Bekor qilish", callback_data="cancel_order"))
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "confirm_order", state=OrderStates.waiting_for_payment_method)
async def confirm_order_handler(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    phone = data.get("phone")
    service_key = data.get("service")
    quantity = data.get("quantity", 1)
    extra = data.get("extra_info", "Yo'q")
    pay_method = data.get("payment_method")

    service = SERVICES.get(service_key)

    order_text = (
        f"Yangi buyurtma! 📩\n\n"
        f"<b>Xizmat:</b> {service['title']}\n"
        f"<b>Ism:</b> {name}\n"
        f"<b>Telefon:</b> {phone}\n"
        f"<b>Miqdor:</b> {quantity}\n"
        f"<b>Qo‘shimcha:</b> {extra}\n"
        f"<b>To‘lov usuli:</b> {pay_method.capitalize()}\n"
    )
    # Adminlarga yuborish
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, order_text)
        except Exception as e:
            logging.error(f"Adminga xabar yuborishda xatolik: {e}")

    await callback_query.message.edit_text("Buyurtmangiz qabul qilindi! Tez orada managerlar siz bilan bog‘lanishadi. Rahmat! 🙏")
    await state.finish()
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "cancel_order", state="*")
async def cancel_order_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.message.edit_text("Buyurtma bekor qilindi.")
    await callback_query.answer()

# --- Donat bo‘limi ---
@dp.callback_query_handler(lambda c: c.data == "service_donate")
async def donate_handler(callback_query: types.CallbackQuery):
    text = f"<b>{SERVICES['donate']['title']}</b>\n\n{SERVICES['donate']['description']}\n\n"
    text += "💳 To‘lov kartalari:\n"
    for card in PAYMENT_CARDS["uzcard"]:
        text += f"{card}\n"
    text += "\nAgar boshqa to‘lov usullari kerak bo‘lsa, biz bilan bog‘laning."
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔙 Ortga", callback_data="back_to_services"))
    await callback_query.message.edit_text(text, reply_markup=kb)

# --- Asosiy catch all handler ---
@dp.message_handler()
async def fallback_handler(message: types.Message):
    await message.answer("Iltimos, xizmatlardan birini tanlang yoki /start yozing.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

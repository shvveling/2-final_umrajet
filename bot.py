import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import os

# Logger
logging.basicConfig(level=logging.INFO)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))  # Admin IDs as integers
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# FSM States
class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_service = State()
    waiting_for_confirmation = State()
    waiting_for_payment = State()

# --- Utility functions ---

def get_welcome_message(user_name: str) -> str:
    return (
        f"👋 Assalomu alaykum, <b>{user_name}</b>!\n\n"
        "UmraJet botiga xush kelibsiz! Sizga eng yaxshi xizmatlarimizni taklif qilamiz. "
        "Quyida mavjud xizmatlarimiz bilan tanishing:\n\n"
        "✨ Umra paketlari\n"
        "✨ Saudiya vizalari\n"
        "✨ Rawdah tasrihi\n"
        "✨ Transport xizmatlari\n"
        "✨ HHR poyezd chiptalari\n"
        "✨ Guruhlik ovqatlanish\n"
        "✨ Donat qilish imkoniyati\n\n"
        "📢 Yangiliklar uchun kanalimizni kuzatib boring: @umrajet\n"
        "👨‍💼 Bosh menejerlarimiz:\n"
        " - @vip_arabiy (Asosiy)\n"
        " - @V001VB (Zaxira)\n\n"
        "📩 Xizmatlardan birini tanlash uchun quyidagi menyudan foydalaning."
    )

def main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
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
    keyboard.add(*buttons)
    return keyboard

def service_panel_keyboard(service_name):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    # Example buttons, customize for each service
    if service_name == "Umra Paketlari":
        keyboard.add(
            types.InlineKeyboardButton("Standard Paket", callback_data="umra_standard"),
            types.InlineKeyboardButton("VIP Paket", callback_data="umra_vip"),
        )
    elif service_name == "Saudiya Vizalari":
        keyboard.add(
            types.InlineKeyboardButton("Umra Viza", callback_data="visa_umra"),
            types.InlineKeyboardButton("Turistik Viza", callback_data="visa_tourist"),
        )
    elif service_name == "Rawdah Tasrihi":
        keyboard.add(
            types.InlineKeyboardButton("Tasrih olish", callback_data="tasreh_order"),
        )
    elif service_name == "Transport Xizmatlari":
        keyboard.add(
            types.InlineKeyboardButton("Makkaga Transport", callback_data="transport_makka"),
            types.InlineKeyboardButton("Madina Transport", callback_data="transport_madina"),
        )
    elif service_name == "HHR Poyezd Chiptalari":
        keyboard.add(
            types.InlineKeyboardButton("Madina – Makkah", callback_data="train_mm"),
            types.InlineKeyboardButton("Riyadh – Dammam", callback_data="train_rd"),
        )
    elif service_name == "Guruhlik Ovqatlanish":
        keyboard.add(
            types.InlineKeyboardButton("Ovqat Buyurtma", callback_data="group_food"),
        )
    elif service_name == "Donat Qilish":
        keyboard.add(
            types.InlineKeyboardButton("Donat qilish", callback_data="donate"),
        )
    keyboard.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu"))
    return keyboard

# --- Handlers ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_name = message.from_user.first_name or "Hurmatli mijoz"
    await message.answer(get_welcome_message(user_name), reply_markup=main_menu_keyboard())

@dp.message_handler(lambda m: m.text == "❌ Bekor Qilish")
async def cancel_order(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Buyurtma bekor qilindi. Yana xohlasangiz, boshlash uchun /start buyrug‘ini bosing.",
                         reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(lambda m: m.text in [
    "🕋 Umra Paketlari",
    "🛂 Saudiya Vizalari",
    "🌟 Rawdah Tasrihi",
    "🚖 Transport Xizmatlari",
    "🚄 HHR Poyezd Chiptalari",
    "🍽️ Guruhlik Ovqatlanish",
    "🎁 Donat Qilish"
])
async def service_selected(message: types.Message, state: FSMContext):
    service = message.text
    await state.update_data(chosen_service=service)
    kb = service_panel_keyboard(service)
    await message.answer(f"✅ Siz <b>{service}</b> bo‘limidasiz. Quyidagi xizmatlardan birini tanlang:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith(("umra_", "visa_", "tasreh_", "transport_", "train_", "group_food", "donate", "back_to_menu")))
async def process_service_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "back_to_menu":
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, "Bosh menyuga qaytdingiz.", reply_markup=main_menu_keyboard())
        return

    # Bu yerda har bir xizmat uchun tafsilotlar va buyurtma bosqichlari qo‘shiladi
    if data.startswith("umra_"):
        # Misol uchun, Umra paketlari
        if data == "umra_standard":
            text = (
                "🕋 <b>Umra Standard Paket</b>\n\n"
                "Sizga arzon va sifatli Umra paketini taklif qilamiz. Barcha asosiy xizmatlar kiradi.\n\n"
                "Qo‘shimcha ma’lumot va buyurtma uchun adminlarimizga murojaat qiling."
            )
        elif data == "umra_vip":
            text = (
                "🕋 <b>Umra VIP Paket</b>\n\n"
                "Eng yuqori sifatdagi xizmatlar, eksklyuziv joylar va qulayliklar.\n\n"
                "Buyurtma berish uchun adminlar bilan bog‘laning."
            )
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, text)
        return

    elif data.startswith("visa_"):
        if data == "visa_umra":
            text = (
                "🛂 <b>Umra Viza</b>\n\n"
                "Umra ziyorati uchun maxsus viza xizmatlari.\n\n"
                "Buyurtma uchun adminlar bilan bog‘laning."
            )
        elif data == "visa_tourist":
            text = (
                "🛂 <b>Turistik Viza</b>\n\n"
                "Saudiya Arabistoni uchun turistik viza xizmatlari.\n\n"
                "Qo‘shimcha ma’lumot va buyurtma uchun adminlarga murojaat qiling."
            )
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, text)
        return

    elif data == "tasreh_order":
        text = (
            "🌟 <b>Rawdah Tasrihi</b>\n\n"
            "Rawdah maydoniga tasrih olish xizmati.\n"
            "Iltimos, buyurtma berish uchun biz bilan bog‘laning."
        )
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, text)
        return

    elif data.startswith("transport_"):
        if data == "transport_makka":
            text = (
                "🚖 <b>Makkaga Transport</b>\n\n"
                "Qulay va ishonchli transport xizmatlari Makkaga yetib borish uchun."
            )
        elif data == "transport_madina":
            text = (
                "🚖 <b>Madina Transport</b>\n\n"
                "Madina shahrida transport xizmatlari."
            )
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, text)
        return

    elif data.startswith("train_"):
        if data == "train_mm":
            text = (
                "🚄 <b>Madina – Makkah</b>\n\n"
                "Tezkor HHR poezd chiptalari.\n"
                "Buyurtma berish uchun adminlar bilan bog‘laning."
            )
        elif data == "train_rd":
            text = (
                "🚄 <b>Riyadh – Dammam</b>\n\n"
                "Saudiya poezd chiptalari.\n"
                "Qo‘shimcha ma’lumot uchun adminlarga murojaat qiling."
            )
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, text)
        return

    elif data == "group_food":
        text = (
            "🍽️ <b>Guruhlik Ovqatlanish</b>\n\n"
            "Guruh uchun ovqatlanish xizmatlari.\n"
            "Buyurtma va tafsilotlar uchun adminlar bilan bog‘laning."
        )
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, text)
        return

    elif data == "donate":
        text = (
            "🎁 <b>Donat Qilish</b>\n\n"
            "Bizga yordam berishni xohlasangiz, quyidagi kartalarga donat qilishingiz mumkin:\n"
            "• Uzcard: 8600 1234 5678 9012\n"
            "• Humo: 9860 1234 5678 9012\n"
            "• Visa/MasterCard: 4111 1111 1111 1111\n\n"
            "Har qanday yordam biz uchun juda qadrli! Rahmat! 🙏"
        )
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, text)
        return

# Qo'shimcha xabarlar va holatlar uchun boshqa handlerlar qo'shilishi mumkin

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

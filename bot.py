import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class OrderStates(StatesGroup):
    choosing_service = State()
    inputting_details = State()

def main_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🕋 Umra Paketlar", callback_data="umra_packages"),
        types.InlineKeyboardButton("🛂 Saudiya Vizalari", callback_data="saudi_visas"),
        types.InlineKeyboardButton("🌹 Ravza Tasreh", callback_data="rawdah_tasreh"),
        types.InlineKeyboardButton("🚖 Transport", callback_data="transport"),
        types.InlineKeyboardButton("🚄 HHR Poyezd", callback_data="train"),
        types.InlineKeyboardButton("🍽️ Guruhlik Ovqatlanish", callback_data="group_food"),
        types.InlineKeyboardButton("💳 To‘lov", callback_data="payments"),
        types.InlineKeyboardButton("🎁 Donat Qilish", callback_data="donate"),
    )
    return keyboard

def payment_info_kb():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("💳 Uzcard", callback_data="pay_uzcard"),
        types.InlineKeyboardButton("🏦 Humo", callback_data="pay_humo"),
        types.InlineKeyboardButton("💳 Visa", callback_data="pay_visa"),
        types.InlineKeyboardButton("🪙 Kripto", callback_data="pay_crypto"),
        types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_main"),
    )
    return keyboard

@dp.message_handler(commands=["start", "menu"])
async def cmd_start(message: types.Message):
    text = (
        f"Assalomu alaykum, {message.from_user.full_name}!\n\n"
        "UmraJet botiga xush kelibsiz!\n"
        "Quyidagi xizmatlardan birini tanlang:"
    )
    await message.answer(text, reply_markup=main_menu())
    await OrderStates.choosing_service.set()

@dp.callback_query_handler(state=OrderStates.choosing_service)
async def process_service_selection(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    user_id = callback.from_user.id

    # Umra paketlar
    if data == "umra_packages":
        text = (
            "🕋 <b>Umra Paketlar</b>\n\n"
            "• Standart paket: <b>1200$</b> dan boshlangan\n"
            "• VIP paket: <b>1800$</b> dan boshlangan\n\n"
            "Menejerlar:\n"
            "• @vip_arabiy (Asosiy)\n"
            "• @V001VB (Zaxira)"
        )
        await callback.message.answer(text, reply_markup=payment_info_kb())
        await state.update_data(service_detail="Umra Paketlar")
        await OrderStates.inputting_details.set()
        return

    # Saudiya vizalari
    if data == "saudi_visas":
        text = (
            "🛂 <b>Saudiya Vizalari</b>\n\n"
            "• Umra viza: <b>160$</b>\n"
            "• Turist viza: <b>120$</b>\n"
            "Guruhlarga narxlar kelishiladi.\n\n"
            "Menejerlar:\n"
            "• @vip_arabiy (Asosiy)\n"
            "• @V001VB (Zaxira)"
        )
        await callback.message.answer(text, reply_markup=payment_info_kb())
        await state.update_data(service_detail="Saudiya Vizalari")
        await OrderStates.inputting_details.set()
        return

    # Ravza Tasreh
    if data == "rawdah_tasreh":
        text = (
            "🌹 <b>Ravza Tasreh</b>\n\n"
            "• Viza berilsa: <b>15 SAR</b> / dona\n"
            "• Viza berilmasa: <b>20 SAR</b> / dona\n"
            "• 10 dona va undan ko‘p bo‘lsa yoki guruhlarga narxlar kelishiladi (arzonroq).\n\n"
            "Menejerlar:\n"
            "• @vip_arabiy (Asosiy)\n"
            "• @V001VB (Zaxira)"
        )
        await callback.message.answer(text, reply_markup=payment_info_kb())
        await state.update_data(service_detail="Ravza Tasreh")
        await OrderStates.inputting_details.set()
        return

    # Transport bo‘limi (oddiy, shunchaki habar)
    if data == "transport":
        text = (
            "🚖 <b>Transport Xizmatlari</b>\n\n"
            "Makkaga va Madinaga ishonchli transport xizmatlari.\n"
            "Menejerlar:\n"
            "• @vip_arabiy\n"
            "• @V001VB"
        )
        await callback.message.answer(text)
        return

    # HHR poyezd chiptalari
    if data == "train":
        text = (
            "🚄 <b>HHR Poyezd Chiptalari</b>\n\n"
            "• Madina – Makkah\n"
            "• Makkah – Madina\n"
            "• Riyadh – Dammam\n"
            "• Dammam – Riyadh\n\n"
            "Buyurtma uchun:\n"
            "• @vip_arabiy\n"
            "• @V001VB"
        )
        await callback.message.answer(text)
        return

    # Guruhlik ovqatlanish
    if data == "group_food":
        text = (
            "🍽️ <b>Guruhlik Ovqatlanish</b>\n\n"
            "Katta guruhlar uchun maxsus ovqatlanish xizmatlari.\n"
            "Narxlar va buyurtma uchun:\n"
            "• @vip_arabiy\n"
            "• @V001VB"
        )
        await callback.message.answer(text)
        return

    # To‘lovlar bo‘limi
    if data == "payments":
        text = (
            "💳 <b>To‘lov Tizimlari</b>\n\n"
            "Quyidagi to‘lov usullaridan birini tanlang:"
        )
        await callback.message.answer(text, reply_markup=payment_info_kb())
        return

    # Donat qilish
    if data == "donate":
        text = (
            "🎁 <b>Donat Qilish</b>\n\n"
            "Bizga yordam bermoqchi bo‘lsangiz, quyidagi usullar orqali donat qilishingiz mumkin:\n\n"
            "Uzcard:\n"
            "1 - 8600 0304 9680 2624 (Khamidov Ibodulloh)\n"
            "2 - 5614 6822 1222 3368 (Khamidov Ibodulloh)\n\n"
            "Humo:\n"
            "9860 1001 2621 9243 (Khamidov Ibodulloh)\n\n"
            "Visa:\n"
            "1 - 4140 8400 0184 8680 (Khamidov Ibodulloh)\n"
            "2 - 4278 3100 2389 5840 (Khamidov Ibodulloh)\n\n"
            "Crypto:\n"
            "USDT (Tron TRC20): TLGiUsNzQ8n31x3VwsYiWEU97jdftTDqT3\n"
            "ETH (BEP20): 0xa11fb72cc1ee74cfdaadb25ab2530dd32bafa8f8\n"
            "BTC (BEP20): 0xa11fb72cc1ee74cfdaadb25ab2530dd32bafa8f8\n\n"
            "Rahmat!\n"
            "Menejerlar:\n"
            "• @vip_arabiy\n"
            "• @V001VB"
        )
        await callback.message.answer(text)
        return

    # To‘lov kartalari ma’lumotlari (individual)
    if data.startswith("pay_"):
        pay_type = data[4:]
        if pay_type == "uzcard":
            text = (
                "💳 <b>Uzcard Kartalar</b>\n\n"
                "1 - <code>8600 0304 9680 2624</code> (Khamidov Ibodulloh)\n"
                "2 - <code>5614 6822 1222 3368</code> (Khamidov Ibodulloh)"
            )
        elif pay_type == "humo":
            text = (
                "🏦 <b>Humo Kartasi</b>\n\n"
                "<code>9860 1001 2621 9243</code> (Khamidov Ibodulloh)"
            )
        elif pay_type == "visa":
            text = (
                "💳 <b>Visa Kartalar</b>\n\n"
                "1 - <code>4140 8400 0184 8680</code> (Khamidov Ibodulloh)\n"
                "2 - <code>4278 3100 2389 5840</code> (Khamidov Ibodulloh)"
            )
        elif pay_type == "crypto":
            text = (
                "🪙 <b>Kripto Hisoblar</b>\n\n"
                "USDT (Tron TRC20): <code>TLGiUsNzQ8n31x3VwsYiWEU97jdftTDqT3</code>\n"
                "ETH (BEP20): <code>0xa11fb72cc1ee74cfdaadb25ab2530dd32bafa8f8</code>\n"
                "BTC (BEP20): <code>0xa11fb72cc1ee74cfdaadb25ab2530dd32bafa8f8</code>"
            )
        else:
            text = "To‘lov turi topilmadi."
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="payments"))
        await callback.message.answer(text, reply_markup=keyboard)
        return

    if data == "back_main":
        await callback.message.answer("Asosiy menyu:", reply_markup=main_menu())
        await OrderStates.choosing_service.set()
        return

    await callback.answer("Noto‘g‘ri yoki mavjud bo‘lmagan buyruq.", show_alert=True)

@dp.message_handler(state=OrderStates.inputting_details)
async def process_order_details(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    service = user_data.get("service_detail", "Xizmat")
    user_text = message.text.strip()

    await message.answer(
        f"✅ Buyurtma qabul qilindi!\n\n"
        f"<b>Xizmat:</b> {service}\n"
        f"<b>Foydalanuvchi ma'lumotlari:</b> {user_text}\n\n"
        f"Menejerlar tez orada siz bilan bog‘lanishadi.\n\n"
        f"📞 Menejerlar: @vip_arabiy, @V001VB",
        reply_markup=main_menu()
    )
    await state.finish()

    # Adminlarga xabar yuborish
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"🔔 <b>Yangi buyurtma</b>\n\n"
                f"<b>Xizmat:</b> {service}\n"
                f"<b>Foydalanuvchi:</b> @{message.from_user.username or message.from_user.full_name}\n"
                f"<b>Ma'lumotlar:</b> {user_text}"
            )
        except Exception as e:
            logging.error(f"Adminga xabar yuborishda xato: {e}")

@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer("Iltimos, menyudan xizmatni tanlang yoki /start yozing.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

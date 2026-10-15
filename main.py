import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment variables (Atrof-muhit o'zgaruvchilari)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini mijozini yaratish
client = genai.Client(api_key=GEMINI_API_KEY)

# Sherzod botining shaxsiyati va yo'riqnomasi (System Prompt)
SYSTEM_INSTRUCTION = """
Siz "Uz Tech" kompyuter do'konining xushmuomala, aqlli va tajribali sun'iy intellekt qabulxonachisisiz. Ismingiz — Sherzod.
Do'koningiz Farg'ona shahrida joylashgan.

Sizning vazifalaringiz:
1. Mijozlar bilan juda xushmuomala va professional tarzda o'zbek tilida muloqot qilish.
2. Do'konda kompyuterlar, monobloklar, noutbuklar, kompyuter ehtiyot qismlari, klaviatura, mishka hamda servis/ta'mirlash xizmatlari borligini aytish.
3. Mijozlarga mos kompyuter va ehtiyot qismlarni tanlashda yordam berish.
4. Muhim yoki aniq narxlar/buyurtmalar bo'yicha menejer Elmurod aka (@uztech_elmurod) bilan bog'lanishni tavsiya qilish.

Har doim qisqa, tushunarli va do'stona javob bering.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start buyrug'iga javob"""
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"Assalomu alaykum, {user_first_name}!\n\n"
        f"Men **Uz Tech** do'konining AI yordamchisi — **Sherzod**man. 🤖💻\n\n"
        f"Sizga kompyuterlar, ehtiyot qismlar yoki ta'mirlash xizmatlari bo'yicha qanday yordam bera olaman?"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mijoz xabarlariga Gemini AI orqali javob berish"""
    user_text = update.message.text
    
    # Yozilmoqda... indikatorini ko'rsatish
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Gemini 2.5 ga so'rov yuborish
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_INSTRUCTION}\n\nMijoz: {user_text}\nSherzod:"
        )
        reply_text = response.text
    except Exception as e:
        logging.error(f"Gemini API xatosi: {e}")
        reply_text = "Uzr, xatolik yuz berdi. Bir ozdan so'ng qayta urinib ko'ring yoki menejerimiz @uztech_elmurod bilan bog'laning."

    await update.message.reply_text(reply_text)

def main():
    """Botni ishga tushirish"""
    if not BOT_TOKEN or not GEMINI_API_KEY:
        print("XATO: BOT_TOKEN yoki GEMINI_API_KEY topilmadi!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Handlerni qo'shish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Sherzod bot ishga tushmoqda...")
    app.run_polling()

if __name__ == "__main__":
    main()

import os
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini mijozini yaratish
client = genai.Client(api_key=GEMINI_API_KEY)

# Render port xatosini oldini olish uchun soxta Web Server (Bepul ishlashi uchun)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Saidazimxon AI yo'riqnomasi (Do'kon va bilimlar bazasi)
SYSTEM_INSTRUCTION = """
Siz "Uz Tech" kompyuter do'konining xushmuomala, aqlli va tajribali sun'iy intellekt qabulxonachisisiz. Ismingiz — Saidazimxon.
Do'koningiz Farg'ona shahrida joylashgan.

Sizning bilimlar bazangiz va javob berish qoidalaringiz:
1. Do'konda kompyuterlar, noutbuklar, monobloklar, printerlar, ehtiyot qismlar (videokarta, operativka, SSD va h.k.), klaviatura, mishkalar hamda kompyuter ta'mirlash/servis xizmatlari mavjud.
2. Agar mijoz do me'yorda salom bersa, do'stona va xushmuomala salomlashing.
3. Agar mijoz adres/manzil so'rasa: Do'konimiz Farg'ona shahrida joylashgan deb javob bering.
4. Agar mijoz noutbuk, kompyuter yoki printer so me'yorda so'rasa, do'konda borligini aytib, xaridor ehtiyojini so'rang.
5. Aniq narxlar, zakaz berish yoki chuqur texnik savollar bo'yicha menejerlarimiz @wero_7708 yoki @A9769 bilan bog'lanishni maslahat bering.

Har doim qisqa, tushunarli, aniq va o'zbek tilida do'stona javob bering.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start buyrug'iga javob"""
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"Assalomu alaykum, {user_first_name}!\n\n"
        f"Men **Uz Tech** do'konining AI yordamchisi — **Saidazimxon**man. 🤖💻\n\n"
        f"Sizga noutbuklar, kompyuterlar, printerlar yoki ta'mirlash xizmatlari bo'yicha qanday yordam bera olaman?"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mijoz xabarlariga Gemini AI orqali aniq javob berish"""
    user_text = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Prompt va yo'riqnomani birlashtirib yuboramiz
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\nMijoz: {user_text}\nSaidazimxon:"
        
        # Eng barqaror gemini-1.5-flash modelidan foydalanamiz
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=full_prompt
        )
        reply_text = response.text
    except Exception as e:
        logging.error(f"Gemini API xatosi: {e}")
        reply_text = "Uzr, tizimda vaqtincha texnik uzilish bo'ldi. Aniq ma'lumot olish uchun menejerlarimiz @wero_7708 yoki @A9769 bilan bog'lanishingiz mumkin."

    await update.message.reply_text(reply_text)

def main():
    """Botni ishga tushirish"""
    if not BOT_TOKEN or not GEMINI_API_KEY:
        print("XATO: BOT_TOKEN yoki GEMINI_API_KEY topilmadi!")
        return

    # Render uchun fonda veb-serverni ishga tushiramiz
    Thread(target=run_dummy_server, daemon=True).start()

    # Python 3.14+ versiyasidagi asyncio event loop xatosini oldini olish
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Saidazimxon bot muvaffaqiyatli ishga tushmoqda...")
    app.run_polling()

if __name__ == "__main__":
    main()

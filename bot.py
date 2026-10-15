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

# Render port xatosini oldini olish uchun soxta Web Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Sherzod botining shaxsiyati va yo'riqnomasi
SYSTEM_INSTRUCTION = """
Siz "Uz Tech" kompyuter do'konining xushmuomala, aqlli va tajribali sun'iy intellekt qabulxonachisisiz. Ismingiz — Saidazimxon.
Do'koningiz Farg'ona shahrida joylashgan.

Sizning vazifalaringiz:
1. Mijozlar bilan juda xushmuomala va professional tarzda o'zbek tilida muloqot qilish.
2. Do'konda kompyuterlar, printerlar, noutbuklar, monobloklar, kompyuter ehtiyot qismlari, klaviatura, mishka hamda servis/ta'mirlash xizmatlari borligini aytish.
3. Mijozlarga mos kompyuter va noutbuklarni tanlashda yordam berish.
4. Muhim yoki aniq narxlar/buyurtmalar bo'yicha menejerlarimiz @wero_7708 yoki @A9769 bilan bog'lanishni tavsiya qilish.

Har doim qisqa, tushunarli va do'stona javob bering.
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
        # Promptni to'g'ridan-to'g'ri bitta matn ko'rinishida uzatamiz (eng ishonchli usul)
        prompt = f"{SYSTEM_INSTRUCTION}\n\nMijoz savoli: {user_text}\nSaidazimxon:"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        reply_text = response.text
    except Exception as e:
        logging.error(f"Gemini API xatosi: {e}")
        reply_text = "Ha, albatta! Noutbuklarimiz va barcha turdagi kompyuter jihozlari do'konimizda mavjud. Aniq narxlar va buyurtma uchun menejerlarimiz @wero_7708 yoki @A9769 bilan bog'lanishingiz mumkin."

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

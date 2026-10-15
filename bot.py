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

# Kanalingiz havolasi va nomi
CHANNEL_LINK = "https://t.me/uztech_computers"
CHANNEL_NAME = "@uztech\_computers"  # Markdown buzilmasligi uchun pastki chiziq ekranlandi

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

# Manzil va ismlarga to'g'ri berkitilgan havolali kontaktlar dizayni
CONTACT_INFO = f"""
📍 **Do'konimiz manzili:** Farg'ona shahri ([Google Maps lokatsiyasi](https://goo.gl/maps/NeV8ogH4ARYnovWi6))

👨🏼‍⚖️ **SOTUV MENEJERLARI:**
• 📞 [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)
• 📞 [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)

🌐 **BIZNING IJTIMOIY TARMOQLAR:**
• 📢 [Telegram kanalimiz]({CHANNEL_LINK})
• 📸 [Instagram sahifamiz](https://www.instagram.com/uzteck/)
"""

# Saidazimxon botining yo'riqnomasi
SYSTEM_INSTRUCTION = f"""
Siz "Uz Tech" kompyuter do'konining xushmuomala, bilimdon va samimiy sun'iy intellekt yordamchisisiz. Ismingiz — Saidazimxon. 
Do'konimiz Farg'ona shahrida joylashgan.

Qoidalar:
1. Mijozlar bilan o'zbek tilida, xuddi inson kabi samimiy, iliq va ravon muloqot qiling.
2. {CHANNEL_LINK} kanalimizdagi barcha noutbuklar, kompyuterlar, printerlar va ehtiyot qismlarni yaxshi bilasiz. Mijozga mos mahsulotlarni tavsiya qiling.
3. Aniq narxlar va buyurtma uchun doimo menejerlarimizga yo'naltiring. Bunda ismlarini albatta quyidagi Markdown formatida yozing:
   - [Elmurod](https://t.me/wero_7708)
   - [Axrorbek](https://t.me/A9769)
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start buyrug'iga javob"""
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"Assalomu alaykum, {user_first_name} aka!\n\n"
        f"Men **Uz Tech** do'konining sun'iy intellekt yordamchisi — **Saidazimxon**man. 🤖💻\n\n"
        f"Sizga qanday kompyuter, noutbuk yoki ehtiyot qismlar bo'yicha yordam kerak? Bemalol murojaat qilishingiz mumkin!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mijoz xabarlariga javob berish"""
    user_text = update.message.text
    text_lower = user_text.lower()
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Manzil yoki lokatsiya so'ralganda tayyor kontaktlarni chiqaradi
    if any(word in text_lower for word in ["manzil", "adres", "lokatsiya", "lokatsya", "qayerda", "qayerdasiz", "kontakt", "telefon", "nomir"]):
        await update.message.reply_text(CONTACT_INFO, parse_mode="Markdown", disable_web_page_preview=True)
        return

    try:
        prompt = f"{SYSTEM_INSTRUCTION}\n\nMijozning xabari: {user_text}\nSaidazimxon javobi:"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        reply_text = response.text
    except Exception as e:
        logging.error(f"Gemini API xatosi: {e}")
        if "salom" in text_lower or "assalom" in text_lower:
            reply_text = "Va alaykum assalom! Uz Tech do'koniga xush kelibsiz. Qanday texnika qidirayotgan edingiz, bemalol ayting."
        else:
            reply_text = (
                f"Ha, albatta! Ayni paytda {CHANNEL_NAME} kanalimizda ko'plab noutbuklar va kompyuter jihozlari mavjud.\n\n"
                f"Aniq narxlar va buyurtma berish uchun menejerlarimiz bilan bog'lanishingiz mumkin:\n"
                f"• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)\n"
                f"• [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)"
            )

    await update.message.reply_text(reply_text, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    """Botni ishga tushirish"""
    if not BOT_TOKEN or not GEMINI_API_KEY:
        print("XATO: BOT_TOKEN yoki GEMINI_API_KEY topilmadi!")
        return

    Thread(target=run_dummy_server, daemon=True).start()

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

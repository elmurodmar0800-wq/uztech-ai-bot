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

# Kanalingiz nomi (bot shu yerdagi ma'lumotlarga tayanadi)
CHANNEL_USERNAME = "@uztech_computers"

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

# Aloqa va manzil ma'lumotlari dizayni
CONTACT_INFO = """
📍 **Do'konimiz manzili:** Farg'ona shahri ([Google Maps lokatsiyasi](https://goo.gl/maps/NeV8ogH4ARYnovWi6))

👨🏼‍⚖️ **SOTUV MENEJERLARI:**
• 📞 **Elmurod:** [+998 93 641 0800](tel:+998936410800) — [@wero_7708](https://t.me/wero_7708)
• 📞 **Axrorbek:** [+998 93 976 9769](tel:+998939769769) — [@A9769](https://t.me/A9769)

🌐 **BIZNING IJTIMOIY TARMOQLAR:**
• 📢 [Telegram kanalimiz](https://t.me/uztech_computers)
• 📸 [Instagram sahifamiz](https://www.instagram.com/uzteck/)
"""

# Saidazimxon botining kengaytirilgan yo'riqnomasi (Kanal mahsulotlari tahlili bilan)
SYSTEM_INSTRUCTION = """
Siz "Uz Tech" kompyuter do'konining xushmuomala, aqlli va tajribali sun'iy intellekt qabulxonachisisiz. Ismingiz — Saidazimxon.
Do'koningiz Farg'ona shahrida joylashgan.

Vazifalaringiz va qoidalaringiz:
1. Mijozlar bilan o'zbek tilida, juda xushmuomala va professional tarzda muloqot qiling.
2. @uztech_computers kanalimizga tashlanadigan so'nggi noutbuklar, kompyuterlar, printerlar, videokartalar, protsessorlar, SSD va boshqa barcha ehtiyot qismlarni yaxshi bilasiz deb hisoblang. Mijoz biror narsa so'rasa, do'konimizda bor deb javob bering va uning xarakteristikasiga mos keladigan mahsulotni tavsiya qiling.
3. Aniq narxlar, oxirgi chegirmalar yoki buyurtma berish bo'yicha har doim menejerlarimiz Elmurod (@wero_7708) yoki Axrorbek (@A9769) bilan bog'lanishni tavsiya qiling.
4. Javoblaringiz qisqa, aniq va foydali bo'lsin.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start buyrug'iga javob"""
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"Assalomu alaykum, {user_first_name}!\n\n"
        f"Men **Uz Tech** do'konining AI yordamchisi — **Saidazimxon**man. 🤖💻\n\n"
        f"Sizga noutbuklar, kompyuterlar, ehtiyot qismlar yoki ta'mirlash xizmatlari bo'yicha qanday yordam bera olaman?"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mijoz xabarlariga kanal ma'lumotlari va Gemini orqali javob berish"""
    user_text = update.message.text
    text_lower = user_text.lower()
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Manzil yoki lokatsiya so'ralganda tayyor chiroyli kontaktlarni chiqaradi
    if any(word in text_lower for word in ["manzil", "adres", "lokatsiya", "lokatsya", "qayerda", "qayerdasiz", "kontakt", "telefon", "nomir"]):
        await update.message.reply_text(CONTACT_INFO, parse_mode="Markdown", disable_web_page_preview=True)
        return

    try:
        # Promptga kanal mahsulotlarini tahlil qilish bo'yicha ko'rsatma beramiz
        prompt = (
            f"{SYSTEM_INSTRUCTION}\n\n"
            f"Eslatma: Mijoz @uztech_computers kanalimizdagi mahsulotlar bo'yicha murojaat qilmoqda. "
            f"Agar mijoz mahsulot so'rasa, uni kanalimizdagi mavjud assortimentga qarab tavsiya qiling, "
            f"xarakteristikasini tushuntiring va narxi hamda buyurtma uchun menejerlarga yo'naltiring.\n\n"
            f"Mijoz savoli: {user_text}\nSaidazimxon:"
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        reply_text = response.text
    except Exception as e:
        logging.error(f"Gemini API xatosi: {e}")
        reply_text = (
            f"Ha, albatta! @uztech_computers kanalimizdagi barcha turdagi noutbuklar, kompyuterlar va ehtiyot qismlar do'konimizda mavjud.\n\n"
            f"Aniq narxlar, rasmlari va buyurtma uchun menejerlarimizga murojaat qiling:\n"
            f"• **Elmurod:** [+998 93 641 0800](tel:+998936410800) — [@wero_7708](https://t.me/wero_7708)\n"
            f"• **Axrorbek:** [+998 93 976 9769](tel:+998939769769) — [@A9769](https://t.me/A9769)"
        )

    await update.message.reply_text(reply_text, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    """Botni ishga tushirish"""
    if not BOT_TOKEN or not GEMINI_API_KEY:
        print("XATO: BOT_TOKEN yoki GEMINI_API_KEY topilmadi!")
        return

    # Render uchun fonda veb-serverni ishga tushiramiz
    Thread(target=run_dummy_server, daemon=True).start()

    # Python 3.14+ asyncio event loop xatosini oldini olish
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

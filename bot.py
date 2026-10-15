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

# Do'kon ma'lumotlari
CONTACT_INFO = """
📍 **Do'konimiz manzili:** Farg'ona shahri ([Google Maps lokatsiyasi](https://goo.gl/maps/NeV8ogH4ARYnovWi6))

⏰ **Ish vaqtimiz:** Dushanbadan shanbagacha, ertalabki 09:00 dan kechki 19:00 gacha. (Yakshanba dam olish kuni)

👨🏼‍⚖️ **SOTUV MENEJERLARI:**
• 📞 [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)
• 📞 [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)

🌐 **BIZNING IJTIMOIY TARMOQLAR:**
• 📢 [Telegram kanalimiz](https://t.me/uztech_computers)
• 📸 [Instagram sahifamiz](https://www.instagram.com/uzteck/)
"""

# Saidazimxonning erkin va aqlli xarakteri
SYSTEM_INSTRUCTION = """
Sen Farg'ona shahridagi "Uz Tech" kompyuter do'konining sun'iy intellekt yordamchisisisan. Isming — Saidazimxon.
Mijozlar bilan o'zbek tilida juda xushmuomala, ochiqko'ngil, samimiy va erkin muloqot qil. Robotga o'xshab quruq takroriy gaplarni yozma.
Do'konimizda noutbuklar, kompyuterlar, printerlar, Wi-Fi routerlar, videokartalar va barcha turdagi ehtiyot qismlar mavjud.
Ish vaqtimiz: Dushanbadan shanbagacha, soat 09:00 dan 19:00 gacha. Yakshanba dam olish kuni.
Agar mijoz aniq narx, chegirma, zakaz yoki mahsulotning narxini so'rasa, quyidagi menejerlarimizga yo'naltir:
- [Elmurod](https://t.me/wero_7708)
- [Axrorbek](https://t.me/A9769)
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"Assalomu alaykum, {user_first_name} aka!\n\n"
        f"Men **Uz Tech** do'konining yordamchisi — **Saidazimxon**man. 🤖💻\n\n"
        f"Sizga noutbuklar, printerlar, routerlar yoki kompyuter qismlari bo'yicha qanday yordam bera olaman?"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    text_lower = user_text.lower()
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Manzil yoki aniq ish vaqti so'ralganda to'g'ridan-to'g'ri kontaktni beramiz
    if any(word in text_lower for word in ["manzil", "adres", "lokatsiya", "qayerda", "kontakt", "telefon", "ish vaqti", "nechigacha", "ishlaysiz", "ochiqmisiz"]):
        await update.message.reply_text(CONTACT_INFO, parse_mode="Markdown", disable_web_page_preview=True)
        return

    try:
        # Gemini AI orqali erkin va jonli javob olish
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\nMijoz xabari: {user_text}\nSaidazimxon javobi:"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt
        )
        reply_text = response.text
        
        if not reply_text:
            raise Exception("Bo'sh javob")
            
    except Exception as e:
        logging.error(f"Gemini API xatosi: {e}")
        # Agar tarmoqda kichik uzilish bo'lsa ishlatiladigan tabiiy zaxira
        if "salom" in text_lower:
            reply_text = "Va alaykum assalom! Uz Tech do'koniga xush kelibsiz. Qanday texnika qidirayotgan edingiz?"
        else:
            reply_text = (
                f"Ayni paytda do'konimizda va [Telegram kanalimizda](https://t.me/uztech_computers) ko'plab texnikalar mavjud.\n\n"
                f"Batafsil ma'lumot va narxlar uchun menejerlarimizga yozishingiz mumkin:\n"
                f"• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)\n"
                f"• [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)"
            )

    await update.message.reply_text(reply_text, parse_mode="Markdown", disable_web_page_preview=True)

def main():
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

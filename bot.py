import os
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini API ni sozlash
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

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

SYSTEM_PROMPT = """
Sen Farg'ona shahridagi "Uz Tech" kompyuter do'konining sun'iy intellekt yordamchisisisan. Isming — Saidazimxon.
Mijozlar bilan o'zbek tilida juda xushmuomala, ochiqko'ngil va erkin muloqot qil. Quruq bir xil qolipdagi takroriy gaplarni zinhor yozma.
Do'konimizda noutbuklar, kompyuterlar, printerlar (masalan MF3010 va boshqalar), Wi-Fi routerlar va barcha turdagi ehtiyot qismlar mavjud.
Ish vaqtimiz: Dushanbadan shanbagacha, soat 09:00 dan 19:00 gacha.
Agar mijoz aniq narx, chegirma, zakaz yoki texnikalarning batafsil narxini so'rasa, quyidagi menejerlarimizga yo'naltir:
- [Elmurod](https://t.me/wero_7708)
- [Axrorbek](https://t.me/A9769)
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"Assalomu alaykum, {user_first_name} aka!\n\n"
        f"Men **Uz Tech** do'konining sun'iy intellekt yordamchisi — **Saidazimxon**man. 🤖💻\n\n"
        f"Sizga qanday texnika, printer yoki ehtiyot qismlar bo'yicha yordam kerak? Bemalol so'rashingiz mumkin!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    text_lower = user_text.lower()
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Manzil yoki ish vaqti so'ralganda tayyor ma'lumotni chiqaradi
    if any(word in text_lower for word in ["manzil", "adres", "lokatsiya", "qayerda", "kontakt", "telefon", "ish vaqti", "nechigacha", "vaqt", "ishlaysiz", "shanba", "yakshanba"]):
        await update.message.reply_text(CONTACT_INFO, parse_mode="Markdown", disable_web_page_preview=True)
        return

    try:
        # To'g'ridan-to'g'ri AI modelidan javob olish
        prompt = f"{SYSTEM_PROMPT}\n\nMijoz savoli: {user_text}\nSaidazimxon javobi:"
        response = ai_model.generate_content(prompt)
        reply_text = response.text
        
        if not reply_text:
            raise Exception("Bo'sh javob")
            
    except Exception as e:
        logging.error(f"Gemini API xatosi: {e}")
        if "salom" in text_lower:
            reply_text = "Va alaykum assalom! Uz Tech do'koniga xush kelibsiz. Qanday texnika qidirayotgan edingiz?"
        elif "printer" in text_lower or "mf3010" in text_lower:
            reply_text = f"Ha, printerlarimiz va kserokopiya apparatlari (shu jumladan MF3010 modellari ham) bor! Aniq narxlari va qolgan-ketganini bilish uchun menejerimiz [Elmurod](https://t.me/wero_7708) bilan bog'lanishingiz mumkin."
        else:
            reply_text = f"Tushundim! Bu bo'yicha batafsil ma'lumot olish uchun menejerlarimizga yozishingiz mumkin:\n• [Elmurod](https://t.me/wero_7708)\n• [Axrorbek](https://t.me/A9769)"

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

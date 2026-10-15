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

# Kanalingiz havolasi
CHANNEL_LINK = "https://t.me/uztech_computers"

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

# Saidazimxon botining erkin va aqlli yo'riqnomasi
SYSTEM_INSTRUCTION = f"""
Sen "Uz Tech" kompyuter do'konining aqlli, bilimdon va samimiy sun'iy intellekt yordamchisisisan. Isming — Saidazimxon. 
Do'konimiz Farg'ona shahrida joylashgan.

Qoidalar:
1. Mijozlar bilan o'zbek tilida, xuddi tirik inson kabi erkin, do'stona va ravon muloqot qil. Quruq bir xil qolipdagi javoblarni yozma.
2. Kompyuterlar, noutbuklar, printerlar va ehtiyot qismlar bo'yicha har qanday savolga o'zing mustaqil mazmunli javob ber, tushuntir va maslahat ber.
3. Agar mijoz do'konimizda yo'q narsani so'rasa (masalan, kitob yoki qalam), buni madaniyatli va hazilomuz tarzda tushuntirib, bizda kompyuter texnikalari borligini ayt.
4. Aniq narxlar yoki buyurtma berish haqida gap ketganda, menejerlarimizni quyidagi formatda ko'rsat:
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
    """Mijoz xabarlariga Gemini orqali erkin javob berish"""
    user_text = update.message.text
    text_lower = user_text.lower()
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Manzil yoki lokatsiya so'ralganda tayyor kontaktlarni chiqaradi
    if any(word in text_lower for word in ["manzil", "adres", "lokatsiya", "lokatsya", "qayerda", "qayerdasiz", "kontakt", "telefon", "nomir"]):
        await update.message.reply_text(CONTACT_INFO, parse_mode="Markdown", disable_web_page_preview=True)
        return

    try:
        # Promptni yanada aniq va qisqa qilib tuzamiz
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\nMijoz: {user_text}\nSaidazimxon:"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt
        )
        reply_text = response.text
        
        # Agar javob bo'sh kelsa
        if not reply_text:
            raise ValueError("Bo'sh javob keldi")
            
    except Exception as e:
        logging.error(f"Gemini API xatosi: {e}")
        # Tabiiy va moslashuvchan zaxira javob
        if "salom" in text_lower or "assalom" in text_lower:
            reply_text = "Va alaykum assalom! Uz Tech do'koniga xush kelibsiz. Qanday texnika qidirayotgan edingiz?"
        elif "printer" in text_lower:
            reply_text = f"Ha, ofis va uy uchun har xil turdagi printerlarimiz bor! Aniq narxlari va qaysi modellari qolganini bilish uchun menejerimiz [Elmurod](https://t.me/wero_7708) bilan bog'lanishingiz mumkin."
        else:
            reply_text = (
                f"Tushundim! Bu bo'yicha batafsil ma'lumot va narxlarni bilish uchun menejerlarimizga yozishingiz mumkin:\n\n"
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

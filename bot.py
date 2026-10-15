import os
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")

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

# Do'kon ma'lumotlari va kontaktlar
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"Assalomu alaykum, {user_first_name} aka!\n\n"
        f"Men **Uz Tech** do'konining yordamchisi — **Saidazimxon**man. 🤖💻\n\n"
        f"Sizga noutbuklar, printerlar, routerlar yoki ehtiyot qismlar bo'yicha qanday yordam bera olaman?"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    text_lower = user_text.lower()
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # 1. Salomlashish
    if any(word in text_lower for word in ["salom", "assalom", "qalaysiz", "yaxshimisiz"]):
        reply_text = "Va alaykum assalom! Uz Tech do'koniga xush kelibsiz. Ishlarimiz yaxshi, o'zingiz tuzumisiz? Qanday texnika qidirayotgan edingiz?"

    # 2. Manzil, ish vaqti yoki vaqtga oid so'rovlar
    elif any(word in text_lower for word in ["manzil", "adres", "lokatsiya", "qayerda", "kontakt", "telefon", "ish vaqti", "nechigacha", "vaqt", "ishlaysiz", "shanba", "yakshanba", "kun", "ishda"]):
        reply_text = CONTACT_INFO

    # 3. Printerlar (L3350, MF3010 va h.k.)
    elif any(word in text_lower for word in ["printer", "l3350", "mf3010", "kserokopiya", "skaner"]):
        reply_text = (
            "Ha, albatta! Do'konimizda ofis va uy uchun har xil turdagi printerlar (shu jumladan L3350, MF3010 modellari va boshqalar) mavjud.\n\n"
            "Aniq narxlari, qolgan-ketganini bilish va buyurtma berish uchun menejerimiz bilan bog'lanishingiz mumkin:\n"
            "• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)"
        )

    # 4. Noutbuk va kompyuterlar
    elif any(word in text_lower for word in ["noutbuk", "kompyuter", "notebook", "laptop", "pc", "noutbukchi"]):
        reply_text = (
            "Ha, do'konimizda o'qish, ofis ishlari va o'yinlar uchun noutbuklar hamda kompyuterlar yetarli miqdorda bor!\n\n"
            "Sizga kerak bo'lgan xarakteristikalarni tanlash va narxlarini kelishish uchun menejerlarimizga yozishingiz mumkin:\n"
            "• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)\n"
            "• [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)"
        )

    # 5. Wi-Fi router va tarmoq jihozlari
    elif any(word in text_lower for word in ["wifi", "wi-fi", "router", "rotir", "rotor", "internet"]):
        reply_text = (
            "Ha, uy va ofis uchun Wi-Fi routerlar hamda tarmoq qurilmalari do'konimizda bor!\n\n"
            "Ularning turlari va narxlarini bilish uchun menejerlarimizga murojaat qilishingiz mumkin:\n"
            "• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)"
        )

    # 6. Boshqa har qanday savollar uchun
    else:
        reply_text = (
            "Tushundim! Bu mahsulot yoki xizmat bo'yicha aniq ma'lumot va narxlarni quyidagi menejerlarimizdan olishingiz mumkin:\n\n"
            "• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)\n"
            "• [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)\n\n"
            "Shuningdek, barcha yangi kelgan tovarlarimizni [Telegram kanalimizda](https://t.me/uztech_computers) kuzatib borishingiz mumkin!"
        )

    await update.message.reply_text(reply_text, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    if not BOT_TOKEN:
        print("XATO: BOT_TOKEN topilmadi!")
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

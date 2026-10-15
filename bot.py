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

# Do'kon ma'lumotlari va kontaktlar (Narxlar qat'iyan yozilmaydi, menejerlarga yo'naltiriladi)
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

def load_products_db():
    """Mahsulotlar bazasi faylini o'qish"""
    if os.path.exists("products.txt"):
        with open("products.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "Hozircha baza bo'sh."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"Assalomu alaykum, {user_first_name} aka!\n\n"
        f"Men **Uz Tech** do'konining yordamchisi — **Saidazimxon**man. 🤖💻\n\n"
        f"Sizga noutbuklar, printerlar, videokartalar, monitorlar yoki aksessuarlar bo'yicha qanday yordam bera olaman?"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    text_lower = user_text.lower()
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # 1. Kimligini so'raganda
    if any(word in text_lower for word in ["kimsiz", "sen kimsiz", "isming", "oting"]):
        reply_text = "Men — 'Uz Tech' do'konining sun'iy intellekt yordamchisi Saidazimxonman! 🤖💻 Do'konimizdagi barcha mahsulotlar va texnikalar bo'yicha ma'lumot berishga tayyorman."

    # 2. Salomlashish
    elif any(word in text_lower for word in ["salom", "assalom", "qalaysiz", "yaxshimisiz"]):
        reply_text = "Va alaykum assalom! Uz Tech do'koniga xush kelibsiz. Ishlarimiz yaxshi, o'zingiz tuzumisiz? Qanday texnika yoki ehtiyot qism qidirayotgan edingiz?"

    # 3. Manzil, ish vaqti yoki kontaktlar
    elif any(word in text_lower for word in ["manzil", "adres", "lokatsiya", "qayerda", "kontakt", "telefon", "ish vaqti", "nechigacha", "vaqt", "ishlaysiz", "shanba", "yakshanba", "kun", "ishda"]):
        reply_text = CONTACT_INFO

    else:
        # Bazadan kalit so'z bo'yicha qidirish
        db_content = load_products_db()
        matched_lines = []
        keywords = text_lower.split()
        
        for line in db_content.split("\n"):
            if any(kw in line.lower() for kw in keywords if len(kw) > 2):
                matched_lines.append(line)
        
        if matched_lines:
            # Ko'p chiqib ketmasligi uchun eng ko'pi bilan 8 ta mos tovarni ko'rsatamiz
            found_text = "\n".join(matched_lines[:8])
            reply_text = (
                f"Ha, do'konimizda shular mavjud:\n\n{found_text}\n\n"
                f"💳 **Narxlar va buyurtma bo'yicha aniq ma'lumot olish uchun menejerlarimizga murojaat qiling:**\n"
                f"• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)\n"
                f"• [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)"
            )
        else:
            reply_text = (
                f"Tushundim! Bu mahsulot yoki uning narxi bo'yicha aniq ma'lumotni quyidagi menejerlarimizdan olishingiz mumkin:\n\n"
                f"• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)\n"
                f"• [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)\n\n"
                f"Shuningdek, barcha yangi kelgan tovarlarimizni [Telegram kanalimizda](https://t.me/uztech_computers) kuzatib borishingiz mumkin!"
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

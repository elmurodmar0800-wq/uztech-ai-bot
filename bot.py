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
        f"Sizga noutbuklar, videokartalar, printerlar yoki boshqa ehtiyot qismlar bo'yicha qanday yordam bera olaman?"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    text_lower = user_text.lower()
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # 1. Kimligini so'raganda
    if any(word in text_lower for word in ["kimsiz", "sen kimsiz", "isming", "oting"]):
        reply_text = "Men — 'Uz Tech' do'konining sun'iy intellekt yordamchisi Saidazimxonman! 🤖💻 Do'konimizdagi barcha texnikalar va mahsulotlar bo'yicha sizga ma'lumot berishga tayyorman."

    # 2. Salomlashish
    elif any(word in text_lower for word in ["salom", "assalom", "qalaysiz", "yaxshimisiz"]):
        reply_text = "Va alaykum assalom! Uz Tech do'koniga xush kelibsiz. Ishlarimiz yaxshi, o'zingiz tuzumisiz? Qanday texnika yoki ehtiyot qism qidirayotgan edingiz?"

    # 3. Manzil, ish vaqti yoki kontaktlar
    elif any(word in text_lower for word in ["manzil", "adres", "lokatsiya", "qayerda", "kontakt", "telefon", "ish vaqti", "nechigacha", "vaqt", "ishlaysiz", "shanba", "yakshanba", "kun", "ishda"]):
        reply_text = CONTACT_INFO

    # 4. Printerlar, katrij va bo'yoqlar
    elif any(word in text_lower for word in ["printer", "l3350", "l18050", "mf3010", "kserokopiya", "skaner", "kraska", "katrij", "kartrij"]):
        reply_text = (
            "Ha, albatta! Do'konimizda ofis va uy uchun har xil turdagi printerlar (shu jumladan L3350, L18050, MF3010 modellari), katrijlar va bo'yoqlar mavjud.\n\n"
            "Aniq narxlari va buyurtma berish uchun menejerimiz bilan bog'lanishingiz mumkin:\n"
            "• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)"
        )

    # 5. Videokartalar (vidio karta, 3050, rx, rtx va h.k.)
    elif any(word in text_lower for word in ["videokarta", "vidio karta", "video karta", "3050", "4060", "rx", "rtx", "gtx"]):
        reply_text = (
            "Ha, do'konimizda o'yinlar va professional ishlar uchun har xil turdagi videokartalar (jumladan RTX 3050 va boshqa modellar) mavjud!\n\n"
            "Ularning narxlari va mavjudligini aniqlash uchun menejerlarimizga yozishingiz mumkin:\n"
            "• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)\n"
            "• [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)"
        )

    # 6. Noutbuk, kompyuter, monoblok va ichki qismlar
    elif any(word in text_lower for word in ["noutbuk", "kompyuter", "notebook", "laptop", "pc", "noutbukchi", "monoblok", "protsessor", "prosesor", "operativka", "ram", "ssd", "hdd", "keys"]):
        reply_text = (
            "Ha, do'konimizda o'qish, ofis va o'yinlar uchun noutbuklar, kompyuterlar, monobloklar hamda barcha turdagi butlovchi qismlar yetarli miqdorda bor!\n\n"
            "Sizga kerak bo'lgan texnika va uning narxlarini kelishish uchun menejerlarimizga yozishingiz mumkin:\n"
            "• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)\n"
            "• [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)"
        )

    # 7. Tarmoq jihozlari (Wi-Fi router, kommutator, switch)
    elif any(word in text_lower for word in ["wifi", "wi-fi", "router", "rotir", "rotor", "internet", "kommutator", "switch", "svich"]):
        reply_text = (
            "Ha, do'konimizda uy va ofis uchun Wi-Fi routerlar, kommutatorlar (switch) hamda tarmoq qurilmalari mavjud!\n\n"
            "Ularning turlari va narxlarini bilish uchun menejerlarimizga murojaat qilishingiz mumkin:\n"
            "• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)\n"
            "• [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)"
        )

    # 8. Periferiya va aksessuarlar
    elif any(word in text_lower for word in ["mishka", "mishqa", "klaviatura", "klavyatura", "kovrik", "sumka", "adapter", "zaryadnik", "monitor"]):
        reply_text = (
            "Ha, do'konimizda monitorlar, mishka, klaviatura, kovriklar, noutbuk sumkalari va adapterlar kabi barcha turdagi aksessuarlar bor!\n\n"
            "Tanlash va narxlarni bilish uchun menejerlarimiz bilan bog'lanishingiz mumkin:\n"
            "• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)\n"
            "• [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)"
        )

    # 9. Boshqa barcha holatlar uchun
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

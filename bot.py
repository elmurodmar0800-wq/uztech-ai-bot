import os
import re
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

BOT_TOKEN = os.environ.get("BOT_TOKEN")

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

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
    if os.path.exists("products.txt"):
        with open("products.txt", "r", encoding="utf-8") as f:
            return f.read()
    return ""

def clean_word(word):
    """O'zbek tilidagi ko'plik va kelishik qo'shimchalarini tozalash"""
    w = word.lower()
    suffixes = ["larimizni", "larimizga", "larimiz", "laridan", "lariga", "lardan", "larda", "larini", "larim", "lari", "larga", "larni", "lar", "da", "ga", "ni", "si"]
    for sfx in suffixes:
        if w.endswith(sfx) and len(w) - len(sfx) >= 3:
            w = w[:-len(sfx)]
            break
    return w

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"Assalomu alaykum, {user_first_name} aka!\n\n"
        f"Men **Uz Tech** do'konining yordamchisi — **Saidazimxon**man. 🤖💻\n\n"
        f"Sizga do'konimizdagi qaysi mahsulot yoki model haqida ma'lumot berishim kerak?"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    text_lower = user_text.lower()
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # 1. Kimligini so'raganda
    if any(word in text_lower for word in ["kimsiz", "sen kimsiz", "isming", "oting"]):
        reply_text = "Men — 'Uz Tech' do'konining sun'iy intellekt yordamchisi Saidazimxonman! 🤖💻 Do'konimizdagi barcha mahsulotlar va texnikalar bo'yicha ma'lumot berishga tayyorman."
        await update.message.reply_text(reply_text, parse_mode="Markdown", disable_web_page_preview=True)
        return

    # 2. Salomlashish
    if any(word in text_lower for word in ["salom", "assalom", "qalaysiz", "yaxshimisiz"]):
        reply_text = "Va alaykum assalom! Uz Tech do'koniga xush kelibsiz. Ishlarimiz yaxshi, o'zingiz tuzumisiz? Qanday texnika yoki model qidirayotgan edingiz?"
        await update.message.reply_text(reply_text, parse_mode="Markdown", disable_web_page_preview=True)
        return

    # 3. Manzil, ish vaqti yoki kontaktlar
    if any(word in text_lower for word in ["manzil", "adres", "lokatsiya", "qayerda", "kontakt", "telefon", "ish vaqti", "nechigacha", "vaqt", "ishlaysiz", "shanba", "yakshanba", "kun", "ishda"]):
        await update.message.reply_text(CONTACT_INFO, parse_mode="Markdown", disable_web_page_preview=True)
        return

    # Qidiruvda e'tiborsiz qoldiriladigan so'zlar
    stop_words = {
        "bormi", "kerak", "bor", "edi", "haqida", "manga", "menga", "sizlarda", "aka", "do'stim", "qanaqalari", "qanaqa", "qaysi",
        "fhd", "ips", "100hz", "144hz", "165hz", "180hz", "240hz", "hdmi", "vga", "usb", "ram", "ssd", "hdr", "1mc", "5mc"
    }
    
    raw_words = re.findall(r'\w+', text_lower)
    cleaned_words = [clean_word(w) for w in raw_words if w not in stop_words and len(w) > 1]
    
    # Asosiy tovar kategoriyalari
    categories_map = {
        "noutbuk": "NOUTBUK", "laptop": "NOUTBUK", "notebook": "NOUTBUK",
        "printer": "PRINTER", "kserokopiya": "PRINTER",
        "monitor": "MONITOR", "ekran": "MONITOR",
        "videokarta": "VIDEOKARTA", "vga": "VIDEOKARTA",
        "router": "WI-FI ROUTER", "wifi": "WI-FI ROUTER", "roter": "WI-FI ROUTER",
        "mishka": "MISHKA", "klaviatura": "KLAVIATURA", "naushnik": "NAUSHNIK",
        "keys": "KORPUS (KEYS)", "kompyuter": "KOMPYUTER", "telefon": "TELEFON"
    }

    # Tekshiruv: foydalanuvchi faqat umumiy kategoriya so'raganmi?
    found_categories = [categories_map[w] for w in cleaned_words if w in categories_map]
    
    # Agar foydalanuvchi biror aniq model (masalan: C50, L3350, 27PRM100, RTX, i5) yoza olmagan bo'lsa va faqat umumiy so'z bo'lsa:
    has_specific_model = any(len(w) >= 3 and w not in categories_map for w in cleaned_words)
    
    if found_categories and not has_specific_model:
        cat_name = found_categories[0]
        reply_text = (
            f"Do'konimizda turli xil **{cat_name}** modellari yetarlicha bor! 💻✨\n\n"
            f"Sizga do'konimizda bor-yo'qligini aniq tekshirib berishim uchun **aynan qaysi brend yoki model** (masalan: i5, RTX 3050, L3350 va h.k.) kerakligini yozib bera olasizmi?"
        )
        await update.message.reply_text(reply_text, parse_mode="Markdown", disable_web_page_preview=True)
        return

    # Bazadan qidirish
    db_content = load_products_db()
    
    if db_content and cleaned_words:
        scored_matches = []
        
        for line in db_content.split("\n"):
            line_str = line.strip()
            if not line_str or line_str.startswith("==="):
                continue
            
            line_lower = line_str.lower()
            
            match_score = 0
            for kw in cleaned_words:
                if kw in line_lower:
                    match_score += 3 if len(kw) >= 3 else 1
            
            if match_score > 0:
                scored_matches.append((match_score, line_str))
        
        scored_matches.sort(key=lambda x: x[0], reverse=True)
        
        if scored_matches:
            matched_lines = [item[1] for item in scored_matches if item[0] >= 3] if any(item[0] >= 3 for item in scored_matches) else [item[1] for item in scored_matches]
            found_text = "\n".join(matched_lines[:8])
            reply_text = (
                f"Ha, do'konimizda quyidagi mos modellar bor:\n\n{found_text}\n\n"
                f"💳 **Narxlar va buyurtma berish uchun menejerlarimizga murojaat qiling:**\n"
                f"• [Elmurod](https://t.me/wero_7708): [+998 93 641 0800](tel:+998936410800)\n"
                f"• [Axrorbek](https://t.me/A9769): [+998 93 976 9769](tel:+998939769769)"
            )
            await update.message.reply_text(reply_text, parse_mode="Markdown", disable_web_page_preview=True)
            return

    # Aks holda umumiy javob
    reply_text = (
        f"Tushundim! Bu model bo'yicha do'konimizdagi mavjudlik va narxlarni quyidagi menejerlarimizdan aniqlashtirishingiz mumkin:\n\n"
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

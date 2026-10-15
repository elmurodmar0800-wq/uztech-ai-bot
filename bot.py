import os
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# Настройки логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Переменные окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Инициализация клиента Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# Фиктивный веб-сервер для проходимости проверок Render (Free Web Service)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Системная инструкция для Саидазимхона
SYSTEM_INSTRUCTION = """
Вы — вежливый, умный и опытный онлайн-консультант компьютерного магазина "Uz Tech" в Фергане. Ваше имя — Саидазимхон.

Правила работы:
1. Общайтесь с клиентами строго на узбекском языке, вежливо и профессионально.
2. Сообщайте, что в магазине есть компьютеры, ноутбуки, моноблоки, принтеры, комплектующие (видеокарты, ОЗУ, SSD и т.д.), периферия, а также услуги по ремонту и сервису.
3. Магазин находится в городе Фергана (Farg'ona shahrida).
4. По поводу точных цен, оформления заказа и глубоких технических вопросов рекомендуйте обращаться к менеджерам: @wero_7708 или @A9769.
5. Отвечайте кратко, понятливо и дружелюбно.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"Assalomu alaykum, {user_first_name}!\n\n"
        f"Men **Uz Tech** do'konining AI yordamchisi — **Saidazimxon**man. 🤖💻\n\n"
        f"Sizga noutbuklar, kompyuterlar, printerlar yoki ta'mirlash xizmatlari bo'yicha qanday yordam bera olaman?"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений пользователя через Gemini AI"""
    user_text = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Корректный запрос к Gemini API
        prompt = f"{SYSTEM_INSTRUCTION}\n\nMijoz savoli: {user_text}\nSaidazimxon javobi:"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        reply_text = response.text
    except Exception as e:
        logging.error(f"Gemini API xatosi: {e}")
        # Интеллектуальный фолбэк на случай временного сбоя API
        text_lower = user_text.lower()
        if "adres" in text_lower or "qayer" in text_lower or "manzil" in text_lower:
            reply_text = "Do'konimiz Farg'ona shahrida joylashgan. Aniq mo'ljal va lokatsiya uchun menejerlarimiz @wero_7708 yoki @A9769 bilan bog'lanishingiz mumkin."
        elif "salom" in text_lower or "assalom" in text_lower:
            reply_text = "Assalomu alaykum! Uz Tech do'koniga xush kelibsiz. Sizga qanday kompyuter yoki texnika bo'yicha yordam kerak?"
        else:
            reply_text = "Ha, albatta! Barcha turdagi noutbuklar, kompyuterlar va ehtiyot qismlar do'konimizda mavjud. Aniq narxlar va buyurtma uchun menejerlarimiz @wero_7708 yoki @A9769 bilan bog'lanishingiz mumkin."

    await update.message.reply_text(reply_text)

def main():
    """Запуск бота"""
    if not BOT_TOKEN or not GEMINI_API_KEY:
        print("XATO: BOT_TOKEN yoki GEMINI_API_KEY topilmadi!")
        return

    # Запуск фонового HTTP-сервера для Render
    Thread(target=run_dummy_server, daemon=True).start()

    # Обход ошибки asyncio event loop на новых версиях Python
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

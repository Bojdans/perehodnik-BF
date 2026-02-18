import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TG_TOKEN")
TARGET_URL = os.getenv("TARGET_URL")

TEXT = (
    "Привет! Быстрый интернет без ограничений ⚡ всего в одном шаге от тебя!!\n"
    "🎁 3 дня бесплатно! Подключайтесь за минуту и забудьте об ограничениях!! \n"
    "✅ Современные методы — максимум защиты и анонимности 🗝\n"
    "✅ Много локаций 🌍"
)

BUTTON_TEXT = "🚀 Запустить бота"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=BUTTON_TEXT, url=TARGET_URL)]]
    )
    await update.message.reply_text(
        text=TEXT,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )


def main() -> None:
    if not TOKEN:
        raise RuntimeError("ENV TG_TOKEN is required")
    if not TARGET_URL:
        raise RuntimeError("ENV TARGET_URL is required")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()

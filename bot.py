import os
from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TG_TOKEN")
TARGET_URL = os.getenv("TARGET_URL")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # куда слать логи (группа/канал/личка)

TEXT = (
    "Высокоскоростное подключение к любым сайтам и бесперебойная работа интернета в одном шаге от тебя!!\n\n"
    "Запускай бота ниже и пользуйся сервисом 3 ДНЯ БЕСПЛАТНО🎁 без ограничений в скорости и качестве! \n\n"
    "P.S: Высокоскоростной и стабильный интернет даже на LTE!!!"
)

BUTTON_TEXT = "🚀 Запустить бота"

BASE_DIR = Path(__file__).resolve().parent
COUNT_FILE = BASE_DIR / "users_count.txt"
IDS_FILE = BASE_DIR / "users_ids.txt"


def _load_ids() -> set[int]:
    if not IDS_FILE.exists():
        return set()
    ids: set[int] = set()
    for line in IDS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.isdigit():
            ids.add(int(line))
    return ids


def _save_new_id(user_id: int) -> bool:
    """
    Возвращает True, если это новый пользователь (ID был добавлен).
    Подсчёт пользователей — уникальный.
    """
    ids = _load_ids()
    if user_id in ids:
        return False

    IDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with IDS_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{user_id}\n")

    COUNT_FILE.write_text(str(len(ids) + 1), encoding="utf-8")
    return True


def _get_count() -> int:
    if not COUNT_FILE.exists():
        return 0
    content = COUNT_FILE.read_text(encoding="utf-8").strip()
    return int(content) if content.isdigit() else 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message = update.effective_message
    if user is None or message is None:
        return

    # 1) Уникальный подсчёт пользователей
    _save_new_id(user.id)
    total = _get_count()

    # 2) Лог в группу: имя + username + общий уникальный счётчик
    full_name = " ".join(x for x in [user.first_name, user.last_name] if x).strip()
    username = f"@{user.username}" if user.username else "нет username"

    log_text = (
        "👤 Новый переход через /start\n"
        f"📛 Имя: {full_name or 'без имени'}\n"
        f"🔗 Username: {username}\n"
        f"📊 Всего уникальных пользователей: {total}"
    )

    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            chat_id=int(ADMIN_CHAT_ID),
            text=log_text
        )

    # 3) Ответ пользователю отправляется всегда, даже при повторном /start
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=BUTTON_TEXT, url=TARGET_URL)]]
    )

    await message.reply_text(
        text=TEXT,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )


def main() -> None:
    if not TOKEN:
        raise RuntimeError("ENV TG_TOKEN is required")
    if not TARGET_URL:
        raise RuntimeError("ENV TARGET_URL is required")
    if not ADMIN_CHAT_ID:
        raise RuntimeError("ENV ADMIN_CHAT_ID is required")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()

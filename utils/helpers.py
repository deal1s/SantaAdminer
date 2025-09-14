from datetime import timedelta
import re

# ----------------------
# Форматування користувачів
# ----------------------
def format_user(user):
    """
    user – словник з полями: telegram_id, name, username
    Повертає рядок: "Ім'я (@username) [ID]"
    """
    return f"{user.get('name','?')} (@{user.get('username','?')}) [{user.get('telegram_id','?')}]"

# ----------------------
# Парсинг часу для нагадувань
# ----------------------
def parse_time(time_str):
    """
    time_str – рядок формату: 1d, 3h, 5m
    Повертає timedelta
    """
    pattern = r"(\d+)([dhm])"
    match = re.match(pattern, time_str)
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    if unit == "d":
        return timedelta(days=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "m":
        return timedelta(minutes=value)
    return None

# ----------------------
# Додаткові хелпери
# ----------------------
def extract_id_or_username(text):
    """
    Парсить ID або @username з тексту команди
    Повертає рядок
    """
    args = text.split()
    if len(args) < 2:
        return None
    return args[1].strip()

def clean_text(text):
    """
    Очищує текст команди від /command
    """
    return " ".join(text.split()[1:]).strip()

from datetime import datetime

def log_action(bot, log_channel_id, action_text):
    """
    Логування дій адміністрації.
    bot – об'єкт TeleBot
    log_channel_id – ID каналу для логів
    action_text – текст дії
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"📝 [{timestamp}] {action_text}"
    try:
        bot.send_message(log_channel_id, log_message)
    except Exception as e:
        print(f"Помилка логування: {e}")

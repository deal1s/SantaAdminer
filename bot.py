import telebot
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import db, logger, helpers
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

# Завантаження конфігурації
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
ADMIN_CHAT_ID = config["ADMIN_CHAT_ID"]
USER_CHAT_ID = config["USER_CHAT_ID"]
LOG_CHANNEL_ID = config["LOG_CHANNEL_ID"]
OWNER_IDS = config["OWNER_IDS"]

bot = telebot.TeleBot(TOKEN)
scheduler = BackgroundScheduler()
scheduler.start()

# Ініціалізація бази даних
db.init_db()

# ----------------------
# Допоміжні функції
# ----------------------
def is_owner(user_id):
    return user_id in OWNER_IDS

def is_head_admin(user_id):
    role = db.get_role(user_id)
    return role == "Head Admin"

def is_gnome(user_id):
    role = db.get_role(user_id)
    return role == "Gnome"

def format_user(user):
    return f"{user.get('name','?')} (@{user.get('username','?')}) [{user.get('telegram_id','?')}]"

# ----------------------
# /start та /help
# ----------------------
@bot.message_handler(commands=["start", "help"])
def start_help(message):
    text = f"""
Привіт! Це бот SANTA ADMINer
Власник бота: Santa

Команди:

/hto (Owner, Head Admin)
/say (Gnome, Head Admin, Owner)
/says
/sayon / sayson
/online_list
/sayb [ID] / sayu [ID]
/add_gnome / remove_gnome
/add_main_admin / remove_main_admin
/ban_s / ban_t / unban_s / unban_t
/mute_s / mute_t / unmute_s / unmute_t
/nah
/alarm
/save_s
/broadcast
/saypin
/note / notes
/reminder / reminde
/adminchat [ID] / userchat [ID] / logchannel [ID]
"""
    bot.reply_to(message, text)

# ----------------------
# /hto – інформація про користувача
# ----------------------
@bot.message_handler(commands=["hto"])
def hto(message):
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.text.split()) > 1:
        try:
            user_id = int(message.text.split()[1])
        except:
            bot.reply_to(message, "Невірний ID")
            return
    else:
        bot.reply_to(message, "Вкажіть ID або reply на повідомлення")
        return

    user = db.get_user_info(user_id)
    if not user:
        bot.reply_to(message, "Користувач не знайдений")
        return
    info = f"""
Ім'я: {user.get('name')}
Username: @{user.get('username')}
ID: {user.get('telegram_id')}
Група: {user.get('group_name','?')} [{user.get('group_id','?')}]
Додано: {user.get('added_by','?')}
"""
    bot.reply_to(message, info)

# ----------------------
# /say – надіслати повідомлення в основний чат
# ----------------------
@bot.message_handler(commands=["say"])
def say(message):
    user_id = message.from_user.id
    if not (is_owner(user_id) or is_head_admin(user_id) or is_gnome(user_id)):
        bot.reply_to(message, "Немає доступу")
        return
    text = message.text.replace("/say","",1).strip()
    if not text:
        bot.reply_to(message,"Введіть текст для відправки")
        return
    msg = bot.send_message(USER_CHAT_ID, text)
    db.save_forward_mapping(msg.message_id, msg.message_id)
    logger.log_action(bot, LOG_CHANNEL_ID, f"{format_user({'telegram_id':user_id,'name':message.from_user.first_name,'username':message.from_user.username})} надіслав /say: {text}")
    bot.reply_to(message,"Повідомлення надіслано")

# ----------------------
# /says – відповідь на повідомлення користувача через адмін-чат
# ----------------------
@bot.message_handler(commands=["says"])
def says(message):
    user_id = message.from_user.id
    if not (is_owner(user_id) or is_head_admin(user_id) or is_gnome(user_id)):
        bot.reply_to(message,"Немає доступу")
        return
    if not message.reply_to_message:
        bot.reply_to(message,"Reply на повідомлення користувача обов'язковий")
        return
    text = message.text.replace("/says","",1).strip()
    if not text:
        bot.reply_to(message,"Введіть текст")
        return
    reply_to_id = message.reply_to_message.message_id
    user_msg_id = db.get_user_message_id(reply_to_id)
    if not user_msg_id:
        bot.reply_to(message,"Повідомлення не знайдено")
        return
    bot.send_message(USER_CHAT_ID, text, reply_to_message_id=user_msg_id)
    logger.log_action(bot, LOG_CHANNEL_ID, f"{format_user({'telegram_id':user_id,'name':message.from_user.first_name,'username':message.from_user.username})} відповів /says: {text}")

# ----------------------
# /sayon – увімкнути онлайн-режим
# ----------------------
@bot.message_handler(commands=["sayon"])
def sayon(message):
    user_id = message.from_user.id
    if not (is_owner(user_id) or is_head_admin(user_id) or is_gnome(user_id)):
        bot.reply_to(message,"Немає доступу")
        return
    db.set_online(user_id, "sayon")
    bot.reply_to(message,"Онлайн-режим увімкнено")
    logger.log_action(bot, LOG_CHANNEL_ID, f"{format_user({'telegram_id':user_id,'name':message.from_user.first_name,'username':message.from_user.username})} увімкнув sayon")

# ----------------------
# /sayson – вимкнути онлайн-режим
# ----------------------
@bot.message_handler(commands=["sayson"])
def sayson(message):
    user_id = message.from_user.id
    db.remove_online(user_id)
    bot.reply_to(message,"Онлайн-режим вимкнено")
    logger.log_action(bot, LOG_CHANNEL_ID, f"{format_user({'telegram_id':user_id,'name':message.from_user.first_name,'username':message.from_user.username})} вимкнув sayson")

# ----------------------
# /online_list – список адмінів онлайн
# ----------------------
@bot.message_handler(commands=["online_list"])
def online_list(message):
    online = db.get_online()
    if not online:
        bot.reply_to(message,"Ніхто не онлайн")
        return
    text = "Адміни онлайн:\n"
    for o in online:
        text += f"• {format_user(o)} – {o['mode']}\n"
    bot.reply_to(message, text)

# ----------------------
# /adminchat, /userchat, /logchannel – змінити чати
# ----------------------
@bot.message_handler(commands=["adminchat","userchat","logchannel"])
def change_chats(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message,"Немає доступу")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message,"Вкажіть ID")
        return
    chat_id = int(args[1])
    if message.text.startswith("/adminchat"):
        global ADMIN_CHAT_ID
        ADMIN_CHAT_ID = chat_id
        bot.reply_to(message,f"ADMIN_CHAT_ID змінено на {chat_id}")
    elif message.text.startswith("/userchat"):
        global USER_CHAT_ID
        USER_CHAT_ID = chat_id
        bot.reply_to(message,f"USER_CHAT_ID змінено на {chat_id}")
    elif message.text.startswith("/logchannel"):
        global LOG_CHANNEL_ID
        LOG_CHANNEL_ID = chat_id
        bot.reply_to(message,f"LOG_CHANNEL_ID змінено на {chat_id}")
    logger.log_action(bot, LOG_CHANNEL_ID, f"{format_user({'telegram_id':message.from_user.id,'name':message.from_user.first_name,'username':message.from_user.username})} змінив чат {chat_id}")

# ----------------------
# Запуск бота
# ----------------------
if __name__ == "__main__":
    print("SANTA ADMINer запущено...")
    bot.infinity_polling()

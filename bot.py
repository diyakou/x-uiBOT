import telebot
import requests
import uuid
import qrcode
from io import BytesIO
from telebot import types
from database import save_user_data, load_user_data, init_db
from variables import chat_id
from xui import get_connection_link , remove_user , list_users
admin_ids = [chat_id]


admin_id = int(admin_ids[0])
print(admin_id)
BOT_token = '7195988118:AAHvTjVl1aWbUKmgNhoJKnD6sYe9pG8MhYU'
bot = telebot.TeleBot(BOT_token)


def authenticate(XUI_URL, XUI_USERNAME, XUI_PASSWORD):
    url = f'{XUI_URL}/login'
    data = {
        'username': XUI_USERNAME,
        'password': XUI_PASSWORD
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        header = response.headers
        SESSION = header['Set-Cookie'].split(';')[0]
        return SESSION
    else:
        raise Exception('Failed to authenticate with X-UI')

def header(sessions):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': sessions
    }
    return headers

def main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton('New Config'),
        types.KeyboardButton('My Config'),
        types.KeyboardButton('Mangements')
    )
    return keyboard

def admin_menu():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton('Users'),
        types.KeyboardButton("remove User"),
        types.KeyboardButton("ban User"),
        types.KeyboardButton("Add Server")
    )
    return keyboard

def admin_only(func):
    def wrapper(message):
        if message.from_user.id == admin_id:
            return func(message)
        else:
            bot.send_message(message.chat.id, "Access denied: Admins only.")
    return wrapper

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Welcome to the X-UI Management Bot! Use the menu below to navigate.",
        reply_markup=main_menu_keyboard()
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    Available Commands:
    /start - Start the bot
    /help - Show this help message
    /status - Check server status
    /list - List all users
    /buy_config - Buy a new config
    /my_configs - View your configs
    /robot_management - Manage servers and users
    """
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['status'])
def check_status(message):
    chat_id = message.chat.id
    user_data = load_user_data(chat_id)
    if not user_data:
        bot.send_message(message.chat.id, "Server data not found. Please add server first.")
        return
    
    try:
        session = authenticate(user_data['server_url'], user_data['username'], user_data['password'])
        headers = header(sessions=session)
        response = requests.get(f"{user_data['server_url']}/panel/api/inbounds/list", headers=headers)
        if response.status_code == 200:
            status_info = response.json()
            bot.send_message(message.chat.id, f"Server Status:\n{status_info}")
        else:
            bot.send_message(message.chat.id, "Failed to retrieve server status.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(func=lambda message: message.text == "New Config")
def buy_config(message):
    bot.send_message(message.chat.id, "Enter Vol")
    bot.register_next_step_handler(message, get_vol)

def get_vol(message):
    vol = message.text
    bot.send_message(message.chat.id, "Enter date")
    bot.register_next_step_handler(message, get_date, vol)

def get_date(message, vol):
    date = message.text
    admin_id = admin_ids[0]  # Assuming single admin for simplicity
    confirmation_text = f"User {message.chat.id} requested a new config:\nVolume: {vol}\nDate: {date}\n\nAccept or reject?"
    bot.send_message(admin_id, confirmation_text)
    bot.register_next_step_handler_by_chat_id(admin_id, handle_admin_response, message.chat.id, vol, date)

def generate_uuid():
    return str(uuid.uuid4())

def generate_inbound_id():
    global current_inbound_id
    current_inbound_id += 1
    return current_inbound_id

current_inbound_id = 10017

def generate_port():
    global current_port
    current_port += 1
    return current_port

current_port = 10000

def handle_admin_response(admin_message, user_chat_id, vol, date):
    global current_inbound_id
    global current_port
    uniqid = generate_uuid()
    port = generate_port()
    inbound_id = generate_inbound_id()
    if admin_message.text.lower() == "accept":
        conf = get_connection_link('146.190.204.201', uniqid, 'vless', "New_Conf_bots", port, 'ws', inbound_id, int(vol), int(date))
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4,)
        qr.add_data(conf[0])
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        bio = BytesIO()
        img.save(bio, format='PNG')
        bio.seek(0)

        bot.send_photo(user_chat_id, photo=bio, caption=conf)

        perform_desired_function(vol, date)
    elif admin_message.text.lower() == "reject":
        bot.send_message(user_chat_id, "Your request has been rejected.")
    else:
        bot.send_message(admin_id, "Please respond with 'accept' or 'reject'.")
        bot.register_next_step_handler_by_chat_id(admin_id, handle_admin_response, user_chat_id, vol, date)

def perform_desired_function(vol, date):
    print(f"Performing function with Volume: {vol} and Date: {date}")

@bot.message_handler(commands=['my_configs'])
def my_configs(message):
    chat_id = message.chat.id
    user_data = load_user_data(chat_id)
    if not user_data:
        bot.send_message(message.chat.id, "Server data not found. Please add server first.")
        return
    
    try:
        session = authenticate(user_data['server_url'], user_data['username'], user_data['password'])
        headers = header(sessions=session)
        response = requests.get(f'{user_data['server_url']}/api/user/configs', headers=headers)
        if response.status_code == 200:
            configs = response.json()
            configs_list = "\n".join([f"ID: {config['id']}, Name: {config['name']}" for config in configs])
            bot.send_message(message.chat.id, f"Your Configs:\n{configs_list}")
        else:
            bot.send_message(message.chat.id, "Failed to retrieve configs.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(func=lambda message: message.text == "Mangements")
@admin_only
def admin_men(message):
    bot.send_message(message.chat.id, "admin panel", reply_markup=admin_menu())

@bot.message_handler(func=lambda message: message.text == "remove User")
@admin_only
def request_uuid(message):
    bot.send_message(message.chat.id, "Enter UUID of user:")
    bot.register_next_step_handler(message, process_uuid)

def process_uuid(message):
    user_uuid = message.text
    result = remove_user(user_uuid)
    print(result)
    bot.send_message(message.chat.id, result)

@bot.message_handler(func=lambda message: message.text == "Users")
@admin_only
def User_list(message):
    list_us = list_users()
    print(list_us)
    bot.send_message(message.chat.id, f"{list_us}")

@bot.message_handler(func=lambda message: message.text == "Add Server")
@admin_only
def Add_server(message):
    bot.send_message(message.chat.id, "Enter Server URL :")
    bot.register_next_step_handler(message, get_server_url)

def get_server_url(message):
    chat_id = message.chat.id
    server_url = message.text
    bot.reply_to(message, "Great! Now, please enter your username:")
    bot.register_next_step_handler(message, get_username, server_url)

def get_username(message, server_url):
    chat_id = message.chat.id
    username = message.text
    bot.reply_to(message, "Thank you! Finally, please enter your password:")
    bot.register_next_step_handler(message, get_password, server_url, username)

def get_password(message, server_url, username):
    chat_id = message.chat.id
    password = message.text
    save_user_data(chat_id, server_url, username, password)
    bot.reply_to(message, "Your information has been saved successfully!")

bot.polling()

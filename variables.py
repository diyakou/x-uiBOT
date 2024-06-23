import json
from database import load_user_data

chat_id = '#'  
user_data = load_user_data(chat_id)
XUI_URL = user_data.get('server_url')
XUI_USERNAME = user_data.get('username')
XUI_PASSWORD = user_data.get('password')

payload = {}

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

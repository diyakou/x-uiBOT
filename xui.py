import requests
from variables import XUI_PASSWORD, XUI_URL, XUI_USERNAME, payload
import json
import uuid
import string
import time

def authenticate():
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

sessions = authenticate()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': sessions
}

def remove_user(user_id):
    url = f'{XUI_URL}/panel/api/inbounds/del/{user_id}'
    req = requests.post(url, headers=headers)
    if req.status_code == 200:
        return "User deleted successfully"
    else:
        return "Error in deleting", req.text

def list_users():
    try:
        response = requests.get(f'{XUI_URL}/panel/api/inbounds/list', headers=headers)
        if response.status_code == 200:
            users = response.json()
            if users.get('success'):
                user_list = users.get('obj', [])
                user_info = ""
                for user in user_list:
                    user_info += f"ID: {user['id']}\n"
                    user_info += f"Remark: {user['remark']}\n"
                    user_info += f"Up: {user['up']}\n"
                    user_info += f"Down: {user['down']}\n"
                    user_info += f"Port: {user['port']}\n"
                    user_info += f"Protocol: {user['protocol']}\n"
                    user_info += f"Enable: {user['enable']}\n\n"
                return f"Users List:\n{user_info}"
        else:
            return "Failed to retrieve users list."
    except Exception as e:
        return str(e)

def random_name1():
    return ''.join(string.ascii_letters + string.ascii_lowercase for _ in range(5))

def get_connection_link(server_id, uniqid, protocol, remark, port, net_type, inbound_id, vol, date, rahgozar=False, custom_path=False, custom_port=0, custom_sni=None):
    base_url = f"{XUI_URL}/panel/api/inbounds/add"
    client_url = f"{XUI_URL}/panel/api/inbounds/addClient"
    volume_gb = vol
    volume_bytes = volume_gb * 1073741824
    random_name = random_name1()
    print(random_name)
    days_until_expiry = date
    current_time_in_ms = int(round(time.time() * 1000))
    expiry_time_ms = current_time_in_ms + days_until_expiry * 24 * 60 * 60 * 1000
    payload_client = {
        "id": inbound_id,
        "settings": f'{{"clients":[{{"id":"{uniqid}","alterId":0,"email":"{random_name}","limitIp":2,"totalGB":{volume_bytes},"expiryTime":{expiry_time_ms},"enable":true,"tgId":"","subId":""}}]}}'
    }
    print(inbound_id)
    payload = {
        "enable": True,
        "remark": remark,
        "listen": "",
        "port": port,
        "protocol": protocol,
        "expiryTime": 0,
        "settings": "{\"clients\":[],\"decryption\":\"none\",\"fallbacks\":[]}",
        "streamSettings": "{\"network\":\"ws\",\"security\":\"none\",\"wsSettings\":{\"acceptProxyProtocol\":false,\"path\":\"/\",\"headers\":{}}}",
        "sniffing": "{\"enabled\":true,\"destOverride\":[\"http\",\"tls\"]}"
    }

    try:
        response = requests.post(base_url, headers=headers, data=payload)
        response.raise_for_status()
        result = response.json()

        success = result.get('success', False)
        message = result.get('msg', '')
        obj = result.get('obj', {})
        if success:
            time.sleep(5)
            create_client = requests.post(client_url, headers=headers, data=payload_client)
            create_client.raise_for_status()
            result2 = create_client.json()
            port_number = obj.get('port', '')
            print(result2)
            connection_link = f"{protocol}://{uniqid}@{server_id}:{port_number}?type=ws&path=%2F&host=&security=none#{remark}"
            return connection_link, message
        else:
            return None, message
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None, str(e)

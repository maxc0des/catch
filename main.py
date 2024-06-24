import requests
import time
from tokens import telegram
from tokens import mqqt_adress
from devices import deviceIds
from devices import devices

setup = []
game_setup = []
request = []
setup_devices = []

t = 0
do_request = False

bot_token = telegram['bot_token']
username = mqqt_adress['username']
io_key = mqqt_adress['io_key']
bot_api = f'https://api.telegram.org/bot{bot_token}/'

def add_user(user_id, device_id):
    devices[user_id] = device_id
    print(devices)

def get_device_id(user_id):
    return devices.get(user_id)

def get_updates(offset=None):
    url = bot_api + 'getUpdates'
    params = {'timeout': 100, 'offset': offset}
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    """Sendet eine Nachricht an einen bestimmten Chat."""
    url = bot_api + 'sendMessage'
    params = {'chat_id': chat_id, 'text': text}
    requests.get(url, params=params)

def send_mqqt(device_adress, action):
    #feed_key = mqqt_adress[device_adress]
    feed_key = device_adress
    data = {'value': action}
    print(bot_token, username, io_key, feed_key, data)
    mqqt_api = f'https://io.adafruit.com/api/v2/{username}/feeds/{feed_key}/data'
    headers = {
        'X-AIO-Key': io_key,
        'Content-Type': 'application/json'
    }
    response = requests.post(mqqt_api, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print('Daten erfolgreich hinzugefügt')
    else:
        print(f'Fehler bei der Anfrage: Status {response.status_code}, Antwort: {response.text}')
    return response

def request_mqqt(device_id):
    feed_key = device_id
    url = f'https://io.adafruit.com/api/v2/{username}/feeds/{feed_key}/data'
    print(url)
    headers = {'X-AIO-Key': io_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            print('Empfangene Daten:', data)
            process_mqqt(data, device_id)
        else:
            print('Keine Daten im Feed vorhanden')
    else:
        print(f'Fehler bei der Anfrage: Status {response.status_code}')

def process_mqqt(data, device_id):
    if device_id in setup_devices:
        if isinstance(data, dict):
            value = data.get('value')  # Using .get() to safely get 'value' from data
            if value == 'ok':
                print('Value is ok')
            else:
                print('Value is not ok')
        else:
            print('Data is not a dictionary:', data)


def process_messages(text, chat_id):
    print("new message: ", text)
    answer = 'something went wrong'  # Ensure 'answer' is always initialized
    if chat_id in setup:
        if text in deviceIds:
            send_mqqt(text, 'connection requested')
            request.append(text)
            setup_devices.append(text)
            answer = "Thank you! Now press the button on your device so we can finish the setup"
            add_user(chat_id, text)
            setup.remove(chat_id)
        else:
            answer = "There is no device with this id"
    if chat_id in game_setup:
        try:
            interval = int(text)
            action = f'intervall={interval}'
            print(action)
            device_address = get_device_id(chat_id)
            print(device_address)
            send_mqqt(device_address, action)
            game_setup.remove(chat_id)
            answer = "Your game is now set up. Send any /startGame to start."
        except ValueError:
            answer = "Please enter a valid number"

    if '/start' in text:
        answer = "Welcome! Let's register your device. What is your device id?"
        setup.append(chat_id)
    elif 'ping' in text:
        answer = "pong"
    elif '/game' in text:
        answer = "Ok! Let's start a game. How often should the device send a photo. Enter the number of minutes"
        game_setup.append(chat_id)
    send_message(chat_id, answer)

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        print(offset)
        if 'result' in updates:
            for update in updates['result']:
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    text = update['message']['text']
                    process_messages(text, chat_id)
                    offset = update['update_id'] + 1
        print(request)
        for requests in request:
            request_mqqt(requests)
        time.sleep(1)

if __name__ == '__main__':
    print("programm gestartet")
    send_mqqt('admin', 'bot online')
    listeningforEvent = False
    main()
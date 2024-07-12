from Adafruit_IO import MQTTClient
import requests
import time
from tokens import telegram
from tokens import mqtt_adress
from devices import deviceIds
from devices import devices
from devices import users
from devices import activated_devices

setup = []
game_setup = []
request = []
setup_devices = []
feeds = ['device1', 'admin']
connection_requested = []
last_message = False


bot_token = telegram['bot_token']
username = mqtt_adress['username']
io_key = mqtt_adress['io_key']
bot_api = f'https://api.telegram.org/bot{bot_token}/'

def connect_mqtt():
    client = MQTTClient(username, io_key)

    client.on_connect = connected
    client.on_disconnect = disconnected
    client.on_message = message
    client.connect()
    client.loop_background()

def connected(client):
    print('Connected to Adafruit IO!')
    
    for feed in feeds:
        print(f'Subscribing to {feed}')
        client.subscribe(feed)

    for devices in deviceIds:
        print(f'Subscribing to {devices}')
        client.subscribe(devices)

def disconnected(client):
    print('Disconnected from Adafruit IO!')

def message(client, feed_id, payload):
    global last_message
    print(f'Feed {feed_id} received new value: {payload}')
    last_message = (feed_id, payload)
    process_mqtt(feed_id, payload)

def get_device(user_id):
    return users.get(user_id, "Device not found")

def get_user(device_id):
    return devices.get(device_id, "User not found")

def add_user(user_id, device_id):
    if user_id in users or device_id in devices:
        return "User ID or Device ID already exists."
    users[user_id] = device_id
    devices[device_id] = user_id
    return "Data pair added successfully."

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

def send_mqtt(device_adress, action):
    feed_key = device_adress
    data = {'value': action}
    print(bot_token, username, io_key, feed_key, data)
    mqtt_api = f'https://io.adafruit.com/api/v2/{username}/feeds/{feed_key}/data'
    headers = {
        'X-AIO-Key': io_key,
        'Content-Type': 'application/json'
    }
    response = requests.post(mqtt_api, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print('Daten erfolgreich hinzugefügt')
    else:
        print(f'Fehler bei der Anfrage: Status {response.status_code}, Antwort: {response.text}')
    return response

def process_mqtt(feed, message): #feed = device id
    print('processing')
    if feed in connection_requested:
        print(message)
        print(type(message))
        chat_id = get_user(feed)
        print(feed)
        if message == '200':
            print('should work')
            activated_devices.append(feed)
            answer = 'Your device was registered and connected to your account succesfully'
            connection_requested.remove(feed)
            activated_devices.append(get_user(feed))
        else:
            answer = 'wait, something went wrong :('
        print(chat_id, answer)
        send_message(chat_id, answer)

def process_messages(text, chat_id):
    message = text
    print("new message: ", message)
    answer = 'Wait, i dont know this command :('
    if chat_id in setup:
        if text in deviceIds:
            device_id = message
            send_mqtt(device_id, 'connection requested')
            setup_devices.append(device_id)
            answer = "Thank you! Now press the button on your device so we can finish the setup."
            add_user(chat_id, device_id)
            connection_requested.append(device_id)
            setup.remove(chat_id)
        else:
            answer = "There is no device with this id"
    if chat_id in game_setup:
        try:
            interval = int(message)
            action = f'intervall={interval}'
            print(action)
            device_address = get_device(chat_id)
            print(device_address)
            send_mqtt(device_address, action)
            game_setup.remove(chat_id)
            answer = "Perfect, now press the button on your device to start the game"
        except ValueError:
            answer = "Please enter a valid number"

    if '/start' in text:
        answer = "Welcome! Let's register your device. What is your device id?"
        setup.append(chat_id)
    elif 'ping' in text:
        answer = "pong"
        print(get_user('device1'))
    elif '/game' in text:
        if chat_id in activated_devices:
            answer = "Ok! Let's configure your game. How often should the device send a photo. Enter the number of minutes"
            game_setup.append(chat_id)
        else:
            answer = 'Your device is not registered yet. Run /start first'
    send_message(chat_id, answer)

def main():
    offset = None
    while True:
        try:
            global last_message
            if last_message:
                feed_id, payload = last_message
                print(f'Handling new message from {feed_id}: {payload}')
                last_message = None
            updates = get_updates(offset)
            print(offset)
            if 'result' in updates:
                for update in updates['result']:
                    if 'message' in update:
                        try:
                            chat_id = update['message']['chat']['id']
                            text = update['message']['text']
                            process_messages(text, chat_id)
                            offset = update['update_id'] + 1
                        except ValueError:
                            print('something went wrong')
            time.sleep(1)
        except KeyboardInterrupt:
            print("stopped the bot")
            break

if __name__ == '__main__':
    print("programm gestartet")
    send_mqtt('admin', 'bot online')
    connect_mqtt()
    listeningforEvent = False
    main()
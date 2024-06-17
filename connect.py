import network
import time
import machine

# Initialisiere die Pins
red = machine.Pin(15, machine.Pin.OUT)
green = machine.Pin(16, machine.Pin.OUT)
blue = machine.Pin(17, machine.Pin.OUT)
buzzer = machine.Pin(18, machine.Pin.OUT)

def indicate(mode):
    if mode == "working":
        blue.value(1)
        green.value(0)
        red.value(0)
        buzzer.value(0)
    elif mode == "error":
        blue.value(0)
        green.value(0)
        red.value(1)
        buzzer.value(1)
    elif mode == "perfect":
        blue.value(0)
        green.value(1)
        red.value(0)
        buzzer.value(0)
    elif mode == "off":
        blue.value(0)
        green.value(0)
        red.value(0)
        buzzer.value(0)
    else:
        print("received unknown mode")
        
def connectWifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    networks = wlan.scan()
    if not ssid in str(networks):
        ssid = input("wifi not found reenter ssid")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(ssid, password)
    print('Verbinden...')
    while not sta_if.isconnected():
        print(".")
        indicate("working")
        time.sleep(0.4)
        indicate("off")
    print('Verbindung hergestellt!')
    print('Netzwerk-Konfiguration:', sta_if.ifconfig())
    indicate("perfect")
connectWifi('ssid', 'password')
indicate("working")
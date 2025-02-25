import time
import urequests
import network
from machine import Pin, ADC
import dht

# --- Wi-Fi Configuration ---
WIFI_SSID = "Nini"
WIFI_PASSWORD = "tesarfamson"

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to network...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print("Network connected:", wlan.ifconfig())

# Connect to Wi-Fi before doing anything else
connect_wifi(WIFI_SSID, WIFI_PASSWORD)

# --- Ubidots Configuration ---
TOKEN = "BBUS-RchHnWwbIEed2SNpCUbwBmpZYJjwCC"  # Replace with your Ubidots TOKEN
DEVICE_LABEL = "Assignment_2"  # Your device label
VARIABLE_LABEL_1 = "temperature"  # Temperature variable label
VARIABLE_LABEL_2 = "humidity"     # Humidity variable label
VARIABLE_LABEL_3 = "LDR"          # LDR variable label

# --- Flask Server Configuration ---
FLASK_URL = "http://192.168.1.22:5000/send_data"

# --- Sensor Setup ---
# Setup ADC for the LDR on pin 34
ldr_adc = ADC(Pin(34))
ldr_adc.atten(ADC.ATTN_11DB)  # 11dB attenuation gives a range ~0-3.3V

# Setup DHT11 sensor on pin 33
dht_sensor = dht.DHT11(Pin(33))

# --- Functions to Build Payload and Send Data ---
def build_payload(temperature, humidity, ldr_value):
    """
    Constructs the JSON payload with sensor data.
    """
    payload = {
        VARIABLE_LABEL_1: temperature,
        VARIABLE_LABEL_2: humidity,
        VARIABLE_LABEL_3: ldr_value
    }
    return payload

def post_request_ubidots(payload):
    """
    Sends the payload to Ubidots. Retries up to 5 times if the status code is >= 400.
    """
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/{}".format(DEVICE_LABEL)
    headers = {
        "X-Auth-Token": TOKEN,
        "Content-Type": "application/json"
    }
    status = 400
    attempts = 0
    while status >= 400 and attempts < 5:
        try:
            response = urequests.post(url, json=payload, headers=headers, timeout=5)
            status = response.status_code
            print("Response Status:", status)
            print("Response Text:", response.text)
            response.close()
        except Exception as e:
            print("Error during POST request:", e)
            status = 500  # Use a default error code for consistency
        attempts += 1
        time.sleep(1)
        
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts. Please check your credentials and internet connection.")
        return False

    print("[INFO] Data sent successfully.")
    return True

def post_request_flask(payload):
    """
    Sends the payload to the Flask website. Retries up to 5 times if the status code is >= 400.
    """
    url = FLASK_URL
    headers = {
        "Content-Type": "application/json"
    }
    status = 400
    attempts = 0
    while status >= 400 and attempts < 5:
        try:
            response = urequests.post(url, json=payload, headers=headers, timeout=5)
            status = response.status_code
            print("Flask - Response Status:", status)
            print("Flask - Response Text:", response.text)
            response.close()
        except Exception as e:
            print("Flask - Error during POST request:", e)
            status = 500
        attempts += 1
        time.sleep(1)
        
    if status >= 400:
        print("[ERROR] Could not send data to Flask after 5 attempts.")
        return False

    print("[INFO] Data sent to Flask successfully.")
    return True

def main():

    # Read sensor values
    try:
        dht_sensor.measure()  # Trigger DHT11 measurement
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
    except Exception as e:
        print("DHT11 sensor error:", e)
        temperature = None
        humidity = None

    ldr_value = ldr_adc.read()  # Read LDR value (0 to 4095)

    # Build payload and send data to Ubidots
    payload = build_payload(temperature, humidity, ldr_value)
    print("Sending payload:", payload)
    post_request_ubidots(payload)
    post_request_flask(payload)
    print("[INFO] Cycle complete.\n")

# --- Main Loop ---
while True:
    main()
    time.sleep(2)  

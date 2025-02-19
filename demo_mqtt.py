import paho.mqtt.client as mqtt
import random
import requests
import time

def poll_connected_devices():
    try:
        response = requests.get("http://localhost:8080/mqtt/connected")
        devices = response.json()
        print("Connected devices:", devices)
    except Exception as e:
        print("Error polling connected devices:", e)

def publish_connection_status(client, status):
    if status:
        payload = f"cam1: 1"
    else:
        payload = "cam1: 0"
    client.publish("connected", payload)
    print(f"Published: {payload}")

def main():
    parser = argparse.ArgumentParser(description="Connect to MQTT")
    parser.add_argument("--remote", action="store_true", help="Use remote server")
    args = parser.parse_args()

    if args.remote:
        mqtt_broker = "mastermind-mqtt-146524160112.us-central1.run.app"
        print("Connecting to remote broker")
    else:
        mqtt_broker = "localhost"
        print("Connecting to local broker")
    
    client = mqtt.Client(client_id="cam1", callback_api_version=1)
    BROKER_PORT = 1883 

    client.connect(mqtt_broker, BROKER_PORT, 60)
    client.loop_start()
    
    while True:
        status = random.choice([True, False])

        # publish to mqtt

        print("Status: ", status)
        publish_connection_status(client, status)
        time.sleep(5)

        # poll status from api endpoint
        poll_connected_devices()

if __name__ == '__main__':
    main()

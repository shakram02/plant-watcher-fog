import json
import threading
import logging
import telepot
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from queue import Queue
from edge.status import EdgeUpdate, EdgeUpdateEncoder
from edge.server import EdgeServer

load_dotenv()
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
CHAT_ID = os.getenv("MY_CHAT_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


def connect_mqtt(client):
    """
    Connects the client to MQTT server
    if it's not already connected.
    """
    logging.info(f"Connecting to MQTT server ({MQTT_BROKER}:{MQTT_PORT})...")
    client.connect(MQTT_BROKER, port=MQTT_PORT)  # connect to MQTT broke
    logging.info("Connected...")


def mqtt_main(msq_queue: Queue):
    logging.info("Setting up MQTT client...")
    client = mqtt.Client()  # create new instance
    bot = telepot.Bot(TELEGRAM_TOKEN)
    connect_mqtt(client)

    while True:
        message: EdgeUpdate = msq_queue.get()

        if not client.is_connected():
            # connect to MQTT broker
            client.connect(MQTT_BROKER, port=MQTT_PORT)

        json_message = json.dumps(message,
                                  separators=(',', ':'),
                                  cls=EdgeUpdateEncoder)
        if not json_message:
            continue

        if message.temp > 23:
            logging.info(f"Alerting [Temp:{message.temp}]")
            temp_alert = f"The temperature is getting high: {message.temp}"
            bot.sendMessage(CHAT_ID, temp_alert)

        logging.info(f"Pushing data from [{message.uuid}]")
        client.publish(MQTT_TOPIC, json_message)


def main():
    format = "[%(asctime)s]: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    ip, port = "0.0.0.0", 8000
    msg_queue = Queue()
    server = EdgeServer(ip, port, msg_queue)
    th = threading.Thread(target=server.loop_forever, daemon=True)
    th.start()
    mqtt_main(msg_queue)
    th.join()


if __name__ == "__main__":
    main()

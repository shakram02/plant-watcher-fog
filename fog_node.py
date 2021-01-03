import json
import threading
import logging
import paho.mqtt.client as mqtt
from queue import Queue
from edge.status import EdgeUpdate, EdgeUpdateEncoder
from edge.server import EdgeServer

MQTT_BROKER = "174.138.103.162"
MQTT_TOPIC = "/hello_world"
MQTT_PORT = 3882


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

import threading
import logging
import paho.mqtt.client as mqtt
from edge.server import EdgeServer

MQTT_BROKER = "174.138.103.162"
MQTT_TOPIC = "/hello_world"
MQTT_PORT = 3881


def connect_mqtt(client):
    """
    Connects the client to MQTT server
    if it's not already connected.
    """
    logging.info("Connecting to MQTT server...")
    client.connect(MQTT_BROKER, port=MQTT_PORT)  # connect to MQTT broke
    logging.info("Connected...")


def mqtt_main():
    logging.info("Setting up MQTT client...")
    client = mqtt.Client()  # create new instance
    connect_mqtt(client)

    while True:
        message = input(">")

        if not client.is_connected():
            # connect to MQTT broker
            client.connect(MQTT_BROKER, port=MQTT_PORT)

        if not message:
            break
        client.publish(MQTT_TOPIC, message)


def main():
    format = "[%(asctime)s]: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    ip, port = "0.0.0.0", 8000
    server = EdgeServer(ip, port)
    th = threading.Thread(target=server.loop_forever, daemon=True)

    # mqtt_main()
    th.start()
    th.join()


if __name__ == "__main__":
    main()

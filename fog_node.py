# import paho.mqtt.client as mqtt
from edge.server import EdgeServer

MQTT_BROKER = "174.138.103.162"
MQTT_TOPIC = "/hello_world"
MQTT_PORT = 3881


def connect_mqtt(client):
    """
    Connects the client to MQTT server
    if it's not already connected.
    """
    client.connect(MQTT_BROKER, port=MQTT_PORT)  # connect to MQTT broke


def mqtt_main():
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
    # mqtt_main()
    ip, port = "0.0.0.0", 8000
    server = EdgeServer(ip, port)
    server.loop_forever()


if __name__ == "__main__":
    main()

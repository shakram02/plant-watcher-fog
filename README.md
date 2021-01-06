# Plant Watcher Fog Server

The fog server for plant node receives the sensor readings of the [Sensor Node](https://github.com/shakram02/plant-watcher-node) and forwards the readings to the MQTT server in the cloud. The fog node also communicates
with the TelegramAPI to send notifications to the user.

The code is broken down into 3 main parts

- UDP server + Communication protocol
- MQTT client
- TelegramAPI

### Steps

1. Build the container user `build_container.sh`
2. Run the container `run_container.sh`
3. This will open a terminal session, `cd` to `app`
4. Install script dependencies `pip install -r requirements.txt`
5. Run the script `python fog_node.py`
6. Open MQTT Explorer and establish the connection to make sure MQTT message arrive

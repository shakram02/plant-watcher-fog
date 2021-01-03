# Plant Watcher Node
Node for plant watching

### Steps
1. Build the container user `build_container.sh`
2. Run the container `run_container.sh`
3. This will open a terminal session, `cd` to `app`
4. Install script dependencies `pip install -r requirements.txt`
5. Run the script `python fog_node.py`
6. Open MQTT Explorer and establish the connection to make sure MQTT message arrive
docker build -t fog-node .
docker run -d -it -p 8000:8000/udp -p 8000:8000 --name fog_node --mount type=bind,source=$(pwd),target=/app fog-node:latest
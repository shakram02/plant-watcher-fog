#!/usr/bin/make

SHELL = /bin/sh

UID := $(shell id -u)
GID := $(shell id -g)

export UID
export GID

build:
	docker build -t fog-node:0.1 .
up: 
	docker-compose up -d
down:
	docker-compose down
shell:
	docker-compose exec node zsh
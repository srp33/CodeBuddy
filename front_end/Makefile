.PHONY: dev-server
dev-server: database
	NUM_PROCESSES=1 \
	PORT=8008 \
	MPORT=9798 \
	DEBUG=true \
	python3 server/webserver.py

database:
	mkdir -p database

.PHONY: html
html:
	./build_html.sh server/html

.PHONY: build-watch
build-watch:
	npm start

.PHONY: docker
docker:
	
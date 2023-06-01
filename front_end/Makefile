.PHONY: dev-server
dev-server: make-dirs
	DEBUG=true \
	python3 server/webserver.py

make-dirs:
	mkdir -p database logs

.PHONY: html
html:
	./build_html.sh server/html

.PHONY: build-watch
build-watch:
	npm install
	npm start

.PHONY: docker
docker:

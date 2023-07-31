.PHONY: dev
dev: 
	mkdir -p database logs \
    && bash build_html.sh server/html \
    && DEBUG=true \
    && python3 server/webserver.py

.PHONY: build-watch
build-watch:
	npm install
	npm start

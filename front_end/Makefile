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

.PHONY: sql
sql: 
	python3 test_database_query.py

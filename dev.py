from http.server import (
	SimpleHTTPRequestHandler as dev_handler,
	test as devserver
)
devserver(HandlerClass=dev_handler, port=8080)
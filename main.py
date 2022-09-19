import logging
import threading
from source.HTTPServer import ThreadedHTTPServer
from source.HTTPRequestHandler import DealUpdatesHandler
from source import config as cfg
from source import TelegramWorker


# journalctl logging when running via systemctl
logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT)


def http_serve():
    try:
        deals_update_server = ThreadedHTTPServer((cfg.HTTP_SERVER_ADDRESS, cfg.HTTP_SERVER_PORT), DealUpdatesHandler)

        while True:
            try:
                deals_update_server.serve_forever()
            except Exception as e:
                logging.error("HTTP server processing exception: ", e)

    except Exception as e:
        logging.error("HTTP server init exception: ", e)


def main():
    http_daemon = threading.Thread(name='deals_update_server', daemon=True,
                                   target=http_serve)
    http_daemon.start()

    # no message listening needed now
    TelegramWorker.run()


main()

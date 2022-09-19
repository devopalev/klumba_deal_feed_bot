from http.server import BaseHTTPRequestHandler
from urllib import parse
import logging

from source.BitrixFieldsAliases import *
from source import BitrixFieldsMappings
from source import TelegramWorker
from source import creds
from source import Jobs


logger = logging.getLogger(__name__)


class DealUpdatesHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            logger.info("New POST request accepted!")
            query = parse.urlparse(self.path).query
            query_components = parse.parse_qs(query, keep_blank_values=True)
            logger.info("Accepted query components: %s", query_components)

            if WEBHOOK_SECRET_ALIAS in query_components \
                    and query_components[WEBHOOK_SECRET_ALIAS][0] == creds.BITRIX_WEBHOOK_SECRET:

                action = query_components[WEBHOOK_ACTION_ALIAS][0]

                if action == BitrixFieldsMappings.BITRIX_ACTION_EQUIPPED:
                    TelegramWorker.JOB_QUEUE.run_once(callback=Jobs.deal_equipped, when=0, context=query_components)
                elif action == BitrixFieldsMappings.BITRIX_ACTION_DELIVERY:
                    TelegramWorker.JOB_QUEUE.run_once(callback=Jobs.deal_in_delivery, when=0, context=query_components)
                elif action == BitrixFieldsMappings.BITRIX_ACTION_WAITING_FOR_SUPPLY:
                    TelegramWorker.JOB_QUEUE.run_once(callback=Jobs.deal_waiting_for_supply, when=0,
                                                      context=query_components)
                elif action == BitrixFieldsMappings.BITRIX_ACTION_RESERVED:
                    TelegramWorker.JOB_QUEUE.run_once(callback=Jobs.deal_reserved, when=0, context=query_components)
                elif action == BitrixFieldsMappings.BITRIX_ACTION_UNAPPROVED:
                    TelegramWorker.JOB_QUEUE.run_once(callback=Jobs.deal_unapproved, when=0, context=query_components)
                else:
                    logger.error('Wrong Bitrix action passed: %s', action)
            else:
                logger.error('Wrong Bitrix webhook secret passed or not provided')

        except Exception as e:
            logger.error('HTTP request handling error: %s', e)


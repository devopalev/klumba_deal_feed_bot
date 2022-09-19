import requests
import time
from . import creds
import logging
from threading import Lock


SESSION = requests.session()
REQUESTS_TIMEOUT = 10
REQUESTS_MAX_ATTEMPTS = 3

QUERY_LIMIT_EXCEEDED = 'QUERY_LIMIT_EXCEEDED'
SLEEP_INTERVAL = 1

# Bitrix OAuth keys
# store in Telegram bot persistence to serialize automatically
OAUTH_LOCK = Lock()


logger = logging.getLogger(__name__)


def send_request(method, params=None, handle_next=False):
    if params is None:
        params = {}

    for a in range(REQUESTS_MAX_ATTEMPTS):
        try:
            response = SESSION.post(url=creds.BITRIX_API_URL + method,
                                    json=params, timeout=REQUESTS_TIMEOUT)

            if response and response.ok:
                json = response.json()

                error = json.get('error')

                # TODO: handle QUERY_LIMIT_EXCEEDED properly
                if error == QUERY_LIMIT_EXCEEDED:
                    time.sleep(SLEEP_INTERVAL)
                    continue

                next_counter = json.get('next')
                result = json.get('result')

                # handling List[]
                if result is not None and handle_next and next_counter:
                    params['start'] = next_counter
                    result.extend(send_request(method, params, True))
                    return result

                if result is not None:
                    return result
                else:
                    error = 'Bitrix bad response: %s\n Attempt: %s\n Request params: %s\n Error:%s' \
                            % (json, a, params, json.get('error_description'))
                    logger.error(error)
            else:
                error = 'Bitrix request failed - %s : Attempt: %s : Request params: %s' \
                        % (response.text, a, params)
                logger.error(error)

        except Exception as e:
            error = 'Sending Bitrix api request error %s' % e
            logger.error(error)

    return None


def generate_photo_link(obj, access_token):
    path = obj['downloadUrl'].replace('auth=', 'auth=' + access_token)
    return creds.BITRIX_MAIN_PAGE + path


def get_deal_photo_dl_urls(deal_id, access_token, field_aliases=()):
    deal = send_request('crm.deal.get', params={'id': deal_id})
    photos_list = []

    for fa in field_aliases:
        if fa in deal:
            data = deal[fa]
            if isinstance(data, list):
                for photo in data:
                    photos_list.append(generate_photo_link(photo, access_token))
            else:
                photos_list.append(generate_photo_link(data, access_token))

    return photos_list


def refresh_oauth(refresh_token):
    for a in range(REQUESTS_MAX_ATTEMPTS):
        try:
            response = SESSION.get(
                url=creds.BITRIX_OAUTH_REFRESH_URL.format(refresh_token),
                timeout=REQUESTS_TIMEOUT)

            if response and response.ok:
                json = response.json()

                access_token = json.get('access_token')
                refresh_token = json.get('refresh_token')

                logger.info('OAuth refreshed')
                return access_token, refresh_token
            else:
                logger.error("Error OAuth refreshing: %s", response)

        except Exception as e:
            error = 'Bitrix OAuth refresh exception %s' % e
            logger.error(error)

    return None, None

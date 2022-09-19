import logging

# dirs
DATA_DIR_NAME = '/home/.klumba_deal_feed'


# Telegram bot persistent storage
TG_STORAGE_NAME = 'bot_storage.pickle'
USER_PERSISTENT_KEY = 'USER_DATA'
BOT_REFRESH_TOKEN_PERSISTENT_KEY = 'BITRIX_REFRESH_TOKEN'
BOT_ACCESS_TOKEN_PERSISTENT_KEY = 'BITRIX_ACCESS_TOKEN'

# logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s :: %(levelname)s :: %(funcName)s :: (%(lineno)d) :: %(message)s'


# times
BITRIX_OAUTH_UPDATE_INTERVAL = 45 * 60  # seconds


HTTP_SERVER_PORT = 8080
HTTP_SERVER_ADDRESS = '0.0.0.0'

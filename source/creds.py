# TG_BOT_TOKEN = '1109255899:AAF1p3T3qWpr9sbRd2RAhDQxAaY06g80IrQ'
TG_BOT_TOKEN = '5538318245:AAG6HItBW90pi_57tIw3jfLc5yyY7VCSbOs'

BITRIX_MAIN_PAGE = 'https://klumba.bitrix24.ru'
# BITRIX_CRM_WEBHOOK_TOKEN = 'rl3koltt14ruuj4f'  # German version
# BITRIX_API_URL = BITRIX_MAIN_PAGE + '/rest/13459/' + BITRIX_CRM_WEBHOOK_TOKEN + '/'  # German version
BITRIX_CRM_WEBHOOK_TOKEN = 'q72jkkgrk3sjms9l'
BITRIX_API_URL = BITRIX_MAIN_PAGE + '/rest/41305/' + BITRIX_CRM_WEBHOOK_TOKEN + '/'
BITRIX_WEBHOOK_SECRET = 'QiP7hKz61syRFt4x0yFj'  # для вебхуков из БП в бота
BITRIX_APP_CLIENT_ID = 'local.5e709c8eaaecf4.42197745'
BITRIX_APP_CLIENT_SECRET = 'eB02M9RY77r2ObSyblQNxRVxDLFhufRWCgeaH1ZFIrOAL6eytu'

BITRIX_OAUTH_REFRESH_URL = 'https://oauth.bitrix.info/oauth/token/' \
                           '?grant_type=refresh_token' \
                           '&client_id=' + BITRIX_APP_CLIENT_ID + \
                           '&client_secret=' + BITRIX_APP_CLIENT_SECRET + \
                           '&refresh_token={}'

# tokens valid only for first app run
BITRIX_FIRST_OAUTH_ACCESS_TOKEN = 'f43ee7600045742a000103500000000500000389011688ea6817c5f757f8e657fedfac'
BITRIX_FIRST_OAUTH_REFRESH_TOKEN = 'e4bd0e610045742a0001035000000005000003a7be3d34822d8a7f69427d1768966104'

# NEW
# BITRIX_FIRST_OAUTH_ACCESS_TOKEN = "c42049630045742a000103500000a15900000748613a65d76e7eb9906aa994312a23fe"
# BITRIX_FIRST_OAUTH_REFRESH_TOKEN = "b49f70630045742a000103500000a159000007ef758be250446731924878f4c032bd20"


# GROUP_CHAT_ID = -377527534  # test env
EQUIPPED_GROUP_CHAT_ID = -1001293162043
DELIVERY_GROUP_CHAT_ID = -1001230141190
RESERVED_GROUP_CHAT_ID = -1001234188083
UNAPPROVED_GROUP_CHAT_ID = -1001740558545
FAILED_DEAL_GROUP_CHAT_ID = -1001586237396

# Late Deals Chat
LATE_DEALS_CHAT_ID = -1001871720175
# LATE_DEALS_CHAT_ID = -1001758642612  # Тестовый чат

# Reclamation CHAT
RECLAMATION_GROUP_CHAT_ID = -1001512624488

# Басово
FESTIVE_UNAPPROVED_BASOVO_CHAT_ID = -1001698457691
# Стадион
FESTIVE_UNAPPROVED_STADION_CHAT_ID = -1001742648236
# Павшинский мост ЦМЦ
FESTIVE_UNAPPROVED_PAVSH_CHAT_ID = -1001711228891
# Максима Горького
FESTIVE_UNAPPROVED_GORKOGO_CHAT_ID = -1001244657047
# Глобус
FESTIVE_UNAPPROVED_GLOBUS_CHAT_ID = -1001767367098
# Вильямса
FESTIVE_UNAPPROVED_VILYAMSA_CHAT_ID = -1001761252332
# Марата
FESTIVE_UNAPPROVED_MARATA_CHAT_ID = -1001437092221
# Тургеневская
FESTIVE_UNAPPROVED_TURGEN_CHAT_ID = -1001613261036
# Красноармейский
FESTIVE_UNAPPROVED_KRASN_CHAT_ID = -1001671442334

# Служба заказов
FESTIVE_UNAPPROVED_SLUZHBA_ZAKAZOV_CHAT_ID = -1001661034176
# Проектный отдел
FESTIVE_UNAPPROVED_PROYEKTNYY_OTDEL_CHAT_ID = -1001744007275
# Бухгалтерия/Администрация/Маркетинг
FESTIVE_UNAPPROVED_ADMINISTRATSIYA_OTDEL_CHAT_ID = -1001723836883

FESTIVE_UNAPPROVED_SALES_DEPARTMENT = {
    '3097': FESTIVE_UNAPPROVED_BASOVO_CHAT_ID,
    '3099': FESTIVE_UNAPPROVED_STADION_CHAT_ID,
    '3113': FESTIVE_UNAPPROVED_PAVSH_CHAT_ID,
    '3101': FESTIVE_UNAPPROVED_KRASN_CHAT_ID,
    '3103': FESTIVE_UNAPPROVED_TURGEN_CHAT_ID,
    '3107': FESTIVE_UNAPPROVED_MARATA_CHAT_ID,
    '3109': FESTIVE_UNAPPROVED_VILYAMSA_CHAT_ID,
    '3111': FESTIVE_UNAPPROVED_GLOBUS_CHAT_ID,
    '3105': FESTIVE_UNAPPROVED_GORKOGO_CHAT_ID,
    '3091': FESTIVE_UNAPPROVED_SLUZHBA_ZAKAZOV_CHAT_ID,
    '3093': FESTIVE_UNAPPROVED_PROYEKTNYY_OTDEL_CHAT_ID,
    '3095': FESTIVE_UNAPPROVED_ADMINISTRATSIYA_OTDEL_CHAT_ID
}

UNAPPROVED_SUBDIVISION = {"2293": FESTIVE_UNAPPROVED_BASOVO_CHAT_ID,
                          "2295": FESTIVE_UNAPPROVED_STADION_CHAT_ID,
                          "2297": FESTIVE_UNAPPROVED_KRASN_CHAT_ID,
                          "2299": FESTIVE_UNAPPROVED_TURGEN_CHAT_ID,
                          "2301": FESTIVE_UNAPPROVED_MARATA_CHAT_ID,
                          "2303": FESTIVE_UNAPPROVED_VILYAMSA_CHAT_ID,
                          "2305": FESTIVE_UNAPPROVED_GLOBUS_CHAT_ID,
                          "2517": FESTIVE_UNAPPROVED_GORKOGO_CHAT_ID,
                          "2883": FESTIVE_UNAPPROVED_PAVSH_CHAT_ID}


REQUEST_PASS_MESSAGE = 'Добро пожаловать в *ленту завершенных заказов Клумба*!\n' \
                               'Введите пароль для дальнейшей работы.\n' \

AUTHORIZATION_SUCCESSFUL = 'Авторизация по паролю пройдена!\n' \
                           'Теперь вы можете использовать возможности бота.'

AUTHORIZATION_UNSUCCESSFUL = 'Авторизация не пройдена. Попробуйте снова.'
UNKNOWN_COMMAND = 'Неизвестная команда. Попробуйте снова.'
UNKNOWN_COMMAND_TYPE = 'Команды должны быть переданы в текстовом виде.'

FILE_LOADING_FAILED = 'Произошла ошибка при загрузке файла. Попробуйте снова.'

BOT_HELP_TEXT = 'Лента завершенных заказов отображает следующую информацию о заказах в реальном времени: \n' \
                '*Номер заказа, Курьер, Ответственный, Что заказано, Флорист, Фото*'

ERROR_BITRIX_REQUEST = 'Произошла ошибка при обращении к серверу. \n' \
                       'Попробуйте снова или подождите некоторое время.'

# Now using: 'equipped', 'in delivery'
DEAL_TEMPLATE = '\nЗаказ {}\\!\n' \
                '*№ заказа:* {}\n' \
                '*Что заказано:* {}\n' \
                '*Курьер:* {}\n' \
                '*Ответственный:* {}\n' \
                '*Флорист:* {}\n' \
                '*Кто принял заказ:* {}\n' \
                '*Сумма:* {}\n' \
                '*Дата:* {}\n' \
                '*Время:* {}\n' \
                '*Тип заказа:* *{}*\n'
#               '{photo}'

DELIMITER_BLOCK_TEXT = '\-\-\-\-\-\-\-\-\-\-\-\n\n'

DEAL_DECLINE = '*Кто отклонил:* {}\n' \
        '*Комментарий по отклонению:* {}\n' + DELIMITER_BLOCK_TEXT



# Now using: 'reserved', 'waiting for supply'
DEAL_RESERVED_TEMPLATE = \
                '*№ заказа:* {}\n' \
                '*Что отложено:* {}\n' \
                '*Что заказано:* {}\n' \
                '*Ссылка на заказ:* {}\n' \
                '*Дата:* {}\n' \
                '*Время:* {}\n' \
                '*Тип заказа:* *{}*\n'\
                '*Кто принял заказ:* {}\n'\
                '*Комментарий по доставке:* {}\n'\
                '*Доставка/Самовывоз:* {}\n'\
                '*Подразделение:* {}\n'
#               '{photo}'

DEAL_WAITING_FOR_SUPPLY_STUB = 'Ждет поставки'
DEAL_NO_RESERVE_NEEDED_STUB = 'Резерв не нужен'

# Now using: 'waiting for supply'
DEAL_WAITING_FOR_SUPPLY_TEMPLATE = \
                '*№ заказа:* {}\n' \
                '*Что отложено:* {}\n' \
                '*Что заказано:* {}\n' \
                '*Ссылка на заказ:* {}\n' \
                '*Дата:* {}\n' \
                '*Время:* {}\n' \
                '*Тип заказа:* *{}*\n'\
                '*Кто принял заказ:* {}\n' \
                '*Комментарий по доставке:* {}\n' \
                '*Доставка/Самовывоз:* {}\n' \
                '*Подразделение:* {}\n'\
                '*Дата поставки:* {}\n'
#               '{photo}'


DEAL_UNAPPROVED_TEMPLATE = \
                '*№ заказа:* {}\n\n' \
                '*Что заказано:* {}\n' \
                '*Комментарий клиента:* {}\n' \
                '*Перезвонить клиенту:* {}\n\n' \
                '*Ответственный:* {}\n' \
                '*Флорист:* *{}*\n'\
                '*Кто укомплектовал заказ:* {}\n' \
                '*Дата:* {}\n' \
                '*Время:* {}\n' \
                '*Комментарий по доставке:* {}\n'\
                '*Источник:* {}\n' \
                '*Сумма:* {}'
#               '{photo}'




DEAL_STATE_EQUIPPED = 'укомплектован'
DEAL_STATE_DELIVERY = 'в доставке'

FIELD_IS_EMPTY_PLACEHOLDER = 'нет'

EQUIPPED_APPROVE_BUTTON_TEXT = 'Согласовать \U00002705'
EQUIPPED_APPROVE_BUTTON_KEY = 'equipped_approve'
EQUIPPED_DECLINE_BUTTON_TEXT = 'Отклонить \U0000274C'
EQUIPPED_DECLINE_BUTTON_KEY = 'equipped_decline'
EQUIPPED_REAPPROVE_BUTTON_TEXT = 'Исправлено, отправить на пересогласование \U00002705'
EQUIPPED_REAPPROVE_BUTTON_KEY_PREFIX = 'equipped_reapprove'

DECLINED_HEADER = '{} *ОТКЛОНЕН*\U0000274C \n'
APPROVED_HEADER = '{} *СОГЛАСОВАН*\U00002705 \n'
REAPPROVED_HEADER = '{} *ИСПРАВЛЕН*\U00002705 \n'

REQUEST_DECLINE_COMMENT = 'Отклоняем заказ {}.\n' \
                          'Напишите, почему?'
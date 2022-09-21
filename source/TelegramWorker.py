import datetime
import pytz

from source import creds
import logging
import os
import traceback
from source import config as cfg
from source import BitrixWorker as BW
from source.approve_equip import TgEquipApprove

from telegram.ext import Updater, MessageHandler, Filters, PicklePersistence, CallbackContext, JobQueue

from telegram import ParseMode, Update


logger = logging.getLogger(__name__)
JOB_QUEUE = None


def dummy_callback_handler(update: Update, context: CallbackContext):
    return None


def error_handler(update, context: CallbackContext):
    try:
        logger.error(msg="Exception while handling Telegram update:", exc_info=context.error)

        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = ''.join(tb_list)

        logger.error(tb_string)
    except Exception as e:
        logger.error(msg="Exception while handling lower-level exception:", exc_info=e)


def bitrix_oauth_update_job(context: CallbackContext):
    with BW.OAUTH_LOCK:
        refresh_token = context.bot_data[cfg.BOT_REFRESH_TOKEN_PERSISTENT_KEY]
        a_token, r_token = BW.refresh_oauth(refresh_token)

        if a_token:
            context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY] = a_token
            context.bot_data[cfg.BOT_REFRESH_TOKEN_PERSISTENT_KEY] = r_token


def reclamations_report_day(context: CallbackContext):
    params = {'filter': {'CLOSEDATE': str(datetime.date.today()), 'CATEGORY_ID': '45', 'CLOSED': 'Y'},
              'select': ['STAGE_ID']}
    res = BW.send_request('crm.deal.list', params=params, handle_next=True)
    all_r = len(res)
    good = 0
    for reclamation in res:
        good += 1 if 'WON' in reclamation.get('STAGE_ID') else 0
    bad = all_r - good
    percent = good / all_r * 100
    if percent > 95:
        emoji = '🟢'
    elif percent > 90:
        emoji = '🟡'
    elif percent > 85:
        emoji = '🟠'
    else:
        emoji = '🔴'

    text = f"{emoji} Отчет дня по рекламациям\n\n<b>Всего</b>: {all_r}\n<b>" \
           f"Успешных</b>: {good}\n<b>Проваленных</b>: {bad}"
    context.bot.send_message(creds.RECLAMATION_GROUP_CHAT_ID, text, ParseMode.HTML)


# entry point
def run():
    os.makedirs(cfg.DATA_DIR_NAME, exist_ok=True)
    storage = PicklePersistence(filename=os.path.join(cfg.DATA_DIR_NAME, cfg.TG_STORAGE_NAME))

    updater = Updater(creds.TG_BOT_TOKEN, persistence=storage)
    dispatcher = updater.dispatcher

    # handle Bitrix OAuth keys update here in job queue
    bot_data = dispatcher.bot_data
    if cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY not in bot_data:
        bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY] = creds.BITRIX_FIRST_OAUTH_ACCESS_TOKEN
        bot_data[cfg.BOT_REFRESH_TOKEN_PERSISTENT_KEY] = creds.BITRIX_FIRST_OAUTH_REFRESH_TOKEN

    jq = updater.job_queue
    jq.run_repeating(bitrix_oauth_update_job, interval=cfg.BITRIX_OAUTH_UPDATE_INTERVAL, first=1)
    tzinfo = pytz.timezone('Europe/Moscow')
    jq.run_daily(reclamations_report_day, days=(0, 1, 2, 3, 4), time=datetime.time(18, tzinfo=tzinfo))

    global JOB_QUEUE
    JOB_QUEUE = jq

    dispatcher.add_handler(TgEquipApprove.CV_REAPPROVE_EQUIP_HANDLER)
    dispatcher.add_handler(TgEquipApprove.CV_APPROVE_EQUIP_HANDLER)
    dispatcher.add_handler(MessageHandler(Filters.all, dummy_callback_handler))
    dispatcher.add_error_handler(error_handler)

    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()

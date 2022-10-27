import datetime
import logging
import os
import re
import time
import threading

from telegram.ext import CallbackContext, CallbackQueryHandler, Dispatcher
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, Message

import source.late_deals.BitrixHandler as BH
from source import Utils, creds
from source.BitrixFieldsAliases import WEBHOOK_DEAL_ID_ALIAS

logger = logging.getLogger(__name__)


class Storage:
    _lock = threading.Lock()
    data = {}
    storage_limit = datetime.timedelta(days=2)

    @classmethod
    def get_history(cls, deal_id):
        with cls._lock:
            return cls.data.get(deal_id)

    @classmethod
    def save(cls, deal_id, message_id, header):
        now = datetime.datetime.now()
        info = {"time": now, "message_id": message_id, "header": header}
        with cls._lock:
            curr: list = cls.data.get(deal_id)
            if curr:
                curr.append(info)
            else:
                cls.data[deal_id] = [info]

    @classmethod
    def rotation(cls):
        now = datetime.datetime.now()
        rot_data = {}
        with cls._lock:
            for deal_id, info in cls.data.items():
                if now - info[-1]['time'] < cls.storage_limit:
                    rot_data[deal_id] = info
            cls.data = rot_data

    @classmethod
    def delete(cls, deal_id):
        with cls._lock:
            return cls.data.pop(deal_id)


def create_reclamation(update: Update, context: CallbackContext):
    deal_id = update.callback_query.data.split(':')[1]
    fullname = update.callback_query.from_user.full_name
    link_user = f'<a href="tg://user?id={update.callback_query.from_user.id}">{fullname}</a>'
    massage_text = update.callback_query.message.text_html

    res = BH.create_reclamation(deal_id, fullname)
    if res:
        update.callback_query.edit_message_text(text=f"☠ Создана рекламация ({link_user})\n\n{massage_text}",
                                                parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        update.callback_query.message.reply_text("Не удалось создать рекламацию. \n@yngphenix, обрати внимание.")


def late_ok(update: Update, context: CallbackContext):
    fullname = update.callback_query.from_user.full_name
    link_user = f'<a href="tg://user?id={update.callback_query.from_user.id}">{fullname}</a>'
    massage_text = update.callback_query.message.text_html
    text = f"👌 Причины опоздания легитимны ({link_user})\n\n{massage_text}"
    update.callback_query.edit_message_text(text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def register_handlers(dispatcher: Dispatcher):
    dispatcher.add_handler(CallbackQueryHandler(late_ok, pattern="late_deal_ok"))
    dispatcher.add_handler(CallbackQueryHandler(create_reclamation, pattern="late_deal_new_reclamation"))


def late_deal(context: CallbackContext):
    query_components = context.job.context
    deal_id = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ID_ALIAS)
    key_stage = Utils.prepare_external_field(query_components, 'key_stage')

    # Форматируем текст
    text_event = Utils.prepare_external_field(query_components, 'text_event', False)
    text_event = re.sub('(_)', '\n', text_event)
    text_event = re.sub(r'(\[\d+\])', '', text_event)

    history = Storage.get_history(deal_id)
    # Добавляем историю уведомлений и очищаем старые
    if history:
        try:
            context.bot.delete_message(creds.LATE_DEALS_CHAT_ID, history[-1]['message_id'])
        except Exception as err:
            logger.error(f"Не удалось удалить прошлое сообщение (deal {deal_id}): {err}")
        history_text = "\n\n<b>История уведомлений:</b>"
        for event in history:
            history_text += f"\n<b>{event['time'].strftime('%m.%d %H:%M')}:</b> {event['header']}"
        text_event += history_text

    keyboard = [[InlineKeyboardButton("Ок 👌", callback_data="late_deal_ok")],
                [InlineKeyboardButton("Создать рекламацию ☠", callback_data=f"late_deal_new_reclamation:{deal_id}")]]

    # Если заказ опоздал, автоматически создаем рекламацию
    if str(key_stage) == '5':
        Storage.delete(deal_id)
        res = BH.create_reclamation(deal_id, "bot")
        if res:
            text_event = f"☠ Создана рекламация (автоматически)\n\n{text_event}"
            context.bot.send_message(chat_id=creds.LATE_DEALS_CHAT_ID, text=text_event,
                                     parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            return
        else:
            text_event = f"Не удалось автоматически создать рекламацию. \n@yngphenix, обрати внимание.\n\n{text_event}"
            context.bot.send_message(chat_id=creds.LATE_DEALS_CHAT_ID, text=text_event,
                                     reply_markup=InlineKeyboardMarkup(keyboard),
                                     parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        message = context.bot.send_message(chat_id=creds.LATE_DEALS_CHAT_ID, text=text_event,
                                           reply_markup=InlineKeyboardMarkup(keyboard),
                                           parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        header = text_event[0:text_event.find('\n')]
        Storage.save(deal_id, message.message_id, header)
        Storage.rotation()

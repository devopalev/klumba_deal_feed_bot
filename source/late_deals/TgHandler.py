import datetime
import logging
import os
import re
import time
import threading
from typing import List

from telegram.ext import CallbackContext, CallbackQueryHandler, Dispatcher
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, Message

import source.late_deals.BitrixHandler as BH
from source import Utils, creds
from source.BitrixFieldsAliases import WEBHOOK_DEAL_ID_ALIAS

logger = logging.getLogger(__name__)


class Event:
    def __init__(self, deal_id, messages: List[Message]):
        self.deal_id = deal_id
        self.messages = messages
        self.header = messages[-1].text[0:messages[-1].text.find('\n')]
        self.time = datetime.datetime.now()

    def delete_messages(self):
        for msg in self.messages:
            msg.delete()

    @property
    def time_str(self):
        return self.time.strftime('%m.%d %H:%M')


class Storage:
    _lock = threading.Lock()
    data = {}
    storage_limit = datetime.timedelta(days=2)

    @classmethod
    def get_history(cls, deal_id) -> List[Event]:
        with cls._lock:
            return cls.data.get(deal_id)

    @classmethod
    def save(cls, deal_id, messages: list):
        event = Event(deal_id, messages)
        with cls._lock:
            curr: list = cls.data.get(deal_id)
            if curr:
                curr.append(event)
            else:
                cls.data[deal_id] = [event]

    @classmethod
    def rotation(cls):
        now = datetime.datetime.now()
        rot_data = {}
        with cls._lock:
            for deal_id, events in cls.data.items():
                if now - events[-1].time < cls.storage_limit:
                    rot_data[deal_id] = events
            cls.data = rot_data

    @classmethod
    def delete(cls, deal_id):
        with cls._lock:
            cls.data.pop(deal_id)


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
            history[-1].delete_messages()
        except Exception as err:
            logger.error(f"Не удалось удалить прошлые сообщение (deal {deal_id}): {err}")
        history_text = "\n\n<b>История уведомлений:</b>"
        for event in history:
            history_text += f"\n<b>{event.time_str}:</b> {event.header}"
        text_event += history_text

    keyboard = [[InlineKeyboardButton("Ок 👌", callback_data="late_deal_ok")],
                [InlineKeyboardButton("Создать рекламацию ☠", callback_data=f"late_deal_new_reclamation:{deal_id}")]]

    # Если заказ опоздал, автоматически создаем рекламацию
    if str(key_stage) == '5':
        Storage.delete(deal_id)
        res = BH.create_reclamation(deal_id, "bot")
        context.bot.send_message(chat_id=creds.TIMERS_SLUZHBA_ZAKAZOV_CHAT_ID, text=text_event,
                                 parse_mode=ParseMode.HTML, disable_web_page_preview=True)
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
        mes1 = context.bot.send_message(chat_id=creds.TIMERS_SLUZHBA_ZAKAZOV_CHAT_ID, text=text_event,
                                        parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        mes2 = context.bot.send_message(chat_id=creds.LATE_DEALS_CHAT_ID, text=text_event,
                                        reply_markup=InlineKeyboardMarkup(keyboard),
                                        parse_mode=ParseMode.HTML, disable_web_page_preview=True)

        Storage.save(deal_id, [mes1, mes2])
        Storage.rotation()

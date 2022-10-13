from telegram.ext import CallbackContext, CallbackQueryHandler, Dispatcher
from telegram import Update, ParseMode

import source.late_deals.BitrixHandler as BH


def create_reclamation(update: Update, context: CallbackContext):
    deal_id = update.callback_query.data.split(':')[1]
    fullname = update.callback_query.from_user.full_name
    link_user = f'<a href="tg://user?id={update.callback_query.from_user.id}">{fullname}</a>'
    massage_text = update.callback_query.message.text
    text = f"☠ Создана рекламация ({link_user})\n\n{massage_text}"
    BH.create_reclamation(deal_id, fullname)
    update.callback_query.edit_message_text(text=text, parse_mode=ParseMode.HTML)


def late_ok(update: Update, context: CallbackContext):
    fullname = update.callback_query.from_user.full_name
    link_user = f'<a href="tg://user?id={update.callback_query.from_user.id}">{fullname}</a>'
    massage_text = update.callback_query.message.text
    text = f"👌 Причины опоздания легитимны ({link_user})\n\n{massage_text}"
    update.callback_query.edit_message_text(text=text, parse_mode=ParseMode.HTML)


def register_handlers(dispatcher: Dispatcher):
    dispatcher.add_handler(CallbackQueryHandler(late_ok, pattern="late_deal_ok"))
    dispatcher.add_handler(CallbackQueryHandler(create_reclamation, pattern="late_deal_new_reclamation"))


from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InputMediaPhoto, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update, Chat

import source.TextSnippets as Txt
import source.BitrixWorker as BW
import source.approve_equip.BitrixHandler as BH
import source.config as cfg
import source.creds as creds
from source.BitrixFieldsAliases import *


class State:
    WRITING_DECLINE_COMMENT = 10


def decision(update: Update, context: CallbackContext):
    action, deal_id = update.callback_query.data.split(":")

    if action == Txt.EQUIPPED_APPROVE_BUTTON_KEY:
        BH.approve_deal(deal_id)
        context.user_data.pop(cfg.APPROVE_EQUIP_DATA_KEY)
        msg_text = update.callback_query.message.text_markdown_v2
        update.effective_chat.send_message(Txt.APPROVED_HEADER.format(deal_id), parse_mode=ParseMode.MARKDOWN_V2)
        update.callback_query.edit_message_text(Txt.APPROVED_HEADER.format(deal_id) + msg_text,
                                                parse_mode=ParseMode.MARKDOWN_V2)
        return ConversationHandler.END

    elif action == Txt.EQUIPPED_DECLINE_BUTTON_KEY:
        update.effective_chat.send_message(Txt.REQUEST_DECLINE_COMMENT.format(deal_id),
                                           reply_to_message_id=update.callback_query.message.message_id)
        context.user_data[cfg.APPROVE_EQUIP_DATA_KEY] = {'message': update.callback_query.message, 'deal_id': deal_id}
        return State.WRITING_DECLINE_COMMENT


def comment(update: Update, context):
    text = update.message.text
    deal_message = context.user_data[cfg.APPROVE_EQUIP_DATA_KEY]['message']
    deal_id = context.user_data[cfg.APPROVE_EQUIP_DATA_KEY]['deal_id']

    comment = f"{update.message.from_user.full_name}: {text}"
    # send message to unapproved chat firstly
    BH.decline_deal(deal_id, comment)
    deal = BW.get_deal(deal_id)
    unapproved_chat_id = BH.get_shop_chat_id(deal)
    access_token = context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY]
    photo_urls = BW.get_deal_photo_dl_urls(deal, access_token, (DEAL_BIG_PHOTO_ALIAS,))

    if deal:
        unapproved_chat = Chat(bot=context.bot, id=unapproved_chat_id, type=Chat.SUPERGROUP)
        keyboard = [
            [InlineKeyboardButton(text=Txt.EQUIPPED_REAPPROVE_BUTTON_TEXT,
                                  callback_data=Txt.EQUIPPED_REAPPROVE_BUTTON_KEY_PREFIX + f":{deal_id}")]]

        link_user = f"[{update.message.from_user.full_name}](tg://user?id={update.message.from_user.id}"
        text_unapproved = Txt.DECLINED_HEADER.format(deal_id) + Txt.DEAL_DECLINE.format(link_user, context) + \
                          deal_message.text_markdown_v2

        if photo_urls:
            media_list = [InputMediaPhoto(media=el) for el in photo_urls]
            unapproved_chat.send_media_group(media=media_list)
        unapproved_chat.send_message(text_unapproved, reply_markup=InlineKeyboardMarkup(keyboard),
                                     parse_mode=ParseMode.MARKDOWN_V2)
        deal_message.edit_text(text_unapproved, parse_mode=ParseMode.MARKDOWN_V2)
        update.effective_chat.send_message(Txt.DECLINED_HEADER.format(deal_id), parse_mode=ParseMode.MARKDOWN_V2)
    return ConversationHandler.END


def reapprove(update: Update, context: CallbackContext):
    orig_text = update.callback_query.message.text.split(Txt.DELIMITER_BLOCK_TEXT)[1]
    deal_id = update.callback_query.data.split(':')[1]

    button_ok = InlineKeyboardButton(Txt.EQUIPPED_APPROVE_BUTTON_TEXT,
                                     callback_data=Txt.EQUIPPED_APPROVE_BUTTON_KEY + f":{deal_id}")
    button_reject = InlineKeyboardButton(Txt.EQUIPPED_DECLINE_BUTTON_TEXT,
                                         callback_data=Txt.EQUIPPED_DECLINE_BUTTON_KEY + f":{deal_id}")
    keyboard = InlineKeyboardMarkup([[button_ok], [button_reject]])

    access_token = context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY]
    photo_urls = BW.get_deal_photo_dl_urls(deal_id, access_token,
                                           (DEAL_BIG_PHOTO_ALIAS,))

    BH.reapprove_deal(deal_id)

    # 1024 symbols of caption only, if more -> need a message
    if photo_urls:
        media_list = [InputMediaPhoto(media=el) for el in photo_urls]
        context.bot.send_media_group(chat_id=creds.EQUIPPED_GROUP_CHAT_ID, media=media_list)

    context.bot.send_message(chat_id=creds.EQUIPPED_GROUP_CHAT_ID, text=orig_text,
                             parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

    text = Txt.REAPPROVED_HEADER.format(deal_id) + update.callback_query.message.text_markdown_v2
    update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN_V2)


def fallback(update, context):
    return None  # do nothing on fallbacks


CV_APPROVE_EQUIP_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(decision,
                    pattern=f"({Txt.EQUIPPED_APPROVE_BUTTON_KEY}|{Txt.EQUIPPED_DECLINE_BUTTON_KEY})")],
    states={State.WRITING_DECLINE_COMMENT: [MessageHandler(Filters.text & Filters.chat(creds.EQUIPPED_GROUP_CHAT_ID),
                                                           callback=comment)]},
    fallbacks=[MessageHandler(Filters.all, callback=fallback), CallbackQueryHandler(fallback)]
)

CV_REAPPROVE_EQUIP_HANDLER = CallbackQueryHandler(reapprove, pattern=Txt.EQUIPPED_REAPPROVE_BUTTON_KEY_PREFIX)


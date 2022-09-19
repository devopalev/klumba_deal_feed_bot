import os
import pathlib

from telegram.ext import CallbackContext, ConversationHandler
from telegram import InputMediaPhoto, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update

import source.TextSnippets as Txt
import source.BitrixWorker as BW
import source.config as cfg
import source.Utils as Utils
import source.creds as creds
from source.BitrixFieldsAliases import *
from source.BitrixFieldsMappings import *
from typing import Dict, List


class State:
    WRITING_DECLINE_COMMENT = 10


def decision(update: Update, context):
    action, deal_id = update.callback_query.data.split(":")

    if action == Txt.EQUIPPED_APPROVE_BUTTON_KEY:
        #TODO: описать поля созданные в битрикс
        update_obj = {
            BFA.FESTIVE_APPROVEMENT_ALIAS: BFM.FESTIVE_APPROVEMENT_YES,
            BFA.FESTIVE_DECLINE_USER_ALIAS: ''
        }
        BW.update_deal(deal_id, update_obj)

        msg_text = update.callback_query.message.text_markdown_v2
        update.effective_chat.send_message(Txt.APPROVED_HEADER.format(deal_id), parse_mode=ParseMode.MARKDOWN_V2)
        update.callback_query.edit_message_text(Txt.APPROVED_HEADER.format('') + msg_text,
                                                parse_mode=ParseMode.MARKDOWN_V2)
        return ConversationHandler.END

    elif action == Txt.EQUIPPED_DECLINE_BUTTON_KEY:
        update.effective_chat.send_message(Txt.REQUEST_DECLINE_COMMENT.format(deal_id),
                                           reply_to_message_id=update.callback_query.message.message_id)
        return State.WRITING_DECLINE_COMMENT


def comment(update: Update, context, user: BaseUser):
    comment = update.message.text
    deal_message = user.festive_data.deal_message
    deal_id = user.festive_data.deal_id

    # send message to unapproved chat firstly
    BH.decline_deal(deal_id, comment, user.bitrix_user_id)

    unapproved_chat_id = user.festive_data.subdiv_chat_id

    if unapproved_chat_id:
        unapproved_chat = Chat(bot=context.bot, id=unapproved_chat_id, type=Chat.SUPERGROUP)
        keyboard = [
            [InlineKeyboardButton(text=Txt.REAPPROVE_BUTTON_TEXT, callback_data=Txt.REAPPROVE_BUTTON_KEY_PREFIX +
                                                                                Cmd.CMD_DELIMETER + deal_id)]]

        reserve_desc = HttpTxt.DEAL_RESERVE_DESC_ELT.format(user.festive_data.deal_reserve_desc) \
            if user.festive_data.deal_reserve_desc != GlobalTxt.FIELD_IS_EMPTY_PLACEHOLDER else ''
        prepaid = HttpTxt.DEAL_PREPAID_ELT.format(user.festive_data.deal_prepaid) \
            if user.festive_data.deal_pay_type == BFM.DEAL_PAY_PREPAID_FRIENDLY else ''
        terminal = HttpTxt.DEAL_TERMINAL_ELT.format(user.festive_data.deal_terminal) \
            if user.festive_data.deal_pay_type == BFM.DEAL_PAY_PERSONAL_FRIENDLY else ''
        change = HttpTxt.DEAL_CHANGE_ELT.format(user.festive_data.deal_change) \
            if user.festive_data.deal_terminal != BFM.DEAL_PAY_TERMINAL_FRIENDLY else ''

        if user.festive_data.photo_urls:
            media_list = [InputMediaPhoto(media=el) for el in user.festive_data.photo_urls]
            context.bot.send_media_group(chat_id=unapproved_chat_id, media=media_list)

        TgCommons.send_mdv2_chat(unapproved_chat, Txt.DECLINED_HEADER.format(deal_id) +
                                 Txt.DEAL_DECLINED.format(user.festive_data.deal_user_declined,
                                                          Utils.prepare_str(comment),
                                                          user.festive_data.deal_accepted,
                                                          user.festive_data.deal_subdivision,
                                                          user.festive_data.deal_link,
                                                          user.festive_data.deal_order,
                                                          user.festive_data.deal_date,
                                                          user.festive_data.deal_time,
                                                          user.festive_data.deal_sum,
                                                          user.festive_data.deal_source,
                                                          user.festive_data.deal_contact,
                                                          reserve_desc, user.festive_data.deal_delivery_type,
                                                          user.festive_data.deal_district,
                                                          user.festive_data.deal_address,
                                                          user.festive_data.deal_delivery_comment,
                                                          user.festive_data.deal_pay_method,
                                                          user.festive_data.deal_pay_type, prepaid, terminal, change,
                                                          user.festive_data.deal_to_pay,
                                                          user.festive_data.deal_pay_status
                                                          ),
                                 keyboard)

        TgCommons.send_mdv2_chat(update.effective_chat, Txt.DECLINED_HEADER.format(deal_id))

        TgCommons.edit_mdv2(deal_message, msg_text=Txt.DECLINED_HEADER.format('')
                                                   + deal_message.text_markdown_v2, need_cancel=False)

    return ConversationHandler.END


def reapprove(update: Update, context, user: BaseUser):
    deal_id = context.match.group(1)
    deal = BW.get_deal(deal_id)

    stage_id = deal.get(BFA.DEAL_STAGE_ALIAS)
    deal_stage = Utils.prepare_external_field(BW.STAGES, stage_id, BW.STAGES_LOCK)

    deal_order = Utils.prepare_external_field(deal, BFA.DEAL_ORDER_ALIAS)

    deal_date = Utils.prepare_deal_date(deal, BFA.DEAL_DATE_ALIAS)
    deal_time = Utils.prepare_deal_time(deal, BFA.DEAL_TIME_ALIAS)
    deal_sum = Utils.prepare_external_field(deal, BFA.DEAL_TOTAL_SUM_ALIAS)

    order_received_by_id = deal.get(BFA.DEAL_ORDER_RECEIVED_BY_ALIAS)
    deal_accepted = Utils.prepare_external_field(BW.BITRIX_IDS_USERS, order_received_by_id,
                                                 BW.BITRIX_USERS_LOCK)

    source_id = Utils.prepare_external_field(deal, BFA.DEAL_SOURCE_ID_ALIAS)
    deal_source = Utils.prepare_external_field(BW.SOURCES, source_id, BW.SOURCES_LOCK)

    contact_id = Utils.prepare_external_field(deal, BFA.DEAL_CONTACT_ALIAS)

    contact_data = BW.get_contact_data(contact_id)
    contact_name = contact_data.get(BFA.CONTACT_USER_NAME_ALIAS)
    contact_phone = contact_data.get(BFA.CONTACT_PHONE_ALIAS)
    deal_contact = contact_name + ' ' + contact_phone

    subdivision_id = Utils.prepare_external_field(deal, BFA.DEAL_SUBDIVISION_ALIAS)
    deal_subdivision = Utils.prepare_external_field(BW.SUBDIVISIONS, subdivision_id, BW.SUBDIVISIONS_LOCK)

    deal_has_reserve = Utils.prepare_external_field(deal, BFA.DEAL_ORDER_HAS_RESERVE_ALIAS)
    deal_reserve_desc = Utils.prepare_external_field(deal, BFA.DEAL_ORDER_RESERVE_DESC_ALIAS)

    deal_delivery_type = Utils.prepare_deal_supply_method(deal, BFA.DEAL_SUPPLY_METHOD_ALIAS)

    district_id = Utils.prepare_external_field(deal, BFA.DEAL_DISTRICT_ALIAS)
    deal_district = Utils.prepare_external_field(BW.DISTRICTS, district_id, BW.DISTRICTS_LOCK)

    address, location = Utils.prepare_deal_address(deal, BFA.DEAL_ADDRESS_ALIAS)
    deal_address = address

    deal_delivery_comment = Utils.prepare_external_field(deal, BFA.DEAL_DELIVERY_COMMENT_ALIAS)

    payment_type_id = Utils.prepare_external_field(deal, BFA.DEAL_PAYMENT_TYPE_ALIAS)
    deal_pay_type = Utils.prepare_external_field(BW.PAYMENT_TYPES, payment_type_id, BW.PAYMENT_TYPES_LOCK)

    payment_method_id = Utils.prepare_external_field(deal, BFA.DEAL_PAYMENT_METHOD_ALIAS)
    deal_pay_method = Utils.prepare_external_field(BW.PAYMENT_METHODS, payment_method_id,
                                                   BW.PAYMENT_METHODS_LOCK)

    deal_prepaid = Utils.prepare_external_field(deal, BFA.DEAL_PREPAID_ALIAS)

    deal_terminal = Utils.prepare_external_field(BW.DEAL_TERMINAL_CHANGE_MAPPING,
                                                 Utils.prepare_external_field(deal, BFA.DEAL_TERMINAL_CHANGE_ALIAS))
    deal_change = Utils.prepare_external_field(deal, BFA.DEAL_CHANGE_SUM_ALIAS)

    deal_to_pay = Utils.prepare_external_field(deal, BFA.DEAL_TO_PAY_ALIAS)

    deal_pay_status = Utils.prepare_external_field(deal, BFA.DEAL_PAYMENT_STATUS_ALIAS)

    if deal_has_reserve == BFM.DEAL_HAS_RESERVE_YES:
        with BW.BITRIX_USERS_LOCK:
            access_token = context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY]
            photo_urls = BW.process_deal_photo_dl_urls(deal, access_token, (BFA.DEAL_ORDER_RESERVE_ALIAS,))
    else:
        photo_urls = None

    BH.reapprove_deal(deal_id)
    HttpJobs.send_festive_deal_message(context.bot, deal_id, deal_stage, deal_order,
                                       deal_date, deal_time, deal_sum, deal_accepted,
                                       deal_source, deal_contact, deal_subdivision, deal_reserve_desc,
                                       deal_delivery_type, deal_district, deal_address, deal_delivery_comment,
                                       deal_pay_method, deal_pay_type, deal_prepaid, deal_terminal, deal_change,
                                       deal_to_pay, deal_pay_status,
                                       photo_urls)

    edited_msg = re.sub(re.escape(Txt.DECLINED_HEADER.format(deal_id)), Txt.REAPPROVED_HEADER.format(deal_id),
                        update.effective_message.text_markdown_v2)

    TgCommons.edit_mdv2(update.effective_message, msg_text=edited_msg,
                        need_cancel=False)


def fallback(update, context, user: BaseUser):
    return None  # do nothing on fallbacks


FESTIVE_CB_HANDLER = FestiveCBQ.FestiveCBQ(callback=festive_decision, pattern=Txt.FESTIVE_ACTION_PATTERN)
FESTIVE_MESSAGE_HANDLER = MessageHandler(Filters.text & Filters.chat(creds.FESTIVE_APPROVAL_CHAT_ID), festive_comment)
FESTIVE_CV_HANDLER = ConversationHandler(entry_points=[FESTIVE_CB_HANDLER],
                                         states={
                                             State.WRITING_DECLINE_COMMENT: [FESTIVE_MESSAGE_HANDLER]
                                         },
                                         fallbacks=[MessageHandler(Filters.all, fallback),
                                                    CallbackQueryHandler(callback=fallback,
                                                                         pattern=GlobalTxt.ANY_STRING_PATTERN)])

FESTIVE_REAPPROVE_HANDLER = FestiveCBQ.FestiveUnapprovedCBQ(callback=festive_reapprove,
                                                            pattern=Txt.FESTIVE_REAPPROVE_PATTERN)

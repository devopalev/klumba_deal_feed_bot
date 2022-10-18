import pathlib

import requests
from telegram.ext import CallbackContext
from telegram import InputMediaPhoto, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, InputFile

import source.TextSnippets as Txt
import source.BitrixWorker as BW
import source.config as cfg
import source.Utils as Utils
import source.creds as creds
from source.BitrixFieldsAliases import *
from source.BitrixFieldsMappings import *


def deal_equipped(context: CallbackContext):
    query_components = context.job.context
    bot = context.bot

    with BW.OAUTH_LOCK:
        access_token = context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY]

        deal_id = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ID_ALIAS)
        deal_responsible = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_RESPONSIBLE_ALIAS)
        deal_florist = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_FLORIST_ALIAS)
        deal_order = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ORDER_ALIAS)
        deal_courier = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_COURIER_ALIAS)
        deal_accepted = Utils.prepare_external_field(query_components, WEBHOOK_ACCEPTED_ALIAS)
        deal_sum = Utils.prepare_external_field(query_components, WEBHOOK_SUM_ALIAS)
        deal_date = Utils.prepare_external_field(query_components, WEBHOOK_DATE_ALIAS)
        deal_time = Utils.prepare_external_field(query_components, WEBHOOK_TIME_ALIAS)
        deal_type = Utils.prepare_external_field(query_components, WEBHOOK_TYPE_ALIAS)

        deal_message = Txt.DEAL_TEMPLATE.format(Txt.DEAL_STATE_EQUIPPED, deal_id,
                                                deal_order, deal_courier,
                                                deal_responsible, deal_florist, deal_accepted,
                                                deal_sum, deal_date, deal_time, deal_type)

        if deal_id != Txt.FIELD_IS_EMPTY_PLACEHOLDER:
            button_ok = InlineKeyboardButton(Txt.EQUIPPED_APPROVE_BUTTON_TEXT,
                                             callback_data=Txt.EQUIPPED_APPROVE_BUTTON_KEY + f":{deal_id}")
            button_reject = InlineKeyboardButton(Txt.EQUIPPED_DECLINE_BUTTON_TEXT,
                                                 callback_data=Txt.EQUIPPED_DECLINE_BUTTON_KEY + f":{deal_id}")
            keyboard = InlineKeyboardMarkup([[button_ok], [button_reject]])

            photo_urls = BW.get_deal_photo_dl_urls(deal_id, access_token,
                                                   (DEAL_BIG_PHOTO_ALIAS, DEAL_POSTCARD_PHOTO_ALIAS,
                                                    DEAL_CHECKLIST_PHOTO_ALIAS))

            # 1024 symbols of caption only, if more -> need a message
            if photo_urls:
                media_list = [InputMediaPhoto(media=el) for el in photo_urls]
                media_list[0].caption = f'⬇⬇⬇ {deal_id} ⬇⬇⬇'
                bot.send_media_group(chat_id=creds.EQUIPPED_GROUP_CHAT_ID, media=media_list)
            else:
                deal_message = "*Фото не найдены!*\n\n" + deal_message
            bot.send_message(chat_id=creds.EQUIPPED_GROUP_CHAT_ID, text=deal_message,
                             parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)


def deal_in_delivery(context: CallbackContext):
    query_components = context.job.context
    bot = context.bot

    with BW.OAUTH_LOCK:
        access_token = context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY]

        deal_id = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ID_ALIAS)
        deal_responsible = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_RESPONSIBLE_ALIAS)
        deal_florist = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_FLORIST_ALIAS)
        deal_order = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ORDER_ALIAS)
        deal_courier = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_COURIER_ALIAS)
        deal_accepted = Utils.prepare_external_field(query_components, WEBHOOK_ACCEPTED_ALIAS)
        deal_sum = Utils.prepare_external_field(query_components, WEBHOOK_SUM_ALIAS)
        deal_date = Utils.prepare_external_field(query_components, WEBHOOK_DATE_ALIAS)
        deal_time = Utils.prepare_external_field(query_components, WEBHOOK_TIME_ALIAS)
        deal_type = Utils.prepare_external_field(query_components, WEBHOOK_TYPE_ALIAS)

        deal_message = Txt.DEAL_TEMPLATE.format(Txt.DEAL_STATE_DELIVERY, deal_id,
                                                deal_order, deal_courier,
                                                deal_responsible, deal_florist, deal_accepted,
                                                deal_sum, deal_date, deal_time, deal_type)

        if deal_id != Txt.FIELD_IS_EMPTY_PLACEHOLDER:
            photo_urls = BW.get_deal_photo_dl_urls(deal_id, access_token,
                                                   (DEAL_BIG_PHOTO_ALIAS,
                                                    DEAL_CHECKLIST_PHOTO_ALIAS))

            # 1024 symbols of caption only, if more -> need a message
            if photo_urls:
                media_list = [InputMediaPhoto(media=el) for el in photo_urls]
                media_list[0].caption = deal_message
                media_list[0].parse_mode = ParseMode.MARKDOWN_V2

                bot.send_media_group(chat_id=creds.DELIVERY_GROUP_CHAT_ID, media=media_list)
            else:
                bot.send_message(chat_id=creds.DELIVERY_GROUP_CHAT_ID, text=deal_message,
                                 parse_mode=ParseMode.MARKDOWN_V2)


def deal_waiting_for_supply(context: CallbackContext):
    query_components = context.job.context
    bot = context.bot

    deal_id = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ID_ALIAS)
    deal_order = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ORDER_ALIAS)
    deal_accepted = Utils.prepare_external_field(query_components, WEBHOOK_ACCEPTED_ALIAS)
    deal_link = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_SITE_LINK_ALIAS)
    deal_date = Utils.prepare_external_field(query_components, WEBHOOK_DATE_ALIAS)
    deal_time = Utils.prepare_external_field(query_components, WEBHOOK_TIME_ALIAS)
    deal_type = Utils.prepare_external_field(query_components, WEBHOOK_TYPE_ALIAS)
    deal_supply_date = Utils.prepare_external_field(query_components, WEBHOOK_SUPPLY_DATE_ALIAS)
    deal_delivery_comment = Utils.prepare_external_field(query_components, WEBHOOK_DELIVERY_COMMENT_ALIAS)
    deal_delivery_type = Utils.prepare_external_field(query_components, WEBHOOK_DELIVERY_TYPE_ALIAS)
    deal_subdivision = Utils.prepare_external_field(query_components, WEBHOOK_SUBDIVISION_ALIAS)

    deal_message = Txt.DEAL_WAITING_FOR_SUPPLY_TEMPLATE.format(deal_id,
                                                               Txt.DEAL_WAITING_FOR_SUPPLY_STUB, deal_order,
                                                               deal_link, deal_date, deal_time, deal_type,
                                                               deal_accepted, deal_delivery_comment, deal_delivery_type,
                                                               deal_subdivision, deal_supply_date)

    if deal_id != Txt.FIELD_IS_EMPTY_PLACEHOLDER:
        photo_stub_path = pathlib.Path(__file__).parent.resolve() / 'data/waiting_for_supply.png'

        with open(photo_stub_path, 'rb') as f:
            bot.send_photo(chat_id=creds.RESERVED_GROUP_CHAT_ID, photo=f,
                           caption=deal_message, parse_mode=ParseMode.MARKDOWN_V2)


def deal_reserved(context: CallbackContext):
    query_components = context.job.context
    bot = context.bot

    deal_id = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ID_ALIAS)
    deal_order = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ORDER_ALIAS)
    deal_accepted = Utils.prepare_external_field(query_components, WEBHOOK_ACCEPTED_ALIAS)
    deal_link = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_SITE_LINK_ALIAS)
    deal_is_reserved = Utils.prepare_external_field(query_components, WEBHOOK_IS_RESERVED_ALIAS)
    deal_date = Utils.prepare_external_field(query_components, WEBHOOK_DATE_ALIAS)
    deal_time = Utils.prepare_external_field(query_components, WEBHOOK_TIME_ALIAS)
    deal_type = Utils.prepare_external_field(query_components, WEBHOOK_TYPE_ALIAS)
    deal_delivery_comment = Utils.prepare_external_field(query_components, WEBHOOK_DELIVERY_COMMENT_ALIAS)
    deal_delivery_type = Utils.prepare_external_field(query_components, WEBHOOK_DELIVERY_TYPE_ALIAS)
    deal_subdivision = Utils.prepare_external_field(query_components, WEBHOOK_SUBDIVISION_ALIAS)

    deal_reserved_str = Utils.prepare_external_field(query_components, WEBHOOK_RESERVED_STR_ALIAS) \
        if deal_is_reserved.lower() == DEAL_IS_RESERVED_YES.lower() else Txt.DEAL_NO_RESERVE_NEEDED_STUB

    deal_message = Txt.DEAL_RESERVED_TEMPLATE.format(deal_id,
                                                     deal_reserved_str, deal_order,
                                                     deal_link, deal_date, deal_time, deal_type, deal_accepted,
                                                     deal_delivery_comment, deal_delivery_type, deal_subdivision)

    with BW.OAUTH_LOCK:
        access_token = context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY]

        if deal_id != Txt.FIELD_IS_EMPTY_PLACEHOLDER:
            if deal_is_reserved.lower() == DEAL_IS_RESERVED_YES.lower():
                photo_urls = BW.get_deal_photo_dl_urls(deal_id, access_token,
                                                       (DEAL_RESERVE_PHOTO_ALIAS,))

                # 1024 symbols of caption only, if more -> need a message
                if photo_urls:
                    media_list = [InputMediaPhoto(media=el) for el in photo_urls]
                    media_list[0].caption = deal_message
                    media_list[0].parse_mode = ParseMode.MARKDOWN_V2

                    bot.send_media_group(chat_id=creds.RESERVED_GROUP_CHAT_ID, media=media_list)
                else:
                    bot.send_message(chat_id=creds.RESERVED_GROUP_CHAT_ID, text=deal_message,
                                     parse_mode=ParseMode.MARKDOWN_V2)
            else:
                photo_stub_path = pathlib.Path(__file__).parent.resolve() / 'data/no_reserve_needed.png'

                with open(photo_stub_path, 'rb') as f:
                    bot.send_photo(chat_id=creds.RESERVED_GROUP_CHAT_ID, photo=f,
                                   caption=deal_message, parse_mode=ParseMode.MARKDOWN_V2)


def deal_unapproved(context: CallbackContext):
    query_components = context.job.context
    bot = context.bot

    with BW.OAUTH_LOCK:
        access_token = context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY]

        deal_id = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ID_ALIAS)
        deal_order = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ORDER_ALIAS)
        deal_client_comment = Utils.prepare_external_field(query_components, WEBHOOK_CLIENT_COMMENT_ALIAS)
        deal_client_callback = Utils.prepare_external_field(query_components, WEBHOOK_CLIENT_CALLBACK_ALIAS)
        deal_responsible = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_RESPONSIBLE_ALIAS)
        deal_florist = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_FLORIST_ALIAS)
        deal_equipper = Utils.prepare_external_field(query_components, WEBHOOK_EQUIPPER_ALIAS)
        deal_date = Utils.prepare_external_field(query_components, WEBHOOK_DATE_ALIAS)
        deal_time = Utils.prepare_external_field(query_components, WEBHOOK_TIME_ALIAS)
        deal_delivery_comment = Utils.prepare_external_field(query_components, WEBHOOK_DELIVERY_COMMENT_ALIAS)
        deal_source = Utils.prepare_external_field(query_components, WEBHOOK_SOURCE_ALIAS)
        deal_sum = Utils.prepare_external_field(query_components, WEBHOOK_SUM_ALIAS)

        deal_message = Txt.DEAL_UNAPPROVED_TEMPLATE.format(deal_id,
                                                           deal_order, deal_client_comment, deal_client_callback,
                                                           deal_responsible, deal_florist, deal_equipper,
                                                           deal_date, deal_time, deal_delivery_comment, deal_source,
                                                           deal_sum)

        if deal_id != Txt.FIELD_IS_EMPTY_PLACEHOLDER:
            photo_urls = BW.get_deal_photo_dl_urls(deal_id, access_token,
                                                   (DEAL_BIG_PHOTO_ALIAS,))

            # 1024 symbols of caption only, if more -> need a message
            if photo_urls:
                media_list = [InputMediaPhoto(media=el) for el in photo_urls]
                media_list[0].caption = deal_message
                media_list[0].parse_mode = ParseMode.MARKDOWN_V2

                bot.send_media_group(chat_id=creds.UNAPPROVED_GROUP_CHAT_ID, media=media_list)
            else:
                bot.send_message(chat_id=creds.UNAPPROVED_GROUP_CHAT_ID, text=deal_message,
                                 parse_mode=ParseMode.MARKDOWN_V2)

        # В чат магазина
        deal: dict = BW.send_request('crm.deal.get', params={'id': deal_id})
        if deal:
            shop_id = deal.get("UF_CRM_1612453867429")

            if shop_id:
                # 1024 symbols of caption only, if more -> need a message
                if photo_urls:
                    media_list = [InputMediaPhoto(media=el) for el in photo_urls]
                    media_list[0].caption = deal_message
                    media_list[0].parse_mode = ParseMode.MARKDOWN_V2

                    bot.send_media_group(chat_id=creds.UNAPPROVED_SUBDIVISION.get(shop_id), media=media_list)
                else:
                    bot.send_message(chat_id=creds.UNAPPROVED_SUBDIVISION.get(shop_id), text=deal_message,
                                     parse_mode=ParseMode.MARKDOWN_V2)


def deal_failed(context: CallbackContext):
    query_components = context.job.context
    bot = context.bot

    deal_id = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ID_ALIAS, False)
    deal_responsible = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_RESPONSIBLE_ALIAS, False)
    deal_order = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ORDER_ALIAS, False)
    deal_sum = Utils.prepare_external_field(query_components, WEBHOOK_SUM_ALIAS, False)
    deal_source = Utils.prepare_external_field(query_components, WEBHOOK_SOURCE_ALIAS, False)
    deal_repeat = 'да' if 'Y' in query_components.get(WEBHOOK_IS_RETURN_CUSTOMER_ALIAS) else 'нет'
    deal_create_date = Utils.prepare_external_field(query_components, WEBHOOK_CREATE_DATE_ALIAS, False)
    deal_possible_closing_date = Utils.prepare_external_field(query_components, WEBHOOK_POSSIBLE_CLOSING_DATE, False)
    deal_cause_failed = Utils.prepare_external_field(query_components, WEBHOOK_CAUSE_FAILED_ALIAS, False)
    deal_contact = Utils.prepare_external_field(query_components, WEBHOOK_CONTACT_ALIAS, False)
    deal_date = Utils.prepare_external_field(query_components, WEBHOOK_DATE_ALIAS, False)
    deal_time = Utils.prepare_external_field(query_components, WEBHOOK_TIME_ALIAS, False)
    verification_kk = Utils.prepare_external_field(query_components, WEBHOOK_VERIFICATION_KK_ALIAS, False)
    verification_kk = ('❌ ' if 'рекламация' in verification_kk else '✅ ') + verification_kk
    text = Txt.DEAL_FAILED_TEMPLATE.format(deal_id, deal_responsible, deal_source, deal_order, deal_sum, deal_repeat,
                                           deal_create_date, deal_possible_closing_date, deal_date, deal_time,
                                           deal_cause_failed, deal_contact, verification_kk)

    bot.send_message(chat_id=creds.FAILED_DEAL_GROUP_CHAT_ID, text=text,
                     parse_mode=ParseMode.HTML)


def reclamation_report(context: CallbackContext):
    query_components = context.job.context

    doc_id = query_components.get(WEBHOOK_RECLAMATION_REPORT_ALIAS)[0]
    recl_id = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ID_ALIAS)
    recl_stage = Utils.prepare_external_field(query_components, WEBHOOK_RECLAMATION_STAGE_ALIAS)
    res = BW.send_request('crm.documentgenerator.document.get', params={'id': doc_id})

    if res:
        url = res['document'].get('pdfUrlMachine')
        pdf = requests.get(url)

        file = InputFile(pdf.content, f"report_{recl_id}.pdf")
        caption = f"📢 Закрыта рекламация №{recl_id}\n<b>Результат:</b> {recl_stage}"
        context.bot.send_document(creds.RECLAMATION_GROUP_CHAT_ID, file, caption=caption, parse_mode=ParseMode.HTML)


def reclamation_new(context: CallbackContext):
    query_components = context.job.context
    recl_id = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ID_ALIAS)
    recl_source = Utils.prepare_external_field(query_components, WEBHOOK_SOURCE_ALIAS)
    text = f"📢 Создана рекламация №{recl_id}\n<b>Источник:</b> {recl_source}"
    context.bot.send_message(chat_id=creds.RECLAMATION_GROUP_CHAT_ID, text=text, parse_mode=ParseMode.HTML)


def late_deal(context: CallbackContext):
    query_components = context.job.context
    deal_id = Utils.prepare_external_field(query_components, WEBHOOK_DEAL_ID_ALIAS)
    text_event = Utils.prepare_external_field(query_components, 'text_event', False).replace('_', '\n')
    keyboard = [[InlineKeyboardButton("Ок 👌", callback_data="late_deal_ok")],
                [InlineKeyboardButton("Создать рекламацию ☠", callback_data=f"late_deal_new_reclamation:{deal_id}")]]

    context.bot.send_message(chat_id=-1001871720175, text=text_event, reply_markup=InlineKeyboardMarkup(keyboard),
                             parse_mode=ParseMode.HTML, disable_web_page_preview=True)

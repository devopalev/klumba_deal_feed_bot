import os
import pathlib

from telegram.ext import CallbackContext, ConversationHandler
from telegram import InputMediaPhoto, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update

import source.TextSnippets as Txt
import source.BitrixWorker as BW
import source.BitrixFieldsAliases as BFA
import source.BitrixFieldsMappings as BFM
import source.config as cfg
import source.Utils as Utils
import source.creds as creds
from source.BitrixFieldsAliases import *
from source.BitrixFieldsMappings import *
from typing import Dict, List


def approve_deal(deal_id):
    BW.update_deal(deal_id, {BFA.EQUIPPED_APPROVEMENT_ALIAS: BFM.EQUIPPED_APPROVEMENT_OK})


def decline_deal(deal_id, comment):
    update_obj = {
        BFA.EQUIPPED_APPROVEMENT_ALIAS: BFM.EQUIPPED_APPROVEMENT_REJECT,
        BFA.EQUIPPED_DECLINE_COMMENT_ALIAS: comment,
    }
    BW.update_deal(deal_id, update_obj)


def get_shop_chat_id(deal: dict):
    value = deal.get(BFA.DEAL_SHOP_PERFORMER)
    return creds.UNAPPROVED_SHOPS.get(value)


def get_info(context, deal_id, user: BaseUser):
    deal = BW.get_deal(deal_id)

    user.festive_data.deal_link = Utils.prepare_external_field(deal, BFA.DEAL_LINK_ALIAS)
    user.festive_data.deal_order = Utils.prepare_external_field(deal, BFA.DEAL_ORDER_ALIAS)

    user.festive_data.deal_user_declined = Utils.prepare_external_field(BW.BITRIX_IDS_USERS, user.bitrix_user_id,
                                                                        BW.BITRIX_USERS_LOCK)

    sales_dev_id = deal.get(BFA.DEAL_SALES_DIVISION_ALIAS)
    # subdiv_name = Utils.prepare_external_field(BW.SUBDIVISIONS, subdiv_id,
    #                                            BW.SUBDIVISIONS_LOCK, escape_md=False)
    user.festive_data.subdiv_chat_id = creds.FESTIVE_UNAPPROVED_SUBDIVS.get(sales_dev_id)

    user.festive_data.deal_date = Utils.prepare_deal_date(deal, BFA.DEAL_DATE_ALIAS)
    user.festive_data.deal_time = Utils.prepare_deal_time(deal, BFA.DEAL_TIME_ALIAS)
    user.festive_data.deal_sum = Utils.prepare_external_field(deal, BFA.DEAL_TOTAL_SUM_ALIAS)

    order_received_by_id = deal.get(BFA.DEAL_ORDER_RECEIVED_BY_ALIAS)
    user.festive_data.deal_accepted = Utils.prepare_external_field(BW.BITRIX_IDS_USERS, order_received_by_id,
                                                 BW.BITRIX_USERS_LOCK)

    source_id = Utils.prepare_external_field(deal, BFA.DEAL_SOURCE_ID_ALIAS)
    user.festive_data.deal_source = Utils.prepare_external_field(BW.SOURCES, source_id, BW.SOURCES_LOCK)

    contact_id = Utils.prepare_external_field(deal, BFA.DEAL_CONTACT_ALIAS)

    contact_data = BW.get_contact_data(contact_id)
    contact_name = contact_data.get(BFA.CONTACT_USER_NAME_ALIAS)
    contact_phone = contact_data.get(BFA.CONTACT_PHONE_ALIAS)
    user.festive_data.deal_contact = contact_name + ' ' + contact_phone

    subdivision_id = Utils.prepare_external_field(deal, BFA.DEAL_SUBDIVISION_ALIAS)
    user.festive_data.deal_subdivision = Utils.prepare_external_field(BW.SUBDIVISIONS, subdivision_id, BW.SUBDIVISIONS_LOCK)

    user.festive_data.deal_has_reserve = Utils.prepare_external_field(deal, BFA.DEAL_ORDER_HAS_RESERVE_ALIAS)
    user.festive_data.deal_reserve_desc = Utils.prepare_external_field(deal, BFA.DEAL_ORDER_RESERVE_DESC_ALIAS)

    user.festive_data.deal_delivery_type = Utils.prepare_deal_supply_method(deal, BFA.DEAL_SUPPLY_METHOD_ALIAS)

    district_id = Utils.prepare_external_field(deal, BFA.DEAL_DISTRICT_ALIAS)
    user.festive_data.deal_district = Utils.prepare_external_field(BW.DISTRICTS, district_id, BW.DISTRICTS_LOCK)

    address, location = Utils.prepare_deal_address(deal, BFA.DEAL_ADDRESS_ALIAS)
    user.festive_data.deal_address = address

    user.festive_data.deal_delivery_comment = Utils.prepare_external_field(deal, BFA.DEAL_DELIVERY_COMMENT_ALIAS)

    payment_type_id = Utils.prepare_external_field(deal, BFA.DEAL_PAYMENT_TYPE_ALIAS)
    user.festive_data.deal_pay_type = Utils.prepare_external_field(BW.PAYMENT_TYPES, payment_type_id, BW.PAYMENT_TYPES_LOCK)

    payment_method_id = Utils.prepare_external_field(deal, BFA.DEAL_PAYMENT_METHOD_ALIAS)
    user.festive_data.deal_pay_method = Utils.prepare_external_field(BW.PAYMENT_METHODS, payment_method_id,
                                                   BW.PAYMENT_METHODS_LOCK)

    user.festive_data.deal_prepaid = Utils.prepare_external_field(deal, BFA.DEAL_PREPAID_ALIAS)

    user.festive_data.deal_terminal = Utils.prepare_external_field(BW.DEAL_TERMINAL_CHANGE_MAPPING,
                                                 Utils.prepare_external_field(deal, BFA.DEAL_TERMINAL_CHANGE_ALIAS))
    user.festive_data.deal_change = Utils.prepare_external_field(deal, BFA.DEAL_CHANGE_SUM_ALIAS)

    user.festive_data.deal_to_pay = Utils.prepare_external_field(deal, BFA.DEAL_TO_PAY_ALIAS)

    user.festive_data.deal_pay_status = Utils.prepare_external_field(deal, BFA.DEAL_PAYMENT_STATUS_ALIAS)

    if user.festive_data.deal_has_reserve == BFM.DEAL_HAS_RESERVE_YES:
        with BW.BITRIX_USERS_LOCK:
            access_token = context.bot_data[cfg.BOT_ACCESS_TOKEN_PERSISTENT_KEY]
            user.festive_data.photo_urls = BW.process_deal_photo_dl_urls(deal, access_token,
                                                                         (BFA.DEAL_ORDER_RESERVE_ALIAS,))
    else:
        user.festive_data.photo_urls = None


def get_deal_photo_dl_urls(deal: dict, access_token, field_aliases=()):
    photos_list = []

    for fa in field_aliases:
        if fa in deal:
            data = deal[fa]
            if isinstance(data, list):
                for photo in data:
                    photos_list.append(BW.generate_photo_link(photo, access_token))
            else:
                photos_list.append(BW.generate_photo_link(data, access_token))

    return photos_list


def reapprove_deal(deal_id):
    update_obj = {
        BFA.FESTIVE_APPROVEMENT_ALIAS: BFM.FESTIVE_APPROVEMENT_NOT_SELECTED,
        BFA.FESTIVE_DECLINE_COMMENT_ALIAS: None,
        BFA.FESTIVE_DECLINE_USER_ALIAS: None
    }
    BW.update_deal(deal_id, update_obj)


# статистика "необработано" и "отклоненных подразделениям"
def stat_unprocessed():
    # TODO: move to batch queries to prevent overload
    sleep_interval = 1

    with BW.FESTIVE_DATES_LOCK:
        params = {
            'select': ['ID'],
            'filter': {
                    BFA.FESTIVE_APPROVEMENT_ALIAS: BFM.FESTIVE_APPROVEMENT_NOT_SELECTED,
                    BFA.DEAL_DATE_ALIAS: BW.FESTIVE_DATES
            }
        }

    unprocessed = BW.send_request('crm.deal.list', params, obtain_total=True)
    subdivs = {}

    with BW.SUBDIVISIONS_LOCK, BW.FESTIVE_DATES_LOCK:
        for s_id, s_name in BW.SUBDIVISIONS.items():
            params = {
                'select': ['ID'],
                'filter': {
                    BFA.FESTIVE_APPROVEMENT_ALIAS: BFM.FESTIVE_APPROVEMENT_NO,
                    BFA.DEAL_DATE_ALIAS: BW.FESTIVE_DATES,
                    BFA.DEAL_SUBDIVISION_ALIAS: s_id
                }
            }

            declined = BW.send_request('crm.deal.list', params, obtain_total=True)
            if declined:
                subdivs[s_name] = declined

            time.sleep(sleep_interval)
    return unprocessed, subdivs

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
    return creds.UNAPPROVED_SUBDIVISION.get(value)


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
        BFA.EQUIPPED_APPROVEMENT_ALIAS: BFM.EQUIPPED_APPROVEMENT_REAPPROVE,
        BFA.EQUIPPED_DECLINE_COMMENT_ALIAS: None,
    }
    BW.update_deal(deal_id, update_obj)


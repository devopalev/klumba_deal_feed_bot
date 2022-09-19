import telegram.utils.helpers as tg_helpers
import source.TextSnippets as Txt


# fully escape Markdownv2 string
def escape_mdv2(string):
    return tg_helpers.escape_markdown(text=string, version=2)


def _stringify_field(field):
    if not bool(field):
        return Txt.FIELD_IS_EMPTY_PLACEHOLDER
    else:
        return str(field)


def prepare_external_field(obj, key, escape_md=True):
    if not obj:
        return Txt.FIELD_IS_EMPTY_PLACEHOLDER

    val = obj.get(key)

    if type(val) is list:
        val = ', '.join(val)

    stringified = _stringify_field(val)
    return escape_mdv2(stringified) if escape_md else stringified

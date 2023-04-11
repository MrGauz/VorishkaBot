import json
import logging

from settings import DEFAULT_LANG

logger = logging.getLogger(__name__)


def translate(message_id: str, lang_code: str) -> str:
    trans = load_translation(lang_code)
    module, message_name = message_id.split(".")

    try:
        # TODO: fill the arguments
        return trans[module][message_name]
    except (KeyError, TypeError) as e:
        if lang_code != DEFAULT_LANG:
            # Try falling back to default language
            logger.warning(f'Could not find translation for {message_id} in {lang_code}', exc_info=e)
            return translate(message_id, DEFAULT_LANG)

        logger.error(f'Could not find translation for {message_id} in default {lang_code}', exc_info=e)
        # TODO: return something to display to the user
        return ""


def load_translation(lang_code: str) -> dict:
    try:
        filename = f"locales/{lang_code}.json".lower()
        with open(filename, 'r', encoding='utf-8') as f:
            # TODO: json schema validation
            return json.load(f)

    except Exception as e:
        if lang_code != DEFAULT_LANG:
            # Try falling back to default language
            logger.warning(f'Could not load translation {lang_code}', exc_info=e)
            return load_translation(DEFAULT_LANG)

        logger.error(f'Default translation {DEFAULT_LANG} could not be loaded', exc_info=e)
        raise ValueError(f'Default translation {DEFAULT_LANG} could not be loaded') from e

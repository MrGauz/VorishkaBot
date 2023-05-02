import json
import logging

from settings import DEFAULT_LANG

logger = logging.getLogger(__name__)


def translate(message_id: str, lang_code: str, placeholders=None) -> str:
    """
    Loads a specified translation and replaces the placeholders with the provided values.

    :param message_id: A string representing the message ID, in the format 'module.message_name'.
    :param lang_code: The language code (e.g., 'en', 'es') for the desired translation.
    :param placeholders: A dictionary containing the placeholders and their values.
                         Defaults to an empty dictionary if not provided.
    :return: The translated message as a string.
    """
    if placeholders is None:
        placeholders = {}

    trans = load_translation(lang_code)
    module, message_name = message_id.split('.')

    try:
        message_template = trans[module][message_name]
        for placeholder, value in placeholders.items():
            message_template = message_template.replace(f'{{{placeholder}}}', str(value))
        return message_template

    except (KeyError, TypeError) as e:
        if lang_code != DEFAULT_LANG:
            # Try falling back to default language
            logger.warning(f'Could not find translation for {message_id} in {lang_code}', exc_info=e)
            return translate(message_id, DEFAULT_LANG, placeholders)

        logger.error(f'Could not find translation for {message_id} in default {lang_code}', exc_info=e)
        return message_id


def load_translation(lang_code: str) -> dict:
    """
    Loads translations for the given language code from a JSON file.

    :param lang_code: The language code (e.g., 'en', 'es') for the desired translation.
    :return: A dictionary containing the translations.
    :raises ValueError: If the default translation file cannot be loaded.
    """
    try:
        filename = f'locales/translations/{lang_code}.json'.lower()
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    except Exception as e:
        if lang_code != DEFAULT_LANG:
            # Try falling back to default language
            logger.warning(f'Could not load translation {lang_code}', exc_info=e)
            return load_translation(DEFAULT_LANG)

        logger.error(f'Default translation {DEFAULT_LANG} could not be loaded', exc_info=e)
        raise ValueError(f'Default translation {DEFAULT_LANG} could not be loaded') from e

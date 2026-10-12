import gettext
import os
import locale

LOCALE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")
DEFAULT_LANGUAGE = "pl"

_current_translation = None

def init_i18n(lang_code: str = None):
    global _current_translation
    
    if lang_code == "polish":
        lang_code = "pl"
    elif lang_code == "english":
        lang_code = "en"

    if not lang_code:
        try:
            sys_lang, _ = locale.getdefaultlocale()
            if sys_lang and sys_lang.startswith("en"):
                lang_code = "en"
            else:
                lang_code = "pl"
        except Exception:
            lang_code = DEFAULT_LANGUAGE

    try:
        _current_translation = gettext.translation(
            domain="messages",
            localedir=LOCALE_DIR,
            languages=[lang_code]
        )
        _current_translation.install()
    except FileNotFoundError:
        _current_translation = gettext.NullTranslations()

def _(message: str) -> str:
    if _current_translation is not None:
        return _current_translation.gettext(message)
    return message
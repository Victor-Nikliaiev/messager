from googletrans import Translator


def translate_string(input_string, target_language="ru", original_language="en"):
    """
    Translates the input_string to the target_language from the original_language.

    :param input_string: String to be translated.
    :param target_language: Language code of the desired target language (default: "ru").
    :param original_language: Language code of the original language (default: "auto").
    :return: Translated string or None if translation fails.
    """
    try:
        translator = Translator()
        # Attempt to translate the string
        translated = translator.translate(
            input_string, src=original_language, dest=target_language
        )
        return translated.text
    except Exception as e:
        # Log the error and return None to indicate a failure
        print(f"Error translating '{input_string}': {e}")
        return None


# Example usage
# original_string = "Hello, world"
# translated_string = translate_string(
#     original_string, target_language="ru", original_language="en"
# )

# print(f"Original: {original_string}")
# print(f"Translated: {translated_string}")

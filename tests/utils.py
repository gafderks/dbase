from django.test import override_settings

english = override_settings(
    LANGUAGE_CODE="en-US",
    LANGUAGES=(("en", "English"),),
)

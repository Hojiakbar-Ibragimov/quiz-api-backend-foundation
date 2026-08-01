import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import UserProfiles
from apps.users.exceptions import (
    NoChangesDetected,
    UnsupportedLanguage
)
from apps.exceptions import ValidationError

from django.db.models import F
from django.db import transaction


def get_profile_by_user_id(user_id):
    user_profile = UserProfiles.objects.filter(
        user_id=user_id
    ).values(
        'user_id',
        'bio',
        real_name=F('user__real_name'),
        username=F('user__username'),
        role=F('user__role'),
        active=F('user__active')
    ).first()

    return user_profile


def get_user_settings(user_id):
    user_lang = get_user_language(user_id)
    user_theme = get_user_theme(user_id)

    return {
        'user_id': user_id,
        'language': user_lang,
        'theme': user_theme
    }

def get_user_language(user_id):
    lang = UserProfiles.objects.filter(
        user_id=user_id
    ).values_list(
        'language',
        flat=True
    ).first()

    return lang


def get_user_theme(user_id):
    user_theme = UserProfiles.objects.filter(
        user_id=user_id
    ).values_list(
        'theme',
        flat=True
    ).first()

    return user_theme


def get_user_bio(user_id):
    user_bio = UserProfiles.objects.filter(
        user_id=user_id
    ).values_list(
        'bio',
        flat=True
    ).first()

    return user_bio


def update_user_language(user_id, lang):
    user_lang = get_user_language(user_id)

    lang = str(lang)

    if (not (lang == 'en'
            or lang == 'uz'
            or lang == 'ru')
            or lang.isdigit()):
        if lang.isalpha() and len(lang) == 2:
            raise UnsupportedLanguage('Not supported language')
        else:
            raise ValidationError(f'Invalid language description: {lang}')

    if user_lang == lang:
        raise NoChangesDetected(
            f'Language is already set to this value'
        )

    UserProfiles.objects.filter(
        user_id=user_id
    ).update(
        language=lang
    )

    return {
            'message': 'Language updated'
        }


def update_user_theme(user_id, theme):
    user_theme = get_user_theme(user_id)


    if (not (theme == 'default'
            or theme == 'light'
            or theme == 'dark')
            or theme.isdigit()):
        raise ValidationError(
            f'Invalid theme description: {theme}'
        )

    if user_theme == theme:
        raise NoChangesDetected(
            f'Theme is already set to this value'
        )

    UserProfiles.objects.filter(
        user_id=user_id
    ).update(
        theme=theme
    )

    return {
        'message': 'Theme updated'
    }


def update_user_bio(user_id, bio):
    user_bio = get_user_bio(user_id)

    if bio == '':
        raise ValidationError('Empty bio')

    if user_bio == bio:
        raise NoChangesDetected(
            f'Bio is already set to this value'
        )

    UserProfiles.objects.filter(
        user_id=user_id
    ).update(
        bio=bio
    )

    return {
        'message': 'Bio updated'
    }


def update_profile_and_setting_data(data, user_id):
    updated_fields = []

    with transaction.atomic():
        if 'language' in data:
            lang = data.get('language')
            message = update_user_language(
                user_id=user_id,
                lang=lang
            )

            updated_fields.append(message.get('message'))

        if 'bio' in data:
            bio = data.get('bio')
            message = update_user_bio(
                user_id=user_id,
                bio=bio
            )

            updated_fields.append(message.get('message'))

        if 'theme' in data:
            theme = data.get('theme')
            message = update_user_theme(
                user_id=user_id,
                theme=theme
            )

            updated_fields.append(message.get('message'))

    return updated_fields
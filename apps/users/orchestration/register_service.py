import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import (
    Users,
    UserStatistics,
    UserProfiles
)
from apps.users.exceptions import (
    UsernameAlreadyTaken
)
from apps.exceptions import ValidationError

from django.db import transaction
from apps.users.service.user_service import (
    get_user_by_username,
    check_username_unique
)


def register_user(name, username, role='user'):
    try:
        check_username_unique(username)
    except UsernameAlreadyTaken as error:
        raise UsernameAlreadyTaken(
            str(error)
        )

    if not (role == 'user'
            or role == 'admin'):
        raise ValidationError(f'Invalid role description: {role}.')

    if username == '':
        raise ValidationError('Empty username.')

    if name == '':
        raise ValidationError('Empty real name')

    with transaction.atomic():

        Users.objects.create(
            real_name=name,
            username=username,
            role=role
        ).save()

        user_id = get_user_by_username(
            username=username
        ).get('id')

        UserProfiles.objects.create(
            user_id=user_id,
            theme='default',
            language='en'
        ).save()

        UserStatistics.objects.create(
            user_id=user_id
        ).save()

    return {
        'message': f'User registered (ID: {user_id})'
    }
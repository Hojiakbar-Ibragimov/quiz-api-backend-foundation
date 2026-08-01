import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db.models import Count
from apps.users.models import Users
from apps.users.exceptions import (
    NoChangesDetected,
    UserNotFound,
    UsernameAlreadyTaken
)
from django.db import transaction
from apps.exceptions import ValidationError


def calculate_users_count():
    users = Users.objects.values(
        'active'
    ).annotate(
        count=Count('active')
    )

    active_users_count = 0
    passive_users_count = 0

    for user in users:
        if not user['active']:
            passive_users_count += user['count']
        else:
            active_users_count += user['count']

    overall_users_count = active_users_count + passive_users_count

    return {
        'actives': active_users_count,
        'inactives': passive_users_count,
        'overall': overall_users_count
    }


def get_user_by_id(user_id):
    user = Users.objects.filter(
        id=user_id
    ).values(
        'id',
        'real_name',
        'username',
        'joined_date',
        'active'
    ).first()

    if not user:
        raise UserNotFound('User not found')

    return user


def get_user_by_username(username):
    user = Users.objects.filter(
        username=username
    ).values(
        'id',
        'real_name',
        'username'
    ).first()

    return user


def get_all_users():
    users = list(
        Users.objects.values(
        'id',
        'username',
        'active'
        )
    )

    return users


def get_user_status_by_id(user_id):
    user_active = Users.objects.filter(
        id=user_id
    ).values_list(
        'active',
        flat=True
    ).first()

    return user_active


def get_username_by_id(user_id):
    username = Users.objects.filter(
        id=user_id
    ).values_list(
        'username',
        flat=True
    ).first()

    return username


def get_user_role(user_id):
    user_role = Users.objects.filter(
        id=user_id
    ).values_list(
        'role',
        flat=True
    ).first()

    return user_role


def get_user_real_name(user_id):
    real_name = Users.objects.filter(
        id=user_id
    ).values_list(
        'real_name',
        flat=True
    ).first()

    return real_name


def get_all_users_status():
    users_status = Users.objects.all().values(
        'id',
        'active'
    )

    return users_status


def update_user_status(user_id, status):
    is_user_active = get_user_status_by_id(user_id)

    if status is True:
        if is_user_active:
            raise NoChangesDetected(
                'User already active'
            )
        else:
            Users.objects.filter(
                id=user_id
            ).update(
                active=status
            )
            message = 'User reactivated'

    elif status is False:
        if not is_user_active:
            raise NoChangesDetected(
                'User already inactive'
            )
        else:
            Users.objects.filter(
                id=user_id
            ).update(
                active=status
            )
            message = 'User deactivated'
    else:
        raise ValidationError(
            f'{status} value must be either True or False'
        )

    return {
        'message': message,
    }


def update_username(user_id, username):
    old_username = get_username_by_id(user_id)

    if username == '':
        raise ValidationError('Empty username')

    if old_username == username:
        raise NoChangesDetected(f'Username is already set to this value')

    try:
        check_username_unique(
            username=username
        )
    except UsernameAlreadyTaken as e:
        raise UsernameAlreadyTaken(str(e))

    Users.objects.filter(
        id=user_id
    ).update(
        username=username
    )

    return {
        'message': 'Username was updated'
    }


def update_real_name(user_id, name):
    old_name = get_user_real_name(user_id)

    if name == '':
        raise ValidationError('Empty real name')

    if old_name == name:
        raise NoChangesDetected(f'Real name is already set to this value')

    Users.objects.filter(
        id=user_id
    ).update(
        real_name=name
    )

    return {
        'message': 'Real name updated'
    }


def delete_user(user_id):
    user_exists = get_user_by_id(user_id)

    if not user_exists:
        raise UserNotFound(
            'User not found'
        )

    Users.objects.filter(
        id=user_id
    ).delete()

    return {
        'message': 'User deleted'
    }


def check_username_unique(username):
    username_already_taken = Users.objects.filter(
        username=username
    ).values_list(
        'username',
        flat=True
    ).first()

    if username_already_taken:
        raise UsernameAlreadyTaken(
            'Username already taken'
        )

def update_user_data(data, user_id):
    updated_fields = []

    with transaction.atomic():
        if 'status' in data:
            status = data.get('status')
            message = update_user_status(
                user_id=user_id,
                status=status
            )

            updated_fields.append(message.get('message'))

        if 'username' in data:
            username = data.get('username')
            message = update_username(
                user_id=user_id,
                username=username
            )

            updated_fields.append(message.get('message'))

        if 'real_name' in data:
            name = data.get('real_name')
            message = update_real_name(
                user_id=user_id,
                name=name
            )

            updated_fields.append(message.get('message'))

    return updated_fields
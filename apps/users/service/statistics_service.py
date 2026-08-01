import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import UserStatistics
from apps.users.exceptions import UserNotFound
from django.db.models import F
from django.db import transaction


def get_user_played_count(user_id):
    played_count = UserStatistics.objects.filter(
        user_id=user_id
    ).values_list(
        'played_count',
        flat=True
    ).first()

    return played_count


def get_user_overall_points(user_id):
    overall_points = UserStatistics.objects.filter(
        user_id=user_id
    ).values_list(
        'overall_points',
        flat=True
    ).first()

    return overall_points


def get_user_record_points(user_id):
    record_points = UserStatistics.objects.filter(
        user_id=user_id
    ).values_list(
        'record_points',
        flat=True
    ).first()

    return record_points


def get_user_won_count(user_id):
    won_count = UserStatistics.objects.filter(
        user_id=user_id
    ).values_list(
        'won_count',
        flat=True
    ).first()

    return won_count


def get_user_all_statistics(user_id):
    overall_statistics = UserStatistics.objects.filter(
        user_id=user_id
    ).values(
        'user_id',
        'played_count',
        'overall_points',
        'record_points',
        'won_count'
    ).first()

    return overall_statistics


def update_user_played_count(user_id):
    user = get_user_played_count(user_id)

    if not user:
        raise UserNotFound(
            f'User not found'
        )

    UserStatistics.objects.filter(
        user_id=user_id
    ).update(
        played_count=F('played_count')+1
    )

    return {
        'message': 'Played count updated'
    }


def update_user_overall_points(user_id, points):
    user = get_user_overall_points(user_id)

    if not user:
        raise UserNotFound(
            'User not found'
        )

    UserStatistics.objects.filter(
        user_id=user_id
    ).update(
        overall_points=F('overall_points')+points
    )

    return {
        'message': 'Overall points updated'
    }


def update_user_record_points(user_id, record):
    user = get_user_record_points(user_id)

    if not user:
        raise UserNotFound(
            'User not found'
        )

    UserStatistics.objects.filter(
        user_id=user_id
    ).update(
        record_points=record
    )

    return {
        'message': 'Record points updated'
    }


def update_user_won_count(user_id):
    user = get_user_won_count(user_id)

    if not user:
        raise UserNotFound(
            'User not found'
        )

    UserStatistics.objects.filter(
        user_id=user_id
    ).update(
        won_count=F('won_count')+1
    )

    return {
        'Won count updated'
    }


def update_user_all_statistics(user_id, this_game_points, correct_answers_count):
    record_points = get_user_record_points(user_id)

    with transaction.atomic():
        UserStatistics.objects.filter(
            user_id=user_id
        ).update(
            played_count=F('played_count')+1
        )

        if correct_answers_count != 0:
            UserStatistics.objects.filter(
                user_id=user_id
            ).update(
                overall_points=F('overall_points')+this_game_points
            )

            if record_points < this_game_points:
                UserStatistics.objects.filter(
                    user_id=user_id
                ).update(
                    record_points=this_game_points
                )

            if correct_answers_count >= 10:
                UserStatistics.objects.filter(
                    user_id=user_id
                ).update(
                    won_count=F('won_count')+1
                )
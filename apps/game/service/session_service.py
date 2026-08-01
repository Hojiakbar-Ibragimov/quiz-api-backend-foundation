import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.game.models import GameSessions
from apps.game.exceptions import (
    SessionNotFound,
    SessionNotActive,
    NoHelpAvailable
)
from apps.exceptions import ValidationError
from django.db.models import F
from datetime import datetime


def get_session_help_change_quest_count(session_id):
    help_count = GameSessions.objects.filter(
        id=session_id
    ).values_list(
        'help_change_quest',
        flat=True
    ).first()

    return help_count


def get_session_help_50_50_count(session_id):
    help_count = GameSessions.objects.filter(
        id=session_id
    ).values_list(
        'help_50_50',
        flat=True
    ).first()

    return help_count


def get_session_correct_answers_count(session_id):
    correct_answers_count = GameSessions.objects.filter(
        id=session_id
    ).values_list(
        'correct_answers_count',
        flat=True
    ).first()


    return correct_answers_count


def get_session_by_id(session_id):
    session = GameSessions.objects.filter(
        id=session_id
    ).values(
        'id',
        'user_id',
        'correct_answers_count',
        'points',
        'started_at',
        'finished_at',
        'spent_time',
        'status'
    ).first()

    if not session:
        raise SessionNotFound('Session not found')

    return session


def get_sessions_by_user_id(user_id):
    sessions = list(
        GameSessions.objects.filter(
            user_id=user_id
        ).values(
            'id',
            'user_id',
            'correct_answers_count',
            'status'
        )
    )

    return sessions


def get_sessions_by_status(status):
    active_sessions = GameSessions.objects.filter(
        status=status
    ).values(
        'id',
        'user_id',
        'status'
    )

    return active_sessions


def get_session_status(session_id):
    session_status = GameSessions.objects.filter(
        id=session_id
    ).values_list(
        'status',
        flat=True
    ).first()

    return session_status


def get_session_language(session_id):
    session_lang =GameSessions.objects.filter(
        id=session_id
    ).values_list(
        'game_lang',
        flat=True
    ).first()

    return session_lang


def get_user_id_by_session(session_id):
    user = GameSessions.objects.filter(
        id=session_id
    ).values_list(
        'user_id',
        flat=True
    ).first()

    return user


def get_time():
    now = datetime.now()

    return datetime.astimezone(now)


def update_session_help_change_quest_count(session_id):
    session_exists = get_session_by_id(session_id)
    help_count = get_session_help_change_quest_count(session_id)

    if not session_exists:
        raise SessionNotFound(
            'Session not found'
        )

    elif session_exists['status'] != 'active':
        raise SessionNotActive(
            'Inactive session'
        )

    elif help_count == 0:
        raise NoHelpAvailable(
            f'Help (for change quest) fully used'
        )

    GameSessions.objects.filter(
        id=session_id
    ).update(
        help_change_quest=F('help_change_quest')-1
    )

    return {
        'message': 'Help (for change quest) count updated'
    }


def update_session_help_50_50_count(session_id):
    session_exists = get_session_by_id(session_id)
    help_count = get_session_help_50_50_count(session_id)

    if not session_exists:
        raise SessionNotFound(
            'Session not found'
        )

    elif session_exists['status'] != 'active':
        raise SessionNotActive(
            'Inactive session'
        )

    elif help_count == 0:
        raise NoHelpAvailable(
            f'Help (50-50) fully used'
        )

    GameSessions.objects.filter(
        id=session_id
    ).update(
        help_50_50=F('help_50_50')-1
    )

    return {
        'message': 'Help (50-50) count updated'
    }


def update_session_points(session_id, points):
    session_exists = get_session_by_id(session_id)

    if not session_exists:
        raise SessionNotFound(
            'Session not found'
        )

    elif session_exists['status'] != 'active':
        raise SessionNotActive(
            'Inactive session'
        )

    GameSessions.objects.filter(
        id=session_id
    ).update(
        correct_answers_count=F('correct_answers_count')+1,
        points=F('points')+points
    )

    return {
        'message': 'Points updated'
    }


def delete_session(session_id):
    session_exists = get_session_by_id(session_id)

    if not session_exists:
        raise SessionNotFound(
            'Session not found'
        )

    GameSessions.objects.filter(
        id=session_id
    ).delete()

    return {
        'message': 'Session deleted',
    }


def calculate_spent_time(started_time):
    now = datetime.now()
    finished_time = datetime.astimezone(now)

    spent_time = finished_time - started_time

    minutes, seconds = divmod(spent_time.seconds, 60)

    return {
        'minutes': minutes,
        'seconds': seconds,
        'overall_seconds': spent_time.seconds
    }


def calculate_points_by_question_difficulty(difficulty):
    if difficulty == 'easy':
        points = 10
    elif difficulty == 'medium':
        points = 20
    elif difficulty == 'hard':
        points = 30
    else:
        raise ValidationError(
            f'Invalid difficulty description: {difficulty}'
        )

    return points

def calculate_difficulty_by_question_count(count_level):
    if 3 >= count_level >= 0:
        difficulty = 'easy'
    elif 7 >= count_level > 3:
        difficulty = 'medium'
    elif 10 >= count_level > 7:
        difficulty = 'hard'
    else:
        raise ValidationError(
            f'Invalid level-count: {count_level}'
        )

    return difficulty
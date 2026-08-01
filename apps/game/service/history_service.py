import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.game.models import AnswersHistory, GameSessions
from apps.game.exceptions import SessionNotFound
from django.db.models import F


def get_answers_history_by_session_id(session_id):
    game_lang = GameSessions.objects.filter(
        id=session_id
    ).values_list(
        'game_lang',
        flat=True
    ).first()

    if not game_lang:
        raise SessionNotFound(
            'Session not found'
        )

    if game_lang == 'uz':
        history = AnswersHistory.objects.filter(
            session_id=session_id,
            question__translation__language=game_lang,
            selected_variant__translation__language=game_lang
        ).values(
            'session_id',
            'question_id',
            question_title=F('question__translation__translated_title'),
            variant_id=F('selected_variant_id'),
            variant_title=F('selected_variant__translation__translated_title'),
            correct=F('is_correct')
        )


    else:
        history = AnswersHistory.objects.filter(
            session_id=session_id
        ).values(
            'session_id',
            'question_id',
            question_title=F('question__question_title'),
            variant_id=F('selected_variant_id'),
            variant_title=F('selected_variant__answer_title'),
            correct=F('is_correct')
        )

    return list(history)


def get_sessions_history_by_user_id(user_id):
    sessions = GameSessions.objects.filter(
        user_id=user_id
    ).values(
        'id',
        'status',
        'user_id',
        username=F('user__username'),
        correct_answers=F('correct_answers_count')
    )

    return list(sessions)
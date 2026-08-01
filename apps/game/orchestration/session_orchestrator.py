import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import UserStatistics
from apps.game.models import (
    GameSessions,
    AnswersHistory
)
from apps.game.service import session_service
from apps.users.service import (
    statistics_service,
    profile_service
)
from apps.questions.service import question_service
from apps.game.exceptions import (
    SessionNotFound,
    SessionNotActive,
    ActiveSessionExists
)
from apps.validators import validate_id
from django.db import transaction
from django.db.models import F


def create_session(user_id):
    user_lang = profile_service.get_user_language(user_id)

    active_sessions_exist = GameSessions.objects.filter(
        user_id=user_id,
        status='active'
    ).values_list(
        'id',
        flat=True
    ).first()

    if active_sessions_exist:
        raise ActiveSessionExists(
            f'User already has an active session ({active_sessions_exist})'
        )

    GameSessions.objects.create(
        user_id=user_id,
        game_lang=user_lang
    )

    session_id = GameSessions.objects.filter(
        user_id=user_id,
        status='active'
    ).values_list(
        'id',
        flat=True
    ).first()

    return {
            'message': f'Session created ({session_id})',
        }


def finish_session(session_id):
    session_exists = session_service.get_session_by_id(session_id)

    if not session_exists:
        raise SessionNotFound(
            f'Session not found'
        )

    elif session_exists['status'] != 'active':
        raise SessionNotActive(
            f'Inactive Session'
        )

    user_id = session_exists.get('user_id')
    user_record_points = (statistics_service.
    get_user_record_points(
        user_id=user_id
    ))
    correct_answers_count = session_exists.get('correct_answers_count')
    this_game_points = session_exists.get('points')

    finished_at = session_service.get_time()
    spent_time = session_service.calculate_spent_time(
        session_exists.get('started_at')
    )

    with transaction.atomic():
        GameSessions.objects.filter(
            id=session_id
        ).update(
            finished_at=finished_at,
            spent_time=spent_time.get('overall_seconds'),
            status='finished',
        )

        UserStatistics.objects.filter(
            user_id=user_id
        ).update(
            played_count=F('played_count')+1
        )

        if correct_answers_count != 0:
            UserStatistics.objects.filter(
                user_id=user_id
            ).update(
                overall_points=F('overall_points') + this_game_points
            )

            if user_record_points < this_game_points:
                UserStatistics.objects.filter(
                    user_id=user_id
                ).update(
                    record_points=this_game_points
                )

            if correct_answers_count == 10:
                UserStatistics.objects.filter(
                    user_id=user_id
                ).update(
                    won_count=F('won_count')+1
                )
    return {
        'message': 'Session finished'
    }


def check_answer_service(answer_id):
    validate_id(
        ids=answer_id,
        error_title=f'Invalid answer_id: {answer_id}'
    )

    answer_correctness = (question_service.
    get_answer_correctness(
        answer_id=answer_id
    ))

    if not answer_correctness.get('is_correct'):
        result = {
            'question_id': answer_correctness.get('question_id'),
            'answer_id': answer_correctness.get('id'),
            'is_correct': False
        }

    else:
        result = {
            'question_id': answer_correctness.get('question_id'),
            'answer_id': answer_correctness.get('id'),
            'is_correct': True
        }

    return result


def save_answer_to_history(session_id, question_id, answer_id, is_correct):
    AnswersHistory.objects.create(
        session_id=session_id,
        question_id=question_id,
        selected_variant_id=answer_id,
        is_correct=is_correct
    )


def submit_answer_flow(session_id, answer_id):
    session = (session_service.
    get_session_by_id(
        session_id=session_id
    ))

    if session.get('status') != 'active':
        raise SessionNotActive(
            'Inactive Session'
        )

    message = check_answer_service(
        answer_id=answer_id
    )

    question_id = message.get('question_id')
    is_answer_correct = message.get('is_correct')

    save_answer_to_history(
        session_id=session_id,
        question_id=question_id,
        answer_id=answer_id,
        is_correct=is_answer_correct
    )

    correct_answers_count = (session_service.
    get_session_correct_answers_count(
        session_id=session_id
    ))

    if not is_answer_correct:
        finish_session(session_id)

        return {
            'message': f'Wrong Answer. '
                       f'You have failed in {correct_answers_count+1}-level'
        }

    else:
        correct_answers_count += 1

        difficulty = (session_service.
        calculate_difficulty_by_question_count(
            count_level=correct_answers_count
        ))

        points = (session_service.
        calculate_points_by_question_difficulty(
            difficulty=difficulty
        ))

        session_service.update_session_points(
            session_id=session_id,
            points=points
        )

        if correct_answers_count == 10:
            finish_session(
                session_id=session_id
            )

            return {
                'message': 'You have won!!!'
            }

    return {
        'message': f'Correct Answer. '
                   f'{correct_answers_count+1}-level Continue'
    }
from json import JSONDecodeError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from .exceptions import (
    ActiveSessionExists,
    SessionNotActive
)
from .service import session_service, history_service
from apps.questions.service import question_service
from .orchestration import session_orchestrator
from ..exceptions import (
    ValidationError,
    NotFoundError
)


@csrf_exempt
def sessions_view(request):
    user_id = 1

    if request.method == 'GET':
        sessions = session_service.get_sessions_by_user_id(
            user_id=user_id
        )

        return JsonResponse(sessions, safe=False)

    if request.method == 'POST':
        try:
            message = session_orchestrator.create_session(
                user_id=user_id
            )

            return JsonResponse(message)
        except ActiveSessionExists as e:
            return JsonResponse(
                {
                    'message': str(e)
                },
                status=400
            )

    return JsonResponse(
        {
            'message': 'Method not allowed'
        },
        status=405
    )


@csrf_exempt
def session_by_id_view(request, session_id):
    if request.method == 'GET':
        try:
            session = session_service.get_session_by_id(
                session_id=session_id
            )

            return JsonResponse(session)
        except NotFoundError as e:
            return JsonResponse(
                {
                    'message': str(e)
                },
                status=404
            )

    return JsonResponse(
        {
            'message': 'Method not allowed'
        },
        status=405
    )


@csrf_exempt
def session_quest_view(request, session_id, question_id=None):

    if request.method == 'GET':
        try:
            session = session_service.get_session_by_id(
                session_id=session_id
            )

            if session.get('status') != 'active':
                raise SessionNotActive(
                    'Inactive session'
                )

            session_lang = session_service.get_session_language(
                session_id=session_id
            )

            difficulty = request.GET.get('difficulty')

            quest = question_service.build_question_response(
                difficulty=difficulty,
                question_id=question_id,
                lang=session_lang
            )

            return JsonResponse(quest)
        except JSONDecodeError:
            return JsonResponse(
                {
                    'message': 'Invalid JSON'
                },
                status=400
            )
        except NotFoundError as e:
            return JsonResponse(
                {
                    'message': str(e)
                },
                status=404
            )
        except ValidationError as e:
            return JsonResponse(
                {
                    'message': str(e)
                },
                status=400
            )
        except SessionNotActive as e:
            return JsonResponse(
                {
                    'message': str(e)
                },
                status=400
            )

    return JsonResponse(
        {
            'message': 'Method not allowed'
        },
        status=405
    )


@csrf_exempt
def submit_answer_view(request, session_id):
    if request.method == 'POST':
        allowed_fields = {
            'answer_id'
        }
        try:
            data = json.loads(request.body)

            if not data:
                return JsonResponse(
                    {
                        'message': 'No fields provided'
                    },
                    status=400
                )

            invalid_fields = set(data.keys()) - allowed_fields

            if invalid_fields:
                return JsonResponse(
                    {
                        'message': f'Invalid fields: {", ".join(data.keys())}. '
                                   f'allowed field: {", ".join(allowed_fields)}'
                    },
                    status=400
                )


            answer_id = data.get('answer_id')

            message = session_orchestrator.submit_answer_flow(
                session_id=session_id,
                answer_id=answer_id
            )

            return JsonResponse(message)


        except JSONDecodeError:
            return JsonResponse(
                {
                    'message': 'Invalid JSON'
                },
                status=400
            )
        except NotFoundError as e:
            return JsonResponse(
                {
                    'message': str(e)
                },
                status=404
            )
        except SessionNotActive as e:
            return JsonResponse(
                {
                    'message': str(e)
                },
                status=400
            )
        except ValidationError as e:
            return JsonResponse(
                {
                    'message': str(e)
                },
                status=400
            )

    return JsonResponse(
        {
            'message': 'Method not allowed'
        },
        status=405
    )

def history_view(request, session_id=None):
    user_id = 1

    if request.method == 'GET':
        try:
            if session_id is not None:
                answers_history = (history_service.
                get_answers_history_by_session_id(
                    session_id=session_id
                ))

                return JsonResponse(
                    {
                        'answers_history': answers_history
                    }
                )
            else:
                sessions_history = (history_service.
                get_sessions_history_by_user_id(
                    user_id=user_id
                ))

                return JsonResponse(
                    {
                        'sessions_history': sessions_history
                    }
                )
        except NotFoundError as e:
            return JsonResponse(
                {
                    'message': str(e)
                },
                status=400
            )

    return JsonResponse(
        {
            'message': 'Method not allowed'
        },
        status=405
    )
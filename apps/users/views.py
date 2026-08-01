import json
from json import JSONDecodeError

from django.http import JsonResponse

from .exceptions import (
    UsernameAlreadyTaken,
    NoChangesDetected,
    UnsupportedLanguage
)
from django.views.decorators.csrf import csrf_exempt
from apps.exceptions import ValidationError
from .orchestration.register_service import register_user
from .service import (
    user_service,
    profile_service,
    statistics_service
)
from ..exceptions import NotFoundError


@csrf_exempt
def users_view(request):
    if request.method == 'GET':
        users = user_service.get_all_users()

        return JsonResponse(users, safe=False)
    if request.method == 'POST':
        requirement_fields = {
            'real_name',
            'username'
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

            invalid_fields = set(data.keys()) - requirement_fields

            if invalid_fields:
                return JsonResponse(
                    {
                        'message': f'Invalid fields: {", ".join(invalid_fields)}. '
                                   f'allowed fields: {", ".join(requirement_fields)}'
                    },
                    status=400
                )

            if not ('real_name' in data
                    and 'username' in data):
                return JsonResponse(
                    {
                        'message': f'Not enough fields. '
                                   f'requirement fields: {", ".join(requirement_fields)}'
                    },
                    status=400
                )

            real_name = data.get('real_name')
            username = data.get('username')

            message = register_user(
                name=real_name,
                username=username
            ).get('message')

            return JsonResponse(
                {
                    'message': message
                },
                status=201
            )

        except JSONDecodeError:
            return JsonResponse(
                {
                    'message': 'Invalid JSON'
                },
                status=400
            )
        except UsernameAlreadyTaken as e:
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


@csrf_exempt
def user_by_id_view(request, user_id):
    """"
    This view supports only GET and
    PATCH of methods.
    """
    if request.method == 'GET':
        try:
            user = user_service.get_user_by_id(
                user_id=user_id
            )

            return JsonResponse(user)
        except NotFoundError as e:
            return JsonResponse(
                {
                    'message': str(e)
                },
                status=404
            )
    if request.method == 'PATCH':
        allowed_fields = {
            'status',
            'username',
            'real_name'
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
                        'message': f'Invalid fields: {", ".join(invalid_fields)}. '
                                   f'allowed fields: {", ".join(allowed_fields)}'
                    },
                    status=400
                )

            updated_fields = user_service.update_user_data(
                data=data,
                user_id=user_id
            )

            return JsonResponse(
                {
                    'message': updated_fields
                }
            )

        except JSONDecodeError:
            return JsonResponse(
                {
                    'message': 'Invalid JSON'
                },
                status=400
            )
        except NoChangesDetected as e:
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
        except UsernameAlreadyTaken as e:
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
def user_profile_view(request, user_id):
    if request.method == 'GET':
        try:
            user_profile = (
                profile_service.get_profile_by_user_id(
                    user_id=user_id
                )
            )

            return JsonResponse(user_profile)
        except NotFoundError as e:
            return JsonResponse(
                {
                    'message': str(e)
                },
                status=404
            )

    if request.method == 'PATCH':
        allowed_fields = {
            'language',
            'bio',
            'theme'
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
                        'message': f'Invalid fields: {", ".join(invalid_fields)}. '
                                   f'allowed fields: {", ".join(allowed_fields)}'
                    },
                    status=400
                )

            updated_fields = profile_service.update_profile_and_setting_data(
                data=data,
                user_id=user_id
            )

            return JsonResponse(
                {
                    'message': updated_fields
                }
            )
        except JSONDecodeError:
            return JsonResponse(
                {
                    'message': 'Invalid JSON'
                },
                status=400
            )
        except NoChangesDetected as e:
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
        except UnsupportedLanguage as e:
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
def user_statistics_view(request, user_id):
    if request.method == 'GET':
        try:
            user_statistics = (
                statistics_service.get_user_all_statistics(
                    user_id=user_id
                )
            )

            return JsonResponse(user_statistics)
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
def user_settings_view(request, user_id):
    if request.method == 'GET':
        try:
            user_settings = (
                profile_service.get_user_settings(
                    user_id=user_id
                )
            )

            return JsonResponse(user_settings)
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
def users_count_view(request):
    if request.method == 'GET':
        users_count = user_service.calculate_users_count()

        return JsonResponse(users_count)

    return JsonResponse(
        {
            'message': 'Method not allowed'
        },
        status=405
    )
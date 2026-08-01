from django.urls import path
from .views import (
    users_view,
    user_by_id_view,
    user_statistics_view,
    user_profile_view,
    user_settings_view,
    users_count_view
)

urlpatterns = [
    path(route='', view=users_view),
    path(route='<int:user_id>', view=user_by_id_view),
    path(route='<int:user_id>/statistics', view=user_statistics_view),
    path(route='<int:user_id>/profile', view=user_profile_view),
    path(route='<int:user_id>/settings', view=user_settings_view),
    path(route='count', view=users_count_view)
]
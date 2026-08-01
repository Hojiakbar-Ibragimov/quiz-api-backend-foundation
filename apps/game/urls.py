from django.urls import path
from .views import (
    sessions_view,
    session_by_id_view,
    session_quest_view,
    submit_answer_view,
    history_view
)

urlpatterns = [
    path(route='', view=sessions_view),
    path(route='<int:session_id>', view=session_by_id_view),
    path(route='<int:session_id>/history', view=history_view),
    path(route='history', view=history_view),
    path(route='<int:session_id>/submit', view=submit_answer_view),
    path(route='<int:session_id>/questions/random', view=session_quest_view),
    path(route='<int:session_id>/questions/<int:question_id>', view=session_quest_view)
]
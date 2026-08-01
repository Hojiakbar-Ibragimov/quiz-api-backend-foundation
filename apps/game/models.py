from django.db import models

from apps.questions.models import AnswerVariants, Questions
from apps.users.models import Users


class GameSessions(models.Model):
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='session')

    correct_answers_count = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    spent_time = models.FloatField(blank=True, null=True)
    help_change_quest = models.IntegerField(default=2)
    help_50_50 = models.IntegerField(default=1)
    status = models.CharField(max_length=10, default='active')
    points = models.IntegerField(default=0)
    game_lang = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'game_sessions'

class AnswersHistory(models.Model):
    session = models.ForeignKey(
        GameSessions,
        models.CASCADE,
        blank=True,
        null=True,
        related_name='answers'
    )

    question = models.ForeignKey(
        Questions,
        on_delete=models.SET_NULL,
        blank=True,
        null=True)

    selected_variant = models.ForeignKey(
        AnswerVariants,
        on_delete=models.SET_NULL,
        blank=True,
        null=True)

    answered_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'answers_history'
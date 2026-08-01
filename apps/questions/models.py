from django.db import models

class Questions(models.Model):
    question_title = models.TextField()
    category = models.TextField(blank=True, null=True)
    difficulty = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'questions'


class AnswerVariants(models.Model):
    question = models.ForeignKey(
        Questions,
        on_delete=models.CASCADE,
        blank=True,
        null=True)

    answer_title = models.TextField()
    is_correct = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'answer_variants'


class TranslatedQuestions(models.Model):
    pk = models.CompositePrimaryKey('question_id', 'language')
    question = models.ForeignKey(
        Questions,
        on_delete=models.CASCADE,
        blank=True,
        related_name='translation'
    )

    language = models.CharField(max_length=10, blank=True)
    translated_title = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'translated_questions'


class TranslatedAnswers(models.Model):
    pk = models.CompositePrimaryKey('answer_id', 'language')
    answer = models.ForeignKey(
        AnswerVariants,
        on_delete=models.CASCADE,
        blank=True,
        related_name='translation'
    )

    language = models.CharField(max_length=10, blank=True)
    translated_title = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'translated_answers'
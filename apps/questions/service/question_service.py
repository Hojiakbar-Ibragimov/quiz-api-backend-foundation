import os, django

from apps.exceptions import ValidationError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.questions.models import (
    Questions,
    AnswerVariants
)
from apps.questions.exceptions import QuestionNotFound
from apps.questions.validators import (
    validate_question_difficulty
)
from apps.validators import validate_id
from django.db.models import F

def build_question_response(difficulty=None, question_id=None, lang='en'):
    question = select_question_strategy(
        question_id=question_id,
        difficulty=difficulty
    )

    answers = get_answers_by_question_id(
        question_id=question.get('id')
    )

    payload = build_question_payload(
        question=question,
        answers=answers,
        lang=lang
    )

    return payload


def get_random_question_data(difficulty=None):
    if difficulty is None:
        question = Questions.objects.values(
            'id',
            'difficulty',
            original_title=F('question_title'),
            translated_title=F('translation__translated_title')
        ).order_by(
            '?'
        ).first()
    else:
        question = Questions.objects.filter(
            difficulty=difficulty
        ).values(
            'id',
            'difficulty',
            original_title=F('question_title'),
            translated_title=F('translation__translated_title')
        ).order_by(
            '?'
        ).first()

    return question


def get_question_by_id(question_id):
    question = Questions.objects.filter(
        id=question_id
    ).values(
        'id',
        'difficulty',
        original_title=F('question_title'),
        translated_title=F('translation__translated_title')
    ).first()

    return question


def get_answers_by_question_id(question_id):
    answers = AnswerVariants.objects.filter(
        question_id=question_id
    ).values(
        'id',
        'is_correct',
        original_title=F('answer_title'),
        translated_title=F('translation__translated_title')
    )

    return answers


def build_question_payload(question, answers, lang):
    if lang == 'en':
        title = 'original_title'
    else:
        title = 'translated_title'

    variants = {}

    index = 0
    rule = {
        1: 'a',
        2: 'b',
        3: 'c',
        4: 'd'
    }

    for answer in answers:
        if index == 4:
            index = 0

        index += 1

        variants[rule[index]] = {
            'id': answer.get('id'),
            'title': answer.get(title)
        }

    return {
        'quest': {
            'id': question.get('id'),
            'title': question.get(title),
            'difficulty': question.get('difficulty')
        },
        'answers': variants
    }


def select_question_strategy(question_id=None, difficulty=None):
    validate_question_difficulty(
        difficulty=difficulty
    )

    if question_id is None:
        question = get_random_question_data(difficulty)
    else:
        if difficulty is not None:
            raise ValidationError('Not allowed parameter difficulty '
                                  'with question_id')
        validate_id(
            ids=question_id,
            error_title=f'Invalid question_id: {question_id}')

        question = get_question_by_id(question_id)

        if not question:
            raise QuestionNotFound(f'Question not found')

    return question


def get_answer_correctness(answer_id):
    is_correct = AnswerVariants.objects.filter(
        id=answer_id
    ).values(
        'is_correct',
        'id',
        'question_id',
    ).first()

    return is_correct


def get_correct_answer_by_question_id(question_id):
    correct_answer = AnswerVariants.objects.filter(
        question_id=question_id,
        is_correct=True
    ).values(
        'id',
        'answer_title',
        'is_correct'
    ).first()

    return correct_answer
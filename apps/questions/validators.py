from apps.exceptions import ValidationError


def validate_question_difficulty(difficulty):
    if difficulty is not None:
        if (not (difficulty == 'easy'
                 or difficulty == 'medium'
                 or difficulty == 'hard')):
            raise ValidationError(f'Invalid difficulty argument: {difficulty}. '
                                  f'allowed: easy, medium, hard')
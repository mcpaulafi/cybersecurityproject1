"""Test module"""
from django.test import TestCase
from .models import Question


class QuestionModelTests(TestCase):
    """Testing for Question model"""

    def test_question_count_is_three(self):
        """Ensure there are exactly 3 recovery questions in the DB"""
        count = Question.objects.count()
        self.assertEqual(count, 3, f"Expected 3 questions, got {count}")

    def test_question_texts_match_choices(self):
        """Ensure DB questions match the defined PASSWORD_QUESTIONS choices"""
        db_values = set(Question.objects.values_list("text", flat=True))
        defined_values = {key for key, _ in Question.PASSWORD_QUESTIONS}
        self.assertSetEqual(db_values, defined_values)

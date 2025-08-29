"""Test module"""
from datetime import timedelta
from django.utils import timezone

from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Appointment, Question, Answer

User = get_user_model()


# Models
class AppointmentModelTests(TestCase):
    """Tests for the Appointment model"""

    def setUp(self):
        """Create common test data"""
        self.user = User.objects.create_user(username="tester",
                                              password="secret123")

    def test_is_open_for_booking_future_and_unbooked(self):
        """Appointment in future with no user should be open"""
        future_time = timezone.now() + timedelta(days=1)
        appointment = Appointment.objects.create(start_date=future_time)
        self.assertTrue(appointment.is_open_for_booking())

    def test_is_open_for_booking_past_date(self):
        """Appointment in the past should not be open"""
        past_time = timezone.now() - timedelta(days=1)
        appointment = Appointment.objects.create(start_date=past_time)
        self.assertFalse(appointment.is_open_for_booking())

    def test_is_open_for_booking_already_booked(self):
        """Appointment already booked by user should not be open"""
        future_time = timezone.now() + timedelta(days=1)
        appointment = Appointment.objects.create(start_date=future_time,
                                                  user_id=self.user)
        self.assertFalse(appointment.is_open_for_booking())

    def test_give_message_returns_text(self):
        """give_message should return the msg_text"""
        appointment = Appointment.objects.create(
            start_date=timezone.now() + timedelta(days=1),
            msg_text="Bring documents"
        )
        self.assertEqual(appointment.give_message(), "Bring documents")



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

class AnswerModelTests(TestCase):
    """Tests for the Answer model"""

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="tester",
                                              password="secret123")

    def test_create_answer_with_question(self):
        """Answer can be created with a linked user and question"""
        answer = Answer.objects.create(
            user=self.user,
            recovery_question=Question.objects.get(text="mother_maiden"),
            answer="Smith"
        )
        self.assertEqual(answer.user.username, "tester")
        self.assertEqual(answer.recovery_question.text, "mother_maiden")
        self.assertEqual(answer.answer, "Smith")

    def test_user_can_have_only_one_answer(self):
        """OneToOneField enforces that each user has only one Answer"""
        Answer.objects.create(user=self.user,
                               recovery_question=Question.objects
                               .get(text="mother_maiden"), answer="Smith")
        with self.assertRaises(Exception):
            Answer.objects.create(user=self.user,
            recovery_question=Question.objects.get(text="first_pet"),
            answer="Buddy")

"""Test module"""
from datetime import timedelta
from django.utils import timezone

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve

from pages import views
from pages.signals import create_default_questions

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

# Signals creates questions on starup

class QuestionSignalTests(TestCase):
    """Tests for the post_migrate signal creating default questions"""

    def test_questions_created_by_signal(self):
        """Signal should insert default PASSWORD_QUESTIONS"""
        # Call signal directly
        create_default_questions(sender=type("MockApp", (), {"name": "pages"}))

        db_values = set(Question.objects.values_list("text", flat=True))
        defined_values = {key for key, _ in Question.PASSWORD_QUESTIONS}
        self.assertSetEqual(db_values, defined_values)

    def test_signal_does_not_duplicate_questions(self):
        """Calling the signal twice should not duplicate questions"""
        create_default_questions(sender=type("MockApp", (), {"name": "pages"}))
        initial_count = Question.objects.count()

        # Call again
        create_default_questions(sender=type("MockApp", (), {"name": "pages"}))
        new_count = Question.objects.count()

        self.assertEqual(initial_count, new_count)

# Urls

class UrlTests(TestCase):
    """Tests for URL configuration in pages.urls"""

    def test_index_url_resolves(self):
        """Check that url works"""
        url = reverse("index")
        self.assertEqual(resolve(url).func, views.index)

    def test_booking_url_resolves(self):
        """Check that url works"""
        url = reverse("booking")
        self.assertEqual(resolve(url).func, views.booking)

    def test_appointments_url_resolves(self):
        """Check that url works"""
        url = reverse("appointments")
        self.assertEqual(resolve(url).func, views.appointments)

    def test_forgot_url_resolves(self):
        """Check that url works"""
        url = reverse("forgot")
        self.assertEqual(resolve(url).func, views.forgot)

    def test_question_url_resolves(self):
        """Check that url works"""
        url = reverse("question")
        self.assertEqual(resolve(url).func, views.question)

    def test_changepswd_url_resolves(self):
        """Check that url works"""
        url = reverse("changepswd")
        self.assertEqual(resolve(url).func, views.changepswd)

# Views

class ViewsTestCase(TestCase):
    """Tests for pages views"""

    def setUp(self):
        """Create a test user and login by default"""
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.login(username="testuser", password="testpass123")

    def test_index_view_shows_appointments(self):
        """ Booking view shows bookable and user appointments """
        future_appt = Appointment.objects.create(
            start_date=timezone.now() + timedelta(days=1)
        )
        user_appt = Appointment.objects.create(
            start_date=timezone.now() + timedelta(days=2),
            user_id=self.user,
        )

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/index.html")
        self.assertIn(future_appt, response.context["available_appointments"])
        self.assertIn(user_appt, response.context["user_appointments"])

    def test_booking_success(self):
        """User is able to make a booking"""
        appt = Appointment.objects.create(start_date=timezone.now() + timedelta(days=1))
        response = self.client.post(reverse("booking"), {
            "start_date_id": appt.id,
            "note": "Checkup",
        })
        self.assertRedirects(response, reverse("index"))
        appt.refresh_from_db()
        self.assertEqual(appt.user_id, self.user)
        self.assertEqual(appt.msg_text, "Checkup")

    def test_booking_past_date_rejected(self):
        """Cannot book a past date"""
        appt = Appointment.objects.create(start_date=timezone.now() - timedelta(days=1))
        response = self.client.post(reverse("booking"), {"start_date_id": appt.id})
        self.assertRedirects(response, reverse("index"))
        appt.refresh_from_db()
        self.assertIsNone(appt.user_id)

    def test_appointments_view(self):
        """Can view all appointments"""
        Appointment.objects.create(start_date=timezone.now() + timedelta(days=1))
        response = self.client.get(reverse("appointments"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/appointments.html")
        self.assertIn("appointments", response.context)

    def test_question_view_get_and_post(self):
        """Saving answer to a question"""
        q = Question.objects.create(text="Test Q?")
        # GET
        response = self.client.get(reverse("question"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/question.html")

        # POST with valid answer
        response = self.client.post(reverse("question"), {
            "question_id": q.id,
            "answer": "valid answer",
        })
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(Answer.objects.filter(user=self.user, recovery_question=q).exists())

    def test_forgot_view_wrong_user(self):
        """Testing forgot password view"""
        q = Question.objects.create(text="Test Q?")
        response = self.client.post(reverse("forgot"), {
            "username": "nosuchuser",
            "question_id": q.id,
            "answer": "abcd",
        })
        self.assertRedirects(response, reverse("forgot"))

    def test_forgot_view_correct_answer(self):
        """Right answer takes to password change page"""
        q = Question.objects.create(text="Test Q?")
        other_user = User.objects.create_user(username="other", password="test123")
        Answer.objects.create(user=other_user, recovery_question=q, answer="abcd")

        response = self.client.post(reverse("forgot"), {
            "username": "other",
            "question_id": q.id,
            "answer": "abcd",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/changepswd.html")

    def test_changepswd_success(self):
        """Password is successfully changed"""
        response = self.client.post(reverse("changepswd"), {
            "username": "testuser",
            "password1": "newStrongPass1",
            "password2": "newStrongPass1",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("index"))

        # Re-login with new password
        self.client.logout()
        login_ok = self.client.login(username="testuser", password="newStrongPass1")
        self.assertTrue(login_ok)

    def test_changepswd_password_mismatch(self):
        """Password change fails"""
        response = self.client.post(reverse("changepswd"), {
            "username": "testuser",
            "password1": "abc12345",
            "password2": "different",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/changepswd.html")

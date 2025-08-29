from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Appointment(models.Model):
    """Class for appointment"""
    start_date = models.DateTimeField("date starts")
    book_date = models.DateTimeField("date booked", auto_now=True)
    msg_text = models.CharField(max_length=200, null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def is_open_for_booking(self) -> bool:
        """Returns true if appointment is available for booking"""
        if (self.user_id is not None) or (self.start_date <= timezone.now()):
            return False
        return True

    def give_message(self):
        """Returns message"""
        return f"{self.msg_text}"

    def __str__(self):
        # pylint: disable=no-member
        booked = f"booked for {self.user_id.username})" if self.user_id else "not booked yet"
        return f"ID {self.id} : {self.start_date} ({booked})"

class Question(models.Model):
    """Class for preset questions for password recovery"""
    PASSWORD_QUESTIONS = [
        ("mother_maiden", "What is your mother's maiden name?"),
        ("first_pet", "What was the name of your first pet?"),
        ("favorite_color", "What is your favorite color?"),
    ]

    # Store in the database
    text = models.CharField(max_length=50, choices=PASSWORD_QUESTIONS)
#                            unique=True, null=True, blank=True)

    def __str__(self):
        return dict(self.PASSWORD_QUESTIONS).get(self.text, self.text)

class Answer(models.Model):
    """User answers for recovery questions"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    recovery_question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.CharField(max_length=200, null=True, blank=True)
    saved_date = models.DateTimeField("date saved", auto_now=True)

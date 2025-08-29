from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Question

@receiver(post_migrate)
def create_default_questions(sender, **kwargs):
    """Preset recovery questions to the database on start"""
    if sender.name == "pages":  # only run for your app
        for key, _ in Question.PASSWORD_QUESTIONS:
            Question.objects.get_or_create(text=key)
"""Modules for views..."""
import re
from django.contrib.admin.views.decorators import staff_member_required # pylint: disable=unused-import
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt # pylint: disable=unused-import
from .models import Appointment, Question, Answer

User = get_user_model()

@login_required
def index(request):
    """Home page of booking"""
    # Future appointments (not past ones)
    available_appointments = ( Appointment.objects
                              .filter(start_date__gte=timezone.now(),
                              user_id__isnull=True)
                              .order_by('start_date'))

    # User's booked appointments
    user_appointments = ( Appointment.objects
                         .filter(user_id=request.user.id)
                         .order_by('-start_date') )

    context = {
        "available_appointments": available_appointments,
        "user_appointments": user_appointments,
        "now": timezone.now()
    }
    return render(request, "pages/index.html", context)

@login_required
# SECURITY FLAW 1: CSRF
# Fix by commenting out # the line below
@csrf_exempt
@transaction.atomic
def booking(request):
    """Booking form handling"""
    if request.method == 'POST':
        customer = request.user
        booked_time = ( Appointment.objects
        .get(id=request.POST.get('start_date_id')))

        # Check that date is not in the past
        if booked_time.start_date < timezone.now():
            messages.error(request, "You cannot book a time in the past.",
                            extra_tags="booking")
            return redirect('index')

        note = request.POST.get('note')

# SECURITY FLAW 3: Injection
# Fix by removing comments from the if clause
        # if not re.match(r'^[\w\s.,!?-]*$', note):
        #     messages.error(request, "Note contains invalid characters!",
        #     extra_tags="booking")
        #     return redirect('index')

        if (booked_time is not None) and (customer is not None):
            booked_time.user_id = customer
            booked_time.msg_text = note
            booked_time.save()
            # Add success message
            messages.success(request, "Booking successful!", extra_tags="booking")
    return redirect('index')


# SECURITY FLAW 2: BROKEN ACCESS
# Fix by removing comment # from the line below
# @staff_member_required
def appointments(request):
    """Appointment list view"""
    # All appointments (not past ones)
    all_appointments = Appointment.objects.all().order_by('start_date')

    context = {
        "appointments": all_appointments,
    }
    return render(request, "pages/appointments.html", context)


@login_required
def question(request):
    """Handling seurity questions"""
    if request.method == 'POST':
        question_id = Question.objects.get(id=request.POST.get('question_id'))
        answer_text = request.POST.get('answer')

        # Input sanitation
        if not re.match(r'^[\w\s.,!?-]*$', answer_text):
            messages.error(request, "Answer contains invalid characters!",
                            extra_tags="answer_check")
            return redirect('question')
        if len(answer_text) < 4:
            messages.error(request, "Answer must be at least 4 characters long.",
                            extra_tags="answer_check")
            return redirect('question')

        if (question_id is not None) and (answer_text is not None):

            Answer.objects.update_or_create(
            user=request.user,  # lookup field
            defaults={
            'recovery_question': question_id,
            'answer': answer_text,
            })
            # Add success message
            messages.success(request, "Recovery question saved successfully!",
                              extra_tags="answer")
            return redirect('index')

    prev_answer = None
    if request.user.is_authenticated:
        prev_answer = Answer.objects.filter(user=request.user).first()

    context = {
        "questions" : Question.objects.all(),
        "prev_answer" : prev_answer
    }

    return render(request, "pages/question.html", context)

# SECURITY FLAW 5: Security Misconfiguration:
# Fix by: TODO

def forgot(request):
    """Forgot password handling"""
    if request.method == 'POST':
        username = request.POST.get('username')
        question_pk = request.POST.get('question_id')
        answer_text = request.POST.get('answer')

        # Input sanitation
        if not re.match(r'^[\w\s.,!?-]*$', answer_text):
            messages.error(request, "Answer contains invalid characters!",
                            extra_tags="answer_check")
            return redirect('forgot')
        if not re.match(r'^[\w\s.,!?-]*$', username):
            messages.error(request, "Username contains invalid characters!",
                            extra_tags="answer_check")
            return redirect('forgot')

        try:
            user = User.objects.get(username=username)
            question_check = Question.objects.get(id=question_pk)
        except (User.DoesNotExist, Question.DoesNotExist):
            messages.error(request, "Invalid username or question!",
                            extra_tags="answer_check")
            return redirect('forgot')

        exists = Answer.objects.filter(
            user=user,
            recovery_question=question_check,
            answer=answer_text
        ).exists()

        if exists:
            # Add success message
            messages.success(request, "Recovery question was answered correctly!",
                              extra_tags="answer_check")
            context = {
            "user" : user
            }
            return render(request, "pages/changepswd.html", context)

        # Add error message
        messages.error(request, "Check answer!", extra_tags="answer_check")

        return redirect('forgot')

    prev_answer = None
    if request.user.is_authenticated:
        prev_answer = Answer.objects.filter(user=request.user).first()
    context = {
        "questions" : Question.objects.all(),
        "prev_answer" : prev_answer
    }

    return render(request, "pages/forgot.html", context)


def changepswd(request):
    """Custom made unsecure view for password change"""
    if request.method == 'POST':
        username = request.POST.get('username')
        pswd1 = request.POST.get('password1')
        pswd2 = request.POST.get('password2')

        try:
            user = User.objects.get(username=username)
            context = {"user" : user}

            print("USEr", username, " PSW;", pswd1, username==pswd1)
            # Basic password checks
            if pswd1 != pswd2:
                messages.error(request, "Passwords do not match!", extra_tags="pswd_check")
                return render(request, "pages/changepswd.html", context)
            if len(pswd1) < 8:
                messages.error(request, "Password must be at least 8 characters long.",
                                extra_tags="pswd_check")
                return render(request, "pages/changepswd.html", context)
# SECURITY FLAW 4: Identification and Authentication Failures:
# Fix by removing comments from the following lines, until comment END OF SECURITY FLAW
            # if username == pswd1:
            #     messages.error(request, "Username and password should not match!",
            #  extra_tags="pswd_check")
            #     return render(request, "pages/changepswd.html", context)
            # if not re.search(r'\d', pswd1):
            #     messages.error(request, "Password must contain at least one number.",
            #  extra_tags="pswd_check")
            #     return redirect('changepswd')
            # if not re.search(r'[A-Z]', pswd1):
            #     messages.error(request, "Password must contain at least one uppercase letter.",
            #                     extra_tags="pswd_check")
            #     return redirect('changepswd')
            # if not re.search(r'[a-z]', pswd1):
            #     messages.error(request, "Password must contain at least one lowercase letter.",
            #                     extra_tags="pswd_check")
            #     return redirect('changepswd')
            # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pswd1):
            #     messages.error(request, "Password must contain at least one special character.",
            #                     extra_tags="pswd_check")
            #     return redirect('changepswd')
# END OF SECURITY FLAW

            user.set_password(pswd1)  # hash password properly
            user.save()

        except User.DoesNotExist:
            # Add error message
            messages.error(request, "Check user!", extra_tags="pswd_check")
            return redirect('changepswd')

        # Add success message
        messages.success(request, "Password updated successfully!", extra_tags="pswd")
        return redirect('index')

    return render(request, "pages/changepswd.html")

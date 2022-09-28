import csv
from django.db import transaction
from io import StringIO
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page
from sesame.decorators import authenticate
from django.shortcuts import render
from vote.forms import ImportForm

from vote.models import Answer, Delegate, Option, Question

# Create your views here.


@authenticate(permanent=True, override=False)
def delegate_view(request):
    return render(
        request,
        'vote/delegate_view.html',
        context={
            'title': _("Votingtool"),
        },
    )


@login_required()
def vote_action(request):
    option = Option.objects.get(pk=request.POST['option'])
    delegate = request.user.delegate
    question = option.question

    Answer.objects.update_or_create(
        delegate=delegate,
        question=question,
        defaults={'option': option},
    )

    return JsonResponse({'option': option.pk})


@login_required()
@cache_page(0.5)
def delegate_data(request):
    question: Question = Question.objects.filter(
        closed=False).order_by('created').first()

    if question is None:
        return JsonResponse({})

    data = {
        'question': question.question,
        'options': question.options,
        'answers': question.answers,
        'results': question.results,
    }

    return JsonResponse(data)


@login_required()
@cache_page(3)
def past_votes(request):
    questions = Question.objects.filter(closed=True).order_by('-created')

    data = [{
        'question': question.question,
        'options': question.options,
        'results': question.results,
    } for question in questions]

    return JsonResponse(data, safe=False)


@user_passes_test(lambda u: u.is_staff)
def staff_view(request):
    return render(request, 'vote/staff_view.html', context={'title': "Admin"})


@user_passes_test(lambda u: u.is_staff)
def create_question(request):
    if Question.objects.filter(closed=False).exists():
        return JsonResponse({'msg': _('Already a question running')})

    question = request.POST.get('question')
    options = [
        option.strip() for option in request.POST.get('options').split('\n')
    ]

    question = Question.objects.create(question=question, closed=False)

    Option.objects.bulk_create(
        [Option(option=option, question=question) for option in options])

    return JsonResponse({'question': question.pk})


@user_passes_test(lambda u: u.is_staff)
def close_question(request):
    question: Question = Question.objects.filter(
        closed=False).order_by('created').first()

    if question is None:
        return JsonResponse({'msg': _("No open questions")})

    question.closed = True
    question.save()

    return JsonResponse({'msg': _("Closed question")})


@user_passes_test(lambda u: u.is_staff)
def import_delegates(request):
    form = ImportForm()
    error, success = '', ''

    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)

        if form.is_valid():
            data = form.cleaned_data
            if data['clear_delegates']:
                Delegate.objects.all().delete()
                get_user_model().objects.filter(is_staff=False).delete()

            content = StringIO(data['csv'].read().decode('utf-8'))
            reader = csv.DictReader(content, delimiter=data['seperator'])

            users = []
            delegates = []

            for row in reader:
                first_name = row[data['first_name']]
                last_name = row[data['last_name']]
                email = row[data['email']]
                delegation = row[data['delegation']]

                user = get_user_model()(
                    first_name=first_name,
                    last_name=last_name,
                    username=email,
                    email=email,
                )

                delegate = Delegate(
                    user=user,
                    delegated_by=delegation,
                )

                users.append(user)
                delegates.append(delegate)
            try:
                with transaction.atomic():
                    get_user_model().objects.bulk_create(users)
                    Delegate.objects.bulk_create(delegates)
                success = "Delegates successfully created"
            except Exception as e:
                error = str(e)

    return render(request, 'vote/import_form.html', {
        'form': form,
        'error': error,
        'success': success
    })

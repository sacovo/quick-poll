from django.contrib import admin
from sesame.utils import get_query_string
from constance import config
from django.core.mail import send_mail
from django.conf import settings
from django.forms.utils import timezone
from vote.models import Delegate, Option, Question

# Register your models here.


@admin.register(Delegate)
class DelegateAdmin(admin.ModelAdmin):
    list_display = ['user', 'delegated_by', 'last_mail']
    actions = ['send_mails']
    date_hierarchy = 'last_mail'
    list_filter = ['mail_failed', 'last_mail']

    @admin.action(description='send mail with auth code')
    def send_mails(self, request, queryset):
        for delegate in queryset:
            user = delegate.user
            url = request.build_absolute_uri('/')
            auth = url + get_query_string(user)
            subject = config.AUTH_SUBJECT.format(delegate=delegate)
            content = config.AUTH_CONTENT.format(delegate=delegate, auth=auth)

            email = delegate.user.email
            success = send_mail(
                subject,
                content,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            if success:
                delegate.last_mail = timezone.now()
                delegate.mail_failed = False
            else:
                delegate.mail_failed = True
            delegate.save()


class OptionInline(admin.TabularInline):
    model = Option
    extra = 3


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question']

    inlines = [OptionInline]

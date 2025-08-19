from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from model_utils.models import TimeStampedModel

# Create your models here.


class Delegate(TimeStampedModel):
    user = models.OneToOneField(get_user_model(), models.CASCADE)
    delegated_by = models.CharField(max_length=255)
    last_mail = models.DateTimeField(default=timezone.datetime(1970, 1, 1))
    mail_failed = models.BooleanField(default=False)

    class Meta:
        ordering = ("delegated_by", "user")

    def __str__(self):
        return str(self.user)


class Question(TimeStampedModel):
    question = models.CharField(max_length=512)
    closed = models.BooleanField(default=False)
    secret = models.BooleanField(default=False)

    @property
    def options(self):
        return {option.pk: option.option for option in self.option_set.all()}

    @property
    def answers(self):
        if self.secret:
            # Set first and last name to "-" and pk to 0
            result = self.answer_set.all().values(
                "option",
                delegate__user__first_name=models.Value("-"),
                delegate__user__last_name=models.Value(""),
                delegate__user__pk=models.Value(0),
                delegate__delegated_by=models.Value("-"),
            )
        else:
            result = self.answer_set.all().values(
                "delegate__user__first_name",
                "delegate__user__last_name",
                "delegate__delegated_by",
                "delegate__user__pk",
                "option",
            )
        return list(result)

    @property
    def results(self):
        return {
            option["option"]: option["count"]
            for option in self.answer_set.all()
            .values("option")
            .annotate(count=models.Count("id"))
        }

    def __str__(self):
        return self.question


class Option(TimeStampedModel):
    option = models.CharField(max_length=255)
    question = models.ForeignKey(
        Question,
        models.CASCADE,
    )

    def __str__(self):
        return self.option


class Answer(TimeStampedModel):
    delegate = models.ForeignKey(Delegate, models.CASCADE)
    question = models.ForeignKey(Question, models.CASCADE)
    option = models.ForeignKey(Option, models.CASCADE)

    def __str__(self):
        return self.option.option

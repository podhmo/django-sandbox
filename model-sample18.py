# -*- coding:utf-8 -*-

"""
prefetch related with to_attr option
"""
import django
from django.db import models
from django.conf import settings
from django.db import connections


settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }},
    INSTALLED_APPS=[__name__]
)
django.setup()


def create_table(model):
    connection = connections['default']
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model)


class Issue(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)

    class Meta:
        app_label = __name__
        unique_together = ("name", )


class Message(models.Model):
    issue = models.ForeignKey(Issue)
    is_public = models.BooleanField(default=True)
    no = models.IntegerField(null=False)
    message = models.TextField(default="", blank=False)

    def __str__(self):
        return "{}..".format(self.message[:5])

    class Meta:
        app_label = __name__
        unique_together = ("issue", "no")

if __name__ == "__main__":
    create_table(Issue)
    create_table(Message)

    a = Issue.objects.create(name="A")
    b = Issue.objects.create(name="B")
    c = Issue.objects.create(name="C")
    Message(message="hello", issue=a, is_public=True, no=1).save()
    Message(message="private hello", issue=a, is_public=False, no=2).save()
    Message(message="bye, bye", issue=a, is_public=True, no=3).save()

    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    from django.db.models import Prefetch
    qs = Issue.objects.all().prefetch_related(
        Prefetch("message_set", queryset=Message.objects.filter(is_public=True), to_attr="publics"),
        Prefetch("message_set", queryset=Message.objects.filter(is_public=False), to_attr="unpublics"),
    ).filter(name="A")
    for issue in qs:
        print(issue)
        print(issue.publics)
        print(issue.unpublics)

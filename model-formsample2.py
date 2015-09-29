# -*- coding:utf-8 -*-
import logging
from django.forms.models import ModelForm
from django import forms
from django.db import models
from django.conf import settings
from django.db import connections
from django.core.management.color import no_style
logger = logging.getLogger(__name__)

settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }},
    INSTALLED_APPS=[__name__]
)


def create_table(model):
    connection = connections['default']
    cursor = connection.cursor()
    sql, references = connection.creation.sql_create_model(model, no_style())
    for statement in sql:
        cursor.execute(statement)

    for f in model._meta.many_to_many:
        create_table(f.rel.through)


# model definition
class Author(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = __name__


class Article(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author)

    class Meta:
        app_label = __name__


# form definition
class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = '__all__'

    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        widget=forms.RadioSelect,
        empty_label=u'該当なし'
    )


if __name__ == "__main__":
    import django
    django.setup()
    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.ERROR)
        logger.addHandler(logging.StreamHandler())

    create_table(Article)
    create_table(Author)

    Author(name="foo").save()
    Author(name="bar").save()

    print(ArticleForm().__html__())
    # output:
    # <tr><th><label for="id_title">Title:</label></th><td><input id="id_title" maxlength="100" name="title" type="text" /></td></tr>
    # <tr><th><label for="id_author_0">Author:</label></th><td><ul id="id_author"><li><label for="id_author_0"><input checked="checked" id="id_author_0" name="author" type="radio" value="" /> 該当なし</label></li>
    # <li><label for="id_author_1"><input id="id_author_1" name="author" type="radio" value="1" /> foo</label></li>
    # <li><label for="id_author_2"><input id="id_author_2" name="author" type="radio" value="2" /> bar</label></li></ul></td></tr>
